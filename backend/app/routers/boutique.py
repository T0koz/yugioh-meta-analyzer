import sqlite3

from fastapi import APIRouter, Depends

from app.db import get_db
from app.schemas import (
    BoutiqueResponse,
    BoutiqueSignal,
    EarlySignal,
    EarlySignalsResponse,
    CardPriceHistory,
    PriceGap,
    PriceHistoryResponse,
    PricePoint,
    SignalLabelRule,
)
from app.price_history import MAX_STEP_DAYS, MIN_POINTS, SOURCE, find_gaps, is_sparse
from app.slugs import slugify
from app.signal_label import PROVISIONAL_NOTE, label_cutoffs, signal_label

router = APIRouter(tags=["boutique"])

BOUTIQUE_SIGNALS_LIMIT = 100
EARLY_SIGNALS_LIMIT = 50


def latest_computed_at(db: sqlite3.Connection, table: str) -> str | None:
    """Date du dernier calcul d'une table (pied de données du front, TOK-99).

    `table` est une constante du code, jamais une saisie. Une base sans colonne
    `computed_at` (ancienne copie, base de test) donne None : la page affiche alors
    « date de calcul inconnue » au lieu de casser.
    """
    try:
        return db.execute(f"SELECT MAX(computed_at) FROM {table}").fetchone()[0]
    except sqlite3.OperationalError:
        return None


def load_boutique_signals(
    db: sqlite3.Connection, archetype: str | None = None
) -> tuple[list[BoutiqueSignal], SignalLabelRule | None]:
    """Signaux boutique (tous, ou ceux d'un archétype) avec leur libellé absolu.

    Partagé avec la page d'archétype (routers/archetypes.py) : mêmes libellés,
    même règle, quel que soit l'endroit où le signal est affiché.
    """
    # Pas de filtre « déjà en TCG » ici : la règle est appliquée à la source
    # (notebook 10, TOK-113), sur les cartes inédites et non sur le nom de
    # l'archétype. L'ancien filtre par nom (TOK-97) faisait double emploi.
    rows = db.execute(
        """
        SELECT s.archetype, s.card_name, s.buy_score_100, s.cm_price, s.ban_tcg,
               s.tcg_window_start, s.tcg_window_end, c.image_url_small
        FROM boutique_buy_signals s
        -- Même jointure que le Ban Radar (TOK-83) : expression indexée, et `+` pour
        -- neutraliser l'affinité TEXT, sinon SQLite ignore idx_cards_name_clean.
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +s.card_name
        WHERE :archetype IS NULL OR s.archetype = :archetype
        ORDER BY s.buy_score_100 DESC
        LIMIT :limit
        """,
        {"archetype": archetype, "limit": BOUTIQUE_SIGNALS_LIMIT},
    ).fetchall()

    # Force OCG de tous les archétypes : référence stable du libellé. Table absente
    # (base de service construite avant ce changement) : on rend les signaux sans libellé.
    try:
        ocg = {
            r["archetype"]: r["ocg_score"]
            for r in db.execute("SELECT archetype, ocg_score FROM ocg_archetype_scores")
        }
    except sqlite3.OperationalError:
        ocg = {}
    all_scores = list(ocg.values())

    def label_of(name: str):
        score = ocg.get(name)
        return signal_label(score, all_scores) if score is not None else None

    data = []
    for row in rows:
        lab = label_of(row["archetype"])
        data.append(
            BoutiqueSignal(
                archetype=row["archetype"],
                archetype_slug=slugify(row["archetype"]),
                card_name=row["card_name"],
                buy_score=row["buy_score_100"],
                signal_label=lab.label if lab else None,
                archetype_rank=lab.rank if lab else None,
                cm_price=row["cm_price"],
                ban_tcg=row["ban_tcg"],
                image_url=row["image_url_small"],
                tcg_window_start=row["tcg_window_start"],
                tcg_window_end=row["tcg_window_end"],
            )
        )
    rule = None
    if all_scores and any(d.signal_label for d in data):
        strong, moderate = label_cutoffs(len(all_scores))
        rule = SignalLabelRule(
            population=len(all_scores),
            strong_max_rank=strong,
            moderate_max_rank=moderate,
            note=PROVISIONAL_NOTE,
        )
    return data, rule


