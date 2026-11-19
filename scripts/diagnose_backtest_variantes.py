"""
Mesure le backtest du Ban Radar sur une base (copie de travail) et compare deux mesures (TOK-136, TOK-137).

    python scripts/diagnose_backtest_variantes.py --db <copie> --out <dossier> --label avant
    python scripts/diagnose_backtest_variantes.py --db <copie> --out <dossier> --label apres
    python scripts/diagnose_backtest_variantes.py --compare <dossier>/avant <dossier>/apres

Lecture seule (`mode=ro`). Aucun calcul nouveau du score : tout passe par `build_ban_radar.backtest_lists`, la
fonction de `--backtest` et de `build_ban_history.py`. Les mesures par liste sont celles de l'onglet Historique
(rang médian des cartes touchées, cartes touchées dans le top 25, base « staples » = même univers classé par la seule
part des decks, rang moyen en cas d'égalité) ; les sommes par format sont celles que compare `verdictMatches`
(`frontend/src/lib/ban-verdict.ts`) aux chiffres figés de `SITE_FACTS.banTop25`.

Sorties (dans `<dossier>/<label>/`) : `listes.csv` (une ligne par liste retenue), `classement.csv` (classement
`ban_radar` TCG du jour, celui qu'écrirait `build_ban_radar.py`), `resume.txt`.

Option du backtest passée à `backtest_lists` : `--connus-a-la-coupure` (TOK-137, `require_uploaded=True` : seulement
les decks mis en ligne avant la coupure).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_radar as radar  # noqa: E402

TOP_N = 25   # comme build_ban_history.TOP_N


def measure(conn: sqlite3.Connection, **kw) -> pd.DataFrame:
    rows = []
    for fmt in ("TCG", "OCG"):
        for r in radar.backtest_lists(conn, fmt, **kw):
            if not r["retained"]:
                continue
            df, ranked = r["ranking"], r["ranked"]
            n = len(df)
            ranks = np.array([k for _, k in ranked])
            base = df.ubiquity.rank(ascending=False, method="average")
            base_ranks = np.array([base[c] for c, _ in ranked])
            rows.append({
                "format": fmt, "effective": r["effective"], "as_of": r["as_of"], "n_decks": r["n_decks"],
                "n_cards": n, "n_hits": len(r["hits"]), "n_ranked": len(ranked),
                "median_rank": int(f"{np.median(ranks):.0f}"), "median_pct": float(np.median(ranks) / n * 100),
                "top25": int((ranks <= TOP_N).sum()),
                "staples_median": int(f"{np.median(base_ranks):.0f}"),
                "staples_median_pct": float(np.median(base_ranks) / n * 100),
                "staples_top25": int((base_ranks <= TOP_N).sum()),
                "random_median": int(f"{n / 2:.0f}"),
            })
    return pd.DataFrame(rows)


def summary(lists: pd.DataFrame) -> str:
    out = []
    for fmt, g in lists.groupby("format", sort=False):
        better_med = int((g.median_rank < g.staples_median).sum())
        better_top = int((g.top25 > g.staples_top25).sum())
        worse_top = int((g.top25 < g.staples_top25).sum())
        n_signed = better_top + worse_top
        p_top = binomtest(better_top, n_signed).pvalue if n_signed else float("nan")
        n_med = int((g.median_rank != g.staples_median).sum())
        p_med = binomtest(better_med, n_med).pvalue if n_med else float("nan")
        out.append(
            f"{fmt} : {len(g)} listes | top 25 radar {g.top25.sum()} contre staples {g.staples_top25.sum()} "
            f"(radar mieux {better_top}, moins bien {worse_top}, signe p = {p_top:.3f}) | rang médian meilleur que "
            f"les staples sur {better_med} listes (p = {p_med:.3f}) | rang médian moyen {g.median_pct.mean():.1f} % "
            f"de l'univers (staples {g.staples_median_pct.mean():.1f} %, hasard 50 %)")
    return "\n".join(out)


def ranking_today(conn: sqlite3.Connection) -> pd.DataFrame:
    (as_of,) = conn.execute("SELECT MAX(created) FROM tournament_decks WHERE ocg = 0").fetchone()
    df = radar.build(conn, as_of[:10], "TCG")
    return df[["card_name", "ban_risk_score", "risk_label", "bridge"]].assign(rank=np.arange(1, len(df) + 1))


def compare(a: Path, b: Path) -> None:
    la, lb = pd.read_csv(a / "listes.csv"), pd.read_csv(b / "listes.csv")
    m = la.merge(lb, on=["format", "effective"], suffixes=("_a", "_b"))
    print(f"Listes : {len(la)} ({a.name}) / {len(lb)} ({b.name}) / {len(m)} communes")
    cols = ["format", "effective", "n_decks_a", "n_decks_b", "n_cards_a", "n_cards_b", "median_rank_a",
            "median_rank_b", "top25_a", "top25_b", "staples_median_a", "staples_median_b",
            "staples_top25_a", "staples_top25_b"]
    print(m[cols].to_string(index=False))
    print(f"\n{a.name} :\n" + summary(la))
    print(f"\n{b.name} :\n" + summary(lb))
    ra, rb = pd.read_csv(a / "classement.csv"), pd.read_csv(b / "classement.csv")
    j = ra.merge(rb, on="card_name", suffixes=("_a", "_b"))
    rho = spearmanr(j.rank_a, j.rank_b).statistic
    for k in (10, 25, 50):
        common = len(set(ra.card_name[:k]) & set(rb.card_name[:k]))
        print(f"Classement du jour, top {k} : {common} cartes communes")
    shift = (j.rank_a - j.rank_b).abs()
    lab = (j.risk_label_a != j.risk_label_b).sum()
    print(f"Classement du jour : {len(ra)} / {len(rb)} cartes, Spearman {rho:.4f}, déplacement médian "
          f"{shift.median():.0f} rang(s), maximal {shift.max():.0f}, libellé de risque changé pour {lab} cartes")
    top = j.sort_values("rank_b").head(25)
    print(top[["card_name", "rank_a", "rank_b", "ban_risk_score_a", "ban_risk_score_b", "bridge_a",
               "bridge_b"]].to_string(index=False))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--label", default="mesure")
    ap.add_argument("--compare", nargs=2, type=Path, metavar=("A", "B"))
    ap.add_argument("--connus-a-la-coupure", action="store_true",
                    help="backtest sur les seuls decks mis en ligne avant la coupure (TOK-137)")
    a = ap.parse_args()
    if a.compare:
        compare(*a.compare)
        return 0
    if not (a.db and a.out):
        ap.error("--db et --out requis (ou --compare)")
    conn = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    kw = {"require_uploaded": True} if a.connus_a_la_coupure else {}
    lists = measure(conn, **kw)
    rank = ranking_today(conn)
    d = a.out / a.label
    d.mkdir(parents=True, exist_ok=True)
    lists.to_csv(d / "listes.csv", index=False)
    rank.to_csv(d / "classement.csv", index=False)
    s = summary(lists)
    (d / "resume.txt").write_text(s + "\n")
    print(lists.to_string(index=False))
    print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
