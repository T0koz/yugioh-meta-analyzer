"""
Légalité des decks à la date du tournoi → table `deck_legality`.

Pourquoi : le drapeau `tournament_decks.illegal` vient de l'API yugiohmeta et est évalué
contre une banlist POSTÉRIEURE au tournoi. Mesure sur le TCG : avant le 2 février 2026,
2 à 19 % des decks sont jugés légaux par l'API, contre 90 à 100 % avec la banlist réellement
en vigueur ce jour-là. Même rupture en OCG (avril 2026). Le filtre `illegal = 0` jette donc
l'essentiel de l'historique, et en priorité les decks qui jouaient des cartes touchées ensuite
(biais de survivant).

Méthode : pour chaque deck, on prend la dernière banlist de son format (TCG/OCG) dont la date
d'effet est ≤ la date du tournoi (`created`), puis on compte les infractions : plus d'exemplaires
(main + extra + side) que la limite (Forbidden 0, Limited 1, Semi-Limited 2). Validation : de
juin à août 2026, période où la liste est stable, le recalcul et l'API concordent à 99-100 %.

Garde-fous pour l'usage :
  - `legal` vaut NULL pour le format Genesys (légalité par points, pas par banlist) : non évaluable.
  - `days_to_boundary` : distance en jours au changement de liste le plus proche. Autour d'un
    changement (≈ 14 jours), la date du tournoi et l'entrée en vigueur réelle sont ambiguës
    (accord API/recalcul de 84-92 % en février-mai 2026, contre 99 % hors de ces fenêtres).
  - Deux cartes (Stake Your Soul!, Vanquish Soul Razen) concentrent des désaccords avec l'API
    en février 2026 : banlist scrapée ou API à vérifier.

La table est dérivée, donc entièrement reconstruite à chaque exécution. `tournament_decks.illegal`
n'est PAS modifié : aucun notebook ni script existant ne change tant qu'on ne les rebranche pas.

    python scripts/compute_deck_legality.py            # reconstruit deck_legality
    python scripts/compute_deck_legality.py --dry-run  # calcule et résume, n'écrit rien
"""

import argparse
import datetime
import os
import sqlite3
import sys

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "yugioh.db")
METHOD = "banlist-at-created-v1"
LIMIT = {"Forbidden": 0, "Limited": 1, "Semi-Limited": 2}
NOT_EVALUABLE = {"Genesys Format"}  # légalité par points : la banlist ne s'applique pas

SCHEMA = """
DROP TABLE IF EXISTS deck_legality;
CREATE TABLE deck_legality (
    deck_id           TEXT PRIMARY KEY,
    format            TEXT NOT NULL,     -- TCG | OCG
    list_name         TEXT,              -- banlist en vigueur à la date du tournoi
    legal             INTEGER,           -- 1 légal, 0 illégal, NULL non évaluable (Genesys)
    n_violations      INTEGER,           -- cartes en infraction (NULL si non évaluable)
    days_to_boundary  INTEGER,           -- jours jusqu'au changement de liste le plus proche
    method            TEXT NOT NULL,
    computed_at       TEXT NOT NULL
);
CREATE INDEX idx_deck_legality_legal ON deck_legality (legal);
"""


