"""Accès aux bases : `combos.db` en écriture, `yugioh.db` en lecture seule.

Garde-fous (relus par l'agent gardien-donnees le 18/11) :
- `ouvrir_reference` ouvre toujours en `mode=ro` (URI SQLite échappée) : aucune écriture possible ;
- `ouvrir_combos` résout le chemin (liens symboliques, casse du disque) et refuse : un nom de base
  du projet (`yugioh.db`, `serving.db`, `backup_*.db`, sans tenir compte de la casse), le même fichier
  que la base de référence, et toute base existante qui contient une table sans le préfixe `cb_`.

Versions du schéma : `PRAGMA user_version`. Une base neuve reçoit `schema.sql` ; une base plus ancienne
reçoit les fichiers `migrations/NNN.sql` manquants, chacun dans une transaction, et seulement ensuite
le nouveau numéro. Aucune migration n'existe encore (version 1).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .chemins import SCHEMA_SQL, base_de_reference

SCHEMA_VERSION = 1
MIGRATIONS = Path(__file__).resolve().parent / "migrations"
BASES_INTERDITES = {"yugioh.db", "serving.db"}


def maintenant() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def uri_lecture_seule(chemin: Path) -> str:
    return Path(chemin).resolve().as_uri() + "?mode=ro"


def ouvrir_reference(chemin: Path) -> sqlite3.Connection:
    """Base de référence, lecture seule. Lève FileNotFoundError si elle est absente."""
    if not Path(chemin).exists():
        raise FileNotFoundError(f"base de référence introuvable : {chemin}")
    con = sqlite3.connect(uri_lecture_seule(chemin), uri=True, timeout=60)
    con.row_factory = sqlite3.Row
    return con


def _verifier_cible(chemin: Path, reference: Path | None) -> Path:
    reel = Path(os.path.realpath(chemin))
    for nom in {chemin.name, reel.name}:
        bas = nom.lower()
        if bas in BASES_INTERDITES or bas.startswith("backup_"):
            raise ValueError(f"refus : le moteur de combos n'écrit jamais dans {nom}")
    ref = reference if reference is not None else base_de_reference()
    if reel.exists() and ref.exists() and os.path.samefile(reel, ref):
        raise ValueError(f"refus : {chemin} désigne la base de référence ({ref})")
    if reel.exists() and reel.stat().st_size > 0:
        con = sqlite3.connect(uri_lecture_seule(reel), uri=True)
        try:
            etrangeres = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'cb\\_%' ESCAPE '\\'"
                " AND name NOT LIKE 'sqlite\\_%' ESCAPE '\\'")]
        finally:
            con.close()
        if etrangeres:
            raise ValueError(f"refus : {chemin} contient des tables étrangères au moteur ({', '.join(etrangeres[:5])})")
    return reel


def ouvrir_combos(chemin: Path, reference: Path | None = None) -> sqlite3.Connection:
    """Base du moteur, créée au besoin ; schéma appliqué ou migré."""
    chemin = Path(chemin)
    reel = _verifier_cible(chemin, reference)
    reel.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(reel, timeout=60)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    appliquer_schema(con)
    return con


def appliquer_schema(con: sqlite3.Connection) -> None:
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        raise RuntimeError(f"combos.db est en version {version}, ce code connaît la version {SCHEMA_VERSION}")
    if 0 < version < SCHEMA_VERSION:
        for v in range(version + 1, SCHEMA_VERSION + 1):
            fichier = MIGRATIONS / f"{v:03d}.sql"
            if not fichier.exists():
                raise RuntimeError(f"combos.db en version {version} : migration manquante {fichier.name}")
            con.execute("BEGIN")
            try:
                for instruction in _instructions(fichier.read_text(encoding="utf-8")):
                    con.execute(instruction)
                con.execute(f"PRAGMA user_version = {v}")
                con.commit()
            except Exception:
                con.rollback()
                raise
    # Idempotent : sur une base à jour, n'ajoute que des objets nouveaux (index…), jamais une colonne.
    con.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
    if version == 0:
        con.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    con.commit()


def _instructions(script: str) -> list[str]:
    morceaux, courant = [], ""
    for ligne in script.splitlines(keepends=True):
        courant += ligne
        if sqlite3.complete_statement(courant):
            if courant.strip():
                morceaux.append(courant)
            courant = ""
    return morceaux
