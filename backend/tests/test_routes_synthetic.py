"""Comportement des routes sur une base synthétique (TOK-135) : filtres, tri, bornes, réponses vides, 404.

Le test de fumée (`test_endpoints.py`) vérifie que chaque route répond 200 sur la base réelle ; ici, on vérifie ce
qu'elle renvoie, sur des tables construites en mémoire, sans `yugioh.db` ni `serving.db`.
"""

import sqlite3
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from app.db import get_db
from app.labels import PRED_GAP_THRESHOLD
from app.main import app
from app.routers.ban_radar import WEIGHTS

CRITERIA = list(WEIGHTS)

CARDS = [
    # name, archetype, views, image_url_small
    ("Ash Blossom & Joyous Spring", None, 900, "https://img/1.jpg"),
    ("Ashened City", "Ashened", 50, "https://img/2.jpg"),
    ("Maliss <P> March Hare", "Maliss", 300, "https://img/3.jpg"),
    ("Branded Fusion", "Branded", 800, "https://img/4.jpg"),
]

# card_name, score, status, top_archetype, criteria (0-1, dans l'ordre de WEIGHTS)
RADAR = [
    ("Ash Blossom & Joyous Spring", 80.0, "Unlimited", None, [1.0, 0.2, 1.0, 0.0, 0.5, 0.3]),
    ("Branded Fusion", 60.0, "Limited", "Branded", [0.5, 0.9, 0.0, 1.0, 0.2, 0.1]),
    ("Maliss P March Hare", 30.0, "Unlimited", "Maliss", [0.2, 0.8, 0.5, 0.0, 0.1, 0.0]),
    ("Carte nulle", 0.0, "Semi-Limited", None, [0.0] * 6),
]


def _base() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE cards (name TEXT, archetype TEXT, views INTEGER, image_url_small TEXT)")
    con.executemany("INSERT INTO cards VALUES (?, ?, ?, ?)", CARDS)
    return con


def _with_radar(con: sqlite3.Connection) -> None:
    con.execute(
        f"""CREATE TABLE ban_radar (card_name TEXT, {", ".join(f"{c} REAL" for c in CRITERIA)},
            ban_risk_score REAL, risk_label TEXT, current_status TEXT, decks INTEGER, deck_share REAL,
            n_archetypes INTEGER, mean_copies REAL, top_archetype TEXT, as_of TEXT, n_decks_window INTEGER)"""
    )
    for name, score, status, top, crit in RADAR:
        con.execute(
            f"INSERT INTO ban_radar VALUES (?, {', '.join('?' * len(CRITERIA))}, ?, 'Modéré', ?, 10, 1.5, 2, 2.0, ?, "
            "'2026-11-14', 1883)",
            (name, *crit, score, status, top),
        )
    con.execute(
        """CREATE TABLE card_impact (card_name TEXT, decks INTEGER, n_archetypes INTEGER, top_archetype TEXT,
            archetype_concentration REAL, as_of TEXT, n_decks_window INTEGER, bridge_score REAL)"""
    )
    con.executemany(
        "INSERT INTO card_impact VALUES (?, 10, ?, ?, 0.5, '2026-11-14', 1883, ?)",
        [("Ash Blossom & Joyous Spring", 9, None, 20.0), ("Branded Fusion", 2, "Branded", 5.0),
         ("Maliss P March Hare", 1, "Maliss", 1.0)],
    )


@contextmanager
def _client(con: sqlite3.Connection):
    app.dependency_overrides[get_db] = lambda: con
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        con.close()


@pytest.fixture
def radar_client():
    con = _base()
    _with_radar(con)
    with _client(con) as client:
        yield client


# ── /ban-radar ───────────────────────────────────────────────────────────────


def test_ban_radar_sorted_by_score_and_limited(radar_client):
    body = radar_client.get("/api/v1/ban-radar?limit=2").json()
    assert [e["card_name"] for e in body["data"]] == ["Ash Blossom & Joyous Spring", "Branded Fusion"]
    assert (body["as_of"], body["n_decks_window"]) == ("2026-11-14", 1883)
    assert body["weights"] == WEIGHTS


