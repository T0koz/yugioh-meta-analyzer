"""
TOK-132 (B3 de l'audit de rigueur) — score de pont et simulateur de ban confrontés aux banlists du backtest.

Lecture seule. N'écrit rien en base, ne change ni `card_impact`, ni `/simulate-ban`, ni ce qu'affiche le site.

    python scripts/diagnose_pont_simulateur.py --db <base> --out <dossier>

Ce qui est testé (deux affirmations du site, jamais confrontées à un vrai ban, audit § 9 et § 10) :
- **Score de pont** (`card_impact.bridge_score = n_archetypes × log(1 + decks)`, onglet « Impact ») : « retirer une
  carte jouée par beaucoup d'archétypes fragmente plusieurs decks à la fois ».
- **Simulateur** (`POST /simulate-ban`) : la « fragmentation » (`betweenness / max`, le critère `bridge` du Ban
  Radar) et la liste des « archétypes voisins » (archétypes `cards.archetype` des 30 voisins de plus fort Jaccard,
  plus l'archétype porteur, triés par ordre alphabétique, 10 au plus).

Données : les listes retenues par `build_ban_radar.backtest_lists` (coupure à la veille de l'entrée en vigueur,
la fonction du backtest, sans copie). Tout prédicteur est calculé à la coupure, avec les seules données connues ce
jour-là : `n_archetypes`, `decks`, part des decks et archétype porteur viennent du classement de la veille ; la
fragmentation et les voisins viennent du graphe daté de TOK-120 (`bridge_date.py`).

Mesure de l'effet (audit § 9) : pour chaque carte, ses **archétypes porteurs** sont ceux dont au moins la moitié des
decks la jouent (fenêtre de 6 mois du Ban Radar, archétypes d'au moins 5 decks). Variation = part de méta cumulée de
ces archétypes dans les 3 mois qui suivent l'entrée en vigueur, moins celle des 3 mois qui précèdent la coupure, en
points (decks légaux du format). Une liste n'entre que si ses 3 mois suivants sont entièrement dans la base.

**Questions et règle, figées avant toute lecture des résultats :**
1. Un ban fait-il baisser la part de ses archétypes porteurs ? Carte touchée contre cartes non touchées de la même
   liste et de même quintile de part des decks (validation de la mesure : si le ban ne la fait pas bouger, aucun
   prédicteur ne pourra rien en dire).
2. Parmi les cartes touchées, le score de pont, la fragmentation et la part des decks seule (méthode naïve) sont-ils
   liés à la variation ? Corrélation de rang, intervalle bootstrap par liste (90 %, 10 000 tirages, graine 132).
3. **Critère de gain (hors échantillon dans le temps)** : régression de la variation sur la part des decks seule,
   contre la part des decks + score de pont (puis + fragmentation), origine glissante ; une liste ne sert à
   l'entraînement que si ses 3 mois suivants sont écoulés avant la coupure de la liste testée. Le score de pont
   (la fragmentation) « apporte un gain » si l'erreur quadratique moyenne sur les listes tenues à l'écart baisse, avec
   un intervalle bootstrap par liste à 90 % entièrement sous 0. Sinon : aucun gain, proposition de renommer
   « Impact » en « diffusion » (formulaire, rien n'est appliqué).
4. Simulateur, archétypes voisins : leurs parts baissent-elles plus que celles d'une liste naïve de même taille (les
   archétypes qui jouent le plus la carte, en nombre de decks) ? Gain si la différence de variation moyenne est
   négative avec un intervalle à 90 % sous 0. (Corrigé après la relecture data-scientist : critère en variation
   relative par archétype, archétypes d'au moins 5 decks des deux côtés ; la première version, en points, favorisait
   la liste naïve, faite des plus gros archétypes.) On mesure aussi combien de noms de la liste existent comme archétype de
   deck (le simulateur lit `cards.archetype`, nomenclature YGOPRODeck, et non l'archétype des decks).
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_radar as radar  # noqa: E402
from bridge_date import DatedGraph  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"

HORIZON_MONTHS = 3
CORENESS_MIN = 0.5            # archétype porteur : au moins la moitié de ses decks jouent la carte
ARCHETYPE_MIN_DECKS = 5
NEIGHBOR_LIMIT = 30           # backend/app/routers/cards.py, COOCCURRENCE_NEIGHBOR_LIMIT
AFFECTED_LIMIT = 10           # backend/app/routers/cards.py, AFFECTED_ARCHETYPES_LIMIT
MIN_TRAIN_LISTS = 4
BOOT = 10_000
SEED = 132
PREDICTORS = ["bridge_score", "fragmentation", "ubiquity", "n_archetypes"]


# --------------------------------------------------------------------------- données

def legal_decks(conn: sqlite3.Connection, fmt: str) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT id, archetype, substr(created, 1, 10) AS day FROM tournament_decks "
        "WHERE ocg = ? AND id IN (SELECT deck_id FROM deck_legality WHERE legal = 1)",
        conn, params=(1 if fmt == "OCG" else 0,))


def shares(decks: pd.DataFrame, start: str, end: str, right_closed: bool) -> tuple[pd.Series, int]:
    """Part de méta de chaque archétype sur [start, end) ou (start, end]."""
    w = decks[(decks.day > start) & (decks.day <= end)] if right_closed else \
        decks[(decks.day >= start) & (decks.day < end)]
    return w.archetype.value_counts(normalize=True), len(w)


def card_frame(conn, graph, card_arch, res, decks, last_day) -> pd.DataFrame | None:
    """Une ligne par carte de l'univers de la liste : prédicteurs à la coupure et variation des porteurs."""
    as_of, eff, fmt = res["as_of"], res["effective"], res["format"]
    post_end = (pd.Timestamp(eff) + pd.DateOffset(months=HORIZON_MONTHS)).strftime("%Y-%m-%d")
    if post_end > last_day:
        return None
    pre_start = (pd.Timestamp(as_of) - pd.DateOffset(months=HORIZON_MONTHS)).strftime("%Y-%m-%d")
    before, n_before = shares(decks, pre_start, as_of, right_closed=True)
    after, n_after = shares(decks, eff, post_end, right_closed=False)
    archs = before.index.union(after.index)
    delta = (after.reindex(archs).fillna(0) - before.reindex(archs).fillna(0)) * 100      # en points

    usage = radar.load_usage(conn, as_of, fmt)
    arch_decks = usage.groupby("archetype").deck_id.nunique()
    pairs = usage.groupby(["card_name", "archetype"]).deck_id.nunique().rename("decks").reset_index()
    pairs["coreness"] = pairs.decks / pairs.archetype.map(arch_decks)
    pairs = pairs[pairs.archetype.map(arch_decks) >= ARCHETYPE_MIN_DECKS]
    porteurs = pairs[pairs.coreness >= CORENESS_MIN].groupby("card_name").archetype.apply(list)

    rk = res["ranking"]
    hits = set(res["hits"])
    df = pd.DataFrame(index=rk.index)
    df["format"], df["effective"], df["as_of"] = fmt, eff, as_of
    df["list_id"] = f"{fmt}|{eff}"
    df["y_hit"] = df.index.isin(hits).astype(int)
    df["ubiquity"] = rk.ubiquity
    df["decks"] = rk.decks
    df["n_archetypes"] = rk.n_archetypes
    df["bridge_score"] = rk.n_archetypes * np.log1p(rk.decks)          # formule de build_card_impact.py
    df["fragmentation"] = graph.bridge(as_of, rk.index).to_numpy()      # betweenness datée / max
    df["porteurs"] = porteurs.reindex(rk.index)
    df["n_porteurs"] = df.porteurs.apply(lambda p: len(p) if isinstance(p, list) else 0)
    df["share_before"] = df.porteurs.apply(
        lambda p: float(before.reindex(p).fillna(0).sum()) * 100 if isinstance(p, list) else np.nan)
    df["variation"] = df.porteurs.apply(
        lambda p: float(delta.reindex(p).fillna(0).sum()) if isinstance(p, list) else np.nan)
    df["variation_rel"] = df.variation / df.share_before.where(df.share_before > 0)
    df["n_decks_before"], df["n_decks_after"] = n_before, n_after

    # Simulateur, liste des archétypes voisins (seulement pour les cartes touchées : c'est l'objet du test).
    # Variation relative par archétype : un petit archétype ne peut pas perdre beaucoup de points (relecture
    # data-scientist) ; même filtre (au moins 5 decks sur la fenêtre de 6 mois) des deux côtés.
    rel = delta / (before.reindex(archs) * 100)
    sim, naive, matched = {}, {}, {}
    deck_archs = {a for a in archs if arch_decks.get(a, 0) >= ARCHETYPE_MIN_DECKS and before.get(a, 0) > 0}
    for card in df.index[df.y_hit == 1]:
        names = set(card_arch.reindex(graph.neighbors(as_of, card, NEIGHBOR_LIMIT)).dropna())
        if isinstance(rk.top_archetype.get(card), str):
            names.add(rk.top_archetype[card])
        listed = sorted(names)[:AFFECTED_LIMIT]
        ok = [a for a in listed if a in deck_archs]
        sim[card], matched[card] = listed, ok
        by_decks = pairs[pairs.card_name == card].sort_values("decks", ascending=False).archetype.tolist()
        naive[card] = by_decks[:max(len(ok), 1)]
    df["sim_listed"] = pd.Series(sim).reindex(df.index)
    df["sim_matched"] = pd.Series(matched).reindex(df.index)
    df["naive_listed"] = pd.Series(naive).reindex(df.index)
    mean_delta = lambda lst: float(delta.reindex(lst).fillna(0).mean()) if isinstance(lst, list) and lst else np.nan
    df["sim_delta"] = df.sim_matched.apply(mean_delta)
    df["naive_delta"] = df.naive_listed.apply(mean_delta)
    mean_rel = lambda lst: float(rel.reindex(lst).mean()) if isinstance(lst, list) and lst else np.nan
    df["sim_rel"] = df.sim_matched.apply(mean_rel)
    df["naive_rel"] = df.naive_listed.apply(mean_rel)
    df["sim_declined"] = df.sim_matched.apply(
        lambda lst: float((delta.reindex(lst).fillna(0) < 0).mean()) if isinstance(lst, list) and lst else np.nan)
    df["naive_declined"] = df.naive_listed.apply(
        lambda lst: float((delta.reindex(lst).fillna(0) < 0).mean()) if isinstance(lst, list) and lst else np.nan)
    return df.reset_index(names="card_name")


