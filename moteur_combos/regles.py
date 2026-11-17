"""Moteur de règles, tranche 0 (TOK-90) : les règles strictement nécessaires à un combo Branded.

Codé ici, et rien d'autre :
- **Invocation Normale** (une par tour, monstre de Niveau 4 ou moins depuis la main, zone libre) ;
- **Invocation Spéciale** par effet et **Invocation Fusion** (matériels envoyés au Cimetière, un matériel par
  élément de la ligne, R24 ; placement Zone Monstre Extra / zone principale, D3 ; position) ;
- **activation** : condition, limites « une fois par tour » (les cinq formes enregistrées au lot 18), **coût**
  payé à l'activation, effet qui doit pouvoir se résoudre (R01, R14), verrous ;
- **chaîne simple** : maillons, fenêtre de réponse (vitesses : une Magie Normale ne répond à rien), résolution
  en ordre inverse, effets déclenchés « If » activés dans une nouvelle chaîne après la chaîne en cours (R10) ;
- **« non couvert »** (D5) : une carte sans formalisation qui serait jouée, déplacée ou choisie arrête tout
  avec `non_couvert` ; une option dont la légalité dépend d'une carte non formalisée est rangée à part
  (« liste peut-être incomplète ») ; une carte non formalisée qui reste en main, sur le terrain ou au
  Cimetière et **aurait pu** agir est inscrite dans les **réserves** du résultat.

**Ajouté au lot C2 (J1, TOK-118)** : effets déclenchés **simultanés** (R22 : le joueur choisit l'ordre et peut
n'en activer qu'une partie ; les obligatoires d'abord), Invocation **Synchro**, Invocation Spéciale **par
procédure** (sans chaîne, R15), coûts par **Sacrifice** et par **bannissement**, défausse, destruction, retour au
Deck (mélangé ou au-dessous), **cibles** choisies à l'activation, **annulation** d'un effet de la chaîne, chaîne
**sans réponse** (R19), Magie Jeu-Rapide posée ce tour (R18), caractéristiques modifiées (nom, Type, Attribut,
Niveau, ATK), effets annulés, cartes insensibles, verrous `extra_aucune` et `extra_fusion_synchro_n8`, pioche
(branche de hasard), **Phase de Fin** (passage, effets de Phase de Fin, retours différés, effet obligatoire en
attente : fin de tour illégale, R23), Phase de Combat refusée au tour 1 (R31).

Non codé (renvoie `non_couvert`, jamais un résultat faux) : Invocation par Tribut, Pose, effets « When » qui
ratent leur moment, Phase de Combat, tour adverse (`hors_perimetre`).

Interface : `Moteur(catalogue).jouer(etat, declaration, script)` joue **une transition** (§ 2.2 des
définitions) et rend un `Resultat`. Chaque décision du joueur passe par le `Script` : le moteur calcule la
liste des options légales, le script en choisit une ; une réponse absente de la liste est illégale.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from inspect import signature
from itertools import combinations, permutations
from typing import Any

from .catalogue import Catalogue, Fiche
from .modele import (
    CELLULES_MAGIE, CELLULES_MONSTRE, ZONES_MONSTRE_EXTRA, Etat, Instance, LimiteConsommee, Modification,
    OccupantZoneExtra, Verrou,
)

NON_CODEE = "non_codee"            # résolution d'un effet déclaré mais pas encore formalisée
HORS_PERIMETRE = "hors_perimetre"  # résolution qui suppose l'adversaire (tour adverse, ses monstres)
NE_PAS_ACTIVER = "ne pas activer"
PASSER = "passer"

PHASES_PRINCIPALES = ("principale_1", "principale_2")

# Couverture (lot C2) : (carte, n° d'effet) dont la résolution, la procédure ou l'effet continu a réellement joué.
# Lue par le harnais pour le statut `formalisee` (un effet jamais exercé par un test reste `brouillon`).
EXERCES: set[tuple[str, int]] = set()
ZONES_PUBLIQUES = ("main", "terrain", "cimetiere", "bannies")


# ── Résultats et exceptions ────────────────────────────────────────────────────────────────────

class Illegal(Exception):
    """L'action (ou le choix) n'est pas dans la liste des actions légales."""


class NonCouvert(Exception):
    """Une carte non formalisée interviendrait : le moteur refuse de donner un résultat (D5)."""


class HorsPerimetre(Exception):
    """L'action suppose l'adversaire ou un autre tour : hors du pilote (§ 2.5)."""


class ErreurScript(Exception):
    """Le script ne correspond pas aux décisions demandées : erreur du test, pas du moteur."""


@dataclass(frozen=True)
class Option:
    valeur: str
    couverte: bool = True          # False : légale, mais la suite ferait intervenir une carte non formalisée
    raison: str | None = None      # pourquoi elle n'est pas couverte
    donnees: Any = None


@dataclass
class Decision:
    type: str                      # type de pas (cb_step.step_type)
    question: str                  # 'activer_declenche', 'reponse', 'carte', 'fusion', 'materiaux'…
    options: list[Option]          # légales
    indeterminees: list[Option] = field(default_factory=list)  # légalité inconnue (carte non formalisée)
    exclues: dict[str, str] = field(default_factory=dict)      # candidates écartées, avec la raison
    choix: str | None = None
    automatique: bool = False

    def valeurs(self) -> list[str]:
        return [o.valeur for o in self.options]

    def option(self, valeur: str) -> Option | None:
        return next((o for o in self.options if o.valeur == valeur), None)


@dataclass(frozen=True)
class Evenement:
    type: str                      # invocation_normale, invocation_speciale, envoyee_cimetiere, ajoutee_main
    carte: str
    zone: str                      # zone d'arrivée : 'terrain', 'cimetiere', 'main'…
    cellule: str | None = None
    detail: tuple[tuple[str, str], ...] = ()

    def a(self, cle: str) -> str | None:
        return dict(self.detail).get(cle)


@dataclass(frozen=True)
class Declaration:
    type: str                      # 'invocation_normale' | 'activer' | 'declenche' | 'invocation_synchro'
    #                                | 'invocation_procedure' | 'phase_de_fin' | 'fin_de_tour' | 'phase_combat'
    carte: str
    effet: int | None = None
    evenement: Evenement | None = None   # 'declenche' : l'événement qui vient d'avoir lieu (état de départ)


@dataclass
class Maillon:
    carte: str
    effet: int
    lieu: tuple[str, str | None]   # (zone, cellule) de la carte au moment de l'activation
    vitesse: int
    est_effet_de_monstre: bool
    donnees: dict = field(default_factory=dict)
    annule: bool = False           # effet annulé (Ash Blossom) : la résolution n'a pas lieu
    sans_reponse: bool = False     # « Neither player can activate cards or effects in response » (R19)
    categories: frozenset = frozenset()


@dataclass
class Pas:
    type: str
    libelle: str
    cartes: list[tuple[str, str, str | None, str | None, str | None]] = field(default_factory=list)
    # (carte, rôle, zone de départ, zone d'arrivée, case d'arrivée) — rôles de cb_step_card


@dataclass
class Resultat:
    verdict: str                   # legal | illegal | non_couvert | hors_perimetre
    raison: str | None
    etat: Etat | None
    pas: list[Pas]
    decisions: list[Decision]
    reserves: set[str]             # cartes non formalisées en jeu qui auraient pu agir (D5, cas 2)
    incomplet: set[str]            # options de légalité inconnue : « liste peut-être incomplète » (D5, cas 3)
    notes: list[str]
    faits_libres: list[str]

    def decision(self, question: str, rang: int = 0) -> Decision:
        trouvees = [d for d in self.decisions if d.question == question]
        return trouvees[rang]


def _option(p, nom: str, quoi: str) -> "Option":
    """Option qui désigne une carte : non couverte si la carte n'est pas formalisée (D5)."""
    couverte = p.declaree(nom)
    return Option(nom, couverte, None if couverte else f"non formalisée : {quoi}, ses effets sont inconnus", nom)


def _arite(fn) -> int:
    try:
        return len(signature(fn).parameters)
    except (TypeError, ValueError):
        return 2


class Script:
    """Réponses prévues aux décisions, dans l'ordre : [(question, valeur), …]."""

    def __init__(self, reponses: list[tuple[str, str]] | None = None):
        self.reponses = list(reponses or [])

    def repondre(self, d: Decision) -> str | None:
        if self.reponses and self.reponses[0][0] == d.question:
            return self.reponses.pop(0)[1]
        return None


