"""TOK-93 : contrôle de fraîcheur des tables servies (`scripts/check_freshness.py`), sur une base synthétique.

Ne lit ni `yugioh.db` ni `serving.db`, et **n'appelle jamais le réseau** : l'endpoint yugiohmeta est remplacé par une
fonction de test. La base est construite ici, avec une date de contrôle imposée.
"""

import datetime as dt
import json
import re
import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_freshness as cf  # noqa: E402

TODAY = dt.date(2026, 11, 18)
GRAPH = [("A", "B"), ("B", "C"), ("C", "D")]   # arêtes au-dessus des seuils du notebook 03 → 4 nœuds

SCHEMA = {
    "archetype_card_profile": ("window_end, computed_at", [("2026-11", "2026-11-16")]),
    "archetype_recent_decks": ("deck_id, created", [("d1", "2026-11-14T10:00:00.000Z")]),
    "archetype_recent_deck_cards": ("deck_id, card_name", [("d1", "A")]),
    "archetype_trend": ("archetype", [("X",)]),
    "ban_backtest_lists": ("format, effective_date, computed_at",
                           [("TCG", "2026-10-19", "2026-11-16"), ("OCG", "2026-10-01", "2026-11-16")]),
    "ban_backtest_cards": ("format, effective_date, card_name", [("TCG", "2026-10-19", "A"), ("OCG", "2026-10-01", "A")]),
    "ban_radar": ("card_name, as_of", [("A", "2026-11-14")]),
    "boutique_buy_signals": ("card_name, computed_at", [("A", "2026-11-16")]),
    "boutique_price_history": ("card_name, snapshot_date, computed_at", [("A", "2026-11-16", "2026-11-17")]),
    "card_cooccurrence": ("card_a, card_b, jaccard, cooc_count",
                          [(a, b, 0.5, 10) for a, b in GRAPH] + [("A", "E", 0.1, 10)]),  # A–E sous le seuil
    "card_graph_metrics": ("card_name", [(c,) for c in "ABCD"]),
    "card_impact": ("card_name, as_of", [("A", "2026-11-14")]),
    "cards": ("id, name, views_week", [(1, "A", 10)]),
    "early_card_signals": ("card_name, as_of, computed_at", [("A", "2026-11-14", "2026-11-18")]),
    "graph_communities": ("community_id, n_cards", [(0, 3), (1, 1)]),
    "meta_predictions": ("archetype, data_month, computed_at", [("X", "2026-10", "2026-11-16")]),
    "meta_scores": ("month, archetype", [("2026-11", "X")]),
    "meta_scores_ocg": ("month, archetype", [("2026-11", "X")]),
    "meta_tier_list": ("archetype, scraped_at", [("X", "2026-11-17")]),
    "ocg_archetype_scores": ("archetype, computed_at", [("X", "2026-11-16")]),
    "tournament_decks": ("id, created, ocg", [("d1", "2026-11-14T10:00:00.000Z", 0), ("d2", "2026-11-13T10:00:00.000Z", 1)]),
    "banlist_history": ("format, effective_date, card_name, status",
                        [("TCG", "2026-10-19", "A", "Limited"), ("OCG", "2026-10-01", "A", "Limited")]),
}
NO_KNOWN = {}


def build(path=":memory:", **overrides) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    for table, (cols, rows) in SCHEMA.items():
        rows = overrides.get(table, rows)
        conn.execute(f"CREATE TABLE {table} ({cols})")
        conn.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(cols.split(',')))})", rows)
    conn.commit()
    return conn


def statuses(conn, today=TODAY, known=NO_KNOWN, **kw) -> dict[str, str]:
    results, _ = cf.check(conn, today, snapshot=None, known=known, **kw)
    return {r.table: r.status for r in results}


def test_every_served_table_has_a_rule():
    assert set(cf.SERVED_TABLES) <= set(cf.RULES), set(cf.SERVED_TABLES) - set(cf.RULES)


def test_fresh_base_has_no_stale_table():
    st = statuses(build())
    assert cf.STALE not in st.values(), st
    # Sans colonne de date ni contrôle de cohérence : dit « non datée », jamais « ok ».
    assert st["card_cooccurrence"] == st["cards"] == cf.UNDATED
    # Lue par aucun routeur : « non lue », quel que soit son statut.
    assert st["archetype_trend"] == cf.UNREAD


def test_computed_at_beyond_threshold_is_stale():
    old = (TODAY - dt.timedelta(days=cf.COMPUTED_MAX_DAYS + 1)).isoformat()
    edge = (TODAY - dt.timedelta(days=cf.COMPUTED_MAX_DAYS)).isoformat()
    assert statuses(build(boutique_buy_signals=[("A", old)]))["boutique_buy_signals"] == cf.STALE
    assert statuses(build(boutique_buy_signals=[("A", edge)]))["boutique_buy_signals"] == cf.OK


def test_empty_date_column_and_empty_table_are_stale():
    assert statuses(build(boutique_buy_signals=[("A", None)]))["boutique_buy_signals"] == cf.STALE
    assert statuses(build(ocg_archetype_scores=[]))["ocg_archetype_scores"] == cf.STALE