def test_ban_radar_filters_by_score_status_and_kind(radar_client):
    names = lambda q: [e["card_name"] for e in radar_client.get(f"/api/v1/ban-radar?{q}").json()["data"]]  # noqa: E731
    assert names("min_score=50") == ["Ash Blossom & Joyous Spring", "Branded Fusion"]
    assert names("status=Limited") == ["Branded Fusion"]
    # generic = sans archétype porteur (top_archetype NULL), archetype = le reste ; le filtre est en SQL.
    assert names("kind=generic") == ["Ash Blossom & Joyous Spring", "Carte nulle"]
    assert names("kind=archetype&limit=1") == ["Branded Fusion"]


def test_ban_radar_criteria_sum_to_the_displayed_score(radar_client):
    for entry in radar_client.get("/api/v1/ban-radar").json()["data"]:
        total = sum(entry["criteria"].values())
        # Arrondi à 2 décimales par critère : 6 critères, écart ≤ 0,03.
        assert total == pytest.approx(entry["ban_risk_score"], abs=0.03), entry
        # Part de chaque critère proportionnelle à valeur × poids.
        if entry["ban_risk_score"]:
            assert all(v >= 0 for v in entry["criteria"].values())


def test_ban_radar_joins_images_through_the_cleaned_card_name(radar_client):
    images = {e["card_name"]: e["image_url"] for e in radar_client.get("/api/v1/ban-radar").json()["data"]}
    # « Maliss <P> March Hare » dans cards, « Maliss P March Hare » dans les decks.
    assert images["Maliss P March Hare"] == "https://img/3.jpg"
    assert images["Carte nulle"] is None


@pytest.mark.parametrize("query", ["limit=201", "min_score=101", "min_score=-1", "kind=autre"])
def test_ban_radar_rejects_out_of_range_parameters(radar_client, query):
    assert radar_client.get(f"/api/v1/ban-radar?{query}").status_code == 422


def test_ban_radar_on_an_empty_table_is_an_empty_answer():
    con = _base()
    _with_radar(con)
    con.execute("DELETE FROM ban_radar")
    with _client(con) as client:
        body = client.get("/api/v1/ban-radar").json()
    assert body["data"] == [] and body["n_decks_window"] == 0 and body["weights"] == WEIGHTS


def test_ban_history_without_its_tables_is_an_empty_answer():
    with _client(_base()) as client:
        body = client.get("/api/v1/ban-radar/history").json()
    assert body["lists"] == [] and body["top_n"] == 0


# ── /card-impact ─────────────────────────────────────────────────────────────


def test_card_impact_sorted_and_filtered_by_kind(radar_client):
    body = radar_client.get("/api/v1/card-impact").json()
    assert [e["bridge_score"] for e in body["data"]] == [20.0, 5.0, 1.0]
    generic = radar_client.get("/api/v1/card-impact?kind=generic").json()["data"]
    assert [e["card_name"] for e in generic] == ["Ash Blossom & Joyous Spring"]
    engine = radar_client.get("/api/v1/card-impact?kind=archetype&limit=1").json()["data"]
    assert [e["card_name"] for e in engine] == ["Branded Fusion"]
    assert radar_client.get("/api/v1/card-impact?limit=201").status_code == 422


# ── /graph/synergies ─────────────────────────────────────────────────────────


@pytest.fixture
def graph_client():
    con = _base()
    con.executescript(
        """
        CREATE TABLE card_graph_metrics (card_name TEXT, betweenness REAL, degree_centrality REAL, closeness REAL,
            degree_weighted REAL);
        INSERT INTO card_graph_metrics VALUES ('A', 0.1, 0, 0, 3.0), ('B', 0.2, 0, 0, 2.0), ('C', 0.0, 0, 0, 1.0);
        CREATE TABLE card_cooccurrence (card_a TEXT, card_b TEXT, jaccard REAL, cooc_count INTEGER);
        INSERT INTO card_cooccurrence VALUES ('A', 'B', 0.5, 10), ('A', 'C', 0.9, 10), ('B', 'C', 0.1, 10);
        """
    )
    with _client(con) as client:
        yield client


