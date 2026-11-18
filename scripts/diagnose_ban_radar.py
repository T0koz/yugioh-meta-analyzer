"""
TOK-115 — Diagnostic du Ban Radar : pourquoi il ne bat pas les « staples les plus jouées » en TCG.

Lecture seule. N'écrit rien en base, ne modifie ni `WEIGHTS` ni le calcul du score.

    python scripts/diagnose_ban_radar.py                       # base du dépôt, sorties dans ./diagnostic_ban_radar
    python scripts/diagnose_ban_radar.py --db <chemin> --out <dossier>
    python scripts/diagnose_ban_radar.py --annonces --db <chemin> --out <dossier>   # lot 21 : veille de l'annonce

Démarche (détail et lecture : docs/journal/ban-radar-tcg-diagnostic.md) :

1. Jeu de données : une ligne par (banlist retenue, carte de l'univers noté la veille). Les six critères sont
   ceux que calcule `build_ban_radar.build` la veille de l'entrée en vigueur ; on les lit dans le classement
   renvoyé par `build_ban_radar.backtest_lists`, la seule source autorisée du backtest (aucune copie du calcul).
   Cible : 1 si la carte est touchée par la liste (gain de sévérité), 0 sinon.
2. Modèle : régression logistique, `class_weight="balanced"`, C = 1 fixé a priori (aucun réglage, donc aucune
   sélection sur les listes de test), critères standardisés sur les seules listes d'entraînement.
3. Validation temporelle à fenêtre croissante : pour chaque liste à tester, entraînement sur les listes dont
   l'entrée en vigueur précède la veille de la liste testée. Jamais de mélange entre dates.
4. Mesures par liste tenue à l'écart : rang médian des cartes touchées, cartes touchées dans le top 25, AUC,
   précision moyenne. Comparées aux poids actuels, aux staples (part des decks seule) et au hasard.
   Incertitude : bootstrap par liste (on rééchantillonne des listes, pas des cartes).

Graine fixée (`SEED`) : deux exécutions sur la même base donnent les mêmes chiffres.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_radar as radar  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"

FEATURES = list(radar.WEIGHTS)                       # les six critères, dans l'ordre du script
FEATURES_NO_BRIDGE = [f for f in FEATURES if f != "bridge"]   # `bridge` lit le graphe actuel (fuite)
TOP_N = 25                                           # même top que la page Historique
MIN_TRAIN_LISTS = 3                                  # listes d'entraînement minimales avant la 1re liste testée
C = 1.0                                              # régularisation par défaut de scikit-learn, non réglée
BOOT = 10_000
SEED = 115


# --------------------------------------------------------------------------- données

def load_dataset(conn: sqlite3.Connection,
                 as_of_override: dict[str, str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, lists = [], []
    for fmt in ("TCG", "OCG"):
        for res in radar.backtest_lists(conn, fmt, as_of_override):
            if not res["retained"]:
                continue
            df = res["ranking"]
            hits = set(res["hits"])
            d = df[FEATURES + ["ban_risk_score", "mean_copies", "n_archetypes", "current_status"]].copy()
            d["card_name"] = df.index
            d["format"] = fmt
            d["effective"] = res["effective"]
            d["as_of"] = res["as_of"]
            d["position"] = np.arange(1, len(d) + 1)       # rang du score actuel, comme --backtest
            d["generic"] = df.top_archetype.isna().astype(int).values
            d["y"] = d.card_name.isin(hits).astype(int)
            rows.append(d.reset_index(drop=True))
            lists.append({"format": fmt, "effective": res["effective"], "as_of": res["as_of"],
                          "n": len(d), "k": int(d.y.sum()), "k_missing": len(res["missing"]),
                          "n_decks": int(res["n_decks"])})
    return pd.concat(rows, ignore_index=True), pd.DataFrame(lists)


# --------------------------------------------------------------------------- mesures

def rank_desc(score: np.ndarray) -> np.ndarray:
    return pd.Series(score).rank(ascending=False, method="average").to_numpy()


def list_metrics(y: np.ndarray, ranks: np.ndarray, score: np.ndarray) -> dict:
    n, k = len(y), int(y.sum())
    hit_ranks = ranks[y == 1]
    return {
        "median_rank": float(np.median(hit_ranks)),
        "median_pct": float(np.median(hit_ranks) / n),
        "top25": int((hit_ranks <= TOP_N).sum()),
        "auc": float(roc_auc_score(y, score)),
        "ap": float(average_precision_score(y, score)),
        "k": k, "n": n,
    }


def random_metrics(n: int, k: int) -> dict:
    # Espérances sous tirage uniforme : rang médian (n+1)/2, top 25 = k*25/n, AUC 0,5, précision moyenne ≈ k/n.
    return {"median_rank": (n + 1) / 2, "median_pct": (n + 1) / 2 / n, "top25": k * TOP_N / n,
            "auc": 0.5, "ap": k / n, "k": k, "n": n}


def score_methods(test: pd.DataFrame, learned: dict[str, np.ndarray]) -> dict[str, dict]:
    y = test.y.to_numpy()
    out = {
        "poids_actuels": list_metrics(y, test.position.to_numpy().astype(float), test.ban_risk_score.to_numpy()),
        "staples": list_metrics(y, rank_desc(test.ubiquity.to_numpy()), test.ubiquity.to_numpy()),
        "hasard": random_metrics(len(y), int(y.sum())),
    }
    for name, s in learned.items():
        out[name] = list_metrics(y, rank_desc(s), s)
    return out


# --------------------------------------------------------------------------- modèles

def fit_logit(train: pd.DataFrame, feats: list[str]) -> tuple[LogisticRegression, StandardScaler]:
    scaler = StandardScaler().fit(train[feats])
    model = LogisticRegression(C=C, class_weight="balanced", max_iter=5000)
    model.fit(scaler.transform(train[feats]), train.y)
    return model, scaler


def logit_score(model, scaler, test, feats) -> np.ndarray:
    return model.decision_function(scaler.transform(test[feats]))


def implied_weights(model, scaler, feats) -> pd.Series:
    """Coefficients ramenés à l'échelle brute des critères, puis normalisés (somme des |poids| = 1).

    Le score actuel est une somme pondérée des critères bruts ; dans une liste, la régression classe les cartes
    par sa partie linéaire (l'intercept ne change pas l'ordre). Coefficient brut = coefficient standardisé / écart
    type : les deux jeux de poids sont alors comparables terme à terme.
    """
    raw = pd.Series(model.coef_[0] / scaler.scale_, index=feats)
    return raw / raw.abs().sum()


def walk_forward(data: pd.DataFrame, lists: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fenêtre croissante. Renvoie les mesures par liste testée et les poids estimés à chaque pas."""
    per_list, coefs = [], []
    data = data.assign(is_ocg=(data.format == "OCG").astype(int))
    for fmt in ("TCG", "OCG"):
        fl = lists[lists.format == fmt].sort_values("effective").reset_index(drop=True)
        for i in range(MIN_TRAIN_LISTS, len(fl)):
            row = fl.iloc[i]
            test = data[(data.format == fmt) & (data.effective == row.effective)]
            # Labels connus la veille de la liste testée : entrée en vigueur strictement antérieure.
            same = data[(data.format == fmt) & (data.effective < row.as_of)]
            pooled = data[data.effective < row.as_of]
            learned = {}
            m6, s6 = fit_logit(same, FEATURES)
            learned["logit_6"] = logit_score(m6, s6, test, FEATURES)
            m5, s5 = fit_logit(same, FEATURES_NO_BRIDGE)
            learned["logit_5_sans_bridge"] = logit_score(m5, s5, test, FEATURES_NO_BRIDGE)
            mp, sp = fit_logit(pooled, FEATURES + ["is_ocg"])
            learned["logit_6_tcg+ocg"] = logit_score(mp, sp, test, FEATURES + ["is_ocg"])
            # Comparaison non linéaire : arbres boostés, poids d'échantillon équilibrés.
            w = np.where(same.y == 1, (same.y == 0).sum() / max(same.y.sum(), 1), 1.0)
            gb = HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05,
                                                random_state=SEED)
            gb.fit(same[FEATURES], same.y, sample_weight=w)
            learned["arbres"] = gb.predict_proba(test[FEATURES])[:, 1]

            for method, m in score_methods(test, learned).items():
                per_list.append({"format": fmt, "effective": row.effective, "method": method,
                                 "n_train_lists": i, "n_train_pos": int(same.y.sum()), **m})
            coefs.append({"format": fmt, "effective": row.effective, "n_train_lists": i,
                          **implied_weights(m6, s6, FEATURES).round(3).to_dict()})
    return pd.DataFrame(per_list), pd.DataFrame(coefs)


