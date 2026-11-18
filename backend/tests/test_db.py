"""Connexion à la base (`app/db.py`) : choix du fichier et lecture seule (TOK-135, sans base réelle).

Le choix du fichier est fait à l'import : il est vérifié dans un sous-processus, avec un environnement contrôlé.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

import app.db as db_module

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent


def _db_path_with(env: dict[str, str]) -> Path:
    clean = {k: v for k, v in os.environ.items() if k not in ("YGO_DB_PATH", "VERCEL")}
    out = subprocess.run(
        [sys.executable, "-c", "from app.db import DB_PATH; print(DB_PATH)"],
        cwd=BACKEND, env={**clean, **env}, capture_output=True, text=True, check=True,
    )
    return Path(out.stdout.strip())


def test_default_is_the_reference_database():
    assert _db_path_with({}) == ROOT / "data" / "yugioh.db"


def test_on_vercel_the_bundled_serving_database_is_used():
    assert _db_path_with({"VERCEL": "1"}) == BACKEND / "data" / "serving.db"


def test_explicit_path_wins_even_on_vercel(tmp_path):
    target = tmp_path / "autre.db"
    assert _db_path_with({"YGO_DB_PATH": str(target), "VERCEL": "1"}) == target


def _make_db(path: Path) -> None:
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE t (x INTEGER)")
    con.execute("INSERT INTO t VALUES (1)")
    con.commit()
    con.close()


def test_connection_is_read_only_and_returns_rows_by_name(tmp_path, monkeypatch):
    path = tmp_path / "base.db"
    _make_db(path)
    monkeypatch.setattr(db_module, "DB_PATH", path)
    gen = db_module.get_db()
    con = next(gen)
    try:
        assert con.execute("SELECT x FROM t").fetchone()["x"] == 1
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            con.execute("INSERT INTO t VALUES (2)")
    finally:
        gen.close()
    # La fermeture du générateur ferme la connexion.
    with pytest.raises(sqlite3.ProgrammingError):
        con.execute("SELECT 1")


def test_a_missing_file_is_not_created(tmp_path, monkeypatch):
    # mode=ro : sqlite3 ne crée pas de base vide à la place d'un fichier absent.
    path = tmp_path / "absente.db"
    monkeypatch.setattr(db_module, "DB_PATH", path)
    with pytest.raises(sqlite3.OperationalError):
        next(db_module.get_db())
    assert not path.exists()
