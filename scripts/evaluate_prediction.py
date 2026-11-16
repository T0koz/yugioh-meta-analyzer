"""
TOK-73 - Evaluation honnete de la prediction et du signal OCG -> TCG.

LECTURE SEULE : la base est ouverte en `mode=ro`, aucune table n'est ecrite.
Toute la partie temporelle est en walk-forward (jamais de split aleatoire), les
scalers / regressions ne sont fittes que sur le passe.

    python scripts/evaluate_prediction.py                  # tout (quelques minutes)
    python scripts/evaluate_prediction.py --part A         # prediction seule
    python scripts/evaluate_prediction.py --part B         # signal OCG->TCG seul
    python scripts/evaluate_prediction.py --boot 300 --perm 300   # test rapide
    python scripts/evaluate_prediction.py --json out.json  # dump des chiffres

Partie A : reproduit notebooks/05_meta_prediction.ipynb (features, Ridge alpha=50,
fenetre 9 mois, ensemble 70 % naif + 30 % Ridge) puis l'evalue sur la VARIATION
(delta realise vs delta predit), avec bootstrap PAR MOIS.

Partie B : reproduit notebooks/09_ocg_tcg_correlation.ipynb puis le soumet a
des tests de permutation par archetype, une validation croisee par archetype, un
balayage de lags corrige des comparaisons multiples et un bootstrap par cluster
(archetype).
"""
import argparse
import json
import sqlite3
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from scipy.stats import binomtest, pearsonr, rankdata
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
DB_URI = f"file:{ROOT / 'data' / 'yugioh.db'}?mode=ro"

WINDOW = 9
W_MODEL = 0.3
ALPHA = 50.0
FEATURE_COLS = [
    "meta_score", "meta_score_t1", "meta_score_t2", "meta_score_t3",
    "delta_1m", "delta_2m", "accel", "roll_mean_3m",
    "share", "share_t1", "avg_placement", "avg_placement_t1",
    "rank_month", "rank_t1",
    "ban_severity", "n_forbidden", "was_hit_recent", "ban_severity_t1",
    "trend_ratio_monthly", "months_since_debut",
]


def connect():
    return sqlite3.connect(DB_URI, uri=True)


def spearman(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return np.nan
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def pct_ci(x, lo=2.5, hi=97.5):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return float("nan"), float("nan")
    return float(np.percentile(x, lo)), float(np.percentile(x, hi))


def sample_blocks(rng, n, block):
    """Indices de mois reechantillonnes : iid (block=1) ou blocs consecutifs."""
    if block <= 1:
        return rng.integers(0, n, n)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, nb)
    return np.concatenate([np.arange(s, s + block) for s in starts])[:n]


# =====================================================================
# PARTIE A - PREDICTION (reproduction du notebook 05)
# =====================================================================
def monthly_formula(decks):
    """Formule du notebook 04 : sqrt(share * placement_score_norm)."""
    total = decks.groupby("month").size().rename("total_decks")
    m = (decks.groupby(["month", "archetype"])
         .agg(deck_count=("id", "count"), avg_placement=("placement", "mean")).reset_index())
    m = m.join(total, on="month")
    m["share"] = m["deck_count"] / m["total_decks"]
    m["placement_score"] = 1.0 / m["avg_placement"]
    m["placement_score_norm"] = m.groupby("month")["placement_score"].transform(lambda x: x / x.max())
    m["meta_score"] = np.sqrt(m["share"] * m["placement_score_norm"])
    return m


def ms_from_decks(con, ocg=None):
    q = """SELECT id, archetype, placement, uploaded, ocg FROM tournament_decks
           WHERE id IN (SELECT deck_id FROM deck_legality WHERE legal = 1)
             AND archetype IS NOT NULL AND placement IS NOT NULL AND uploaded IS NOT NULL"""
    d = pd.read_sql(q, con)
    if ocg is not None:
        d = d[d["ocg"] == ocg]
    d["month"] = pd.to_datetime(d["uploaded"].str[:7] + "-01")
    return monthly_formula(d)[["month", "archetype", "deck_count", "share", "avg_placement", "meta_score"]]


def build_dataset(ms_in, con):
    """Copie fidele des cellules 3 et 5 du notebook 05."""
    ms = ms_in.copy()
    cards_bl = pd.read_sql("""
        SELECT archetype,
               SUM(CASE WHEN ban_tcg='Forbidden' THEN 1 ELSE 0 END) AS n_banned,
               SUM(CASE WHEN ban_tcg='Limited' THEN 1 ELSE 0 END) AS n_limited,
               SUM(CASE WHEN ban_tcg='Semi-Limited' THEN 1 ELSE 0 END) AS n_semi,
               COUNT(*) AS n_cards
        FROM cards WHERE archetype IS NOT NULL GROUP BY archetype""", con)
    cards_bl["trend_ratio"] = (cards_bl["n_limited"] + cards_bl["n_semi"]) / (cards_bl["n_cards"] + 1)
    static = cards_bl[["archetype", "trend_ratio", "n_cards"]].copy()
    banl = pd.read_sql("""SELECT month, archetype, n_forbidden, n_limited AS bl_n_limited, n_semi,
                          ban_severity, was_hit_recent, ban_severity_t1 FROM banlist_features""", con)
    banl["month"] = pd.to_datetime(banl["month"])
    banl = banl.merge(static[["archetype", "n_cards"]], on="archetype", how="left")
    banl["trend_ratio_monthly"] = (banl["bl_n_limited"] + banl["n_semi"]) / (banl["n_cards"].fillna(1) + 1)

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
    ds = clean.merge(static[["archetype", "trend_ratio"]], on="archetype", how="left")
    ds = ds.merge(banl[["archetype", "month", "ban_severity", "n_forbidden", "was_hit_recent",
                        "ban_severity_t1", "trend_ratio_monthly"]], on=["archetype", "month"], how="left")
    ds = ds.fillna(0)
    debut = ms.groupby("archetype")["month"].min().rename("debut_month").reset_index()
    ds = ds.merge(debut, on="archetype", how="left")
    ds["months_since_debut"] = ((ds["month"].dt.year - ds["debut_month"].dt.year) * 12
                                + (ds["month"].dt.month - ds["debut_month"].dt.month))
    return ds


