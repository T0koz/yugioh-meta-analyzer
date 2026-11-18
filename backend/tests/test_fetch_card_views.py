"""TOK-138 : rafraîchissement de `cards.views_week` et archive datée (`scripts/fetch_card_views.py`).

Base synthétique et relevé factice (`--from-json`) : **aucun appel réseau**, ni `yugioh.db` ni `serving.db`.
"""

import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_freshness as cf  # noqa: E402
import fetch_card_views as fcv  # noqa: E402

BASE = [  # id, name, views_week, ban_tcg (une autre colonne, qui ne doit pas bouger)
    (1, "Ash Blossom &amp; Joyous Spring", 100, "Unlimited"),
    (2, "Maliss <P> March Hare", 50, "Limited"),
    (3, "Void Liberation", 70, None),
    (4, "Carte retirée de l'API", 5, None),
]


def api_card(cid, name, viewsweek=None, views=None):
    misc = {} if viewsweek is None else {"viewsweek": viewsweek, "views": views or viewsweek * 10}
    return {"id": cid, "name": name, "misc_info": [misc]}


API = [
    api_card(1, "Ash Blossom & Joyous Spring", 120),   # entité HTML en base : même carte
    api_card(2, "Maliss <P> March Hare", 50),           # inchangée
    api_card(3, "Void Unleashing", 999),                # renommée : garde de nom
    api_card(5, "Carte nouvelle", 300),                 # absente de cards
]


def make_db(path: Path) -> Path:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE cards (id INTEGER PRIMARY KEY, name TEXT, views_week INTEGER, ban_tcg TEXT)")
    conn.executemany("INSERT INTO cards VALUES (?,?,?,?)", BASE)
    conn.commit()
    conn.close()
    return path


def run(monkeypatch, db: Path, api: list, *extra) -> int:
    src = db.with_name("api.json")
    src.write_text(json.dumps({"data": api}))
    monkeypatch.setattr(sys, "argv", ["fetch_card_views.py", "--db", str(db), "--from-json", str(src), *extra])
    monkeypatch.setattr(fcv, "fetch_api", lambda: pytest.fail("appel réseau interdit dans les tests"))
    return fcv.main()


