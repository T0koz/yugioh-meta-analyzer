import sqlite3

from fastapi import APIRouter, Depends

from app.db import get_db
from app.schemas import (
    BoutiqueResponse,
    BoutiqueSignal,
    EarlySignal,
    EarlySignalsResponse,
    SignalLabelRule,
)
from app.signal_label import PROVISIONAL_NOTE, label_cutoffs, signal_label

router = APIRouter(tags=["boutique"])

BOUTIQUE_SIGNALS_LIMIT = 100
EARLY_SIGNALS_LIMIT = 50


@router.get("/boutique/signals", response_model=BoutiqueResponse)
def get_boutique_signals(db: sqlite3.Connection = Depends(get_db)) -> BoutiqueResponse:
    # Pas de filtre ici : la règle « pas encore en TCG » est appliquée à la source
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
        ORDER BY s.buy_score_100 DESC
        LIMIT ?
        """,
        (BOUTIQUE_SIGNALS_LIMIT,),
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

    def label_of(archetype: str):
        score = ocg.get(archetype)
        return signal_label(score, all_scores) if score is not None else None

    data = []
    for row in rows:
        lab = label_of(row["archetype"])
        data.append(
            BoutiqueSignal(
                archetype=row["archetype"],
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
    return BoutiqueResponse(data=data, label_rule=rule)


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
    return EarlySignalsResponse(data=data)
