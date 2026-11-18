"""
TOK-131 (B4) - Intervalles de prevision par archetype pour les predictions meta.

LECTURE SEULE par defaut (base ouverte en `mode=ro`). Rien n'est ecrit sans `--write`.

    python scripts/build_prediction_intervals.py                 # evaluation + intervalles courants (~10 s)
    python scripts/build_prediction_intervals.py --boot 300      # test rapide
    python scripts/build_prediction_intervals.py --json out.json # dump des chiffres
    python scripts/build_prediction_intervals.py --db /chemin/copie.db --write   # table nouvelle
    python scripts/build_prediction_intervals.py --db data/yugioh.db --write --reference  # base de reference

Prevision evaluee : celle qui est servie, `p = max(niveau + 0,3 * delta_Ridge, 0)` (notebook 05,
ensemble 70 % naif + 30 % Ridge). Residus du walk-forward strict reproduit par
`scripts/evaluate_prediction.py` (`build_dataset`, `walk_forward`, importes, pas recopies), sur la
table `meta_scores` (TCG pur depuis TOK-80) comme le notebook.

Conformite sequentielle : pour le mois de test t, tout quantile ou toute echelle se calcule sur les
seuls residus des mois < t. La cible d'une ligne du mois s est le mois s + 1 : a la fin du mois t,
les cibles des lignes s < t sont connues. Meme regle que l'entrainement du walk-forward.

=====================================================================================
PROTOCOLE FIGE AVANT LA PREMIERE EXECUTION (aucun chiffre de couverture vu avant)
=====================================================================================
Mois : les 27 mois de test du walk-forward (2024-08 -> 2026-10). Les 3 premiers (2024-08 a
2024-10, 75 lignes) servent d'amorce de calibration seulement ; le critere porte sur les 24
suivants (2024-11 -> 2026-10), meme fenetre que `docs/evaluation-prediction.md`. Le dernier mois
(cible 2026-11, partielle) est garde dans le critere et retire en sensibilite.

Niveau nominal : 80 %. Borne basse tronquee a 0 (une part ne peut pas etre negative ; la cible est
toujours >= 0, donc la troncature ne change jamais la couverture, seulement la largeur).

Candidats (calibration cumulative : tous les residus des mois < t) :
  ABS       score |e|, quantile conforme d'ordre ceil((n+1)*0,8) ; intervalle p +/- q.
  ACI       ABS avec niveau adaptatif (Gibbs et Candes 2021) : alpha_{t+1} = alpha_t +
            gamma * (0,2 - taux de non-couverture du mois t), gamma = 0,05 (fixe a la main,
            declare) ; niveau borne a n/(n+1) (plus grand residu) quand alpha <= 0.
  NORM      score |e| / s(niveau), s = a + b * niveau ajuste par MCO sur les residus passes,
            plancher 0,25 * mediane(|e| passes) (garde-fou numerique, fixe a la main) ;
            intervalle p +/- q * s(niveau).
  MONDRIAN  ABS par classe de niveau (terciles du niveau calcules sur la calibration passee) ;
            repli sur ABS global si une classe a moins de 20 residus passes.
Methodes naives (memes mois, meme calibration cumulative) :
  N-PERS    centre = niveau du mois (persistance), +/- quantile conforme des |y - niveau| passes.
  N-GAUSS   centre = p, +/- 1,2816 * ecart type des residus passes.
Sensibilite (non candidate) : ABS en fenetre glissante de 12 mois.

AJOUT APRES LA PREMIERE EXECUTION (exploratoire, jamais retenu par la regle) : ASYM et
MONDRIAN-ASYM, quantiles conformes SIGNES separes pour chaque queue (ordre floor((n+1)*0,1) et
ceil((n+1)*0,9) des residus e = y - p), global ou par classe de niveau. Motif : les rates du tiers
haut tombent surtout sous la borne basse (la prevision n'applique que 30 % du retour a la moyenne).
A pre-enregistrer avant toute adoption sur des mois nouveaux.

Critere du ticket : couverture globale observee sur les 24 mois dans [75 % ; 85 %].
Regle d'adoption :
  (1) couverture globale dans [75 ; 85] % ;
  (2) couverture du tiers superieur de niveau (terciles du niveau sur les lignes evaluees) dans
      [70 ; 90] % (tolerance doublee : un tiers des lignes) ;
  (3) parmi les candidats qui remplissent (1) et (2) : plus petit score de Winkler moyen ;
      egalite (ecart < 1 %) departagee par simplicite : ABS, MONDRIAN, NORM, ACI ;
  (4) le retenu est compare aux deux naives (Winkler, ecart bootstrap par mois) ; s'il ne bat pas
      N-GAUSS, c'est dit, sans changer le choix.
  Si aucun candidat ne remplit (1) et (2) : critere non atteint, rien n'est recommande a l'affichage.
Bootstrap : 2 000 tirages des MOIS (iid, et blocs de 3 mois consecutifs), graine 42.
=====================================================================================

Ecriture (`--write`) : table NOUVELLE `meta_prediction_intervals` (jamais une table existante),
transaction unique, pour les lignes de `meta_predictions` du dernier `data_month` (celles que
sert l'API). Refuse la base du depot principal sans `--reference`.
"""
import argparse
import datetime
import json
import math
import sqlite3
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate_prediction as ep  # noqa: E402

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
LEVEL = 0.8
ALPHA_MISS = 1 - LEVEL
Z80 = 1.2815515655446004
N_SEED_MONTHS = 3
N_EVAL_MONTHS = 24
GAMMA_ACI = 0.05
NORM_FLOOR_FRAC = 0.25
MONDRIAN_MIN = 20
SLIDING_MONTHS = 12
SEED = 42
CANDIDATES = ["ABS", "MONDRIAN", "NORM", "ACI"]  # ordre de simplicite (departage)
NAIVES = ["N-PERS", "N-GAUSS"]
EXPLORATORY = ["ASYM", "MONDRIAN-ASYM"]  # ajoutes apres lecture, jamais adoptes
TABLE = "meta_prediction_intervals"


