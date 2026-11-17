"""Échantillon de relecture du jalon J1 (lot C2, TOK-118) : méthode validée par l'agent data-scientist-ygo le 18/11.

Unité : l'**effet** (verdict = toutes ses clauses correctement formalisées). Deux strates d'effets du pilote :
- (a) exercés par au moins une situation de `tests-branded.yaml` (écrites avant ce lot, rejouées par l'oracle) ;
- (b) exercés seulement par `situations-j1.yaml` (verdicts écrits par l'agent qui a formalisé).
Tirage simple sans remise dans chaque strate, 10 + 10, graine fixée (20260118), listes triées (carte, n° d'effet)
avant le tirage : le résultat est reproductible. Les effets `HORS_PERIMETRE` sont relus **en exhaustif**, à part
(erreur possible : mauvais classement). Taux global pondéré par strate (taille de la strate / effets du pilote).

    python scripts/combos_echantillon_j1.py      # écrit le tableau Markdown sur la sortie standard
"""

from __future__ import annotations

import random

from . import chemins, regles
from .base import ouvrir_reference
from .cartes import FORMALISATIONS
from .catalogue import construire_catalogue
from .deck import charger_deck, lire_textes, tous_les_noms
from .regles import HORS_PERIMETRE
from .scenarios import SCENARIOS, SCENARIOS_J1, executer_situation
from .situations import charger_tests, construire_depart

GRAINE = 20260118
TAILLE_PAR_STRATE = 10


def strates() -> tuple[list, list, list]:
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(chemins.base_de_reference())
    try:
        cat = construire_catalogue(deck, lire_textes(con, [c.card_id for c in deck.cartes]), tous_les_noms(con),
                                   FORMALISATIONS)
    finally:
        con.close()

    def jouer(fichier, scenarios) -> set:
        regles.EXERCES.clear()
        jeu = charger_tests(fichier)
        for s in jeu.situations:
            if s["id"] in scenarios:
                executer_situation(s, construire_depart(s, jeu, deck).etat, jeu.alias, cat, scenarios)
        return set(regles.EXERCES)

    par_yaml = jouer(chemins.TESTS_YAML, SCENARIOS)
    pilote = sorted((n, e.numero) for n, f in FORMALISATIONS.items() for e in f.effets if e.resolution != HORS_PERIMETRE)
    hors = sorted((n, e.numero) for n, f in FORMALISATIONS.items() for e in f.effets if e.resolution == HORS_PERIMETRE)
    a = [x for x in pilote if x in par_yaml]
    b = [x for x in pilote if x not in par_yaml]
    return a, b, hors


def tirer(graine: int = GRAINE, taille: int = TAILLE_PAR_STRATE):
    a, b, hors = strates()
    rng = random.Random(graine)
    return a, b, hors, sorted(rng.sample(a, min(taille, len(a)))), sorted(rng.sample(b, min(taille, len(b))))


def main() -> int:
    a, b, hors, ea, eb = tirer()
    print(f"Strate a (YAML + oracle) : {len(a)} effets ; strate b (situations J1 seules) : {len(b)} ; "
          f"hors périmètre : {len(hors)}. Graine {GRAINE}, {TAILLE_PAR_STRATE} par strate.\n")
    print("| # | Strate | Carte | Effet | Formalisation (paraphrase, `cartes*.py`) | Correct ? | Gravité | Note |")
    print("|---|---|---|---|---|---|---|---|")
    k = 0
    for strate, liste in (("a", ea), ("b", eb)):
        for nom, num in liste:
            k += 1
            note = FORMALISATIONS[nom].effet(num).note.replace("|", "/")
            print(f"| {k} | {strate} | {nom} | {num} | {note} | [ ] oui [ ] non | | |")
    print("\nHors périmètre (relecture exhaustive du classement) :\n")
    print("| Carte | Effet | Raison du classement | Bien classé ? |")
    print("|---|---|---|---|")
    for nom, num in hors:
        print(f"| {nom} | {num} | {FORMALISATIONS[nom].effet(num).note.replace('|', '/')} | [ ] oui [ ] non |")
    return 0