def walk_forward(ds):
    """Walk-forward fenetre 9 mois. Pour chaque mois test i : fit sur les 9 mois
    precedents UNIQUEMENT (cibles connues a la date i), scaler fitte sur ce train."""
    months = sorted(ds["month"].unique())
    out = []
    for i in range(WINDOW, len(months)):
        tr = ds["month"].isin(months[max(0, i - WINDOW):i])
        te = ds["month"] == months[i]
        if te.sum() < 3:
            continue
        sc = StandardScaler()
        mdl = Ridge(alpha=ALPHA)
        mdl.fit(sc.fit_transform(ds.loc[tr, FEATURE_COLS].values), ds.loc[tr, "delta_next"].values)
        d_ridge = mdl.predict(sc.transform(ds.loc[te, FEATURE_COLS].values))
        # baseline "retour a la moyenne" a UNE feature : delta_next ~ k * delta_1m, k fitte sur le train
        x = ds.loc[tr, "delta_1m"].values
        y = ds.loc[tr, "delta_next"].values
        k = float((x * y).sum() / max((x * x).sum(), 1e-12))
        # baselines OLS (fittees sur le train) : retour a la moyenne sur le NIVEAU, puis niveau + delta_1m
        xl = ds.loc[tr, ["meta_score"]].values
        xl2 = ds.loc[tr, ["meta_score", "delta_1m"]].values
        t = ds.loc[te]
        d_lvl = ols_fit_predict(xl, y, t[["meta_score"]].values)
        d_ols2 = ols_fit_predict(xl2, y, t[["meta_score", "delta_1m"]].values)
        out.append(pd.DataFrame({
            "month": months[i], "archetype": t["archetype"].values,
            "cur": t["meta_score"].values, "nxt": t["meta_score_next"].values,
            "delta": (t["meta_score_next"] - t["meta_score"]).values,
            "d_ridge": d_ridge, "d_mom": k * t["delta_1m"].values, "k_mom": k,
            "d_lvl": d_lvl, "d_ols2": d_ols2,
        }))
    return pd.concat(out, ignore_index=True)


def sign_acc(delta, pred):
    m = (delta != 0) & (pred != 0)
    return float(np.mean(np.sign(delta[m]) == np.sign(pred[m]))) if m.sum() else np.nan


def pooled_metrics(R, w=W_MODEL):
    cur, nxt, dl = R["cur"].values, R["nxt"].values, R["delta"].values
    dr, dm = R["d_ridge"].values, R["d_mom"].values
    de = w * dr
    o = {
        "rho_d_ridge": spearman(dl, dr), "rho_d_mom": spearman(dl, dm),
        "mae_pers": float(np.mean(np.abs(dl))), "mae_ridge": float(np.mean(np.abs(dl - dr))),
        "mae_ens": float(np.mean(np.abs(dl - de))), "mae_mom": float(np.mean(np.abs(dl - dm))),
        "sign_ridge": sign_acc(dl, dr), "sign_mom": sign_acc(dl, dm),
        "rho_lvl_naive": spearman(nxt, cur), "rho_lvl_ridge": spearman(nxt, cur + dr),
        "rho_lvl_ens": spearman(nxt, cur + de),
    }
    s0 = float(np.sum(dl ** 2))
    o["skill_mse_ridge"] = 1 - float(np.sum((dl - dr) ** 2)) / s0
    o["skill_mse_ens"] = 1 - float(np.sum((dl - de) ** 2)) / s0
    o["skill_mse_mom"] = 1 - float(np.sum((dl - dm) ** 2)) / s0
    for nm in ("lvl", "ols2"):
        d_ = R["d_" + nm].values
        o["rho_d_" + nm] = spearman(dl, d_)
        o["mae_" + nm] = float(np.mean(np.abs(dl - d_)))
        o["skill_mse_" + nm] = 1 - float(np.sum((dl - d_) ** 2)) / s0
        o["sign_" + nm] = sign_acc(dl, d_)
    o["d_rho_d_ridge_vs_lvl"] = o["rho_d_ridge"] - o["rho_d_lvl"]
    o["d_mae_ridge_vs_lvl"] = o["mae_ridge"] - o["mae_lvl"]
    o["d_mae_ens_vs_pers"] = o["mae_ens"] - o["mae_pers"]
    o["d_mae_ridge_vs_pers"] = o["mae_ridge"] - o["mae_pers"]
    o["d_rho_lvl_ens_vs_naive"] = o["rho_lvl_ens"] - o["rho_lvl_naive"]
    o["d_rho_lvl_ridge_vs_naive"] = o["rho_lvl_ridge"] - o["rho_lvl_naive"]
    return o


def monthly_table(R, w=W_MODEL):
    rows = []
    for m, t in R.groupby("month"):
        cur, nxt, dl, dr, dm = (t[c].values for c in ["cur", "nxt", "delta", "d_ridge", "d_mom"])
        rows.append({
            "month": m, "n": len(t),
            "rho_d_ridge": spearman(dl, dr), "rho_d_mom": spearman(dl, dm),
            "rho_lvl_naive": spearman(nxt, cur), "rho_lvl_ens": spearman(nxt, cur + w * dr),
            "rho_lvl_ridge": spearman(nxt, cur + dr),
            "mae_pers": np.mean(np.abs(dl)), "mae_ens": np.mean(np.abs(dl - w * dr)),
            "mae_ridge": np.mean(np.abs(dl - dr)),
        })
    return pd.DataFrame(rows)


def bootstrap_by_month(R, B, block, seed):
    """Reechantillonne les MOIS (pas les lignes) : les ~60 archetypes d'un meme mois
    partagent le meme contexte de meta, ils ne sont pas independants."""
    rng = np.random.default_rng(seed)
    groups = [g for _, g in R.groupby("month")]
    mt = monthly_table(R)
    keys_p, keys_m = None, ["rho_d_ridge", "rho_d_mom", "rho_lvl_naive", "rho_lvl_ens", "rho_lvl_ridge"]
    out = {}
    for _ in range(B):
        idx = sample_blocks(rng, len(groups), block)
        Rb = pd.concat([groups[i] for i in idx], ignore_index=True)
        pm = pooled_metrics(Rb)
        sub = mt.iloc[idx]
        for k in keys_m:
            pm["mean_" + k] = float(np.nanmean(sub[k]))
        pm["mean_d_rho_lvl_ens_vs_naive"] = float(np.nanmean(sub["rho_lvl_ens"] - sub["rho_lvl_naive"]))
        pm["mean_d_mae_ens_vs_pers"] = float(np.mean(sub["mae_ens"] - sub["mae_pers"]))
        for k, v in pm.items():
            out.setdefault(k, []).append(v)
    return {k: np.array(v) for k, v in out.items()}


