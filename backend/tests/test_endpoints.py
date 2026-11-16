"""Test de fumée de l'API : chaque endpoint doit répondre 200 sur la base réelle.

Pourquoi : les tables servies sont recalculées chaque lundi (scripts/refresh_all.py).
Un recalcul peut faire apparaître une valeur que le schéma Pydantic n'accepte pas
(ex. TOK-95 : `archetype = NULL` dans early_card_signals → erreur 500 en production
alors que le code n'avait pas bougé). Ce test le voit avant le push.

Lancer depuis backend/ :
    ../.venv/bin/python -m pytest tests -q                                  # yugioh.db
    YGO_DB_PATH=../data/serving.db ../.venv/bin/python -m pytest tests -q   # base de prod
"""

import pytest
from fastapi.testclient import TestClient

from app.db import DB_PATH
from app.main import app

if not DB_PATH.exists():
    pytest.skip(f"Base absente : {DB_PATH}", allow_module_level=True)

client = TestClient(app)

# Requêtes explicites pour les routes qui ont des paramètres obligatoires, et pour
# les variantes de filtre qui passent par du SQL différent.
EXPLICIT_GETS = {
    "/api/v1/cards/search": ["/api/v1/cards/search?q=Ash"],
    "/api/v1/cards/{name}": ["/api/v1/cards/Ash Blossom & Joyous Spring"],
    # Un archétype de la tier list, un nom à barre oblique (signal boutique, absent du TCG).
    "/api/v1/archetypes/{slug}": ["/api/v1/archetypes/branded", "/api/v1/archetypes/harpie-amazoness"],
    "/api/v1/ban-radar": [
        "/api/v1/ban-radar?kind=archetype",
        "/api/v1/ban-radar?kind=generic",
    ],
    "/api/v1/card-impact": [
        "/api/v1/card-impact?kind=archetype",
        "/api/v1/card-impact?kind=generic",
    ],
}


def _get_routes() -> list[tuple[str, bool]]:
    """(chemin, a des paramètres obligatoires) pour chaque GET déclaré dans l'API."""
    routes = []
    for path, ops in app.openapi()["paths"].items():
        op = ops.get("get")
        if op is None:
            continue
        required = any(p.get("required") for p in op.get("parameters", []))
        routes.append((path, required))
    return routes


def _urls_to_check() -> list[str]:
    urls = []
    for path, required in _get_routes():
        if not required:
            urls.append(path)
        urls.extend(EXPLICIT_GETS.get(path, []))
    return urls


def test_every_route_with_required_params_is_covered():
    # Un nouvel endpoint à paramètre obligatoire doit être ajouté à EXPLICIT_GETS,
    # sinon il échapperait au test de fumée sans bruit.
    missing = [p for p, required in _get_routes() if required and p not in EXPLICIT_GETS]
    assert not missing, f"Ajouter ces routes à EXPLICIT_GETS : {missing}"


@pytest.mark.parametrize("url", _urls_to_check())
def test_get_returns_200(url):
    response = client.get(url)
    assert response.status_code == 200, f"{url} → {response.status_code} : {response.text[:300]}"


def test_simulate_ban_returns_200():
    response = client.post("/api/v1/simulate-ban", json={"card_name": "Ash Blossom & Joyous Spring"})
    assert response.status_code == 200, response.text[:300]


def test_unknown_archetype_is_a_404():
    assert client.get("/api/v1/archetypes/archetype-qui-n-existe-pas").status_code == 404


def test_tier_list_slugs_resolve_to_their_archetype():
    # Chaque slug servi par la tier list doit ramener à la page du même archétype.
    for entry in client.get("/api/v1/meta/tier-list").json()["data"]:
        detail = client.get(f"/api/v1/archetypes/{entry['slug']}")
        assert detail.status_code == 200, entry
        assert detail.json()["archetype"] == entry["archetype"]
        assert detail.json()["tcg"]["share"] == entry["share"]
