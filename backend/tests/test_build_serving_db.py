"""`scripts/build_serving_db.py` : garde de couverture et copie des tables servies (TOK-135).

Bases construites dans un dossier temporaire : ni `yugioh.db` ni `serving.db` ne sont lues ou écrites.
"""

import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_serving_db as bsd  # noqa: E402


def test_served_tables_have_no_duplicate():
    assert len(bsd.SERVED_TABLES) == len(set(bsd.SERVED_TABLES))


def test_table_reference_reads_from_and_join_only():
    sql = """
        SELECT r.*, c.image_url_small FROM ban_radar r
        LEFT JOIN cards c ON c.name = r.card_name
        -- FROM commentaire_compte_aussi
        WHERE x IN (SELECT y FROM sous_table)
    """
    assert set(bsd.TABLE_REFERENCE.findall(sql)) == {"ban_radar", "cards", "commentaire_compte_aussi", "sous_table"}


# Noms que l'expression régulière attrape sans être des tables : imports (`from app…`, `from fastapi…`,
# `from typing…`), alias et CTE du SQL des routeurs, table système.
NOT_TABLES = {"a", "p", "cur", "prev", "months", "spread", "app", "fastapi", "typing", "sqlite_master"}
# Lue seulement si elle existe (TOK-131, avant formulaire) : hors de SERVED_TABLES exprès.
OPTIONAL_TABLES = {"meta_prediction_intervals"}


def test_every_table_named_by_a_router_is_served_or_declared_optional():
    # `check_coverage` ne voit que les tables présentes dans yugioh.db : une table citée par un routeur mais pas
    # encore calculée lui échappe. Ce test la voit avant le premier calcul.
    referenced = bsd.tables_referenced_by_api()
    assert {"ban_radar", "cards", "meta_scores", "boutique_buy_signals"} <= referenced
    unexpected = referenced - set(bsd.SERVED_TABLES) - NOT_TABLES - OPTIONAL_TABLES
    assert not unexpected, f"tables citées par un routeur, absentes de SERVED_TABLES : {sorted(unexpected)}"


def test_check_coverage_flags_a_router_table_missing_from_the_list(monkeypatch):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE ban_radar (x)")
    con.execute("CREATE TABLE cards (x)")
    monkeypatch.setattr(bsd, "SERVED_TABLES", ["cards"])
    assert bsd.check_coverage(con) == ["ban_radar"]


def test_build_copies_rows_schema_and_explicit_indexes(tmp_path, monkeypatch):
    source_path, destination = tmp_path / "source.db", tmp_path / "serving.db"
    src = sqlite3.connect(source_path)
    src.executescript(
        """
        CREATE TABLE cards (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        INSERT INTO cards VALUES (1, 'Maliss <P> March Hare'), (2, 'Ash Blossom & Joyous Spring');
        CREATE TABLE "ban_radar" (card_name TEXT, ban_risk_score REAL);
        INSERT INTO ban_radar VALUES ('Ash Blossom & Joyous Spring', 80.0);
        CREATE INDEX idx_ban_radar_card ON ban_radar(card_name);
        CREATE TABLE deck_cards (deck_id TEXT, card_name TEXT);
        INSERT INTO deck_cards VALUES ('d1', 'x');
        """
    )
    monkeypatch.setattr(bsd, "SERVED_TABLES", ["cards", "ban_radar"])
    bsd.ensure_name_index(src)
    bsd.build(src, destination)
    src.close()

    out = sqlite3.connect(destination)
    tables = {r[0] for r in out.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables == {"cards", "ban_radar"}, "seules les tables servies sont copiées"
    assert out.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 2
    assert out.execute("SELECT ban_risk_score FROM ban_radar").fetchone()[0] == 80.0
    indexes = {r[0] for r in out.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")}
    assert {"idx_ban_radar_card", "idx_cards_name_clean"} <= indexes
    # La contrainte NOT NULL vient du DDL d'origine.
    with pytest.raises(sqlite3.IntegrityError):
        out.execute("INSERT INTO cards (id, name) VALUES (3, NULL)")
    out.close()


def test_build_refuses_a_served_table_absent_from_the_source(tmp_path, monkeypatch):
    src = sqlite3.connect(tmp_path / "source.db")
    src.execute("CREATE TABLE cards (name TEXT)")
    monkeypatch.setattr(bsd, "SERVED_TABLES", ["cards", "table_absente"])
    with pytest.raises(SystemExit, match="table_absente"):
        bsd.build(src, tmp_path / "serving.db")
    src.close()
