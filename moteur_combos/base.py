"""Accès aux bases : `combos.db` en écriture, `yugioh.db` en lecture seule.

Deux garde-fous :
- `ouvrir_reference` ouvre toujours en `mode=ro` (URI SQLite) : aucune écriture possible ;
- `ouvrir_combos` refuse un fichier nommé `yugioh.db` ou `serving.db`.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .chemins import SCHEMA_SQL

SCHEMA_VERSION = 1
BASES_INTERDITES = {"yugioh.db", "serving.db"}


def maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ouvrir_reference(chemin: Path) -> sqlite3.Connection:
    """Base de référence, lecture seule. Lève FileNotFoundError si elle est absente."""
    if not Path(chemin).exists():
        raise FileNotFoundError(f"base de référence introuvable : {chemin}")
    con = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True, timeout=60)
    con.row_factory = sqlite3.Row
    return con


def ouvrir_combos(chemin: Path) -> sqlite3.Connection:
    """Base du moteur, créée au besoin ; le schéma est appliqué (idempotent)."""
    chemin = Path(chemin)
    if chemin.name in BASES_INTERDITES:
        raise ValueError(f"refus : le moteur de combos n'écrit jamais dans {chemin.name}")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(chemin, timeout=60)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    appliquer_schema(con)
    return con


def appliquer_schema(con: sqlite3.Connection) -> None:
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        raise RuntimeError(f"combos.db est en version {version}, ce code connaît la version {SCHEMA_VERSION}")
    con.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
    con.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    con.commit()
