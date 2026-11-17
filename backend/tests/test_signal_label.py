"""Libellé absolu des signaux boutique : règle de rang et endpoint /boutique/signals."""

import sqlite3

from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app
from app.signal_label import label_cutoffs, label_for, rank_in, signal_label


def test_cutoffs_on_the_real_population():
    # 89 archétypes OCG au 2026-11-16 : 10 % -> 8, 25 % -> 22.
    assert label_cutoffs(89) == (8, 22)


def test_label_depends_on_rank_not_on_the_batch():
    assert label_for(3, 89) == "Fort"       # Raise Moon
    assert label_for(12, 89) == "Modéré"    # Trirealm Rift
    assert label_for(18, 89) == "Modéré"    # Harpie/Amazoness
    assert label_for(9, 89) == "Modéré"     # juste en dessous du top 10 %
    assert label_for(23, 89) == "Faible"
    assert label_for(89, 89) == "Faible"


def test_there_is_no_forced_strong_label():
    # Un lot dont le meilleur archétype est classé 40e sur 89 n'a aucun « Fort ».
    scores = [float(100 - i) for i in range(89)]
    assert signal_label(scores[39], scores).label == "Faible"


def test_rank_ties_share_the_best_rank():
    assert rank_in(5.0, [9.0, 5.0, 5.0, 1.0]) == 2


def test_no_population_means_no_label():
    assert signal_label(10.0, []) is None


def _fake_db(with_ocg_table: bool) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE boutique_buy_signals (archetype TEXT, card_name TEXT, buy_score_100 REAL,
            cm_price REAL, ban_tcg TEXT, tcg_window_start TEXT, tcg_window_end TEXT);
        CREATE TABLE cards (name TEXT, image_url_small TEXT);
        INSERT INTO boutique_buy_signals VALUES
            ('Fort A', 'Carte 1', 100, 0.1, NULL, '2027-01-01', '2027-05-01'),
            ('Faible B', 'Carte 2', 90, 0.2, NULL, '2027-01-01', '2027-05-01'),
            ('Inconnu', 'Carte 3', 80, 0.3, NULL, NULL, NULL);
        """
    )
    if with_ocg_table:
        con.execute("CREATE TABLE ocg_archetype_scores (archetype TEXT, ocg_score REAL)")
        # 20 archétypes : Fort A est 1er (top 5 %), Faible B 20e.
        rows = [("Fort A", 100.0)] + [(f"x{i}", 80.0 - i) for i in range(18)] + [("Faible B", 1.0)]
        con.executemany("INSERT INTO ocg_archetype_scores VALUES (?, ?)", rows)
    return con


def _get(with_ocg_table: bool) -> dict:
    con = _fake_db(with_ocg_table)
    app.dependency_overrides[get_db] = lambda: con
    try:
        return TestClient(app).get("/api/v1/boutique/signals").json()
    finally:
        app.dependency_overrides.pop(get_db, None)
        con.close()


def test_endpoint_returns_absolute_labels_and_the_rule():
    body = _get(True)
    by_card = {d["card_name"]: d for d in body["data"]}
    assert by_card["Carte 1"]["signal_label"] == "Fort"
    assert by_card["Carte 1"]["archetype_rank"] == 1
    assert by_card["Carte 2"]["signal_label"] == "Faible"
    assert by_card["Carte 2"]["archetype_rank"] == 20
    # Archétype absent de la table de référence : pas de libellé inventé.
    assert by_card["Carte 3"]["signal_label"] is None
    assert "buy_label" not in by_card["Carte 1"]
    rule = body["label_rule"]
    assert rule["population"] == 20 and rule["strong_max_rank"] == 2 and rule["moderate_max_rank"] == 5
    assert rule["provisional"] is True and "non validés hors échantillon" in rule["note"]


def test_endpoint_degrades_without_the_reference_table():
    body = _get(False)
    assert len(body["data"]) == 3
    assert all(d["signal_label"] is None for d in body["data"])
    assert body["label_rule"] is None
