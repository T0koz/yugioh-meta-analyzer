import sqlite3

from fastapi import APIRouter, Depends

from app.db import get_db
from app.schemas import BoutiqueResponse, BoutiqueSignal, EarlySignal, EarlySignalsResponse

router = APIRouter(tags=["boutique"])

BOUTIQUE_SIGNALS_LIMIT = 100
EARLY_SIGNALS_LIMIT = 50


@router.get("/boutique/signals", response_model=BoutiqueResponse)
def get_boutique_signals(db: sqlite3.Connection = Depends(get_db)) -> BoutiqueResponse:
    rows = db.execute(
        """
        SELECT archetype, card_name, buy_score_100, buy_label, cm_price,
               ban_tcg, tcg_entry_estimated
        FROM boutique_buy_signals
        ORDER BY buy_score_100 DESC
        LIMIT ?
        """,
        (BOUTIQUE_SIGNALS_LIMIT,),
    ).fetchall()

    data = [
        BoutiqueSignal(
            archetype=row["archetype"],
            card_name=row["card_name"],
            buy_score=row["buy_score_100"],
            buy_label=row["buy_label"],
            cm_price=row["cm_price"],
            ban_tcg=row["ban_tcg"],
            tcg_entry_estimated=row["tcg_entry_estimated"],
        )
        for row in rows
    ]
    return BoutiqueResponse(data=data)


@router.get("/early-signals", response_model=EarlySignalsResponse)
def get_early_signals(db: sqlite3.Connection = Depends(get_db)) -> EarlySignalsResponse:
    rows = db.execute(
        """
        SELECT card_name, archetype, early_score, views_week
        FROM early_card_signals
        ORDER BY early_score DESC
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
        )
        for row in rows
    ]
    return EarlySignalsResponse(data=data)
