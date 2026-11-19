"""Invariants des réponses de l'API sur la base réelle (TOK-135).

Complète le test de fumée (`test_endpoints.py`, « répond 200 ») : ce qui est servi doit rester cohérent avec les
règles du code (tiers, tendance, trous de prix, seuils du backtest), quelle que soit la semaine de calcul. Lancer
sur les deux bases, comme le test de fumée (`scripts/check.py` le fait).
"""

import pytest
from fastapi.testclient import TestClient

from app.db import DB_PATH
from app.labels import direction_from_gap
from app.main import app
from app.price_history import find_gaps, is_sparse
from app.routers.meta import EVOLUTION_ARCHETYPE_LIMIT
from app.tiering import TIER_MIN_DECKS, TIER_THRESHOLDS, tier_for

if not DB_PATH.exists():
    pytest.skip(f"Base absente : {DB_PATH}", allow_module_level=True)

client = TestClient(app)


def get(path: str) -> dict:
    response = client.get(f"/api/v1{path}")
    assert response.status_code == 200, response.text[:300]
    return response.json()


def test_tier_list_applies_the_tier_rules_on_one_window():
    body = get("/meta/tier-list")
    assert body["data"], "tier list vide"
    assert body["tier_thresholds"] == [{"tier": t, "share": s} for t, s in TIER_THRESHOLDS]
    assert body["tier_min_decks"] == TIER_MIN_DECKS
    assert body["window_start"] <= body["window_end"]
    assert sum(e["decks"] for e in body["data"]) <= body["n_decks"]
    for entry in body["data"]:
        assert entry["share"] == pytest.approx(entry["decks"] / body["n_decks"])
        assert entry["tier"] == tier_for(entry["share"], entry["decks"]), entry
    shares = [e["share"] for e in body["data"]]
    assert shares == sorted(shares, reverse=True), "tier list non triée par part décroissante"
    assert len({e["slug"] for e in body["data"]}) == len(body["data"]), "deux archétypes ont le même slug"


def test_evolution_counts_are_consistent_with_monthly_totals():
    body = get("/meta/evolution")
    assert 0 < len(body["data"]) <= EVOLUTION_ARCHETYPE_LIMIT
    for archetype, points in body["data"].items():
        months = [p["month"] for p in points]
        assert months == sorted(months), archetype
        for p in points:
            assert 0 <= p["share"] <= 1, (archetype, p)
            assert 0 <= p["decks"] <= body["decks_by_month"][p["month"]], (archetype, p)


def test_predictions_direction_is_the_drawn_gap():
    body = get("/meta/predictions")
    assert body["data_month"] and body["data"]
    for entry in body["data"]:
        assert entry["direction"] == direction_from_gap(entry["current"], entry["predicted"]), entry
        if entry["interval_lo"] is not None:
            assert entry["interval_lo"] <= entry["interval_hi"]


def test_boutique_prices_gaps_follow_the_drawing_rules():
    body = get("/boutique/prices")
    dates = set()
    for card in body["cards"]:
        points = [p["date"] for p in card["points"]]
        assert points == sorted(points), card["card_name"]
        assert [(g["start"], g["end"], g["days"]) for g in card["gaps"]] == find_gaps(points)
        assert card["sparse"] == is_sparse(len(points))
        assert all(p["price"] > 0 for p in card["points"]), card["card_name"]
        dates |= set(points)
    assert body["snapshot_count"] == len(dates)
    if dates:
        assert (body["period_start"], body["period_end"]) == (min(dates), max(dates))


def test_boutique_labels_follow_the_served_rule():
    body = get("/boutique/signals")
    rule = body["label_rule"]
    for signal in body["data"]:
        rank = signal["archetype_rank"]
        if rank is None:
            assert signal["signal_label"] is None
            continue
        assert 1 <= rank <= rule["population"]
        expected = "Fort" if rank <= rule["strong_max_rank"] else "Modéré" if rank <= rule["moderate_max_rank"] else "Faible"
        assert signal["signal_label"] == expected, signal
        if signal["tcg_window_start"] and signal["tcg_window_end"]:
            assert signal["tcg_window_start"] <= signal["tcg_window_end"]


def test_ban_history_retained_lists_pass_the_thresholds():
    body = get("/ban-radar/history")
    assert body["lists"], "historique vide : lancer scripts/build_ban_history.py puis build_serving_db.py"
    for lst in body["lists"]:
        if lst["retained"]:
            assert lst["n_decks"] >= body["min_decks"] and lst["n_hits"] >= body["min_hits"], lst["effective_date"]
            assert lst["skip_reason"] is None
            assert lst["random_low"] <= lst["random_rank"] <= lst["random_high"]
            assert 1 <= lst["median_rank"] <= lst["n_cards"]
        else:
            assert lst["skip_reason"] in ("decks", "hits"), lst["effective_date"]
        hits = [c for c in lst["cards"] if c["hit"]]
        assert len(hits) <= lst["n_hits"], lst["effective_date"]


def test_ban_radar_is_sorted_and_its_criteria_sum_to_the_score():
    body = get("/ban-radar?limit=200")
    scores = [e["ban_risk_score"] for e in body["data"]]
    assert scores == sorted(scores, reverse=True)
    for entry in body["data"]:
        assert 0 <= entry["ban_risk_score"] <= 100
        assert sum(entry["criteria"].values()) == pytest.approx(entry["ban_risk_score"], abs=0.03), entry["card_name"]
        assert entry["current_status"] != "Forbidden", entry["card_name"]
        # deck_share est en pourcentage (schemas.py) : decks / n_decks_window × 100.
        assert entry["deck_share"] == pytest.approx(100 * entry["decks"] / body["n_decks_window"], abs=0.01)


def test_early_signals_are_sorted_and_counted():
    body = get("/early-signals")
    scores = [e["early_score"] for e in body["data"]]
    assert scores == sorted(scores, reverse=True)
    assert len(body["data"]) <= 50
    if body["cards_scored"] is not None:
        assert body["cards_scored"] >= len(body["data"])
        assert 0 <= (body["text_signal_cards"] or 0) <= body["cards_scored"]


def test_simulator_deck_archetypes_count_lists_at_most_once():
    # `/simulate-ban` additionne les listes de Main et d'Extra Deck (TOK-132, jalon n°8) : cela suppose qu'une carte
    # n'est jamais dans les deux zones pour un même archétype. Le test signale la rupture au lieu de la masquer.
    import sqlite3

    con = sqlite3.connect(f"{DB_PATH.resolve().as_uri()}?mode=ro", uri=True)
    try:
        both = con.execute(
            """SELECT COUNT(*) FROM (SELECT archetype, card_name FROM archetype_card_profile
               WHERE zone IN ('main', 'extra') GROUP BY archetype, card_name HAVING COUNT(DISTINCT zone) > 1)"""
        ).fetchone()[0]
    finally:
        con.close()
    assert both == 0
    body = client.post("/api/v1/simulate-ban", json={"card_name": "Ash Blossom & Joyous Spring"}).json()
    assert body["deck_archetypes"], "Ash Blossom n'est jouée par aucun archétype de la fenêtre ?"
    for usage in body["deck_archetypes"]:
        assert 1 <= usage["lists"] <= usage["decks"], usage
    lists = [u["lists"] for u in body["deck_archetypes"]]
    assert lists == sorted(lists, reverse=True)
