"""
TOK-55 — Ban Radar contre l'historique : range le backtest liste par liste.

Écrit deux tables, servies par `GET /api/v1/ban-radar/history` :

- `ban_backtest_lists` : une ligne par banlist (TCG et OCG), retenue ou écartée ;
- `ban_backtest_cards` : pour chaque liste retenue, le top N prévu la veille et
  toutes les cartes réellement touchées, avec leur rang.

    python scripts/build_ban_history.py               # écrit les deux tables
    python scripts/build_ban_history.py --dry-run     # affiche sans écrire
    python scripts/build_ban_history.py --db <chemin> # autre base (worktree, copie)

Aucun calcul nouveau du score : tout passe par `build_ban_radar.backtest_lists`,
la même fonction que `build_ban_radar.py --backtest`. Rangs médians, univers et
hasard sont donc ceux qu'imprime le backtest (mêmes arrondis). Ajouts, calculés
sur les seules données de la veille :

- la bande du hasard : rangs médians obtenus en tirant au sort autant de cartes
  que de cartes touchées classées (5e et 95e centiles, 20 000 tirages, graine fixe) ;
- la base « staples les plus jouées » : même univers, classé par part des decks
  seule (critère `ubiquity`), rang moyen en cas d'égalité.

À lancer après `build_ban_radar.py` et `fetch_banlist_history.py` (une nouvelle
banlist devient un point de mesure), puis `build_serving_db.py`.
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_radar as radar  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"

# Taille du « top prévu » montré pour chaque liste. 10 cartes ≈ 1 % d'un univers
# de 700 à 1 200 cartes : c'est la tête du classement qu'un lecteur regarde.
TOP_N = 10
RANDOM_DRAWS = 20_000
RANDOM_SEED = 55


def random_band(n_cards: int, k: int, rng: np.random.Generator) -> tuple[int, int]:
    """5e et 95e centiles du rang médian de k cartes tirées au hasard parmi n."""
    draws = np.array([np.median(rng.choice(n_cards, size=k, replace=False) + 1)
                      for _ in range(RANDOM_DRAWS)])
    low, high = np.percentile(draws, [5, 95])
    return int(round(low)), int(round(high))


def statuses(conn: sqlite3.Connection, fmt: str) -> dict[str, pd.Series]:
    """Statut de chaque carte par date d'effet, pour dire « avant → après »."""
    bh = pd.read_sql_query(
        "SELECT effective_date, card_name, status FROM banlist_history "
        "WHERE format = ? AND effective_date IS NOT NULL",
        conn,
        params=(fmt,),
    )
    return {date: grp.set_index("card_name").status for date, grp in bh.groupby("effective_date")}


