"""
Signaux précoces des cartes récentes → table `early_card_signals` (page `/early-signals`).

    python scripts/build_early_signals.py              # écrit la table
    python scripts/build_early_signals.py --dry-run    # affiche le top 20 sans écrire
    python scripts/build_early_signals.py --db <chemin>  # autre base (copie de test, worktree)

Reprend le calcul du notebook 11 (même score, mêmes poids, mêmes fenêtres), avec les correctifs
du ticket A1 de l'audit de rigueur (lot 20, `docs/journal/audit-rigueur-statistique.md` § 1) :

- **Date de référence = dernier deck TCG relevé** (`MAX(created)`), et non la date du jour :
  deux exécutions sur la même base donnent la même table.
- **Banlist en vigueur à cette date**, lue dans `banlist_history` (format TCG). L'ancien filtre
  lisait `cards.ban_tcg`, figé au 13 juin 2026 : Kewl Tune Rotary, Forbidden depuis le
  2026-09-21, était 4e sur 50. Exclues : Forbidden et Limited à la date de référence.
- **Cartes déjà sorties en TCG avant la fenêtre TCG exclues** (`TCG_DAYS`, 168 jours). Avant, une
  carte sortie en OCG dans les 380 derniers jours restait éligible même sortie en TCG depuis six
  mois : les cartes classées 1, 4, 5 et 20 (sorties en TCG le 2026-05-07) ne « montaient » plus.
- **Cartes déjà en méta exclues** : jouées dans au moins 3 % des decks TCG légaux des `META_RECENT_DAYS`
  (90) jours qui précèdent la date de référence. 3 % est le seuil du tier T3 de la tier list
  (`backend/app/tiering.py`, réglé à la main) : une carte plus jouée que le plus petit tier n'est
  plus un signal « avant la méta » (Elfnote June Pride, sortie le 2026-07-02, était dans 19 % des decks).

Score (réglage posé à la main, jamais validé, déclaré sur `/methode`) :
    early_score = 0,35 · vues + 0,35 · proximité de texte + 0,30 · force OCG de l'archétype
- vues : log(1 + vues sur une semaine, YGOPRODeck), normalisé sur le maximum des cartes retenues ;
- proximité de texte : moyenne des 3 plus fortes similarités de texte (`text_synergies`, ≥ 0,1)
  avec les cartes des 20 archétypes au meilleur score méta des ~200 derniers jours, normalisée sur
  le maximum des cartes retenues ;
- force OCG : `ocg_archetype_scores.ocg_score` de l'archétype de la carte (0 sans archétype),
  normalisé sur le maximum des archétypes de `ocg_archetype_scores`.

⚠ Au calcul du lot 20 (decks jusqu'au 2026-11-14), la proximité de texte vaut 0 pour toutes les cartes
retenues (44 sont dans `text_synergies`, aucune n'atteint 0,1 avec une carte des 20 archétypes méta) :
le score revient alors à 54 % vues et 46 % force OCG (0,35 / 0,65 et 0,30 / 0,65). L'API sert le
nombre de cartes à proximité positive (`text_signal_cards`) pour que la page le dise sans date en dur.

Le calcul ne lit aucun deck pour noter une carte : il n'y a pas de « présence dans les decks ».
"""

import argparse
import datetime
import os
import sqlite3

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.tiering import TIER_THRESHOLDS  # noqa: E402  (seuil T3 partagé avec la tier list)

DB = str(ROOT / "data" / "yugioh.db")

# Fenêtres du notebook 11 (TOK-82), réglées à la main, relatives à la date de référence.
TCG_DAYS = 168    # carte sortie en TCG depuis moins de ~5,5 mois
OCG_DAYS = 380    # carte sortie en OCG depuis moins de ~12,5 mois (et pas encore en TCG avant la fenêtre)
META_DAYS = 200   # archétypes méta récents (meta_scores)
META_TOP = 20
TEXT_MIN = 0.1
WEIGHTS = {"views": 0.35, "text": 0.35, "ocg": 0.30}

