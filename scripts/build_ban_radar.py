"""
TOK-53 — Ban Radar : score de risque de ban par carte (multi-critères).

Génère la table `ban_radar` dans yugioh.db.

    python scripts/build_ban_radar.py              # écrit la table
    python scripts/build_ban_radar.py --dry-run    # affiche le top 25
    python scripts/build_ban_radar.py --backtest   # rejoue les banlists passées

Le score est un score de RISQUE 0-100, pas une probabilité calibrée : il classe
les cartes par ressemblance au profil des cartes historiquement touchées. La
mise en regard publique avec l'historique réel est TOK-55.

Critères retenus après backtest sur la banlist du 2026-05-18 (voir --backtest).
Deux enseignements ont façonné le jeu de features :

- Konami ne frappe pas les staples génériques les plus joués (Ash Blossom est
  à 3 depuis toujours) mais les pièces de moteur des decks qui gagnent. Le
  nombre d'archétypes qui jouent une carte ne discrimine rien du tout
  (médiane 4 chez les touchées comme chez les autres) — critère abandonné.
- Le nombre moyen d'exemplaires joués est le critère le plus discriminant
  (2.50 chez les touchées vs 1.10) : une carte jouée à 3 offre une marge de
  restriction, une carte jouée à 1 beaucoup moins. Le retirer fait chuter le
  rappel top-10% de 5/10 à 1/10.
"""

import argparse
import os
import sqlite3

import numpy as np
import pandas as pd

DB = os.path.join(os.path.dirname(__file__), "..", "data", "yugioh.db")

WINDOW_MONTHS = 6
MOMENTUM_SPLIT_MONTHS = 3
MIN_DECKS = 5
MAX_COPIES = 3

# En dessous, la carte est jouée un peu partout : pas d'archétype d'attache,
# c'est une staple générique.
GENERIC_CONCENTRATION_THRESHOLD = 0.5

# Somme = 1.0. Testés à ±0.10 sans changer le classement des cartes touchées.
WEIGHTS = {
    "ubiquity": 0.30,     # part des decks du format qui jouent la carte
    "carrier": 0.25,      # pièce de moteur d'un archétype qui pèse dans la méta
    "copies": 0.20,       # marge de restriction (jouée à 3 = réductible)
    "restriction": 0.10,  # déjà touchée : Konami y revient
    "momentum": 0.10,     # usage en hausse
    "bridge": 0.05,       # centralité de type pont dans le graphe de synergies
}

# Une carte déjà à 1 exemplaire et toujours omniprésente est la cible suivante.
RESTRICTION_WEIGHT = {"Limited": 1.0, "Semi-Limited": 0.6}

RISK_BANDS = [(70, "Critique"), (50, "Élevé"), (30, "Modéré"), (0, "Faible")]

# Sévérité croissante : une carte est « touchée » quand elle monte d'un cran.
SEVERITY = {"Unlimited": 0, "Semi-Limited": 1, "Limited": 2, "Forbidden": 3}

# En dessous, l'univers noté est trop maigre pour que le backtest dise quoi que
# ce soit : la plupart des cartes touchées n'atteignent même pas le seuil
# d'entrée, et le rang médian porte sur deux ou trois observations.
BACKTEST_MIN_DECKS = 600
BACKTEST_MIN_HITS = 5


def risk_label(score: float) -> str:
    return next(label for threshold, label in RISK_BANDS if score >= threshold)


def load_usage(conn: sqlite3.Connection, as_of: str, fmt: str) -> pd.DataFrame:
    """Une ligne par (carte, deck) sur la fenêtre glissante, decks légaux du format."""
    return pd.read_sql_query(
        f"""
        SELECT dc.card_name, dc.amount, td.id AS deck_id, td.archetype,
               strftime('%Y-%m', td.created) AS month
        FROM deck_cards dc
        JOIN tournament_decks td ON td.id = dc.deck_id
        WHERE td.ocg = :ocg AND td.illegal = 0
          AND td.created <= :as_of
          AND td.created >= date(:as_of, '-{WINDOW_MONTHS} months')
        """,
        conn,
        params={"as_of": as_of, "ocg": 1 if fmt == "OCG" else 0},
    )


