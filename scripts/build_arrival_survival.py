"""Fenêtre d'arrivée en TCG par analyse de survie, par archétype (TOK-130, ticket B1 de l'audit).

    python scripts/build_arrival_survival.py                 # analyse + validation, lecture seule
    python scripts/build_arrival_survival.py --db COPIE.db --write   # écrit 2 tables NOUVELLES sur COPIE.db
    python scripts/build_arrival_survival.py --write --reference     # base de référence (orchestrateur, après sauvegarde)

Lecture seule par défaut (`mode=ro` sur `data/yugioh.db` du dépôt principal, retrouvé depuis un worktree). `--write` crée ou remplace uniquement
`tcg_arrival_survival` et `tcg_arrival_km` (tables propres à ce script), en une transaction ; il refuse
d'écrire si l'une de ces tables existe déjà avec un autre schéma. Rien de ce que le site affiche ne change :
le notebook 10 garde sa fenêtre 75-202 jours tant que Thomas n'a pas validé le formulaire.

Définitions (fixées après lecture des délais bruts, AVANT la première validation glissante)
-----------------------------------------------------------------------------------------
- Origine de prévision t : le 1er de chaque mois. Population à t = règle du notebook 10 rejouée avec les seules
  données antérieures à t : decks OCG légaux de [t - 3 mois, t), archétype >= 5 decks, cartes clés (main, >= 30 %
  des decks de l'archétype), staples OCG exclues (> 20 % des decks ET >= 30 archétypes), carte « inédite » si
  jamais vue dans un deck TCG avant t et `tcg_date` > t ; archétype retenu si >= 3 cartes clés inédites.
  (Les filtres « staples TCG » et « interdites TCG » du notebook ne retirent que des cartes déjà sorties en TCG :
  ils ne changent pas le compte des inédites, on les omet.)
- Unité : composante d'archétypes. Deux libellés dont les cartes inédites se recouvrent à >= 50 % (du plus petit
  ensemble) sont fusionnés (K9 / Vanquish Soul K9 / Crystron K9...) : sinon le même événement compte plusieurs fois.
- Ancre (origine du temps) : médiane, sur les cartes inédites de l'unité, de leur premier deck OCG (même ancre que
  le notebook 10). Burn-in : ancre >= 2024-03-01, les données OCG commencent en janvier 2024 (ancres antérieures
  tronquées à gauche).
- Événement « arrivée » : la moitié (arrondie au-dessus) des cartes inédites de l'unité est sortie en TCG
  (sortie d'une carte = `cards.tcg_date` si elle est passée, sinon premier deck TCG). Critère sur les cartes, pas
  sur le nom : 9 libellés sur 62 étaient déjà joués en TCG sous ce nom avant l'ancre (Branded, Mitsurugi...).
  L'arrivée « >= 5 decks TCG dont le nom contient l'archétype » (validateur) est donnée en sensibilité.
- Censure : pas d'arrivée à la date d'observation. Entrée différée : une unité n'est à risque qu'à partir de son
  âge à la première rétention (celles arrivées avant d'être retenues ne sont jamais dans la population).
- Kaplan-Meier à entrée différée, écrit à la main. Fenêtre annoncée pour une unité d'âge u : quantiles 10 % et
  90 % de la loi conditionnelle P(T <= x | T > u) = 1 - S(x)/S(u) ; bornes au milieu des paliers de la courbe ;
  couverture annoncée = probabilité KM de la fenêtre (>= 80 %, exacte à cause des marches). Si la loi
  conditionnelle n'atteint pas 90 % dans le support observé (fraction « jamais » ou suivi trop court), pas de
  fenêtre : on annonce seulement P(arrivée dans les 183 jours).
- Validation à origine glissante : à chaque origine, KM estimée avec les seules unités déjà retenues, censurées à
  t. Prévision évaluée si sa fin de fenêtre est <= dernière date de la base (suivi complet, quel que soit le
  résultat : on n'écarte jamais une prévision parce qu'elle n'a pas encore réussi). Une arrivée hors fenêtre, ou
  pas d'arrivée à la fin de la fenêtre, est un échec.
- Règle de décision (fixée avant exécution) : population principale = chaque unité à sa PREMIÈRE rétention, origine
  dans 2024-2025 ; critère atteint si |couverture observée - couverture annoncée moyenne| <= 5 points. Incertitude :
  bootstrap par cohorte (mois de l'ancre ; les archétypes d'un même set OCG arrivent ensemble en TCG), 2 000 tirages,
  graine 20261118 ; Wilson à 95 % donné à titre indicatif (il suppose les unités indépendantes).
- Méthodes naïves : (a) fenêtre actuelle 75-202 jours (P10-P90 par carte, estimée sur 2022-2025, donc en
  partie dans l'échantillon) ; (a') même méthode recalculée à chaque origine sur les cartes connues à t ;
  (b) P10-P90 empiriques des délais des seules unités déjà arrivées à t (survivants, sans censure ni âge).
"""
from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main_checkout() -> Path:
    """Dépôt principal (un worktree n'a pas de base) : même méthode que scripts/check.py."""
    try:
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
        return Path(common).parent
    except (OSError, subprocess.CalledProcessError):
        return ROOT