# « Déjà en méta » : part des decks TCG légaux récents au-delà du seuil T3 de la tier list.
META_RECENT_DAYS = 90
META_SHARE_MAX = dict(TIER_THRESHOLDS)["T3"]

# Statuts exclus à la date de référence (critère de fin A1 : 0 carte Forbidden ou Limited).
EXCLUDED_STATUS = ("Forbidden", "Limited")


def clean(name: str) -> str:
    """`cards.name` porte `<P>`/`<C>`/`<Q>` ; `banlist_history` et `deck_cards`, non."""
    return name.replace("<", "").replace(">", "")


def ref_date(conn: sqlite3.Connection) -> pd.Timestamp:
    last = conn.execute("SELECT MAX(created) FROM tournament_decks WHERE ocg = 0").fetchone()[0]
    if not last:
        raise SystemExit("Aucun deck TCG dans tournament_decks : date de référence impossible")
    return pd.Timestamp(last[:10])


def banlist_at(conn: sqlite3.Connection, as_of: str) -> pd.Series:
    """Statut TCG en vigueur à `as_of`, indexé par nom de carte (même règle que le Ban Radar)."""
    bh = pd.read_sql_query(
        "SELECT card_name, status, effective_date, end_date FROM banlist_history WHERE format = 'TCG'",
        conn,
    )
    in_force = bh[(bh.effective_date <= as_of) & (bh.end_date.isna() | (bh.end_date >= as_of))]
    return in_force.groupby("card_name").status.first()


def deck_usage(conn: sqlite3.Connection, start: str, end: str) -> tuple[int, dict]:
    """(nombre de decks TCG légaux entre `start` et `end` inclus, decks qui jouent chaque carte)."""
    decks = """
        SELECT d.id FROM tournament_decks d JOIN deck_legality l ON l.deck_id = d.id
        WHERE d.ocg = 0 AND l.legal = 1 AND substr(d.created, 1, 10) BETWEEN ? AND ?
    """
    n = conn.execute(f"SELECT COUNT(*) FROM ({decks})", (start, end)).fetchone()[0]
    rows = conn.execute(
        f"SELECT card_name, COUNT(DISTINCT deck_id) FROM deck_cards WHERE deck_id IN ({decks}) GROUP BY card_name",
        (start, end),
    ).fetchall()
    return n, dict(rows)