# --------------------------------------------------------------------------- incertitude

def bootstrap_diff(per_list: pd.DataFrame, fmt: str, a: str, b: str, metric: str,
                   rng: np.random.Generator) -> tuple[float, float, float, int, int, int]:
    """Différence a − b de la moyenne (somme pour top25) d'une mesure, bootstrap par liste.

    Renvoie (estimation, borne 5 %, borne 95 %, listes où a fait mieux, listes, égalités).
    Les fenêtres de 6 mois se chevauchent et 7 listes c'est peu : l'intervalle est optimiste, à lire avec le
    test du signe.
    """
    p = per_list[per_list.format == fmt].pivot(index="effective", columns="method", values=metric)
    d = (p[a] - p[b]).to_numpy()
    agg = np.sum if metric == "top25" else np.mean
    idx = rng.integers(0, len(d), size=(BOOT, len(d)))
    draws = agg(d[idx], axis=1)
    lower_is_better = metric in ("median_rank", "median_pct")
    wins = int((d < 0).sum() if lower_is_better else (d > 0).sum())
    lo, hi = np.percentile(draws, [5, 95])
    return float(agg(d)), float(lo), float(hi), wins, len(d), int((d == 0).sum())


def sign_test(wins: int, n: int, ties: int) -> float:
    """Test du signe bilatéral, égalités retirées : plus prudent que le bootstrap sur 7 listes."""
    return float(binomtest(wins, n - ties).pvalue) if n - ties else 1.0


