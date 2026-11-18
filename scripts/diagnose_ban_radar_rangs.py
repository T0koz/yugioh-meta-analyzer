"""
TOK-120 — Ban Radar : critères en rangs centiles par liste, régression logistique conditionnelle, pont daté (B5).

Lecture seule. N'écrit rien en base, ne modifie ni `WEIGHTS` ni le calcul du score servi. Suite du diagnostic
TOK-115 (`diagnose_ban_radar.py`, dont il réutilise les fonctions : jeu de données, mesures, bootstrap, test du signe,
dates d'annonce du lot 21).

    python scripts/diagnose_ban_radar_rangs.py --db <base> --out <dossier>                    # veille de l'entrée en vigueur
    python scripts/diagnose_ban_radar_rangs.py --db <base> --out <dossier> --coupure contenu  # veille du contenu (lot 21)
    python scripts/diagnose_ban_radar.py --rangs --db <base> --out <dossier>                 # même chose, depuis TOK-115

Questions :
1. Ramener chaque critère à son rang centile dans la liste (0 à 1, égalités au rang moyen) rend-il les poids écrits
   égaux aux poids effectifs, et ce score fait-il mieux que les poids actuels et que les staples ?
2. Une régression logistique **conditionnelle par liste** (vraisemblance de « quelles k cartes parmi les n de la liste
   sont touchées », approximation de Breslow, vérifiée contre la vraisemblance exacte) estime des poids qui ne servent qu'à classer à
   l'intérieur d'une liste, ce que fait le Ban Radar ; fait-elle mieux que la logistique ordinaire de TOK-115 ?
3. Le critère `bridge` recalculé à la date de coupure (`bridge_date.py`, decks mis en ligne avant la coupure
   seulement) change-t-il quelque chose ?

Méthode (identique à TOK-115) : validation temporelle à fenêtre croissante, au moins 3 listes d'entraînement, une
liste ne sert à l'entraînement que si elle est entrée en vigueur avant la coupure de la liste testée ; 7 listes
tenues à l'écart par format ; mesures par liste (rang médian des cartes touchées, top 25, AUC, précision moyenne) ;
bootstrap par liste (10 000 tirages, graine 120) et test du signe.

**Candidats et règle d'adoption, figés avant toute lecture des résultats** (opérationnalisation de la règle de
TOK-115, « battre les poids actuels ET les staples sur les listes tenues à l'écart ») :
- candidats : `rangs_poids_ecrits` (poids actuels appliqués aux rangs centiles, aucun paramètre estimé) et
  `clogit_rangs` (logit conditionnel sur les rangs centiles, listes TCG et OCG ensemble) ;
- dans un format, la règle est remplie si le candidat fait mieux que les poids actuels ET que les staples en rang
  médian (moyenne des rangs médians en % de l'univers) et sur au moins 5 des 7 listes tenues à l'écart pour chacune
  des deux comparaisons, sans placer moins de cartes touchées dans son top 25 (total des 7 listes) que les poids
  actuels ;
- adoption proposée seulement si la règle est remplie en TCG ET en OCG, aux deux coupures (veille de l'entrée en
  vigueur, veille du contenu). Un écart n'est dit « démontré » que si le test du signe donne p < 0,05.
Les autres méthodes (`clogit_brut`, `clogit_rangs_format`, `poids_actuels_pont_date`, `rangs_pont_actuel`,
`logit_6`) sont des descriptions qui aident à lire les candidats, pas des candidats.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_radar as radar  # noqa: E402
import diagnose_ban_radar as diag  # noqa: E402
from bridge_date import DatedGraph  # noqa: E402

FEATURES = diag.FEATURES
DATED = [f if f != "bridge" else "bridge_date" for f in FEATURES]     # critères avec le pont daté
RANKS = [f"r_{f}" for f in DATED]                                       # rangs centiles (pont daté)
RANKS_OLD_BRIDGE = [f"r_{f}" for f in FEATURES]                         # rangs centiles (pont actuel)
W = pd.Series(radar.WEIGHTS)
CALIBRATION_DATE = "2026-08-14"     # poids posés à la main ce jour-là (context.md)
CANDIDATES = ("rangs_poids_ecrits", "clogit_rangs")
SEED = 120


# --------------------------------------------------------------------------- données

def dataset(conn: sqlite3.Connection, coupure: str, graph: DatedGraph) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Jeu de données TOK-115 à la coupure choisie, enrichi du pont daté et des rangs centiles par liste."""
    if coupure == "effective":
        data, lists = diag.scenario_dataset(conn, {})
    else:
        _, base_lists = diag.scenario_dataset(conn, {})
        ref = set(zip(base_lists[base_lists.retained == 1].format, base_lists[base_lists.retained == 1].effective))
        over = {k: v for k, v in diag.announcement_overrides(conn)["contenu"].items() if k in ref}
        data, lists = diag.scenario_dataset(conn, over)
    lists = lists[lists.retained == 1].reset_index(drop=True)

    parts = []
    for (fmt, eff), g in data.groupby(["format", "effective"], sort=False):
        g = g.copy()
        g["bridge_date"] = graph.bridge(g.as_of.iloc[0], pd.Index(g.card_name)).to_numpy()
        for f in FEATURES + ["bridge_date"]:
            g[f"r_{f}"] = g[f].rank(method="average", pct=True)
        g["list_id"] = f"{fmt}|{eff}"
        parts.append(g)
    return pd.concat(parts, ignore_index=True), lists