# ---------------------------------------------------------------------------
# Donnees
# ---------------------------------------------------------------------------
def connect(db_path):
    return sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro", uri=True)


def load_ms(con, table="meta_scores"):
    ms = pd.read_sql(f"SELECT month, archetype, share, avg_placement, meta_score FROM {table} "
                     "ORDER BY month, archetype", con)
    ms["month"] = pd.to_datetime(ms["month"])
    return ms


def residual_frame(con, table="meta_scores"):
    """Walk-forward strict (evaluate_prediction) -> une ligne par (mois, archetype) teste."""
    ms = load_ms(con, table)
    ds = ep.build_dataset(ms, con)
    R = ep.walk_forward(ds)
    R["p"] = np.maximum(R["cur"] + ep.W_MODEL * R["d_ridge"], 0.0)
    R["y"] = R["nxt"]
    R["e"] = R["y"] - R["p"]
    R["e_pers"] = R["y"] - R["cur"]
    R["rank_in_month"] = R.groupby("month")["cur"].rank(ascending=False, method="first")
    tot = pd.read_sql(f"SELECT month, MAX(total_decks) AS n FROM {table} GROUP BY month", con)
    tot = dict(zip(pd.to_datetime(tot["month"]), tot["n"]))
    R["n_decks_target"] = [tot.get(m + pd.offsets.MonthBegin(1)) for m in R["month"]]
    R["n_decks_cur"] = [tot.get(m) for m in R["month"]]
    return R.sort_values(["month", "archetype"]).reset_index(drop=True), ms, ds


# ---------------------------------------------------------------------------
# Conformite
# ---------------------------------------------------------------------------
def conformal_q(scores, level):
    """Quantile conforme : k-ieme plus petit score, k = ceil((n+1)*level). inf si k > n."""
    s = np.sort(np.asarray(scores, float))
    n = len(s)
    if n == 0:
        return math.inf
    k = math.ceil((n + 1) * level - 1e-12)
    return float(s[k - 1]) if k <= n else math.inf


def signed_q(e):
    """Bornes conformes signees (queues separees) : (k_lo-ieme, k_hi-ieme plus petit residu)."""
    s = np.sort(np.asarray(e, float))
    n = len(s)
    k_lo = math.floor((n + 1) * ALPHA_MISS / 2 + 1e-12)
    k_hi = math.ceil((n + 1) * (1 - ALPHA_MISS / 2) - 1e-12)
    lo = float(s[k_lo - 1]) if k_lo >= 1 else -math.inf
    hi = float(s[k_hi - 1]) if k_hi <= n else math.inf
    return lo, hi


def scale_fit(cal):
    """s(niveau) = a + b*niveau, MCO de |e| sur le niveau, plancher declare."""
    x, y = cal["cur"].values, np.abs(cal["e"].values)
    X = np.column_stack([np.ones_like(x), x])
    a, b = np.linalg.lstsq(X, y, rcond=None)[0]
    floor = NORM_FLOOR_FRAC * float(np.median(y))
    return float(a), float(b), floor


def scale_eval(a, b, floor, x):
    return np.maximum(a + b * np.asarray(x, float), floor)