def summarize_A(R, label, B, seed):
    pt = pooled_metrics(R)
    mt = monthly_table(R)
    pt["mean_rho_d_ridge"] = float(np.nanmean(mt["rho_d_ridge"]))
    pt["mean_rho_d_mom"] = float(np.nanmean(mt["rho_d_mom"]))
    pt["mean_rho_lvl_naive"] = float(np.mean(mt["rho_lvl_naive"]))
    pt["mean_rho_lvl_ens"] = float(np.mean(mt["rho_lvl_ens"]))
    pt["mean_rho_lvl_ridge"] = float(np.mean(mt["rho_lvl_ridge"]))
    pt["mean_d_rho_lvl_ens_vs_naive"] = float(np.mean(mt["rho_lvl_ens"] - mt["rho_lvl_naive"]))
    pt["mean_d_mae_ens_vs_pers"] = float(np.mean(mt["mae_ens"] - mt["mae_pers"]))
    pt["n_rows"], pt["n_months"] = int(len(R)), int(R["month"].nunique())
    pt["base_rate_up"] = float(np.mean(R["delta"] > 0))
    pt["frac_delta_zero"] = float(np.mean(R["delta"] == 0))
    bs_iid = bootstrap_by_month(R, B, 1, seed)
    bs_blk = bootstrap_by_month(R, B, 3, seed + 1)
    ci = {k: pct_ci(v) for k, v in bs_iid.items()}
    ci_blk = {k: pct_ci(v) for k, v in bs_blk.items()}
    # test des signes (apparie, par mois) : l'ensemble bat-il le naif ?
    d_rho = (mt["rho_lvl_ens"] - mt["rho_lvl_naive"]).values
    d_mae = (mt["mae_ens"] - mt["mae_pers"]).values
    win_rho, n_rho = int((d_rho > 0).sum()), int((d_rho != 0).sum())
    win_mae, n_mae = int((d_mae < 0).sum()), int((d_mae != 0).sum())
    sign = {
        "months_ens_beats_naive_rho": win_rho, "n_months_rho": n_rho,
        "p_sign_rho": float(binomtest(win_rho, n_rho, 0.5).pvalue),
        "months_ens_beats_pers_mae": win_mae, "n_months_mae": n_mae,
        "p_sign_mae": float(binomtest(win_mae, n_mae, 0.5).pvalue),
    }
    # sensibilite au poids W (descriptif : choisir le max serait de la selection)
    wgrid = {}
    for w in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
        pm = pooled_metrics(R, w)
        wgrid[w] = {"rho_lvl": pm["rho_lvl_ens"], "mae_delta": pm["mae_ens"], "skill_mse": 1 - float(
            np.sum((R["delta"].values - w * R["d_ridge"].values) ** 2)) / float(np.sum(R["delta"].values ** 2))}
    return {"label": label, "point": pt, "ci_month_iid": ci, "ci_month_block3": ci_blk,
            "sign_test": sign, "w_grid": wgrid, "monthly": mt}


def part_A(con, B, seed):
    res = {}
    ms_mixed = pd.read_sql("SELECT month, archetype, share, avg_placement, meta_score FROM meta_scores "
                           "ORDER BY month, archetype", con)
    ms_mixed["month"] = pd.to_datetime(ms_mixed["month"])
    # --- verification : meta_scores melange-t-elle TCG + OCG ?
    recomputed_all = ms_from_decks(con, None)
    chk = ms_mixed.merge(recomputed_all, on=["month", "archetype"], suffixes=("", "_re"))
    res["mixed_check"] = {
        "n_rows_table": int(len(ms_mixed)), "n_rows_recomputed_all": int(len(recomputed_all)),
        "n_matched": int(len(chk)),
        "max_abs_diff_meta_score": float((chk["meta_score"] - chk["meta_score_re"]).abs().max()),
    }
    tcg_only = ms_from_decks(con, 0)
    ocg_only = ms_from_decks(con, 1)
    res["mixed_check"]["decks_tcg"] = int(tcg_only["deck_count"].sum())
    res["mixed_check"]["decks_ocg"] = int(ocg_only["deck_count"].sum())
    res["mixed_check"]["frac_ocg_in_meta_scores"] = res["mixed_check"]["decks_ocg"] / (
        res["mixed_check"]["decks_tcg"] + res["mixed_check"]["decks_ocg"])

    def run(ms, label, drop_last_target=False):
        ds = build_dataset(ms, con)
        if drop_last_target:
            ds = ds[ds["month_next"] < ds["month"].max() + pd.offsets.MonthBegin(1)]
        R = walk_forward(ds)
        out = summarize_A(R, label, B, seed)
        out["dataset_rows"] = int(len(ds))
        out["dataset_months"] = f"{ds['month'].min():%Y-%m} -> {ds['month'].max():%Y-%m}"
        # notebook : rho poole "ensemble" vs "naif"
        return out, R

    # Reference : table meta_scores telle que lue par le notebook (TCG+OCG melanges)
    res["A_mixed"], R_mixed = run(ms_mixed, "meta_scores (TCG+OCG melanges) - fidele au notebook 05")
    # Sensibilite 1 : le dernier mois cible (2026-11, partiel au 14/11) est exclu
    R_nopartial = R_mixed[R_mixed["month"] < R_mixed["month"].max()]
    res["A_mixed_no_partial_month"] = summarize_A(
        R_nopartial, "idem sans le mois test le plus recent (cible partielle)", B, seed)
    # Sensibilite 2 : TCG pur recalcule avec la formule du notebook 04
    res["A_tcg_pure"], R_tcg = run(tcg_only[["month", "archetype", "share", "avg_placement", "meta_score"]],
                                   "TCG pur (ocg=0), formule du notebook 04")
    return res


# =====================================================================
# PARTIE B - SIGNAL OCG -> TCG (reproduction du notebook 09)
# =====================================================================
PANEL_START = "2024-01"


def region_scores(con, ocg, formula="sqrt"):
    """Formule du notebook 09 (cellule 3), mois = date `created`."""
    df = pd.read_sql("""
        SELECT substr(created,1,7) AS month, archetype, COUNT(*) AS n_decks,
               AVG(CASE WHEN placement IS NOT NULL THEN placement END) AS avg_placement
        FROM tournament_decks
        WHERE ocg=? AND archetype IS NOT NULL AND id IN (SELECT deck_id FROM deck_legality WHERE legal=1)
        GROUP BY month, archetype""", con, params=(int(ocg),))
    df["month"] = pd.to_datetime(df["month"])
    df = df.join(df.groupby("month")["n_decks"].sum().rename("total"), on="month")
    df["share"] = df["n_decks"] / df["total"]
    ps = 1 / df["avg_placement"].replace(0, np.nan)
    df["ps_norm"] = ps / ps.groupby(df["month"]).transform("max")
    df["score"] = np.sqrt(df["share"] * df["ps_norm"].fillna(df["share"])) if formula == "sqrt" else df["share"]
    return df[["month", "archetype", "score", "share", "n_decks"]]


