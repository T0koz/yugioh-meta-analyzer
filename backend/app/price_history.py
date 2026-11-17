"""Règles d'affichage de l'historique de prix (TOK-103), sans accès à la base.

`scripts/build_boutique_price_history.py` recopie les relevés tels quels ; les
règles qui décident de ce que la courbe a le droit de relier ne vivent qu'ici.
Aucun calcul statistique : on ne lisse pas, on n'interpole pas, on ne comble rien.
"""

from datetime import date

# Deux relevés consécutifs à plus de 10 jours d'écart ne sont pas reliés : la
# période entre eux est un trou, dessiné comme tel. La cadence visée est
# hebdomadaire (job du lundi) ; 10 jours tolèrent un relevé pris avec quelques
# jours de retard, pas une semaine sautée. Avant novembre 2026, les relevés
# étaient pris à la main (2026-06-19 → 07-03 : 14 jours, 07-03 → 08-05 : 33,
# 08-14 → 11-01 : 79) : ces trois périodes apparaissent comme des trous.
MAX_STEP_DAYS = 10

# Sous 3 relevés, aucune ligne n'est tracée : la page écrit « relevés trop rares »
# et ne montre que les points.
MIN_POINTS = 3

SOURCE = "prix moyen Cardmarket relevé via l'API YGOPRODeck"


def days_between(start: str, end: str) -> int:
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def find_gaps(dates: list[str]) -> list[tuple[str, str, int]]:
    """Périodes sans relevé : (dernier relevé avant, premier relevé après, jours)."""
    gaps = []
    for previous, current in zip(dates, dates[1:]):
        days = days_between(previous, current)
        if days > MAX_STEP_DAYS:
            gaps.append((previous, current, days))
    return gaps


def is_sparse(n_points: int) -> bool:
    return n_points < MIN_POINTS
