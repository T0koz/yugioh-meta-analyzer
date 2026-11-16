"""Règles des fiches de composition (TOK-114), sans accès à la base.

`scripts/build_archetype_profiles.py` compte (part des listes, médiane des
exemplaires) ; les seuils d'étiquette et l'effectif minimal ne vivent qu'ici.
Justification mesurée : docs/journal/decks-tok-114.md.
"""

# « De base » : la carte est dans au moins 80 % des listes de l'archétype.
# À ce seuil, la somme des exemplaires médians des cartes de base du main donne un
# cœur de 26 à 34 cartes pour 7 des 8 archétypes à 10 listes ou plus (à 70 %, 4 sur
# 8 dépassent 35 ; à 90 %, Branded tombe à 19). La distribution des parts est en U,
# sans creux net : 80 est un seuil rond cohérent, pas un optimum.
BASE_MIN_SHARE = 0.80
# « D'appoint » : de 20 % à moins de 80 % des listes. En dessous, pas d'étiquette.
FLEX_MIN_SHARE = 0.20

# Sous 8 listes, pas de part calculée : en ramenant Elfnote (82 listes) et Angelechy
# (65) à n listes par tirage, 19 à 24 % des étiquettes changent à n = 5, 9 à 13 % à
# n = 8, 7 à 14 % à n = 10. Passer de 5 à 8 divise l'erreur par deux, 10 n'apporte rien.
MIN_PROFILE_DECKS = 8

ROLE_BASE = "base"
ROLE_FLEX = "appoint"


def role_for(share: float) -> str | None:
    if share >= BASE_MIN_SHARE:
        return ROLE_BASE
    if share >= FLEX_MIN_SHARE:
        return ROLE_FLEX
    return None


def has_profile(n_decks: int) -> bool:
    return n_decks >= MIN_PROFILE_DECKS