def compute_carrier(usage: pd.DataFrame, n_decks: int) -> pd.DataFrame:
    """Pour chaque carte : son archétype porteur et le poids de ce couple.

    carrier = (part des decks de l'archétype qui jouent la carte) x (part de
    méta de l'archétype). Élevé pour une pièce indispensable d'un deck qui pèse,
    quasi nul pour une tech jouée çà et là ou pour le cœur d'un deck confidentiel.
    """
    archetype_decks = usage.groupby("archetype").deck_id.nunique()
    archetype_share = archetype_decks / n_decks

    pairs = (
        usage.groupby(["card_name", "archetype"])
        .deck_id.nunique()
        .rename("decks")
        .reset_index()
    )
    pairs["coreness"] = pairs.decks / pairs.archetype.map(archetype_decks)
    pairs["carrier"] = pairs.coreness * pairs.archetype.map(archetype_share)

    best = (
        pairs.sort_values("carrier", ascending=False)
        .drop_duplicates("card_name")
        .set_index("card_name")
    )
    # Part des decks jouant la carte qui appartiennent à cet archétype. Basse
    # pour une staple générique : sans ça, Ash Blossom serait étiquetée du nom
    # du deck le plus représenté du format, ce qui n'a aucun sens.
    best["concentration"] = best.decks / pairs.groupby("card_name").decks.sum()
    return best


def compute_momentum(usage: pd.DataFrame, as_of: str) -> pd.Series:
    """Croissance du taux de jeu sur les 3 derniers mois vs les 3 précédents.

    Rapporté au nombre de decks de chaque demi-fenêtre, sinon une demi-fenêtre
    plus fournie en tournois ferait passer toutes les cartes pour montantes.
    """
    split = (pd.Timestamp(as_of) - pd.DateOffset(months=MOMENTUM_SPLIT_MONTHS)).strftime("%Y-%m")
    recent, older = usage[usage.month > split], usage[usage.month <= split]

    n_recent, n_older = recent.deck_id.nunique(), older.deck_id.nunique()
    if not n_recent or not n_older:
        return pd.Series(dtype=float)

    rate_recent = recent.groupby("card_name").deck_id.nunique() / n_recent
    rate_older = older.groupby("card_name").deck_id.nunique() / n_older
    growth = rate_recent.div(rate_older.reindex(rate_recent.index).fillna(0)) - 1

    # Une carte absente de la demi-fenêtre ancienne donne un ratio infini :
    # traitée comme "montante à fond" plutôt que rejetée.
    return growth.replace(np.inf, 1.0).clip(0, 1).fillna(0)


def current_banlist_status(conn: sqlite3.Connection, as_of: str, fmt: str) -> pd.Series:
    """Statut en vigueur à `as_of` dans ce format, indexé par carte.

    Le filtre porte sur la colonne `format` et non sur le nom de la page :
    Yugipedia nomme les listes TCG d'avant 2021 sans suffixe, un
    `list_name LIKE '%TCG%'` en laissait 33 de côté.
    """
    bh = pd.read_sql_query(
        "SELECT card_name, status, effective_date, end_date FROM banlist_history "
        "WHERE format = ?",
        conn,
        params=(fmt,),
    )
    in_force = bh[(bh.effective_date <= as_of) & (bh.end_date.isna() | (bh.end_date >= as_of))]
    return in_force.groupby("card_name").status.first()


