"""
Validation du journal des prédictions (TOK-75) : compare chaque prédiction `mûre` à la réalité.

    python scripts/validate_predictions.py            # rapport + table prediction_validation
    python scripts/validate_predictions.py --dry-run  # rapport seul, n'écrit rien

Lit `prediction_log` (append-only) et la réalité (`meta_scores_regional`, `tournament_decks`,
`deck_legality`, `banlist_history`, `card_price_history`). Écrit UNIQUEMENT la table dérivée
`prediction_validation` (reconstruite à chaque run). Ne modifie jamais `prediction_log`.

Règles d'honnêteté appliquées à chaque famille :
  - une prédiction n'est évaluée que si sa cible est échue (mois révolu / liste suivante parue) ;
  - une prédiction dont la cible est antérieure au mois de calcul n'est PAS une prévision
    (c'est un rejeu) : elle est exclue et comptée à part (cas des lots `backfill` de meta_forecast
    dont le « mois suivant » est déjà passé) ;
  - la provenance (`live` / `backfill`) est reportée : seul `live` commité est une preuve.

Familles :
  meta_forecast    cible = mois ; réalité = meta_score TCG (meta_scores_regional, échelle propre).
                   Mesure : direction (signe de la variation vs baseline) ; pas d'erreur de niveau,
                   les échelles de `meta_scores` et `meta_scores_regional` diffèrent.
  ban_risk_<fmt>   cible = prochaine banlist du format après made_at ; réalité = cartes dont le
                   statut gagne en sévérité. Rang médian des cartes touchées / univers noté.
  boutique_signal  cible = mois d'entrée TCG estimé ; réalité = part TCG de l'archétype ce mois-là
                   vs le mois de calcul.
  boutique_buy     idem + variation Cardmarket de la carte (made_at → fin du mois cible) vs la médiane
                   du marché (cartes ≥ 1 € au départ).
  early_card       pas de cible datée : descriptif seulement (part de decks TCG légaux jouant la carte
                   depuis made_at).
"""
import argparse
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_ban_radar import banlist_events  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "yugioh.db"
TODAY = date.today()
CUR_MONTH = TODAY.strftime("%Y-%m")


def month_done(m: str) -> bool:
    return m < CUR_MONTH


def validate_meta(con, log) -> list[dict]:
    rows = []
    reg = pd.read_sql("SELECT month, archetype, meta_score FROM meta_scores_regional WHERE region='TCG'", con)
    real = reg.set_index(["month", "archetype"]).meta_score
    for r in log.itertuples():
        base = {"kind": r.kind, "subject": r.subject, "made_at": r.made_at, "target": r.target_date,
                "provenance": r.provenance}
        if not r.target_date or r.target_date < r.made_at[:7]:
            rows.append({**base, "status": "exclue_rejeu"}); continue
        base["partielle"] = int(r.target_date == r.made_at[:7])  # cible = mois de calcul : une partie du mois était connue
        if not month_done(r.target_date):
            rows.append({**base, "status": "non_échue"}); continue
        key = (r.target_date, r.subject)
        if key not in real.index:
            rows.append({**base, "status": "réalité_absente"}); continue
        # direction vs baseline : on lit le niveau de départ dans le payload (pred_delta) → signe seulement
        pay = json.loads(r.payload); delta = pay.get("pred_delta")
        prev = real.get((pay.get("data_month"), r.subject))
        if delta is None or prev is None:
            rows.append({**base, "status": "base_absente"}); continue
        rows.append({**base, "status": "évaluée", "predicted_delta": delta, "realized_delta": real[key] - prev,
                     "direction_ok": int(np.sign(delta) == np.sign(real[key] - prev))})
    return rows


def validate_ban(con, log, fmt) -> list[dict]:
    events = banlist_events(con, fmt)
    rows = []
    for made_at, g in log.groupby("made_at"):
        nxt = [e for e in events if e[1] > made_at]
        base = {"kind": g.kind.iloc[0], "made_at": made_at, "provenance": g.provenance.iloc[0], "subject": "(liste)"}
        if not nxt:
            rows.append({**base, "status": "non_échue", "n": len(g)}); continue
        eve, eff, hits = nxt[0]
        # première liste du format parue après made_at, même sans durcissement : on prend la liste suivante
        s = g.set_index("subject").predicted_value.sort_values(ascending=False)
        rank = pd.Series(np.arange(1, len(s) + 1), index=s.index)
        hit_in = [h for h in hits if h in rank.index]
        if len(hit_in) < 3:
            rows.append({**base, "status": "trop_peu_de_cartes_touchées", "n": len(g), "target": eff}); continue
        rk = rank[hit_in]
        rows.append({**base, "status": "évaluée", "target": eff, "n": len(g), "n_hits": len(hits),
                     "n_hits_in_universe": len(hit_in), "median_rank": float(rk.median()),
                     "random_rank": len(s) / 2, "top10": int((rk <= 0.1 * len(s)).sum()),
                     "top25": int((rk <= 0.25 * len(s)).sum())})
    return rows