def bootstrap_weights(data: pd.DataFrame, fmt: str, rng: np.random.Generator, n_boot: int = 2000) -> pd.DataFrame:
    """Intervalle des poids estimés sur toutes les listes du format, en rééchantillonnant des listes."""
    d = data[data.format == fmt]
    eff = d.effective.unique()
    groups = {e: d[d.effective == e] for e in eff}
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(eff, size=len(eff), replace=True)
        sample = pd.concat([groups[e] for e in pick], ignore_index=True)
        if sample.y.sum() < 5:
            continue
        m, s = fit_logit(sample, FEATURES)
        draws.append(implied_weights(m, s, FEATURES))
    draws = pd.DataFrame(draws)
    return pd.DataFrame({"p05": draws.quantile(0.05), "p50": draws.quantile(0.5), "p95": draws.quantile(0.95),
                         "part_positive": (draws > 0).mean()})


# --------------------------------------------------------------------------- diagnostics descriptifs

def univariate_auc(data: pd.DataFrame) -> pd.DataFrame:
    """AUC de chaque critère pris seul, liste par liste (0,5 = hasard ; < 0,5 = classe à l'envers)."""
    out = []
    for (fmt, eff), g in data.groupby(["format", "effective"]):
        row = {"format": fmt, "effective": eff}
        for f in FEATURES + ["ban_risk_score"]:
            row[f] = roc_auc_score(g.y, g[f])
        out.append(row)
    return pd.DataFrame(out)


def drop_one(data: pd.DataFrame) -> pd.DataFrame:
    """Score actuel recalculé sans un critère (poids restants inchangés), AUC moyenne et top 25 par format.

    Aucun ajustement : les poids sont ceux du script, on retire un terme à la fois. Le rééchelonnage sur le
    maximum et l'exclusion des cartes Forbidden ne changent pas l'ordre (déjà appliqués dans l'univers lu).
    """
    out = []
    variants = {"tous": FEATURES, **{f"sans_{f}": [x for x in FEATURES if x != f] for f in FEATURES}}
    for name, feats in variants.items():
        for fmt in ("TCG", "OCG"):
            aucs, top, meds = [], 0, []
            for _, g in data[data.format == fmt].groupby("effective"):
                s = sum(g[f] * radar.WEIGHTS[f] for f in feats).to_numpy()
                m = list_metrics(g.y.to_numpy(), rank_desc(s), s)
                aucs.append(m["auc"]); top += m["top25"]; meds.append(m["median_rank"])
            out.append({"variante": name, "format": fmt, "auc_moy": np.mean(aucs), "top25": top,
                        "mediane_des_rangs_medians": np.median(meds)})
    return pd.DataFrame(out)