def test_as_of_lagging_behind_last_deck_is_stale():
    assert statuses(build(ban_radar=[("A", "2026-11-06")]))["ban_radar"] == cf.STALE  # 8 j avant le 14/11
    assert statuses(build(ban_radar=[("A", "2026-11-07")]))["ban_radar"] == cf.OK


def test_monthly_table_two_months_behind_is_stale():
    assert statuses(build(meta_scores=[("2026-09", "X")]))["meta_scores"] == cf.STALE
    assert statuses(build(meta_scores=[("2026-10", "X")]))["meta_scores"] == cf.OK
    assert statuses(build(meta_scores_ocg=[("2026-09", "X")]))["meta_scores_ocg"] == cf.STALE
    assert statuses(build(meta_scores_ocg=[("2026-10", "X")]))["meta_scores_ocg"] == cf.OK


def test_graph_tables_must_match_cooccurrence_graph():
    st = statuses(build(card_graph_metrics=[("A",), ("B",)], graph_communities=[(0, 2)]))
    assert st["card_graph_metrics"] == st["graph_communities"] == cf.STALE


def test_ban_history_must_cover_latest_banlist():
    newer = SCHEMA["banlist_history"][1] + [("TCG", "2026-11-10", "B", "Forbidden")]
    st = statuses(build(banlist_history=newer))
    assert st["ban_backtest_lists"] == st["ban_backtest_cards"] == cf.STALE
    # Une liste annoncée mais pas encore en vigueur n'est pas exigée.
    future = SCHEMA["banlist_history"][1] + [("TCG", "2026-12-01", "B", "Forbidden")]
    assert statuses(build(banlist_history=future))["ban_backtest_lists"] == cf.OK


def test_latest_list_skipped_by_backtest_is_not_a_false_alarm():
    # Liste écartée (< 600 decks) : une ligne dans ban_backtest_lists, aucune carte dans ban_backtest_cards.
    lists = SCHEMA["ban_backtest_lists"][1] + [("TCG", "2026-11-10", "2026-11-16")]
    banlists = SCHEMA["banlist_history"][1] + [("TCG", "2026-11-10", "B", "Forbidden")]
    st = statuses(build(ban_backtest_lists=lists, banlist_history=banlists))
    assert st["ban_backtest_lists"] == st["ban_backtest_cards"] == cf.OK


def test_child_table_takes_parent_status_and_detects_orphans():
    assert statuses(build(archetype_recent_decks=[("d1", "2026-10-01")]))["archetype_recent_deck_cards"] == cf.STALE
    assert statuses(build(archetype_recent_deck_cards=[("zz", "A")]))["archetype_recent_deck_cards"] == cf.STALE
    assert statuses(build(archetype_recent_deck_cards=[]))["archetype_recent_deck_cards"] == cf.STALE  # vide


def test_stale_table_not_read_by_api_is_reported_without_failing():
    assert statuses(build(meta_tier_list=[("X", "2026-06-17")]))["meta_tier_list"] == cf.UNREAD  # TOK-97


def test_missing_table_and_broken_query_are_stale():
    conn = build()
    conn.execute("DROP TABLE card_impact")
    conn.execute("ALTER TABLE ban_radar RENAME COLUMN as_of TO as_of_renamed")
    st = statuses(conn)
    assert st["card_impact"] == st["ban_radar"] == cf.STALE


def test_known_stale_is_tolerated_until_expiry_only():
    conn = build(card_graph_metrics=[("A",)])
    known = {"card_graph_metrics:graphe": ("TOK-136", "2026-12-31", "test")}
    assert statuses(conn, known=known)["card_graph_metrics"] == cf.KNOWN
    assert statuses(conn, today=dt.date(2027, 1, 1), known=known)["card_graph_metrics"] == cf.STALE
    # Jamais de tolérance pour une table vide.
    assert statuses(build(card_graph_metrics=[]), known=known)["card_graph_metrics"] == cf.STALE


def test_serving_base_is_checked_against_reference_dates():
    serving = build()
    serving.execute("DROP TABLE tournament_decks")
    serving.execute("DROP TABLE banlist_history")
    assert statuses(serving)["ban_radar"] == cf.SKIPPED            # sans référence : dit, pas conclu
    assert statuses(serving, ref=build())["ban_radar"] == cf.OK    # avec yugioh.db comme référence


def test_frozen_views_make_early_signals_stale(tmp_path, monkeypatch):
    snap = tmp_path / "cards.json"
    snap.write_text('[{"id": 1, "misc_info": [{"viewsweek": 10}]}]')
    monkeypatch.setattr(cf, "snapshot_date", lambda: dt.date(2026, 6, 13))
    conn = build()
    ctx = cf.Context(conn, TODAY, snap, known=NO_KNOWN)
    assert cf.views_age(ctx, "early_card_signals").status == cf.STALE
    conn.execute("UPDATE cards SET views_week = 99")
    assert cf.views_age(ctx, "early_card_signals").status == cf.UNDATED  # rafraîchies, mais sans date