def notebook_lags(ocg_ms, tcg_ms, lags):
    """Copie de la cellule 5 du notebook 09 : jointure interne + Pearson."""
    out = {}
    o = ocg_ms.rename(columns={"score": "meta_score_ocg"})
    t = tcg_ms.rename(columns={"month": "m_t", "score": "meta_score_tcg"})
    for lag in lags:
        s = o.copy()
        s["month_tcg"] = s["month"].apply(lambda d: d + relativedelta(months=lag))
        mg = s.merge(t, left_on=["month_tcg", "archetype"], right_on=["m_t", "archetype"], how="inner")
        if len(mg) < 10:
            continue
        r, p = pearsonr(mg["meta_score_ocg"], mg["meta_score_tcg"])
        out[lag] = {"r": float(r), "p_naive": float(p), "n": int(len(mg)),
                    "n_archetypes": int(mg["archetype"].nunique())}
    return out


def make_panels(ocg_df, tcg_df, col="score"):
    months = pd.period_range(PANEL_START, max(ocg_df["month"].max(), tcg_df["month"].max()).strftime("%Y-%m"), freq="M")
    mi = {m.to_timestamp(): i for i, m in enumerate(months)}
    o = ocg_df[ocg_df["month"] >= PANEL_START]
    t = tcg_df[tcg_df["month"] >= PANEL_START]
    archs = sorted(set(o["archetype"]) | set(t["archetype"]))
    ai = {a: i for i, a in enumerate(archs)}
    O = np.zeros((len(archs), len(months)))
    T = np.zeros_like(O)
    for df, M in ((o, O), (t, T)):
        for m, a, v in zip(df["month"], df["archetype"], df[col]):
            M[ai[a], mi[m]] = v
    return O, T, archs, [m.strftime("%Y-%m") for m in months]


def wpearson(X, Y, W):
    n = W.sum()
    if n < 5:
        return np.nan
    mx, my = (W * X).sum() / n, (W * Y).sum() / n
    dx, dy = X - mx, Y - my
    vx, vy = (W * dx * dx).sum(), (W * dy * dy).sum()
    return float((W * dx * dy).sum() / np.sqrt(vx * vy)) if vx > 0 and vy > 0 else np.nan


def wpartial(X, Y, Z, W):
    n = W.sum()
    if n < 5:
        return np.nan
    mz = (W * Z).sum() / n
    dz = Z - mz
    vz = (W * dz * dz).sum()
    if vz <= 0:
        return np.nan
    mx, my = (W * X).sum() / n, (W * Y).sum() / n
    bx = (W * (X - mx) * dz).sum() / vz
    by = (W * (Y - my) * dz).sum() / vz
    return wpearson(X - mx - bx * dz, Y - my - by * dz, W)


def lag_stats(O, T, lag, RO=None, RT=None):
    """Statistiques au lag `lag` : OCG(t) -> TCG(t+lag), univers = archetypes x mois.
      inner   : jointure interne du notebook (O>0 et Y>0)  -> selection sur la CIBLE (biais)
      full    : toutes les cellules archetype x mois, zeros inclus (univers fixe)
      visible : O(t)>0 ou T(t)>0 -> univers connu a la date t seulement (honnete)
      part    : correlation partielle OCG(t) ~ TCG(t+L) | TCG(t), univers visible
      ar      : correlation TCG(t) ~ TCG(t+L), univers visible (baseline autoregressive)
      cs      : Spearman transversal moyen (par mois), univers complet
    """
    M = O.shape[1]
    X, Y, Z = O[:, :M - lag], T[:, lag:], T[:, :M - lag]
    inner = ((X > 0) & (Y > 0)).astype(float)
    vis = ((X > 0) | (Z > 0)).astype(float)
    s = {"inner": wpearson(X, Y, inner), "n_inner": int(inner.sum()),
         "full": wpearson(X, Y, np.ones_like(X)),
         "visible": wpearson(X, Y, vis), "n_visible": int(vis.sum()),
         "part": wpartial(X, Y, Z, vis), "ar": wpearson(Z, Y, vis)}
    if RO is not None:
        Xr, Yr = RO[:, :M - lag], RT[:, lag:]
        Xc, Yc = Xr - Xr.mean(0), Yr - Yr.mean(0)
        den = np.sqrt((Xc ** 2).sum(0) * (Yc ** 2).sum(0))
        with np.errstate(invalid="ignore", divide="ignore"):
            r = (Xc * Yc).sum(0) / den
        s["cs"] = float(np.nanmean(r))
    return s


def col_ranks(A):
    return np.column_stack([rankdata(A[:, j]) for j in range(A.shape[1])])


STATS = ["inner", "full", "part", "cs"]