def method_interval(method, cal, te, aci_level=None):
    """Retourne (centre, ecart vers le bas, ecart vers le haut) pour `te`, calibre sur `cal`."""
    c, lo, hi = _method_interval(method, cal, te, aci_level)
    return c, lo, (lo if hi is None else hi)


def _method_interval(method, cal, te, aci_level=None):
    p = te["p"].values
    n = len(cal)
    if method == "ASYM":
        ql, qh = signed_q(cal["e"])
        return p, np.full(len(te), -ql), np.full(len(te), qh)
    if method == "MONDRIAN-ASYM":
        edges = np.quantile(cal["cur"].values, [1 / 3, 2 / 3])
        cls_cal = np.digitize(cal["cur"].values, edges)
        cls_te = np.digitize(te["cur"].values, edges)
        gl, gh = signed_q(cal["e"])
        lo, hi = np.empty(len(te)), np.empty(len(te))
        for k in range(3):
            ek = cal["e"].values[cls_cal == k]
            ql, qh = signed_q(ek) if len(ek) >= MONDRIAN_MIN else (gl, gh)
            lo[cls_te == k], hi[cls_te == k] = -ql, qh
        return p, lo, hi
    if method in ("ABS", "ABS-12M"):
        return p, np.full(len(te), conformal_q(np.abs(cal["e"]), LEVEL)), None
    if method == "ACI":
        lvl = min(max(aci_level, 0.0), n / (n + 1))
        return p, np.full(len(te), conformal_q(np.abs(cal["e"]), lvl)), None
    if method == "NORM":
        a, b, fl = scale_fit(cal)
        q = conformal_q(np.abs(cal["e"].values) / scale_eval(a, b, fl, cal["cur"]), LEVEL)
        return p, q * scale_eval(a, b, fl, te["cur"]), None
    if method == "MONDRIAN":
        edges = np.quantile(cal["cur"].values, [1 / 3, 2 / 3])
        cls_cal = np.digitize(cal["cur"].values, edges)
        cls_te = np.digitize(te["cur"].values, edges)
        q_glob = conformal_q(np.abs(cal["e"]), LEVEL)
        hw = np.empty(len(te))
        for c in range(3):
            sc = np.abs(cal["e"].values[cls_cal == c])
            hw[cls_te == c] = conformal_q(sc, LEVEL) if len(sc) >= MONDRIAN_MIN else q_glob
        return p, hw, None
    if method == "N-PERS":
        return te["cur"].values, np.full(len(te), conformal_q(np.abs(cal["e_pers"]), LEVEL)), None
    if method == "N-GAUSS":
        return p, np.full(len(te), Z80 * float(np.std(cal["e"].values, ddof=1))), None
    raise ValueError(method)


def run_method(R, method, eval_months):
    """Boucle sequentielle sur les mois evalues. Calibration = mois < t (cumulative, ou 12 mois)."""
    out, aci_alpha = [], ALPHA_MISS
    for t in eval_months:
        cal = R[R["month"] < t]
        if method == "ABS-12M":
            cal = cal[cal["month"] >= t - pd.DateOffset(months=SLIDING_MONTHS)]
        te = R[R["month"] == t]
        c, hl, hh = method_interval(method, cal, te, aci_level=1 - aci_alpha)
        lo, hi = np.maximum(c - hl, 0.0), c + hh
        y = te["y"].values
        cov = (y >= lo) & (y <= hi)
        cov_untrunc = (y >= c - hl) & (y <= hi)
        out.append(te.assign(method=method, center=c, lo=lo, hi=hi, covered=cov,
                             covered_untrunc=cov_untrunc, calibration_n=len(cal),
                             aci_level=(1 - aci_alpha) if method == "ACI" else np.nan))
        if method == "ACI":
            aci_alpha = aci_alpha + GAMMA_ACI * (ALPHA_MISS - (1 - cov.mean()))
    return pd.concat(out, ignore_index=True), aci_alpha


def winkler(lo, hi, y, alpha=ALPHA_MISS):
    return (hi - lo) + (2 / alpha) * np.maximum(lo - y, 0) + (2 / alpha) * np.maximum(y - hi, 0)