def graph_summary(graph: DatedGraph, lists: pd.DataFrame, conn: sqlite3.Connection) -> pd.DataFrame:
    """Taille du graphe daté à chaque coupure, et accord avec le pont actuel (`card_graph_metrics`)."""
    current = pd.read_sql_query("SELECT card_name, betweenness FROM card_graph_metrics", conn) \
        .set_index("card_name").betweenness
    rows = []
    for as_of in sorted(lists.as_of.unique()):
        g = graph.at(as_of)
        bc = g["betweenness"]
        common = bc.index.intersection(current.index)
        rows.append({"as_of": as_of, "decks_connus": g["n_decks"], "noeuds": g["n_nodes"], "aretes": g["n_edges"],
                     "noeuds_communs_avec_actuel": len(common),
                     "spearman_avec_actuel": bc[common].corr(current[common], method="spearman")})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- modèles

def _breslow(beta: np.ndarray, X: np.ndarray, y: np.ndarray, starts: np.ndarray, k: np.ndarray):
    """− log-vraisemblance conditionnelle (approximation de Breslow) et son gradient.

    Pour chaque liste g : Σ_{i touchée} η_i − k_g · log Σ_{i ∈ g} exp(η_i). Les données sont triées par liste,
    `starts` donne le début de chaque liste. L'approximation traite les k cartes touchées comme k tirages
    indépendants dans la liste ; l'écart à la vraisemblance exacte est d'ordre k / n (≈ 1 % ici).
    """
    eta = X @ beta
    mx = np.maximum.reduceat(eta, starts)
    e = np.exp(eta - np.repeat(mx, np.diff(np.append(starts, len(eta)))))
    se = np.add.reduceat(e, starts)
    lse = np.log(se) + mx
    ll = float(eta[y == 1].sum() - (k * lse).sum())
    p = e / np.repeat(se, np.diff(np.append(starts, len(eta))))
    expect = np.add.reduceat(p[:, None] * X, starts, axis=0)            # E[x] dans chaque liste
    grad = X[y == 1].sum(axis=0) - (k[:, None] * expect).sum(axis=0)
    return -ll, -grad


