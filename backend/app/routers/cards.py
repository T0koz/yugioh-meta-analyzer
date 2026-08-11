import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db import get_db
from app.schemas import BanSimRequest, BanSimResult, CommunityImpact, SearchResponse, SearchResult

router = APIRouter(tags=["cards"])

COOCCURRENCE_NEIGHBOR_LIMIT = 30
AFFECTED_ARCHETYPES_LIMIT = 10
SEARCH_MIN_QUERY_LENGTH = 2


def resolve_card_name(db: sqlite3.Connection, query: str) -> str | None:
    exact = db.execute("SELECT name FROM cards WHERE LOWER(name) = LOWER(?)", (query,)).fetchone()
    if exact:
        return exact["name"]
    fuzzy = db.execute(
        "SELECT name FROM cards WHERE LOWER(name) LIKE LOWER(?) ORDER BY LENGTH(name) ASC LIMIT 1",
        (f"%{query}%",),
    ).fetchone()
    return fuzzy["name"] if fuzzy else None


# Enregistré avant /cards/{name} : sinon FastAPI matcherait "search" comme {name}.
@router.get("/cards/search", response_model=SearchResponse)
def search_cards(
    q: str = Query(..., min_length=1),
    limit: int = Query(8, le=25),
    db: sqlite3.Connection = Depends(get_db),
) -> SearchResponse:
    if len(q.strip()) < SEARCH_MIN_QUERY_LENGTH:
        return SearchResponse(data=[])

    rows = db.execute(
        """
        SELECT name, archetype, image_url_small
        FROM cards
        WHERE LOWER(name) LIKE LOWER(?)
        ORDER BY (LOWER(name) LIKE LOWER(?)) DESC, views DESC
        LIMIT ?
        """,
        (f"%{q}%", f"{q}%", limit),
    ).fetchall()

    return SearchResponse(
        data=[
            SearchResult(name=row["name"], archetype=row["archetype"], image_url=row["image_url_small"])
            for row in rows
        ]
    )


@router.get("/cards/{name}")
def get_card(name: str, db: sqlite3.Connection = Depends(get_db)) -> dict:
    resolved = resolve_card_name(db, name)
    if not resolved:
        raise HTTPException(status_code=404, detail="Card not found")
    row = db.execute("SELECT * FROM cards WHERE name = ?", (resolved,)).fetchone()
    return dict(row)


@router.post("/simulate-ban", response_model=BanSimResult)
def simulate_ban(payload: BanSimRequest, db: sqlite3.Connection = Depends(get_db)) -> BanSimResult:
    resolved = resolve_card_name(db, payload.card_name)
    if not resolved:
        raise HTTPException(status_code=404, detail="Card not found")

    image_row = db.execute(
        "SELECT image_url_small FROM cards WHERE name = ?", (resolved,)
    ).fetchone()
    image_url = image_row["image_url_small"] if image_row else None

    metrics = db.execute(
        "SELECT betweenness FROM card_graph_metrics WHERE card_name = ?", (resolved,)
    ).fetchone()
    max_betweenness = db.execute("SELECT MAX(betweenness) FROM card_graph_metrics").fetchone()[0] or 1.0
    betweenness = metrics["betweenness"] if metrics else 0.0
    # Pas de métrique de fragmentation précalculée : approximée par la betweenness
    # normalisée sur le max du dataset (une carte plus "pont" fragmente davantage
    # sa communauté si elle est retirée).
    fragmentation = round(betweenness / max_betweenness, 4) if max_betweenness else 0.0

    impact = db.execute(
        "SELECT bridge_score, top_archetype FROM card_impact WHERE card_name = ?", (resolved,)
    ).fetchone()
    bridge_score = impact["bridge_score"] if impact else 0.0
    top_archetype = impact["top_archetype"] if impact else None

    neighbor_rows = db.execute(
        """
        SELECT card_a, card_b FROM card_cooccurrence
        WHERE card_a = :name OR card_b = :name
        ORDER BY jaccard DESC LIMIT :limit
        """,
        {"name": resolved, "limit": COOCCURRENCE_NEIGHBOR_LIMIT},
    ).fetchall()
    neighbor_names = {row["card_b"] if row["card_a"] == resolved else row["card_a"] for row in neighbor_rows}

    archetypes: set[str] = set()
    if neighbor_names:
        placeholders = ",".join("?" for _ in neighbor_names)
        archetype_rows = db.execute(
            f"SELECT DISTINCT archetype FROM cards WHERE name IN ({placeholders}) AND archetype IS NOT NULL",
            tuple(neighbor_names),
        ).fetchall()
        archetypes = {row["archetype"] for row in archetype_rows}
    if top_archetype:
        archetypes.add(top_archetype)

    community_id = -1
    if top_archetype:
        community_row = db.execute(
            "SELECT community_id FROM graph_communities WHERE top_archetypes LIKE ? LIMIT 1",
            (f"%{top_archetype}%",),
        ).fetchone()
        if community_row:
            community_id = community_row["community_id"]

    return BanSimResult(
        removed_card=resolved,
        image_url=image_url,
        affected_archetypes=sorted(archetypes)[:AFFECTED_ARCHETYPES_LIMIT],
        community_impact=CommunityImpact(community_id=community_id, fragmentation=fragmentation),
        bridge_score=bridge_score or 0.0,
    )
