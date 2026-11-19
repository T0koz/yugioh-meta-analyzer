"""TOK-137 : fenêtre du backtest du Ban Radar, decks connus à la coupure (`require_uploaded`).

Base synthétique en mémoire : ne lit ni `yugioh.db` ni `serving.db`.
"""

import sqlite3
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_ban_radar as radar  # noqa: E402

AS_OF = "2026-05-17"
DECKS = [  # id, ocg, created (tournoi), uploaded (mise en ligne)
    ("d1", 0, "2026-03-01T10:00:00.000Z", "2026-03-04T10:00:00.000Z"),   # connu avant la coupure
    ("d2", 0, "2026-05-15T10:00:00.000Z", "2026-05-20T10:00:00.000Z"),   # joué avant, mis en ligne après
    ("d3", 0, "2026-05-18T10:00:00.000Z", "2026-05-19T10:00:00.000Z"),   # joué après la coupure
    ("d4", 0, "2025-10-01T10:00:00.000Z", "2025-10-03T10:00:00.000Z"),   # hors fenêtre de 6 mois
    ("d5", 1, "2026-04-01T10:00:00.000Z", "2026-04-02T10:00:00.000Z"),   # OCG
]


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE tournament_decks (id TEXT, ocg INTEGER, created TEXT, uploaded TEXT, archetype TEXT)")
    conn.executemany("INSERT INTO tournament_decks VALUES (?,?,?,?,'X')", DECKS)
    conn.execute("CREATE TABLE deck_cards (deck_id TEXT, card_name TEXT, amount INTEGER, zone TEXT)")
    conn.executemany("INSERT INTO deck_cards VALUES (?, 'Carte', 3, 'main')", [(d[0],) for d in DECKS])
    conn.execute("CREATE TABLE deck_legality (deck_id TEXT, legal INTEGER)")
    conn.executemany("INSERT INTO deck_legality VALUES (?, 1)", [(d[0],) for d in DECKS])
    return conn


def test_default_window_is_unchanged():
    assert set(radar.load_usage(db(), AS_OF, "TCG").deck_id) == {"d1", "d2"}


def test_require_uploaded_drops_decks_published_after_cutoff():
    assert set(radar.load_usage(db(), AS_OF, "TCG", require_uploaded=True).deck_id) == {"d1"}
    assert set(radar.load_usage(db(), AS_OF, "OCG", require_uploaded=True).deck_id) == {"d5"}


def test_backtest_signatures_default_to_current_behaviour():
    import inspect
    for fn in (radar.load_usage, radar.build, radar.backtest_lists, radar.backtest):
        assert inspect.signature(fn).parameters["require_uploaded"].default is False
