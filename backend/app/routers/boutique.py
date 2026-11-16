import sqlite3

from fastapi import APIRouter, Depends

from app.db import get_db
from app.schemas import BoutiqueResponse, BoutiqueSignal, EarlySignal, EarlySignalsResponse

router = APIRouter(tags=["boutique"])

BOUTIQUE_SIGNALS_LIMIT = 100
# Un archétype qui cumule au moins ce nombre de decks TCG légaux sur 12 mois est
# déjà arrivé en TCG : ce n'est plus un signal « avant le TCG » (TOK-97). Le
# résultat est le même pour un seuil de 1, 5 ou 10 ; 5 évite qu'un deck isolé suffise.
TCG_PRESENCE_MIN_DECKS = 5
EARLY_SIGNALS_LIMIT = 50


@router.get("/boutique/signals", response_model=BoutiqueResponse)
def get_boutique_signals(db: sqlite3.Connection = Depends(get_db)) -> BoutiqueResponse:
    # `tcg_entry_estimated` n'est pas servi : le notebook 10 y écrit « date du
    # calcul + 4 mois », la même constante pour toutes les lignes.
    rows = db.execute(
        """
        WITH tcg_present AS (
            SELECT archetype
            FROM meta_scores
            WHERE month >= strftime('%Y-%m', (SELECT MAX(month) FROM meta_scores) || '-01', '-11 months')
            GROUP BY archetype
            HAVING SUM(deck_count) >= :min_decks
        )
        SELECT s.archetype, s.card_name, s.buy_score_100, s.buy_label, s.cm_price, s.ban_tcg,
               c.image_url_small
        FROM boutique_buy_signals s
        -- Même jointure que le Ban Radar (TOK-83) : expression indexée, et `+` pour
        -- neutraliser l'affinité TEXT, sinon SQLite ignore idx_cards_name_clean.
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +s.card_name
        WHERE NOT EXISTS (SELECT 1 FROM tcg_present p WHERE p.archetype = s.archetype)
        ORDER BY s.buy_score_100 DESC
        LIMIT :limit
        """,
        {"min_decks": TCG_PRESENCE_MIN_DECKS, "limit": BOUTIQUE_SIGNALS_LIMIT},
    ).fetchall()

    data = [
        BoutiqueSignal(
            archetype=row["archetype"],
            card_name=row["card_name"],
            buy_score=row["buy_score_100"],
            buy_label=row["buy_label"],
            cm_price=row["cm_price"],
            ban_tcg=row["ban_tcg"],
            image_url=row["image_url_small"],
        )
        for row in rows
    ]
    return BoutiqueResponse(data=data)


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
