#!/usr/bin/env python3
"""Export de l'échantillon J1 pour la session de l'oracle (TOK-143, jalon n°5).

Écrit `docs/moteur-combos/echantillon-j1.md` **en termes de jeu seulement** (nom de carte, rang de l'effet dans le texte
TCG, déclencheur ou condition en une ligne, strate), sans structure interne du moteur ni texte de carte recopié :
1. les 20 effets tirés par `moteur_combos/echantillon.py` (graine 20260118, strates a et b, 10 + 10) ;
2. les 57 effets du pilote, chacun avec les situations déjà jouées dans l'oracle qui l'exercent (situations du YAML et
   de J1 rejouées par l'oracle selon `reponses-oracle.md`), pour voir les effets jamais exercés devant l'oracle.

L'exercice d'un effet par une situation est mesuré en rejouant la situation dans le moteur (effet résolu au moins une
fois, préalables compris) : une situation par passage, pour attribuer chaque effet à ses situations.

    python scripts/combos_export_echantillon.py [--sortie docs/moteur-combos/echantillon-j1.md]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from moteur_combos import chemins, regles  # noqa: E402
from moteur_combos.base import ouvrir_reference  # noqa: E402
from moteur_combos.cartes import FORMALISATIONS  # noqa: E402
from moteur_combos.catalogue import construire_catalogue  # noqa: E402
from moteur_combos.deck import charger_deck, lire_textes, tous_les_noms  # noqa: E402
from moteur_combos.echantillon import GRAINE, TAILLE_PAR_STRATE, tirer  # noqa: E402
from moteur_combos.scenarios import SCENARIOS, SCENARIOS_J1, executer_situation  # noqa: E402
from moteur_combos.situations import charger_tests, construire_depart  # noqa: E402

SORTIE = RACINE / "docs" / "moteur-combos" / "echantillon-j1.md"

# Ce que l'oracle a joué, d'après `reponses-oracle.md` (§ 2 « Situations jouées » et § 7.2).
YAML_NON_JOUEES = {"T52", "T53", "T67", "T68"}
YAML_EN_PARTIE = {"T06", "T08", "T09", "T10", "T13", "T14", "T17", "T19", "T49", "T57", "T61", "T72"}
J1_EN_PARTIE: set[str] = set()   # les 30 situations J1 ont été rejouées ; valeurs d'ATK non lues (J14, J24, J25)
ATK_NON_LUE = {"J14", "J24", "J25"}
DESACCORDS = {"T37": "R23", "J07": "R23 (accord partiel)", "J26": "N09 (désaccord, corrigé au lot C3)"}

GENRES = {"declenche": "effet déclenché", "ignition": "effet d'ignition", "rapide": "effet rapide",
          "activation_carte": "activation de la carte", "procedure": "Invocation par sa propre procédure",
          "fin": "effet de Phase de Fin", "restriction": "effet continu"}
ZONES = {"main": "main", "terrain": "terrain", "cimetiere": "Cimetière", "bannies": "bannie"}


def condition(nom: str, numero: int) -> str:
    """Genre, zone et déclencheur ou condition en une ligne, d'après notre paraphrase (aucun texte de carte)."""
    e = FORMALISATIONS[nom].effet(numero)
    note = re.sub(r"\s*\((R|T|N|J)\d+[a-z]?[^)]*\)", "", e.note or "")
    note = re.sub(r",? ?\b[RN]\d+[ab]?\b", "", note)
    note = re.sub(r"\*\*|`|⚖[^.;]*", "", note).strip()
    note = re.sub(r"\s*\((codé|code)[^)]*\)", "", note)
    note = re.sub(r"\(\s*\)", "", note)
    tete = note.split(". ")[0].strip().rstrip(".")
    if len(tete) > 170:
        tete = tete[:167].rsplit(" ", 1)[0] + "…"
    zones = ", ".join(ZONES.get(z, z) for z in e.zones)
    return f"{GENRES.get(e.genre, e.genre)} ({zones}) — {tete}"


def exercice_par_situation(cat, deck) -> dict[tuple[str, int], list[str]]:
    par_effet: dict[tuple[str, int], list[str]] = defaultdict(list)
    for fichier, scenarios in ((chemins.TESTS_YAML, SCENARIOS), (chemins.SITUATIONS_J1, SCENARIOS_J1)):
        jeu = charger_tests(fichier)
        for s in jeu.situations:
            if s["id"] not in scenarios:
                continue
            regles.EXERCES.clear()
            executer_situation(s, construire_depart(s, jeu, deck).etat, jeu.alias, cat, scenarios)
            for cle in regles.EXERCES:
                par_effet[cle].append(s["id"])
    return par_effet


