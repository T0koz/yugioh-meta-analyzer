"""Fiches des cartes du deck : caractéristiques imprimées, noms, archétypes, mentions, matériels (tranche 0).

Une fiche réunit ce que le moteur peut savoir d'une carte **sans la formaliser** : ce qui est imprimé
(type, Attribut, Type de monstre, Niveau, ATK/DEF), les noms et archétypes (calculés au lot 18 depuis le
nom et les clauses « always treated as »), les noms cités entre guillemets (« mentionne », R04) et la
ligne de matériels d'un monstre Fusion découpée en éléments (R05, R06, R24).

Lecture du texte, pas règle : un élément de matériel qui n'est qu'un nom entre guillemets (`"Fallen of
Albaz"`) se lit sans formalisation ; un élément décrit en mots (« 1 Beast, Beast-Warrior, or Winged Beast
monster ») ne se lit **que** par la formalisation de la carte (`cartes.py`). Sans elle, le moteur dit
« indéterminé », jamais « possible ».

La formalisation n'est rattachée à une fiche que si l'empreinte du texte lu est celle sur laquelle elle a
été écrite : un errata la désactive (la carte redevient « non couverte »).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .deck import DeckSource, TexteCarte, etiquettes, vocabulaire_archetypes

_GUILLEMETS = re.compile(r'"([^"]+)"')
_TRAITE = re.compile(r'\(This card is always treated as[^)]*\)')
_QUANTITE = re.compile(r"^(\d+)(\+?)\s")


@dataclass(frozen=True)
class ElementMateriel:
    """Un élément de la ligne de matériels (séparateur « + »)."""
    texte: str
    minimum: int
    plus: bool              # « 2+ » : au moins `minimum`, sans maximum
    nom: str | None         # élément qui n'est qu'un nom entre guillemets


def lire_materiels(texte: str) -> tuple[ElementMateriel, ...]:
    """Première ligne d'un monstre Fusion ou Synchro, découpée sur « + »."""
    premiere = texte.split("\n", 1)[0].strip()
    elements = []
    for brut in (e.strip() for e in premiere.split(" + ")):
        m_nom = re.fullmatch(r'"([^"]+)"', brut)
        m_qte = _QUANTITE.match(brut)
        if m_nom:
            elements.append(ElementMateriel(brut, 1, False, m_nom.group(1)))
        elif m_qte:
            elements.append(ElementMateriel(brut, int(m_qte.group(1)), m_qte.group(2) == "+", None))
        else:
            elements.append(ElementMateriel(brut, 1, False, None))
    return tuple(elements)


@dataclass(frozen=True)
class Fiche:
    nom: str
    zone_deck: str                 # main / extra / side
    type_carte: str                # « Effect Monster », « Spell Card »…
    frame: str | None              # effect, fusion, synchro, spell, trap…
    attribut: str | None
    race: str | None               # Type de monstre, ou sous-type de Magie/Piège (« Normal », « Quick-Play »)
    niveau: int | None
    atk: int | None
    defense: int | None
    text_sha256: str
    noms: frozenset[str]
    archetypes: frozenset[str]
    mentions: frozenset[str]       # noms cités entre guillemets, hors nom imprimé et clause « treated as »
    materiels: tuple[ElementMateriel, ...] = ()
    formalisation: object | None = None   # cartes.Formalisation, si l'empreinte correspond
    formalisation_ecartee: str | None = None  # raison, si une formalisation existe mais ne s'applique pas

    @property
    def est_monstre(self) -> bool:
        return "Monster" in self.type_carte

    @property
    def est_magie(self) -> bool:
        return self.type_carte.startswith("Spell")

    @property
    def est_piege(self) -> bool:
        return self.type_carte.startswith("Trap")

    @property
    def est_fusion(self) -> bool:
        return self.frame == "fusion"

    @property
    def est_extra(self) -> bool:
        return self.frame in {"fusion", "synchro", "xyz", "link"}

    @property
    def magie_normale(self) -> bool:
        return self.est_magie and self.race == "Normal"

    def mentionne_comme_materiel(self, nom: str) -> bool:
        """R05 : le nom figure dans la ligne de matériels (élément nommé)."""
        return any(e.nom == nom for e in self.materiels)

    def bornes_materiels(self) -> tuple[int, float]:
        """Nombre de matériels possible (min, max), lu dans la ligne de matériels."""
        mini = sum(e.minimum for e in self.materiels)
        maxi = float("inf") if any(e.plus for e in self.materiels) else mini
        return mini, maxi

    @property
    def declaree(self) -> bool:
        """Tous les effets de la carte sont déclarés (le moteur sait quand ils peuvent s'activer)."""
        return self.formalisation is not None


@dataclass
class Catalogue:
    fiches: dict[str, Fiche] = field(default_factory=dict)

    def __getitem__(self, nom: str) -> Fiche:
        return self.fiches[nom]

    def get(self, nom: str) -> Fiche | None:
        return self.fiches.get(nom)


def mentions(nom: str, texte: str) -> frozenset[str]:
    sans_clause = _TRAITE.sub("", texte)
    return frozenset(m for m in _GUILLEMETS.findall(sans_clause) if m != nom)


def construire_catalogue(deck: DeckSource, textes: dict[int, TexteCarte], noms_base: set[str],
                         formalisations: dict[str, object] | None = None) -> Catalogue:
    """Une fiche par carte du deck. `formalisations` : nom imprimé → cartes.Formalisation."""
    formalisations = formalisations or {}
    vocab = vocabulaire_archetypes([t.texte for t in textes.values()], noms_base)
    cat = Catalogue()
    for c in deck.cartes:
        t = textes.get(c.card_id)
        if t is None:
            continue
        tags = etiquettes(c.nom, t.texte, vocab)
        f = formalisations.get(c.nom)
        ecartee = None
        if f is not None and getattr(f, "text_sha256") != t.sha256:
            ecartee = "texte changé depuis la formalisation (errata ?) : carte non couverte"
            f = None
        cat.fiches[c.nom] = Fiche(
            nom=c.nom, zone_deck=c.zone, type_carte=c.type or "", frame=t.frame_type, attribut=c.attribut,
            race=c.race, niveau=c.niveau, atk=c.atk, defense=c.defense, text_sha256=t.sha256,
            noms=frozenset(tag for tag, k, _ in tags if k == "nom"),
            archetypes=frozenset(tag for tag, k, _ in tags if k == "archetype"),
            mentions=mentions(c.nom, t.texte),
            materiels=lire_materiels(t.texte) if t.frame_type in {"fusion", "synchro"} else (),
            formalisation=f, formalisation_ecartee=ecartee,
        )
    return cat