def compute(con):
    td = pd.read_sql(
        "SELECT id, ocg, illegal, tournament_type, created FROM tournament_decks", con
    )
    td["date"] = pd.to_datetime(td.created, utc=True).dt.tz_localize(None).dt.normalize()
    td["fmt"] = td.ocg.map({1: "OCG", 0: "TCG"})

    bl = pd.read_sql(
        "SELECT list_name, format, effective_date, card_name, status FROM banlist_history", con
    )
    # certains noms Yugipedia portent un suffixe de wiki (« Allure of Darkness|sc »)
    bl["card"] = bl.card_name.str.split("|").str[0].str.strip().str.lower()
    bl["eff"] = pd.to_datetime(bl.effective_date, errors="coerce")
    bl = bl.dropna(subset=["eff"])
    bl["limit"] = bl.status.map(LIMIT)
    bl = bl.dropna(subset=["limit"])

    dc = pd.read_sql("SELECT deck_id, card_name, amount FROM deck_cards", con)
    dc["card"] = dc.card_name.str.strip().str.lower()
    copies = dc.groupby(["deck_id", "card"], as_index=False).amount.sum()

    lists = bl.groupby(["format", "list_name"], as_index=False).eff.first().sort_values("eff")

    parts = []
    for fmt in ("TCG", "OCG"):
        d = td[td.fmt == fmt].sort_values("date")
        ls = lists[lists.format == fmt][["list_name", "eff"]].reset_index(drop=True)
        d = pd.merge_asof(d, ls, left_on="date", right_on="eff", direction="backward")
        # date d'effet de la liste suivante : sert à la distance au changement de liste
        d = d.merge(
            ls.assign(next_eff=ls.eff.shift(-1))[["list_name", "next_eff"]], on="list_name", how="left"
        )
        to_prev = (d.date - d.eff).dt.days
        to_next = (d.next_eff - d.date).dt.days
        d["days_to_boundary"] = pd.concat([to_prev, to_next], axis=1).min(axis=1)
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)

    ban = bl[["format", "list_name", "card", "limit"]].rename(columns={"format": "fmt"})
    m = copies.merge(d[["id", "fmt", "list_name"]], left_on="deck_id", right_on="id")
    m = m.merge(ban, on=["fmt", "list_name", "card"], how="inner")
    viol = m[m.amount > m.limit].groupby("deck_id").size().rename("n_violations")
    d = d.merge(viol, left_on="id", right_index=True, how="left")
    d["n_violations"] = d.n_violations.fillna(0).astype(int)
    d["legal"] = (d.n_violations == 0).astype(float)

    skip = d.tournament_type.isin(NOT_EVALUABLE) | d.list_name.isna()
    d.loc[skip, ["legal", "n_violations"]] = None

    now = datetime.date.today().isoformat()
    out = pd.DataFrame({
        "deck_id": d.id, "format": d.fmt, "list_name": d.list_name,
        "legal": d.legal, "n_violations": d.n_violations,
        "days_to_boundary": d.days_to_boundary,
        "method": METHOD, "computed_at": now,
    })
    return out, d


def summarize(out, d):
    print(f"[deck_legality] {len(out)} decks évalués.")
    d = d.assign(legal_api=(d.illegal == 0).astype(int), month=d.date.dt.to_period("M"))
    ev = d[d.legal.notna()]
    print(f"  non évaluables (Genesys / sans banlist) : {int(d.legal.isna().sum())}")
    for fmt in ("TCG", "OCG"):
        x = ev[ev.fmt == fmt]
        print(f"  {fmt} : légaux recalcul {int(x.legal.sum())}/{len(x)} "
              f"| légaux selon l'API {int(x.legal_api.sum())}/{len(x)} "
              f"| decks récupérés (illégaux API, légaux recalcul) : "
              f"{int(((x.legal_api == 0) & (x.legal == 1)).sum())}")
    stable = ev[ev.days_to_boundary > 14]
    print(f"  accord API/recalcul hors fenêtre de changement de liste (>14 j) : "
          f"{(stable.legal == stable.legal_api).mean():.3f} sur {len(stable)} decks, "
          f"dont les decks postérieurs au 2026-06-01 : "
          f"{(stable[stable.date >= '2026-06-01'].legal == stable[stable.date >= '2026-06-01'].legal_api).mean():.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="calcule et résume sans écrire")
    args = ap.parse_args()

    if not os.path.exists(DB_PATH):
        sys.exit(f"[deck_legality] base introuvable : {DB_PATH}")
    # timeout long : le backend ou un notebook peut garder la base ouverte en lecture
    con = sqlite3.connect(DB_PATH, timeout=60)
    try:
        out, d = compute(con)
        summarize(out, d)
        if args.dry_run:
            print("[deck_legality] dry-run : rien n'est écrit.")
            return
        con.executescript(SCHEMA)
        out.to_sql("deck_legality", con, if_exists="append", index=False)
        con.commit()
        print("[deck_legality] table deck_legality reconstruite.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