MAIN_DB = main_checkout() / "data" / "yugioh.db"

OCG_WINDOW_MONTHS = 3      # notebook 10, FENETRE_OCG_MOIS
MIN_OCG_DECKS = 5          # notebook 10, MIN_OCG_DECKS
MIN_UNRELEASED = 3         # notebook 10, MIN_CARTES_INEDITES
KEY_FREQ = 0.3             # notebook 10, FREQ_CARTE_CLE
OCG_STAPLE_SHARE, OCG_STAPLE_ARCH = 0.20, 30
MERGE_OVERLAP = 0.5
ARRIVAL_FRAC = 0.5
BURN_IN = pd.Timestamp("2024-03-01")
LEVEL = 0.80
HORIZON_DAYS = 183
MIN_EVENTS = 8             # sous 8 arrivées connues, ni KM ni quantiles empiriques ne sont estimés
FIXED_P10, FIXED_P90 = 75, 202
EVAL_START, EVAL_END = pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-01")
N_BOOT, SEED = 2000, 20261118
METHOD = (f"km-entree-differee-v1 (arrivée = {ARRIVAL_FRAC:.0%} des cartes inédites sorties en TCG ; "
          f"ancre = médiane du 1er deck OCG ; burn-in {BURN_IN.date()})")


# ---------------------------------------------------------------- chargement

def load(con):
    decks = pd.read_sql("""SELECT td.id, td.archetype, td.ocg, substr(td.created, 1, 10) AS d, dl.legal
                           FROM tournament_decks td LEFT JOIN deck_legality dl ON dl.deck_id = td.id""", con)
    decks["d"] = pd.to_datetime(decks.d)
    ref = decks.d.max()
    dc = pd.read_sql("SELECT deck_id AS id, card_name, zone FROM deck_cards", con)
    m = dc.merge(decks[["id", "ocg", "d", "archetype", "legal"]], on="id")
    cards = pd.read_sql("SELECT REPLACE(REPLACE(name,'<',''),'>','') AS card_name, tcg_date, ocg_date FROM cards",
                        con).drop_duplicates("card_name").set_index("card_name")
    cards["tcg_date"] = pd.to_datetime(cards.tcg_date, errors="coerce")
    cards["ocg_date"] = pd.to_datetime(cards.ocg_date, errors="coerce")
    c = cards.join(m[m.ocg == 0].groupby("card_name").d.min().rename("first_tcg"), how="outer")
    c = c.join(m[m.ocg == 1].groupby("card_name").d.min().rename("first_ocg"), how="outer")
    # sortie TCG datée : tcg_date officielle si passée, sinon premier deck TCG ; jamais une date future
    c["release"] = c.tcg_date.where(c.tcg_date <= ref).fillna(c.first_tcg.where(c.first_tcg <= ref))
    ocgm = m[(m.ocg == 1) & (m.zone == "main") & (m.legal == 1) & m.archetype.notna()]
    od = decks[(decks.ocg == 1) & (decks.legal == 1) & decks.archetype.notna()]
    tcg_names = decks[(decks.ocg == 0) & decks.archetype.notna()][["archetype", "d"]]
    return ref, c, ocgm, od, cards, tcg_names


def retained_at(t, c, ocgm, od):
    """Règle du notebook 10 rejouée à l'origine t (données de [t - 3 mois, t) seulement)."""
    lo = t - pd.DateOffset(months=OCG_WINDOW_MONTHS)
    w = ocgm[(ocgm.d >= lo) & (ocgm.d < t)]
    wd = od[(od.d >= lo) & (od.d < t)]
    if wd.empty:
        return {}
    size = wd.groupby("archetype").id.nunique()
    occ = w.groupby("card_name").agg(n=("id", "nunique"), a=("archetype", "nunique"))
    staple = set(occ[(occ.n / wd.id.nunique() > OCG_STAPLE_SHARE) & (occ.a >= OCG_STAPLE_ARCH)].index)
    f = w.groupby(["archetype", "card_name"]).id.nunique().reset_index(name="k").join(size.rename("n"), on="archetype")
    f = f[(f.k / f.n >= KEY_FREQ) & (f.n >= MIN_OCG_DECKS) & ~f.card_name.isin(staple)]
    f = f.join(c[["first_tcg", "tcg_date"]], on="card_name")
    f = f[~((f.first_tcg < t) | (f.tcg_date <= t))]
    return {a: set(g.card_name) for a, g in f.groupby("archetype") if len(g) >= MIN_UNRELEASED}