# ── Partie : l'état en cours de transition ─────────────────────────────────────────────────────

class Partie:
    def __init__(self, catalogue: Catalogue, etat: Etat, script: Script):
        self.cat = catalogue
        self.etat = etat
        self.script = script
        self.pas: list[Pas] = []
        self.decisions: list[Decision] = []
        self.reserves: set[str] = set()
        self.incomplet: set[str] = set()
        self.notes: list[str] = []
        self.chaine: list[Maillon] = []
        self.evenements: list[Evenement] = []

    # ── Fiches ─────────────────────────────────────────────────────────────────────────────────
    def fiche(self, nom: str) -> Fiche:
        f = self.cat.get(nom)
        if f is None:
            raise NonCouvert(f"{nom} : aucune fiche (carte hors du deck chargé)")
        return f

    def declaree(self, nom: str) -> bool:
        f = self.cat.get(nom)
        return f is not None and f.declaree

    def exiger_declaree(self, nom: str, quoi: str) -> None:
        if not self.declaree(nom):
            f = self.cat.get(nom)
            raison = (f.formalisation_ecartee if f is not None and f.formalisation_ecartee else "non formalisée")
            raise NonCouvert(f"{nom} : {raison} ({quoi})")

    def noms_de(self, inst: Instance) -> frozenset[str]:
        f = self.cat.get(inst.carte)
        noms = set(f.noms if f else {inst.carte})
        courant = inst.nom_courant()
        if courant != inst.carte:
            noms = {courant} | (set(self.cat[courant].noms) if self.cat.get(courant) else set())
        return frozenset(noms)

    def archetypes_de(self, inst: Instance) -> frozenset[str]:
        f = self.cat.get(inst.nom_courant()) or self.cat.get(inst.carte)
        return f.archetypes if f else frozenset()

    # ── Caractéristiques courantes (modifications temporaires comprises, lot C2) ───────────────
    def _modif(self, inst: Instance, champ: str):
        valeurs = [m.valeur for m in inst.modifications if m.champ == champ]
        return valeurs[-1] if valeurs else None

    def race_de(self, inst: Instance) -> str | None:
        return self._modif(inst, "race") or (self.cat[inst.carte].race if self.cat.get(inst.carte) else None)

    def attribut_de(self, inst: Instance) -> str | None:
        return self._modif(inst, "attribut") or (self.cat[inst.carte].attribut if self.cat.get(inst.carte) else None)

    def niveau_de(self, inst: Instance) -> int | None:
        v = self._modif(inst, "niveau")
        if v is not None:
            return int(v)
        f = self.cat.get(inst.carte)
        return f.niveau if f else None

    def atk_de(self, inst: Instance, sur_le_terrain: bool = True) -> int | None:
        """ATK courante sur le terrain (gains compris) ; ATK imprimée ailleurs."""
        f = self.cat.get(inst.carte)
        base = f.atk if f else None
        if base is None or not sur_le_terrain:
            return base
        bonus = getattr(f.formalisation, "bonus_atk", None) if f.declaree else None
        gain = bonus(self, inst) if bonus is not None and not self.effets_annules(inst) else 0
        if gain:
            EXERCES.add((inst.carte, 1))
        return base + gain + sum(int(m.valeur) for m in inst.modifications if m.champ == "atk_gain")

    def est_syntoniseur(self, inst: Instance) -> bool:
        f = self.cat.get(inst.carte)
        return f is not None and "Tuner" in f.type_carte

    def effets_annules(self, inst: Instance) -> bool:
        return any(m.champ == "effets_annules" for m in inst.modifications)

    def insensible(self, inst: Instance, source: str, active: bool = True) -> bool:
        """La carte est-elle insensible à un effet de `source` (`Dogma`, `Titaniklad`) ? Lu dans la formalisation."""
        f = self.cat.get(inst.carte)
        fn = getattr(f.formalisation, "insensible", None) if f is not None and f.declaree else None
        r = bool(fn and not self.effets_annules(inst) and fn(self, inst, source, active))
        if r:
            EXERCES.add((inst.carte, getattr(f.formalisation, "effet_insensible", 1)))
        return r

    def lieu_de(self, inst: Instance) -> tuple[str, str | None] | None:
        for c, i in self.monstres() + [x for x in self.j.cases if x[0] not in CELLULES_MONSTRE]:
            if i is inst:
                return ("terrain", c)
        return None

    def controle_rien(self) -> bool:
        return not self.monstres() and not self.j.cases

    # ── Zones du joueur 0 (le pilote ne joue que le tour du joueur 0) ──────────────────────────
    @property
    def j(self):
        return self.etat.joueurs[0]

    def _poser_joueur(self, j) -> None:
        self.etat = replace(self.etat, joueurs=(j, self.etat.joueurs[1]))

    def monstres(self, joueur: int = 0) -> list[tuple[str, Instance]]:
        cases = [(c, i) for c, i in self.etat.joueurs[joueur].cases if c in CELLULES_MONSTRE]
        zme = [(o.cellule, o.instance) for o in self.etat.zones_monstre_extra if o.controleur == joueur]
        return cases + zme

    def instance_en(self, lieu: tuple[str, str | None], nom: str) -> Instance | None:
        zone, cellule = lieu
        if zone == "terrain":
            for c, i in self.monstres() + [(c, i) for c, i in self.j.cases if c not in CELLULES_MONSTRE]:
                if c == cellule and i.carte == nom:
                    return i
            return None
        return next((i for i in self._multi(zone) if i.carte == nom), None)

    def _multi(self, zone: str) -> tuple[Instance, ...]:
        j = self.j
        if zone == "deck":
            return j.deck + j.deck_dessus + j.deck_dessous
        return getattr(j, zone)

    def cases_monstre_libres(self) -> list[str]:
        prises = {c for c, _ in self.j.cases}
        return [c for c in CELLULES_MONSTRE if c not in prises]

    def cases_magie_libres(self) -> list[str]:
        prises = {c for c, _ in self.j.cases}
        return [c for c in CELLULES_MAGIE if c not in prises]

    def zme_disponible(self) -> str | None:
        """Première Zone Monstre Extra libre, si le joueur n'en occupe aucune (une seule par joueur)."""
        if any(o.controleur == 0 for o in self.etat.zones_monstre_extra):
            return None
        prises = {o.cellule for o in self.etat.zones_monstre_extra}
        return next((c for c in ZONES_MONSTRE_EXTRA if c not in prises), None)

    def retirer(self, zone: str, nom: str, cellule: str | None = None) -> Instance:
        """Retire un exemplaire (les copies égales sont interchangeables)."""
        j = self.j
        if zone == "terrain":
            for o in self.etat.zones_monstre_extra:
                if o.cellule == cellule and o.instance.carte == nom:
                    self.etat = replace(self.etat, zones_monstre_extra=tuple(
                        x for x in self.etat.zones_monstre_extra if x is not o))
                    return o.instance
            for c, i in j.cases:
                if c == cellule and i.carte == nom:
                    self._poser_joueur(replace(j, cases=tuple(x for x in j.cases if x[0] != c)))
                    return i
            raise ErreurScript(f"{nom} absent de la case {cellule}")
        if zone == "deck":
            for attr in ("deck", "deck_dessus", "deck_dessous"):
                seq = list(getattr(j, attr))
                for k, i in enumerate(seq):
                    if i.carte == nom:
                        del seq[k]
                        self._poser_joueur(replace(j, **{attr: tuple(seq)}))
                        return i
            raise ErreurScript(f"{nom} absent du Deck")
        seq = list(getattr(j, zone))
        for k, i in enumerate(seq):
            if i.carte == nom:
                del seq[k]
                self._poser_joueur(replace(j, **{zone: tuple(seq)}))
                return i
        raise ErreurScript(f"{nom} absent de la zone {zone}")

    def ajouter(self, zone: str, inst: Instance, cellule: str | None = None) -> None:
        j = self.j
        if zone == "terrain":
            if cellule in ZONES_MONSTRE_EXTRA:
                self.etat = replace(self.etat, zones_monstre_extra=self.etat.zones_monstre_extra
                                    + (OccupantZoneExtra(cellule, 0, inst),))
            else:
                self._poser_joueur(replace(j, cases=j.cases + ((cellule, inst),)))
            return
        self._poser_joueur(replace(j, **{zone: getattr(j, zone) + (inst,)}))

    def melanger(self) -> None:
        """Après une recherche ou un prélèvement dans le Deck : l'ordre connu disparaît (R02)."""
        j = self.j
        if j.deck_dessus or j.deck_dessous:
            self._poser_joueur(replace(j, deck=j.deck + j.deck_dessus + j.deck_dessous, deck_dessus=(),
                                       deck_dessous=()))
        self.pas.append(Pas("resoudre", "Deck mélangé"))

    # ── Mouvements (avec contrôle « non couvert ») ─────────────────────────────────────────────
    def _quitte_terrain_bannie(self, zone: str, inst: Instance) -> bool:
        """`Cocatorium` : « banish it when it leaves the field » (restriction portée par l'exemplaire)."""
        return zone == "terrain" and "bannir_si_quitte_terrain" in inst.restrictions

    def _evenement_memoire(self, cle: str) -> None:
        m = self.etat.memoire
        if cle not in m.evenements:
            self.etat = replace(self.etat, memoire=replace(m, evenements=m.evenements | {cle}))

    def envoyer_cimetiere(self, zone: str, nom: str, cellule: str | None, role: str, comme: str) -> None:
        self.exiger_declaree(nom, f"envoyée au Cimetière ({comme}) : ses effets déclenchés sont inconnus")
        ancienne = self.retirer(zone, nom, cellule)
        f = self.fiche(nom)
        if self._quitte_terrain_bannie(zone, ancienne):
            self._bannir_instance(zone, nom, ancienne, "visible", role, comme + " (bannie à la place : quitte le terrain)")
            return
        correcte = ancienne.correctement_invoquee if (f.est_extra and zone in ("terrain", "bannies")) else (
            False if zone == "extra" else None)
        self.ajouter("cimetiere", Instance(carte=nom, venue_extra_deck=f.est_extra, correctement_invoquee=correcte,
                                           envoyee_cimetiere_ce_tour=True))
        self.evenements.append(Evenement("envoyee_cimetiere", nom, "cimetiere",
                                         detail=(("depuis", zone), ("comme", comme))))
        if f.est_fusion:
            self._evenement_memoire("fusion_envoyee_cimetiere")
        if zone == "extra":
            self.evenements.append(Evenement("quitte_extra", nom, "cimetiere"))
        self.pas[-1].cartes.append((nom, role, zone, "cimetiere", None))

    def _bannir_instance(self, zone: str, nom: str, ancienne: Instance, face: str, role: str, comme: str) -> None:
        f = self.fiche(nom)
        correcte = ancienne.correctement_invoquee if (f.est_extra and zone in ("terrain", "cimetiere")) else (
            False if zone == "extra" else None)
        self.ajouter("bannies", Instance(carte=nom, face=face, venue_extra_deck=f.est_extra,
                                         correctement_invoquee=correcte))
        self.evenements.append(Evenement("bannie", nom, "bannies", detail=(("depuis", zone), ("face", face),
                                                                           ("comme", comme))))
        if zone == "extra":
            self.evenements.append(Evenement("quitte_extra", nom, "bannies"))
        self.pas[-1].cartes.append((nom, role, zone, "bannies", None))

    def bannir(self, zone: str, nom: str, cellule: str | None, role: str, comme: str, face: str = "visible") -> None:
        self.exiger_declaree(nom, f"bannie ({comme}) : ses effets déclenchés sont inconnus")
        ancienne = self.retirer(zone, nom, cellule)
        self._bannir_instance(zone, nom, ancienne, face, role, comme)

    def detruire(self, nom: str, cellule: str, role: str, source: str) -> None:
        """Destruction par un effet : la carte va au Cimetière (ou est bannie, Cocatorium). `Branded Opening`
        (effet 2) peut remplacer la destruction d'un monstre Fusion du joueur (effet de remplacement)."""
        self.exiger_declaree(nom, "détruite : ses effets sont inconnus")
        inst = self.instance_en(("terrain", cellule), nom)
        f = self.fiche(nom)
        if inst is not None and f.est_fusion and cellule not in CELLULES_MAGIE:
            remplacants = [i for i in self.j.cimetiere if i.carte == "Branded Opening" and self.declaree(i.carte)]
            fo = self.cat["Branded Opening"].formalisation if remplacants else None
            if fo is not None and not self.limite_consommee(fo.effet(2), remplacants[0]):
                o = self.choisir(Decision("choisir", "remplacement", [
                    Option("bannir Branded Opening"), Option("ne pas remplacer")]))
                EXERCES.add(("Branded Opening", 2))
                if o.valeur == "bannir Branded Opening":
                    self.pas.append(Pas("resoudre", f"Branded Opening bannie à la place de la destruction de {nom}"))
                    self.consommer_limites(fo.effet(2), ("cimetiere", None), "Branded Opening")
                    self.bannir("cimetiere", "Branded Opening", None, "cout", "remplacement")
                    return
        self.pas.append(Pas("resoudre", f"{nom} détruite ({source})"))
        self.envoyer_cimetiere("terrain", nom, cellule, role, "detruite")

    def defausser(self, nom: str, role: str = "cout") -> None:
        self.envoyer_cimetiere("main", nom, None, role, "defausse")

    def sacrifier(self, nom: str, cellule: str, role: str = "cout") -> None:
        self.envoyer_cimetiere("terrain", nom, cellule, role, "sacrifice")

    def vers_deck(self, zone: str, nom: str, cellule: str | None, role: str, ou: str = "melange") -> None:
        """Mélanger dans le Deck (`ou` = 'melange') ou placer au-dessous (`ou` = 'dessous', R02). Une carte de
        l'Extra Deck retourne à l'Extra Deck."""
        self.exiger_declaree(nom, "renvoyée dans le Deck : ses effets sont inconnus")
        self.retirer(zone, nom, cellule)
        f = self.fiche(nom)
        j = self.j
        if f.est_extra:
            self._poser_joueur(replace(j, extra=j.extra + (Instance(carte=nom),)))
            arrivee = "extra"
        elif ou == "dessous":
            self._poser_joueur(replace(j, deck_dessous=(Instance(carte=nom),) + j.deck_dessous))
            arrivee = "deck (dessous)"
        else:
            self._poser_joueur(replace(j, deck=j.deck + (Instance(carte=nom),)))
            arrivee = "deck"
        self.pas[-1].cartes.append((nom, role, zone, arrivee, None))

    def ajouter_main(self, zone: str, nom: str, role: str) -> None:
        self.exiger_declaree(nom, "ajoutée à la main : ses effets sont inconnus")
        self.retirer(zone, nom)
        self.ajouter("main", Instance(carte=nom))
        self.evenements.append(Evenement("ajoutee_main", nom, "main", detail=(("depuis", zone),)))
        self.pas[-1].cartes.append((nom, role, zone, "main", None))

    def piocher(self) -> None:
        """Pioche : branche de hasard (§ 2.2, « Subir le hasard »), une option par nom de carte du Deck."""
        noms = sorted({i.carte for i in self._multi("deck")})
        if not noms:
            self.notes.append("pioche impossible : Deck vide")
            return
        o = self.choisir(Decision("hasard", "pioche", [_option(self, n, "piochée") for n in noms]))
        self.pas.append(Pas("resoudre", f"pioche (hasard) : {o.valeur}"))
        self.ajouter_main("deck", o.valeur, "piochee")

    def invoquer_specialement(self, zone: str, nom: str, cellule_depart: str | None, cellule: str, position: str,
                              mode: str = "invocation_speciale", restrictions: tuple[str, ...] = ()) -> None:
        self.exiger_declaree(nom, "Invoquée Spécialement : ses effets sont inconnus")
        f = self.fiche(nom)
        if getattr(f.formalisation, "un_seul_controle", False) and any(
                i.carte == nom and i.face == "visible" for _, i in self.monstres()):
            raise Illegal(f"« You can only control 1 \"{nom}\" »")
        self.retirer(zone, nom, cellule_depart)
        inst = Instance(carte=nom, face="visible", position=position, arrivee=mode, arrivee_ce_tour=True,
                        venue_extra_deck=f.est_extra, correctement_invoquee=True if f.est_extra else None,
                        restrictions=restrictions)
        self.ajouter("terrain", inst, cellule)
        if zone == "extra":
            m = self.etat.memoire
            self.etat = replace(self.etat, memoire=replace(m, invocations_extra=m.invocations_extra + (
                (nom, mode.replace("invocation_", "")),)))
            self.evenements.append(Evenement("quitte_extra", nom, "terrain", cellule))
        self.evenements.append(Evenement("invocation_speciale", nom, "terrain", cellule,
                                         detail=(("depuis", zone), ("mode", mode))))
        self.pas[-1].cartes.append((nom, "deplacee", zone, "terrain", cellule))

    def invoquer_dans_case_libre(self, zone: str, nom: str, cellule_depart: str | None = None,
                                 position: str | None = None, restrictions: tuple[str, ...] = ()) -> bool:
        """Invocation Spéciale par effet vers une zone Monstre principale (monstre qui ne vient pas de l'Extra
        Deck : jamais la Zone Monstre Extra). Position choisie par le joueur si l'effet ne l'impose pas."""
        libres = self.cases_monstre_libres()
        if not libres:
            self.notes.append(f"{nom} : plus de zone Monstre libre à la résolution")
            return False
        if position is None:
            position = self.choisir(Decision("choisir", "position", [Option("attaque"), Option("defense")])).valeur
        self.pas.append(Pas("resoudre", f"{nom} : {zone} → terrain ({position})"))
        self.invoquer_specialement(zone, nom, cellule_depart, libres[0], position, restrictions=restrictions)
        return True

    def modifier(self, lieu: tuple[str, str | None], nom: str, modifs: tuple) -> None:
        inst = self.retirer(lieu[0], nom, lieu[1])
        self.ajouter(lieu[0], replace(inst, modifications=inst.modifications + tuple(modifs)), lieu[1])

    # ── Décisions ──────────────────────────────────────────────────────────────────────────────
    def choisir(self, d: Decision) -> Option:
        for o in d.indeterminees:
            if d.question == "reponse":
                self._reserve_si_non_declaree(o)   # carte en jeu qui aurait pu répondre (D5, cas 2)
            else:
                self.incomplet.add(o.valeur)       # liste peut-être incomplète (D5, cas 3)
        reponse = self.script.repondre(d)
        if reponse is None:
            if len(d.options) == 1 and not d.indeterminees:
                d.choix, d.automatique = d.options[0].valeur, True
                self.decisions.append(d)
                return d.options[0]
            raise ErreurScript(f"décision « {d.question} » sans réponse prévue (options : {d.valeurs()}, "
                               f"indéterminées : {[o.valeur for o in d.indeterminees]})")
        d.choix = reponse
        self.decisions.append(d)
        self.pas.append(Pas(d.type, f"{d.question} : {reponse}"))
        o = d.option(reponse)
        if o is not None:
            if not o.couverte:
                raise NonCouvert(f"{d.question} « {reponse} » : {o.raison}")
            return o
        ind = next((x for x in d.indeterminees if x.valeur == reponse), None)
        if ind is not None:
            raise NonCouvert(f"{d.question} « {reponse} » : légalité indéterminée ({ind.raison})")
        if reponse in d.exclues:
            raise Illegal(f"{d.question} « {reponse} » : {d.exclues[reponse]}")
        raise Illegal(f"{d.question} « {reponse} » absent des options légales {d.valeurs()}")

    def _reserve_si_non_declaree(self, o: Option) -> None:
        nom = o.donnees if isinstance(o.donnees, str) else None
        if nom and not self.declaree(nom):
            self.reserves.add(nom)

    def noter_reserves(self) -> None:
        """Cartes non formalisées dans une zone où elles pourraient agir (D5, cas 2) : le résultat est donné,
        mais avec cette réserve écrite."""
        for zone in ("main", "cimetiere", "bannies"):
            for i in getattr(self.j, zone):
                if not self.declaree(i.carte):
                    self.reserves.add(i.carte)
        for _, i in self.monstres() + list(self.j.cases):
            if not self.declaree(i.carte):
                self.reserves.add(i.carte)

    # ── Limites « une fois par tour » ──────────────────────────────────────────────────────────
    def limite_consommee(self, effet, inst: Instance | None) -> str | None:
        for forme, nom in effet.limites:
            if forme == "par_exemplaire":
                if inst is not None and effet.numero in inst.limites_exemplaire:
                    return f"« Once per turn » de cet exemplaire déjà utilisé (effet {effet.numero})"
                continue
            cle = LimiteConsommee(forme, nom, effet.numero if forme == "par_nom_effet" else None)
            if cle in self.etat.memoire.limites:
                return f"limite « {forme} » de « {nom} » déjà consommée ce tour"
        return None

    def consommer_limites(self, effet, lieu: tuple[str, str | None], nom_carte: str) -> None:
        m = self.etat.memoire
        nouvelles = set(m.limites)
        for forme, nom in effet.limites:
            if forme == "par_exemplaire":
                self._marquer_exemplaire(lieu, nom_carte, effet.numero)
            else:
                nouvelles.add(LimiteConsommee(forme, nom, effet.numero if forme == "par_nom_effet" else None))
        self.etat = replace(self.etat, memoire=replace(self.etat.memoire, limites=frozenset(nouvelles)))

    def _marquer_exemplaire(self, lieu, nom, numero) -> None:
        zone, cellule = lieu
        inst = self.retirer(zone, nom, cellule)
        self.ajouter(zone, replace(inst, limites_exemplaire=inst.limites_exemplaire + (numero,)), cellule)

    def ajouter_verrou(self, v: Verrou) -> None:
        m = self.etat.memoire
        if v not in m.verrous:
            self.etat = replace(self.etat, memoire=replace(m, verrous=m.verrous + (v,)))

    def verrou_interdit_extra(self, f: Fiche) -> str | None:
        """Un verrou interdit-il d'Invoquer Spécialement `f` depuis l'Extra Deck ?"""
        for v in self.etat.memoire.verrous:
            if v.cle == "extra_fusion_seulement":
                if not f.est_fusion:
                    return f"verrou de {v.source} : Extra Deck = monstres Fusion seulement"
            elif v.cle == "extra_aucune":
                return f"verrou de {v.source} : aucune Invocation Spéciale depuis l'Extra Deck"
            elif v.cle == "extra_fusion_synchro_n8":
                if not (f.frame in ("fusion", "synchro") and f.niveau == 8):
                    return f"verrou de {v.source} : Extra Deck = Fusion ou Synchro de Niveau 8 seulement"
            else:
                raise NonCouvert(f"verrou « {v.cle} » de {v.source} non codé")
        if self.etat.memoire.faits_libres:
            # Un verrou écrit en phrases n'est pas lu : on ne conclut pas à « possible ».
            for fait in self.etat.memoire.faits_libres:
                if "verrou" in fait.lower():
                    raise NonCouvert(f"verrou non formalisé dans la mémoire du tour : « {fait} »")
        return None

    # ── Fusion ─────────────────────────────────────────────────────────────────────────────────
    def analyser_fusions(self, candidats: list[Fiche], materiaux: list[tuple[str, str | None, Instance]],
                         nombre_exact: int | None, obligatoire: tuple[str, str | None, Instance] | None = None
                         ) -> tuple[list[Option], list[Option], dict[str, str]]:
        """Pour chaque monstre Fusion : possible (paires couvertes), indéterminé ou impossible (raison).
        `materiaux` : (zone, cellule, exemplaire) disponibles ; `obligatoire` : matériel imposé (« including
        this card »)."""
        possibles, indeterminees, exclues = [], [], {}
        for f in candidats:
            mini, maxi = f.bornes_materiels()
            if nombre_exact is not None and not (mini <= nombre_exact <= maxi):
                exclues[f.nom] = f"demande {mini}{'+' if maxi == float('inf') else ''} matériels, l'effet en utilise {nombre_exact}"
                continue
            if len(materiaux) < mini:
                exclues[f.nom] = f"{len(materiaux)} matériel(s) disponible(s), il en faut au moins {mini}"
                continue
            try:
                interdit = self.verrou_interdit_extra(f)
            except NonCouvert as exc:
                indeterminees.append(Option(f.nom, False, str(exc), f.nom))
                continue
            if interdit:
                exclues[f.nom] = interdit
                continue
            if getattr(f.formalisation, "un_seul_controle", False) and f.declaree and any(
                    i.carte == f.nom for _, i in self.monstres()):
                exclues[f.nom] = f"« You can only control 1 \"{f.nom}\" »"
                continue
            paires, inconnues, raison = self._affectations(f, materiaux, obligatoire, nombre_exact)
            if paires:
                couverte = f.declaree
                possibles.append(Option(f.nom, couverte, None if couverte else "monstre Fusion non formalisé",
                                        {"paires": paires, "inconnues": inconnues}))
            elif inconnues or raison is None:
                indeterminees.append(Option(f.nom, False, raison or "matériels non formalisés", f.nom))
            else:
                exclues[f.nom] = raison
        return possibles, indeterminees, exclues

    def _restriction_materiel(self, inst: Instance) -> tuple[bool, str | None]:
        """(refusé, inconnu) : `Albion` ne sert pas de matériel (R24) ; carte non formalisée → inconnu."""
        fi = self.cat.get(inst.carte)
        if fi is None or not fi.declaree:
            return False, f"{inst.carte} non formalisée : restrictions de matériel inconnues"
        if getattr(fi.formalisation, "interdit_materiel_fusion", False):
            EXERCES.add((inst.carte, 1))
            return True, None
        return False, None

    def _affectations(self, f: Fiche, materiaux, obligatoire, nombre_exact: int | None = None):
        """Affectations matériel → élément (un matériel par élément, R24). Renvoie (couvertes, indéterminées,
        raison d'impossibilité ou None si la ligne n'est pas lisible sans formalisation). Un prédicat renvoie
        True, False ou None (caractéristique non précisée dans l'état : « indéterminé »)."""
        elements = list(f.materiels)
        fo = f.formalisation if f.declaree else None
        groupe = getattr(fo, "materiels_groupe", None)
        couvertes, inconnues, vus = [], [], set()

        def retenir(choisis, inconnu):
            libelle = " + ".join(f"{inst.carte} ({zone})" for zone, _, inst in choisis)
            if libelle in vus:
                return
            vus.add(libelle)
            (inconnues if inconnu else couvertes).append((libelle, choisis, inconnu))

        if groupe is not None:
            # Ligne décrite en mots pour l'ensemble (« 2 monsters with the same Type… », « 2+ Fusion Monsters
            # with different Attributes ») : le prédicat porte sur le groupe entier.
            mini, maxi = f.bornes_materiels()
            if nombre_exact is not None:
                mini = maxi = nombre_exact
            maxi = int(min(maxi, len(materiaux)))
            for k in range(mini, maxi + 1):
                for combo in combinations(range(len(materiaux)), k):
                    choisis = [materiaux[i] for i in combo]
                    if obligatoire is not None and obligatoire not in choisis:
                        continue
                    verdict = groupe(self, [(self.cat.get(i.carte), i) for _, _, i in choisis])
                    if verdict is False:
                        continue
                    inconnu = None if verdict else "caractéristique d'un matériel non précisée dans l'état"
                    refuse = False
                    for _, _, inst in choisis:
                        r, inc = self._restriction_materiel(inst)
                        refuse |= r
                        inconnu = inconnu or inc
                    if not refuse:
                        retenir(choisis, inconnu)
            if not couvertes and not inconnues:
                return [], [], "aucune combinaison de matériels ne remplit la ligne"
            return couvertes, inconnues, None

        if any(e.minimum != 1 or e.plus for e in elements):
            return [], [], None  # élément « 2 monstres… » sans prédicat de groupe : lisible seulement formalisé
        predicats = getattr(fo, "materiels", None) if fo is not None else None
        for e in elements:
            if e.nom and not any(e.nom in self.noms_de(i) for _, _, i in materiaux):
                noms = [x.nom for x in elements if x.nom]
                return [], [], f"aucun monstre « {noms[0]} » parmi les matériels disponibles"
        if predicats is None:
            return [], [("?", "ligne de matériels non formalisée")], None
        for combo in permutations(range(len(materiaux)), len(elements)):
            choisis = [materiaux[k] for k in combo]
            if obligatoire is not None and obligatoire not in choisis:
                continue
            ok, inconnu = True, None
            for e, pred, (zone, cellule, inst) in zip(elements, predicats, choisis):
                fi = self.cat.get(inst.carte)
                if e.nom:
                    if e.nom not in self.noms_de(inst):
                        ok = False
                        break
                else:
                    v = pred(fi, inst, self) if fi is not None and _arite(pred) == 3 else (
                        pred(fi, inst) if fi is not None else False)
                    if v is False:
                        ok = False
                        break
                    if v is None:
                        inconnu = inconnu or f"{inst.carte} : caractéristique non précisée dans l'état"
                r, inc = self._restriction_materiel(inst)
                if r:
                    ok = False
                    break
                inconnu = inconnu or inc
            if ok:
                retenir(choisis, inconnu)
        return couvertes, inconnues, ("aucune combinaison de matériels ne remplit la ligne" if not inconnues else None)

    # ── Synchro (lot C2) ───────────────────────────────────────────────────────────────────────
    def analyser_synchro(self, f: Fiche) -> tuple[list, list, str | None]:
        """Ensembles de matériels d'une Invocation Synchro : 1 Syntoniseur (de Niveau imposé si la ligne le dit)
        + 1 ou plus non-Syntoniseurs, monstres face visible du terrain, somme des Niveaux = Niveau du Synchro."""
        fo = f.formalisation
        niveau_synt = getattr(fo, "synchro_niveau_syntoniseur", None)
        monstres = [("terrain", c, i) for c, i in self.monstres() if i.face == "visible"]
        couvertes, inconnues = [], []
        for k in range(2, len(monstres) + 1):
            for combo in combinations(monstres, k):
                synt = [m for m in combo if self.est_syntoniseur(m[2])]
                if len(synt) != 1:
                    continue
                if niveau_synt is not None and self.niveau_de(synt[0][2]) != niveau_synt:
                    continue
                niveaux = [self.niveau_de(m[2]) for m in combo]
                if None in niveaux or sum(niveaux) != f.niveau:
                    continue
                libelle = " + ".join(f"{i.carte} ({c})" for _, c, i in combo)
                inconnu = next((f"{i.carte} non formalisée : restrictions de matériel inconnues"
                                for _, _, i in combo if not self.declaree(i.carte)), None)
                (inconnues if inconnu else couvertes).append((libelle, list(combo), inconnu))
        raison = None if (couvertes or inconnues) else (
            "aucun ensemble de matériels : 1 Syntoniseur" + (f" de Niveau {niveau_synt}" if niveau_synt else "")
            + f" + 1 ou plus non-Syntoniseurs, Niveaux totalisant {f.niveau}")
        return couvertes, inconnues, raison

    def placements_extra(self, liberes: int = 0) -> list[str]:
        out = []
        if self.zme_disponible():
            out.append("zone_monstre_extra")
        if self.cases_monstre_libres() or liberes:
            out.append("zone_principale")
        return out

    def placer_depuis_extra(self, f: Fiche, mode: str) -> None:
        """Placement (Zone Monstre Extra / zone principale, D3) et position, puis Invocation depuis l'Extra Deck."""
        placements = self.placements_extra()
        if not placements:
            raise Illegal("aucune zone libre pour un monstre de l'Extra Deck")
        p = self.choisir(Decision("placer", "placement", [Option(x) for x in placements]))
        cellule = self.zme_disponible() if p.valeur == "zone_monstre_extra" else self.cases_monstre_libres()[0]
        pos = self.choisir(Decision("choisir", "position", [Option("attaque"), Option("defense")]))
        self.pas.append(Pas("resoudre", f"{mode.replace('_', ' ')} de {f.nom}"))
        self.invoquer_specialement("extra", f.nom, None, cellule, pos.valeur, mode=mode)

    def invoquer_par_fusion(self, f: Fiche, choisis) -> None:
        """Matériels au Cimetière, puis Invocation Fusion depuis l'Extra Deck (placement et position décidés)."""
        self.pas.append(Pas("resoudre", f"matériels de {f.nom}"))
        depuis_deck = False
        for zone, cellule, inst in choisis:
            self.envoyer_cimetiere(zone, inst.carte, cellule, "materiel", "materiel_fusion")
            depuis_deck |= zone == "deck"
        if depuis_deck:
            self.melanger()
        self.placer_depuis_extra(f, "invocation_fusion")
        # Mémoire des matériels (Titaniklad : « combined original Levels of the monsters used »).
        niveaux = sum(self.cat[i.carte].niveau or 0 for _, _, i in choisis if self.cat.get(i.carte))
        cell = next((c for c, i in self.monstres() if i.carte == f.nom and i.arrivee == "invocation_fusion"
                     and i.arrivee_ce_tour), None)
        if cell is not None:
            self.modifier(("terrain", cell), f.nom, (Modification("materiaux", str(len(choisis)), "permanente"),
                                                     Modification("niveaux_materiaux", str(niveaux), "permanente")))

    def fusionner(self, candidats: list[Fiche], materiaux, nombre_exact: int | None, exclues_avant: dict | None = None,
                  obligatoire=None) -> None:
        """Résolution commune des effets « Fusion Summon 1 … using … » : choix du monstre, puis des matériels."""
        possibles, indeterminees, exclues = self.analyser_fusions(candidats, materiaux, nombre_exact, obligatoire)
        exclues = {**(exclues_avant or {}), **exclues}
        if not possibles:
            if indeterminees:
                self.choisir(Decision("choisir", "fusion", [], indeterminees, exclues))
            self.notes.append("aucune Invocation Fusion possible à la résolution")
            return
        o = self.choisir(Decision("choisir", "fusion", possibles, indeterminees, exclues))
        paires = o.donnees["paires"]
        inconnues = [Option(lib, False, raison, None) for lib, _, raison in o.donnees["inconnues"]]
        om = self.choisir(Decision("choisir", "materiaux", [Option(lib, True, None, ch) for lib, ch, _ in paires],
                                   inconnues))
        self.invoquer_par_fusion(self.cat[o.valeur], om.donnees)

    # ── Activation ─────────────────────────────────────────────────────────────────────────────
    def legalite(self, nom: str, effet, lieu, evenement: Evenement | None = None) -> str | None:
        """None si l'activation est légale ; sinon la raison. NonCouvert / HorsPerimetre si indécidable."""
        inst = self.instance_en(lieu, nom)
        if inst is None:
            return f"{nom} n'est pas en {lieu[0]}"
        if lieu[0] not in effet.zones:
            return f"l'effet {effet.numero} de {nom} ne s'active pas depuis la zone {lieu[0]}"
        f = self.fiche(nom)
        if lieu[0] == "terrain" and f.est_monstre and self.effets_annules(inst):
            return f"les effets de {nom} sont annulés"
        if effet.genre == "activation_carte" and lieu[0] == "terrain":
            if inst.face != "cachee":
                return f"{nom} est déjà face visible sur le terrain"
            if inst.posee_ce_tour and f.race == "Quick-Play":
                return "une Magie Jeu-Rapide posée ne s'active pas le tour où elle a été posée (R18)"
        phase = self.etat.cadre.phase
        if effet.genre == "fin" and phase != "fin":
            return "effet de Phase de Fin : il ne s'active que pendant la Phase de Fin"
        if effet.genre != "fin" and effet.phases and phase not in effet.phases:
            return f"ne s'active que pendant : {', '.join(effet.phases)}"
        raison = self.limite_consommee(effet, inst)
        if raison:
            return raison
        if effet.condition is not None:
            raison = effet.condition(self, lieu, nom)
            if raison:
                return raison
        if effet.genre == "activation_carte" and lieu[0] == "main" and not self.cases_magie_libres():
            return "aucune zone Magie/Piège libre"
        if effet.cout is not None and not effet.cout(self, lieu, nom):
            return "coût impossible à payer"
        if effet.cible is not None and not effet.cible(self, lieu, nom):
            return "aucune cible valide"
        if effet.possible is not None:
            possible = effet.possible(self, lieu, nom)
            if possible is False:
                return "l'effet ne peut rien faire à la résolution (R01)"
            if possible is None:
                raise NonCouvert(f"effet {effet.numero} de {nom} : résolution indécidable (cartes non formalisées)")
        return None

    def activer(self, nom: str, effet, lieu) -> None:
        """Activation légale : poser la Magie, payer le coût, choisir la cible, consommer les limites, ouvrir le
        maillon."""
        f = self.fiche(nom)
        self.pas.append(Pas("declarer", f"activation : {nom} (effet {effet.numero})", [(nom, "acteur", lieu[0], None, None)]))
        if effet.genre == "activation_carte" and lieu[0] == "main":
            cellule = self.cases_magie_libres()[0]
            inst = self.retirer("main", nom)
            self.ajouter("terrain", replace(inst, face="visible"), cellule)
            lieu = ("terrain", cellule)
            self.pas[-1].cartes[-1] = (nom, "acteur", "main", "terrain", cellule)
        elif effet.genre == "activation_carte" and lieu[0] == "terrain":
            inst = self.retirer("terrain", nom, lieu[1])
            self.ajouter("terrain", replace(inst, face="visible", posee_ce_tour=False), lieu[1])
        donnees: dict = {}
        if effet.cout is not None:
            options = effet.cout(self, lieu, nom)
            o = self.choisir(Decision("cout", "cout", options))
            self.pas.append(Pas("cout", f"coût : {o.valeur}"))
            r = o.donnees(self)
            if isinstance(r, dict):
                donnees.update(r)
        if effet.cible is not None:
            options = effet.cible(self, lieu, nom)
            o = self.choisir(Decision("cibler", "cible", options))
            self.pas.append(Pas("cibler", f"cible : {o.valeur}"))
            donnees["cible"] = o.donnees
        self.consommer_limites(effet, lieu, nom)
        if effet.a_l_activation is not None:
            r = effet.a_l_activation(self, lieu, nom)
            if isinstance(r, dict):
                donnees.update(r)
        self.chaine.append(Maillon(nom, effet.numero, lieu, effet.vitesse, f.est_monstre, donnees,
                                   sans_reponse=effet.sans_reponse, categories=frozenset(effet.categories)))
        self.notes.append(f"maillon {len(self.chaine)} : {nom} (effet {effet.numero})")

    def fenetre_reponse(self) -> None:
        """Après chaque maillon : l'adversaire (aucune réponse, pilote), puis le joueur du tour."""
        self.pas.append(Pas("enchainer", f"fenêtre adverse après le maillon {len(self.chaine)} : aucune réponse (pilote)"))
        dernier = self.chaine[-1]
        options, indeterminees, exclues = [Option(PASSER)], [], {}
        for zone in ("main", "terrain", "cimetiere", "bannies"):
            vus = set()
            for lieu, inst in self._instances_publiques(zone):
                cle_vue = (inst.carte, lieu[1])
                if cle_vue in vus:
                    continue
                vus.add(cle_vue)
                f = self.cat.get(inst.carte)
                if f is None:
                    continue
                if not f.declaree:
                    if f.magie_normale and zone == "main":
                        exclues[inst.carte] = "Magie Normale : vitesse 1, elle ne répond à aucun effet"
                    elif f.est_piege and zone == "main":
                        exclues[inst.carte] = "un Piège ne s'active pas depuis la main"
                    elif zone != "bannies":
                        indeterminees.append(Option(inst.carte, False, "non formalisée : effets rapides inconnus",
                                                    inst.carte))
                    continue
                for e in f.formalisation.effets:
                    rapide = e.genre == "rapide" or (e.genre == "activation_carte" and e.vitesse >= 2)
                    libelle = f"{inst.carte}/{e.numero}"
                    if not rapide:
                        if e.genre == "activation_carte" and zone == "main":
                            exclues.setdefault(inst.carte, f"vitesse {e.vitesse} : ne répond à aucun effet")
                        continue
                    if e.vitesse < dernier.vitesse:
                        exclues[libelle] = "vitesse insuffisante"
                        continue
                    if any(o.valeur == libelle for o in options):
                        continue
                    raison = self.legalite(inst.carte, e, lieu)
                    if raison:
                        exclues.setdefault(libelle, raison)
                        continue
                    couverte = e.resolution not in (NON_CODEE,)
                    options.append(Option(libelle, couverte,
                                          None if couverte else "résolution non formalisée", (inst.carte, e, lieu)))
        if dernier.sans_reponse:
            r19 = "aucune carte ni aucun effet ne peut être activé en réponse à cette activation (R19)"
            for o in options[1:] + indeterminees:
                exclues[o.valeur] = r19
            for nom in {i.carte for i in self.j.main}:
                exclues.setdefault(nom, r19)
            options, indeterminees = [Option(PASSER)], []
        o = self.choisir(Decision("enchainer", "reponse", options, indeterminees, exclues))
        if o.valeur != PASSER:
            nom, e, lieu = o.donnees
            self.activer(nom, e, lieu)
            self.fenetre_reponse()

    def _instances_publiques(self, zone: str):
        if zone == "terrain":
            return [(("terrain", c), i) for c, i in self.monstres() + [x for x in self.j.cases if x[0] not in CELLULES_MONSTRE]]
        return [((zone, None), i) for i in getattr(self.j, zone)]

    def resoudre_chaine(self) -> None:
        while self.chaine:
            m = self.chaine.pop()
            f = self.fiche(m.carte)
            e = f.formalisation.effet(m.effet)
            self.pas.append(Pas("resoudre", f"résolution du maillon {len(self.chaine) + 1} : {m.carte} (effet {m.effet})"))
            if m.annule:
                self.notes.append(f"maillon {len(self.chaine) + 1} ({m.carte}) : effet annulé, rien ne se résout")
            else:
                if e.resolution == NON_CODEE:
                    raise NonCouvert(f"résolution de l'effet {m.effet} de {m.carte} non formalisée")
                if e.resolution == HORS_PERIMETRE:
                    raise HorsPerimetre(f"effet {m.effet} de {m.carte} : suppose l'adversaire ou un autre tour")
                e.resolution(self, m)
                EXERCES.add((m.carte, m.effet))
            if e.genre == "activation_carte" and f.est_magie and f.race in ("Normal", "Quick-Play"):
                if self.instance_en(m.lieu, m.carte) is not None:
                    self.pas.append(Pas("resoudre", f"{m.carte} va au Cimetière après résolution"))
                    self.envoyer_cimetiere(m.lieu[0], m.carte, m.lieu[1], "acteur", "apres_resolution")

    # ── Effets déclenchés ──────────────────────────────────────────────────────────────────────
    def _candidats_declenches(self, evenements):
        candidats = []
        for zone in ZONES_PUBLIQUES:
            for lieu, inst in self._instances_publiques(zone):
                f = self.cat.get(inst.carte)
                if f is None or not f.declaree:
                    continue
                for e in f.formalisation.effets:
                    if e.genre != "declenche" or lieu[0] not in e.zones:
                        continue
                    evt = next((ev for ev in evenements if e.declencheur(self, ev, lieu, inst.carte)), None)
                    if evt is None:
                        continue
                    if e.timing == "when":
                        raise NonCouvert(f"{inst.carte} : effet « When » (raté du moment non codé)")
                    libelle = f"{inst.carte}/{e.numero}"
                    if any(c[0] == libelle for c in candidats):
                        continue
                    candidats.append((libelle, inst.carte, e, lieu, evt))
        return candidats

    def declencheurs(self) -> bool:
        """Effets déclenchés par les événements en attente, activés dans une nouvelle chaîne (R10). Plusieurs à la
        fois (R22, lot C2) : le joueur les met en chaîne un par un, dans l'ordre qu'il choisit ; les obligatoires
        doivent y être, les facultatifs peuvent être laissés. Renvoie True si une chaîne a été jouée."""
        evenements, self.evenements = self.evenements, []
        if not evenements:
            return False
        restants = self._candidats_declenches(evenements)
        if not restants:
            return False
        premier_tour = True
        while True:
            options, exclues = [], {}
            for libelle, nom, e, lieu, evt in restants:
                raison = self.legalite(nom, e, lieu, evt)
                if raison:
                    exclues[libelle] = raison
                    if premier_tour:
                        self.notes.append(f"déclencheur {libelle} non activable : {raison}")
                    continue
                couverte = e.resolution != NON_CODEE
                options.append(Option(libelle, couverte, None if couverte else "résolution non formalisée",
                                      (nom, e, lieu)))
            premier_tour = False
            if not options and not exclues:
                break
            obligatoires = [o for o in options if not o.donnees[1].facultatif]
            offertes = options + ([] if obligatoires else [Option(NE_PAS_ACTIVER)])
            o = self.choisir(Decision("declarer", "activer_declenche", offertes, [], exclues))
            if o.valeur == NE_PAS_ACTIVER:
                break
            nom, e, lieu = o.donnees
            self.activer(nom, e, lieu)
            restants = [c for c in restants if c[0] != o.valeur]
            if not restants:
                break
        if not self.chaine:
            return False
        self.fenetre_reponse()
        self.resoudre_chaine()
        return True

    def jouer_declencheurs(self) -> None:
        while self.declencheurs():
            pass

    # ── Déclarations (état stable) ─────────────────────────────────────────────────────────────
    def verifier_etat_ouvert(self, phases: tuple[str, ...] = PHASES_PRINCIPALES) -> None:
        c = self.etat.cadre
        if c.joueur_actif != 0:
            raise HorsPerimetre("tour adverse")
        if c.phase not in phases:
            if c.phase in PHASES_PRINCIPALES + ("fin",):
                raise Illegal(f"phase « {c.phase} » : cette action n'y est pas permise")
            raise NonCouvert(f"phase « {c.phase} » : seules les Phases Principales et la Phase de Fin sont codées")
        if not self.etat.est_stable():
            raise Illegal("une chaîne est en cours")

    def invocation_normale(self, nom: str) -> None:
        self.verifier_etat_ouvert()
        if not any(i.carte == nom for i in self.j.main):
            raise Illegal(f"{nom} n'est pas dans la main")
        f = self.fiche(nom)
        if not f.est_monstre:
            raise Illegal(f"{nom} n'est pas un monstre")
        if self.etat.cadre.invocation_normale_utilisee:
            raise Illegal("une seule Invocation Normale ou Pose par tour")
        if not self.cases_monstre_libres():
            raise Illegal("aucune zone Monstre principale libre")
        self.exiger_declaree(nom, "Invocation Normale")
        if getattr(f.formalisation, "invocation_normale_interdite", False):
            raise Illegal(f"{nom} ne peut pas être Invoqué Normalement")
        if (f.niveau or 0) > 4:
            raise NonCouvert("Invocation par Tribut non codée")
        cellule = self.cases_monstre_libres()[0]
        self.pas.append(Pas("declarer", f"Invocation Normale : {nom}"))
        self.retirer("main", nom)
        self.ajouter("terrain", Instance(carte=nom, face="visible", position="attaque", arrivee="invocation_normale",
                                         arrivee_ce_tour=True), cellule)
        self.pas[-1].cartes.append((nom, "acteur", "main", "terrain", cellule))
        self.etat = replace(self.etat, cadre=replace(self.etat.cadre, invocation_normale_utilisee=True))
        self.pas.append(Pas("enchainer", "fenêtre adverse après l'invocation : aucune réponse (pilote)"))
        self.evenements.append(Evenement("invocation_normale", nom, "terrain", cellule))

    def activer_declaration(self, nom: str, numero: int | None) -> None:
        self.verifier_etat_ouvert(PHASES_PRINCIPALES + ("fin",))
        f = self.fiche(nom)
        lieux = [((z, None), i) for z in ("main", "cimetiere", "bannies") for i in getattr(self.j, z) if i.carte == nom]
        lieux += [(lieu, i) for lieu, i in self._instances_publiques("terrain") if i.carte == nom]
        if not lieux:
            raise Illegal(f"{nom} n'est ni en main, ni sur le terrain, ni au Cimetière")
        if not f.declaree:
            if f.est_piege and all(l[0][0] == "main" for l in lieux):
                raise Illegal("un Piège ne s'active pas depuis la main")
            self.exiger_declaree(nom, "activation")
        e = f.formalisation.effet(numero or 1)
        if e.genre == "declenche":
            raise Illegal(f"effet {e.numero} de {nom} : effet déclenché, il ne s'active que lorsque son événement survient")
        if e.genre == "restriction":
            raise Illegal(f"effet {e.numero} de {nom} : pas un effet qui s'active")
        if e.genre == "procedure":
            raise Illegal(f"effet {e.numero} de {nom} : Invocation Spéciale par procédure, elle ne s'active pas (R15)")
        phase = self.etat.cadre.phase
        lent = e.genre == "ignition" or (e.genre == "activation_carte" and e.vitesse == 1)
        if lent and phase not in PHASES_PRINCIPALES:
            raise Illegal(f"effet de vitesse 1 : seulement pendant une Phase Principale (phase « {phase} »)")
        raisons = []
        lieux_vus = set()
        for lieu, _ in lieux:
            if lieu in lieux_vus:
                continue
            lieux_vus.add(lieu)
            raison = self.legalite(nom, e, lieu)
            if raison is None:
                self.activer(nom, e, lieu)
                self.fenetre_reponse()
                self.resoudre_chaine()
                return
            raisons.append(raison)
        raise Illegal(raisons[0])

    def invocation_procedure(self, nom: str) -> None:
        """Invocation Spéciale par la procédure de la carte (« you can Special Summon this card (from your
        hand) ») : elle ne s'active pas, n'ouvre pas de chaîne (R15)."""
        self.verifier_etat_ouvert()
        f = self.fiche(nom)
        if not any(i.carte == nom for i in self.j.main):
            raise Illegal(f"{nom} n'est pas dans la main")
        self.exiger_declaree(nom, "Invocation Spéciale par procédure")
        e = next((x for x in f.formalisation.effets if x.genre == "procedure"), None)
        if e is None:
            raise Illegal(f"{nom} n'a pas de procédure d'Invocation Spéciale")
        raison = self.legalite(nom, e, ("main", None))
        if raison:
            raise Illegal(raison)
        if not self.cases_monstre_libres():
            raise Illegal("aucune zone Monstre principale libre")
        self.pas.append(Pas("declarer", f"Invocation Spéciale par procédure : {nom}"))
        self.consommer_limites(e, ("main", None), nom)
        EXERCES.add((nom, e.numero))
        pos = self.choisir(Decision("choisir", "position", [Option("attaque"), Option("defense")]))
        self.invoquer_specialement("main", nom, None, self.cases_monstre_libres()[0], pos.valeur)
        self.pas.append(Pas("enchainer", "fenêtre adverse après l'invocation : aucune réponse (pilote)"))

    def invocation_synchro(self, nom: str) -> None:
        self.verifier_etat_ouvert()
        if not any(i.carte == nom for i in self.j.extra):
            raise Illegal(f"{nom} n'est pas dans l'Extra Deck")
        f = self.fiche(nom)
        if f.frame != "synchro":
            raise Illegal(f"{nom} n'est pas un monstre Synchro")
        self.exiger_declaree(nom, "Invocation Synchro")
        interdit = self.verrou_interdit_extra(f)
        if interdit:
            raise Illegal(interdit)
        couvertes, inconnues, raison = self.analyser_synchro(f)
        if not couvertes and not inconnues:
            raise Illegal(raison)
        self.pas.append(Pas("declarer", f"Invocation Synchro : {nom}"))
        o = self.choisir(Decision("choisir", "materiaux", [Option(lib, True, None, ch) for lib, ch, _ in couvertes],
                                  [Option(lib, False, r, None) for lib, _, r in inconnues]))
        self.pas.append(Pas("resoudre", f"matériels de {nom}"))
        for zone, cellule, inst in o.donnees:
            self.envoyer_cimetiere(zone, inst.carte, cellule, "materiel", "materiel_synchro")
        self.placer_depuis_extra(f, "invocation_synchro")
        self.pas.append(Pas("enchainer", "fenêtre adverse après l'invocation : aucune réponse (pilote)"))

    def passer_phase_de_fin(self) -> None:
        """Phase Principale → Phase de Fin (au tour 1, pas de Phase de Combat, R31). Fin des modifications « jusqu'à
        la Phase de Fin » ; retours différés (`Ecclesia and the Dark Dragon`)."""
        self.verifier_etat_ouvert()
        self.pas.append(Pas("declarer", "passage à la Phase de Fin"))
        self.etat = replace(self.etat, cadre=replace(self.etat.cadre, phase="fin"))
        for c, i in list(self.monstres()):
            if any(m.echeance == "phase_de_fin" for m in i.modifications):
                inst = self.retirer("terrain", i.carte, c)
                self.ajouter("terrain", replace(inst, modifications=tuple(
                    m for m in inst.modifications if m.echeance != "phase_de_fin")), c)
        m = self.etat.memoire
        restent = []
        for d in m.effets_differes:
            if d.echeance != "phase_de_fin_retour":
                restent.append(d)
                continue
            position = "defense" if "position=defense" in d.description else "attaque"
            if not any(i.carte == d.source for i in self.j.bannies):
                self.notes.append(f"{d.source} n'est plus bannie : pas de retour")
                continue
            if not self.cases_monstre_libres():
                raise NonCouvert(f"retour de {d.source} sans zone Monstre principale libre : non codé")
            self.pas.append(Pas("resoudre", f"{d.source} revient sur le terrain ({position})"))
            inst = self.retirer("bannies", d.source)
            self.ajouter("terrain", replace(inst, face="visible", position=position, arrivee="autre",
                                            arrivee_ce_tour=True), self.cases_monstre_libres()[0])
        self.etat = replace(self.etat, memoire=replace(self.etat.memoire, effets_differes=tuple(restent)))

    def effets_de_fin_en_attente(self) -> list[str]:
        en_attente = []
        for zone in ZONES_PUBLIQUES:
            for lieu, inst in self._instances_publiques(zone):
                f = self.cat.get(inst.carte)
                if f is None or not f.declaree:
                    continue
                for e in f.formalisation.effets:
                    if e.genre == "fin" and not e.facultatif and self.legalite(inst.carte, e, lieu) is None:
                        en_attente.append(f"{inst.carte}/{e.numero}")
        return en_attente

    def fin_de_tour(self) -> None:
        self.verifier_etat_ouvert(("fin",))
        attente = self.effets_de_fin_en_attente()
        if attente:
            raise Illegal(f"effet obligatoire de Phase de Fin non résolu : {', '.join(attente)} (R23)")
        if "Mulcharmy Fuwalos" in self.etat.memoire.effets_appliques and len(self.j.main) > 6:
            raise NonCouvert("Mulcharmy Fuwalos : retour aléatoire de cartes de la main dans le Deck non codé")
        if len(self.j.main) > 6:
            raise NonCouvert("défausse jusqu'à 6 cartes en fin de tour non codée")
        self.pas.append(Pas("declarer", "fin du tour"))
        self.notes.append("tour terminé")

    def declenchement_initial(self, evt: Evenement) -> None:
        """L'état de départ dit qu'un événement vient d'avoir lieu (« vient d'être Invoqué Spécialement »)."""
        self.verifier_etat_ouvert()
        self.evenements.append(evt)


