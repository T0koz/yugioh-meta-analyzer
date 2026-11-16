"""
TOK-34/TOK-54 — Bridge score généralisé : impact d'une carte sur la méta si
elle disparaît.

Remplace la partie `card_impact` de `setup_impact_tables.py` (`ban_impact`
reste hors scope : non consommé par l'API ni le front). L'original ne notait
que les 35 cartes les plus récemment sorties, sur les 90 jours suivant leur
release — `/simulate-ban` renvoyait `bridge_score = 0` pour les 13 762 autres
cartes du jeu, ce qui bloquait TOK-34 et TOK-54.

    python scripts/build_card_impact.py             # écrit la table
    python scripts/build_card_impact.py --dry-run    # affiche le top 25

bridge_score = n_archetypes × log(1 + decks), sur la même fenêtre glissante
et le même univers que le Ban Radar (WINDOW_MONTHS, MIN_DECKS, TCG only —
voir build_ban_radar.py) plutôt qu'une fenêtre figée post-release : une carte
jouée par beaucoup d'archétypes en volume est une pièce de connexion, la
retirer fragmente plusieurs decks à la fois, pas un seul.

Dérivé de la table `ban_radar` (déjà calculée) plutôt que recalculé depuis
`deck_cards` : `n_archetypes` et `decks` y sont l'usage de chaque carte sur
la fenêtre pour tout l'univers noté, pas seulement son archétype dominant —
exactement ce que mesurait `n_archetypes_3m`/`total_decks_3m` dans l'original.
Éviter une deuxième requête sur 900k lignes, et rester automatiquement
synchronisé à chaque reconstruction du Ban Radar.
"""

import argparse
import os
import sqlite3

import numpy as np
import pandas as pd

DB = os.path.join(os.path.dirname(__file__), "..", "data", "yugioh.db")


def build(conn: sqlite3.Connection) -> pd.DataFrame:
    radar = pd.read_sql_query(
        """
        SELECT card_name, decks, n_archetypes, top_archetype,
               archetype_concentration, as_of, n_decks_window
        FROM ban_radar
        WHERE format = 'TCG'
        """,
        conn,
    )
    if radar.empty:
        raise SystemExit("ban_radar est vide — lance d'abord scripts/build_ban_radar.py")

    radar["bridge_score"] = (radar.n_archetypes * np.log1p(radar.decks)).round(3)
    return radar.sort_values("bridge_score", ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Affiche le top 25 sans écrire")
    args = parser.parse_args()

    conn = sqlite3.connect(DB)
    df = build(conn)

    print(f"card_impact — {len(df)} cartes notées "
          f"({df.n_decks_window.iloc[0]} decks sur la fenêtre, arrêté au {df.as_of.iloc[0]})")
    print(
        df.head(25)[
            ["card_name", "bridge_score", "n_archetypes", "decks", "top_archetype"]
        ].to_string(index=False)
    )

    if args.dry_run:
        return

    df.to_sql("card_impact", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_card_impact_name ON card_impact(card_name)")
    conn.commit()
    print(f"\nTable card_impact écrite ({len(df)} lignes)")


if __name__ == "__main__":
    main()