def build_panel(origins, c, ocgm, od):
    """Panel (origine, libellé, cartes inédites) puis composantes fusionnées par recouvrement des cartes."""
    rows = [(t, a, U) for t in origins for a, U in retained_at(t, c, ocgm, od).items()]
    P = pd.DataFrame(rows, columns=["t", "label", "U"])
    first = P.sort_values("t").groupby("label").U.first()
    labels = list(first.index)
    parent = {a: a for a in labels}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if len(first[a] & first[b]) / min(len(first[a]), len(first[b])) >= MERGE_OVERLAP:
                parent[find(a)] = find(b)
    P["comp"] = P.label.map(find)
    return P


def arrival(U, c, frac=ARRIVAL_FRAC):
    r = c.loc[sorted(U), "release"].dropna().sort_values()
    k = max(1, int(np.ceil(frac * len(U))))
    return r.iloc[k - 1] if len(r) >= k else pd.NaT


def anchor_of(U, c):
    return c.loc[sorted(U), "first_ocg"].median().normalize()


def unit_panel(P, c, frac=ARRIVAL_FRAC, by="comp"):
    """Une ligne par (origine, unité) : cartes inédites réunies, ancre, date d'arrivée."""
    g = P.groupby(["t", by])
    U = g.U.agg(lambda s: set().union(*s)).rename("U")
    out = U.reset_index().rename(columns={by: "unit"})
    out["labels"] = g.label.agg(lambda s: " / ".join(sorted(s))).values
    out["anchor"] = out.U.apply(lambda u: anchor_of(u, c))
    out["arrival"] = out.U.apply(lambda u: arrival(u, c, frac))
    out["n_unrel"] = out.U.apply(len)
    return out


# ---------------------------------------------------------------- Kaplan-Meier

def km(entry, exit_, event):
    """Kaplan-Meier à entrée différée (à risque en x si entry < x <= exit). Renvoie temps, S, n, d, var Greenwood."""
    entry, exit_, event = map(np.asarray, (entry, exit_, event))
    times = np.unique(exit_[event == 1])
    n = np.array([((entry < x) & (exit_ >= x)).sum() for x in times])
    d = np.array([((exit_ == x) & (event == 1)).sum() for x in times])
    ok = n > 0
    times, n, d = times[ok], n[ok], d[ok]
    S = np.cumprod(1 - d / n)
    with np.errstate(divide="ignore", invalid="ignore"):
        gw = np.cumsum(np.where(n > d, d / (n * (n - d)), np.nan))
    return pd.DataFrame({"time": times, "n_risk": n, "n_event": d, "S": S, "var": S ** 2 * gw})


def S_at(curve, x):
    s = curve.S[curve.time <= x]
    return float(s.iloc[-1]) if len(s) else 1.0


def km_window(curve, u, max_time, level=LEVEL):
    """Fenêtre conditionnelle [L, U] (âges en jours) et sa probabilité KM, ou None si 90 % n'est pas atteint."""
    su = S_at(curve, u)
    cur = curve[curve.time > u]
    if su <= 0 or cur.empty:
        return None
    F = 1 - cur.S.values / su
    tt = cur.time.values
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    if F.max() < hi - 1e-12:
        return None
    j = int(np.argmax(F >= lo - 1e-12))
    k = int(np.argmax(F >= hi - 1e-12))
    prev = tt[j - 1] if j > 0 else u
    L = (prev + tt[j]) / 2 if j > 0 else u
    nxt = tt[k + 1] if k + 1 < len(tt) else min(max_time, tt[k])
    Uend = (tt[k] + nxt) / 2
    cov = F[k] - (F[j - 1] if j > 0 else 0.0)
    return L, Uend, cov


def km_horizon(curve, u, max_time, h=HORIZON_DAYS):
    if u + h > max_time:
        return None
    su = S_at(curve, u)
    return 1 - S_at(curve, u + h) / su if su > 0 else None


# ---------------------------------------------------------------- validation glissante