def effective_weights(data: pd.DataFrame) -> pd.DataFrame:
    """Poids nominaux contre poids effectifs du score actuel.

    Dans une somme pondérée, ce qui départage les cartes n'est pas le poids seul mais poids x dispersion du critère :
    un critère qui varie peu d'une carte à l'autre (la part des decks : presque toutes les cartes sont sous 5 %)
    pèse peu dans le classement, quel que soit son poids. Dispersion = écart type intra-liste, moyenné sur les listes.
    """
    out = []
    for fmt, g in data.groupby("format"):
        sd = g.groupby("effective")[FEATURES].std().mean()
        eff = pd.Series({f: radar.WEIGHTS[f] * sd[f] for f in FEATURES})
        for f in FEATURES:
            out.append({"format": fmt, "critere": f, "poids_nominal": radar.WEIGHTS[f],
                        "ecart_type": sd[f], "poids_effectif": eff[f] / eff.sum()})
    return pd.DataFrame(out).pivot(index="critere", columns="format",
                                   values=["poids_nominal", "ecart_type", "poids_effectif"]).loc[FEATURES]


def reference_rankings(data: pd.DataFrame) -> pd.DataFrame:
    """Classements sans aucun ajustement sur les 20 listes : poids actuels, part des decks, critère porteur seul.

    Le critère porteur est retenu ici après avoir vu les AUC univariées : c'est une description, pas un modèle
    validé (il n'est pas tenu à l'écart).
    """
    out = []
    for (fmt, eff), g in data.groupby(["format", "effective"]):
        y = g.y.to_numpy()
        for name, s, ranks in (("poids_actuels", g.ban_risk_score, g.position.astype(float)),
                               ("staples", g.ubiquity, None), ("carrier_seul", g.carrier, None)):
            s = s.to_numpy()
            m = list_metrics(y, ranks.to_numpy() if ranks is not None else rank_desc(s), s)
            out.append({"format": fmt, "effective": eff, "method": name, **m})
    return pd.DataFrame(out)


def hit_profile(data: pd.DataFrame) -> pd.DataFrame:
    """Médiane de chaque critère chez les cartes touchées et les autres, par format."""
    cols = FEATURES + ["mean_copies", "n_archetypes", "generic"]
    g = data.groupby(["format", "y"])[cols].median().round(4)
    g["n"] = data.groupby(["format", "y"]).size()
    return g


# --------------------------------------------------------------------------- lot 21 : veille de l'annonce

SCENARIOS = {
    # nom: (colonne de banlist_announcements, repli sur la borne haute `first_source_date` ?)
    "effective": None,
    "annonce": ("announced_date", False),            # la date que dit Yugipedia (peut n'être qu'une date de sortie)
    "contenu": ("content_date", False),              # jour de publication des cartes, preuve à l'appui
    "contenu+borne": ("content_date", True),         # idem, + borne haute (source citée) pour 4 listes TCG
}