# ---------------------------------------------------------------------------
# Mesures
# ---------------------------------------------------------------------------
def summarize(I, edges):
    w = winkler(I["lo"].values, I["hi"].values, I["y"].values)
    terc = np.digitize(I["cur"].values, edges)
    top5 = I["rank_in_month"].values <= 5
    o = {
        "n_rows": int(len(I)), "n_months": int(I["month"].nunique()),
        "coverage": float(I["covered"].mean()),
        "coverage_untruncated": float(I["covered_untrunc"].mean()),
        "width_mean": float((I["hi"] - I["lo"]).mean()),
        "width_median": float((I["hi"] - I["lo"]).median()),
        "winkler_mean": float(w.mean()),
        "share_lo_truncated": float((I["lo"] <= 0).mean()),
        "miss_below": float((I["y"] < I["lo"]).mean()), "miss_above": float((I["y"] > I["hi"]).mean()),
    }
    for c, nm in enumerate(["T1_bas", "T2_milieu", "T3_haut"]):
        m = terc == c
        o[f"coverage_{nm}"] = float(I["covered"].values[m].mean())
        o[f"width_{nm}"] = float((I["hi"] - I["lo"]).values[m].mean())
        o[f"n_{nm}"] = int(m.sum())
        o[f"miss_below_{nm}"] = float((I["y"].values[m] < I["lo"].values[m]).mean())
        o[f"miss_above_{nm}"] = float((I["y"].values[m] > I["hi"].values[m]).mean())
    o["coverage_top5"] = float(I["covered"].values[top5].mean())
    o["width_top5"] = float((I["hi"] - I["lo"]).values[top5].mean())
    o["n_top5"] = int(top5.sum())
    return o


def monthly_cov(I):
    g = I.groupby("month")
    return pd.DataFrame({"n": g.size(), "coverage": g["covered"].mean(),
                         "width": g.apply(lambda t: float((t["hi"] - t["lo"]).mean())),
                         "n_decks_target": g["n_decks_target"].first()})


def boot_months(I_by_method, B, block, seed, ref=None):
    """Couverture poolee et Winkler par tirage des mois. Ecart de Winkler vs `ref` si fourni."""
    rng = np.random.default_rng(seed)
    months = sorted(next(iter(I_by_method.values()))["month"].unique())
    agg = {}
    for m, I in I_by_method.items():
        w = winkler(I["lo"].values, I["hi"].values, I["y"].values)
        agg[m] = (I.assign(w=w).groupby("month")
                  .agg(k=("covered", "sum"), n=("covered", "size"), w=("w", "sum")).reindex(months))
    res = {m: {"cov": [], "wink": []} for m in I_by_method}
    if ref:
        for m in I_by_method:
            res[m]["d_wink_vs_ref"] = []
    for _ in range(B):
        idx = ep.sample_blocks(rng, len(months), block)
        for m, a in agg.items():
            k, n, w = a["k"].values[idx].sum(), a["n"].values[idx].sum(), a["w"].values[idx].sum()
            res[m]["cov"].append(k / n)
            res[m]["wink"].append(w / n)
        if ref:
            for m in I_by_method:
                res[m]["d_wink_vs_ref"].append(res[m]["wink"][-1] - res[ref]["wink"][-1])
    return {m: {k: ep.pct_ci(v) for k, v in d.items()} for m, d in res.items()}


def lag1_autocorr(x):
    x = np.asarray(x, float)
    return float(np.corrcoef(x[:-1], x[1:])[0, 1]) if len(x) > 3 else float("nan")


def adopt(summ):
    elig = [m for m in CANDIDATES
            if 0.75 <= summ[m]["coverage"] <= 0.85 and 0.70 <= summ[m]["coverage_T3_haut"] <= 0.90]
    if not elig:
        return None, elig
    best = min(summ[m]["winkler_mean"] for m in elig)
    for m in CANDIDATES:  # ordre de simplicite
        if m in elig and summ[m]["winkler_mean"] <= best * 1.01:
            return m, elig
    return None, elig