def collect(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RANDOM_SEED)
    lists, cards = [], []

    for fmt in ("TCG", "OCG"):
        by_date = statuses(conn, fmt)
        dates = sorted(by_date)

        for result in radar.backtest_lists(conn, fmt):
            effective, hits = result["effective"], result["hits"]
            row = {
                "format": fmt,
                "effective_date": effective,
                "as_of": result["as_of"],
                "n_decks": int(result["n_decks"]),
                "n_hits": len(hits),
                "retained": int(result["retained"]),
                "skip_reason": None,
            }
            if not result["retained"]:
                row["skip_reason"] = ("decks" if result["n_decks"] < radar.BACKTEST_MIN_DECKS
                                      else "hits")
                lists.append(row)
                continue

            df, ranked, missing = result["ranking"], result["ranked"], result["missing"]
            n = len(df)
            ranks = np.array([r for _, r in ranked])
            percentiles = ranks / n * 100

            # Base de comparaison : même univers, classé par part des decks seule.
            baseline = df.ubiquity.rank(ascending=False, method="average")
            base_ranks = np.array([baseline[c] for c, _ in ranked])
            band = random_band(n, len(ranks), rng)

            row.update({
                "n_cards": n,
                "n_hits_ranked": len(ranked),
                "n_hits_missing": len(missing),
                # Mêmes arrondis que l'affichage de --backtest (format .0f).
                "median_rank": int(f"{np.median(ranks):.0f}"),
                "random_rank": int(f"{n / 2:.0f}"),
                "random_low": band[0],
                "random_high": band[1],
                "top_n": TOP_N,
                "top_n_hits": int((ranks <= TOP_N).sum()),
                "top10pct_hits": int((percentiles <= 10).sum()),
                "top25pct_hits": int((percentiles <= 25).sum()),
                "baseline_median_rank": int(f"{np.median(base_ranks):.0f}"),
                "baseline_top_n_hits": int((base_ranks <= TOP_N).sum()),
            })
            lists.append(row)

            previous = dates[dates.index(effective) - 1]
            before, after = by_date[previous], by_date[effective]
            rank_of = dict(ranked)
            keep = list(df.index[:TOP_N]) + [h for h in hits if h not in df.index[:TOP_N]]
            for card in keep:
                in_universe = card in df.index
                cards.append({
                    "format": fmt,
                    "effective_date": effective,
                    "card_name": card,
                    "rank": int(df.index.get_loc(card) + 1) if in_universe else None,
                    "ban_risk_score": float(df.loc[card, "ban_risk_score"]) if in_universe else None,
                    "baseline_rank": float(baseline[card]) if in_universe else None,
                    "hit": int(card in hits),
                    "in_top": int(in_universe and df.index.get_loc(card) < TOP_N),
                    "generic": int(in_universe and pd.isna(df.loc[card, "top_archetype"])),
                    "top_archetype": (df.loc[card, "top_archetype"]
                                      if in_universe and not pd.isna(df.loc[card, "top_archetype"])
                                      else None),
                    "status_before": before.get(card, "Unlimited"),
                    "status_after": after.get(card, "Unlimited"),
                })
                if card in hits and in_universe:
                    assert rank_of[card] == cards[-1]["rank"]

    computed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lists_df = pd.DataFrame(lists)
    # Les listes écartées n'ont pas de classement : sans Int64, pandas passerait
    # toutes ces colonnes en flottants et SQLite les stockerait en REAL.
    for column in lists_df.columns.difference(["format", "effective_date", "as_of", "skip_reason"]):
        lists_df[column] = lists_df[column].astype("Int64")
    lists_df["computed_at"] = computed_at
    cards_df = pd.DataFrame(cards)
    cards_df["rank"] = cards_df["rank"].astype("Int64")
    return lists_df, cards_df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Base à lire et à écrire (défaut : data/yugioh.db)")
    parser.add_argument("--dry-run", action="store_true", help="Calcule et affiche sans écrire")
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")
    uri = f"file:{args.db}?mode=ro" if args.dry_run else str(args.db)
    conn = sqlite3.connect(uri, uri=args.dry_run, timeout=60)

    lists, cards = collect(conn)
    retained = lists[lists.retained == 1]
    cols = ["format", "effective_date", "n_cards", "n_decks", "n_hits", "n_hits_ranked",
            "median_rank", "random_rank", "random_low", "random_high", "top_n_hits",
            "top10pct_hits", "top25pct_hits", "baseline_median_rank", "baseline_top_n_hits"]
    print(retained[cols].to_string(index=False))
    print(f"\n{len(retained)} listes retenues, {len(lists) - len(retained)} écartées, "
          f"{len(cards)} lignes de cartes (top {TOP_N} + cartes touchées)")

    if args.dry_run:
        return

    lists.to_sql("ban_backtest_lists", conn, if_exists="replace", index=False)
    cards.to_sql("ban_backtest_cards", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ban_backtest_cards_list "
                 "ON ban_backtest_cards(format, effective_date)")
    conn.commit()
    print("Tables ban_backtest_lists et ban_backtest_cards écrites")


if __name__ == "__main__":
    main()