def _prepare(train: pd.DataFrame, feats: list[str], mean, sd):
    t = train.sort_values("list_id", kind="stable")
    X = ((t[feats] - mean) / sd).to_numpy(float)
    y = t.y.to_numpy()
    codes = t.list_id.to_numpy()
    starts = np.flatnonzero(np.r_[True, codes[1:] != codes[:-1]])
    k = np.add.reduceat(y, starts).astype(float)
    return X, y, starts, k


def fit_clogit(train: pd.DataFrame, feats: list[str], standardize: bool) -> tuple[np.ndarray, pd.Series, pd.Series]:
    """Logit conditionnel par liste (Breslow), sans pénalité. Scores = ((x − m) / s) · β ; seul l'ordre compte."""
    X0 = train[feats]
    mean = X0.mean() if standardize else pd.Series(0.0, index=feats)
    sd = X0.std(ddof=0).replace(0, 1.0) if standardize else pd.Series(1.0, index=feats)
    X, y, starts, k = _prepare(train, feats, mean, sd)
    res = minimize(_breslow, np.zeros(len(feats)), args=(X, y, starts, k), jac=True, method="L-BFGS-B",
                   options={"maxiter": 5000, "gtol": 1e-8})
    return res.x, mean, sd


def exact_loglik(beta: np.ndarray, train: pd.DataFrame, feats: list[str]) -> float:
    """Log-vraisemblance conditionnelle exacte : Σ η_touchées − log e_k(exp η), e_k = polynôme symétrique
    élémentaire de degré k, calculé en log par récurrence. Sert seulement à vérifier l'approximation de Breslow."""
    X, y, starts, k = _prepare(train, feats, pd.Series(0.0, index=feats), pd.Series(1.0, index=feats))
    eta = X @ beta
    ends = np.append(starts[1:], len(eta))
    ll = 0.0
    for a, b, kk in zip(starts, ends, k.astype(int)):
        if kk == 0:
            continue
        logE = np.full(kk + 1, -np.inf)
        logE[0] = 0.0
        for v in eta[a:b]:
            logE[1:] = np.logaddexp(logE[1:], logE[:-1] + v)
        ll += eta[a:b][y[a:b] == 1].sum() - logE[kk]
    return float(ll)


def exact_check(data: pd.DataFrame) -> pd.DataFrame:
    """Poids du logit conditionnel sur les rangs : Breslow contre maximum de la vraisemblance exacte."""
    b_bres, _, _ = fit_clogit(data, RANKS, standardize=False)
    # Départ à zéro (et non au point de Breslow), pour ne pas biaiser la vérification vers l'approximation.
    res = minimize(lambda b: -exact_loglik(b, data, RANKS), np.zeros(len(RANKS)), method="Powell",
                   options={"xtol": 1e-4, "ftol": 1e-8, "maxfev": 6000})
    norm = lambda b: b / np.abs(b).sum()
    print(f"log-vraisemblance exacte : au point de Breslow {exact_loglik(b_bres, data, RANKS):.3f}, "
          f"à son propre maximum {-res.fun:.3f}")
    return pd.DataFrame({"breslow": norm(b_bres), "exacte": norm(res.x)}, index=FEATURES).round(3)


def clogit_score(params, mean, sd, test, feats) -> np.ndarray:
    return ((test[feats] - mean) / sd).to_numpy() @ params


def fixed_methods(test: pd.DataFrame) -> dict[str, np.ndarray]:
    """Méthodes sans paramètre estimé (poids actuels appliqués autrement)."""
    raw_dated = test[DATED].to_numpy() @ W.to_numpy()
    return {
        "poids_actuels_pont_date": raw_dated,
        "rangs_poids_ecrits": test[RANKS].to_numpy() @ W.to_numpy(),
        "rangs_pont_actuel": test[RANKS_OLD_BRIDGE].to_numpy() @ W.to_numpy(),
    }