# ---------------------------------------------------------------------------
# Prevision courante (copie de la cellule 11 du notebook 05, absente d'evaluate_prediction)
# ---------------------------------------------------------------------------
def production_predictions(con, ms, ds):
    """Reconstruit `meta_predictions` comme le notebook 05 (cellule 11), sans rien ecrire.
    `ms_clean` (avant fillna) et `banl_feat` sont recalcules : `groupby().last()` du notebook
    prend la derniere valeur NON NULLE par colonne, il faut les NaN d'origine."""
    ms = ms.copy()
    g = ms.sort_values(["archetype", "month"]).groupby("archetype")
    for col in ["meta_score", "share", "avg_placement"]:
        for lag in [1, 2, 3]:
            ms[f"{col}_t{lag}"] = g[col].shift(lag)
    ms["delta_1m"] = ms["meta_score"] - ms["meta_score_t1"]
    ms["delta_2m"] = ms["meta_score"] - ms["meta_score_t2"]
    ms["accel"] = ms["delta_1m"] - (ms["meta_score_t1"] - ms["meta_score_t2"])
    ms["roll_mean_3m"] = g["meta_score"].transform(lambda x: x.shift(1).rolling(3, min_periods=2).mean())
    ms["rank_month"] = ms.groupby("month")["meta_score"].rank(pct=True)
    ms["rank_t1"] = ms.groupby("month")["meta_score_t1"].rank(pct=True)
    ms["meta_score_next"] = g["meta_score"].shift(-1)
    ms["month_next"] = g["month"].shift(-1)
    ms["delta_next"] = ms["meta_score_next"] - ms["meta_score"]
    clean = ms.dropna(subset=["meta_score_next", "meta_score_t1", "delta_next"])
    clean = clean[(clean["month_next"] - clean["month"]).dt.days.between(25, 35)]

    n_cards = pd.read_sql("SELECT archetype, COUNT(*) AS n_cards FROM cards WHERE archetype IS NOT NULL "
                          "GROUP BY archetype", con)
    banl = pd.read_sql("""SELECT month, archetype, n_forbidden, n_limited AS bl_n_limited, n_semi,
                          ban_severity, was_hit_recent, ban_severity_t1 FROM banlist_features""", con)
    banl["month"] = pd.to_datetime(banl["month"])
    banl = banl.merge(n_cards, on="archetype", how="left")
    banl["trend_ratio_monthly"] = (banl["bl_n_limited"] + banl["n_semi"]) / (banl["n_cards"].fillna(1) + 1)

    months = sorted(ds["month"].unique())
    tr = ds["month"].isin(months[-ep.WINDOW:])
    sc, mdl = StandardScaler(), Ridge(alpha=ep.ALPHA)
    mdl.fit(sc.fit_transform(ds.loc[tr, ep.FEATURE_COLS].values), ds.loc[tr, "delta_next"].values)

    cutoff = ds["month"].max() - pd.DateOffset(months=4)
    last = clean[clean["month"] >= cutoff].sort_values("month").groupby("archetype").last().reset_index()
    last_banl = (banl.sort_values("month").groupby("archetype").last().reset_index()
                 [["archetype", "ban_severity", "n_forbidden", "was_hit_recent", "ban_severity_t1",
                   "trend_ratio_monthly"]])
    last = last.merge(last_banl, on="archetype", how="left").fillna(0)
    debut = ms.groupby("archetype")["month"].min().rename("debut_month").reset_index()
    last = last.merge(debut, on="archetype", how="left")
    last["months_since_debut"] = ((last["month"].dt.year - last["debut_month"].dt.year) * 12
                                  + (last["month"].dt.month - last["debut_month"].dt.month))
    for col in ep.FEATURE_COLS:
        if col not in last.columns:
            last[col] = 0.0
    d = mdl.predict(sc.transform(last[ep.FEATURE_COLS].fillna(0).values))
    last["pred_delta"] = d
    last["pred_meta_score"] = (last["meta_score"] + ep.W_MODEL * d).clip(lower=0)
    last["data_month"] = last["month"].dt.strftime("%Y-%m")
    return last[["archetype", "data_month", "meta_score", "pred_delta", "pred_meta_score"]]


def current_intervals(R, served, method, aci_level_next):
    """Intervalles des previsions servies : calibration = residus des mois < data_month."""
    rows = []
    for dm, grp in served.groupby("data_month"):
        t = pd.Timestamp(dm + "-01")
        cal = R[R["month"] < t]
        te = pd.DataFrame({"p": grp["pred_meta_score"].values, "cur": grp["meta_score_current"].values})
        lvl = aci_level_next if method == "ACI" else None
        c, hl, hh = method_interval(method, cal, te, aci_level=lvl)
        target = (t + pd.offsets.MonthBegin(1)).strftime("%Y-%m")
        for a, pc, l_, h_ in zip(grp["archetype"], c, hl, hh):
            rows.append({"archetype": a, "data_month": dm, "target_month": target, "pred": float(pc),
                         "lo": float(max(pc - l_, 0.0)), "hi": float(pc + h_), "level": LEVEL,
                         "method": method, "calibration_n": int(len(cal))})
    return pd.DataFrame(rows)


def main_repo_root():
    """Racine du depot principal : ROOT, ou le depot dont ROOT est un worktree (`.git` fichier)."""
    git = ROOT / ".git"
    if git.is_file():
        gitdir = Path(git.read_text().split("gitdir:", 1)[1].strip())
        if not gitdir.is_absolute():
            gitdir = (ROOT / gitdir).resolve()
        return gitdir.parents[2]  # <depot>/.git/worktrees/<nom>
    return ROOT


