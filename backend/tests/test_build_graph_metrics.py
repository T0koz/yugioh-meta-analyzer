"""TOK-136 : recalcul de `card_graph_metrics` et `graph_communities` (`scripts/build_graph_metrics.py`).

Base synthétique construite ici : ne lit ni `yugioh.db` ni `serving.db`.
"""

import sqlite3
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_graph_metrics as bgm  # noqa: E402

# Deux triangles reliés par C–D (pont), une paire sous le seuil de Jaccard, une sous le seuil de decks.
PAIRS = [("A", "B", 0.6, 20), ("A", "C", 0.5, 20), ("B", "C", 0.5, 20), ("C", "D", 0.35, 8),
         ("D", "E", 0.6, 20), ("D", "F", 0.5, 20), ("E", "F", 0.5, 20),
         ("A", "X", 0.2, 50), ("B", "Y", 0.9, 3)]


def make_db(path: Path) -> Path:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE card_cooccurrence (card_a TEXT, card_b TEXT, jaccard REAL, cooc_count INTEGER)")
    conn.executemany("INSERT INTO card_cooccurrence VALUES (?,?,?,?)", PAIRS)
    conn.execute("CREATE TABLE cards (name TEXT, archetype TEXT)")
    conn.executemany("INSERT INTO cards VALUES (?,?)",
                     [("A", "Alpha"), ("B", "Alpha"), ("C", "Alpha"), ("D", "Delta"), ("E", "Delta"),
                      ("Maliss <P> Hare", "Maliss")])
    conn.execute("CREATE TABLE card_graph_metrics (card_name TEXT PRIMARY KEY, betweenness REAL, "
                 "degree_centrality REAL, closeness REAL, degree_weighted REAL)")
    conn.execute("INSERT INTO card_graph_metrics VALUES ('OLD', 0.5, 0.1, 0.1, 1.0)")
    conn.execute("CREATE TABLE graph_communities (community_id INTEGER PRIMARY KEY, n_cards INTEGER, "
                 "lead_card TEXT, archetype_label TEXT, top_archetypes TEXT, lead_degree REAL)")
    conn.execute("INSERT INTO graph_communities VALUES (0, 1, 'OLD', 'Old', 'Old', 1.0)")
    conn.commit()
    conn.close()
    return path


def compute(db: Path):
    conn = sqlite3.connect(db)
    edges = bgm.load_edges(conn)
    arch = bgm.archetype_map(conn)
    conn.close()
    G = bgm.build_graph(edges)
    return G, bgm.compute_metrics(G), bgm.compute_communities(G, arch)


def test_thresholds_and_metrics(tmp_path):
    G, metrics, _ = compute(make_db(tmp_path / "t.db"))
    assert set(G.nodes) == set("ABCDEF")            # X (Jaccard 0,2) et Y (3 decks) exclus
    assert list(metrics.columns) == ["card_name", "betweenness", "degree_centrality", "closeness", "degree_weighted"]
    top = metrics.iloc[0].card_name
    assert top in {"C", "D"}                         # le pont a la plus forte intermédiarité (exacte)
    assert metrics.set_index("card_name").betweenness["A"] == 0


def test_communities_deterministic_and_named(tmp_path):
    db = make_db(tmp_path / "t.db")
    _, _, (c1, m1) = compute(db)
    _, _, (c2, m2) = compute(db)
    assert c1.equals(c2) and m1 == m2
    assert c1.n_cards.sum() == 6 and len(c1) == 2
    assert {m1["A"], m1["B"], m1["C"]} != {m1["D"], m1["E"], m1["F"]}
    labels = dict(zip(c1.lead_card, c1.archetype_label))
    # « Maliss <P> Hare » (cards) est retrouvé sous son nom sans chevrons, celui des decks.
    assert bgm.archetype_map(sqlite3.connect(db))["Maliss P Hare"] == "Maliss"
    assert set(labels.values()) <= {"Alpha", "Delta", "F"}


def test_write_replaces_both_tables_and_backs_up(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    monkeypatch.setattr(sys, "argv", ["build_graph_metrics.py", "--db", str(db)])
    assert bgm.main() == 0
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM card_graph_metrics").fetchone()[0] == 6
    assert conn.execute("SELECT SUM(n_cards) FROM graph_communities").fetchone()[0] == 6
    assert not conn.execute("SELECT 1 FROM card_graph_metrics WHERE card_name='OLD'").fetchone()
    backups = list(tmp_path.glob("backup_graphe_t_*.db"))
    assert len(backups) == 1
    old = sqlite3.connect(backups[0])
    assert old.execute("SELECT card_name FROM card_graph_metrics").fetchall() == [("OLD",)]


def test_dry_run_writes_nothing(tmp_path, monkeypatch):
    db = make_db(tmp_path / "t.db")
    monkeypatch.setattr(sys, "argv", ["build_graph_metrics.py", "--db", str(db), "--dry-run"])
    assert bgm.main() == 0
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT card_name FROM card_graph_metrics").fetchall() == [("OLD",)]
    assert not list(tmp_path.glob("backup_graphe_*.db"))


def test_failed_write_leaves_both_tables_untouched(tmp_path):
    db = make_db(tmp_path / "t.db")
    _, metrics, (comms, _) = compute(db)
    dup = metrics.iloc[[0, 0]]                         # clé primaire en double : l'INSERT échoue
    try:
        bgm.write(db, dup, comms)
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("l'écriture aurait dû échouer")
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT card_name FROM card_graph_metrics").fetchall() == [("OLD",)]
    assert conn.execute("SELECT lead_card FROM graph_communities").fetchall() == [("OLD",)]


def test_backups_are_pruned(tmp_path):
    db = make_db(tmp_path / "t.db")
    for day in range(1, 11):
        (tmp_path / f"backup_graphe_t_202601{day:02d}.db").write_bytes(b"")
    bgm.backup_tables(db)
    left = sorted(p.name for p in tmp_path.glob("backup_graphe_t_*.db"))
    assert len(left) == bgm.KEEP_BACKUPS and left[0] == "backup_graphe_t_20260104.db"
    assert not list(tmp_path.glob("*.tmp"))


def test_pending_form_steps_are_skipped_and_tolerated():
    """Une étape verrouillée (refresh_all.PENDING_FORM) est sautée, et ses tables restent tolérées par TOK-93."""
    import check_freshness as cf
    import refresh_all as ra
    names = {n for n, _ in ra.STEPS}
    assert set(ra.PENDING_FORM) <= names
    tickets = {ticket for ticket, _, _ in cf.KNOWN_STALE.values()}
    for step, ticket in ra.PENDING_FORM.items():
        assert ticket in tickets, f"{step} verrouillée sans tolérance {ticket} dans check_freshness"
    assert ("graph_metrics" in ra.PENDING_FORM) == ("card_graph_metrics:graphe" in cf.KNOWN_STALE)