def walk_forward(data: pd.DataFrame, lists: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    per_list, weights = [], []
    for fmt in ("TCG", "OCG"):
        fl = lists[lists.format == fmt].sort_values("effective").reset_index(drop=True)
        for i in range(diag.MIN_TRAIN_LISTS, len(fl)):
            row = fl.iloc[i]
            test = data[(data.format == fmt) & (data.effective == row.effective)]
            same = data[(data.format == fmt) & (data.effective < row.as_of)]
            pooled = data[data.effective < row.as_of]
            learned = fixed_methods(test)
            m6, s6 = diag.fit_logit(same, FEATURES)                      # TOK-115, pont actuel, pour mémoire
            learned["logit_6"] = diag.logit_score(m6, s6, test, FEATURES)
            b, mu, sd = fit_clogit(pooled, RANKS, standardize=False)
            learned["clogit_rangs"] = clogit_score(b, mu, sd, test, RANKS)
            weights.append({"format": fmt, "effective": row.effective, "n_train_lists": pooled.list_id.nunique(),
                            **dict(zip(DATED, np.round(b / np.abs(b).sum(), 3)))})
            b, mu, sd = fit_clogit(same, RANKS, standardize=False)
            learned["clogit_rangs_format"] = clogit_score(b, mu, sd, test, RANKS)
            b, mu, sd = fit_clogit(pooled, DATED, standardize=True)
            learned["clogit_brut"] = clogit_score(b, mu, sd, test, DATED)
            for method, m in diag.score_methods(test, learned).items():
                per_list.append({"format": fmt, "effective": row.effective, "method": method,
                                 "n_train_lists": i, "n_train_lists_tcg_ocg": pooled.list_id.nunique(), **m})
    return pd.DataFrame(per_list), pd.DataFrame(weights)


# --------------------------------------------------------------------------- lectures

def effective_weights(data: pd.DataFrame) -> pd.DataFrame:
    """Poids écrits contre poids effectifs (poids × écart type intra-liste moyen), critères bruts et en rangs."""
    out = []
    for fmt, g in data.groupby("format"):
        for label, cols in (("brut_pont_actuel", FEATURES), ("rangs_pont_date", RANKS)):
            sd = g.groupby("effective")[cols].std().mean().to_numpy()
            eff = W.to_numpy() * sd
            for f, s, e in zip(FEATURES, sd, eff / eff.sum()):
                out.append({"format": fmt, "echelle": label, "critere": f, "poids_ecrit": W[f],
                            "ecart_type": s, "poids_effectif": e})
    return pd.DataFrame(out)


def all_lists(data: pd.DataFrame) -> pd.DataFrame:
    """Méthodes sans paramètre estimé sur toutes les listes retenues (description, pas une validation)."""
    rows = []
    for (fmt, eff), g in data.groupby(["format", "effective"]):
        for method, m in diag.score_methods(g, fixed_methods(g)).items():
            rows.append({"format": fmt, "effective": eff, "method": method, **m})
    return pd.DataFrame(rows)


def comparisons(per_list: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    pairs = [(c, ref) for c in CANDIDATES for ref in ("poids_actuels", "staples")] + [
        ("clogit_brut", "poids_actuels"), ("clogit_brut", "staples"),
        ("clogit_rangs", "logit_6"), ("clogit_rangs_format", "staples"),
        ("poids_actuels_pont_date", "poids_actuels"), ("rangs_poids_ecrits", "rangs_pont_actuel"),
        ("staples", "hasard"),
    ]
    for fmt in ("TCG", "OCG"):
        for a, b in pairs:
            for metric in ("median_pct", "top25", "auc", "ap"):
                est, lo, hi, wins, n, ties = diag.bootstrap_diff(per_list, fmt, a, b, metric, rng)
                rows.append({"format": fmt, "a": a, "b": b, "mesure": metric, "ecart": est, "p05": lo, "p95": hi,
                             "a_mieux": wins, "listes": n, "egalites": ties,
                             "p_signe": diag.sign_test(wins, n, ties)})
    return pd.DataFrame(rows)


def adoption(per_list: pd.DataFrame) -> pd.DataFrame:
    """Règle figée (docstring) : candidat contre poids actuels et staples, par format."""
    rows = []
    for fmt in ("TCG", "OCG"):
        p = per_list[per_list.format == fmt]
        med = p.pivot(index="effective", columns="method", values="median_pct")
        top = p.pivot(index="effective", columns="method", values="top25")
        for c in CANDIDATES:
            r = {"format": fmt, "candidat": c, "listes": len(med)}
            ok = True
            for ref in ("poids_actuels", "staples"):
                d = med[c] - med[ref]
                r[f"rang_pct_moins_{ref}"] = round(float(d.mean()) * 100, 2)
                r[f"listes_mieux_que_{ref}"] = int((d < 0).sum())
                r[f"p_signe_{ref}"] = round(diag.sign_test(int((d < 0).sum()), len(d), int((d == 0).sum())), 3)
                ok &= bool(d.mean() < 0 and (d < 0).sum() >= 5)
            r["top25_candidat"] = int(top[c].sum())
            r["top25_poids_actuels"] = int(top.poids_actuels.sum())
            ok &= r["top25_candidat"] >= r["top25_poids_actuels"]
            r["regle_remplie"] = ok
            rows.append(r)
    return pd.DataFrame(rows)


def after_calibration(per_list: pd.DataFrame) -> pd.DataFrame:
    """Listes entrées en vigueur après le calage des poids : les seules où les poids actuels n'ont rien vu."""
    p = per_list[per_list.effective > CALIBRATION_DATE]
    return p.pivot_table(index=["format", "effective", "k", "n"], columns="method",
                         values=["median_rank", "top25"]).round(1)


def full_weights(data: pd.DataFrame, rng: np.random.Generator, n_boot: int = 1000) -> pd.DataFrame:
    """Poids du logit conditionnel sur les rangs, toutes listes (TCG + OCG), intervalle bootstrap par liste."""
    b, _, _ = fit_clogit(data, RANKS, standardize=False)
    point = pd.Series(b / np.abs(b).sum(), index=FEATURES)
    ids = data.list_id.unique()
    groups = {i: data[data.list_id == i] for i in ids}
    draws = []
    for k in range(n_boot):
        pick = rng.choice(ids, size=len(ids), replace=True)
        sample = pd.concat([groups[i].assign(list_id=f"{i}#{j}") for j, i in enumerate(pick)], ignore_index=True)
        bb, _, _ = fit_clogit(sample, RANKS, standardize=False)
        draws.append(bb / np.abs(bb).sum())
    draws = pd.DataFrame(draws, columns=FEATURES)
    return pd.DataFrame({"ecrit": W, "estime": point, "p05": draws.quantile(0.05), "p95": draws.quantile(0.95),
                         "part_positive": (draws > 0).mean()}).round(3)


# --------------------------------------------------------------------------- sortie

def run(conn: sqlite3.Connection, out: Path, coupure: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 40)
    warnings.filterwarnings("ignore", category=FutureWarning)
    rng = np.random.default_rng(SEED)

    graph = DatedGraph(conn)
    data, lists = dataset(conn, coupure, graph)
    print(f"Coupure : {coupure} — {len(lists)} listes retenues "
          f"({(lists.format == 'TCG').sum()} TCG, {(lists.format == 'OCG').sum()} OCG), "
          f"{len(data)} lignes, {int(data.y.sum())} cartes touchées classées")
    print(lists[["format", "effective", "as_of", "n", "k", "k_missing", "n_decks"]].to_string(index=False))

    print("\n== Graphe daté à chaque coupure (decks mis en ligne avant la coupure) ==")
    gs = graph_summary(graph, lists, conn)
    gs.to_csv(out / "graphe_date.csv", index=False)
    print(gs.round(3).to_string(index=False))
    corr = data.groupby(["format", "effective"]).apply(
        lambda g: g.bridge.corr(g.bridge_date, method="spearman"), include_groups=False)
    print(f"Pont actuel contre pont daté, corrélation de rang dans l'univers de chaque liste : médiane "
          f"{corr.median():.3f} (min {corr.min():.3f}, max {corr.max():.3f})")
    for name, col in (("pont actuel", "bridge"), ("pont daté", "bridge_date")):
        auc = data.groupby(["format", "effective"]).apply(lambda g: roc_auc_score(g.y, g[col]),
                                                           include_groups=False)
        print(f"AUC du {name} seul : TCG {auc.loc['TCG'].mean():.3f}, OCG {auc.loc['OCG'].mean():.3f}")

    print("\n== Poids écrits et poids effectifs ==")
    ew = effective_weights(data)
    ew.to_csv(out / "poids_effectifs.csv", index=False)
    tab = ew.pivot_table(index="critere", columns=["echelle", "format"], values="poids_effectif").loc[FEATURES]
    tab.columns = [f"{e}_{f}" for e, f in tab.columns]
    print(tab.assign(poids_ecrit=W).round(3).to_string())

    print("\n== Méthodes sans paramètre estimé, toutes les listes retenues (description) ==")
    al = all_lists(data)
    al.to_csv(out / "toutes_listes.csv", index=False)
    print(al.groupby(["format", "method"]).agg(listes=("effective", "nunique"),
                                               mediane_des_rangs_medians=("median_rank", "median"),
                                               rang_median_pct_moy=("median_pct", "mean"),
                                               top25_total=("top25", "sum"), auc_moy=("auc", "mean"))
          .round(3).to_string())

    per_list, wsteps = walk_forward(data, lists)
    per_list.to_csv(out / "par_liste.csv", index=False)
    wsteps.to_csv(out / "poids_clogit_par_pas.csv", index=False)

    print(f"\n== Validation temporelle (au moins {diag.MIN_TRAIN_LISTS} listes d'entraînement) : synthèse ==")
    print(diag.summarize(per_list).to_string())

    print("\n== Par liste tenue à l'écart : rang médian ==")
    print(per_list.pivot_table(index=["format", "effective", "k", "n"], columns="method",
                               values="median_rank").round(1).to_string())
    print("\n== Par liste tenue à l'écart : top 25 ==")
    print(per_list.pivot_table(index=["format", "effective"], columns="method", values="top25").to_string())

    print("\n== Écarts, bootstrap par liste (intervalle 90 %) et test du signe ==")
    cmp_ = comparisons(per_list, rng)
    cmp_.to_csv(out / "bootstrap.csv", index=False)
    print(cmp_.round(4).to_string(index=False))

    print("\n== Règle d'adoption (figée avant lecture) ==")
    ad = adoption(per_list)
    ad.to_csv(out / "adoption.csv", index=False)
    print(ad.to_string(index=False))

    print(f"\n== Listes postérieures au calage des poids ({CALIBRATION_DATE}) ==")
    print(after_calibration(per_list).to_string())

    print("\n== Poids du logit conditionnel sur les rangs à chaque pas (|somme| = 1, TCG + OCG) ==")
    print(wsteps.to_string(index=False))

    print("\n== Poids du logit conditionnel sur les rangs, toutes les listes, intervalle bootstrap par liste (90 %) ==")
    fw = full_weights(data, rng)
    fw.to_csv(out / "poids_clogit_rangs.csv")
    print(fw.to_string())

    print("\n== Vérification : approximation de Breslow contre vraisemblance conditionnelle exacte (toutes les listes) ==")
    print(exact_check(data).to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=diag.DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=Path("diagnostic_ban_radar_rangs"))
    parser.add_argument("--coupure", choices=["effective", "contenu"], default="effective",
                        help="effective = veille de l'entrée en vigueur (référence TOK-115) ; contenu = veille du "
                             "jour où les cartes touchées sont devenues publiques (banlist_announcements, lot 21)")
    args = parser.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=60)
    run(conn, args.out, args.coupure)


if __name__ == "__main__":
    main()
