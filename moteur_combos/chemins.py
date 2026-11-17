"""Emplacements des fichiers et des bases.

- `data/combos.db` : base du moteur, propre au dépôt (ou au worktree) où l'on travaille, ignorée par Git.
- `data/yugioh.db` : base de référence, **lue seulement** (`mode=ro`). Dans un worktree elle n'existe
  que dans le dépôt principal : on la cherche là, sauf si `YGO_DB_PATH` est défini.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "moteur-combos"
DECK_SOURCE = DOCS / "deck-branded-source.json"
TESTS_YAML = DOCS / "tests-branded.yaml"
POINTS_DE_REGLE = DOCS / "points-de-regle-a-valider.md"
SCHEMA_SQL = Path(__file__).resolve().parent / "schema.sql"
COMBOS_DB = ROOT / "data" / "combos.db"


def depot_principal() -> Path:
    """Racine du dépôt principal (différente de ROOT dans un worktree)."""
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(common).parent
    except (OSError, subprocess.CalledProcessError):
        return ROOT


def base_de_reference() -> Path:
    """yugioh.db à lire : YGO_DB_PATH, sinon celle du dépôt courant, sinon celle du dépôt principal."""
    if env := os.environ.get("YGO_DB_PATH"):
        return Path(env)
    locale = ROOT / "data" / "yugioh.db"
    return locale if locale.exists() else depot_principal() / "data" / "yugioh.db"
