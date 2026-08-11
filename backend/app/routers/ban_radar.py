import sqlite3

from fastapi import APIRouter, Depends, Query

from app.schemas import BanRadarCriteria, BanRadarEntry, BanRadarResponse
from app.db import get_db

router = APIRouter(tags=["ban-radar"])

BAN_RADAR_LIMIT_DEFAULT = 50

# Doit rester aligné sur WEIGHTS dans scripts/build_ban_radar.py : la table
# ban_radar stocke les critères bruts (0-1), la pondération est réappliquée ici
# pour renvoyer au front la contribution de chaque critère en points de score.
WEIGHTS = {
    "ubiquity": 0.30,
    "carrier": 0.25,
    "copies": 0.20,
    "restriction": 0.10,
    "momentum": 0.10,
    "bridge": 0.05,
}


@router.get("/ban-radar", response_model=BanRadarResponse)
def get_ban_radar(
    limit: int = Query(BAN_RADAR_LIMIT_DEFAULT, le=200),
    min_score: float = Query(0, ge=0, le=100),
    status: str | None = Query(None, description="Filtre sur le statut TCG actuel"),
    db: sqlite3.Connection = Depends(get_db),
) -> BanRadarResponse:
    meta = db.execute("SELECT as_of, n_decks_window FROM ban_radar LIMIT 1").fetchone()
    if meta is None:
        return BanRadarResponse(data=[], as_of="", n_decks_window=0, weights=WEIGHTS)

    rows = db.execute(
        """
        SELECT r.*, c.image_url_small
        FROM ban_radar r
        LEFT JOIN cards c ON c.name = r.card_name
        WHERE r.ban_risk_score >= :min_score
          AND (:status IS NULL OR r.current_status = :status)
        ORDER BY r.ban_risk_score DESC
        LIMIT :limit
        """,
        {"min_score": min_score, "status": status, "limit": limit},
    ).fetchall()

    # Le score final est rééchelonné sur le max du dataset : les contributions
    # brutes x poids sont remises à la même échelle pour qu'elles se somment
    # bien au score affiché.
    data = []
    for row in rows:
        weighted = {key: row[key] * weight for key, weight in WEIGHTS.items()}
        total = sum(weighted.values())
        scale = row["ban_risk_score"] / total if total else 0.0
        data.append(
            BanRadarEntry(
                card_name=row["card_name"],
                ban_risk_score=row["ban_risk_score"],
                risk_label=row["risk_label"],
                current_status=row["current_status"],
                deck_share=row["deck_share"],
                decks=row["decks"],
                n_archetypes=row["n_archetypes"],
                mean_copies=row["mean_copies"],
                top_archetype=row["top_archetype"],
                image_url=row["image_url_small"],
                criteria=BanRadarCriteria(
                    **{key: round(value * scale, 2) for key, value in weighted.items()}
                ),
            )
        )

    return BanRadarResponse(
        data=data,
        as_of=meta["as_of"],
        n_decks_window=meta["n_decks_window"],
        weights=WEIGHTS,
    )
