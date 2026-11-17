from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import archetypes, ban_radar, boutique, card_impact, cards, decks, graph, meta

app = FastAPI(title="YGO Meta Analyzer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(meta.router, prefix=API_PREFIX)
app.include_router(boutique.router, prefix=API_PREFIX)
app.include_router(graph.router, prefix=API_PREFIX)
app.include_router(cards.router, prefix=API_PREFIX)
app.include_router(ban_radar.router, prefix=API_PREFIX)
app.include_router(card_impact.router, prefix=API_PREFIX)
app.include_router(archetypes.router, prefix=API_PREFIX)
app.include_router(decks.router, prefix=API_PREFIX)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