def write_table(db_path, df, computed_at):
    con = sqlite3.connect(str(db_path))
    try:
        exists = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (TABLE,)).fetchone()
        if exists:
            prev = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
            print(f"  table {TABLE} deja presente ({prev} lignes) : remplacee (table propre a ce script)")
        with con:  # transaction unique
            con.execute(f"DROP TABLE IF EXISTS {TABLE}")
            con.execute(f"""CREATE TABLE {TABLE} (
                archetype TEXT NOT NULL, data_month TEXT NOT NULL, target_month TEXT NOT NULL,
                pred REAL NOT NULL, lo REAL NOT NULL, hi REAL NOT NULL, level REAL NOT NULL,
                method TEXT NOT NULL, calibration_n INTEGER NOT NULL, computed_at TEXT NOT NULL,
                PRIMARY KEY (archetype, data_month, method))""")
            con.executemany(
                f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,?,?,?,?,?)",
                [(r.archetype, r.data_month, r.target_month, r.pred, r.lo, r.hi, r.level, r.method,
                  r.calibration_n, computed_at) for r in df.itertuples()])
        print(f"  {len(df)} lignes ecrites dans {TABLE} ({db_path})")
    finally:
        con.close()


# ---------------------------------------------------------------------------
def fmt_pct(x):
    return f"{100 * x:5.1f} %"


def ci_str(ci):
    return f"[{100 * ci[0]:.1f} ; {100 * ci[1]:.1f}]"


