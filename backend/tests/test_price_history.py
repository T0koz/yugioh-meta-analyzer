"""Règles d'affichage de l'historique de prix (TOK-103) et endpoint /boutique/prices, sur une base synthétique.

TOK-135 : `app/price_history.py` n'avait aucun test. Ne lit ni `yugioh.db` ni `serving.db`.
"""

import sqlite3

from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app
from app.price_history import MAX_STEP_DAYS, MIN_POINTS, days_between, find_gaps, is_sparse


def test_days_between_counts_calendar_days():
    assert days_between("2026-11-01", "2026-11-01") == 0
    assert days_between("2026-10-31", "2026-11-01") == 1
    assert days_between("2026-02-28", "2026-03-01") == 1  # 2026 n'est pas bissextile


def test_a_gap_starts_strictly_above_the_maximum_step():
    assert MAX_STEP_DAYS == 10
    # 10 jours d'écart : relié ; 11 jours : trou.
    assert find_gaps(["2026-11-01", "2026-11-11"]) == []
    assert find_gaps(["2026-11-01", "2026-11-12"]) == [("2026-11-01", "2026-11-12", 11)]


def test_gaps_are_listed_in_order_with_their_bounds():
    dates = ["2026-06-19", "2026-07-03", "2026-08-05", "2026-08-12", "2026-11-01"]
    assert find_gaps(dates) == [
        ("2026-06-19", "2026-07-03", 14),
        ("2026-07-03", "2026-08-05", 33),
        ("2026-08-12", "2026-11-01", 81),
    ]


def test_no_gap_without_two_snapshots():
    assert find_gaps([]) == []
    assert find_gaps(["2026-11-01"]) == []


def test_sparse_below_the_minimum_number_of_points():
    assert MIN_POINTS == 3
    assert is_sparse(0) and is_sparse(2)
    assert not is_sparse(3)


def _fake_db(with_table: bool) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.row_factory = sqlite3.Row
    if with_table:
        con.executescript(
            """
            CREATE TABLE boutique_price_history (card_name TEXT, snapshot_date TEXT, cardmarket_price REAL,
                tcgplayer_price REAL, computed_at TEXT);
            INSERT INTO boutique_price_history VALUES
                ('Carte A', '2026-11-01', 1.0, NULL, '2026-11-17'),
                ('Carte A', '2026-11-08', 1.2, NULL, '2026-11-17'),
                ('Carte A', '2026-11-30', 1.1, NULL, '2026-11-17'),
                ('Carte B', '2026-11-08', 5.0, NULL, '2026-11-17');
            """
        )
    return con


def _get(with_table: bool) -> dict:
    con = _fake_db(with_table)
    app.dependency_overrides[get_db] = lambda: con
    try:
        return TestClient(app).get("/api/v1/boutique/prices").json()
    finally:
        app.dependency_overrides.pop(get_db, None)
        con.close()


def test_endpoint_draws_gaps_and_flags_sparse_cards():
    body = _get(with_table=True)
    cards = {c["card_name"]: c for c in body["cards"]}
    assert [p["date"] for p in cards["Carte A"]["points"]] == ["2026-11-01", "2026-11-08", "2026-11-30"]
    assert cards["Carte A"]["gaps"] == [{"start": "2026-11-08", "end": "2026-11-30", "days": 22}]
    assert cards["Carte A"]["sparse"] is False
    assert cards["Carte B"]["sparse"] is True and cards["Carte B"]["gaps"] == []
    assert body["snapshot_count"] == 3  # dates distinctes, toutes cartes confondues
    assert (body["period_start"], body["period_end"]) == ("2026-11-01", "2026-11-30")
    assert (body["max_step_days"], body["min_points"]) == (MAX_STEP_DAYS, MIN_POINTS)
    assert body["computed_at"] == "2026-11-17"


def test_endpoint_without_the_table_returns_an_empty_history():
    # Base construite avant TOK-103 : réponse vide, pas d'erreur 500.
    body = _get(with_table=False)
    assert body["cards"] == [] and body["snapshot_count"] == 0
    assert body["period_start"] is None and body["computed_at"] is None