class Moteur:
    def __init__(self, catalogue: Catalogue):
        self.catalogue = catalogue

    def jouer(self, etat: Etat, declaration: Declaration, script: Script | None = None) -> Resultat:
        p = Partie(self.catalogue, etat, script or Script())
        p.noter_reserves()
        verdict, raison = "legal", None
        try:
            t = declaration.type
            if t == "invocation_normale":
                p.invocation_normale(declaration.carte)
            elif t == "activer":
                p.activer_declaration(declaration.carte, declaration.effet)
            elif t == "declenche":
                if declaration.evenement is None:
                    raise ErreurScript("déclaration « declenche » sans événement")
                p.declenchement_initial(declaration.evenement)
            elif t == "invocation_procedure":
                p.invocation_procedure(declaration.carte)
            elif t == "invocation_synchro":
                p.invocation_synchro(declaration.carte)
            elif t == "phase_de_fin":
                p.passer_phase_de_fin()
            elif t == "fin_de_tour":
                p.fin_de_tour()
            elif t == "phase_combat":
                p.verifier_etat_ouvert()
                if etat.cadre.tour == 1:
                    raise Illegal("le joueur qui commence n'a pas de Phase de Combat à son premier tour (R31)")
                raise HorsPerimetre("Phase de Combat")
            else:
                raise ErreurScript(f"déclaration inconnue : {t}")
            p.jouer_declencheurs()
            if t == "declenche" and not any(d.question == "activer_declenche" for d in p.decisions):
                raise Illegal(f"aucun effet de {declaration.carte} ne se déclenche sur cet événement")
            p.noter_reserves()
        except Illegal as exc:
            verdict, raison = "illegal", str(exc)
        except NonCouvert as exc:
            verdict, raison = "non_couvert", str(exc)
        except HorsPerimetre as exc:
            verdict, raison = "hors_perimetre", str(exc)
        if p.script.reponses and verdict == "legal":
            raise ErreurScript(f"réponses non utilisées : {p.script.reponses}")
        faits = list(etat.memoire.faits_libres) + [n for j in etat.joueurs for i in j.toutes_les_instances()
                                                   for n in i.notes]
        return Resultat(verdict, raison, p.etat if verdict == "legal" else None, p.pas, p.decisions,
                        p.reserves, p.incomplet, p.notes, faits)