@router.get("/boutique/signals", response_model=BoutiqueResponse)
def get_boutique_signals(db: sqlite3.Connection = Depends(get_db)) -> BoutiqueResponse:
    data, rule = load_boutique_signals(db)
    computed_at = latest_computed_at(db, "boutique_buy_signals")
    return BoutiqueResponse(data=data, label_rule=rule, computed_at=computed_at)


@router.get("/boutique/prices", response_model=PriceHistoryResponse)
def get_boutique_prices(db: sqlite3.Connection = Depends(get_db)) -> PriceHistoryResponse:
    """Relevés de prix Cardmarket des cartes du signal boutique (TOK-103).

    Table absente (base construite avant TOK-103) : réponse vide, la page
    affiche les signaux sans courbe au lieu de casser.
    """
    try:
        rows = db.execute(
            """
            SELECT card_name, snapshot_date, cardmarket_price
            FROM boutique_price_history
            ORDER BY card_name, snapshot_date
            """
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []

    by_card: dict[str, list[PricePoint]] = {}
    for row in rows:
        by_card.setdefault(row["card_name"], []).append(
            PricePoint(date=row["snapshot_date"], price=row["cardmarket_price"])
        )

    cards = []
    for name, points in by_card.items():
        gaps = find_gaps([p.date for p in points])
        cards.append(
            CardPriceHistory(
                card_name=name,
                points=points,
                gaps=[PriceGap(start=s, end=e, days=d) for s, e, d in gaps],
                sparse=is_sparse(len(points)),
            )
        )

    dates = sorted({row["snapshot_date"] for row in rows})
    return PriceHistoryResponse(
        cards=cards,
        period_start=dates[0] if dates else None,
        period_end=dates[-1] if dates else None,
        snapshot_count=len(dates),
        max_step_days=MAX_STEP_DAYS,
        min_points=MIN_POINTS,
        source=SOURCE,
        computed_at=latest_computed_at(db, "boutique_price_history") if rows else None,
    )


@router.get("/early-signals", response_model=EarlySignalsResponse)
def get_early_signals(db: sqlite3.Connection = Depends(get_db)) -> EarlySignalsResponse:
    rows = db.execute(
        """
        SELECT s.card_name, s.archetype, s.early_score, s.views_week, c.image_url_small
        FROM early_card_signals s
        -- Même jointure que le Ban Radar (TOK-83) : expression indexée, et `+` pour
        -- neutraliser l'affinité TEXT, sinon SQLite ignore idx_cards_name_clean.
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +s.card_name
        ORDER BY s.early_score DESC
        LIMIT ?
        """,
        (EARLY_SIGNALS_LIMIT,),
    ).fetchall()

    data = [
        EarlySignal(
            card_name=row["card_name"],
            archetype=row["archetype"],
            early_score=row["early_score"],
            views_week=row["views_week"],
            image_url=row["image_url_small"],
        )
        for row in rows
    ]
    computed_at = latest_computed_at(db, "early_card_signals")
    cards_scored, text_signal_cards = db.execute(
        "SELECT COUNT(*), SUM(signal_text > 0) FROM early_card_signals"
    ).fetchone()
    try:
        as_of = db.execute("SELECT MAX(as_of) FROM early_card_signals").fetchone()[0]
    except sqlite3.OperationalError:  # table calculée avant le lot 20 (notebook 11) : pas de date de référence
        as_of = None
    return EarlySignalsResponse(
        data=data,
        computed_at=computed_at,
        as_of=as_of,
        cards_scored=cards_scored,
        text_signal_cards=text_signal_cards or 0,
    )