def banlist_events(conn: sqlite3.Connection, fmt: str) -> list[tuple[str, str, list[str]]]:
    """(veille, date d'effet, cartes nouvellement restreintes) pour chaque liste.

    Une carte compte comme touchée quand son statut gagne en sévérité par
    rapport à la liste précédente du même format. Les assouplissements sont
    ignorés : le Ban Radar prédit des restrictions.
    """
    bh = pd.read_sql_query(
        "SELECT effective_date, card_name, status FROM banlist_history "
        "WHERE format = ? AND effective_date IS NOT NULL",
        conn,
        params=(fmt,),
    )
    events = []
    dates = sorted(bh.effective_date.unique())
    for previous_date, date in zip(dates, dates[1:]):
        before = bh[bh.effective_date == previous_date].set_index("card_name").status
        after = bh[bh.effective_date == date].set_index("card_name").status
        hits = [
            card
            for card, status in after.items()
            if SEVERITY[status] > SEVERITY.get(before.get(card, "Unlimited"), 0)
        ]
        if hits:
            eve = (pd.Timestamp(date) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            events.append((eve, date, hits))
    return events


def build(conn: sqlite3.Connection, as_of: str, fmt: str = "TCG") -> pd.DataFrame:
    usage = load_usage(conn, as_of, fmt)
    if usage.empty:
        raise SystemExit(f"Aucun deck {fmt} sur la fenêtre se terminant le {as_of}")

    n_decks = usage.deck_id.nunique()
    totals = usage.groupby("card_name").agg(
        decks=("deck_id", "nunique"),
        n_archetypes=("archetype", "nunique"),
        mean_copies=("amount", "mean"),
    )
    totals = totals[totals.decks >= MIN_DECKS]

    carrier = compute_carrier(usage, n_decks).reindex(totals.index)
    status = current_banlist_status(conn, as_of, fmt)
    betweenness = pd.read_sql_query(
        "SELECT card_name, betweenness FROM card_graph_metrics", conn
    ).set_index("card_name").betweenness
    max_betweenness = betweenness.max() or 1.0

    df = pd.DataFrame(index=totals.index)
    df["ubiquity"] = totals.decks / n_decks
    df["carrier"] = carrier.carrier.fillna(0)
    df["copies"] = ((totals.mean_copies - 1) / (MAX_COPIES - 1)).clip(0, 1)
    df["restriction"] = status.reindex(df.index).map(RESTRICTION_WEIGHT).fillna(0.0)
    df["momentum"] = compute_momentum(usage, as_of).reindex(df.index).fillna(0.0)
    df["bridge"] = (betweenness.reindex(df.index).fillna(0) / max_betweenness).clip(0, 1)

    raw = sum(df[k] * w for k, w in WEIGHTS.items())

    # Les cartes déjà Forbidden ne peuvent plus être bannies : hors radar.
    # Retirées avant le rééchelonnage pour ne pas écraser l'échelle.
    df = df[status.reindex(df.index) != "Forbidden"]
    raw = raw.reindex(df.index)

    # Rééchelonné sur le max observé : en absolu aucune carte ne dépasse ~0.45
    # et les paliers de risque ne discrimineraient rien.
    df["ban_risk_score"] = (raw / raw.max() * 100).round(1)
    df["risk_label"] = df.ban_risk_score.map(risk_label)

    df["current_status"] = status.reindex(df.index).fillna("Unlimited")
    df["decks"] = totals.decks.reindex(df.index)
    df["deck_share"] = (df.ubiquity * 100).round(2)
    df["n_archetypes"] = totals.n_archetypes.reindex(df.index)
    df["mean_copies"] = totals.mean_copies.reindex(df.index).round(2)
    df["top_archetype"] = carrier.archetype.reindex(df.index).where(
        carrier.concentration.reindex(df.index) >= GENERIC_CONCENTRATION_THRESHOLD
    )
    df["archetype_concentration"] = carrier.concentration.reindex(df.index).round(3)
    df["format"] = fmt
    df["as_of"] = as_of
    df["n_decks_window"] = n_decks

    for column in WEIGHTS:
        df[column] = df[column].round(4)

    return df.sort_values("ban_risk_score", ascending=False).reset_index()


def backtest(conn: sqlite3.Connection, formats: tuple[str, ...] = ("TCG", "OCG")) -> None:
    """Rejoue le score la veille de chaque banlist et situe les cartes touchées.

    Les listes sont lues depuis `banlist_history` plutôt que codées en dur :
    toute nouvelle banlist scrapée devient automatiquement un point de mesure.
    """
    for fmt in formats:
        print(f"\n{'=' * 66}\n{fmt}\n{'=' * 66}")
        skipped = []

        for as_of, effective, hits in banlist_events(conn, fmt):
            usage_decks = load_usage(conn, as_of, fmt).deck_id.nunique()
            if usage_decks < BACKTEST_MIN_DECKS or len(hits) < BACKTEST_MIN_HITS:
                skipped.append((effective, usage_decks, len(hits)))
                continue

            df = build(conn, as_of, fmt).set_index("card_name")
            n = len(df)
            ranked = [(h, df.index.get_loc(h) + 1) for h in hits if h in df.index]
            missing = [h for h in hits if h not in df.index]

            print(f"\n--- Liste du {effective} — {len(hits)} cartes touchées")
            print(f"    univers noté : {n} cartes ({usage_decks} decks sur {WINDOW_MONTHS} mois)")
            if not ranked:
                print("    aucune carte touchée n'atteint le seuil d'entrée")
                continue

            ranks = np.array([r for _, r in ranked])
            percentiles = ranks / n * 100
            for card, rank in sorted(ranked, key=lambda x: x[1]):
                print(f"      #{rank:<4} ({rank / n * 100:4.1f}%)  "
                      f"{df.loc[card, 'ban_risk_score']:>5}  {card}")
            if missing:
                print(f"    hors univers (<{MIN_DECKS} decks) : {len(missing)}")
            print(f"    -> rang médian {np.median(ranks):.0f}/{n} (aléatoire ≈ {n / 2:.0f})"
                  f" | top-10% : {(percentiles <= 10).sum()}/{len(ranks)}"
                  f" | top-25% : {(percentiles <= 25).sum()}/{len(ranks)}")

        if skipped:
            print(f"\n    {len(skipped)} listes écartées faute de matière "
                  f"(<{BACKTEST_MIN_DECKS} decks ou <{BACKTEST_MIN_HITS} cartes touchées) — "
                  f"les plus récentes : "
                  + ", ".join(f"{d} ({n} decks, {h} touchées)" for d, n, h in skipped[-3:]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", help="Date de référence YYYY-MM-DD (défaut : dernier deck du format)")
    parser.add_argument("--format", choices=["tcg", "ocg"], default="tcg",
                        help="Format noté (défaut : tcg — c'est lui que sert l'API)")
    parser.add_argument("--dry-run", action="store_true", help="Affiche le top 25 sans écrire")
    parser.add_argument("--backtest", action="store_true", help="Rejoue les banlists passées")
    args = parser.parse_args()

    conn = sqlite3.connect(DB)
    fmt = args.format.upper()

    if args.backtest:
        backtest(conn)
        return

    as_of = args.as_of or conn.execute(
        "SELECT MAX(created) FROM tournament_decks WHERE ocg = ?",
        (1 if fmt == "OCG" else 0,),
    ).fetchone()[0][:10]

    df = build(conn, as_of, fmt)
    print(f"Ban Radar {fmt} au {as_of} — {len(df)} cartes notées "
          f"({df.n_decks_window.iloc[0]} decks sur {WINDOW_MONTHS} mois)")
    print(df.risk_label.value_counts().to_string())
    print()
    print(
        df.head(25)[
            ["card_name", "ban_risk_score", "risk_label", "current_status",
             "deck_share", "mean_copies", "top_archetype"]
        ].to_string(index=False)
    )

    if args.dry_run:
        return

    # La table `ban_radar` est celle que sert l'API, et /ban-radar n'expose pas
    # de notion de format : écrire l'OCG dedans remplacerait silencieusement le
    # classement TCG affiché sur le site.
    if fmt != "TCG":
        raise SystemExit(
            "Le classement OCG ne s'écrit pas en base : la table ban_radar est servie "
            "telle quelle par l'API, qui est TCG. Relance avec --dry-run pour le consulter."
        )

    df.to_sql("ban_radar", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ban_radar_card ON ban_radar(card_name)")
    conn.commit()
    print(f"\nTable ban_radar écrite ({len(df)} lignes)")


if __name__ == "__main__":
    main()