def training(first_rows, t):
    """Unités déjà retenues à t : (entrée, sortie, événement) en âge depuis l'ancre, censure à t."""
    tr = first_rows[first_rows.t <= t]
    known = tr.arrival.notna() & (tr.arrival <= t)
    exit_ = np.where(known, (tr.arrival - tr.anchor).dt.days, (t - tr.anchor).dt.days)
    entry = (tr.t - tr.anchor).dt.days.values
    return entry, exit_.astype(float), known.astype(int).values, tr


def predict(panel, first_rows, card_lags, ref, horizon=True):
    """Toutes les méthodes, à chaque (origine, unité) du panel."""
    out = []
    for t, g in panel.groupby("t"):
        entry, exit_, ev, tr = training(first_rows, t)
        n_ev = int(ev.sum())
        curve = km(entry, exit_, ev) if n_ev >= MIN_EVENTS else None
        max_time = float(exit_.max()) if len(exit_) else 0.0
        surv = exit_[ev == 1]
        cl = card_lags[(card_lags.ocg_date < t) & (card_lags.tcg_date <= t)].lag
        for r in g.itertuples():
            u = (t - r.anchor).days
            base = dict(t=t, unit=r.unit, labels=r.labels, anchor=r.anchor, age=u, arrival=r.arrival,
                        n_train=len(tr), n_events_train=n_ev, cohort=r.anchor.strftime("%Y-%m"))
            wins = {"a_fixe_75_202": (FIXED_P10, FIXED_P90, LEVEL)}
            if len(cl) >= 30:
                wins["a2_carte_glissante"] = (*np.percentile(cl, [10, 90]), LEVEL)
            if n_ev >= MIN_EVENTS:
                wins["b_survivants"] = (*np.quantile(surv, [0.1, 0.9]), LEVEL)
            if curve is not None:
                w = km_window(curve, u, max_time)
                wins["km_survie"] = w if w is not None else (np.nan, np.nan, np.nan)
            for name, (L, Ue, cov) in wins.items():
                row = dict(base, method=name, L=L, U=Ue, announced=cov)
                if np.isnan(L):
                    row["status"] = "pas_de_fenetre"
                else:
                    start, end = r.anchor + pd.Timedelta(days=L), r.anchor + pd.Timedelta(days=Ue)
                    row.update(start=start, end=end)
                    arrived = pd.notna(r.arrival)
                    if end > ref and not arrived:
                        row["status"] = "suivi_incomplet"
                    elif end > ref:      # arrivée connue mais fin de fenêtre future : on n'évalue pas (sélection)
                        row["status"] = "suivi_incomplet"
                    else:
                        row["status"] = "evaluee"
                        row["hit"] = int(arrived and start <= r.arrival <= end)
                out.append(row)
            if horizon and curve is not None:
                p = km_horizon(curve, u, max_time)
                row = dict(base, method="km_horizon_183j", announced=p)
                if p is None:
                    row["status"] = "pas_de_fenetre"
                elif t + pd.Timedelta(days=HORIZON_DAYS) > ref:
                    row["status"] = "suivi_incomplet"
                else:
                    row["status"] = "evaluee"
                    row["hit"] = int(pd.notna(r.arrival) and r.arrival <= t + pd.Timedelta(days=HORIZON_DAYS))
                out.append(row)
    return pd.DataFrame(out)


def binom_two_sided(k, n):
    """Test du signe exact bilatéral (p = 0,5)."""
    if n == 0:
        return 1.0
    from math import comb
    pk = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-15))


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def boot(df, rng, n_boot=N_BOOT):
    """Bootstrap par cohorte : IC 95 % de la couverture observée et de l'écart observée - annoncée."""
    groups = [g for _, g in df.groupby("cohort")]
    if len(groups) < 2:
        return (np.nan,) * 4
    hits = np.array([g.hit.sum() for g in groups], float)
    ann = np.array([g.announced.sum() for g in groups], float)
    ns = np.array([len(g) for g in groups], float)
    idx = rng.integers(0, len(groups), size=(n_boot, len(groups)))
    obs = hits[idx].sum(1) / ns[idx].sum(1)
    gap = obs - ann[idx].sum(1) / ns[idx].sum(1)
    return (*np.percentile(obs, [2.5, 97.5]), *np.percentile(gap, [2.5, 97.5]))