def validate_boutique(con, log) -> list[dict]:
    reg = pd.read_sql("SELECT month, archetype, share FROM meta_scores_regional WHERE region='TCG'", con).set_index(["month", "archetype"]).share
    rows = []
    px = pd.read_sql("SELECT card_name, snapshot_date, cardmarket_price p FROM card_price_history", con)
    for r in log.itertuples():
        arch = r.subject.split(" | ")[0]
        base = {"kind": r.kind, "subject": r.subject, "made_at": r.made_at, "target": r.target_date, "provenance": r.provenance}
        if not r.target_date or not month_done(r.target_date):
            rows.append({**base, "status": "non_échue"}); continue
        s0 = reg.get((r.made_at[:7], arch), 0.0); s1 = reg.get((r.target_date, arch), 0.0)
        row = {**base, "status": "évaluée", "tcg_share_at_made": s0, "tcg_share_at_target": s1,
               "share_up": int(s1 > s0)}
        if r.kind == "boutique_buy":
            card = r.subject.split(" | ")[1]
            end = f"{r.target_date}-31"
            a = px[(px.card_name == card) & (px.snapshot_date >= r.made_at)].sort_values("snapshot_date")
            b = px[(px.card_name == card) & (px.snapshot_date <= end)].sort_values("snapshot_date")
            if len(a) and len(b) and a.p.iloc[0] and a.p.iloc[0] >= 1:
                row["price_change"] = b.p.iloc[-1] / a.p.iloc[0] - 1
        rows.append(row)
    return rows


def validate_early(con, log) -> list[dict]:
    legal = pd.read_sql("SELECT td.id, td.created FROM tournament_decks td JOIN deck_legality dl ON dl.deck_id=td.id "
                        "WHERE td.ocg=0 AND dl.legal=1", con)
    rows = []
    for made_at, g in log.groupby("made_at"):
        ids = legal[legal.created >= made_at].id
        if len(ids) < 50:
            rows.append({"kind": "early_card", "made_at": made_at, "subject": "(lot)", "provenance": g.provenance.iloc[0], "status": "non_échue"}); continue
        used = pd.read_sql("SELECT card_name, COUNT(DISTINCT deck_id) n FROM deck_cards WHERE deck_id IN (%s) GROUP BY 1" %
                           ",".join("?" * len(ids)), con, params=list(ids)).set_index("card_name").n / len(ids)
        for r in g.itertuples():
            rows.append({"kind": "early_card", "made_at": made_at, "subject": r.subject, "provenance": r.provenance,
                         "status": "descriptive", "tcg_deck_share_since": float(used.get(r.subject, 0.0))})
    return rows


def summarize(v: pd.DataFrame) -> None:
    print(f"Validation au {TODAY} — {len(v)} lignes (prediction_validation)\n")
    print(v.groupby(["kind", "provenance", "status"]).size().rename("n").to_string(), "\n")
    e = v[v.kind == "meta_forecast"]; e = e[e.status == "évaluée"]
    if len(e):
        print(f"meta_forecast évaluées : {len(e)} ; direction correcte {e.direction_ok.mean():.0%}\n")
    for kind, g in v[v.kind.str.startswith("ban_risk")].groupby("made_at"):
        for r in g[g.status == "évaluée"].itertuples():
            print(f"{r.kind} {r.made_at} → liste {r.target}: {r.n_hits_in_universe}/{r.n_hits} cartes touchées notées, "
                  f"rang médian {r.median_rank:.0f}/{r.n} (hasard {r.random_rank:.0f}), top-10% {r.top10}, top-25% {r.top25}")
    b = v[(v.kind.str.startswith("boutique")) & (v.status == "évaluée")]
    for kind, g in b.groupby("kind"):
        print(f"{kind}: {len(g)} évaluées ; part TCG en hausse pour {g.share_up.mean():.0%}", end="")
        if "price_change" in g and g.price_change.notna().any():
            print(f" ; variation de prix médiane {g.price_change.median():+.1%} (n={g.price_change.notna().sum()})", end="")
        print()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    con = sqlite3.connect(f"file:{DB}?mode=ro" if a.dry_run else DB, uri=a.dry_run, timeout=60)
    log = pd.read_sql("SELECT * FROM prediction_log", con)
    rows = []
    rows += validate_meta(con, log[log.kind == "meta_forecast"])
    for fmt in ("tcg", "ocg"):
        l = log[log.kind == f"ban_risk_{fmt}"]
        if len(l): rows += validate_ban(con, l, fmt.upper())
    rows += validate_boutique(con, log[log.kind.isin(["boutique_signal", "boutique_buy"])])
    e = log[log.kind == "early_card"]
    if len(e): rows += validate_early(con, e)
    v = pd.DataFrame(rows); v["validated_on"] = TODAY.isoformat()
    summarize(v)
    if not a.dry_run:
        v.to_sql("prediction_validation", con, if_exists="replace", index=False)
        print("\nTable prediction_validation écrite.")
    con.close()


if __name__ == "__main__":
    main()