def test_graph_keeps_the_strongest_nodes_and_only_their_edges(graph_client):
    body = graph_client.get("/api/v1/graph/synergies?limit=2&min_jaccard=0").json()
    assert [n["id"] for n in body["nodes"]] == ["A", "B"]
    # A–C a le plus fort Jaccard mais C n'est pas renvoyé : arête absente.
    assert body["edges"] == [{"source": "A", "target": "B", "weight": 0.5}]


def test_graph_drops_edges_under_the_jaccard_threshold(graph_client):
    body = graph_client.get("/api/v1/graph/synergies?limit=3&min_jaccard=0.5").json()
    assert {(e["source"], e["target"]) for e in body["edges"]} == {("A", "B"), ("A", "C")}
    assert graph_client.get("/api/v1/graph/synergies?min_jaccard=1.5").status_code == 422
    assert graph_client.get("/api/v1/graph/synergies?limit=501").status_code == 422


# ── /cards ───────────────────────────────────────────────────────────────────


@pytest.fixture
def cards_client():
    with _client(_base()) as client:
        yield client


def test_search_ignores_one_character_queries(cards_client):
    assert cards_client.get("/api/v1/cards/search?q=A").json() == {"data": []}
    assert cards_client.get("/api/v1/cards/search?q=%20A%20").json() == {"data": []}
    assert cards_client.get("/api/v1/cards/search").status_code == 422
    assert cards_client.get("/api/v1/cards/search?q=as&limit=26").status_code == 422


def test_search_puts_prefix_matches_first_then_popular_cards(cards_client):
    names = [r["name"] for r in cards_client.get("/api/v1/cards/search?q=as").json()["data"]]
    # Les deux commencent par « As » : la plus vue d'abord ; aucune autre carte ne contient « as ».
    assert names == ["Ash Blossom & Joyous Spring", "Ashened City"]
    names = [r["name"] for r in cards_client.get("/api/v1/cards/search?q=fus").json()["data"]]
    assert names == ["Branded Fusion"]


def test_search_respects_the_limit(cards_client):
    assert len(cards_client.get("/api/v1/cards/search?q=as&limit=1").json()["data"]) == 1


@pytest.mark.xfail(
    reason="Bug signalé (TOK-135) : `q` est injecté tel quel dans un motif LIKE, « % » et « _ » n'y sont pas "
    "échappés. Une recherche « %% » renvoie toutes les cartes au lieu d'aucune (aucun nom ne contient « %% »). "
    "Même cause dans resolve_card_name : /cards/%25 rend une carte au lieu d'un 404.",
    strict=False,
)
def test_search_treats_like_wildcards_as_plain_characters(cards_client):
    assert cards_client.get("/api/v1/cards/search?q=%25%25").json() == {"data": []}


def test_card_lookup_is_case_insensitive_and_404_when_unknown(cards_client):
    body = cards_client.get("/api/v1/cards/branded fusion").json()
    assert body["name"] == "Branded Fusion" and body["archetype"] == "Branded"
    assert cards_client.get("/api/v1/cards/Carte qui n existe pas").status_code == 404


def test_simulate_ban_of_an_unknown_card_is_a_404(cards_client):
    response = cards_client.post("/api/v1/simulate-ban", json={"card_name": "Carte qui n existe pas"})
    assert response.status_code == 404
    assert cards_client.post("/api/v1/simulate-ban", json={}).status_code == 422