def bh_adjust(p):
    p = np.asarray(p, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    run = 1.0
    for rank, i in zip(range(n, 0, -1), order[::-1]):
        run = min(run, p[i] * n / rank)
        adj[i] = run
    return adj


def permutation_tests(O, T, lags, P, seed, mode="identity"):
    """Permutation PAR ARCHETYPE : on echange les series OCG ENTIERES entre archetypes
    (permutation en blocs) et on laisse TCG intact. Cela conserve, pour chaque serie,
    sa distribution, son autocorrelation temporelle et sa duree de vie, et ne casse que
    l'appariement 'tel archetype OCG <-> tel archetype TCG'. Permuter les lignes
    individuelles serait faux : les 35 mois d'un meme archetype sont tres dependants.

    mode="shift" : au lieu d'echanger les archetypes, on DECALE circulairement la serie OCG
    de chaque archetype d'un offset aleatoire (son identite est conservee, seul l'alignement
    temporel est detruit). Teste l'apport du TIMING au-dela de 'les archetypes forts le sont
    partout'."""
    rng = np.random.default_rng(seed)
    A, M = O.shape
    shift = mode == "shift"
    stats = ["inner", "full", "part"] if shift else STATS
    RO, RT = (None, None) if shift else (col_ranks(O), col_ranks(T))
    obs = {L: lag_stats(O, T, L, RO, RT) for L in lags}
    null = {st: np.full((P, len(lags)), np.nan) for st in stats}
    for b in range(P):
        if shift:
            k = rng.integers(0, M, A)
            Op = O[np.arange(A)[:, None], (np.arange(M)[None, :] - k[:, None]) % M]
            ROp = None
        else:
            perm = rng.permutation(A)
            Op, ROp = O[perm], RO[perm]
        for j, L in enumerate(lags):
            s = lag_stats(Op, T, L, ROp, RT)
            for st in stats:
                null[st][b, j] = s[st]
    out = {}
    for st in stats:
        ov = np.array([obs[L][st] for L in lags])
        nl = null[st]
        p = np.array([(1 + np.nansum(nl[:, j] >= ov[j])) / (1 + np.sum(~np.isnan(nl[:, j])))
                      for j in range(len(lags))])
        # p-value du MAX sur la famille de lags (corrige la selection du meilleur lag)
        mx = np.nanmax(nl, axis=1)
        p_max = np.array([(1 + np.sum(mx >= ov[j])) / (1 + P) for j in range(len(lags))])
        # idem restreint a la plage du notebook (2..7)
        sel = [j for j, L in enumerate(lags) if 2 <= L <= 7]
        mx27 = np.nanmax(nl[:, sel], axis=1)
        p_max27 = np.array([(1 + np.sum(mx27 >= ov[j])) / (1 + P) for j in range(len(lags))])
        out[st] = {"obs": ov, "p_raw": p, "p_bonf": np.minimum(p * len(lags), 1.0), "p_bh": bh_adjust(p),
                   "p_maxT_0_8": p_max, "p_maxT_2_7": p_max27,
                   "null_mean": np.nanmean(nl, axis=0), "null_q95": np.nanpercentile(nl, 95, axis=0)}
    out["n_perm"] = P
    return out


def cluster_bootstrap(O, T, lags, B, seed):
    """Reechantillonne les ARCHETYPES (clusters) avec remise."""
    rng = np.random.default_rng(seed)
    A = O.shape[0]
    keys = ("inner", "visible", "part", "ar", "rev_inner", "rev_visible", "rev_part")
    res = {st: np.full((B, len(lags)), np.nan) for st in keys}
    for b in range(B):
        idx = rng.integers(0, A, A)
        Ob, Tb = O[idx], T[idx]
        for j, L in enumerate(lags):
            s = lag_stats(Ob, Tb, L)
            sr = lag_stats(Tb, Ob, L)      # sens inverse : TCG(t) -> OCG(t+L)
            for st in ("inner", "visible", "part", "ar"):
                res[st][b, j] = s[st]
            for st in ("inner", "visible", "part"):
                res["rev_" + st][b, j] = sr[st]
    return res


def design(O, T, lag):
    """Lignes (archetype, t) VISIBLES a la date t (O(t)>0 ou T(t)>0) : la selection ne
    depend pas de la cible. Renvoie les identifiants + features + cible TCG(t+lag)."""
    A, M = O.shape
    a_idx, t_idx = np.meshgrid(np.arange(A), np.arange(M - lag), indexing="ij")
    X, Z, Y = O[:, :M - lag], T[:, :M - lag], T[:, lag:]
    keep = (X > 0) | (Z > 0)
    return (a_idx[keep], t_idx[keep], X[keep], Z[keep], Y[keep])


FEATS = {"M0 constante": [], "M1 AR(TCG t)": ["z"], "M2 OCG t": ["x"], "M3 AR + OCG": ["z", "x"]}


def ols_fit_predict(Xtr, ytr, Xte):
    if Xtr.shape[1] == 0:
        return np.full(len(Xte), ytr.mean())
    A = np.column_stack([np.ones(len(Xtr)), Xtr])
    beta, *_ = np.linalg.lstsq(A, ytr, rcond=None)
    return np.column_stack([np.ones(len(Xte)), Xte]) @ beta


def loao_cv(O, T, lag, B, seed):
    """Leave-one-archetype-out : generalisation a un archetype jamais vu. Attention :
    ce n'est PAS un test de prevision (l'entrainement contient des mois posterieurs au test),
    c'est un test de 'la relation tient-elle d'un archetype a l'autre ?'. """
    a, t, x, z, y = design(O, T, lag)
    cols = {"x": x, "z": z}
    preds = {k: np.zeros(len(y)) for k in FEATS}
    for g in np.unique(a):
        te = a == g
        for k, fs in FEATS.items():
            Xm = np.column_stack([cols[f] for f in fs]) if fs else np.zeros((len(y), 0))
            preds[k][te] = ols_fit_predict(Xm[~te], y[~te], Xm[te])
    groups = np.unique(a)
    sse = {k: np.array([np.sum((y[a == g] - preds[k][a == g]) ** 2) for g in groups]) for k in FEATS}
    cnt = np.array([np.sum(a == g) for g in groups])
    out = {"n_rows": int(len(y)), "n_archetypes": int(len(groups)), "models": {}}
    for k in FEATS:
        out["models"][k] = {"mse": float(sse[k].sum() / cnt.sum()),
                            "r2_vs_const": 1 - float(sse[k].sum() / sse["M0 constante"].sum()),
                            "rho": spearman(y, preds[k])}
    rng = np.random.default_rng(seed)
    d31, d20 = [], []
    for _ in range(B):
        i = rng.integers(0, len(groups), len(groups))
        n = cnt[i].sum()
        d31.append((sse["M3 AR + OCG"][i].sum() - sse["M1 AR(TCG t)"][i].sum()) / n)
        d20.append((sse["M2 OCG t"][i].sum() - sse["M0 constante"][i].sum()) / n)
    out["d_mse_M3_minus_M1"] = float(out["models"]["M3 AR + OCG"]["mse"] - out["models"]["M1 AR(TCG t)"]["mse"])
    out["ci_d_mse_M3_minus_M1"] = pct_ci(d31)
    out["d_mse_M2_minus_M0"] = float(out["models"]["M2 OCG t"]["mse"] - out["models"]["M0 constante"]["mse"])
    out["ci_d_mse_M2_minus_M0"] = pct_ci(d20)
    return out


def walk_forward_ocg(O, T, lag, B, seed, min_train_months=8, block=3):
    """Prevision TEMPORELLE : a la date t, on ne fitte que sur les paires (s, s+lag) dont
    la cible est deja connue (s + lag <= t). On predit TCG(t+lag)."""
    A, M = O.shape
    a, t, x, z, y = design(O, T, lag)
    cols = {"x": x, "z": z}
    test_months = [m for m in range(M - lag) if (m - lag + 1) >= min_train_months]
    per_month = []
    rows = {k: [] for k in FEATS}
    ys = []
    for m in test_months:
        tr = (t + lag) <= m
        te = t == m
        if te.sum() < 5 or tr.sum() < 50:
            continue
        ys.append(y[te])
        sse = {}
        for k, fs in FEATS.items():
            Xm = np.column_stack([cols[f] for f in fs]) if fs else np.zeros((len(y), 0))
            p = ols_fit_predict(Xm[tr], y[tr], Xm[te])
            rows[k].append(p)
            sse[k] = float(np.sum((y[te] - p) ** 2))
        sse["n"] = int(te.sum())
        per_month.append(sse)
    if not per_month:
        return None
    pm = pd.DataFrame(per_month)
    yall = np.concatenate(ys)
    out = {"n_test_months": len(pm), "n_rows": int(pm["n"].sum()), "models": {}}
    for k in FEATS:
        pall = np.concatenate(rows[k])
        out["models"][k] = {"mse": float(pm[k].sum() / pm["n"].sum()),
                            "r2_vs_const": 1 - float(pm[k].sum() / pm["M0 constante"].sum()),
                            "rho": spearman(yall, pall)}
    rng = np.random.default_rng(seed)
    d31, d20 = [], []
    for _ in range(B):
        idx = sample_blocks(rng, len(pm), block)
        s = pm.iloc[idx]
        d31.append((s["M3 AR + OCG"].sum() - s["M1 AR(TCG t)"].sum()) / s["n"].sum())
        d20.append((s["M2 OCG t"].sum() - s["M0 constante"].sum()) / s["n"].sum())
    out["d_mse_M3_minus_M1"] = float((pm["M3 AR + OCG"].sum() - pm["M1 AR(TCG t)"].sum()) / pm["n"].sum())
    out["ci_d_mse_M3_minus_M1"] = pct_ci(d31)
    out["d_mse_M2_minus_M0"] = float((pm["M2 OCG t"].sum() - pm["M0 constante"].sum()) / pm["n"].sum())
    out["ci_d_mse_M2_minus_M0"] = pct_ci(d20)
    out["months_M3_beats_M1"] = int((pm["M3 AR + OCG"] < pm["M1 AR(TCG t)"]).sum())
    return out


def part_B(con, P, B, seed):
    res = {}
    lags_nb = list(range(2, 8))
    lags = list(range(0, 9))
    ocg = region_scores(con, 1)
    tcg_clean = region_scores(con, 0)
    ms = pd.read_sql("SELECT month, archetype, meta_score AS score FROM meta_scores", con)
    ms["month"] = pd.to_datetime(ms["month"])

    # B1 - reproduction du notebook (TCG = table meta_scores, MELANGEE) puis TCG propre
    res["B1_notebook_mixed"] = notebook_lags(ocg, ms, lags_nb)
    res["B1_notebook_clean_tcg"] = notebook_lags(ocg, tcg_clean, lags_nb)
    O, T, archs, months = make_panels(ocg, tcg_clean)
    res["panel"] = {"n_archetypes": len(archs), "n_months": len(months), "months": f"{months[0]} -> {months[-1]}"}
    # controle croise : la jointure interne par panneau = la jointure pandas du notebook
    chk = {L: lag_stats(O, T, L)["inner"] for L in lags_nb}
    nb24 = notebook_lags(ocg[ocg["month"] >= PANEL_START], tcg_clean[tcg_clean["month"] >= PANEL_START], lags_nb)
    res["B1_notebook_clean_tcg_2024plus"] = nb24
    res["B1_panel_crosscheck_inner"] = {L: {"panel": chk[L], "pandas": nb24[L]["r"]} for L in chk if L in nb24}
    # lag 0 avec la table melangee : contamination mecanique
    Om, Tm, _, _ = make_panels(ocg, ms)
    res["B1_lag0_mixed_vs_clean"] = {
        "inner_mixed": lag_stats(Om, Tm, 0)["inner"], "inner_clean": lag_stats(O, T, 0)["inner"],
        "inner_mixed_lag4": lag_stats(Om, Tm, 4)["inner"], "inner_clean_lag4": lag_stats(O, T, 4)["inner"]}

    # B2/B4 - permutation par archetype sur tous les lags
    res["B2_perm"] = permutation_tests(O, T, lags, P, seed)
    res["B2_perm_shift"] = permutation_tests(O, T, lags, P, seed + 11, mode="shift")
    # Sensibilite : table melangee (TCG contamine par l'OCG) sous le meme test
    permm = permutation_tests(Om, Tm, lags, max(P // 2, 200), seed + 7)
    res["B2_perm_mixed_target"] = {k: v for k, v in permm.items() if k in ("inner", "full", "n_perm")}
    # Sensibilite : score = part de decks uniquement (sans le terme de placement)
    ocg_sh, tcg_sh = region_scores(con, 1, "share"), region_scores(con, 0, "share")
    Os, Ts, _, _ = make_panels(ocg_sh, tcg_sh)
    res["B2_share_only"] = {L: lag_stats(Os, Ts, L) for L in lags}

    # B5 - bootstrap par cluster (archetype) : CI de r(L) et stabilite de l'argmax
    cb = cluster_bootstrap(O, T, lags, B, seed + 1)
    res["B5_cluster"] = {}
    for st, M in cb.items():
        res["B5_cluster"][st] = {
            "ci": [pct_ci(M[:, j]) for j in range(len(lags))],
            "argmax_0_8": {int(L): float(np.mean(np.nanargmax(np.where(np.isnan(M), -9, M), axis=1) == j))
                           for j, L in enumerate(lags)},
            "argmax_2_7": {int(L): float(np.mean(np.nanargmax(np.where(np.isnan(M[:, 2:8]), -9, M[:, 2:8]), axis=1) == j - 2))
                           for j, L in enumerate(lags) if 2 <= L <= 7},
        }
    res["B5_cluster"]["diff_vs_lag4"] = {
        st: [pct_ci(cb[st][:, 4] - cb[st][:, j]) for j in range(len(lags))] for st in ("inner", "visible", "part")}
    res["B5_cluster"]["fwd_minus_rev"] = {
        st: [pct_ci(cb[st][:, j] - cb["rev_" + st][:, j]) for j in range(len(lags))] for st in ("inner", "visible", "part")}
    res["B5_cluster"]["diff_inner_4_minus_3"] = pct_ci(cb["inner"][:, 4] - cb["inner"][:, 3])
    res["B5_cluster"]["diff_inner_4_minus_5"] = pct_ci(cb["inner"][:, 4] - cb["inner"][:, 5])
    res["B5_cluster"]["diff_inner_4_minus_0"] = pct_ci(cb["inner"][:, 4] - cb["inner"][:, 0])
    res["B5_cluster"]["diff_part_4_minus_0"] = pct_ci(cb["part"][:, 4] - cb["part"][:, 0])

    # B3 - validation croisee par archetype + walk-forward temporel (baseline AR)
    res["B3_loao"] = {L: loao_cv(O, T, L, B, seed + 2) for L in (2, 4, 6)}
    res["B3_walkforward"] = {L: walk_forward_ocg(O, T, L, B, seed + 3) for L in range(1, 9)}
    return res


# =====================================================================
# Affichage
# =====================================================================
def f3(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.3f}"


def ci_s(c, d=3):
    return f"[{c[0]:+.{d}f} ; {c[1]:+.{d}f}]"


def print_A(res):
    print("\n" + "=" * 78 + "\nPARTIE A - PREDICTION\n" + "=" * 78)
    mc = res["mixed_check"]
    print(f"[Controle] meta_scores : {mc['n_rows_table']} lignes ; recalcul sans filtre ocg = "
          f"{mc['n_rows_recomputed_all']} lignes, {mc['n_matched']} appariees, ecart max meta_score = "
          f"{mc['max_abs_diff_meta_score']:.2e}")
    print(f"           decks TCG = {mc['decks_tcg']}, decks OCG = {mc['decks_ocg']} -> "
          f"{100 * mc['frac_ocg_in_meta_scores']:.1f} % des decks de meta_scores sont OCG (TABLE MELANGEE)")
    for key in ("A_mixed", "A_mixed_no_partial_month", "A_tcg_pure"):
        r = res[key]
        p, c, cb = r["point"], r["ci_month_iid"], r["ci_month_block3"]
        print(f"\n--- {r['label']}")
        if "dataset_rows" in r:
            print(f"    dataset {r['dataset_rows']} lignes ({r['dataset_months']})")
        print(f"    points d'evaluation : {p['n_rows']} lignes (archetype x mois) sur {p['n_months']} mois test ; "
              f"part de delta>0 = {100 * p['base_rate_up']:.1f} %, delta==0 = {100 * p['frac_delta_zero']:.1f} %")
        print(f"    {'metrique':42s} {'valeur':>8s}   IC95 % mois iid           IC95 % blocs de 3")
        def row(name, k):
            d = 5 if ("mae" in k) else 3
            print(f"    {name:46s} {p[k]:>+9.{d}f}   {ci_s(c[k], d):28s}  {ci_s(cb[k], d)}")
        print("    -- niveau (comme dans le notebook)")
        row("rho poole  niveau  naif", "rho_lvl_naive")
        row("rho poole  niveau  ensemble 70/30", "rho_lvl_ens")
        row("rho poole  niveau  Ridge seul", "rho_lvl_ridge")
        row("  diff ensemble - naif (poole)", "d_rho_lvl_ens_vs_naive")
        row("rho moyen/mois niveau naif", "mean_rho_lvl_naive")
        row("rho moyen/mois niveau ensemble", "mean_rho_lvl_ens")
        row("  diff ensemble - naif (moyen/mois)", "mean_d_rho_lvl_ens_vs_naive")
        print("    -- variation (delta realise vs predit) ; persistance = delta 0, rho non defini")
        row("rho poole  delta  Ridge (= ensemble)", "rho_d_ridge")
        row("rho moyen/mois delta Ridge", "mean_rho_d_ridge")
        row("rho poole  delta  momentum 1 feature", "rho_d_mom")
        row("MAE delta persistance", "mae_pers")
        row("MAE delta ensemble 0.3", "mae_ens")
        row("MAE delta Ridge seul", "mae_ridge")
        row("MAE delta momentum 1 feature", "mae_mom")
        row("  diff MAE ensemble - persistance (<0 = gain)", "d_mae_ens_vs_pers")
        row("  diff MAE Ridge - persistance", "d_mae_ridge_vs_pers")
        row("gain MSE vs persistance, ensemble", "skill_mse_ens")
        row("gain MSE vs persistance, Ridge", "skill_mse_ridge")
        row("gain MSE vs persistance, momentum", "skill_mse_mom")
        row("signe correct Ridge (delta!=0)", "sign_ridge")
        row("signe correct momentum", "sign_mom")
        print("    -- baselines de retour a la moyenne (OLS fittee sur le train)")
        row("rho poole delta : OLS(niveau)", "rho_d_lvl")
        row("rho poole delta : OLS(niveau, delta_1m)", "rho_d_ols2")
        row("MAE delta OLS(niveau)", "mae_lvl")
        row("MAE delta OLS(niveau, delta_1m)", "mae_ols2")
        row("gain MSE vs persistance, OLS(niveau)", "skill_mse_lvl")
        row("gain MSE vs persistance, OLS(niveau, d1m)", "skill_mse_ols2")
        row("signe correct OLS(niveau)", "sign_lvl")
        row("  diff rho delta : Ridge - OLS(niveau)", "d_rho_d_ridge_vs_lvl")
        row("  diff MAE delta : Ridge - OLS(niveau)", "d_mae_ridge_vs_lvl")
        s = r["sign_test"]
        print(f"    test des signes par mois : ensemble > naif en rho niveau {s['months_ens_beats_naive_rho']}/{s['n_months_rho']} "
              f"(p={s['p_sign_rho']:.3f}) ; MAE delta < persistance {s['months_ens_beats_pers_mae']}/{s['n_months_mae']} "
              f"(p={s['p_sign_mae']:.3f})")
        print("    sensibilite au poids W (descriptif, W=0.3 a ete choisi sur ces memes donnees) :")
        for w, v in r["w_grid"].items():
            print(f"      W={w:.1f}  rho niveau={v['rho_lvl']:+.4f}  MAE delta={v['mae_delta']:.5f}  gain MSE={v['skill_mse']:+.4f}")


def print_B(res):
    print("\n" + "=" * 78 + "\nPARTIE B - SIGNAL OCG -> TCG\n" + "=" * 78)
    print(f"Panneau : {res['panel']['n_archetypes']} archetypes x {res['panel']['n_months']} mois ({res['panel']['months']})")
    for key, lab in (("B1_notebook_mixed", "Notebook 09 sur donnees actuelles (TCG = meta_scores MELANGEE)"),
                     ("B1_notebook_clean_tcg", "Meme code, TCG PUR (ocg=0, memes formules)")):
        print(f"\n[{lab}]  lags 2..7, jointure interne, Pearson")
        for L, v in res[key].items():
            print(f"   lag {L}: r={v['r']:+.3f}  n={v['n']}  ({v['n_archetypes']} archetypes)  p_naif={v['p_naive']:.2g}")
    print("\n[Meme code, TCG PUR, OCG restreint a 2024+ (= panneau)]")
    for L, v in res["B1_notebook_clean_tcg_2024plus"].items():
        print(f"   lag {L}: r={v['r']:+.3f}  n={v['n']}  ({v['n_archetypes']} archetypes)")
    print("\n[Controle croise jointure panneau vs pandas, 2024+] ",
          {L: (round(v['panel'], 4), round(v['pandas'], 4)) for L, v in res["B1_panel_crosscheck_inner"].items()})
    z = res["B1_lag0_mixed_vs_clean"]
    print(f"[Contamination] r(inner) lag0 : table melangee {z['inner_mixed']:+.3f} vs TCG pur {z['inner_clean']:+.3f} ; "
          f"lag4 : {z['inner_mixed_lag4']:+.3f} vs {z['inner_clean_lag4']:+.3f}")
    pr = res["B2_perm"]
    print(f"\n[Permutation par archetype, {pr['n_perm']} permutations, une-queue, TCG pur] -- 0..8")
    for st, lab in (("inner", "r Pearson, jointure interne (notebook)"), ("full", "r Pearson, univers complet (zeros inclus)"),
                    ("part", "r PARTIEL OCG(t)~TCG(t+L) | TCG(t)"), ("cs", "Spearman transversal moyen/mois")):
        d = pr[st]
        print(f"\n  {lab}")
        print("   lag   obs     nul(moy)  nul(q95)  p_brut  p_Bonf  p_BH   p_max(0-8)  p_max(2-7)")
        for j in range(9):
            print(f"   {j:>3d} {d['obs'][j]:+.3f}   {d['null_mean'][j]:+.3f}    {d['null_q95'][j]:+.3f}   {d['p_raw'][j]:.4f}  "
                  f"{d['p_bonf'][j]:.4f}  {d['p_bh'][j]:.4f}   {d['p_maxT_0_8'][j]:.4f}     {d['p_maxT_2_7'][j]:.4f}")
    ps = res["B2_perm_shift"]
    print(f"\n[Permutation par DECALAGE CIRCULAIRE de chaque serie OCG, {ps['n_perm']} perm. : teste le timing, pas l'identite]")
    for st, lab in (("inner", "r interne"), ("full", "r univers complet"), ("part", "r partiel | TCG(t)")):
        d = ps[st]
        print(f"  {lab}: " + " | ".join(f"L{j} obs={d['obs'][j]:+.3f} nul={d['null_mean'][j]:+.3f}/q95 {d['null_q95'][j]:+.3f} p={d['p_raw'][j]:.4f}" for j in range(9)))
    pm = res["B2_perm_mixed_target"]
    print(f"\n  [Cible melangee TCG+OCG, {pm['n_perm']} perm.] r interne par lag : "
          + ", ".join(f"{j}:{pm['inner']['obs'][j]:+.3f}(p={pm['inner']['p_raw'][j]:.3f})" for j in range(9)))
    print("\n[Score = part de decks seulement] r interne / visible / partiel / ar / n_inner par lag")
    for L, s in res["B2_share_only"].items():
        print(f"   lag {L}: inner={f3(s['inner'])} visible={f3(s['visible'])} part={f3(s['part'])} ar={f3(s['ar'])} n={s['n_inner']}")
    print("\n[Baseline autoregressive] r(TCG t, TCG t+L) vs r(OCG t, TCG t+L), univers visible, + n")
    for j in range(9):
        L = j
        s = lag_stats(*make_panels_cache["clean"][:2], L)
        print(f"   lag {L}: AR={f3(s['ar'])}  OCG={f3(s['visible'])}  partiel OCG|AR={f3(s['part'])}  n_visible={s['n_visible']}")
    cb = res["B5_cluster"]
    print("\n[Bootstrap par archetype (clusters)] IC95 % et frequence d'etre le meilleur lag")
    for st in ("inner", "visible", "part", "rev_inner", "rev_visible", "rev_part", "ar"):
        print(f"  {st}:")
        for j in range(9):
            a27 = cb[st].get("argmax_2_7", {}).get(j)
            print(f"   lag {j}: IC {ci_s(cb[st]['ci'][j])}  argmax(0-8)={cb[st]['argmax_0_8'][j]:.2f}"
                  + (f"  argmax(2-7)={a27:.2f}" if a27 is not None else ""))
    for st in ("inner", "visible", "part"):
        print(f"  IC95 % de r(lag 4) - r(lag L), {st} : "
              + " ".join(f"L{j}:{ci_s(cb['diff_vs_lag4'][st][j], 2)}" for j in range(9) if j != 4))
    for st in ("inner", "visible", "part"):
        print(f"  IC95 % de [OCG->TCG] - [TCG->OCG] (sens direct moins inverse), {st} : "
              + " ".join(f"L{j}:{ci_s(cb['fwd_minus_rev'][st][j], 2)}" for j in range(1, 9)))
    for k in ("diff_inner_4_minus_3", "diff_inner_4_minus_5", "diff_inner_4_minus_0", "diff_part_4_minus_0"):
        print(f"  {k}: IC95 % {ci_s(cb[k])}")
    print("\n[Validation croisee par archetype : leave-one-archetype-out] cible TCG(t+L), univers visible a t")
    for L, v in res["B3_loao"].items():
        print(f"  lag {L}: n={v['n_rows']} lignes, {v['n_archetypes']} archetypes")
        for k, m in v["models"].items():
            print(f"     {k:14s} MSE={m['mse']:.6f}  R2 vs constante={m['r2_vs_const']:+.3f}  rho={'n/a' if k.startswith('M0') else f3(m['rho'])}")
        print(f"     dMSE(M3-M1)={v['d_mse_M3_minus_M1']:+.2e} IC95 {v['ci_d_mse_M3_minus_M1'][0]:+.2e};{v['ci_d_mse_M3_minus_M1'][1]:+.2e}"
              f" | dMSE(M2-M0)={v['d_mse_M2_minus_M0']:+.2e} IC95 {v['ci_d_mse_M2_minus_M0'][0]:+.2e};{v['ci_d_mse_M2_minus_M0'][1]:+.2e}")
    print("\n[Walk-forward temporel (fit sur cibles deja connues)] cible TCG(t+L)")
    for L, v in res["B3_walkforward"].items():
        if v is None:
            continue
        m = v["models"]
        print(f"  lag {L}: {v['n_test_months']} mois test, {v['n_rows']} lignes | R2 vs const : M1={m['M1 AR(TCG t)']['r2_vs_const']:+.3f} "
              f"M2={m['M2 OCG t']['r2_vs_const']:+.3f} M3={m['M3 AR + OCG']['r2_vs_const']:+.3f} | "
              f"dMSE(M3-M1)={v['d_mse_M3_minus_M1']:+.2e} IC95 [{v['ci_d_mse_M3_minus_M1'][0]:+.2e};{v['ci_d_mse_M3_minus_M1'][1]:+.2e}] "
              f"M3<M1 {v['months_M3_beats_M1']}/{v['n_test_months']} mois")


make_panels_cache = {}


def to_jsonable(o):
    if isinstance(o, dict):
        return {str(k): to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, pd.DataFrame):
        return json.loads(o.to_json(orient="records", date_format="iso"))
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["A", "B", "all"], default="all")
    ap.add_argument("--boot", type=int, default=2000, help="replicats bootstrap")
    ap.add_argument("--perm", type=int, default=2000, help="permutations")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--json", type=str, default=None, help="ecrit les chiffres dans ce fichier JSON")
    a = ap.parse_args()
    con = connect()
    res = {}
    if a.part in ("A", "all"):
        res["A"] = part_A(con, a.boot, a.seed)
        print_A(res["A"])
    if a.part in ("B", "all"):
        ocg, tcg = region_scores(con, 1), region_scores(con, 0)
        O, T, _, _ = make_panels(ocg, tcg)
        make_panels_cache["clean"] = (O, T)
        res["B"] = part_B(con, a.perm, a.boot, a.seed)
        print_B(res["B"])
    con.close()
    if a.json:
        Path(a.json).write_text(json.dumps(to_jsonable(res), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