def build(conn: sqlite3.Connection, ref: pd.Timestamp) -> tuple[pd.DataFrame, dict]:
    as_of = ref.strftime("%Y-%m-%d")
    tcg_from = (ref - pd.Timedelta(days=TCG_DAYS)).strftime("%Y-%m-%d")
    ocg_from = (ref - pd.Timedelta(days=OCG_DAYS)).strftime("%Y-%m-%d")
    meta_from = (ref - pd.Timedelta(days=META_DAYS)).strftime("%Y-%m-01")

    cards = pd.read_sql_query(
        """
        SELECT id, name, archetype, tcg_date, ocg_date, views_week
        FROM cards
        WHERE (tcg_date >= ? OR ocg_date >= ?)
          AND (tcg_date IS NULL OR tcg_date >= ?)
          AND views_week IS NOT NULL
        """,
        conn,
        params=(tcg_from, ocg_from, tcg_from),
    )
    # Garde de nom : une carte renumérotée par YGOPRODeck apparaît deux fois sous le même nom.
    cards = cards.sort_values("views_week", ascending=False).drop_duplicates("name").reset_index(drop=True)

    status = banlist_at(conn, as_of)
    cards["ban_status"] = cards["name"].map(lambda n: status.get(clean(n)))
    excluded = cards[cards["ban_status"].isin(EXCLUDED_STATUS)]
    cards = cards[~cards["ban_status"].isin(EXCLUDED_STATUS)].copy()

    # Déjà en méta : part des decks TCG légaux des META_RECENT_DAYS jours avant la référence.
    recent_from = (ref - pd.Timedelta(days=META_RECENT_DAYS)).strftime("%Y-%m-%d")
    n_recent, usage = deck_usage(conn, recent_from, as_of)
    cards["recent_share"] = cards["name"].map(lambda n: usage.get(clean(n), 0) / n_recent if n_recent else 0.0)
    in_meta = cards[cards["recent_share"] >= META_SHARE_MAX]
    cards = cards[cards["recent_share"] < META_SHARE_MAX].copy()

    # Signal 1 : vues sur une semaine.
    cards["views_log"] = np.log1p(cards["views_week"].fillna(0))
    cards["signal_views"] = (cards["views_log"] / cards["views_log"].max()).round(4)

    # Signal 2 : proximité de texte avec les cartes des archétypes méta récents.
    meta_archs = pd.read_sql_query(
        "SELECT archetype FROM meta_scores WHERE month >= ? "
        "GROUP BY archetype ORDER BY AVG(meta_score) DESC LIMIT ?",
        conn,
        params=(meta_from, META_TOP),
    )["archetype"].tolist()
    ph = ",".join("?" * len(meta_archs))
    meta_set = set(
        pd.read_sql_query(f"SELECT DISTINCT name FROM cards WHERE archetype IN ({ph})", conn, params=meta_archs)["name"]
    )
    new_set = set(cards["name"])
    ts = pd.read_sql_query(
        "SELECT card_a, card_b, text_synergy_score FROM text_synergies WHERE text_synergy_score >= ?",
        conn,
        params=(TEXT_MIN,),
    )
    ts = ts[(ts.card_a.isin(new_set) & ts.card_b.isin(meta_set)) | (ts.card_b.isin(new_set) & ts.card_a.isin(meta_set))].copy()
    a_new = ts.card_a.isin(new_set)
    ts["card_new"] = np.where(a_new, ts.card_a, ts.card_b)
    ts["card_meta"] = np.where(a_new, ts.card_b, ts.card_a)
    if ts.empty:
        ts_agg = pd.DataFrame(columns=["card_new", "max_meta_synergy", "top3_meta_synergy", "n_meta_connections", "best_meta_match"])
    else:
        ts_agg = ts.groupby("card_new").agg(
            max_meta_synergy=("text_synergy_score", "max"),
            top3_meta_synergy=("text_synergy_score", lambda x: x.nlargest(3).mean()),
            n_meta_connections=("text_synergy_score", "count"),
        ).reset_index()
        best = ts.sort_values("text_synergy_score", ascending=False).drop_duplicates("card_new")
        ts_agg = ts_agg.merge(best[["card_new", "card_meta"]].rename(columns={"card_meta": "best_meta_match"}), on="card_new")
    top3_max = ts_agg["top3_meta_synergy"].max() if len(ts_agg) else 0
    ts_agg["signal_text"] = (ts_agg["top3_meta_synergy"] / top3_max).round(4) if top3_max else 0.0

    # Signal 3 : force OCG de l'archétype.
    ocg = pd.read_sql_query("SELECT archetype, ocg_score FROM ocg_archetype_scores", conn)
    ocg_map = (ocg.set_index("archetype")["ocg_score"] / ocg["ocg_score"].max()).round(4).to_dict()
    cards["signal_ocg"] = cards["archetype"].map(ocg_map).fillna(0.0)

    res = cards.merge(ts_agg, left_on="name", right_on="card_new", how="left").drop(columns="card_new")
    for col in ("signal_text", "max_meta_synergy", "top3_meta_synergy"):
        res[col] = res[col].astype(float).fillna(0.0)
    res["n_meta_connections"] = res["n_meta_connections"].fillna(0).astype(int)
    res["best_meta_match"] = res["best_meta_match"].fillna("")

    res["early_score"] = (
        WEIGHTS["views"] * res["signal_views"] + WEIGHTS["text"] * res["signal_text"] + WEIGHTS["ocg"] * res["signal_ocg"]
    ).round(4)
    res["early_score_100"] = (res["early_score"] / res["early_score"].max() * 100).round(1)
    res = res.sort_values(["early_score_100", "name"], ascending=[False, True]).reset_index(drop=True)
    # Nom sans <P>/<C>/<Q> : l'API joint `cards` sur le nom nettoyé (index idx_cards_name_clean).
    res["card_name"] = res["name"].map(clean)

    info = {
        "as_of": as_of, "tcg_from": tcg_from, "ocg_from": ocg_from, "meta_from": meta_from,
        "n_meta_archs": len(meta_archs), "n_excluded_ban": len(excluded),
        "recent_from": recent_from, "n_recent": n_recent,
        "in_meta": in_meta[["name", "recent_share"]].sort_values("recent_share", ascending=False).values.tolist(),
        "excluded_ban": excluded[["name", "ban_status"]].values.tolist(),
        "n_text_positive": int((res["signal_text"] > 0).sum()),
    }
    return res, info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=DB, help="Base à lire et écrire (défaut : data/yugioh.db)")
    parser.add_argument("--dry-run", action="store_true", help="Affiche le top 20 sans écrire")
    args = parser.parse_args()

    uri = f"file:{os.path.abspath(args.db)}{'?mode=ro' if args.dry_run else ''}"
    conn = sqlite3.connect(uri, uri=True, timeout=60)
    ref = ref_date(conn)
    res, info = build(conn, ref)

    print(f"Date de référence (dernier deck TCG) : {info['as_of']}")
    print(f"Fenêtres : TCG ≥ {info['tcg_from']}, OCG ≥ {info['ocg_from']} (sans sortie TCG antérieure), méta ≥ {info['meta_from']}")
    print(f"Cartes notées : {len(res)} ; exclues par la banlist du {info['as_of']} : {info['n_excluded_ban']}")
    for name, st in info["excluded_ban"]:
        print(f"  − {name} ({st})")
    print(f"Exclues car déjà en méta (≥ {META_SHARE_MAX:.0%} des {info['n_recent']} decks TCG légaux "
          f"du {info['recent_from']} au {info['as_of']}) : {len(info['in_meta'])}")
    for name, share in info["in_meta"]:
        print(f"  − {name} ({share:.1%})")
    print(f"Cartes avec une proximité de texte positive : {info['n_text_positive']} sur {len(res)}")
    cols = ["card_name", "archetype", "tcg_date", "views_week", "signal_views", "signal_text", "signal_ocg", "early_score_100"]
    print(res[cols].head(20).to_string(index=False))

    if args.dry_run:
        return

    out = res[["card_name", "archetype", "tcg_date", "ocg_date", "views_week", "signal_views", "signal_text",
               "signal_ocg", "early_score", "early_score_100", "max_meta_synergy", "n_meta_connections",
               "best_meta_match"]].copy()
    out["as_of"] = info["as_of"]  # date de référence : dernier deck TCG relevé
    out["computed_at"] = datetime.date.today().isoformat()
    # DROP + CREATE + INSERT dans une seule transaction : un échec de to_sql ne laisse pas une table vide.
    conn.execute("BEGIN")
    conn.execute("DROP TABLE IF EXISTS early_card_signals")
    conn.execute(
        """
        CREATE TABLE early_card_signals (
            card_name TEXT PRIMARY KEY, archetype TEXT, tcg_date TEXT, ocg_date TEXT,
            views_week INTEGER, signal_views REAL, signal_text REAL, signal_ocg REAL,
            early_score REAL, early_score_100 REAL, max_meta_synergy REAL,
            n_meta_connections INTEGER, best_meta_match TEXT, as_of TEXT, computed_at TEXT
        )
        """
    )
    out.to_sql("early_card_signals", conn, if_exists="append", index=False)
    conn.commit()
    print(f"\nTable early_card_signals écrite ({len(out)} lignes)")


if __name__ == "__main__":
    main()
