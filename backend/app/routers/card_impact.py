import sqlite3
from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.schemas import CardImpactEntry, CardImpactResponse
from app.db import get_db

router = APIRouter(tags=["card-impact"])

CARD_IMPACT_LIMIT_DEFAULT = 50


@router.get("/card-impact", response_model=CardImpactResponse)
def get_card_impact(
    limit: int = Query(CARD_IMPACT_LIMIT_DEFAULT, le=200),
    kind: Literal["generic", "archetype"] | None = Query(
        None,
        description="generic = staples sans deck d'attache, archetype = pièces de moteur",
    ),
    db: sqlite3.Connection = Depends(get_db),
) -> CardImpactResponse:
    meta = db.execute("SELECT as_of, n_decks_window FROM card_impact LIMIT 1").fetchone()
    if meta is None:
        return CardImpactResponse(data=[], as_of="", n_decks_window=0)

    rows = db.execute(
        """
        SELECT ci.*, c.image_url_small
        FROM card_impact ci
        -- cards.name porte parfois la notation <C>/<P>/<Q> (ex: "Maliss <P>
        -- March Hare") que card_impact.card_name, dérivé de deck_cards, n'a
        -- jamais — sans le strip, la jointure échoue et l'image manque.
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +ci.card_name -- le « + » désactive l'affinité TEXT : sans lui SQLite n'utilise pas idx_cards_name_clean (TOK-83)
        WHERE (:kind IS NULL
               OR (:kind = 'generic' AND ci.top_archetype IS NULL)
               OR (:kind = 'archetype' AND ci.top_archetype IS NOT NULL))
        ORDER BY ci.bridge_score DESC
        LIMIT :limit
        """,
        {"kind": kind, "limit": limit},
    ).fetchall()

    return CardImpactResponse(
        data=[
            CardImpactEntry(
                card_name=row["card_name"],
                bridge_score=row["bridge_score"],
                n_archetypes=row["n_archetypes"],
                decks=row["decks"],
                top_archetype=row["top_archetype"],
                image_url=row["image_url_small"],
            )
            for row in rows
        ],
        as_of=meta["as_of"],
        n_decks_window=meta["n_decks_window"],
    )
