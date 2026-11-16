"""Libellé absolu des signaux boutique (suite de TOK-113), sans accès à la base.

Avant : Fort / Modéré / Faible venaient de `buy_score_100`, divisé par le meilleur
score du lot. Il y avait donc toujours un « Fort », même avec un signal faible.

Maintenant : le libellé est le RANG de l'archétype parmi TOUS les archétypes OCG
(`ocg_archetype_scores`, ~89 lignes), classés sur `ocg_score` (meta_score OCG ×
log(1 + vues/semaine), la même formule que le signal d'alerte). Un rang ne dépend
pas du lot affiché et ne dérive pas quand le maximum bouge, contrairement à un
seuil en points (le maximum brut est passé de 1,84 en juin à 2,58 en novembre).

Les coupes (10 % et 25 %) sont des quantiles ronds, pas des optimums : aucune
donnée ne permet de les valider (une seule série datée, première échéance en
mars 2027). Voir docs/journal/seuils-signal-boutique.md.
"""

from dataclasses import dataclass

# Part des archétypes OCG (classés du plus fort au plus faible) qui reçoit chaque libellé.
STRONG_TOP_SHARE = 0.10
MODERATE_TOP_SHARE = 0.25

PROVISIONAL_NOTE = (
    "Seuils provisoires, non validés hors échantillon : le libellé est le rang de "
    "l’archétype parmi les archétypes OCG, pas une probabilité d’arrivée ni de hausse de prix."
)


@dataclass(frozen=True)
class SignalLabel:
    label: str  # « Fort » | « Modéré » | « Faible »
    rank: int  # 1 = archétype OCG le plus fort
    population: int  # nombre d'archétypes OCG classés


def rank_in(score: float, all_scores: list[float]) -> int:
    """Rang à 1 de `score` (ex æquo : le meilleur rang partagé)."""
    return 1 + sum(1 for s in all_scores if s > score)


def label_for(rank: int, population: int) -> str:
    share = rank / population
    if share <= STRONG_TOP_SHARE:
        return "Fort"
    if share <= MODERATE_TOP_SHARE:
        return "Modéré"
    return "Faible"


def label_cutoffs(population: int) -> tuple[int, int]:
    """Rangs maximaux (inclus) du Fort et du Modéré pour cette population."""
    strong = int(STRONG_TOP_SHARE * population + 1e-9)
    moderate = int(MODERATE_TOP_SHARE * population + 1e-9)
    return strong, moderate


def signal_label(score: float, all_scores: list[float]) -> SignalLabel | None:
    if not all_scores:
        return None
    rank = rank_in(score, all_scores)
    return SignalLabel(label_for(rank, len(all_scores)), rank, len(all_scores))