def announcement_overrides(conn: sqlite3.Connection) -> dict[str, dict[str, tuple[str, str]]]:
    """{scénario: {format|effective: (veille de la date, nature de la date)}}, lu dans `banlist_announcements`.

    Une liste sans date pour le scénario garde la veille de l'entrée en vigueur (nature « inchangée »).
    """
    have = conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'banlist_announcements'").fetchone()
    if not have:
        raise SystemExit("Table banlist_announcements absente : lancer scripts/fetch_banlist_announcements.py")
    ann = pd.read_sql_query("SELECT * FROM banlist_announcements", conn)
    out: dict[str, dict] = {}
    for name, spec in SCENARIOS.items():
        if spec is None:
            continue
        col, bound = spec
        m = {}
        for _, r in ann.iterrows():
            day, kind = r[col], "date"
            if (day is None or pd.isna(day)) and bound and isinstance(r.first_source_date, str):
                day, kind = r.first_source_date, "borne"
            if isinstance(day, str) and day <= r.effective_date:
                eve = (pd.Timestamp(day) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                # Jamais plus tard que la veille de l'entrée en vigueur (une annonce le jour même ne change rien).
                eff_eve = (pd.Timestamp(r.effective_date) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
                m[(r.format, r.effective_date)] = (min(eve, eff_eve), kind)
        out[name] = m
    return out


def decks_between(conn: sqlite3.Connection, fmt: str, as_of_new: str, as_of_eff: str) -> tuple[int, int]:
    """(decks légaux joués dans (as_of_new, as_of_eff], decks de la fenêtre habituelle se terminant à as_of_eff)."""
    usage = radar.load_usage(conn, as_of_eff, fmt)
    ids = usage.deck_id.unique().tolist()
    created = pd.read_sql_query(
        f"SELECT id, created FROM tournament_decks WHERE id IN ({','.join('?' * len(ids))})", conn, params=ids)
    return int((created.created > as_of_new).sum()), len(ids)


def scenario_dataset(conn: sqlite3.Connection, over: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Jeu de données d'un scénario : override groupé par format (`backtest_lists` le lit par date d'effet)."""
    rows, lists = [], []
    for fmt in ("TCG", "OCG"):
        sub = {eff: v[0] for (f, eff), v in over.items() if f == fmt}
        d, l = load_dataset_one(conn, fmt, sub)
        rows.append(d); lists.append(l)
    return pd.concat(rows, ignore_index=True), pd.concat(lists, ignore_index=True)


def load_dataset_one(conn: sqlite3.Connection, fmt: str, override: dict[str, str]):
    rows, lists = [], []
    for res in radar.backtest_lists(conn, fmt, override):
        if not res["retained"]:
            lists.append({"format": fmt, "effective": res["effective"], "as_of": res["as_of"], "retained": 0,
                          "n": 0, "k": len(res["hits"]), "k_missing": 0, "n_decks": int(res["n_decks"])})
            continue
        df = res["ranking"]
        hits = set(res["hits"])
        d = df[FEATURES + ["ban_risk_score", "mean_copies", "n_archetypes", "current_status"]].copy()
        d["card_name"] = df.index
        d["format"] = fmt
        d["effective"] = res["effective"]
        d["as_of"] = res["as_of"]
        d["position"] = np.arange(1, len(d) + 1)
        d["generic"] = df.top_archetype.isna().astype(int).values
        d["y"] = d.card_name.isin(hits).astype(int)
        rows.append(d.reset_index(drop=True))
        lists.append({"format": fmt, "effective": res["effective"], "as_of": res["as_of"], "retained": 1,
                      "n": len(d), "k": int(d.y.sum()), "k_missing": len(res["missing"]),
                      "n_decks": int(res["n_decks"])})
    return (pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()), pd.DataFrame(lists)


def announcement_effect(conn: sqlite3.Connection, out: Path) -> None:
    """Classer « la veille de l'annonce » au lieu de « la veille de l'entrée en vigueur ».

    Trois scénarios contre la référence, sur les mêmes listes (celles retenues dans les deux) :
    la date que dit Yugipedia (`annonce`), le jour de publication des cartes (`contenu`), et `contenu` complété par
    la borne haute de 4 listes TCG sans date d'annonce écrite (`contenu+borne`). Mesures par liste : rang médian
    des cartes touchées, cartes touchées dans le top 25, AUC ; poids actuels, staples (part des decks), hasard.
    Incertitude : bootstrap par liste (graine fixe) et test du signe. Aucune estimation : les poids sont ceux du
    script, rien n'est ajusté.
    """
    base_data, base_lists = scenario_dataset(conn, {})
    ref_set = set(zip(base_lists[base_lists.retained == 1].format, base_lists[base_lists.retained == 1].effective))
    print(f"Référence (veille de l'entrée en vigueur) : {len(ref_set)} listes retenues")
    # Seules les listes du backtest sont rejouées à une autre date (les 150 autres listes de la table n'y servent pas).
    overrides = {n: {k: v for k, v in o.items() if k in ref_set} for n, o in announcement_overrides(conn).items()}

    scen_data, scen_lists, shifts = {"effective": base_data}, {"effective": base_lists}, []
    for name, over in overrides.items():
        d, l = scenario_dataset(conn, over)
        scen_data[name], scen_lists[name] = d, l
        for (fmt, eff), (as_of, kind) in over.items():
            eve = (pd.Timestamp(eff) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            if as_of >= eve:
                continue
            n_between, n_win = decks_between(conn, fmt, as_of, eve)
            shifts.append({"scenario": name, "format": fmt, "effective": eff, "as_of": as_of, "nature": kind,
                           "jours_avant": (pd.Timestamp(eve) - pd.Timestamp(as_of)).days,
                           "decks_exclus": n_between, "decks_fenetre": n_win,
                           "part_exclue": n_between / n_win if n_win else np.nan})
    shifts = pd.DataFrame(shifts)
    shifts.to_csv(out / "annonces_decalages.csv", index=False)

    rng = np.random.default_rng(SEED)
    per_rows = []
    for name, data in scen_data.items():
        if data.empty:
            continue
        for (fmt, eff), g in data.groupby(["format", "effective"]):
            for method, m in score_methods(g, {}).items():
                per_rows.append({"scenario": name, "format": fmt, "effective": eff, "method": method, **m})
    per = pd.DataFrame(per_rows)
    per.to_csv(out / "annonces_par_liste.csv", index=False)

    retained = {n: set(zip(l[l.retained == 1].format, l[l.retained == 1].effective)) for n, l in scen_lists.items()}
    for name in overrides:
        lost = sorted(retained["effective"] - retained[name])
        print(f"[{name}] listes retenues : {len(retained[name])} ; perdues par rapport à la référence : {lost or 'aucune'}")

    print("\n== Décalage de la date de coupure, par liste (scénario « contenu+borne ») ==")
    sh = shifts[shifts.scenario == "contenu+borne"]
    print(sh.round(3).to_string(index=False))
    for fmt in ("TCG", "OCG"):
        s_ = sh[sh.format == fmt]
        print(f"{fmt} : {len(s_)} listes décalées sur {sum(1 for f, _ in ref_set if f == fmt)} ; jours avant l'entrée en vigueur, médiane "
              f"{s_.jours_avant.median():.0f} (min {s_.jours_avant.min()}, max {s_.jours_avant.max()}) ; part des decks de la "
              f"fenêtre exclus, médiane {s_.part_exclue.median():.1%} (max {s_.part_exclue.max():.1%})")

    print("\n== Mesures par scénario (listes retenues dans le scénario ET dans la référence) ==")
    summary, paired = [], []
    for name in ["effective", *overrides]:
        common = retained["effective"] & retained[name]
        p = per[(per.scenario == name) & per.set_index(["format", "effective"]).index.isin(common)]
        for (fmt, method), g in p.groupby(["format", "method"]):
            summary.append({"scenario": name, "format": fmt, "method": method, "listes": g.effective.nunique(),
                            "mediane_des_rangs_medians": g.median_rank.median(), "rang_median_pct_moy": g.median_pct.mean(),
                            "top25_total": g.top25.sum(), "cartes_touchees": g.k.sum(), "auc_moy": g.auc.mean()})
    summary = pd.DataFrame(summary)
    summary.to_csv(out / "annonces_synthese.csv", index=False)
    print(summary.round(3).to_string(index=False))

    print("\n== Écart de chaque scénario à la référence, liste par liste (bootstrap par liste, intervalle 90 %) ==")
    print("Un écart positif de `rang_median_pct` = classement moins bon qu'à la veille de l'entrée en vigueur.")
    for name in overrides:
        common = sorted(retained["effective"] & retained[name])
        moved = set(zip(shifts[shifts.scenario == name].format, shifts[shifts.scenario == name].effective))
        for fmt in ("TCG", "OCG"):
            for method in ("poids_actuels", "staples"):
                for metric in ("median_pct", "top25", "auc"):
                    a = per[(per.scenario == name) & (per.format == fmt) & (per.method == method)].set_index("effective")[metric]
                    b = per[(per.scenario == "effective") & (per.format == fmt) & (per.method == method)].set_index("effective")[metric]
                    effs = [e for (f, e) in common if f == fmt and (f, e) in moved]
                    if not effs:
                        continue
                    d = (a.loc[effs] - b.loc[effs]).to_numpy()
                    agg = np.sum if metric == "top25" else np.mean
                    idx = rng.integers(0, len(d), size=(BOOT, len(d)))
                    lo, hi = np.percentile(agg(d[idx], axis=1), [5, 95])
                    better = int((d < 0).sum()) if metric == "median_pct" else int((d > 0).sum())
                    worse = int((d > 0).sum()) if metric == "median_pct" else int((d < 0).sum())
                    paired.append({"scenario": name, "format": fmt, "methode": method, "mesure": metric,
                                   "listes_decalees": len(d), "ecart": float(agg(d)), "p05": float(lo), "p95": float(hi),
                                   "mieux": better, "pire": worse, "egalites": int((d == 0).sum()),
                                   "p_signe": sign_test(better, len(d), int((d == 0).sum()))})
    paired = pd.DataFrame(paired)
    paired.to_csv(out / "annonces_ecarts.csv", index=False)
    print(paired.round(4).to_string(index=False))

    print("\n== Score contre staples dans chaque scénario (listes retenues dans les deux scénarios) ==")
    rel = []
    for name in ["effective", *overrides]:
        common = retained["effective"] & retained[name]
        for fmt in ("TCG", "OCG"):
            p = per[(per.scenario == name) & (per.format == fmt) & per.set_index(["format", "effective"]).index.isin(common)]
            for metric in ("median_pct", "top25", "auc"):
                pv = p.pivot(index="effective", columns="method", values=metric)
                d = (pv.poids_actuels - pv.staples).to_numpy()
                wins = int((d < 0).sum()) if metric == "median_pct" else int((d > 0).sum())
                ties = int((d == 0).sum())
                agg = np.sum if metric == "top25" else np.mean
                idx = rng.integers(0, len(d), size=(BOOT, len(d)))
                lo, hi = np.percentile(agg(d[idx], axis=1), [5, 95])
                rel.append({"scenario": name, "format": fmt, "mesure": metric, "listes": len(d),
                            "score_moins_staples": float(agg(d)), "p05": float(lo), "p95": float(hi),
                            "score_mieux": wins, "egalites": ties, "p_signe": sign_test(wins, len(d), ties)})
    rel = pd.DataFrame(rel)
    rel.to_csv(out / "annonces_score_vs_staples.csv", index=False)
    print(rel.round(4).to_string(index=False))


# --------------------------------------------------------------------------- sortie

def summarize(per_list: pd.DataFrame) -> pd.DataFrame:
    agg = per_list.groupby(["format", "method"]).agg(
        listes=("effective", "nunique"),
        mediane_des_rangs_medians=("median_rank", "median"),
        rang_median_pct_moy=("median_pct", "mean"),
        top25_total=("top25", "sum"),
        cartes_touchees=("k", "sum"),
        auc_moy=("auc", "mean"),
        ap_moy=("ap", "mean"),
    )
    return agg.round(3)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=Path("diagnostic_ban_radar"))
    parser.add_argument("--annonces", action="store_true",
                        help="Lot 21 (TOK-121) : mesure seulement l'effet de classer la veille de l'annonce "
                             "(lit banlist_announcements ; le diagnostic TOK-115 n'est pas relancé)")
    args = parser.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")
    args.out.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 30)
    warnings.filterwarnings("ignore", category=FutureWarning)

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=60)
    if args.annonces:
        announcement_effect(conn, args.out)
        return
    data, lists = load_dataset(conn)
    data.to_csv(args.out / "dataset.csv", index=False)
    print(f"Jeu de données : {len(data)} lignes, {data.y.sum()} cartes touchées classées, "
          f"{len(lists)} listes ({(lists.format == 'TCG').sum()} TCG, {(lists.format == 'OCG').sum()} OCG)")
    print(lists.to_string(index=False))

    print("\n== Profil des cartes touchées (médianes) ==")
    print(hit_profile(data).to_string())

    print("\n== AUC de chaque critère seul, moyenne et nombre de listes > 0,5 ==")
    uni = univariate_auc(data)
    uni.to_csv(args.out / "auc_univariee.csv", index=False)
    for fmt in ("TCG", "OCG"):
        u = uni[uni.format == fmt]
        print(fmt, " | ".join(f"{f} {u[f].mean():.3f} ({(u[f] > 0.5).sum()}/{len(u)})"
                              for f in FEATURES + ["ban_risk_score"]))
    print(uni.round(3).to_string(index=False))

    print("\n== Parts des cartes touchées : jouées à moins de 1,5 exemplaire, génériques, déjà restreintes ==")
    hits = data[data.y == 1]
    print(hits.groupby("format").agg(touchees=("y", "size"),
                                     moins_de_1_5_ex=("mean_copies", lambda c: round((c < 1.5).mean(), 2)),
                                     generiques=("generic", "mean"),
                                     deja_restreintes=("restriction", lambda r: round((r > 0).mean(), 2))).round(2)
          .to_string())
    top = data[data.position <= TOP_N]
    print("Top 25 du score actuel, médianes :", top.groupby("format")[["mean_copies", "ubiquity", "momentum"]]
          .median().round(3).to_dict("index"))

    print("\n== Poids nominaux et poids effectifs du score actuel ==")
    print(effective_weights(data).round(3).to_string())

    print("\n== Classements sans ajustement, 20 listes (description, pas de validation) ==")
    ref = reference_rankings(data)
    ref.to_csv(args.out / "references_20_listes.csv", index=False)
    print(ref.groupby(["format", "method"]).agg(mediane_des_rangs_medians=("median_rank", "median"),
                                                top25_total=("top25", "sum"), auc_moy=("auc", "mean"),
                                                ap_moy=("ap", "mean")).round(3).to_string())
    for fmt in ("TCG", "OCG"):
        p = ref[ref.format == fmt].pivot(index="effective", columns="method", values=["median_rank", "top25"])
        w_med = int((p.median_rank.poids_actuels < p.median_rank.staples).sum())
        w_top = int((p.top25.poids_actuels > p.top25.staples).sum())
        t_top = int((p.top25.poids_actuels == p.top25.staples).sum())
        print(f"{fmt} : poids actuels meilleurs que les staples en rang médian sur {w_med}/10 listes "
              f"(test du signe p = {sign_test(w_med, 10, 0):.3f}) ; top 25 sur {w_top}/10, {t_top} égalités "
              f"(p = {sign_test(w_top, 10, t_top):.3f})")

    print("\n== Score actuel sans un critère (poids fixes, toutes les listes, aucun ajustement) ==")
    print(drop_one(data).round(3).to_string(index=False))

    per_list, coefs = walk_forward(data, lists)
    per_list.to_csv(args.out / "par_liste.csv", index=False)
    coefs.to_csv(args.out / "poids_par_pas.csv", index=False)

    print(f"\n== Validation temporelle (au moins {MIN_TRAIN_LISTS} listes d'entraînement) : synthèse ==")
    print(summarize(per_list).to_string())

    print("\n== Par liste tenue à l'écart ==")
    show = per_list.pivot_table(index=["format", "effective", "k", "n"], columns="method",
                                values=["median_rank", "top25", "auc"]).round(2)
    print(show.to_string())

    print("\n== Écarts, bootstrap par liste (intervalle 90 %, listes où le 1er fait mieux) ==")
    rng = np.random.default_rng(SEED)
    pairs = [("logit_6", "poids_actuels"), ("logit_6", "staples"), ("poids_actuels", "staples"),
             ("logit_5_sans_bridge", "staples"), ("logit_6_tcg+ocg", "staples"), ("arbres", "staples"),
             ("staples", "hasard"), ("poids_actuels", "hasard")]
    boot_rows = []
    for fmt in ("TCG", "OCG"):
        for a, b in pairs:
            for metric in ("median_pct", "top25", "auc", "ap"):
                est, lo, hi, wins, n, ties = bootstrap_diff(per_list, fmt, a, b, metric, rng)
                boot_rows.append({"format": fmt, "a": a, "b": b, "mesure": metric, "ecart": est,
                                  "p05": lo, "p95": hi, "a_mieux": f"{wins}/{n}", "egalites": ties,
                                  "p_signe": sign_test(wins, n, ties)})
    boot = pd.DataFrame(boot_rows)
    boot.to_csv(args.out / "bootstrap.csv", index=False)
    print(boot.round(4).to_string(index=False))

    print("\n== Poids estimés à chaque pas (logit_6, |somme| = 1) ==")
    print(coefs.to_string(index=False))

    print("\n== Poids estimés sur toutes les listes du format, intervalle bootstrap par liste ==")
    for fmt in ("TCG", "OCG"):
        m, s = fit_logit(data[data.format == fmt], FEATURES)
        w = implied_weights(m, s, FEATURES)
        std = pd.Series(m.coef_[0], index=FEATURES)
        print(f"\n{fmt} — poids (échelle brute, |somme|=1) et coefficient standardisé")
        tab = pd.DataFrame({"actuel": pd.Series(radar.WEIGHTS), "estime": w.round(3),
                            "coef_standardise": std.round(3)})
        print(tab.join(bootstrap_weights(data, fmt, rng).round(3)).to_string())


if __name__ == "__main__":
    main()
