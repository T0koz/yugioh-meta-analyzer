"""Harnais du jeu de tests Branded du moteur de combos (lot 18) — une seule commande.

    python scripts/combos_harnais.py            # rapport + écriture dans data/combos.db
    python scripts/combos_harnais.py --detail   # une ligne par situation

Lit les textes des cartes en lecture seule dans yugioh.db (dans un worktree : celle du dépôt
principal, ou YGO_DB_PATH). N'écrit que dans data/combos.db (ignorée par Git). Détail : moteur_combos/harnais.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from moteur_combos.harnais import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