def load(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    graph = DatedGraph(conn)
    card_arch = pd.read_sql_query("SELECT name, archetype FROM cards WHERE archetype IS NOT NULL", conn) \
        .drop_duplicates("name").set_index("name").archetype
    frames, lists = [], []
    for fmt in ("TCG", "OCG"):
        decks = legal_decks(conn, fmt)
        last_day = decks.day.max()
        for res in radar.backtest_lists(conn, fmt):
            if not res["retained"]:
                continue
            f = card_frame(conn, graph, card_arch, res, decks, last_day)
            lists.append({"format": fmt, "effective": res["effective"], "as_of": res["as_of"],
                          "complete": f is not None, "k_ranked": len(res["ranked"]),
                          "n_decks_before": None if f is None else int(f.n_decks_before.iloc[0]),
                          "n_decks_after": None if f is None else int(f.n_decks_after.iloc[0])})
            if f is not None:
                frames.append(f)
    return pd.concat(frames, ignore_index=True), pd.DataFrame(lists)


# --------------------------------------------------------------------------- incertitude

def boot_lists(df: pd.DataFrame, stat, rng: np.random.Generator, n: int = BOOT) -> tuple[float, float, float]:
    """Statistique et intervalle à 90 % en rééchantillonnant des listes (les cartes d'une liste ne sont pas
    indépendantes : même fenêtre, mêmes archétypes, souvent le même deck visé par plusieurs cartes)."""
    ids = df.list_id.unique()
    groups = {i: df[df.list_id == i] for i in ids}
    draws = []
    for _ in range(n):
        pick = rng.choice(ids, size=len(ids), replace=True)
        s = stat(pd.concat([groups[i] for i in pick], ignore_index=True))
        if np.isfinite(s):
            draws.append(s)
    lo, hi = np.percentile(draws, [5, 95])
    return float(stat(df)), float(lo), float(hi)


def rho(x: str, y: str):
    return lambda d: spearmanr(d[x], d[y]).statistic if d[x].nunique() > 1 else np.nan


# --------------------------------------------------------------------------- analyses

def ban_effect(data: pd.DataFrame, rng, clean: bool = False) -> pd.DataFrame:
    """Q1 : variation des porteurs d'une carte touchée moins celle des non-touchées de même liste et même quintile."""
    d = data[data.n_porteurs > 0].copy()
    d["quintile"] = d.groupby("list_id").ubiquity.transform(lambda u: pd.qcut(u.rank(method="first"), 5, labels=False))
    if clean:
        # Relecture data-scientist : un contrôle qui partage un porteur avec une carte touchée de la même liste
        # subit lui aussi le ban, ce qui tire l'effet vers 0. Variante sans ces contrôles.
        hit_archs = d[d.y_hit == 1].groupby("list_id").porteurs.apply(lambda s: set().union(*map(set, s)))
        shared = d.apply(lambda r: bool(set(r.porteurs) & hit_archs.get(r.list_id, set())), axis=1)
        d = d[(d.y_hit == 1) | ~shared]
    ctrl = d[d.y_hit == 0].groupby(["list_id", "quintile"]).variation.median().rename("controle")
    hits = d[d.y_hit == 1].join(ctrl, on=["list_id", "quintile"])
    hits = hits.dropna(subset=["controle"]) if clean else hits
    hits["effet"] = hits.variation - hits.controle
    rows = []
    for fmt, g in [("tous", hits), *hits.groupby("format")]:
        est, lo, hi = boot_lists(g, lambda x: x.effet.mean(), rng)
        rows.append({"format": fmt, "cartes_touchees": len(g), "listes": g.list_id.nunique(),
                     "variation_touchees_moy": g.variation.mean(), "controle_moy": g.controle.mean(),
                     "effet_moy_points": est, "p05": lo, "p95": hi, "part_touchees_en_baisse": (g.variation < 0).mean()})
    return pd.DataFrame(rows), hits


def correlations(hits: pd.DataFrame, rng) -> pd.DataFrame:
    """Q2 : corrélation de rang entre chaque prédicteur et la variation, cartes touchées seulement."""
    rows = []
    for target in ("variation", "variation_rel"):
        d = hits.dropna(subset=[target])
        for p in PREDICTORS:
            est, lo, hi = boot_lists(d, rho(p, target), rng)
            rows.append({"cible": target, "predicteur": p, "rho": est, "p05": lo, "p95": hi, "cartes": len(d)})
        for p in ("bridge_score", "fragmentation"):
            f = lambda x, p=p: rho(p, target)(x) - rho("ubiquity", target)(x)
            est, lo, hi = boot_lists(d, f, rng)
            rows.append({"cible": target, "predicteur": f"{p} − ubiquity", "rho": est, "p05": lo, "p95": hi,
                         "cartes": len(d)})
    return pd.DataFrame(rows)


def _ols(train: pd.DataFrame, test: pd.DataFrame, feats: list[str], target: str = "variation") -> np.ndarray:
    mu, sd = train[feats].mean(), train[feats].std(ddof=0).replace(0, 1)
    X = np.column_stack([np.ones(len(train)), ((train[feats] - mu) / sd).to_numpy()]) if feats else np.ones((len(train), 1))
    beta, *_ = np.linalg.lstsq(X, train[target].to_numpy(), rcond=None)
    Xt = np.column_stack([np.ones(len(test)), ((test[feats] - mu) / sd).to_numpy()]) if feats else np.ones((len(test), 1))
    return Xt @ beta


def walk_forward(hits: pd.DataFrame, target: str = "variation") -> pd.DataFrame:
    """Q3 : origine glissante, listes des deux formats ensemble (variable de format), ordonnées par coupure.

    Une liste n'entre dans l'entraînement que si sa variation est connue à la coupure de la liste testée :
    entrée en vigueur + 3 mois antérieure à cette coupure.
    """
    d = hits.dropna(subset=[target]).assign(is_ocg=lambda x: (x.format == "OCG").astype(int))
    meta = d.groupby("list_id").agg(as_of=("as_of", "first"), effective=("effective", "first")).sort_values("as_of")
    meta["known"] = (pd.to_datetime(meta.effective) + pd.DateOffset(months=HORIZON_MONTHS)).dt.strftime("%Y-%m-%d")
    models = {"constante": [], "ubiquity": ["ubiquity", "is_ocg"],
              "ubiquity+bridge_score": ["ubiquity", "bridge_score", "is_ocg"],
              "ubiquity+fragmentation": ["ubiquity", "fragmentation", "is_ocg"],
              "bridge_score": ["bridge_score", "is_ocg"]}
    rows = []
    for lid, m in meta.iterrows():
        train_ids = meta.index[meta.known < m.as_of]
        if len(train_ids) < MIN_TRAIN_LISTS:
            continue
        train, test = d[d.list_id.isin(train_ids)], d[d.list_id == lid]
        for name, feats in models.items():
            pred = _ols(train, test, feats, target)
            rows.append({"list_id": lid, "as_of": m.as_of, "n_train_lists": len(train_ids), "modele": name,
                         "mse": float(np.mean((test[target].to_numpy() - pred) ** 2)), "cartes": len(test)})
    return pd.DataFrame(rows)


def mse_gain(wf: pd.DataFrame, a: str, b: str, rng) -> dict:
    p = wf.pivot(index="list_id", columns="modele", values="mse")
    diff = (p[a] - p[b]).to_numpy()
    idx = rng.integers(0, len(diff), size=(BOOT, len(diff)))
    lo, hi = np.percentile(diff[idx].mean(axis=1), [5, 95])
    wins = int((diff < 0).sum())
    ties = int((diff == 0).sum())
    pval = float(binomtest(wins, len(diff) - ties).pvalue) if len(diff) - ties else 1.0
    return {"a": a, "b": b, "listes": len(diff), "mse_a_moins_b": float(diff.mean()), "p05": float(lo),
            "p95": float(hi), "a_mieux": wins, "p_signe": pval, "gain": bool(hi < 0)}


def coefficients(hits: pd.DataFrame, rng, n_boot: int = 2000) -> pd.DataFrame:
    """Lecture complémentaire, ajoutée après lecture de Q3 : SIGNE des coefficients (critères standardisés).

    La règle de Q3 ne fixait pas le sens attendu. L'affirmation « Impact » en fixe un : à part des decks égale, une
    carte à fort score de pont ferait davantage baisser ses porteurs (coefficient négatif). Intervalle bootstrap par
    liste à 90 %, toutes les cartes touchées, variable de format.
    """
    d = hits.dropna(subset=["variation"]).assign(is_ocg=lambda x: (x.format == "OCG").astype(int))
    ids = d.list_id.unique()
    groups = {i: d[d.list_id == i] for i in ids}
    rows = []
    for target in ("variation", "variation_rel"):
        dd = d.dropna(subset=[target])
        for feats in (["ubiquity", "bridge_score"], ["ubiquity", "fragmentation"], ["ubiquity", "n_archetypes"]):
            def fit(x, feats=feats, target=target):
                mu, sd = x[feats].mean(), x[feats].std(ddof=0).replace(0, 1)
                X = np.column_stack([np.ones(len(x)), ((x[feats] - mu) / sd).to_numpy(), x.is_ocg.to_numpy()])
                return np.linalg.lstsq(X, x[target].to_numpy(), rcond=None)[0][1:1 + len(feats)]
            point = fit(dd)
            draws = []
            for _ in range(n_boot):
                pick = rng.choice(ids, size=len(ids), replace=True)
                sample = pd.concat([groups[i] for i in pick], ignore_index=True).dropna(subset=[target])
                draws.append(fit(sample))
            draws = np.array(draws)
            for j, f in enumerate(feats):
                rows.append({"cible": target, "modele": " + ".join(feats), "critere": f, "coef_standardise": point[j],
                             "p05": np.percentile(draws[:, j], 5), "p95": np.percentile(draws[:, j], 95),
                             "part_negative": float((draws[:, j] < 0).mean())})
    return pd.DataFrame(rows)


def simulator(hits: pd.DataFrame, rng) -> tuple[pd.DataFrame, dict]:
    """Q4 : archétypes voisins du simulateur contre la liste naïve de même taille."""
    h = hits.copy()
    h["n_listed"] = h.sim_listed.apply(len)
    h["n_matched"] = h.sim_matched.apply(len)
    stats = {"cartes_touchees": len(h), "noms_listes": int(h.n_listed.sum()),
             "noms_qui_sont_des_archetypes_de_deck": int(h.n_matched.sum()),
             "cartes_sans_aucun_nom_mesurable": int((h.n_matched == 0).sum())}
    d = h.dropna(subset=["sim_rel", "naive_rel"])
    rows = []
    for label, col_a, col_b in (("variation relative moyenne (critère)", "sim_rel", "naive_rel"),
                                ("variation moyenne (points)", "sim_delta", "naive_delta"),
                                ("part des archétypes en baisse", "sim_declined", "naive_declined")):
        est, lo, hi = boot_lists(d, lambda x: (x[col_a] - x[col_b]).mean(), rng)
        rows.append({"mesure": label, "simulateur_moy": d[col_a].mean(), "naive_moy": d[col_b].mean(),
                     "simulateur_moins_naive": est, "p05": lo, "p95": hi, "cartes": len(d),
                     "listes": d.list_id.nunique()})
    return pd.DataFrame(rows), stats


# --------------------------------------------------------------------------- sortie

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=Path("diagnostic_pont_simulateur"))
    args = parser.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")
    args.out.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    warnings.filterwarnings("ignore", category=FutureWarning)
    rng = np.random.default_rng(SEED)

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=60)
    data, lists = load(conn)
    print(f"Listes retenues par le backtest : {len(lists)} ; avec 3 mois suivants complets : {int(lists.complete.sum())}")
    print(lists.to_string(index=False))
    hits_all = data[data.y_hit == 1]
    print(f"\nCartes touchées classées sur ces listes : {len(hits_all)} ; avec au moins un archétype porteur : "
          f"{int((hits_all.n_porteurs > 0).sum())} ; nombre de porteurs, médiane {hits_all.n_porteurs.median():.0f}")
    keep = ["format", "effective", "card_name", "ubiquity", "n_archetypes", "bridge_score", "fragmentation",
            "n_porteurs", "share_before", "variation", "variation_rel", "sim_delta", "naive_delta"]
    hits_all[keep].to_csv(args.out / "cartes_touchees.csv", index=False)

    print("\n== Q1. Un ban fait-il baisser la part de ses archétypes porteurs ? (contrôle : même liste, même quintile) ==")
    eff, hits = ban_effect(data, rng)
    eff.to_csv(args.out / "effet_du_ban.csv", index=False)
    print(eff.round(3).to_string(index=False))
    eff_clean, _ = ban_effect(data, rng, clean=True)
    eff_clean.to_csv(args.out / "effet_du_ban_controles_propres.csv", index=False)
    print("Variante (relecture) : contrôles qui ne partagent aucun porteur avec une carte touchée de la liste")
    print(eff_clean.round(3).to_string(index=False))

    print("\n== Q2. Corrélation de rang avec la variation (cartes touchées ; négatif = va dans le sens « impact ») ==")
    cor = correlations(hits, rng)
    cor.to_csv(args.out / "correlations.csv", index=False)
    print(cor.round(3).to_string(index=False))

    print("\n== Q3. Prévision hors échantillon dans le temps (origine glissante) ==")
    wf = walk_forward(hits)
    wf.to_csv(args.out / "origine_glissante.csv", index=False)
    print(wf.pivot_table(index=["list_id", "n_train_lists"], columns="modele", values="mse").round(2).to_string())
    print(wf.groupby("modele").mse.mean().round(3).to_string())
    gains = pd.DataFrame([mse_gain(wf, a, b, rng) for a, b in (
        ("ubiquity+bridge_score", "ubiquity"), ("ubiquity+fragmentation", "ubiquity"),
        ("bridge_score", "ubiquity"), ("ubiquity", "constante"))])
    gains.to_csv(args.out / "gains.csv", index=False)
    print(gains.round(3).to_string(index=False))

    print("\n== Q3 bis (ajouté après lecture) : signe des coefficients, et variation relative ==")
    print("Corrélations de rang chez les cartes touchées : score de pont / nombre de porteurs "
          f"{spearmanr(hits.bridge_score, hits.n_porteurs).statistic:.3f} ; score de pont / part cumulée des porteurs "
          f"{spearmanr(hits.bridge_score, hits.share_before, nan_policy='omit').statistic:.3f} ; part des decks / part "
          f"cumulée des porteurs {spearmanr(hits.ubiquity, hits.share_before, nan_policy='omit').statistic:.3f}")
    co = coefficients(hits, rng)
    co.to_csv(args.out / "coefficients.csv", index=False)
    print(co.round(3).to_string(index=False))
    wf_rel = walk_forward(hits, "variation_rel")
    wf_rel.to_csv(args.out / "origine_glissante_relative.csv", index=False)
    print("Variation relative (variation / part cumulée des porteurs avant), erreur quadratique moyenne hors échantillon :")
    print(wf_rel.groupby("modele").mse.mean().round(4).to_string())
    print(pd.DataFrame([mse_gain(wf_rel, a, b, rng) for a, b in (
        ("ubiquity+bridge_score", "ubiquity"), ("ubiquity+fragmentation", "ubiquity"), ("ubiquity", "constante"))])
          .round(4).to_string(index=False))

    print("\n== Q4. Simulateur : archétypes voisins contre liste naïve de même taille ==")
    sim, stats = simulator(hits, rng)
    sim.to_csv(args.out / "simulateur.csv", index=False)
    print(stats)
    print(sim.round(3).to_string(index=False))

    print("\n== Verdict selon la règle figée ==")
    g_bs = gains[(gains.a == "ubiquity+bridge_score") & (gains.b == "ubiquity")].gain.iloc[0]
    g_fr = gains[(gains.a == "ubiquity+fragmentation") & (gains.b == "ubiquity")].gain.iloc[0]
    g_sim = bool(sim[sim.mesure.str.startswith("variation relative")].p95.iloc[0] < 0)
    print(f"score de pont : {'gain' if g_bs else 'aucun gain'} ; fragmentation : {'gain' if g_fr else 'aucun gain'} ; "
          f"archétypes voisins du simulateur : {'gain' if g_sim else 'aucun gain'}")
    sign = co[(co.cible == "variation") & (co.modele == "ubiquity + bridge_score") & (co.critere == "bridge_score")]
    print(f"Sens du score de pont à part des decks égale (Q3 bis) : coefficient {sign.coef_standardise.iloc[0]:+.2f} "
          f"[{sign.p05.iloc[0]:+.2f} ; {sign.p95.iloc[0]:+.2f}] ; l'affirmation « Impact » attend un coefficient négatif.")


if __name__ == "__main__":
    main()