def etiquette(sid: str) -> str:
    if sid in YAML_NON_JOUEES:
        return f"~~{sid}~~"
    marque = "*" if sid in YAML_EN_PARTIE or sid in J1_EN_PARTIE else ""
    marque += "†" if sid in DESACCORDS else ""
    return sid + marque


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sortie", type=Path, default=SORTIE)
    args = ap.parse_args(argv)
    a, b, hors, ea, eb = tirer()
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(chemins.base_de_reference())
    try:
        cat = construire_catalogue(deck, lire_textes(con, [c.card_id for c in deck.cartes]), tous_les_noms(con),
                                   FORMALISATIONS)
    finally:
        con.close()
    par_effet = exercice_par_situation(cat, deck)
    pilote = sorted(a + b)
    out = [
        "# Échantillon J1 et effets du pilote, pour l'oracle (TOK-143, jalon n°5)", "",
        "> **18/11/2026**, généré par `scripts/combos_export_echantillon.py`. Pour la session de l'oracle (jalon n°6, "
        "isolée) : tout est dit en termes de jeu ; aucune structure du moteur, aucun texte de carte recopié (les "
        "descriptions sont nos paraphrases). **Numéro d'effet** = rang de l'effet dans **notre lecture du texte TCG**, "
        "dans l'ordre du texte (une phrase continue, comme un gain d'ATK, compte comme un effet) : il peut différer "
        "des numéros ①②③ imprimés ; en cas de doute, se fier à la description.", "",
        "## 1. Les 20 effets tirés (graine 20260118)", "",
        f"Tirage simple sans remise, {TAILLE_PAR_STRATE} par strate, listes triées par (carte, numéro) avant le tirage "
        f"(`moteur_combos/echantillon.py`, méthode validée par `data-scientist-ygo`). **Strate a** : effets exercés "
        f"par au moins une situation de `tests-branded.yaml` ({len(a)} effets). **Strate b** : effets exercés "
        f"seulement par `situations-j1.yaml` ({len(b)} effets). Verdict attendu par effet : toutes ses clauses "
        "jouées comme l'oracle les joue (unité = l'effet). Taux global pondéré par strate : "
        f"{len(a)}/{len(pilote)} et {len(b)}/{len(pilote)}.", "",
        "| # | Strate | Carte | Effet n° | Genre, zone, déclencheur ou condition | Situations déjà jouées dans l'oracle |",
        "|---|---|---|---|---|---|",
    ]
    k = 0
    for strate, liste in (("a", ea), ("b", eb)):
        for nom, num in liste:
            k += 1
            sits = ", ".join(etiquette(s) for s in sorted(set(par_effet.get((nom, num), [])))) or "—"
            out.append(f"| {k} | {strate} | {nom} | {num} | {condition(nom, num)} | {sits} |")
    jamais = [x for x in pilote if not [s for s in par_effet.get(x, []) if s not in YAML_NON_JOUEES]]
    desaccord = [x for x in pilote if par_effet.get(x) and all(s in DESACCORDS or s in YAML_NON_JOUEES
                                                                for s in par_effet[x])]
    partiels = [x for x in pilote if x not in jamais
                and all(s in YAML_EN_PARTIE or s in YAML_NON_JOUEES for s in par_effet.get(x, []))]
    out += ["", f"## 2. Les {len(pilote)} effets du pilote et les situations qui les exercent", "",
            "Situations : `T..` = `tests-branded.yaml`, `J..` = `situations-j1.yaml`. Marques : `*` rejouée **en "
            "partie** seulement par l'oracle ; `~~T52~~` **non rejouée** ; `†` désaccord ou accord partiel avec "
            "l'oracle (T37, J07 : R23 ; J26 : N09, corrigé depuis). J14, J24, J25 : accord sur la légalité et les "
            "déplacements, valeurs d'ATK non lues par l'oracle.", "",
            f"**Effets jamais exercés devant l'oracle : {len(jamais)}**"
            + (" — " + ", ".join(f"{n} {e}" for n, e in jamais) if jamais else "") + ". "
            f"**Exercés seulement par des situations rejouées en partie : {len(partiels)}**"
            + (" — " + ", ".join(f"{n} {e}" for n, e in partiels) if partiels else "") + ". "
            f"**Exercés seulement par une situation en désaccord avec l'oracle : {len(desaccord)}**"
            + (" — " + ", ".join(f"{n} {e}" for n, e in desaccord) if desaccord else "") + ". "
            "« Exercé » = l'effet est résolu au moins une fois quand le moteur rejoue la situation ; une situation où "
            "l'effet est seulement proposé dans une liste ne compte pas.", "",
            "| Carte | Effet n° | Strate | Tiré | Genre, zone, déclencheur ou condition | Situations |",
            "|---|---|---|---|---|---|"]
    tires = set(ea) | set(eb)
    for nom, num in pilote:
        sits = ", ".join(etiquette(s) for s in sorted(set(par_effet.get((nom, num), [])),
                                                       key=lambda x: (x[0], int(x[1:])))) or "—"
        out.append(f"| {nom} | {num} | {'a' if (nom, num) in a else 'b'} | {'oui' if (nom, num) in tires else ''} | "
                   f"{condition(nom, num)} | {sits} |")
    out += ["", f"## 3. Effets hors périmètre ({len(hors)}, relus en exhaustif, à part)", "",
            "Effets qui supposent l'adversaire, la Phase de Combat ou un autre tour : non joués par le moteur au "
            "tour 1. À vérifier dans l'oracle : que leur condition est bien fausse au tour 1 du pilote.", "",
            "| Carte | Effet n° | Genre, zone, déclencheur ou condition |", "|---|---|---|"]
    out += [f"| {n} | {e} | {condition(n, e)} |" for n, e in hors]
    args.sortie.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"✓ {args.sortie} : {len(ea) + len(eb)} effets tirés, {len(pilote)} effets du pilote, "
          f"{len(jamais)} jamais exercés devant l'oracle, {len(partiels)} seulement en partie")
    return 0


if __name__ == "__main__":
    sys.exit(main())