def _with_graph(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE card_graph_metrics (card_name TEXT, betweenness REAL);
        INSERT INTO card_graph_metrics VALUES ('Maliss <P> March Hare', 0.2), ('Branded Fusion', 0.4);
        CREATE TABLE card_cooccurrence (card_a TEXT, card_b TEXT, jaccard REAL);
        INSERT INTO card_cooccurrence VALUES ('Maliss <P> March Hare', 'Ashened City', 0.5);
        CREATE TABLE graph_communities (community_id INTEGER, top_archetypes TEXT);
        INSERT INTO graph_communities VALUES (3, 'Maliss, Ashened');
        """
    )


def _with_profile(con: sqlite3.Connection) -> None:
    con.execute(
        """CREATE TABLE archetype_card_profile (archetype TEXT, zone TEXT, card_name TEXT, n_lists INTEGER,
            n_decks INTEGER, share REAL, median_copies REAL, window_start TEXT, window_end TEXT,
            n_decks_window INTEGER, computed_at TEXT)"""
    )
    con.executemany(
        "INSERT INTO archetype_card_profile VALUES (?, ?, ?, ?, ?, 0, 3, '2026-10', '2026-11', 396, '2026-11-16')",
        [
            # Noms de deck_cards : sans les marques <P> de cards.name.
            ("Maliss", "main", "Maliss P March Hare", 9, 9),
            ("Maliss", "side", "Maliss P March Hare", 2, 9),  # Side Deck : pas compté
            ("Live☆Twin", "main", "Maliss P March Hare", 3, 12),
            ("Branded", "main", "Maliss P March Hare", 3, 40),
            ("Branded", "main", "Branded Fusion", 40, 40),
        ],
    )


def test_simulate_ban_lists_the_deck_archetypes_that_play_the_card():
    con = _base()
    _with_radar(con)
    _with_graph(con)
    _with_profile(con)
    with _client(con) as client:
        body = client.post("/api/v1/simulate-ban", json={"card_name": "Maliss <P> March Hare"}).json()
    assert body["removed_card"] == "Maliss <P> March Hare"
    # Tri : listes qui jouent la carte, puis taille de l'archétype ; effectif (k sur n) et slug servis.
    assert body["deck_archetypes"] == [
        {"archetype": "Maliss", "slug": "maliss", "lists": 9, "decks": 9},
        {"archetype": "Branded", "slug": "branded", "lists": 3, "decks": 40},
        {"archetype": "Live☆Twin", "slug": "live-twin", "lists": 3, "decks": 12},
    ]
    assert (body["deck_window_start"], body["deck_window_end"], body["deck_window_decks"]) == ("2026-10", "2026-11", 396)
    # Champ historique conservé (additif seulement), plus affiché par le front.
    assert isinstance(body["affected_archetypes"], list)


def test_simulate_ban_without_profile_table_serves_no_deck_archetype():
    con = _base()
    _with_radar(con)
    _with_graph(con)
    with _client(con) as client:
        body = client.post("/api/v1/simulate-ban", json={"card_name": "Ash Blossom & Joyous Spring"}).json()
    assert body["deck_archetypes"] == [] and body["deck_window_decks"] is None


# ── /meta/predictions ────────────────────────────────────────────────────────


def test_predictions_serve_the_latest_month_with_the_drawn_direction():
    con = _base()
    con.executescript(
        """
        CREATE TABLE meta_predictions (archetype TEXT, data_month TEXT, meta_score_current REAL, pred_delta REAL,
            pred_meta_score REAL, pred_direction TEXT, computed_at TEXT);
        INSERT INTO meta_predictions VALUES
            ('Ancien', '2026-09', 0.10, 0, 0.20, '↑', '2026-10-01'),
            ('Monte', '2026-10', 0.100, 0.02, 0.104, '↑', '2026-11-16'),
            ('Stable', '2026-10', 0.100, 0.01, 0.103, '↑', '2026-11-16'),
            ('Baisse', '2026-10', 0.100, -0.02, 0.096, '↓', '2026-11-16');
        """
    )
    with _client(con) as client:
        body = client.get("/api/v1/meta/predictions").json()
    assert body["data_month"] == "2026-10" and body["computed_at"] == "2026-11-16"
    directions = {e["archetype"]: e["direction"] for e in body["data"]}
    # Seuil sur l'écart dessiné (prévu − observé) : +0,004 > 0,003, +0,003 n'est pas au-dessus.
    assert directions == {"Monte": "Rising", "Stable": "Stable", "Baisse": "Declining"}
    assert [e["predicted"] for e in body["data"]] == sorted((e["predicted"] for e in body["data"]), reverse=True)
    assert body["direction_threshold"] == PRED_GAP_THRESHOLD
    # Sans table d'intervalles (TOK-131 non servi) : aucun intervalle, aucune méthode.
    assert body["interval_method"] is None and all(e["interval_lo"] is None for e in body["data"])