def evaluate(con, table, B, label, verbose=True):
    R, ms, ds = residual_frame(con, table)
    months = sorted(R["month"].unique())
    seed_m, eval_m = months[:N_SEED_MONTHS], months[N_SEED_MONTHS:N_SEED_MONTHS + N_EVAL_MONTHS]
    methods = CANDIDATES + NAIVES + ["ABS-12M"] + EXPLORATORY
    I, aci_next = {}, None
    for m in methods:
        I[m], a = run_method(R, m, eval_m)
        if m == "ACI":
            aci_next = 1 - a
    Ie = I["ABS"]
    edges = np.quantile(Ie["cur"].values, [1 / 3, 2 / 3])
    summ = {m: summarize(I[m], edges) for m in methods}
    # sensibilite : sans le dernier mois (cible partielle)
    last = eval_m[-1]
    summ_nolast = {m: summarize(I[m][I[m]["month"] < last], edges) for m in methods}
    bs_iid = boot_months(I, B, 1, SEED, ref="N-GAUSS")
    bs_blk = boot_months(I, B, 3, SEED + 1, ref="N-GAUSS")
    bs_pers = boot_months({k: I[k] for k in methods}, B, 1, SEED + 2, ref="N-PERS")
    adopted, elig = adopt(summ)
    mc = {m: monthly_cov(I[m]) for m in methods}
    res = {
        "label": label, "table": table,
        "n_rows_walk_forward": int(len(R)), "n_months_walk_forward": len(months),
        "seed_months": [f"{m:%Y-%m}" for m in seed_m], "n_seed_rows": int(R["month"].isin(seed_m).sum()),
        "eval_months": f"{eval_m[0]:%Y-%m} -> {eval_m[-1]:%Y-%m}", "n_eval_months": len(eval_m),
        "level_terciles_edges": [float(x) for x in edges],
        "summary": summ, "summary_without_last_month": summ_nolast,
        "boot_iid": bs_iid, "boot_block3": bs_blk, "boot_vs_pers": bs_pers,
        "eligible": elig, "adopted": adopted, "aci_level_next": aci_next,
        "lag1_autocorr_monthly_coverage": {m: lag1_autocorr(mc[m]["coverage"].values) for m in methods},
        "abs_q_trajectory": [float(I["ABS"][I["ABS"]["month"] == t]["hi"].sub(
            I["ABS"][I["ABS"]["month"] == t]["center"]).iloc[0]) for t in eval_m],
        "corr_abs_resid_level": float(np.corrcoef(np.abs(R["e"]), R["cur"])[0, 1]),
        "spearman_abs_resid_level": float(ep.spearman(np.abs(R["e"]), R["cur"])),
    }
    if verbose:
        print(f"\n=== {label} : table {table} ===")
        print(f"walk-forward : {len(R)} lignes, {len(months)} mois ; amorce {res['seed_months'][0]} -> "
              f"{res['seed_months'][-1]} ({res['n_seed_rows']} lignes) ; evaluation {res['eval_months']} "
              f"({summ['ABS']['n_rows']} lignes, {len(eval_m)} mois)")
        print(f"|residu| vs niveau : Pearson {res['corr_abs_resid_level']:+.3f}, "
              f"Spearman {res['spearman_abs_resid_level']:+.3f} ; terciles du niveau : "
              f"{edges[0]:.4f} / {edges[1]:.4f}")
        print(f"\n{'methode':9s} {'couv.':>8s} {'IC95 mois':>15s} {'IC95 blocs3':>15s} {'larg.moy':>9s} "
              f"{'Winkler':>8s} {'bas':>7s} {'milieu':>7s} {'haut':>7s} {'top5':>7s} {'sans dern.':>10s}")
        for m in methods:
            s = summ[m]
            print(f"{m:9s} {fmt_pct(s['coverage'])} {ci_str(bs_iid[m]['cov']):>15s} "
                  f"{ci_str(bs_blk[m]['cov']):>15s} {100 * s['width_mean']:8.2f}  {100 * s['winkler_mean']:7.2f} "
                  f"{fmt_pct(s['coverage_T1_bas'])} {fmt_pct(s['coverage_T2_milieu'])} "
                  f"{fmt_pct(s['coverage_T3_haut'])} {fmt_pct(s['coverage_top5'])} "
                  f"{fmt_pct(summ_nolast[m]['coverage']):>10s}")
        print("(largeur et Winkler en points de score x100 ; ASYM et MONDRIAN-ASYM : exploratoires, "
              "ajoutes apres lecture, jamais retenus)")
        print("\nRates sous la borne basse / au-dessus de la borne haute, par tiers de niveau :")
        for m in methods:
            s = summ[m]
            print(f"  {m:9s} " + "  ".join(
                f"{nm} {fmt_pct(s['miss_below_' + nm])} / {fmt_pct(s['miss_above_' + nm])}"
                for nm in ["T1_bas", "T2_milieu", "T3_haut"]))
        print(f"\nEligibles (regle figee) : {elig} ; retenu : {adopted}")
        for m in methods:
            d = bs_iid[m]["d_wink_vs_ref"]
            dp = bs_pers[m]["d_wink_vs_ref"]
            print(f"  Winkler {m:9s} - N-GAUSS : {100 * (summ[m]['winkler_mean'] - summ['N-GAUSS']['winkler_mean']):+.3f} "
                  f"[{100 * d[0]:+.3f} ; {100 * d[1]:+.3f}]   - N-PERS : "
                  f"{100 * (summ[m]['winkler_mean'] - summ['N-PERS']['winkler_mean']):+.3f} "
                  f"[{100 * dp[0]:+.3f} ; {100 * dp[1]:+.3f}]")
        print("\nCouverture par mois (ABS, MONDRIAN, N-GAUSS, MONDRIAN-ASYM) :")
        t = pd.concat({m: mc[m][["coverage", "width"]] for m in ["ABS", "MONDRIAN", "N-GAUSS", "MONDRIAN-ASYM"]},
                      axis=1)
        t.insert(0, "n_decks_cible", mc["ABS"]["n_decks_target"])
        t.insert(0, "n", mc["ABS"]["n"])
        t.index = [f"{x:%Y-%m}" for x in t.index]
        print(t.to_string(float_format=lambda v: f"{v:.3f}"))
        print(f"autocorrelation lag 1 de la couverture mensuelle : "
              + ", ".join(f"{m} {v:+.2f}" for m, v in res["lag1_autocorr_monthly_coverage"].items()))
        print(f"niveau ACI final : {aci_next:.3f}")
    res["_R"], res["_ms"], res["_ds"], res["_monthly"] = R, ms, ds, mc
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--db", default=str(ROOT / "data" / "yugioh.db"))
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--json")
    ap.add_argument("--write", action="store_true", help="cree la table meta_prediction_intervals")
    ap.add_argument("--reference", action="store_true", help="autorise --write sur la base du depot principal")
    ap.add_argument("--no-ocg", action="store_true", help="saute la sensibilite OCG")
    args = ap.parse_args()
    t0 = time.time()
    np.random.seed(SEED)

    db = Path(args.db).resolve()
    if args.write and db == (main_repo_root() / "data" / "yugioh.db").resolve() and not args.reference:
        sys.exit(f"Refus : {db} est la base de reference. Ajouter --reference pour y ecrire.")
    con = connect(db)
    main_res = evaluate(con, "meta_scores", args.boot, "TCG (prevision servie)")
    R = main_res["_R"]

    # --- previsions servies : reconstruction et intervalles
    served = pd.read_sql("SELECT archetype, data_month, meta_score_current, pred_meta_score, computed_at "
                         "FROM meta_predictions", con)
    rebuilt = production_predictions(con, main_res["_ms"], main_res["_ds"])
    cmp_ = served.merge(rebuilt, on="archetype", how="outer", suffixes=("", "_re"), indicator=True)
    both = cmp_[cmp_["_merge"] == "both"]
    rec = {
        "n_served": int(len(served)), "n_rebuilt": int(len(rebuilt)),
        "n_matched": int(len(both)),
        "only_served": sorted(cmp_.loc[cmp_["_merge"] == "left_only", "archetype"]),
        "only_rebuilt": sorted(cmp_.loc[cmp_["_merge"] == "right_only", "archetype"]),
        "data_month_equal": bool((both["data_month"] == both["data_month_re"]).all()),
        "max_abs_diff_pred": float((both["pred_meta_score"] - both["pred_meta_score_re"]).abs().max()),
        "max_abs_diff_current": float((both["meta_score_current"] - both["meta_score"]).abs().max()),
        "served_computed_at": sorted(served["computed_at"].unique().tolist()),
    }
    latest = served["data_month"].max()
    cur_served = served[served["data_month"] == latest]
    # ecart entre prevision servie et prevision du walk-forward strict pour le meme mois
    wf_last = R[R["month"] == pd.Timestamp(latest + "-01")][["archetype", "p", "y"]]
    gap = cur_served.merge(wf_last, on="archetype")
    rec["served_vs_walkforward_latest"] = {
        "n": int(len(gap)),
        "mean_abs_gap": float((gap["pred_meta_score"] - gap["p"]).abs().mean()) if len(gap) else None,
        "max_abs_gap": float((gap["pred_meta_score"] - gap["p"]).abs().max()) if len(gap) else None,
    }
    method = main_res["adopted"] or "ABS"
    cur_int = current_intervals(R, cur_served, method, main_res["aci_level_next"])
    all_int = {m: current_intervals(R, cur_served, m, main_res["aci_level_next"])
               for m in CANDIDATES + NAIVES[1:] + EXPLORATORY}
    print(f"\n=== Previsions servies (meta_predictions) ===")
    print(f"servies {rec['n_served']} (data_month : {sorted(served['data_month'].unique())}), "
          f"reconstruites {rec['n_rebuilt']}, appariees {rec['n_matched']}, "
          f"data_month identiques : {rec['data_month_equal']}, ecart max prevision "
          f"{rec['max_abs_diff_pred']:.2e}, ecart max niveau {rec['max_abs_diff_current']:.2e}")
    if rec["only_served"] or rec["only_rebuilt"]:
        print(f"  seulement servies : {rec['only_served']} ; seulement reconstruites : {rec['only_rebuilt']}")
    g = rec["served_vs_walkforward_latest"]
    print(f"servie vs walk-forward strict ({latest}, n = {g['n']}) : ecart moyen {g['mean_abs_gap']:.5f}, "
          f"max {g['max_abs_gap']:.5f}")
    print(f"\nIntervalles courants ({method}, {LEVEL:.0%}, data_month {latest}, calibration "
          f"{cur_int['calibration_n'].iloc[0]} residus) :")
    show = cur_int.sort_values("pred", ascending=False)
    for r in show.itertuples():
        print(f"  {r.archetype:30s} {100 * r.pred:6.2f}  [{100 * r.lo:6.2f} ; {100 * r.hi:6.2f}]")

    # --- sensibilite OCG (methode d'intervalle, prevision NON servie)
    ocg_res = None
    if not args.no_ocg:
        ocg_res = evaluate(con, "meta_scores_ocg", args.boot,
                           "OCG (sensibilite, modele TCG reapplique, non servi)")

    computed_at = datetime.date.today().isoformat()
    con.close()
    if args.write:
        write_table(db, cur_int, computed_at)

    if args.json:
        def clean(o):
            if isinstance(o, dict):
                return {str(k): clean(v) for k, v in o.items() if not str(k).startswith("_")}
            if isinstance(o, (list, tuple)):
                return [clean(v) for v in o]
            if isinstance(o, (np.floating, np.integer)):
                return o.item()
            return o
        dump = {"main": clean(main_res), "reconstruction": rec, "method_current": method,
                "current_intervals": cur_int.to_dict("records"),
                "current_intervals_all_methods": {m: d.to_dict("records") for m, d in all_int.items()},
                "monthly": {m: [{"month": f"{k:%Y-%m}", **{c: (float(v) if v is not None else None)
                                                            for c, v in row.items()}}
                                for k, row in d.iterrows()] for m, d in main_res["_monthly"].items()},
                "ocg": clean(ocg_res) if ocg_res else None}
        Path(args.json).write_text(json.dumps(dump, indent=1, ensure_ascii=False))
        print(f"\nJSON : {args.json}")
    print(f"\nTemps d'execution : {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
