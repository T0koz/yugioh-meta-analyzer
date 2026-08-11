import sqlite3

from fastapi import APIRouter, Depends

from app.db import get_db
from app.labels import map_pred_direction, map_tier, map_trend_label
from app.schemas import (
    EvolutionPoint,
    EvolutionResponse,
    PredictionEntry,
    PredictionsResponse,
    TierEntry,
    TierListResponse,
)

router = APIRouter(prefix="/meta", tags=["meta"])

# Nombre d'archétypes retenus dans /meta/evolution : le front affiche des
# boutons de sélection par archétype, un payload avec les 122 archétypes
# de meta_scores serait inexploitable dans l'UI.
EVOLUTION_ARCHETYPE_LIMIT = 15


def get_archetype_image(db: sqlite3.Connection, archetype: str) -> str | None:
    row = db.execute(
        """
        SELECT image_url_small FROM cards
        WHERE archetype = ? AND image_url_small IS NOT NULL
        ORDER BY views DESC LIMIT 1
        """,
        (archetype,),
    ).fetchone()
    if row:
        return row["image_url_small"]
    # meta_tier_list mélange parfois deux archétypes dans un même nom (ex: "Ryzeal
    # Mitsurugi") sans entrée correspondante dans cards.archetype : on retombe sur
    # le premier archétype connu contenu dans ce nom composé.
    row = db.execute(
        """
        SELECT image_url_small FROM cards
        WHERE archetype IS NOT NULL AND image_url_small IS NOT NULL AND ? LIKE '%' || archetype || '%'
        ORDER BY LENGTH(archetype) DESC, views DESC LIMIT 1
        """,
        (archetype,),
    ).fetchone()
    return row["image_url_small"] if row else None


@router.get("/tier-list", response_model=TierListResponse)
def get_tier_list(db: sqlite3.Connection = Depends(get_db)) -> TierListResponse:
    latest = db.execute(
        "SELECT MAX(scraped_at) FROM meta_tier_list WHERE format = 'TCG'"
    ).fetchone()[0]

    rows = db.execute(
        """
        SELECT m.archetype, m.tier, m.share_pct,
               t.meta_score_recent, t.trend_label
        FROM meta_tier_list m
        LEFT JOIN archetype_trend t ON t.archetype = m.archetype
        WHERE m.format = 'TCG' AND m.scraped_at = ?
        ORDER BY m.share_pct DESC
        """,
        (latest,),
    ).fetchall()

    data = [
        TierEntry(
            archetype=row["archetype"],
            tier=map_tier(row["tier"]),
            meta_score=row["meta_score_recent"] if row["meta_score_recent"] is not None else row["share_pct"] / 100,
            share=row["share_pct"] / 100,
            trend=map_trend_label(row["trend_label"]),
            image_url=get_archetype_image(db, row["archetype"]),
        )
        for row in rows
    ]
    return TierListResponse(data=data, generated_at=latest)


@router.get("/evolution", response_model=EvolutionResponse)
def get_evolution(db: sqlite3.Connection = Depends(get_db)) -> EvolutionResponse:
    latest_month = db.execute("SELECT MAX(month) FROM meta_scores").fetchone()[0]
    top_archetypes = [
        row["archetype"]
        for row in db.execute(
            """
            SELECT archetype, meta_score
            FROM meta_scores
            WHERE month = ?
            ORDER BY meta_score DESC
            LIMIT ?
            """,
            (latest_month, EVOLUTION_ARCHETYPE_LIMIT),
        ).fetchall()
    ]
    if not top_archetypes:
        return EvolutionResponse(data={})

    placeholders = ",".join("?" for _ in top_archetypes)
    rows = db.execute(
        f"""
        SELECT archetype, month, meta_score, share
        FROM meta_scores
        WHERE archetype IN ({placeholders})
        ORDER BY archetype, month
        """,
        top_archetypes,
    ).fetchall()

    data: dict[str, list[EvolutionPoint]] = {a: [] for a in top_archetypes}
    for row in rows:
        data[row["archetype"]].append(
            EvolutionPoint(month=row["month"], meta_score=row["meta_score"], share=row["share"])
        )
    return EvolutionResponse(data=data)


@router.get("/predictions", response_model=PredictionsResponse)
def get_predictions(db: sqlite3.Connection = Depends(get_db)) -> PredictionsResponse:
    latest_month = db.execute("SELECT MAX(data_month) FROM meta_predictions").fetchone()[0]
    rows = db.execute(
        """
        SELECT archetype, meta_score_current, pred_meta_score, pred_direction
        FROM meta_predictions
        WHERE data_month = ?
        ORDER BY pred_meta_score DESC
        """,
        (latest_month,),
    ).fetchall()

    data = [
        PredictionEntry(
            archetype=row["archetype"],
            current=row["meta_score_current"],
            predicted=row["pred_meta_score"],
            direction=map_pred_direction(row["pred_direction"]),
        )
        for row in rows
    ]
    return PredictionsResponse(data=data, model="Ridge + Naïf blend (ρ≈+0.65)")