def summarize(pred, title, rng, years=(2024, 2025)):
    print(f"\n### {title}")
    print(f"{'méthode':<20} {'période':<9} {'prév.':>5} {'unités':>6} {'cohortes':>8} {'annoncée':>8} {'observée':>8} "
          f"{'IC boot. 95 %':>15} {'écart (IC)':>22} {'Wilson 95 %':>15} {'sans fenêtre':>12} {'suivi incomplet':>15}")
    rows = []
    for meth, gm in pred.groupby("method", sort=False):
        periods = [(str(y), gm[gm.t.dt.year == y]) for y in years]
        periods += [("total", gm)] if len(years) > 1 else []
        for per, gp in periods:
            e = gp[gp.status == "evaluee"]
            nw = int((gp.status == "pas_de_fenetre").sum())
            ni = int((gp.status == "suivi_incomplet").sum())
            if e.empty:
                print(f"{meth:<20} {per:<9} {0:>5} {'':>6} {'':>8} {'':>8} {'':>8} {'':>15} {'':>22} {'':>15} {nw:>12} {ni:>15}")
                continue
            o, a = e.hit.mean(), e.announced.mean()
            lo, hi, glo, ghi = boot(e, rng)
            wl, wh = wilson(e.hit.sum(), len(e))
            print(f"{meth:<20} {per:<9} {len(e):>5} {e.unit.nunique():>6} {e.cohort.nunique():>8} {a:>8.1%} {o:>8.1%} "
                  f"{f'[{lo:.0%} ; {hi:.0%}]':>15} {f'{o - a:+.1%} [{glo:+.0%} ; {ghi:+.0%}]':>22} "
                  f"{f'[{wl:.0%} ; {wh:.0%}]':>15} {nw:>12} {ni:>15}")
            rows.append(dict(method=meth, period=per, n=len(e), units=e.unit.nunique(), cohorts=e.cohort.nunique(),
                             announced=a, observed=o, gap=o - a, gap_lo=glo, gap_hi=ghi))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- écriture (table nouvelle)