def test_updates_views_only_with_name_guard_and_archives(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    assert run(monkeypatch, db, API) == 0
    conn = sqlite3.connect(db)
    assert dict(conn.execute("SELECT id, views_week FROM cards")) == {1: 120, 2: 50, 3: 70, 4: 5}
    assert dict(conn.execute("SELECT id, ban_tcg FROM cards")) == {1: "Unlimited", 2: "Limited", 3: None, 4: None}
    assert dict(conn.execute("SELECT id, name FROM cards"))[1] == "Ash Blossom &amp; Joyous Spring"  # nom intact
    snap = conn.execute("SELECT card_id, card_name, views_week, views FROM card_views_snapshots ORDER BY card_id")
    assert [r[:3] for r in snap] == [(1, "Ash Blossom & Joyous Spring", 120), (2, "Maliss <P> March Hare", 50),
                                     (3, "Void Unleashing", 999), (5, "Carte nouvelle", 300)]
    (day,) = conn.execute("SELECT DISTINCT snapshot_date FROM card_views_snapshots").fetchone()
    assert dt.date.fromisoformat(day)
    assert len(list(tmp_path.glob("backup_vues_t_*.db"))) == 1


def test_same_day_rerun_replaces_that_day(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    run(monkeypatch, db, API)
    run(monkeypatch, db, [api_card(1, "Ash Blossom & Joyous Spring", 130), *API[1:]])
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM card_views_snapshots").fetchone()[0] == 4
    assert conn.execute("SELECT views_week FROM card_views_snapshots WHERE card_id = 1").fetchone()[0] == 130


def test_dry_run_writes_nothing(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    assert run(monkeypatch, db, API, "--dry-run") == 0
    conn = sqlite3.connect(db)
    assert dict(conn.execute("SELECT id, views_week FROM cards"))[1] == 100
    assert not conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'card_views_snapshots'").fetchone()


def test_truncated_or_viewless_response_writes_nothing(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    assert run(monkeypatch, db, API[:2]) == 1                                  # 2 cartes pour 4 en base
    assert run(monkeypatch, db, [api_card(c["id"], c["name"]) for c in API]) == 1  # plus de viewsweek
    conn = sqlite3.connect(db)
    assert dict(conn.execute("SELECT id, views_week FROM cards"))[1] == 100
    assert not conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'card_views_snapshots'").fetchone()


def test_missing_views_never_overwrite_with_null(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    api = [api_card(1, "Ash Blossom & Joyous Spring"), *API[1:]]   # carte 1 sans viewsweek
    assert run(monkeypatch, db, api) == 0
    assert sqlite3.connect(db).execute("SELECT views_week FROM cards WHERE id = 1").fetchone()[0] == 100


def test_failed_write_rolls_back(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    real_plan = fcv.plan

    def broken_plan(api, base):
        p = real_plan(api, base)
        p["snapshot"].append(p["snapshot"][0])        # clé primaire en double dans l'archive : l'INSERT échoue
        return p

    monkeypatch.setattr(fcv, "plan", broken_plan)
    with pytest.raises(sqlite3.IntegrityError):
        fcv.write(db, "2026-11-18", "2026-11-18T00:00:00Z", API)
    conn = sqlite3.connect(db)
    assert dict(conn.execute("SELECT id, views_week FROM cards"))[1] == 100
    assert not conn.execute("SELECT 1 FROM sqlite_master WHERE name = 'card_views_snapshots'").fetchone()


def test_freshness_dates_views_from_latest_snapshot(tmp_path):
    db = make_db(tmp_path / "t.db")
    fcv.write(db, "2026-11-16", "2026-11-16T06:00:00Z", API)
    conn = sqlite3.connect(db)
    ctx = cf.Context(conn, dt.date(2026, 11, 18), snapshot=None, known={})
    r = cf.views_age(ctx, "early_card_signals")
    assert r.status == cf.OK and "2026-11-16" in r.detail
    late = cf.Context(conn, dt.date(2026, 12, 1), snapshot=None, known={})
    assert cf.views_age(late, "early_card_signals").status == cf.STALE
    conn.execute("UPDATE cards SET views_week = views_week + 1")   # vues qui ne viennent plus du relevé
    assert cf.views_age_from_snapshots(ctx, "early_card_signals") is None


def test_renumbered_card_gets_views_by_name(tmp_path, monkeypatch):
    """Une carte dont l'API a changé l'id (même nom, ancien id absent de l'API) reçoit les vues sur son id en base."""
    db = make_db(tmp_path / "t.db")
    api = [*API, api_card(44, "Carte retirée de l'API", 77)]     # id 4 → 44
    assert run(monkeypatch, db, api) == 0
    assert sqlite3.connect(db).execute("SELECT views_week FROM cards WHERE id = 4").fetchone()[0] == 77


def test_ambiguous_renumbering_is_left_alone(tmp_path):
    base = {4: ("Double", 5), 6: ("Double", 6), 1: ("Ash", 1)}
    p = fcv.plan([api_card(1, "Ash", 2), api_card(9, "Double", 50)], base)
    assert p["updates"] == [(2, 1)] and p["ambiguous"] == [(9, "Double", [4, 6])]


def test_first_backup_is_always_kept(tmp_path):
    db = make_db(tmp_path / "t.db")
    for day in range(1, 12):
        (tmp_path / f"backup_vues_t_202601{day:02d}.db").write_bytes(b"")
    fcv.backup(db, "2026-11-18")
    left = sorted(p.name for p in tmp_path.glob("backup_vues_t_*.db"))
    assert left[0] == "backup_vues_t_20260101.db" and len(left) == fcv.KEEP_BACKUPS + 1


def test_card_views_step_is_non_blocking():
    import refresh_all as ra
    assert "card_views" in ra.NON_BLOCKING and "card_views" in ra.PENDING_FORM
    names = [n for n, _ in ra.STEPS]
    assert names.index("fetch_new_cards") < names.index("card_views") < names.index("early_signals")


def test_freshness_dates_what_is_served(tmp_path):
    """Si early_card_signals n'a pas été recalculée après le relevé, ses vues ne sont pas datées par lui."""
    db = make_db(tmp_path / "t.db")
    fcv.write(db, "2026-11-16", "2026-11-16T06:00:00Z", API)
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE early_card_signals (card_name TEXT, views_week INTEGER)")
    conn.executemany("INSERT INTO early_card_signals VALUES (?, ?)",
                     [("Ash Blossom & Joyous Spring", 100), ("Maliss <P> March Hare", 49)])   # vues d'avant
    ctx = cf.Context(conn, dt.date(2026, 11, 18), snapshot=None, known={})
    assert cf.views_age_from_snapshots(ctx, "early_card_signals") is None
    conn.execute("UPDATE early_card_signals SET views_week = 120 WHERE card_name LIKE 'Ash%'")
    conn.execute("UPDATE early_card_signals SET views_week = 50 WHERE card_name LIKE 'Maliss%'")
    r = cf.views_age_from_snapshots(ctx, "early_card_signals")
    assert r.status == cf.OK and "early_card_signals.views_week" in r.detail
