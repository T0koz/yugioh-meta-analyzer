"""Tirage de l'échantillon de relecture du jalon J1 (moteur de combos, lot C2). Détail : moteur_combos/echantillon.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from moteur_combos.echantillon import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