def write_tables(db_path, rows, curve, as_of):
    con = sqlite3.connect(db_path, timeout=60)
    try:
        existing = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        cols_s = list(rows.columns)
        cols_k = list(curve.columns)
        for name, cols in (("tcg_arrival_survival", cols_s), ("tcg_arrival_km", cols_k)):
            if name in existing:
                have = [r[1] for r in con.execute(f"PRAGMA table_info({name})")]
                if have != cols:
                    raise SystemExit(f"Table {name} existante avec un autre schéma : refus d'écrire.")
        with con:   # une seule transaction
            con.execute("DROP TABLE IF EXISTS tcg_arrival_survival")
            con.execute("DROP TABLE IF EXISTS tcg_arrival_km")
            rows.to_sql("tcg_arrival_survival", con, index=False)
            curve.to_sql("tcg_arrival_km", con, index=False)
    finally:
        con.close()
    print(f"\nÉcrit dans {db_path} : tcg_arrival_survival ({len(rows)} lignes), tcg_arrival_km ({len(curve)} lignes), "
          f"as_of {as_of}.")


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", type=Path, default=MAIN_DB)
    ap.add_argument("--write", action="store_true", help="écrit 2 tables nouvelles (à tester sur une copie)")
    ap.add_argument("--reference", action="store_true",
                    help="autorise --write sur la base du dépôt principal (après sauvegarde, formulaire validé)")
    args = ap.parse_args()
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    pd.set_option("display.width", 250)

    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=60)
    ref, c, ocgm, od, cards, tcg_names = load(con)
    con.close()
    origins = list(pd.date_range("2024-02-01", ref, freq="MS"))
    P = build_panel(origins, c, ocgm, od)
    panel = unit_panel(P, c)
    panel = panel[panel.anchor >= BURN_IN]
    first_rows = panel.sort_values("t").groupby("unit").first().reset_index()
    card_lags = cards.dropna(subset=["tcg_date", "ocg_date"]).copy()
    card_lags["lag"] = (card_lags.tcg_date - card_lags.ocg_date).dt.days
    card_lags = card_lags[(card_lags.ocg_date >= "2022-01-01") & (card_lags.lag > 0)]

    print(f"Base : {args.db} | dernière date (REF) : {ref.date()} | origines mensuelles : {len(origins)}")
    print(f"Libellés retenus au moins une fois : {P.label.nunique()} ; unités après fusion : {P.comp.nunique()} ; "
          f"après burn-in (ancre >= {BURN_IN.date()}) : {first_rows.unit.nunique()}")
    merged = P.groupby("comp").label.unique()
    print("Fusions :", "; ".join(" / ".join(sorted(v)) for v in merged if len(v) > 1))

    # -------- courbe au REF
    fr = first_rows.copy()
    fr["dur"] = np.where(fr.arrival.notna(), (fr.arrival - fr.anchor).dt.days, (ref - fr.anchor).dt.days)
    fr["ev"] = fr.arrival.notna().astype(int)
    fr["entry"] = (fr.t - fr.anchor).dt.days
    curve = km(fr.entry, fr["dur"], fr.ev)
    print(f"\n## Courbe de Kaplan-Meier au {ref.date()} : {len(fr)} unités, {fr.ev.sum()} arrivées, "
          f"{len(fr) - fr.ev.sum()} censurées, {fr.anchor.dt.strftime('%Y-%m').nunique()} cohortes (mois d'ancre)")
    print(f"Délais observés (jours depuis l'ancre) : min {fr.dur[fr.ev == 1].min()}, médiane {fr.dur[fr.ev == 1].median():.0f}, "
          f"max {fr.dur[fr.ev == 1].max()} ; censurées : {sorted(fr.dur[fr.ev == 0].tolist())}")
    # IC par bootstrap de cohortes
    fr["cohort"] = fr.anchor.dt.strftime("%Y-%m")
    grid = [60, 75, 90, 105, 120, 150, 180, 202, 240, 300, 365]
    cohorts = [g for _, g in fr.groupby("cohort")]
    bs = []
    for _ in range(N_BOOT):
        s = pd.concat([cohorts[i] for i in rng.integers(0, len(cohorts), len(cohorts))])
        cv = km(s.entry, s["dur"], s.ev)
        bs.append([1 - S_at(cv, x) for x in grid])
    bs = np.array(bs)
    print(f"{'jours':>6} {'à risque':>8} {'P(arrivé)':>10} {'IC 95 % (cohortes)':>20} {'Greenwood ±1,96 se':>20}")
    for i, x in enumerate(grid):
        s = S_at(curve, x)
        v = curve["var"][curve.time <= x]
        se = float(np.sqrt(v.iloc[-1])) if len(v) else 0.0
        nr = int(((fr.entry < x) & (fr["dur"] >= x)).sum())
        lo, hi = np.percentile(bs[:, i], [2.5, 97.5])
        print(f"{x:>6} {nr:>8} {1 - s:>10.1%} {f'[{lo:.0%} ; {hi:.0%}]':>20} {f'± {1.96 * se:.0%}':>20}")
    tail = curve[curve.n_risk >= 5]
    i180 = grid.index(180)
    print(f"P(jamais arrivé) <= S au dernier temps avec >= 5 unités à risque ({int(tail.time.iloc[-1])} j) = "
          f"{tail.S.iloc[-1]:.1%} (borne HAUTE : un archétype qui n'arrive jamais n'est pas arrivé à ce délai) ; "
          f"S(180 j) IC 95 % cohortes [{1 - np.percentile(bs[:, i180], 97.5):.0%} ; {1 - np.percentile(bs[:, i180], 2.5):.0%}]. "
          f"Au-delà de {int(curve.time[curve.n_risk >= 2].iloc[-1])} j, moins de 2 unités à risque : la queue n'est pas estimée.")

    # -------- validation
    ev_panel = panel[(panel.t >= EVAL_START) & (panel.t <= EVAL_END)].copy()
    first_eval = ev_panel.sort_values("t").groupby("unit").first().reset_index()
    pred_first = predict(first_eval, first_rows, card_lags, ref)
    pred_all = predict(ev_panel, first_rows, card_lags, ref)
    print("\n## Validation à origine glissante (origines 2024-01 → 2025-12)")
    print("Prévisions sans fenêtre = KM non estimable (< 8 arrivées connues) ou 90 % non atteint ; "
          "« suivi incomplet » = fin de fenêtre après REF.")
    summ = summarize(pred_first, "Population principale : chaque unité à sa première rétention", rng)
    summarize(pred_all, "Sensibilité : toutes les paires (unité, mois) où l'unité est retenue", rng)
    det = pred_first[pred_first.method == "km_survie"][["t", "labels", "anchor", "age", "n_events_train", "L", "U",
                                                        "announced", "arrival", "status", "hit"]]
    print("\nDétail KM, première rétention :")
    print(det.to_string(index=False))

    # -------- extension 2026 (supplément, hors critère)
    sup_panel = panel[(panel.t > EVAL_END)]
    sup_first = sup_panel[~sup_panel.unit.isin(first_eval.unit)].sort_values("t").groupby("unit").first().reset_index()
    pred_sup = predict(sup_first, first_rows, card_lags, ref)
    summarize(pred_sup, "Supplément hors critère : premières rétentions de 2026 (évaluées si la fenêtre est finie)",
              rng, years=(2026,))

    summarize(pd.concat([pred_first, pred_sup]), "Groupé hors critère : premières rétentions 2024-2026", rng,
              years=(2024, 2025, 2026))
    allp = panel[panel.t >= EVAL_START]
    stale = (allp.t > allp.anchor + pd.Timedelta(days=FIXED_P90))
    print(f"\nPaires (unité, mois) retenues 2024-2026 : {len(allp)} ; fenêtre fixe 75-202 déjà finie à la date "
          f"d'affichage : {int(stale.sum())} ({', '.join(sorted(allp[stale].labels.unique()))})")

    # -------- comparaison appariée et variante unilatérale (2025-2026, hors critère, exploratoire)
    both = pd.concat([pred_first, pred_sup])
    both = both[both.method.isin(["a_fixe_75_202", "a2_carte_glissante", "b_survivants", "km_survie"])]
    ok = both[both.status == "evaluee"].pivot_table(index=["t", "unit"], columns="method", values="hit")
    ok = ok.dropna()
    wd = both[both.status == "evaluee"].assign(w=lambda d: d.U - np.maximum(d.L, d.age))
    wd = wd.set_index(["t", "unit"]).loc[ok.index].groupby("method").w.median()
    an = both[both.status == "evaluee"].set_index(["t", "unit"]).loc[ok.index].groupby("method").announced.mean()
    coh = both.drop_duplicates(["t", "unit"]).set_index(["t", "unit"]).loc[ok.index].cohort
    print(f"\n## Comparaison appariée : prévisions évaluées par les 4 méthodes (premières rétentions 2024-2026), "
          f"n = {len(ok)}, {coh.nunique()} cohortes")
    print(f"{'méthode':<20} {'annoncée':>8} {'observée':>8} {'k sur n':>8} {'largeur médiane restante (j)':>28}")
    for meth in ok.columns:
        print(f"{meth:<20} {an[meth]:>8.1%} {ok[meth].mean():>8.1%} {f'{int(ok[meth].sum())}/{len(ok)}':>8} {wd[meth]:>28.0f}")
    d = ok["km_survie"] - ok["a_fixe_75_202"]
    print(f"KM juste et fixe faux : {(d > 0).sum()} ; fixe juste et KM faux : {(d < 0).sum()} (test du signe exact "
          f"p = {binom_two_sided(int((d > 0).sum()), int((d != 0).sum())):.2f})")
    one = both[(both.status == "evaluee")].copy()
    one["hit_late"] = (one.arrival.notna() & (one.arrival <= one.end)).astype(int)
    print("Variante unilatérale (exploratoire, choisie après lecture) : arrivée avant la fin de fenêtre — "
          + " ; ".join(f"{m} {g.hit_late.mean():.0%} (n = {len(g)})" for m, g in one.groupby("method")))

    # -------- sensibilités de définition
    print("\n## Sensibilités (population principale, KM seule, 2024-2025)")
    sens = {}
    for name, kw in [("arrivée = 1re carte inédite sortie", dict(frac=1e-9)),
                     ("arrivée = toutes les cartes inédites sorties", dict(frac=1.0)),
                     ("unités = libellés (sans fusion)", dict(by="label"))]:
        pn = unit_panel(P, c, **kw)
        pn = pn[pn.anchor >= BURN_IN]
        frs = pn.sort_values("t").groupby("unit").first().reset_index()
        e = pn[(pn.t >= EVAL_START) & (pn.t <= EVAL_END)].sort_values("t").groupby("unit").first().reset_index()
        pr = predict(e, frs, card_lags, ref, horizon=False)
        sens[name] = pr
    pn = unit_panel(P, c)   # sans burn-in
    frs = pn.sort_values("t").groupby("unit").first().reset_index()
    e = pn[(pn.t >= EVAL_START) & (pn.t <= EVAL_END)].sort_values("t").groupby("unit").first().reset_index()
    sens["sans burn-in (ancres de janv.-févr. 2024 gardées)"] = predict(e, frs, card_lags, ref, horizon=False)
    # arrivée par nom (validateur), libellés jamais joués en TCG avant l'ancre
    pl = unit_panel(P, c, by="label")
    pl = pl[pl.anchor >= BURN_IN]

    def name_arrival(r):
        s = tcg_names[tcg_names.archetype.str.contains(r.unit, regex=False)].d.sort_values()
        if (s < r.anchor).sum() >= 5:
            return "deja"
        after = s[s >= r.anchor]
        return after.iloc[4] if len(after) >= 5 else pd.NaT
    fl = pl.sort_values("t").groupby("unit").first().reset_index()
    na = fl.apply(name_arrival, axis=1)
    keep = fl.unit[na.astype(str) != "deja"]
    pl = pl[pl.unit.isin(keep)].copy()
    pl["arrival"] = pl.unit.map(dict(zip(fl.unit, na)))
    pl["arrival"] = pd.to_datetime(pl.arrival.where(pl.arrival.astype(str) != "deja"))
    frs = pl.sort_values("t").groupby("unit").first().reset_index()
    e = pl[(pl.t >= EVAL_START) & (pl.t <= EVAL_END)].sort_values("t").groupby("unit").first().reset_index()
    sens[f"arrivée par nom (>= 5 decks TCG, validateur), {len(keep)} libellés sur {len(fl)}"] = \
        predict(e, frs, card_lags, ref, horizon=False)
    for name, pr in sens.items():
        k = pr[(pr.method == "km_survie") & (pr.status == "evaluee")]
        nw = int(((pr.method == "km_survie") & (pr.status == "pas_de_fenetre")).sum())
        if k.empty:
            print(f"- {name} : aucune prévision évaluable ({nw} sans fenêtre)")
            continue
        lo, hi, glo, ghi = boot(k, rng)
        f = pr[(pr.method == "a_fixe_75_202") & (pr.status == "evaluee")]
        print(f"- {name} : n = {len(k)} ({k.cohort.nunique()} cohortes), annoncée {k.announced.mean():.1%}, "
              f"observée {k.hit.mean():.1%} [{lo:.0%} ; {hi:.0%}], écart {k.hit.mean() - k.announced.mean():+.1%} "
              f"; sans fenêtre {nw} | fixe 75-202 : {f.hit.mean():.1%} (n = {len(f)})")

    # -------- verdict
    m = summ[(summ.method == "km_survie") & (summ.period == "total")]
    if len(m):
        r = m.iloc[0]
        ok = abs(r.gap) <= 0.05
        print(f"\n## Critère (|observée - annoncée| <= 5 points, KM, première rétention, 2024-2025) : "
              f"{'ATTEINT' if ok else 'NON ATTEINT'} en estimation ponctuelle ({r.gap:+.1%}, n = {r.n}, "
              f"{r.cohorts} cohortes) ; IC 95 % de l'écart [{r.gap_lo:+.0%} ; {r.gap_hi:+.0%}] : "
              f"{'compatible' if r.gap_lo <= 0.05 and r.gap_hi >= -0.05 else 'incompatible'} avec ± 5 points, "
              f"{'mais trop large pour le démontrer' if (r.gap_hi - r.gap_lo) > 0.10 else 'et assez étroit'}.")

    # -------- prévision au REF (pour --write)
    t_now = ref + pd.Timedelta(days=1)
    now = retained_at(t_now, c, ocgm, od)
    print(f"\n## Archétypes retenus au {ref.date()} (règle du notebook 10) : {sorted(now)}")
    max_time = float(fr["dur"].max())
    out_rows = []
    labels_by_comp = P.groupby("label").comp.first().to_dict()
    for lab, U in sorted(now.items()):
        a = anchor_of(U, c)
        u = (t_now - a).days
        w = km_window(curve, u, max_time)
        p6 = km_horizon(curve, u, max_time)
        row = dict(archetype=lab, unit=labels_by_comp.get(lab, lab), n_unreleased=len(U),
                   ocg_anchor=a.strftime("%Y-%m-%d"), age_days=u,
                   window_start=(a + pd.Timedelta(days=w[0])).strftime("%Y-%m-%d") if w else None,
                   window_end=(a + pd.Timedelta(days=w[1])).strftime("%Y-%m-%d") if w else None,
                   announced_coverage=round(w[2], 4) if w else None,
                   p_arrival_183d=round(p6, 4) if p6 is not None else None,
                   km_units=len(fr), km_events=int(fr.ev.sum()),
                   method=METHOD, as_of=ref.strftime("%Y-%m-%d"),
                   computed_at=datetime.now().strftime("%Y-%m-%d"))
        out_rows.append(row)
        print(f"- {lab} : ancre {row['ocg_anchor']} (âge {u} j), fenêtre {row['window_start']} → {row['window_end']} "
              f"(probabilité KM {row['announced_coverage']}), P(arrivée sous 183 j) {row['p_arrival_183d']}")
    if args.write:
        if args.db.resolve() == MAIN_DB.resolve() and not args.reference:
            print("Refus : --write sur la base du dépôt principal sans --reference. Tester sur une copie (--db).")
            return 1
        kc = curve.assign(se=np.sqrt(curve["var"])).drop(columns="var").rename(
            columns={"time": "time_days", "S": "survival"})
        kc["p_arrived"] = 1 - kc.survival
        kc["as_of"] = ref.strftime("%Y-%m-%d")
        kc["computed_at"] = datetime.now().strftime("%Y-%m-%d")
        write_tables(args.db, pd.DataFrame(out_rows), kc, ref.date())
    print(f"\nTemps d'exécution : {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
