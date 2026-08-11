import sqlite3

from fastapi import APIRouter, Depends, Query

from app.db import get_db
from app.schemas import GraphEdge, GraphNode, GraphResponse

router = APIRouter(prefix="/graph", tags=["graph"])

NODE_LIMIT_DEFAULT = 150
MIN_JACCARD_DEFAULT = 0.15


@router.get("/synergies", response_model=GraphResponse)
def get_synergies(
    limit: int = Query(NODE_LIMIT_DEFAULT, le=500),
    min_jaccard: float = Query(MIN_JACCARD_DEFAULT, ge=0, le=1),
    db: sqlite3.Connection = Depends(get_db),
) -> GraphResponse:
    node_rows = db.execute(
        """
        SELECT g.card_name, g.degree_weighted, c.archetype
        FROM card_graph_metrics g
        LEFT JOIN cards c ON c.name = g.card_name
        ORDER BY g.degree_weighted DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    node_names = [row["card_name"] for row in node_rows]
    nodes = [
        GraphNode(id=row["card_name"], group=row["archetype"], size=row["degree_weighted"])
        for row in node_rows
    ]

    if not node_names:
        return GraphResponse(nodes=[], edges=[])

    placeholders = ",".join("?" for _ in node_names)
    params = [*node_names, *node_names, min_jaccard]
    edge_rows = db.execute(
        f"""
        SELECT card_a, card_b, jaccard
        FROM card_cooccurrence
        WHERE card_a IN ({placeholders}) AND card_b IN ({placeholders}) AND jaccard >= ?
        """,
        params,
    ).fetchall()

    edges = [
        GraphEdge(source=row["card_a"], target=row["card_b"], weight=row["jaccard"])
        for row in edge_rows
    ]
    return GraphResponse(nodes=nodes, edges=edges)
