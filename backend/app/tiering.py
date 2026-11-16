"""Tier list maison (TOK-91) : règles de tier et de tendance, sans accès à la base.

La table `meta_tier_list` (scrapée sur yugiohmeta) est figée au 17 juin 2026 :
l'endpoint source renvoie 404. On recalcule donc la tier list à la volée depuis
`meta_scores` (TCG pur, rafraîchie chaque lundi). Ces fonctions sont pures pour
pouvoir être testées sans base (backend/tests/test_tiering.py).
"""

from math import sqrt

# Un mois seul est trop mince en début de mois (156 decks au 14 novembre 2026 :
# l'intervalle à 95 % d'une part de 5 % fait ±3,4 points, plus large qu'un seuil
# de tier). On cumule donc les mois les plus récents jusqu'à ce minimum.
MIN_WINDOW_DECKS = 300

# Seuils sur la PART de decks de la fenêtre, pas sur meta_score : le meta_score
# d'un deck unique classé premier vaut sqrt(1/n) et passerait devant des
# archétypes joués par dix fois plus de monde.
TIER_THRESHOLDS: list[tuple[str, float]] = [("T0", 0.40), ("T1", 0.15), ("T2", 0.07), ("T3", 0.03)]
# En dessous, une part n'est pas estimable : Rogue d'office.
TIER_MIN_DECKS = 5

# Tendance : test de deux proportions entre la fenêtre courante et la précédente.
TREND_Z = 1.96  # seuil bilatéral à 5 %
# Le test n'est pas valide sur de très petits comptes (5 decks contre 0 sortirait
# « en hausse ») : Stable d'office en dessous.
TREND_MIN_DECKS = 10


def tier_for(share: float, decks: int) -> str:
    if decks < TIER_MIN_DECKS:
        return "Rogue"
    for tier, threshold in TIER_THRESHOLDS:
        if share >= threshold:
            return tier
    return "Rogue"


def trend_for(decks: int, n: int, decks_prev: int, n_prev: int) -> str:
    """Rising / Declining si la part a bougé au-delà du bruit d'échantillonnage.

    z = (p1 - p2) / sqrt(p(1-p)(1/n1 + 1/n2)), p étant la part poolée des deux
    fenêtres. Avec une soixantaine d'archétypes testés à 5 %, deux ou trois
    signaux peuvent être dus au hasard : c'est une indication, pas une preuve.
    """
    if n <= 0 or n_prev <= 0 or decks + decks_prev < TREND_MIN_DECKS:
        return "Stable"
    pooled = (decks + decks_prev) / (n + n_prev)
    variance = pooled * (1 - pooled) * (1 / n + 1 / n_prev)
    if variance <= 0:
        return "Stable"
    z = (decks / n - decks_prev / n_prev) / sqrt(variance)
    if z >= TREND_Z:
        return "Rising"
    if z <= -TREND_Z:
        return "Declining"
    return "Stable"


def meta_score_for(share: float, avg_placement: float, best_placement_score: float) -> float:
    """Formule du notebook 04 : sqrt(part × score de placement normalisé au max de la fenêtre)."""
    if avg_placement <= 0 or best_placement_score <= 0:
        return 0.0
    return sqrt(share * (1 / avg_placement) / best_placement_score)
