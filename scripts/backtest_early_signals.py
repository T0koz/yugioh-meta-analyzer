"""
TOK-129 (B2 de l'audit de rigueur) : backtest des signaux précoces contre « vues seules » et le hasard.

    python scripts/backtest_early_signals.py                    # analyse complète (≈ 1 min)
    python scripts/backtest_early_signals.py --verifier         # contrôle de reproduction (voir plus bas)
    python scripts/backtest_early_signals.py --db <chemin> --json <sortie.json>

Lecture seule : la base est ouverte en `mode=ro`, rien n'est écrit en base.

Définitions figées AVANT la première exécution sur les résultats (2026-11-18)
---------------------------------------------------------------------------
- **Classement rejoué** : celui de `scripts/build_early_signals.py` (lot 20, TOK-122), reconstruit à la date t
  avec les seules données antérieures à t : fenêtres de sortie TCG 168 j / OCG 380 j, carte sortie quelque part au
  plus tard à t, banlist TCG en vigueur à t (Forbidden et Limited exclues), cartes déjà en méta exclues (≥ 3 % des
  decks TCG légaux du ]t − 90 j ; t]), archétypes méta = 20 meilleurs `meta_scores` des mois entièrement écoulés
  depuis t − 200 j, force OCG recalculée à t (formule du notebook 10 sur les decks OCG légaux des 3 mois avant t).
  Mêmes poids : 0,35 vues + 0,35 texte + 0,30 force OCG.
- **Entrer en méta** : la carte est jouée (toutes zones) dans au moins 3 % des decks TCG légaux créés dans
  ]t ; t + 120 j]. 3 % est le seuil « déjà en méta » de `build_early_signals.py` (seuil T3 de la tier list) :
  une carte signalée « avant la méta » est réussie si elle franchit ce même seuil dans les 4 mois. Sensibilité
  déclarée d'avance : seuil 1 %.
- **Mesure** : precision@20 (part des 20 premières cartes qui entrent en méta). Égalités de score : espérance sous
  un départage au hasard (les cartes à égalité au rang 20 comptent au prorata). Univers de moins de 20 cartes :
  precision@N.
- **Bases naïves** : « vues seules » (classement par `views_week`) et le hasard (espérance = taux de base de
  l'univers). Rapportées à titre d'information, sans critère : « déjà un peu joué » (part des decks TCG des 90 j
  avant t, sous 3 %) et « force OCG seule ».
- **Origines** :
  1. *Origine propre* : t = 2026-06-13, date de l'instantané `data/raw/cards.json` (commit `cc9b27d` du 13/06).
     Les vues y sont contemporaines de t : aucune fuite par les vues. Cartes absentes de l'instantané exclues.
  2. *Origines glissantes* : le 1er de chaque mois de 2024-07 à 2026-07 (25 dates ; t + 120 j reste avant le
     dernier deck relevé). ⚠ Les vues sont celles du 13/06/2026 pour toutes les dates : pour t antérieur, elles
     viennent du futur (une carte devenue jouée est plus consultée). Cette fuite avantage « vues seules » plus
     que le score (poids effectifs moyens du score rejoué : vues 34 %, texte 32 %, force OCG 33 % ; le texte
     n'est pas nul aux dates passées, contrairement au calcul servi du lot 20). La force OCG contient aussi les
     vues (moyenne des cartes clés).
- **Critère (brief B2)** : sur les origines glissantes, écart moyen Δ = P@20(score) − P@20(vues seules) > 0 et
  intervalle bootstrap à 95 % par date (10 000 tirages des dates avec remise, graine 20261118) qui exclut 0.
  Sensibilité : bootstrap par blocs de 4 mois consécutifs (les fenêtres de 120 j se chevauchent).
  L'origine propre est un contrôle sans fuite (bootstrap sur les cartes, une seule date).
- **Liste réellement servie le 2026-06-17** (journal `prediction_log`, `early_card`, backfill) : precision@20 de
  la liste d'avant le lot 20, à titre de constat, sur ]2026-06-17 ; + 120 j].

Ajouté après la première exécution (relecture `data-scientist-ygo`, déclaré) : variantes sans vues, formule servie
sans texte, texte + force OCG ; précision par archétype (chaque archétype du top 20 compte pour 1), part des
archétypes du top 20 avec au moins une réussite, réussites plafonnées à 3 par archétype ; bootstrap par épisodes
(8 grappes de dates consécutives où le même archétype arrive, découpage posé après lecture des résultats) ;
autocorrélation des écarts et effectif efficace (formule AR(1)).

Contrôle `--verifier` : à la date du dernier deck, avec les vues de la base, le classement reconstruit doit
redonner `early_card_signals` (lot 20) et la force OCG recalculée doit redonner `ocg_archetype_scores`.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_early_signals import (  # noqa: E402  (mêmes constantes et fonctions que le classement servi)
    EXCLUDED_STATUS, META_DAYS, META_RECENT_DAYS, META_SHARE_MAX, META_TOP, OCG_DAYS, TCG_DAYS, TEXT_MIN, WEIGHTS,
    banlist_at, clean, deck_usage,
)

DB = ROOT / "data" / "yugioh.db"
SNAPSHOT = ROOT / "data" / "raw" / "cards.json"
SNAPSHOT_DATE = "2026-06-13"   # commit cc9b27d
PUBLISHED_DATE = "2026-06-17"  # liste journalisée (prediction_log, backfill)

HORIZON_DAYS = 120
TOP_K = 20
OUTCOME_SHARE = META_SHARE_MAX          # 3 %
OUTCOME_SHARE_SENS = 0.01               # sensibilité déclarée
ROLLING = [d.strftime("%Y-%m-%d") for d in pd.date_range("2024-07-01", "2026-07-01", freq="MS")]
SEED = 20261118
N_BOOT = 10_000
BLOCK = 4

# Notebook 10 (force OCG), mêmes réglages.
OCG_MONTHS = 3
STAPLE_MONTHS = 12
KEY_FREQ = 0.3
STAPLE_SHARE = 0.20
STAPLE_MIN_ARCH = 30
LEGAL_IDS = "(SELECT deck_id FROM deck_legality WHERE legal = 1)"


# ── Données à la date t ────────────────────────────────────────────────────────

def day(t: str, delta: int) -> str:
    return (pd.Timestamp(t) + pd.Timedelta(days=delta)).strftime("%Y-%m-%d")


def ocg_scores_at(conn: sqlite3.Connection, t: str, views: dict[str, float],
                  with_views: bool = True) -> dict[str, float]:
    """Force OCG par archétype à t (notebook 10, cellules 1 à 7), normalisée sur 0-1.
    `with_views=False` : part OCG pondérée par le classement seule (`meta_score_ocg`), sans les vues.
    `views` : vues par nom nettoyé. Decks bornés à t (le notebook n'a pas de borne haute : il tourne au dernier deck)."""
    ocg_from = (pd.Timestamp(t) - pd.DateOffset(months=OCG_MONTHS)).strftime("%Y-%m-%d")
    tcg_from = (pd.Timestamp(t) - pd.DateOffset(months=STAPLE_MONTHS)).strftime("%Y-%m-%d")
    upto = day(t, 1)  # created < t + 1 jour
    raw = pd.read_sql_query(
        f"""SELECT strftime('%Y-%m', created) AS month, archetype, COUNT(*) AS n_decks,
                   AVG(CASE WHEN placement IS NOT NULL THEN placement END) AS avg_placement
            FROM tournament_decks
            WHERE ocg = 1 AND archetype IS NOT NULL AND id IN {LEGAL_IDS} AND created >= ? AND created < ?
            GROUP BY month, archetype""",
        conn, params=(ocg_from, upto))
    if raw.empty:
        return {}
    agg = raw.groupby("archetype").agg(n_decks=("n_decks", "sum"), avg_placement=("avg_placement", "mean")).reset_index()
    agg["share"] = agg.n_decks / agg.n_decks.sum()
    ps = 1 / agg.avg_placement.replace(0, np.nan)
    agg["meta"] = np.sqrt(agg.share * (ps / ps.max()).fillna(agg.share))
    if not with_views:
        return (agg.set_index("archetype").meta / agg.meta.max()).to_dict()

    oc = pd.read_sql_query(
        f"""SELECT dc.deck_id, dc.card_name, td.archetype FROM deck_cards dc JOIN tournament_decks td ON td.id = dc.deck_id
            WHERE td.ocg = 1 AND td.archetype IS NOT NULL AND td.id IN {LEGAL_IDS}
              AND td.created >= ? AND td.created < ? AND dc.zone = 'main'""",
        conn, params=(ocg_from, upto))
    size = oc.groupby("archetype").deck_id.nunique().rename("n_arch")
    n_ocg = oc.deck_id.nunique()
    freq = oc.groupby(["archetype", "card_name"]).deck_id.nunique().reset_index(name="n").join(size, on="archetype")
    key = freq[freq.n / freq.n_arch >= KEY_FREQ].copy()

    n_tcg = conn.execute(
        f"SELECT COUNT(*) FROM tournament_decks WHERE ocg = 0 AND id IN {LEGAL_IDS} AND created >= ? AND created < ?",
        (tcg_from, upto)).fetchone()[0]
    staples = {r[0] for r in conn.execute(
        f"""SELECT dc.card_name FROM deck_cards dc JOIN tournament_decks td ON td.id = dc.deck_id
            WHERE td.ocg = 0 AND td.id IN {LEGAL_IDS} AND td.created >= ? AND td.created < ?
            GROUP BY dc.card_name
            HAVING COUNT(DISTINCT dc.deck_id) * 1.0 / ? > ? AND COUNT(DISTINCT td.archetype) >= ?""",
        (tcg_from, upto, max(n_tcg, 1), STAPLE_SHARE, STAPLE_MIN_ARCH))}
    occ = oc.groupby("card_name").agg(n=("deck_id", "nunique"), a=("archetype", "nunique"))
    staples |= set(occ[(occ.n / max(n_ocg, 1) > STAPLE_SHARE) & (occ.a >= STAPLE_MIN_ARCH)].index)
    status = banlist_at(conn, t)
    staples |= set(status[status == "Forbidden"].index)

    key = key[~key.card_name.isin(staples)].copy()
    key["views"] = key.card_name.map(views)
    avg = key.groupby("archetype").views.mean()
    agg["avg_views"] = agg.archetype.map(avg).fillna(0)
    agg["score"] = agg.meta * np.log1p(agg.avg_views)
    mx = agg.score.max()
    return (agg.set_index("archetype").score / mx).to_dict() if mx > 0 else {}


def rank_at(conn: sqlite3.Connection, cards: pd.DataFrame, t: str, text: pd.DataFrame,
            strict: bool = True) -> tuple[pd.DataFrame, dict]:
    """Classement des signaux précoces à t. `cards` : id, name, archetype, tcg_date, ocg_date, views_week
    (vues de la source choisie). Reprend `build_early_signals.build`, borné à t.
    `strict=False` reproduit exactement le script du lot 20 (contrôle `--verifier`) : il garde les cartes pas
    encore sorties à t (date OCG annoncée) et le mois de t, en partie postérieur, dans les archétypes méta."""
    tcg_from, ocg_from = day(t, -TCG_DAYS), day(t, -OCG_DAYS)
    c = cards[
        ((cards.tcg_date >= tcg_from) | (cards.ocg_date >= ocg_from))
        & (cards.tcg_date.isna() | (cards.tcg_date >= tcg_from))
        & (((cards.tcg_date <= t) | (cards.ocg_date <= t)) | (not strict))  # sortie au plus tard à t
        & cards.views_week.notna()
    ]
    c = c.sort_values("views_week", ascending=False).drop_duplicates("name").copy()
    c["card"] = c.name.map(clean)

    status = banlist_at(conn, t)
    c["ban_status"] = c.card.map(status.get)
    n_ban = int(c.ban_status.isin(EXCLUDED_STATUS).sum())
    c = c[~c.ban_status.isin(EXCLUDED_STATUS)]

    n_recent, usage = deck_usage(conn, day(t, -META_RECENT_DAYS), t)
    c["recent_share"] = c.card.map(lambda n: usage.get(n, 0) / n_recent if n_recent else 0.0)
    n_meta = int((c.recent_share >= META_SHARE_MAX).sum())
    c = c[c.recent_share < META_SHARE_MAX].copy()

    vlog = np.log1p(c.views_week.fillna(0))
    c["signal_views"] = vlog / vlog.max() if vlog.max() > 0 else 0.0

    # Mois entièrement écoulés avant t (le mois de t contient des decks postérieurs). La comparaison de
    # `month` ('AAAA-MM') à 'AAAA-MM-01' est celle du script servi : elle écarte le mois de `meta_from` lui-même.
    meta_from = (pd.Timestamp(t) - pd.Timedelta(days=META_DAYS)).strftime("%Y-%m-01")
    meta_archs = [r[0] for r in conn.execute(
        "SELECT archetype FROM meta_scores WHERE month >= ? AND month < ? "
        "GROUP BY archetype ORDER BY AVG(meta_score) DESC LIMIT ?",
        (meta_from, t[:7] if strict else "9999-99", META_TOP))]
    meta_set = set(cards.loc[cards.archetype.isin(meta_archs), "name"])
    new_set = set(c.name)
    ts = text[(text.card_a.isin(new_set) & text.card_b.isin(meta_set)) | (text.card_b.isin(new_set) & text.card_a.isin(meta_set))]
    if len(ts):
        new = np.where(ts.card_a.isin(new_set), ts.card_a, ts.card_b)
        top3 = ts.assign(new=new).groupby("new").text_synergy_score.apply(lambda x: x.nlargest(3).mean())
        c["signal_text"] = c.name.map(top3 / top3.max()).fillna(0.0)
    else:
        c["signal_text"] = 0.0

    views_clean = cards.assign(card=cards.name.map(clean)).drop_duplicates("card").set_index("card").views_week.to_dict()
    ocg = ocg_scores_at(conn, t, views_clean)
    c["signal_ocg"] = c.archetype.map(ocg).fillna(0.0)
    # Variantes sans aucune vue (ajoutées après la première exécution, pour isoler la fuite des vues).
    c["signal_ocg_pure"] = c.archetype.map(ocg_scores_at(conn, t, {}, with_views=False)).fillna(0.0)
    c["score_sans_vues"] = WEIGHTS["text"] * c.signal_text + WEIGHTS["ocg"] * c.signal_ocg_pure
    c["servi_sans_texte"] = WEIGHTS["views"] * c.signal_views + WEIGHTS["ocg"] * c.signal_ocg  # texte = 0, comme au lot 20
    c["vues_force_ocg_pure"] = WEIGHTS["views"] * c.signal_views + WEIGHTS["ocg"] * c.signal_ocg_pure
    c["early_score"] = WEIGHTS["views"] * c.signal_views + WEIGHTS["text"] * c.signal_text + WEIGHTS["ocg"] * c.signal_ocg
    c = c.sort_values(["early_score", "card"], ascending=[False, True]).reset_index(drop=True)
    info = {"n_ban": n_ban, "n_in_meta": n_meta, "n_recent_decks": n_recent, "n_meta_archs": len(meta_archs),
            "n_text_positive": int((c.signal_text > 0).sum())}
    return c, info


def outcome(conn: sqlite3.Connection, t: str, horizon: int = HORIZON_DAYS) -> tuple[int, dict]:
    """(decks TCG légaux de ]t ; t + horizon], part des decks qui jouent chaque carte)."""
    n, usage = deck_usage(conn, day(t, 1), day(t, horizon))
    return n, {k: v / n for k, v in usage.items()} if n else {}


# ── Mesures ────────────────────────────────────────────────────────────────────

def precision_at_k(score: np.ndarray, y: np.ndarray, k: int = TOP_K) -> float:
    """Precision@k, égalités départagées en espérance (prorata dans le groupe à cheval sur le rang k)."""
    n = len(score)
    if n == 0:
        return float("nan")
    k = min(k, n)
    order = np.argsort(-score, kind="stable")
    s, yy = score[order], y[order]
    cut = s[k - 1]
    above = s > cut
    tie = s == cut
    hits = yy[above].sum() + (k - above.sum()) * yy[tie].mean()
    return float(hits / k)


def boot_dates(d: np.ndarray, rng: np.random.Generator, block: int = 1) -> tuple[float, float]:
    n = len(d)
    if block <= 1:
        idx = rng.integers(0, n, size=(N_BOOT, n))
        means = d[idx].mean(axis=1)
    else:  # blocs mobiles de dates consécutives
        nb = int(np.ceil(n / block))
        starts = rng.integers(0, n - block + 1, size=(N_BOOT, nb))
        idx = (starts[:, :, None] + np.arange(block)).reshape(N_BOOT, -1)[:, :n]
        means = d[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def boot_cards(df: pd.DataFrame, cols: tuple[str, str], rng: np.random.Generator) -> tuple[float, float]:
    """Une seule date : rééchantillonne les cartes de l'univers, recalcule les deux top 20."""
    a, b, y = (df[cols[0]].to_numpy(float), df[cols[1]].to_numpy(float), df.y.to_numpy(float))
    n = len(df)
    out = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        out[i] = precision_at_k(a[idx], y[idx]) - precision_at_k(b[idx], y[idx])
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


METHODS = {
    "score": "early_score",
    "vues": "views_week",
    "deja_joue": "recent_share",
    "force_ocg": "signal_ocg",
    "force_ocg_sans_vues": "signal_ocg_pure",   # ajoutée après la première exécution (fuite)
    "score_sans_vues": "score_sans_vues",       # idem
    "servi_sans_texte": "servi_sans_texte",     # idem (relecture) : la formule effectivement servie au lot 20
    "vues_force_ocg_pure": "vues_force_ocg_pure",  # idem
}
# Épisodes : dates consécutives où le même archétype arrive en TCG (posé après lecture, relecture data scientist).
EPISODES = {"2024-07": 1, "2024-08": 1, "2024-09": 2, "2024-10": 2, "2024-11": 2, "2024-12": 2, "2025-01": 3,
            "2025-02": 3, "2025-03": 3, "2025-04": 3, "2025-05": 4, "2025-06": 4, "2025-07": 4, "2025-08": 4,
            "2025-09": 5, "2025-10": 5, "2025-11": 5, "2025-12": 6, "2026-01": 6, "2026-02": 6, "2026-03": 7,
            "2026-04": 7, "2026-05": 7, "2026-06": 8, "2026-07": 8}
ROBUST_PAIRS = [("score", "vues"), ("score", "force_ocg_sans_vues"), ("force_ocg_sans_vues", "vues"),
                ("score_sans_vues", "force_ocg_sans_vues"), ("score", "vues_force_ocg_pure"),
                ("vues_force_ocg_pure", "force_ocg_sans_vues"), ("servi_sans_texte", "force_ocg_sans_vues")]
OTHERS = ["vues", "hasard", "deja_joue", "force_ocg", "force_ocg_sans_vues", "score_sans_vues"]


def top_weighted(r: pd.DataFrame, col: str, k: int = TOP_K) -> pd.DataFrame:
    """Top k avec poids d'égalité (prorata au rang k), comme `precision_at_k`."""
    s = r[col].to_numpy(float)
    k = min(k, len(s))
    cut = np.sort(s)[::-1][k - 1]
    above, tie = r[s > cut], r[s == cut]
    return pd.concat([above.assign(w=1.0), tie.assign(w=(k - len(above)) / len(tie))])


def archetype_metrics(r: pd.DataFrame, col: str) -> dict:
    """Précision par archétype, part d'archétypes avec une réussite, réussites plafonnées à 3 par archétype."""
    tw = top_weighted(r.assign(arch=r.archetype.fillna("~" + r.card)), col)
    g = tw.assign(h=tw.w * tw.y).groupby("arch")
    return {"arch": float((g.h.sum() / g.w.sum()).mean()), "anyhit": float(g.y.max().mean()),
            "cap3": float(g.h.sum().clip(upper=3).sum() / tw.w.sum())}


def evaluate(conn, cards, t, text, threshold=OUTCOME_SHARE) -> tuple[dict, pd.DataFrame]:
    ranked, info = rank_at(conn, cards, t, text)
    n_out, share = outcome(conn, t)
    ranked["share_after"] = ranked.card.map(share).fillna(0.0)
    ranked["y"] = (ranked.share_after >= threshold).astype(int)
    row = {"t": t, "N": len(ranked), "K": int(ranked.y.sum()), "n_decks_after": n_out, **info}
    row["hasard"] = row["K"] / row["N"] if row["N"] else float("nan")
    for m, col in METHODS.items():
        row[m] = precision_at_k(ranked[col].to_numpy(float), ranked.y.to_numpy(float))
        for suf, v in archetype_metrics(ranked, col).items():
            row[f"{m}_{suf}"] = v
    return row, ranked


def boot_clusters(d: np.ndarray, groups: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    """Bootstrap par grappes (épisodes) : on tire des épisodes avec remise, on garde toutes leurs dates."""
    keys = np.unique(groups)
    parts = {k: d[groups == k] for k in keys}
    means = [np.concatenate([parts[k] for k in rng.choice(keys, len(keys))]).mean() for _ in range(N_BOOT)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def robustness(df: pd.DataFrame, rng: np.random.Generator) -> dict:
    ep = df.t.str[:7].map(EPISODES).to_numpy()
    out = {}
    print("  Robustesse (relecture data scientist) : moyenne, IC dates, IC épisodes (8 grappes), épisodes devant/derrière")
    for a, b in ROBUST_PAIRS:
        for suf, lab in (("", "cartes"), ("_arch", "par archétype"), ("_anyhit", "archétypes touchés"), ("_cap3", "plafond 3")):
            d = (df[a + suf] - df[b + suf]).to_numpy()
            e = pd.Series(d).groupby(ep).mean()
            ci_d, ci_e = boot_dates(d, rng), boot_clusters(d, ep, rng)
            dm = d - d.mean()
            r1 = float(np.sum(dm[1:] * dm[:-1]) / np.sum(dm * dm)) if np.sum(dm * dm) else 0.0
            n_eff = len(d) * (1 - r1) / (1 + r1)
            out[f"{a}-{b}{suf}"] = {"moyenne": float(d.mean()), "ic_dates": ci_d, "ic_episodes": ci_e,
                                     "episodes_devant": int((e > 0).sum()), "episodes_derriere": int((e < 0).sum()),
                                     "acf1": r1, "n_efficace": n_eff}
            print(f"    {a} − {b} [{lab}] : {d.mean():+.3f}  [{ci_d[0]:+.3f} ; {ci_d[1]:+.3f}]  "
                  f"[{ci_e[0]:+.3f} ; {ci_e[1]:+.3f}]  {int((e > 0).sum())}/{int((e < 0).sum())}"
                  + (f"  (ACF1 {r1:+.2f}, n efficace {n_eff:.1f})" if suf == "" else ""))
    return out


# ── Programme ──────────────────────────────────────────────────────────────────

def load_cards(conn, snapshot: Path | None) -> pd.DataFrame:
    cards = pd.read_sql_query("SELECT id, name, archetype, tcg_date, ocg_date, views_week FROM cards", conn)
    if snapshot is None:
        return cards
    snap = json.loads(snapshot.read_text())
    views = {c["id"]: (c.get("misc_info") or [{}])[0].get("viewsweek") for c in snap}
    cards = cards[cards.id.isin(views)].copy()  # cartes connues au 13/06 seulement
    cards["views_week"] = cards.id.map(views)
    return cards


def verify(conn) -> None:
    """Reproduction du classement servi (lot 20) et de la force OCG (notebook 10) à la date du dernier deck."""
    cards = load_cards(conn, None)
    text = pd.read_sql_query("SELECT card_a, card_b, text_synergy_score FROM text_synergies WHERE text_synergy_score >= ?",
                             conn, params=(TEXT_MIN,))
    served = pd.read_sql_query("SELECT card_name, early_score, as_of FROM early_card_signals ORDER BY early_score DESC, card_name", conn)
    as_of = served.as_of.iloc[0]
    ranked, _ = rank_at(conn, cards, as_of, text, strict=False)
    ocg_ref = pd.read_sql_query("SELECT archetype, ocg_score, computed_at FROM ocg_archetype_scores", conn)
    ref_day = conn.execute("SELECT MAX(substr(created,1,10)) FROM tournament_decks").fetchone()[0]
    views_clean = cards.assign(card=cards.name.map(clean)).drop_duplicates("card").set_index("card").views_week.to_dict()
    ocg = pd.Series(ocg_scores_at(conn, ref_day, views_clean)) * 100
    m = ocg_ref.set_index("archetype").ocg_score
    common = m.index.intersection(ocg.index)
    print(f"Force OCG au {ref_day} : {len(common)} archétypes communs sur {len(m)} servis / {len(ocg)} recalculés ; "
          f"écart absolu max {np.abs(m[common] - ocg[common].round(1)).max():.2f} point sur 100 ; "
          f"Spearman {m[common].rank().corr(ocg[common].rank()):.4f}")
    top_s = served.card_name.head(50).tolist()
    top_r = ranked.card.head(50).tolist()
    diff = (served.set_index("card_name").early_score - ranked.set_index("card").early_score).abs()
    print(f"Classement au {as_of} : {len(served)} cartes servies, {len(ranked)} reconstruites ; "
          f"top 20 mêmes cartes : {set(top_s[:20]) == set(top_r[:20])} (même ordre : {top_s[:20] == top_r[:20]}) ; "
          f"top 50 commun : {len(set(top_s) & set(top_r))}/50 ; écart max de early_score : {diff.max():.5f} "
          f"(le script servi arrondit chaque signal à 4 décimales)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--json", help="Écrit les résultats détaillés dans ce fichier")
    ap.add_argument("--verifier", action="store_true", help="Contrôle de reproduction seulement")
    a = ap.parse_args()

    conn = sqlite3.connect(f"file:{os.path.abspath(a.db)}?mode=ro", uri=True, timeout=60)
    if a.verifier:
        verify(conn)
        return

    rng = np.random.default_rng(SEED)
    cards = load_cards(conn, Path(a.snapshot))
    text = pd.read_sql_query("SELECT card_a, card_b, text_synergy_score FROM text_synergies WHERE text_synergy_score >= ?",
                             conn, params=(TEXT_MIN,))
    last = conn.execute("SELECT MAX(substr(created,1,10)) FROM tournament_decks WHERE ocg = 0").fetchone()[0]
    assert day(ROLLING[-1], HORIZON_DAYS) <= last, "horizon non observé pour la dernière origine"
    res: dict = {"params": {"horizon_days": HORIZON_DAYS, "top_k": TOP_K, "outcome_share": OUTCOME_SHARE,
                            "seed": SEED, "n_boot": N_BOOT, "snapshot_date": SNAPSHOT_DATE, "last_tcg_deck": last}}

    # 1. Origine propre
    print(f"=== Origine propre t = {SNAPSHOT_DATE} (vues de l'instantané du même jour) ===")
    clean_res = {}
    for thr in (OUTCOME_SHARE, OUTCOME_SHARE_SENS):
        row, ranked = evaluate(conn, cards, SNAPSHOT_DATE, text, thr)
        ci_v = boot_cards(ranked, ("early_score", "views_week"), rng)
        ci_h = None
        print(f"seuil {thr:.0%} : N = {row['N']}, entrées K = {row['K']} (hasard {row['hasard']:.3f}), "
              f"decks après = {row['n_decks_after']}")
        print("  P@20 " + " | ".join(f"{m} {row[m]:.3f}" for m in METHODS))
        print(f"  Δ score − vues = {row['score'] - row['vues']:+.3f}, IC 95 % (bootstrap cartes) [{ci_v[0]:+.3f} ; {ci_v[1]:+.3f}]")
        top = ranked.head(TOP_K)[["card", "archetype", "views_week", "early_score", "share_after", "y"]]
        topv = ranked.sort_values(["views_week", "card"], ascending=[False, True]).head(TOP_K)[["card", "views_week", "share_after", "y"]]
        if thr == OUTCOME_SHARE:
            print("  Top 20 du score :")
            print(top.to_string(index=False))
            print("  Top 20 des vues :")
            print(topv.to_string(index=False))
            print("  Cartes entrées en méta (univers) :")
            print(ranked[ranked.y == 1][["card", "archetype", "views_week", "early_score", "share_after"]].assign(
                rang_score=ranked.index[ranked.y == 1] + 1).to_string(index=False))
        clean_res[f"{thr}"] = {**row, "ci_score_vues_cartes": ci_v,
                               "top_score": top.to_dict("records"), "top_vues": topv.to_dict("records")}
    res["origine_propre"] = clean_res

    # 2. Origines glissantes
    print(f"\n=== Origines glissantes ({len(ROLLING)} dates, vues du {SNAPSHOT_DATE} : fuite déclarée) ===")
    for thr in (OUTCOME_SHARE, OUTCOME_SHARE_SENS):
        rows = [evaluate(conn, cards, t, text, thr)[0] for t in ROLLING]
        df = pd.DataFrame(rows)
        base_cols = ["t", "N", "K", "n_decks_after", "n_ban", "n_in_meta", "n_recent_decks", "n_meta_archs",
                     "n_text_positive", "hasard", *METHODS]
        if thr == OUTCOME_SHARE:
            print(df[["t", "N", "K", "hasard", *METHODS, "n_text_positive"]]
                  .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        summ = {"seuil": thr, "par_date": df[base_cols].to_dict("records")}
        for other in OTHERS:
            d = (df.score - df[other]).to_numpy()
            summ[f"delta_{other}"] = {
                "moyenne": float(d.mean()), "ic_dates": boot_dates(d, rng), "ic_blocs": boot_dates(d, rng, BLOCK),
                "score_devant": int((d > 0).sum()), "egalites": int((d == 0).sum()), "derriere": int((d < 0).sum()),
            }
        means = {m: float(df[m].mean()) for m in ["score", *OTHERS]}
        summ["moyennes"] = means
        print(f"seuil {thr:.0%} : moyennes P@20 " + ", ".join(f"{k} {v:.3f}" for k, v in means.items()))
        for other in OTHERS:
            s = summ[f"delta_{other}"]
            print(f"  Δ score − {other:19s} = {s['moyenne']:+.3f}  IC dates [{s['ic_dates'][0]:+.3f} ; {s['ic_dates'][1]:+.3f}]"
                  f"  IC blocs [{s['ic_blocs'][0]:+.3f} ; {s['ic_blocs'][1]:+.3f}]"
                  f"  devant/égal/derrière {s['score_devant']}/{s['egalites']}/{s['derriere']}")
        if thr == OUTCOME_SHARE:
            summ["robustesse"] = robustness(df, rng)
        res[f"glissantes_{thr}"] = summ
    s = res[f"glissantes_{OUTCOME_SHARE}"]["delta_vues"]
    met = s["moyenne"] > 0 and s["ic_dates"][0] > 0
    print(f"\nCritère B2 (Δ score − vues > 0, IC par date qui exclut 0) : {'REMPLI' if met else 'NON REMPLI'}")
    res["critere_rempli"] = met

    # 3. Liste réellement servie le 17/06
    pub = pd.read_sql_query(
        "SELECT subject AS card, predicted_value AS score100, baseline_value AS views FROM prediction_log "
        "WHERE kind = 'early_card' AND provenance = 'backfill' AND made_at = ?", conn, params=(PUBLISHED_DATE,))
    if len(pub):
        n_out, share = outcome(conn, PUBLISHED_DATE)
        n_prev, usage_prev = deck_usage(conn, day(PUBLISHED_DATE, -META_RECENT_DAYS), PUBLISHED_DATE)
        pub["card"] = pub.card.map(clean)
        pub["share_after"] = pub.card.map(share).fillna(0.0)
        pub["share_before"] = pub.card.map(lambda n: usage_prev.get(n, 0) / n_prev)
        pub["y"] = (pub.share_after >= OUTCOME_SHARE).astype(int)
        pub["y_new"] = ((pub.share_after >= OUTCOME_SHARE) & (pub.share_before < OUTCOME_SHARE)).astype(int)
        r = {"N": len(pub)}
        for lab, col in (("score", "score100"), ("vues", "views")):
            r[f"{lab}_p20"] = precision_at_k(pub[col].to_numpy(float), pub.y.to_numpy(float))
            r[f"{lab}_p20_nouvelles"] = precision_at_k(pub[col].to_numpy(float), pub.y_new.to_numpy(float))
        r["deja_en_meta_top20"] = int((pub.sort_values("score100", ascending=False).head(TOP_K).share_before >= OUTCOME_SHARE).sum())
        r["hasard"] = float(pub.y.mean())
        r["hasard_nouvelles"] = float(pub.y_new.mean())
        print(f"\n=== Liste servie le {PUBLISHED_DATE} (avant le lot 20), {len(pub)} cartes ===")
        print(f"  P@20 score {r['score_p20']:.3f} (vues seules {r['vues_p20']:.3f}, hasard {r['hasard']:.3f}) ; "
              f"nouvelles entrées seulement : score {r['score_p20_nouvelles']:.3f}, vues {r['vues_p20_nouvelles']:.3f}, "
              f"hasard {r['hasard_nouvelles']:.3f} ; top 20 déjà en méta au 17/06 : {r['deja_en_meta_top20']}")
        res["liste_servie_0617"] = r

    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
        print(f"\nRésultats écrits dans {a.json}")


if __name__ == "__main__":
    main()
