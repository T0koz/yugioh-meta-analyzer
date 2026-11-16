"""
Reconstruit `banlist_features` (mois × archétype) depuis `banlist_history` (TOK-69).

Le générateur d'origine vivait dans une ancienne version du notebook 09 ; quand
`fetch_banlist_history.py` l'a remplacé, la table est restée sans producteur et ne
se rafraîchissait plus (dernier mois : 2026-06). Ce script la rend reproductible.

Définition (rétro-ingéniérée puis validée contre la table historique : 0 écart sur
`ban_severity`, `ban_severity_t1`, `was_hit_recent` ; 14 écarts sur 3 660 lignes
n_forbidden/n_limited/n_semi, attribuables aux amendements Yugipedia) :
  - liste TCG en vigueur au 1er jour du mois ;
  - cartes jointes à `cards.archetype` (jointure sur le nom sans <>) ;
  - ban_severity = 3·interdites + 2·limitées + 1·semi-limitées ;
  - ban_severity_t1 = sévérité du mois précédent (NaN le premier mois) ;
  - was_hit_recent = la sévérité a augmenté vs mois précédent (1er mois : sévérité > 0).
Archétypes = ceux de `meta_scores` (donc à lancer APRÈS le notebook 04).

    python scripts/build_banlist_features.py [--dry-run]
"""
import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB = Path(__file__).resolve().parents[1] / "data" / "yugioh.db"


def build(con) -> pd.DataFrame:
    bl = pd.read_sql("SELECT effective_date, card_name, status FROM banlist_history WHERE format='TCG'", con)
    cards = pd.read_sql("SELECT name, archetype FROM cards WHERE archetype IS NOT NULL", con)
    cards["card_name"] = cards.name.str.replace("<", "").str.replace(">", "")
    cards = cards[["card_name", "archetype"]].drop_duplicates()
    arch = sorted(pd.read_sql("SELECT DISTINCT archetype FROM meta_scores", con).archetype)
    first = pd.read_sql("SELECT MIN(created) c, MAX(created) m FROM tournament_decks", con).iloc[0]
    months = pd.date_range(pd.Timestamp("2024-01-01"), pd.Timestamp(first.m[:7] + "-01"), freq="MS")

    rows = []
    for d in months:
        cur = bl[bl.effective_date <= d.strftime("%Y-%m-%d")]
        cur = cur[cur.effective_date == cur.effective_date.max()]
        g = cur.merge(cards, on="card_name").groupby(["archetype", "status"]).size().unstack(fill_value=0)
        for c in ("Forbidden", "Limited", "Semi-Limited"):
            if c not in g:
                g[c] = 0
        g = g.reindex(arch, fill_value=0)
        rows.append(pd.DataFrame({"month": d, "archetype": arch, "n_forbidden": g.Forbidden.values,
                                  "n_limited": g.Limited.values, "n_semi": g["Semi-Limited"].values}))
    f = pd.concat(rows, ignore_index=True)
    f["ban_severity"] = 3 * f.n_forbidden + 2 * f.n_limited + f.n_semi
    f = f.sort_values(["archetype", "month"])
    prev = f.groupby("archetype").ban_severity.shift(1)
    f["ban_severity_t1"] = prev
    f["was_hit_recent"] = ((f.ban_severity > prev) | (prev.isna() & (f.ban_severity > 0))).astype(int)
    return f.sort_values(["month", "archetype"]).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB, timeout=60)
    f = build(con)
    print(f"[banlist_features] {len(f)} lignes, {f.month.min():%Y-%m} → {f.month.max():%Y-%m}, "
          f"{f.archetype.nunique()} archétypes, {int(f.was_hit_recent.sum())} 'hit'")
    if not a.dry_run:
        f.to_sql("banlist_features", con, if_exists="replace", index=False)
        print("[banlist_features] écrite.")
    con.close()


if __name__ == "__main__":
    main()
