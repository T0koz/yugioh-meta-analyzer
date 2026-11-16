import sqlite3

from fastapi import APIRouter, Depends

from app.db import get_db
from app.labels import map_pred_direction
from app.schemas import (
    EvolutionPoint,
    EvolutionResponse,
    PredictionEntry,
    PredictionsResponse,
    TierEntry,
    TierListResponse,
)
from app.tiering import MIN_WINDOW_DECKS, meta_score_for, tier_for, trend_for

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
    # Les noms d'archétype de yugiohmeta en mélangent parfois deux (ex: "Ryzeal
    # Mitsurugi") sans entrée correspondante dans cards.archetype : on retombe sur
    # le plus long archétype connu contenu dans ce nom composé. La comparaison se
    # fait par mots entiers, sinon « Ashtra » prend l'image de l'archétype « Ra ».
    row = db.execute(
        """
        SELECT image_url_small FROM cards
        WHERE archetype IS NOT NULL AND image_url_small IS NOT NULL
          AND ' ' || ? || ' ' LIKE '% ' || archetype || ' %'
        ORDER BY LENGTH(archetype) DESC, views DESC LIMIT 1
        """,
        (archetype,),
    ).fetchone()
    return row["image_url_small"] if row else None


# Fenêtre courante = mois les plus récents cumulés jusqu'à `min` decks ; fenêtre
# précédente = même règle, juste avant (sert à la tendance).
TIER_LIST_SQL = """
WITH months AS (
    SELECT month, MAX(total_decks) AS n,
           SUM(MAX(total_decks)) OVER (ORDER BY month DESC) AS cum
    FROM meta_scores GROUP BY month
),
cur AS (
    SELECT month, n FROM months WHERE cum - n < :min
),
prev AS (
    SELECT month, n FROM (
        SELECT month, n, SUM(n) OVER (ORDER BY month DESC) AS cum2
        FROM months WHERE month < (SELECT MIN(month) FROM cur)
    ) WHERE cum2 - n < :min
),
a AS (
    SELECT archetype, SUM(deck_count) AS decks,
           SUM(deck_count * avg_placement) * 1.0 / SUM(deck_count) AS avg_placement
    FROM meta_scores WHERE month IN (SELECT month FROM cur) GROUP BY archetype
),
p AS (
    SELECT archetype, SUM(deck_count) AS decks_prev
    FROM meta_scores WHERE month IN (SELECT month FROM prev) GROUP BY archetype
)
SELECT a.archetype, a.decks, a.avg_placement,
       COALESCE(p.decks_prev, 0) AS decks_prev,
       (SELECT SUM(n) FROM cur) AS n_cur,
       COALESCE((SELECT SUM(n) FROM prev), 0) AS n_prev,
       (SELECT MIN(month) FROM cur) AS window_start,
       (SELECT MAX(month) FROM cur) AS window_end
FROM a LEFT JOIN p ON p.archetype = a.archetype
ORDER BY a.decks DESC, a.avg_placement ASC
"""


@router.get("/tier-list", response_model=TierListResponse)
def get_tier_list(db: sqlite3.Connection = Depends(get_db)) -> TierListResponse:
    """Tier list recalculée depuis `meta_scores` (TOK-91), règles dans app/tiering.py."""
    rows = db.execute(TIER_LIST_SQL, {"min": MIN_WINDOW_DECKS}).fetchall()
    if not rows:
        return TierListResponse(data=[], window_start="", window_end="", n_decks=0)

    n_cur, n_prev = rows[0]["n_cur"], rows[0]["n_prev"]
    best_placement_score = max(1 / row["avg_placement"] for row in rows if row["avg_placement"] > 0)

    data = []
    for row in rows:
        share = row["decks"] / n_cur
        data.append(
            TierEntry(
                archetype=row["archetype"],
                tier=tier_for(share, row["decks"]),
                meta_score=meta_score_for(share, row["avg_placement"], best_placement_score),
                share=share,
                trend=trend_for(row["decks"], n_cur, row["decks_prev"], n_prev),
                image_url=get_archetype_image(db, row["archetype"]),
            )
        )
    return TierListResponse(
        data=data, window_start=rows[0]["window_start"], window_end=rows[0]["window_end"], n_decks=n_cur
    )


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
    images = {a: url for a in top_archetypes if (url := get_archetype_image(db, a))}
    decks_by_month = {
        row["month"]: row["n"]
        for row in db.execute("SELECT month, MAX(total_decks) AS n FROM meta_scores GROUP BY month")
    }
    return EvolutionResponse(data=data, images=images, decks_by_month=decks_by_month)


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
            image_url=get_archetype_image(db, row["archetype"]),
        )
        for row in rows
    ]
    try:
        computed_at = db.execute(
            "SELECT MAX(computed_at) FROM meta_predictions WHERE data_month = ?", (latest_month,)
        ).fetchone()[0]
    except sqlite3.OperationalError:  # base sans colonne computed_at : le front écrit « date inconnue »
        computed_at = None
    return PredictionsResponse(
        data=data, model="70 % naïf + 30 % Ridge", data_month=latest_month, computed_at=computed_at
    )
