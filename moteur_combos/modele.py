"""Structures de données du moteur de combos : état, exemplaires, mémoire du tour, cible, arrêt.

Traduction en code des définitions de `docs/moteur-combos/definitions-et-schema.md` (§ 2).
**Aucune règle de jeu ici** : ces classes disent ce qu'un état peut contenir et comment on
l'écrit sous forme canonique, jamais ce qui est légal. La consommation des limites, les verrous,
la légalité d'une action sont de la tranche 0 (TOK-90).

Choix d'écriture :
- tout est immuable (`frozen=True`) : un état est une valeur, comparée par son empreinte ;
- un exemplaire n'a pas d'identité propre : deux exemplaires aux attributs égaux sont
  interchangeables (§ 2.3, point 1), la forme canonique trie les multi-ensembles ;
- le terrain garde la case exacte de chaque carte (D3 révisée, « entre-deux », 18/11).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from typing import Any, Iterable

# ── Vocabulaire fermé ─────────────────────────────────────────────────────────────────────────

PHASES = ("pioche", "standby", "principale_1", "combat", "principale_2", "fin")

# Zones à forme de multi-ensemble, par joueur (§ 2.1 B). Le Cimetière en fait partie : son ordre
# ne sert qu'à l'arbitre (relecture 1, question ouverte 2).
ZONES_MULTI = ("main", "deck", "extra", "cimetiere", "bannies")

CELLULES_MONSTRE = ("M1", "M2", "M3", "M4", "M5")
CELLULES_MAGIE = ("S1", "S2", "S3", "S4", "S5")
CELLULE_TERRAIN = "TERRAIN"
# Zones Monstre Extra : communes aux deux joueurs, elles appartiennent au terrain (§ 2.1 B).
ZONES_MONSTRE_EXTRA = ("ZME_G", "ZME_D")
TOUTES_LES_CELLULES = CELLULES_MONSTRE + ZONES_MONSTRE_EXTRA + CELLULES_MAGIE + (CELLULE_TERRAIN,)

# Géométrie, vue depuis le joueur 0 : colonne de chaque case. Donnée enregistrée, pas une règle.
COLONNE = {
    **{c: i for i, c in enumerate(CELLULES_MONSTRE, start=1)},
    **{c: i for i, c in enumerate(CELLULES_MAGIE, start=1)},
    "ZME_G": 2,
    "ZME_D": 4,
}

# D3 révisée : options de placement d'une Invocation depuis l'Extra Deck (une option de l'action).
OPTIONS_PLACEMENT_EXTRA = ("zone_monstre_extra", "zone_principale")

# D3 révisée : les colonnes ne sont énumérées que si une carte du deck lit la position. Liste
# DÉCLARÉE (décision D3 du 16/11, cartes nommées par elle), pas déduite des textes.
CARTES_LISANT_LA_POSITION = frozenset({"Sprind the Irondash Dragon", "Albion the Sanctifire Dragon"})

# Formes de « une fois par tour » (relecture 1 : trois formes ; deux variantes lues dans les textes).
FORMES_LIMITE = ("activation_par_nom", "par_nom_effet", "par_nom_carte", "invocation_par_nom", "par_exemplaire")
FORMES_MEMOIRE = FORMES_LIMITE[:4]  # par_exemplaire est un attribut de l'exemplaire (bloc C)

MOTIFS_ARRET = (
    "fin_forcee", "fin_volontaire", "tronque_profondeur", "retour_etat_connu",
    "boucle", "cible_atteinte", "non_couvert", "hors_perimetre",
)

STATUTS_FORMALISATION = ("non_traitee", "brouillon", "formalisee", "verifiee", "non_formalisable")
STATUTS_EXECUTABLES = ("formalisee", "verifiee")  # D5 / § 3.4 : les autres → « non couvert »

ARRIVEES = (
    "invocation_normale", "pose", "invocation_speciale", "invocation_fusion", "invocation_synchro", "autre",
)
POSITIONS = ("attaque", "defense")
FACES = ("visible", "cachee")

ZONES_CIBLE = ("terrain", "main", "cimetiere", "bannies")


def _verifier(valeur: Any, permis: Iterable[Any], quoi: str) -> None:
    if valeur not in permis:
        raise ValueError(f"{quoi} inconnu : {valeur!r} (permis : {', '.join(map(str, permis))})")


def empreinte(objet: Any) -> str:
    """SHA-256 d'un JSON canonique (clés triées, sans espaces superflus)."""
    texte = json.dumps(objet, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(texte.encode()).hexdigest()


# ── Bloc C : attributs d'un exemplaire ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Modification:
    """Modification temporaire d'une caractéristique (nom, Type, Attribut, Niveau, ATK…)."""
    champ: str
    valeur: str
    echeance: str  # 'fin_de_tour', 'phase_de_fin', 'permanente'…

    def canon(self) -> list:
        return [self.champ, self.valeur, self.echeance]


@dataclass(frozen=True)
class Instance:
    """Un exemplaire de carte. Pas d'identifiant : les exemplaires égaux sont interchangeables."""
    carte: str                                   # nom imprimé
    proprietaire: int = 0
    face: str | None = None                      # visible / cachee (terrain, bannies) ; None ailleurs
    position: str | None = None                  # attaque / defense (monstre sur le terrain)
    arrivee: str | None = None                   # comment elle est arrivée là (None : non précisé)
    arrivee_ce_tour: bool = False
    venue_extra_deck: bool = False
    correctement_invoquee: bool | None = None    # None : non précisé (ou sans objet)
    envoyee_cimetiere_ce_tour: bool = False
    posee_ce_tour: bool = False                  # Magie/Piège posée face cachée ce tour
    modifications: tuple[Modification, ...] = ()
    limites_exemplaire: tuple[int, ...] = ()     # n° d'effet « Once per turn » consommés (bloc C)
    restrictions: tuple[str, ...] = ()           # ex. « ne peut pas utiliser cet effet au tour suivant »
    compteurs: tuple[tuple[str, int], ...] = ()
    notes: tuple[str, ...] = ()                  # texte libre non formalisé (D7) : compte dans l'empreinte

    def __post_init__(self) -> None:
        _verifier(self.proprietaire, (0, 1), "propriétaire")
        if self.face is not None:
            _verifier(self.face, FACES, "face")
        if self.position is not None:
            _verifier(self.position, POSITIONS, "position")
        if self.arrivee is not None:
            _verifier(self.arrivee, ARRIVEES, "arrivée")

    def nom_courant(self) -> str:
        """Nom actuel : le dernier « nom » modifié, sinon le nom imprimé (§ 2.1, test 3)."""
        noms = [m.valeur for m in self.modifications if m.champ == "nom"]
        return noms[-1] if noms else self.carte

    def canon(self) -> dict:
        return {
            "carte": self.carte,
            "proprietaire": self.proprietaire,
            "face": self.face,
            "position": self.position,
            "arrivee": self.arrivee,
            "arrivee_ce_tour": self.arrivee_ce_tour,
            "venue_extra_deck": self.venue_extra_deck,
            "correctement_invoquee": self.correctement_invoquee,
            "envoyee_cimetiere_ce_tour": self.envoyee_cimetiere_ce_tour,
            "posee_ce_tour": self.posee_ce_tour,
            "modifications": [m.canon() for m in self.modifications],
            "limites_exemplaire": sorted(self.limites_exemplaire),
            "restrictions": sorted(self.restrictions),
            "compteurs": sorted([list(c) for c in self.compteurs]),
            "notes": list(self.notes),
        }


_CLES_TRI: dict[Instance, str] = {}


def _cle_tri(i: Instance) -> str:
    """Clé de tri d'un exemplaire : son JSON canonique, mémoïsé (TOK-140). `Instance` est figée et hachable : deux
    exemplaires égaux ont la même clé. Sans la mémoïsation, ce JSON coûtait ≈ 40 % du temps d'exploration."""
    c = _CLES_TRI.get(i)
    if c is None:
        c = json.dumps(i.canon(), sort_keys=True, ensure_ascii=False)
        if len(_CLES_TRI) >= 500_000:
            _CLES_TRI.clear()
        _CLES_TRI[i] = c
    return c


def _multi(instances: Iterable[Instance]) -> list[dict]:
    """Multi-ensemble canonique : liste triée des exemplaires (les copies égales se confondent). Même résultat que le
    tri des `canon()` par leur JSON (test `test_multi_memoise_identique`)."""
    return [i.canon() for i in sorted(instances, key=_cle_tri)]


# ── Bloc B : zones ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ZonesJoueur:
    main: tuple[Instance, ...] = ()
    deck: tuple[Instance, ...] = ()               # partie mélangée (multi-ensemble)
    deck_dessus: tuple[Instance, ...] = ()        # segment connu, du dessus vers le bas
    deck_dessous: tuple[Instance, ...] = ()       # segment connu, de la dernière carte vers le haut
    extra: tuple[Instance, ...] = ()
    cimetiere: tuple[Instance, ...] = ()
    bannies: tuple[Instance, ...] = ()
    cases: tuple[tuple[str, Instance], ...] = ()  # M1-M5, S1-S5, TERRAIN de ce joueur
    main_connue: bool = True                      # information cachée (§ 2.5) : False chez l'adversaire
    deck_connu: bool = True

    def __post_init__(self) -> None:
        vues = [c for c, _ in self.cases]
        for c in vues:
            if c not in CELLULES_MONSTRE + CELLULES_MAGIE + (CELLULE_TERRAIN,):
                raise ValueError(f"case de joueur invalide : {c!r} (les Zones Monstre Extra sont communes)")
        if len(vues) != len(set(vues)):
            raise ValueError(f"deux cartes dans la même case : {sorted(vues)}")

    def case(self, cellule: str) -> Instance | None:
        return dict(self.cases).get(cellule)

    def toutes_les_instances(self) -> list[Instance]:
        return [
            *self.main, *self.deck, *self.deck_dessus, *self.deck_dessous, *self.extra,
            *self.cimetiere, *self.bannies, *(i for _, i in self.cases),
        ]

    def canon(self) -> dict:
        return {
            "main": _multi(self.main),
            "deck": _multi(self.deck),
            "deck_dessus": [i.canon() for i in self.deck_dessus],
            "deck_dessous": [i.canon() for i in self.deck_dessous],
            "extra": _multi(self.extra),
            "cimetiere": _multi(self.cimetiere),
            "bannies": _multi(self.bannies),
            "cases": {c: i.canon() for c, i in sorted(self.cases)},
            "main_connue": self.main_connue,
            "deck_connu": self.deck_connu,
        }


@dataclass(frozen=True)
class OccupantZoneExtra:
    """Occupant d'une Zone Monstre Extra : la zone est commune, l'occupant porte son contrôleur."""
    cellule: str
    controleur: int
    instance: Instance

    def __post_init__(self) -> None:
        _verifier(self.cellule, ZONES_MONSTRE_EXTRA, "Zone Monstre Extra")
        _verifier(self.controleur, (0, 1), "contrôleur")


# ── Bloc A : cadre ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Cadre:
    tour: int = 1
    joueur_actif: int = 0
    phase: str = "principale_1"
    points_de_vie: tuple[int, int] = (8000, 8000)
    invocation_normale_utilisee: bool = False
    chaine: tuple[str, ...] = ()                 # vide dans un état stable
    declenches_en_attente: tuple[str, ...] = ()  # idem
    fenetre_adverse: str = "aucune_reponse"      # réservé (§ 2.5)

    def __post_init__(self) -> None:
        if self.tour < 1:
            raise ValueError("le tour commence à 1")
        _verifier(self.joueur_actif, (0, 1), "joueur actif")
        _verifier(self.phase, PHASES, "phase")

    def canon(self) -> dict:
        return {
            "tour": self.tour,
            "joueur_actif": self.joueur_actif,
            "phase": self.phase,
            "points_de_vie": list(self.points_de_vie),
            "invocation_normale_utilisee": self.invocation_normale_utilisee,
            "chaine": list(self.chaine),
            "declenches_en_attente": list(self.declenches_en_attente),
            "fenetre_adverse": self.fenetre_adverse,
        }


# ── Bloc D : mémoire du tour ───────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LimiteConsommee:
    """Limite « une fois par tour » consommée, clé sur le nom cité par la clause."""
    forme: str
    nom: str
    effet: int | None = None   # numéro d'effet, seulement pour par_nom_effet

    def __post_init__(self) -> None:
        _verifier(self.forme, FORMES_MEMOIRE, "forme de limite de la mémoire du tour")
        if (self.forme == "par_nom_effet") != (self.effet is not None):
            raise ValueError("le numéro d'effet est requis pour par_nom_effet, et seulement pour elle")

    def canon(self) -> list:
        return [self.forme, self.nom, self.effet]


@dataclass(frozen=True)
class Verrou:
    """Restriction qui dure (« you cannot Special Summon from the Extra Deck, except… »).
    `cle` est une étiquette formelle posée par la formalisation ; le lot 18 n'en interprète aucune."""
    source: str
    cle: str
    echeance: str = "fin_de_tour"

    def canon(self) -> list:
        return [self.source, self.cle, self.echeance]


@dataclass(frozen=True)
class EffetDiffere:
    """Effet qui se résoudra plus tard, éventuellement à un autre tour (`Gold Sarcophagus`)."""
    source: str
    echeance: str
    description: str

    def canon(self) -> list:
        return [self.source, self.echeance, self.description]


@dataclass(frozen=True)
class MemoireTour:
    limites: frozenset[LimiteConsommee] = frozenset()
    verrous: tuple[Verrou, ...] = ()
    invocations_extra: tuple[tuple[str, str], ...] = ()   # (nom, type d'invocation), dans l'ordre
    evenements: frozenset[str] = frozenset()
    effets_differes: tuple[EffetDiffere, ...] = ()
    effets_appliques: frozenset[str] = frozenset()
    faits_libres: tuple[str, ...] = ()                    # texte libre non formalisé (D7)

    def canon(self) -> dict:
        return {
            "limites": sorted((lim.canon() for lim in self.limites), key=json.dumps),
            "verrous": sorted((v.canon() for v in self.verrous), key=json.dumps),
            "invocations_extra": [list(x) for x in self.invocations_extra],  # l'ordre compte (T12)
            "evenements": sorted(self.evenements),
            "effets_differes": sorted((e.canon() for e in self.effets_differes), key=json.dumps),
            "effets_appliques": sorted(self.effets_appliques),
            "faits_libres": sorted(self.faits_libres),
        }


# ── L'état ─────────────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Etat:
    cadre: Cadre = field(default_factory=Cadre)
    joueurs: tuple[ZonesJoueur, ZonesJoueur] = field(
        default_factory=lambda: (ZonesJoueur(), ZonesJoueur(main_connue=False, deck_connu=False))
    )
    zones_monstre_extra: tuple[OccupantZoneExtra, ...] = ()
    memoire: MemoireTour = field(default_factory=MemoireTour)

    def __post_init__(self) -> None:
        if len(self.joueurs) != 2:
            raise ValueError("un état a exactement deux joueurs")
        cellules = [o.cellule for o in self.zones_monstre_extra]
        if len(cellules) != len(set(cellules)):
            raise ValueError("deux cartes dans la même Zone Monstre Extra")

    # Forme canonique et empreintes (§ 2.3)
    def forme_canonique(self) -> dict:
        return {
            "A": self.cadre.canon(),
            "B": {
                "joueurs": [j.canon() for j in self.joueurs],
                "zones_monstre_extra": {
                    o.cellule: {"controleur": o.controleur, "instance": o.instance.canon()}
                    for o in sorted(self.zones_monstre_extra, key=lambda o: o.cellule)
                },
            },
            "D": self.memoire.canon(),
        }

    def json_canonique(self) -> str:
        return json.dumps(self.forme_canonique(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    def empreinte(self) -> str:
        return hashlib.sha256(self.json_canonique().encode()).hexdigest()

    def plateau(self) -> dict:
        """« Plateau final » pour l'affichage (§ 2.3) : terrain, main, Cimetière, bannies, sans la mémoire."""
        b = self.forme_canonique()["B"]
        return {
            "joueurs": [
                {k: j[k] for k in ("main", "cimetiere", "bannies", "cases")} for j in b["joueurs"]
            ],
            "zones_monstre_extra": b["zones_monstre_extra"],
        }

    def empreinte_plateau(self) -> str:
        return empreinte(self.plateau())

    def est_stable(self) -> bool:
        return not self.cadre.chaine and not self.cadre.declenches_en_attente

    def remplacer(self, **changements: Any) -> "Etat":
        return replace(self, **changements)


# ── Cible d'exploration et arrêt (§ 2.4 d, e) ──────────────────────────────────────────────────

@dataclass(frozen=True)
class ConditionCible:
    zone: str
    carte: str
    minimum: int = 1

    def __post_init__(self) -> None:
        _verifier(self.zone, ZONES_CIBLE, "zone de cible")
        if self.minimum < 1:
            raise ValueError("une condition de cible demande au moins 1 exemplaire")

    def canon(self) -> dict:
        return {"zone": self.zone, "carte": self.carte, "minimum": self.minimum}


@dataclass(frozen=True)
class CibleExploration:
    """Plateau final visé (relecture 1). Structure seulement : l'algorithme qui l'utilise est à venir."""
    description: str
    conditions: tuple[ConditionCible, ...]

    def __post_init__(self) -> None:
        if not self.conditions:
            raise ValueError("une cible sans condition n'en est pas une")

    def conditions_json(self) -> str:
        return json.dumps([c.canon() for c in self.conditions], ensure_ascii=False)


def verifier_motif_arret(motif: str) -> str:
    _verifier(motif, MOTIFS_ARRET, "motif d'arrêt")
    return motif
