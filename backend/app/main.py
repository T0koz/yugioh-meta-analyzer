from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import boutique, cards, graph, meta

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


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