def fake_endpoint(ok: bool):
    return lambda *a, **k: {"url": cf.ENDPOINT, "ok": ok, "http_status": 200 if ok else None, "seconds": 0.0,
                            "detail": "HTTP 200, 1 deck(s)" if ok else "échec réseau : test"}


def run_main(monkeypatch, *args) -> int:
    monkeypatch.setattr(sys, "argv", ["check_freshness.py", *args])
    return cf.main()


def test_exit_code_journal_and_status(tmp_path, monkeypatch, capsys):
    db, journal = tmp_path / "base.db", tmp_path / "fetch_health.jsonl"
    build(str(db)).close()
    monkeypatch.setattr(cf, "SNAPSHOT", None)
    monkeypatch.setattr(cf, "KNOWN_STALE", {})
    monkeypatch.setattr(cf, "probe_endpoint", fake_endpoint(True))
    common = ["--db", str(db), "--today", TODAY.isoformat(), "--journal", str(journal)]
    assert run_main(monkeypatch, *common) == 0
    assert run_main(monkeypatch, "--status", "--journal", str(journal)) == 0

    conn = sqlite3.connect(db)
    conn.execute("UPDATE ocg_archetype_scores SET computed_at = '2026-10-01'")
    conn.commit()
    conn.close()
    assert run_main(monkeypatch, *common) == 1
    assert "PÉRIMÉES (1) : ocg_archetype_scores" in capsys.readouterr().out
    assert run_main(monkeypatch, "--status", "--journal", str(journal)) == 1
    assert "✗ ocg_archetype_scores" in capsys.readouterr().out

    entries = [json.loads(l) for l in journal.read_text().splitlines()]
    assert [e["ok"] for e in entries] == [True, False]
    assert all(e["step"] == cf.STEP and '"freshness"' not in json.dumps(e) for e in entries)  # cf. refresh_decks.py


def test_endpoint_failure_fails_the_check(tmp_path, monkeypatch, capsys):
    db, journal = tmp_path / "base.db", tmp_path / "fetch_health.jsonl"
    build(str(db)).close()
    monkeypatch.setattr(cf, "SNAPSHOT", None)
    monkeypatch.setattr(cf, "KNOWN_STALE", {})
    monkeypatch.setattr(cf, "probe_endpoint", fake_endpoint(False))
    assert run_main(monkeypatch, "--db", str(db), "--today", TODAY.isoformat(), "--journal", str(journal)) == 1
    assert "échec réseau" in capsys.readouterr().out
    assert json.loads(journal.read_text())["endpoint"]["ok"] is False
    assert run_main(monkeypatch, "--status", "--journal", str(journal)) == 1
    assert "endpoint EN ERREUR" in capsys.readouterr().out
    # --sans-endpoint : aucun appel, journal sans endpoint.
    monkeypatch.setattr(cf, "probe_endpoint", lambda *a, **k: pytest.fail("appel réseau inattendu"))
    assert run_main(monkeypatch, "--db", str(db), "--today", TODAY.isoformat(), "--sans-endpoint", "--sans-journal") == 0


def test_probe_reports_network_errors(monkeypatch):
    def boom(*a, **k):
        raise cf.urllib.error.URLError("nom inconnu")
    monkeypatch.setattr(cf.urllib.request, "urlopen", boom)
    out = cf.probe_endpoint()
    assert out["ok"] is False and "échec réseau" in out["detail"]


def test_wired_after_serving_in_monday_job():
    """Le contrôle tourne en fin de refresh_decks.py, après la base de service, jamais dans refresh_all.py
    (un code 1 dans refresh_all ferait sauter la reconstruction de serving.db)."""
    decks = (SCRIPTS / "refresh_decks.py").read_text()
    assert "TABLES_FRESHNESS" in decks and "check_freshness.py" in decks
    assert decks.index('("serving", "scripts/build_serving_db.py")') < decks.index("TABLES_FRESHNESS = ")
    assert "check_freshness" not in (SCRIPTS / "refresh_all.py").read_text()


def test_constants_match_their_sources():
    fetch = (SCRIPTS / "fetch_tournament_decks.py").read_text()
    assert re.search(r'BASE_URL\s*=\s*"([^"]+)"', fetch).group(1) == cf.ENDPOINT
    bridge = (SCRIPTS / "bridge_date.py").read_text()
    assert float(re.search(r"EDGE_MIN_JACCARD = ([\d.]+)", bridge).group(1)) == cf.EDGE_MIN_JACCARD
    assert int(re.search(r"EDGE_MIN_COOC = (\d+)", bridge).group(1)) == cf.EDGE_MIN_COOC
    graph = (SCRIPTS / "build_graph_metrics.py").read_text()   # TOK-136 : le producteur des deux tables
    assert float(re.search(r"EDGE_MIN_JACCARD = ([\d.]+)", graph).group(1)) == cf.EDGE_MIN_JACCARD
    assert int(re.search(r"EDGE_MIN_COOC = (\d+)", graph).group(1)) == cf.EDGE_MIN_COOC
