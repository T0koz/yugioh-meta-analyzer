"""Lecture de `tests-branded.yaml` et construction de l'état de départ d'une situation.

Ce qui est structuré : les zones (main, terrain, Cimetière, bannies), la phase, le tour, le deck
(« les 40 cartes moins celles placées ailleurs ») et l'Extra Deck (les 15 moins celles placées).
Ce qui reste en texte libre (D7) : la mémoire du tour décrite en phrases (« verrou NADIR… ») et les
annotations d'exemplaire non reconnues. Elles sont gardées dans l'état (elles comptent dans son
empreinte) et le départ est marqué « partiel » : la tranche 0 les formalisera.

Conventions de départ déclarées (pas des règles, voir `PLACEMENT`) : un monstre du Main Deck sur
le terrain prend la première zone principale libre ; le premier monstre de l'Extra Deck prend la
Zone Monstre Extra de gauche, les suivants les zones principales ; une Magie/Piège prend la première
zone Magie/Piège libre. Aucun test actuel ne lit la case (jeu-de-tests-branded.md § 4).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .deck import DeckSource
from .modele import (
    CELLULES_MAGIE, CELLULES_MONSTRE, Cadre, Etat, Instance, MemoireTour, Modification,
    OccupantZoneExtra, ZonesJoueur,
)

CLES_DEPART = {"main", "terrain", "cimetiere", "bannies", "memoire", "phase", "tour", "terrain_adverse"}
PHASES_YAML = {"Phase de Fin": "fin", "Phase Principale 1": "principale_1", "Phase Principale 2": "principale_2"}
VERDICTS = {"legal", "illegal", "non_couvert"}
PLACEMENT = "convention de départ"

_JETON = re.compile(r"^([A-Z][A-Z0-9_]*)(?:\s*\((.*)\))?\s*$")

# Annotations d'exemplaire reconnues : (motif, attributs posés). Lecture du vocabulaire du YAML, pas
# une règle : « Invocation Fusion » dit comment la carte est arrivée, rien de plus.
_ANNOTATIONS = [
    (re.compile(r"Invocation Normale|Invoqué(?:e)? Normalement"),
     dict(arrivee="invocation_normale", arrivee_ce_tour=True)),
    (re.compile(r"Invocation Fusion|Invoqué(?:e)? par Fusion"),
     dict(arrivee="invocation_fusion", arrivee_ce_tour=True, venue_extra_deck=True, correctement_invoquee=True)),
    (re.compile(r"Invocation Synchro"),
     dict(arrivee="invocation_synchro", arrivee_ce_tour=True, venue_extra_deck=True, correctement_invoquee=True)),
    (re.compile(r"Invoqué(?:e)? Spécialement|vient d'être Invoqué(?:e)? Spécialement"),
     dict(arrivee="invocation_speciale", arrivee_ce_tour=True)),
    (re.compile(r"posée face cachée ce tour"), dict(face="cachee", posee_ce_tour=True)),
    (re.compile(r"envoyée? au Cimetière"), dict(envoyee_cimetiere_ce_tour=True)),
    (re.compile(r"en Défense|Position de Défense"), dict(position="defense")),
]
# Fragments purement descriptifs (caractéristiques imprimées, numéro d'exemplaire) : rien à poser.
_DESCRIPTIFS = re.compile(r"^(Syntoniseur(, Niveau \d+)?|Niveau \d+|\d+e exemplaire)$")
# « nom, Type, Attribut et Niveau de MERC jusqu'à la Phase de Fin » (T32).
_NOM_TEMPORAIRE = re.compile(r"^nom(?:, Type, Attribut et Niveau)? de ([A-Z][A-Z0-9_]*) jusqu'à la Phase de Fin$")
_RESTE = re.compile(r"\bpar\b|\bpuis\b|utilisé|matériels?\b|\beffet\b|exemplaire")
# Mémoire : seul fait structuré sans ambiguïté.
_INVOCATION_NORMALE = re.compile(r"^Invocation Normale utilisée")


@dataclass
class Depart:
    test_id: str
    etat: Etat | None = None
    erreurs: list[str] = field(default_factory=list)       # départ incohérent : test inexploitable
    faits_libres: list[str] = field(default_factory=list)  # texte libre gardé dans l'état (D7)
    conventions: list[str] = field(default_factory=list)   # placements et déductions déclarés

    @property
    def complet(self) -> bool:
        return self.etat is not None and not self.faits_libres

    @property
    def valide(self) -> bool:
        return self.etat is not None and not self.erreurs


@dataclass
class JeuDeTests:
    fichier: Path
    sha256: str
    alias: dict[str, str]
    situations: list[dict]


def charger_tests(chemin: Path) -> JeuDeTests:
    import hashlib

    brut = chemin.read_bytes()
    data = yaml.safe_load(brut)
    return JeuDeTests(chemin, hashlib.sha256(brut).hexdigest(), dict(data["cartes"]), list(data["situations"]))


def verifier_jeu(jeu: JeuDeTests, deck: DeckSource, noms_base: set[str] | None = None) -> list[str]:
    """Cohérence des alias et des champs, sans règle : identifiants, alias connus, verdicts permis."""
    erreurs = []
    noms_deck = set(deck.par_nom())
    for alias, nom in jeu.alias.items():
        if nom not in noms_deck:
            erreurs.append(f"alias {alias} → « {nom} » absent du deck source")
        if noms_base is not None and nom not in noms_base:
            erreurs.append(f"alias {alias} → « {nom} » absent de la base de référence")
    if len(set(jeu.alias.values())) != len(jeu.alias):
        erreurs.append("deux alias pour le même nom de carte")
    ids = [s.get("id") for s in jeu.situations]
    for i, n in Counter(ids).items():
        if n > 1:
            erreurs.append(f"identifiant en double : {i}")
    attendus = {f"T{k:02d}" for k in range(1, len(ids) + 1)}
    if set(ids) != attendus:
        erreurs.append(f"identifiants non contigus : manquants {sorted(attendus - set(ids))}")
    for s in jeu.situations:
        sid = s.get("id")
        attendu = s.get("attendu") or {}
        if attendu.get("verdict") not in VERDICTS:
            erreurs.append(f"{sid} : verdict {attendu.get('verdict')!r} inconnu")
        if s.get("perimetre") not in {"pilote", "hors_pilote"}:
            erreurs.append(f"{sid} : périmètre {s.get('perimetre')!r} inconnu")
        for r in s.get("regles") or []:
            if not re.fullmatch(r"R\d{2}", r):
                erreurs.append(f"{sid} : point de règle mal écrit {r!r}")
        # Alias cités dans les listes d'options : doivent tous exister.
        for cle in ("choix", "exclus", "choix_cout_coca", "choix_dessous_du_deck"):
            for jeton in _aplatir(attendu.get(cle)):
                if re.fullmatch(r"[A-Z][A-Z0-9_]+", jeton) and jeton not in jeu.alias:
                    erreurs.append(f"{sid} : alias inconnu {jeton!r} dans attendu.{cle}")
    return erreurs


def _aplatir(valeur) -> list[str]:
    if valeur is None:
        return []
    if isinstance(valeur, str):
        return [valeur]
    if isinstance(valeur, dict):
        return [x for v in valeur.values() for x in _aplatir(v)]
    return [x for v in valeur for x in _aplatir(v)]


def _lire_annotation(texte: str, alias: dict[str, str]) -> tuple[dict, list[Modification], list[str]]:
    """Attributs reconnus, modifications temporaires, et fragments laissés en texte libre."""
    attributs: dict = {}
    modifs: list[Modification] = []
    libres: list[str] = []
    for fragment in (f.strip() for f in texte.split(";")):
        if not fragment:
            continue
        m = _NOM_TEMPORAIRE.match(fragment)
        if m and m.group(1) in alias:
            modifs.append(Modification("nom", alias[m.group(1)], "phase_de_fin"))
            continue
        if _DESCRIPTIFS.match(fragment):
            continue
        reconnu = False
        for motif, poses in _ANNOTATIONS:
            if motif.search(fragment):
                attributs.update(poses)
                reconnu = True
        # Prudence : un fragment non reconnu, ou reconnu mais qui porte un reste (« par BFUSION »,
        # « puis utilisé comme matériel », « 1er effet utilisé ») est gardé en texte libre.
        if not reconnu or _RESTE.search(fragment):
            libres.append(fragment)
    return attributs, modifs, libres


def construire_depart(situation: dict, jeu: JeuDeTests, deck: DeckSource) -> Depart:
    sid = situation["id"]
    d = Depart(sid)
    depart = situation.get("depart") or {}
    inconnues = set(depart) - CLES_DEPART
    if inconnues:
        d.erreurs.append(f"clé(s) de départ inconnue(s) : {sorted(inconnues)}")
    cartes = deck.par_nom()

    def resoudre(jeton: str, zone: str) -> tuple[str, str | None] | None:
        m = _JETON.match(str(jeton))
        if not m or m.group(1) not in jeu.alias:
            d.erreurs.append(f"{zone} : « {jeton} » ne commence pas par un alias connu")
            return None
        return jeu.alias[m.group(1)], m.group(2)

    utilises: Counter[str] = Counter()
    zones: dict[str, list[Instance]] = {"main": [], "cimetiere": [], "bannies": []}
    libres_instances: list[str] = []

    def instance(nom: str, annotation: str | None, zone: str) -> Instance:
        attributs, modifs, libres = _lire_annotation(annotation or "", jeu.alias)
        origine = cartes[nom].zone
        if origine == "extra" and zone in ("cimetiere", "bannies", "terrain"):
            attributs.setdefault("venue_extra_deck", True)
        if zone == "bannies":
            attributs.setdefault("face", "visible")
        for lib in libres:
            libres_instances.append(f"{nom} ({zone}) : {lib}")
        return Instance(carte=nom, modifications=tuple(modifs), notes=tuple(libres), **attributs)

    for zone in ("main", "cimetiere", "bannies"):
        for jeton in depart.get(zone) or []:
            r = resoudre(jeton, zone)
            if r is None:
                continue
            nom, annotation = r
            if zone == "main" and cartes[nom].zone == "extra":
                d.erreurs.append(f"main : {nom} est une carte d'Extra Deck")
            utilises[nom] += 1
            zones[zone].append(instance(nom, annotation, zone))

    # Terrain : cases exactes, selon la convention de départ déclarée.
    cases: list[tuple[str, Instance]] = []
    zme: list[OccupantZoneExtra] = []
    libres_m = list(CELLULES_MONSTRE)
    libres_s = list(CELLULES_MAGIE)
    for jeton in depart.get("terrain") or []:
        r = resoudre(jeton, "terrain")
        if r is None:
            continue
        nom, annotation = r
        utilises[nom] += 1
        inst = instance(nom, annotation, "terrain")
        carte = cartes[nom]
        est_monstre = bool(carte.type) and "Monster" in carte.type
        if inst.face is None:
            inst = _avec(inst, face="visible")
        if est_monstre and carte.zone == "extra":
            if inst.correctement_invoquee is None:
                # Un monstre de l'Extra Deck sur le terrain y est forcément arrivé par une invocation :
                # déduction de cohérence, déclarée.
                inst = _avec(inst, correctement_invoquee=True)
                d.conventions.append(f"{nom} : sur le terrain, donc « correctement invoqué » (déduction)")
            if not zme:
                zme.append(OccupantZoneExtra("ZME_G", 0, inst))
                d.conventions.append(f"{nom} → ZME_G ({PLACEMENT})")
                continue
        if est_monstre:
            if not libres_m:
                d.erreurs.append("terrain : plus de zone Monstre libre")
                continue
            cellule = libres_m.pop(0)
        else:
            if not libres_s:
                d.erreurs.append("terrain : plus de zone Magie/Piège libre")
                continue
            cellule = libres_s.pop(0)
        cases.append((cellule, inst))
        d.conventions.append(f"{nom} → {cellule} ({PLACEMENT})")

    adverses: list[tuple[str, Instance]] = []
    for k, jeton in enumerate(depart.get("terrain_adverse") or []):
        # Monstre générique de l'adversaire (hors pilote) : pas une carte du deck.
        adverses.append((CELLULES_MONSTRE[k], Instance(carte=f"<générique : {jeton}>", proprietaire=1,
                                                       face="visible", position="attaque")))
        d.conventions.append(f"terrain adverse : « {jeton} » → carte générique en {CELLULES_MONSTRE[k]}")

    # Deck et Extra Deck : la liste moins ce qui est placé ailleurs (convention du YAML).
    deck_instances, extra_instances = [], []
    for nom, carte in cartes.items():
        reste = carte.nombre - utilises[nom]
        if reste < 0:
            d.erreurs.append(f"{nom} : {utilises[nom]} exemplaires placés, {carte.nombre} dans la liste")
            continue
        if carte.zone == "main":
            deck_instances += [Instance(carte=nom)] * reste
        elif carte.zone == "extra":
            extra_instances += [Instance(carte=nom)] * reste
        # side : hors de l'état (seules les cartes placées depuis le Side Deck y entrent, ex. LAVA)

    # Mémoire du tour.
    invocation_normale = False
    faits: list[str] = []
    for fait in depart.get("memoire") or []:
        if _INVOCATION_NORMALE.match(str(fait)):
            invocation_normale = True
        else:
            faits.append(str(fait))
    deja = [nom for _, i in cases for nom in [i.carte] if i.arrivee == "invocation_normale"]
    if deja and not invocation_normale:
        invocation_normale = True
        d.conventions.append(f"Invocation Normale marquée utilisée : {deja[0]} est annoncé Invoqué Normalement")

    phase_yaml = depart.get("phase")
    phase = "principale_1"
    if phase_yaml is not None:
        if phase_yaml not in PHASES_YAML:
            d.erreurs.append(f"phase inconnue : {phase_yaml!r}")
        else:
            phase = PHASES_YAML[phase_yaml]

    d.faits_libres = faits + libres_instances
    if d.erreurs:
        return d
    try:
        d.etat = Etat(
            cadre=Cadre(tour=int(depart.get("tour", 1)), phase=phase, invocation_normale_utilisee=invocation_normale),
            joueurs=(
                ZonesJoueur(
                    main=tuple(zones["main"]), deck=tuple(deck_instances), extra=tuple(extra_instances),
                    cimetiere=tuple(zones["cimetiere"]), bannies=tuple(zones["bannies"]), cases=tuple(cases),
                ),
                ZonesJoueur(cases=tuple(adverses), main_connue=False, deck_connu=False),
            ),
            zones_monstre_extra=tuple(zme),
            memoire=MemoireTour(faits_libres=tuple(faits)),
        )
    except ValueError as exc:
        d.erreurs.append(f"état refusé par le modèle : {exc}")
    return d


def _avec(inst: Instance, **changements) -> Instance:
    from dataclasses import replace

    return replace(inst, **changements)


def cartes_citees(texte: str, alias: dict[str, str]) -> list[str]:
    """Alias cités dans un texte libre (action), dans l'ordre d'apparition."""
    return [a for a in re.findall(r"\b[A-Z][A-Z0-9_]+\b", texte) if a in alias]
