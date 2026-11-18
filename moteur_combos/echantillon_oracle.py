"""Jalon n°7 (TOK-144) : le moteur joue les situations de l'échantillon J1 et on compare aux réponses de l'oracle.

Les situations (`situations-echantillon-j1.yaml`) ont été écrites et jouées par la session de l'oracle (jalon n°6),
sans lire le moteur. Ici, chaque situation est **traduite une fois, à la main**, en déclarations et en réponses aux
décisions du moteur (comme `SCENARIOS_J1`), puis on **relève** ce que le moteur propose. La référence est la réponse
de l'oracle (`reponses-oracle.md` § 9.2), recopiée dans `ORACLE` ; le champ `attendu` du YAML (lecture écrite avant de
jouer) n'est jamais lu. Règle de comptage : `j1-rapport.md` § 8 (figée avant la première exécution).

Ce module ne contient aucune règle de jeu : il dit quoi demander au moteur et quoi relever.

Conventions de traduction (celles du lanceur de l'oracle, § 8.4 et 9.3 de `reponses-oracle.md`) : position Attaque,
Zone Monstre Extra de gauche pour un monstre de l'Extra Deck, plus basse zone libre. « Posé » = placé sans historique
d'invocation (pas `venue_extra_deck`, arrivée non précisée, pas correctement invoqué). Un monstre du terrain adverse est
un vrai exemplaire de la carte, contrôlé par l'adversaire (pas une carte générique).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field, replace

from . import chemins, regles
from .cartes import ALBAZ, ALUBER, BFUSION, RIND, TBKITT
from .cartes_j1 import (
    AEON, ASH, BHIGH, BOPENING, CARTESIA, CHAMPIONS, COCA, DECCLESIA, DOGMA, DRAGO, EDD, GARURA, GRANG, GSWORD,
    IECCLESIA, LULU, MERC, MIRROR, MIXOUSIA, NADIR, OGRE, QUEM, SANCTIFIRE, SARC, SKITT, SPOLY, TFTV, TITAN, WHITE,
)
from .exploration import declarations
from .modele import CELLULES_MONSTRE, Instance
from .regles import NE_PAS_ACTIVER, PASSER, Declaration, Moteur, Partie, Script
from .situations import charger_tests, construire_depart

ECHANTILLON_YAML = chemins.DOCS / "situations-echantillon-j1.yaml"

# Les 20 effets tirés (graine 20260118), strate et nom du moteur.
EFFETS_TIRES = {
    "ALUBER/1": ("a", ALUBER, 1), "CARTESIA/2": ("a", CARTESIA, 2), "BFUSION/1": ("a", BFUSION, 1),
    "DECCLESIA/2": ("a", DECCLESIA, 2), "GARURA/2": ("a", GARURA, 2), "NADIR/1": ("a", NADIR, 1),
    "SPOLY/1": ("a", SPOLY, 1), "GSWORD/2": ("a", GSWORD, 2), "TITAN/3": ("a", TITAN, 3), "MERC/2": ("a", MERC, 2),
    "BOPENING/2": ("b", BOPENING, 2), "BHIGH/2": ("b", BHIGH, 2), "LULU/1": ("b", LULU, 1), "LULU/2": ("b", LULU, 2),
    "OGRE/1": ("b", OGRE, 1), "AEON/1": ("b", AEON, 1), "CHAMPIONS/1": ("b", CHAMPIONS, 1),
    "CHAMPIONS/2": ("b", CHAMPIONS, 2), "TITAN/1": ("b", TITAN, 1), "TITAN/2": ("b", TITAN, 2),
}

# Non tranché par l'oracle (règle figée, cas a) : situation déclarée non testable.
NON_TESTABLES = {"E18": "l'oracle ne sait pas donner à un monstre adverse un historique d'invocation (§ 9.1)"}


# ── Départ ─────────────────────────────────────────────────────────────────────────────────────

_POSE = re.compile(r"^\s*pos[ée]e?\s*$")
_ANCIEN = re.compile(r"^au Cimetière depuis un tour précédent$")


def _nettoyer(jeton: str) -> tuple[str, bool]:
    """« CARTESIA (posée) » → (« CARTESIA », True) ; annotations propres à ce fichier retirées."""
    m = re.match(r"^([A-Z][A-Z0-9_]*)\s*(?:\((.*)\))?\s*$", str(jeton))
    if not m:
        return str(jeton), False
    nom, ann = m.group(1), (m.group(2) or "").strip()
    if _POSE.match(ann):
        return nom, True
    if _ANCIEN.match(ann):
        return nom, False   # au Cimetière depuis un tour précédent : état par défaut (pas envoyé ce tour)
    return str(jeton), False


@dataclass
class DepartE:
    etat: object | None
    erreurs: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)


def construire_depart_echantillon(s: dict, jeu, deck) -> DepartE:
    """Départ d'une situation de l'échantillon : `construire_depart` (conventions du lot 18) sur une copie de la
    situation dont les annotations propres à ce fichier sont traduites ici (déclarées dans `conventions`)."""
    depart = dict(s.get("depart") or {})
    poses: list[tuple[str, int]] = []   # (alias, rang sur le terrain)
    conventions: list[str] = []
    copie: dict = {}
    for zone in ("main", "terrain", "cimetiere", "bannies"):
        jetons = []
        for k, j in enumerate(depart.get(zone) or []):
            nom, pose = _nettoyer(j)
            if pose:
                poses.append((nom, k))
            jetons.append(nom)
        if jetons:
            copie[zone] = jetons
    adverses = [_nettoyer(j)[0] for j in depart.get("terrain_adverse") or []]
    # Exemplaires au-delà de la liste (« 2e copie ajoutée au départ ») : ajoutés sans retirer du Deck.
    cartes = deck.par_nom()
    compte = Counter(jeu.alias[x] for z in ("main", "terrain", "cimetiere", "bannies") for x in copie.get(z, []))
    surplus = {n: k - cartes[n].nombre for n, k in compte.items() if k > cartes[n].nombre}
    retires: dict[str, list[str]] = {}
    if surplus:
        for n, k in surplus.items():
            a = next(x for x, v in jeu.alias.items() if v == n)
            main = copie.get("main", [])
            for _ in range(k):
                main.remove(a)
                retires.setdefault("main", []).append(a)
            conventions.append(f"{n} : {k} exemplaire(s) en plus de la liste, ajouté(s) en main hors Deck")
    s2 = {"id": s["id"], "depart": copie, "attendu": {"verdict": "legal"}}
    d = construire_depart(s2, jeu, deck)
    if d.etat is None:
        return DepartE(None, d.erreurs, d.conventions + conventions)
    etat = d.etat
    j0, j1 = etat.joueurs
    # Exemplaires en plus.
    for a in retires.get("main", []):
        j0 = replace(j0, main=j0.main + (Instance(carte=jeu.alias[a]),))
    # « Posé » : sans historique d'invocation.
    for a, _ in poses:
        nom = jeu.alias[a]
        # « autre » : arrivée connue, qui n'est pas une invocation (comme le retour d'`Ecclesia and the Dark Dragon`).
        sans = dict(arrivee="autre", arrivee_ce_tour=False, venue_extra_deck=False, correctement_invoquee=False)
        cases = []
        fait = False
        for c, i in j0.cases:
            if not fait and i.carte == nom and i.arrivee != "autre":
                i = replace(i, **sans)
                fait = True
            cases.append((c, i))
        j0 = replace(j0, cases=tuple(cases))
        zme = list(etat.zones_monstre_extra)
        for k, o in enumerate(zme):
            if not fait and o.instance.carte == nom and o.instance.arrivee != "autre":
                zme[k] = replace(o, instance=replace(o.instance, **sans))
                fait = True
        etat = replace(etat, zones_monstre_extra=tuple(zme))
        conventions.append(f"{nom} posé : sans historique d'invocation")
    # Terrain adverse : vrais exemplaires, contrôlés par l'adversaire.
    cases_adv = []
    for k, a in enumerate(adverses):
        nom = jeu.alias[a]
        cases_adv.append((CELLULES_MONSTRE[k], Instance(carte=nom, proprietaire=1, face="visible", position="attaque")))
        conventions.append(f"terrain adverse : {nom} posé en {CELLULES_MONSTRE[k]} (exemplaire réel de l'adversaire)")
    j1 = replace(j1, cases=tuple(cases_adv))
    etat = replace(etat, joueurs=(j0, j1))
    return DepartE(etat, [], d.conventions + conventions)


# ── Pilotage du moteur ─────────────────────────────────────────────────────────────────────────

class Arret(Exception):
    """Point d'observation atteint : on arrête la transition sans la finir."""


class EtapeRefusee(Exception):
    """Une étape que l'oracle a jouée légalement est refusée par le moteur."""

    def __init__(self, message, decl=None):
        super().__init__(message)
        self.decl = decl


def _parties(v: str, sans_case: bool = False) -> list[str]:
    parts = [x.strip() for x in v.split(" + ")]
    if sans_case:
        parts = [re.sub(r"\s*\((?:M\d|ZME_[GD])\)$", "", x) for x in parts]
    return sorted(parts)


def _apparier(v: str, valeurs: list[str]) -> str:
    """Valeur exacte ; sinon préfixe unique ; sinon mêmes matériels dans un autre ordre (ou sur d'autres cases)."""
    if v in valeurs:
        return v
    cand = [x for x in valeurs if x.startswith(v)]
    if len(cand) == 1:
        return cand[0]
    for sans_case in (False, True):
        cand = [x for x in valeurs if _parties(x, sans_case) == _parties(v, sans_case)]
        if len(cand) == 1:
            return cand[0]
    return v


class Pilote(Script):
    """Réponses prévues (question, valeur) dans l'ordre ; défauts déclarés pour le reste : ne pas répondre à ses
    propres maillons, position Attaque, Zone Monstre Extra d'abord, ne pas activer un déclencheur non cité."""

    def __init__(self, reponses=(), stop=None):
        super().__init__(list(reponses))
        self.vues = []
        self.stop = stop

    def repondre(self, d):
        self.vues.append(d)
        if self.stop is not None and self.stop(d):
            raise Arret()
        vals = d.valeurs()
        if self.reponses and self.reponses[0][0] == d.question:
            return _apparier(self.reponses.pop(0)[1], vals)
        q = d.question
        if q == "reponse":
            return PASSER
        if q == "position" and "attaque" in vals:
            return "attaque"
        if q == "placement" and vals:
            return "zone_monstre_extra" if "zone_monstre_extra" in vals else vals[0]
        if q == "activer_declenche" and NE_PAS_ACTIVER in vals:
            return NE_PAS_ACTIVER
        return None


class Ctx:
    def __init__(self, cat, etat):
        self.cat = cat
        self.etat = etat
        self.depart = etat
        self.m = Moteur(cat)
        self.decisions = []
        self.resultats = []
        self.refus = None   # étape refusée relevée par une situation (carte, effet), pour les statuts

    def jouer(self, decl, *reps, stop=None):
        s = Pilote(reps, stop)
        try:
            res = self.m.jouer(self.etat, decl, s)
        except Arret:
            self.decisions += s.vues
            return None
        self.decisions += s.vues
        self.resultats.append(res)
        if res.verdict != "legal":
            raise EtapeRefusee(f"{decl.type} {decl.carte} {decl.effet or ''} : {res.verdict} ({res.raison})", decl)
        self.etat = res.etat
        return res

    def neuf(self) -> "Ctx":
        """Même départ, autre passage (pour relever une seconde branche)."""
        return Ctx(self.cat, self.depart)

    def propose(self, decl) -> bool:
        """L'action passe-t-elle la légalité de la déclaration (on s'arrête à la première décision) ?"""
        try:
            res = self.m.jouer(self.etat, decl, Pilote((), stop=lambda d: True))
        except Arret:
            return True
        if res.verdict == "non_couvert":
            raise EtapeRefusee(f"{decl.type} {decl.carte} : non couvert ({res.raison})", decl)
        return res.verdict == "legal"

    def tenter(self, nom, n=1) -> bool:
        return self.propose(Declaration("activer", nom, n))

    # ── Relevés ────────────────────────────────────────────────────────────────────────────────
    def dec(self, question, rang=0):
        trouvees = [d for d in self.decisions if d.question == question]
        return trouvees[rang] if rang < len(trouvees) else None

    def options(self, question, rang=0) -> set[str]:
        d = self.dec(question, rang)
        return set() if d is None else set(d.valeurs()) | {o.valeur for o in d.indeterminees}

    def noms(self, question, rang=0) -> set[str]:
        """Options d'une décision ramenées aux noms de cartes (« Nom (M1) », « Nom/2 » → « Nom »)."""
        out = set()
        for v in self.options(question, rang):
            if v in (PASSER, NE_PAS_ACTIVER, "terminer", "ne pas annuler"):
                continue
            out.add(re.sub(r"\s*\((?:[^()]*)\)$", "", v).split("/")[0])
        return out

    def declenches(self, rang=0) -> set[str]:
        return self.noms("activer_declenche", rang)

    def a_repondu(self, nom) -> bool:
        """La carte figure-t-elle dans une fenêtre de réponse relevée ?"""
        return any(v.split("/")[0] == nom for d in self.decisions if d.question == "reponse" for v in d.valeurs())

    def synchros(self) -> set[str]:
        return {i.carte for i in self.etat.joueurs[0].extra
                if (f := self.cat.get(i.carte)) is not None and f.frame == "synchro"
                and self.propose(Declaration("invocation_synchro", i.carte))}

    def liste_fin(self) -> set[str]:
        """Effets activables pendant la Phase de Fin (noms de cartes)."""
        return {d.carte for d in declarations(self.etat, self.cat, frozenset())
                if d.type == "activer" and self.propose(d)}

    def ou(self, nom, joueur=0) -> set[str]:
        j = self.etat.joueurs[joueur]
        z = {zone for zone in ("main", "deck", "extra", "cimetiere", "bannies")
             if any(i.carte == nom for i in getattr(j, zone))}
        if any(i.carte == nom for c, i in j.cases if c in CELLULES_MONSTRE) or any(
                o.instance.carte == nom and o.controleur == joueur for o in self.etat.zones_monstre_extra):
            z.add("terrain")
        return z

    def atk(self, nom):
        p = Partie(self.cat, self.etat, Script())
        v = [p.atk_de(i) for _, i in p.monstres() if i.carte == nom]
        return v[0] if len(v) == 1 else v

    def annule(self, nom) -> bool:
        p = Partie(self.cat, self.etat, Script())
        return any(p.effets_annules(i) for _, i in p.monstres() if i.carte == nom)


def M(*parts) -> str:
    return " + ".join(f"{n} ({z})" for n, z in parts)


def D(nom, n):
    return ("activer_declenche", f"{nom}/{n}")


def act(nom, n=1):
    return Declaration("activer", nom, n)


NS = lambda nom: Declaration("invocation_normale", nom)          # noqa: E731
FIN = Declaration("phase_de_fin", "—")


# ── Situations : traduction en décisions et relevés ────────────────────────────────────────────
# Chaque fonction rend un dictionnaire de relevés ; les clés sont celles de `ORACLE[id]`.

def e01(c):
    c.jouer(NS(ALUBER), D(ALUBER, 1), ("carte", BFUSION))
    return {"propose": ALUBER in c.declenches(), "liste": c.noms("carte")}


def e02(c):
    c.jouer(act(BOPENING), ("defausse", ASH), ("carte", ALUBER), ("option", "Invoquer Spécialement en Défense"),
            D(ALUBER, 1), ("carte", BHIGH))
    return {"propose": ALUBER in c.declenches(), "liste": c.noms("carte", 1)}


def e03(c):
    c.jouer(NS(ALUBER))
    return {"propose": ALUBER in c.declenches()}


def e04(c):
    c.jouer(NS(ALUBER), D(ALUBER, 1), ("carte", BFUSION))
    c.jouer(act(BOPENING), ("defausse", ASH), ("carte", ALUBER), ("option", "Invoquer Spécialement en Défense"))
    return {"propose": ALUBER in c.declenches(1)}


def e05(c):
    c.jouer(act(CARTESIA, 2), ("fusion", GRANG), ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "main"))))
    mats = {x for o in c.options("materiaux") for x in o.split(" + ")}
    return {"propose": True, "fusions": c.noms("fusion"), "materiaux_grang": mats}


def e06(c):
    c.jouer(NS(ALUBER), D(ALUBER, 1), ("reponse", f"{CARTESIA}/2"), ("fusion", GRANG),
            ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "main"))), ("carte", BFUSION))
    return {"propose_en_reponse": c.a_repondu(CARTESIA)}


def e07(c):
    c.jouer(act(WHITE, 1), ("cout", TITAN))
    c.jouer(FIN)
    fin = c.liste_fin()
    return {"propose": CARTESIA in fin, "liste_fin": fin}


def e08(c):
    c.jouer(act(CARTESIA, 2), stop=lambda d: d.question == "fusion")
    return {"propose": c.dec("fusion") is not None, "fusions": c.noms("fusion")}


def e08b(c):
    c.jouer(act(CARTESIA, 2), ("fusion", MIXOUSIA), stop=lambda d: d.question == "materiaux")
    mats = {x for o in c.options("materiaux") for x in o.split(" + ")}
    return {"propose": c.dec("fusion") is not None, "mixousia_cartesia_ash": MIXOUSIA in c.noms("fusion")
            and {f"{CARTESIA} (terrain)", f"{ASH} (main)"} <= mats}


def e09(c):
    c.jouer(act(CARTESIA, 2), ("fusion", GRANG), ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "main"))))
    return {"propose": c.tenter(CARTESIA, 2)}


MAT_RIND_DECK = M((ALBAZ, "deck"), (COCA, "deck"))


def e10(c):
    c.jouer(act(BFUSION), ("fusion", RIND), ("materiaux", MAT_RIND_DECK))
    return {"propose": True, "fusions": c.noms("fusion"), "rind_albaz_coca_deck": "terrain" in c.ou(RIND)}


def e11(c):
    c.jouer(act(BFUSION), ("fusion", SANCTIFIRE), ("materiaux", M((ALBAZ, "main"), (CARTESIA, "terrain"))))
    zones = {re.search(r"\((\w+)\)$", x).group(1) for d in c.decisions if d.question == "materiaux"
             for o in d.valeurs() for x in o.split(" + ")}
    return {"propose": True, "zones_materiaux": zones, "sanctifire_albaz_main_cartesia_terrain": "terrain" in c.ou(SANCTIFIRE)}


def e12(c):
    c.jouer(act(BFUSION), stop=lambda d: d.question == "fusion")
    return {"fusions": c.noms("fusion")}


def e13(c):
    avant = c.synchros()
    c.jouer(act(BFUSION), ("fusion", RIND), ("materiaux", MAT_RIND_DECK))
    return {"synchros_avant": avant, "synchros_apres": c.synchros()}


def e14(c):
    c.jouer(Declaration("invocation_synchro", EDD), ("materiaux", M((IECCLESIA, "M1"), (ALUBER, "M2"))))
    return {"propose": c.tenter(BFUSION)}


def e15(c):
    c.jouer(act(BFUSION), ("fusion", RIND), ("materiaux", MAT_RIND_DECK))
    return {"propose": c.tenter(BFUSION)}


def e16(c):
    return {"propose": c.tenter(BFUSION)}


def e17(c):
    c.jouer(act(BFUSION), ("fusion", RIND), ("materiaux", MAT_RIND_DECK))
    p = c.tenter(DECCLESIA, 2)
    c.jouer(act(DECCLESIA, 2))
    return {"propose": p, "decclesia_terrain": "terrain" in c.ou(DECCLESIA)}


def e19(c):
    c.jouer(NS(ALUBER))
    return {"propose": c.tenter(DECCLESIA, 2)}


def e20(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    return {"propose": c.tenter(DECCLESIA, 2)}


def e21(c):
    c.jouer(act(BFUSION), ("fusion", RIND), ("materiaux", MAT_RIND_DECK))
    c.jouer(act(DECCLESIA, 2))
    return {"propose": c.tenter(DECCLESIA, 2)}


def e22(c):
    avant = len(c.etat.joueurs[0].main)
    c.jouer(act(NADIR), ("envoi", GARURA), ("carte", DECCLESIA), D(GARURA, 2), ("pioche", ALUBER))
    return {"propose": GARURA in c.declenches(), "pioche": len(c.etat.joueurs[0].main) - (avant - 1 + 1)}


def e23(c):
    c.jouer(act(CARTESIA, 2), ("fusion", MIRROR), ("materiaux", M((ALBAZ, "main"), (GARURA, "terrain"))), D(GARURA, 2), ("pioche", ALUBER))
    return {"propose": GARURA in c.declenches()}


def e24(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    extra = {i.carte for i in c.etat.joueurs[0].extra} | {TITAN}
    return {"propose": True, "envoyables_tout_extra": c.noms("envoi") == extra, "ajoutables": c.noms("carte")}


def e25(c):
    c.jouer(act(NADIR), ("envoi", GARURA), ("carte", QUEM))
    return {"ajoutables": c.noms("carte")}


def e26(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    return {"albaz_cimetiere_dans_liste": ALBAZ in c.noms("carte") and "main" in c.ou(ALBAZ)
            and "cimetiere" not in c.ou(ALBAZ)}


def e27(c):
    return {"propose": c.tenter(NADIR)}


def e28(c):
    c.jouer(act(NADIR), ("reponse", f"{CARTESIA}/2"), ("fusion", GRANG),
            ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "main"))), ("envoi", TITAN), ("carte", WHITE))
    return {"propose_en_reponse": c.a_repondu(CARTESIA), "grang_terrain": "terrain" in c.ou(GRANG),
            "nadir_resolu": "main" in c.ou(WHITE)}


def e29(c):
    avant = c.synchros()
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    return {"edd_avant": EDD in avant, "edd_apres": EDD in c.synchros()}


def e30(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    return {"propose": c.tenter(NADIR)}


def e31(c):
    return {"propose": c.tenter(SPOLY)}


def e32(c):
    if not c.tenter(SPOLY):
        return {"propose": False, "fusions": set(), "skitt_adverse_materiel": False, "skitt_cimetiere_adverse": False}
    c.jouer(act(SPOLY), ("cout", f"défausser {ASH}"), ("fusion", RIND),
            ("materiaux", M((ALBAZ, "terrain"), (SKITT, "terrain adverse"))))
    mats = {x for o in c.options("materiaux") for x in o.split(" + ")}
    return {"propose": True, "fusions": c.noms("fusion"), "skitt_adverse_materiel": any(x.startswith(SKITT) for x in mats),
            "skitt_cimetiere_adverse": "cimetiere" in c.ou(SKITT, 1)}


def e33(c):
    return {"propose": c.tenter(SPOLY)}


def e34(c):
    c.jouer(act(SPOLY), ("cout", f"défausser {ASH}"), ("fusion", GRANG),
            ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "terrain"))))
    return {"propose": True, "bopening_en_reponse": c.a_repondu(BOPENING)}


def e35(c):
    c.jouer(NS(ALUBER), D(ALUBER, 1), ("reponse", f"{SPOLY}/1"), ("cout", f"défausser {ASH}"), ("fusion", GRANG),
            ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "terrain"))), ("carte", BFUSION))
    return {"propose_en_reponse": c.a_repondu(SPOLY)}


def e36(c):
    c.jouer(act(COCA, 2), ("cout", MERC), D(GSWORD, 2), ("carte", CARTESIA))
    return {"propose": GSWORD in c.declenches(), "declenches": c.declenches(), "invocables": c.noms("carte")}


def e37(c):
    c.jouer(act(COCA, 2), ("cout", MERC), D(GSWORD, 2), ("carte", DECCLESIA))
    return {"propose_depuis_terrain": GSWORD in c.declenches() and "bannies" in c.ou(GSWORD),
            "invocables": c.noms("carte"), "decclesia_terrain": "terrain" in c.ou(DECCLESIA)}


def e38(c):
    c.jouer(act(COCA, 2), ("cout", MERC))
    return {"propose": GSWORD in c.declenches(), "declenches": c.declenches()}


def e39(c):
    c.jouer(act(TFTV, 1), ("cout", TITAN), ("cible", RIND), ("remplacement", "bannir Branded Opening"))
    return {"propose": GSWORD in c.declenches()}


def e40(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", DECCLESIA))
    c.jouer(FIN)
    p = TITAN in c.liste_fin()
    c.jouer(act(TITAN, 3), ("carte", ALBAZ), ("option", "ajouter à la main"))
    return {"propose": p, "liste": c.noms("carte", 1), "option_ajouter": "ajouter à la main" in c.options("option")}


def e41(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", DECCLESIA))
    c.jouer(FIN)
    c.jouer(act(TITAN, 3), ("carte", QUEM), ("option", "Invoquer Spécialement"))
    return {"option_invoquer": any(o.startswith("Invoquer") for o in c.options("option")),
            "quem_terrain": "terrain" in c.ou(QUEM)}


def e42(c):
    c.jouer(act(NADIR), ("envoi", GARURA), ("carte", QUEM))
    c.jouer(FIN)
    return {"propose": TITAN in c.liste_fin()}


def e43(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    c.jouer(FIN)
    return {"propose": TITAN in c.liste_fin()}


def e44(c):
    c.jouer(act(COCA, 2), ("cout", MERC), D(MERC, 2), ("carte", ALBAZ))
    return {"propose": MERC in c.declenches(), "liste": c.noms("carte")}


def e45(c):
    c.jouer(act(SARC), ("carte", MERC), D(MERC, 2), ("carte", WHITE))
    return {"propose": MERC in c.declenches(), "liste": c.noms("carte", 1)}


def _tftv_rind(c, remplacer):
    reps = [("cout", TITAN), ("cible", RIND)]
    if remplacer is not None:
        reps.append(("remplacement", remplacer))
    c.jouer(act(TFTV, 1), *reps)


def e46(c):
    _tftv_rind(c, "bannir Branded Opening")
    return {"question": c.dec("remplacement") is not None, "rind_reste": "terrain" in c.ou(RIND),
            "bopening_bannie": "bannies" in c.ou(BOPENING)}


def e47(c):
    _tftv_rind(c, "ne pas remplacer")
    return {"question": c.dec("remplacement") is not None, "rind_detruit": "cimetiere" in c.ou(RIND),
            "bopening_reste": "cimetiere" in c.ou(BOPENING)}


def e48(c):
    c.jouer(act(TFTV, 1), ("cout", TITAN), ("cible", ALUBER))
    return {"question": c.dec("remplacement") is not None, "aluber_detruit": "cimetiere" in c.ou(ALUBER)}


def e49(c):
    try:
        c.jouer(act(TFTV, 1), ("cout", TITAN), ("cible", f"{RIND} (M1)"))
    except EtapeRefusee as exc:
        c.refus = exc.decl
        return {"question": c.dec("remplacement") is not None, "rind_adverse_detruit": False,
                "_refus": str(exc), "_cibles": sorted(c.options("cible"))}
    return {"question": c.dec("remplacement") is not None, "rind_adverse_detruit": "cimetiere" in c.ou(RIND, 1)}


def e50(c):
    c.jouer(act(BOPENING), ("defausse", ASH), ("carte", ALUBER), ("option", "ajouter à la main"))
    _tftv_rind(c, "bannir Branded Opening")
    return {"question": c.dec("remplacement") is not None}


def e51(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    c.jouer(FIN)
    fin = c.liste_fin()
    return {"propose": BHIGH in fin, "liste_fin": fin}


def e52(c):
    c.jouer(NS(ALUBER), D(ALUBER, 1), ("carte", BFUSION))
    c.jouer(FIN)
    return {"propose": BHIGH in c.liste_fin()}


def e53(c):
    c.jouer(act(NADIR), ("envoi", EDD), ("carte", ALBAZ))
    c.jouer(FIN)
    return {"propose": BHIGH in c.liste_fin()}


def e54(c):
    c.jouer(act(BHIGH), ("revele", SKITT), ("envoi", DOGMA), ("appliquer", "appliquer"),
            ("carte", ALBAZ))
    c.jouer(FIN)
    fin = c.liste_fin()
    return {"propose": BHIGH in fin, "liste_fin": fin}


def e55(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ), D(LULU, 1), ("annuler", "ne pas annuler"))
    return {"propose": LULU in c.declenches(), "question_annuler": c.dec("annuler") is not None,
            "atk_lulu": c.atk(LULU), "atk_aluber": c.atk(ALUBER)}


def e56(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ), D(LULU, 1), ("annuler", ALUBER))
    return {"question_annuler": c.dec("annuler") is not None, "cibles_annulation": c.noms("annuler")}


def e57(c):
    c.jouer(act(CARTESIA, 2), ("fusion", GRANG), ("materiaux", M((CARTESIA, "terrain"), (ALBAZ, "main"))),
            D(LULU, 1), ("annuler", "ne pas annuler"))
    return {"propose": LULU in c.declenches(), "declenches": c.declenches(), "atk_lulu": c.atk(LULU),
            "atk_grang": c.atk(GRANG)}


def e58(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ), D(LULU, 1), ("annuler", "ne pas annuler"))
    c.jouer(act(WHITE, 1), ("cout", SANCTIFIRE))
    return {"propose": LULU in c.declenches(1) if c.dec("activer_declenche", 1) else False}


def e59(c):
    c.jouer(Declaration("invocation_synchro", LULU),
            ("materiaux", M((QUEM, "M1"), (DECCLESIA, "M2"), (ALUBER, "M3"))))
    return {"propose": LULU in c.declenches()}


def e60(c):
    c.jouer(act(NADIR), ("envoi", LULU), ("carte", ALBAZ))
    c.jouer(FIN)
    p = LULU in c.liste_fin()
    c.jouer(act(LULU, 2), ("carte", IECCLESIA))
    return {"propose": p, "liste": c.noms("carte", 1), "iecclesia_terrain": "terrain" in c.ou(IECCLESIA)}


def e61(c):
    c.jouer(act(NADIR), ("envoi", LULU), ("carte", ALBAZ))
    c.jouer(FIN)
    c.jouer(act(LULU, 2), ("carte", CARTESIA), ("zone", "main"))
    return {"cartesia_main_dans_liste": CARTESIA in c.noms("carte", 1), "cartesia_terrain": "terrain" in c.ou(CARTESIA)}


def e62(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    c.jouer(FIN)
    fin = c.liste_fin()
    return {"propose": LULU in fin, "liste_fin": fin}


def e63(c):
    c.jouer(NS(QUEM), D(QUEM, 1), ("reponse", f"{OGRE}/1"), ("carte", ALBAZ))
    return {"propose_en_reponse": c.a_repondu(OGRE), "quem_detruit": "cimetiere" in c.ou(QUEM),
            "albaz_envoye": "cimetiere" in c.ou(ALBAZ)}


def e64(c):
    c.jouer(NS(ALUBER), D(ALUBER, 1), ("reponse", f"{OGRE}/1"), ("carte", BFUSION))
    return {"propose_en_reponse": c.a_repondu(OGRE), "aluber_detruit": "cimetiere" in c.ou(ALUBER),
            "aluber_resolu": "main" in c.ou(BFUSION)}


def e65(c):
    c.jouer(act(NADIR), ("envoi", TITAN), ("carte", ALBAZ))
    return {"propose_en_reponse": c.a_repondu(OGRE)}


def e66(c):
    c.jouer(act(WHITE, 1), ("cout", TITAN))
    return {"propose_en_reponse": c.a_repondu(OGRE)}


def e67(c):
    c.jouer(NS(QUEM), D(QUEM, 1), ("reponse", f"{OGRE}/1"), ("carte", ALBAZ))
    c.jouer(act(CARTESIA, 1))
    n = len([d for d in c.decisions if d.question == "reponse"])
    c.jouer(act(CARTESIA, 2), stop=lambda d: d.question == "reponse")
    d = c.dec("reponse", n)
    return {"propose_en_reponse": d is not None and any(v.split("/")[0] == OGRE for v in d.valeurs()),
            "_fenetre": d is not None}


def _aeon(c, *bannir):
    c.jouer(act(SPOLY), ("cout", f"défausser {ASH}"), ("fusion", AEON),
            ("materiaux", M((RIND, "terrain"), (GRANG, "terrain"))), D(AEON, 1), *[("bannir", b) for b in bannir])


def e68(c):
    _aeon(c, f"{RIND} (cimetiere)", f"{GRANG} (cimetiere)")
    bans = [d for d in c.decisions if d.question == "bannir"]
    return {"propose": AEON in c.declenches(), "bannissables": c.noms("bannir"),
            "minimum_1": "terminer" not in bans[0].valeurs(), "maximum_2": len(bans) == 2}


def e69(c):
    _aeon(c, f"{ASH} (cimetiere)", "terminer")
    return {"une_carte_acceptee": "bannies" in c.ou(ASH)}


def e70(c):
    _aeon(c, f"{ASH} (cimetiere)", "terminer")
    return {"propose": c.tenter(AEON, 2)}


def _champions(c, *suite, stop=None):
    c.jouer(Declaration("invocation_synchro", CHAMPIONS), ("materiaux", M((IECCLESIA, "M1"), (ALUBER, "M2"))), *suite,
            stop=stop)


def e71(c):
    _champions(c, D(CHAMPIONS, 1), ("carte", CARTESIA))
    c2 = c.neuf()
    _champions(c2, D(CHAMPIONS, 1), ("carte", IECCLESIA), stop=lambda d: d.question == "zone")
    return {"propose": CHAMPIONS in c.declenches(), "liste": c.noms("carte"),
            "iecclesia_deck_et_cimetiere": c2.options("zone") == {"deck", "cimetiere"}}


def e72(c):
    _champions(c, D(CHAMPIONS, 1), ("carte", CARTESIA), ("zone", "cimetiere"))
    return {"cartesia_cimetiere": CARTESIA in c.noms("carte") and "cimetiere" in c.options("zone")}


def e73(c):
    _champions(c)
    c.jouer(act(CHAMPIONS, 2), ("cible", CHAMPIONS), ("detruire", "détruire"))
    c.jouer(act(TFTV, 2), ("cible", CHAMPIONS))
    return {"champions_cible_tftv": CHAMPIONS in c.noms("cible", 1), "propose": CHAMPIONS in c.declenches(1)
            if c.dec("activer_declenche", 1) else False}


def e74(c):
    c.jouer(act(CHAMPIONS, 2), ("cible", ALUBER), ("detruire", "détruire"))
    return {"cibles": c.noms("cible"), "question_detruire": c.dec("detruire") is not None,
            "aluber_detruit": "cimetiere" in c.ou(ALUBER)}


def e75(c):
    c.jouer(act(CHAMPIONS, 2), ("cible", ALUBER), ("detruire", "ne pas détruire"))
    return {"aluber_reste": "terrain" in c.ou(ALUBER)}


def e76(c):
    c.jouer(act(CHAMPIONS, 2), ("cible", ALUBER))
    return {"question_detruire": c.dec("detruire") is not None, "aluber_reste": "terrain" in c.ou(ALUBER)}


def e77(c):
    c.jouer(act(CHAMPIONS, 2), ("cible", ALUBER), ("detruire", "détruire"))
    return {"question_detruire": c.dec("detruire") is not None}


def e78(c):
    c.jouer(act(CHAMPIONS, 2), ("cible", ALUBER))
    return {"propose": c.tenter(CHAMPIONS, 2)}


def _titan_spoly(c, mat1, mat2, placement=None):
    reps = [("cout", f"défausser {ASH}"), ("fusion", TITAN), ("materiaux", M((mat1, "terrain"), (mat2, "terrain")))]
    if placement:
        reps.append(("placement", placement))
    c.jouer(act(SPOLY), *reps)


def e79(c):
    _titan_spoly(c, ALBAZ, GRANG)
    return {"fusions": c.noms("fusion"), "atk_titan": c.atk(TITAN)}


def e80(c):
    _titan_spoly(c, WHITE, DOGMA)
    return {"atk_titan": c.atk(TITAN)}


def e81(c):
    return {"atk_titan": c.atk(TITAN)}


def e82(c):
    c.jouer(act(CARTESIA, 2), ("fusion", MIRROR), ("materiaux", M((WHITE, "main"), (RIND, "terrain"))))
    _titan_spoly(c, ALBAZ, GRANG)
    c.jouer(act(MIRROR, 1), ("cout", SANCTIFIRE), ("bannir", TITAN))
    return {"titan_propose": TITAN in c.noms("bannir"), "titan_reste": "terrain" in c.ou(TITAN),
            "atk_titan": c.atk(TITAN)}


def e83(c):
    c.jouer(act(CARTESIA, 2), ("fusion", MIRROR), ("materiaux", M((ALBAZ, "main"), (RIND, "terrain"))))
    c.jouer(act(MIRROR, 1), ("cout", SANCTIFIRE), ("bannir", TITAN))
    return {"titan_banni": "bannies" in c.ou(TITAN)}


def e84(c):
    _titan_spoly(c, ALBAZ, GRANG)
    c.jouer(act(TFTV, 1), ("cout", SANCTIFIRE), ("cible", TITAN))
    return {"titan_detruit": "cimetiere" in c.ou(TITAN)}


def e85(c):
    _titan_spoly(c, ALBAZ, GRANG)
    _champions(c)
    c.jouer(act(CHAMPIONS, 2), ("cible", TITAN))
    return {"titan_ciblable": TITAN in c.noms("cible"), "question_detruire": c.dec("detruire") is not None,
            "titan_reste": "terrain" in c.ou(TITAN), "titan_annule": c.annule(TITAN)}


# ── Réponses de l'oracle (`reponses-oracle.md` § 9.2 et § 9.1), recopiées en relevés comparables ──────
# Seuls les éléments écrits par l'oracle sont comparés (règle figée, § 8 de `j1-rapport.md`). Listes : ensembles de noms
# distincts (« ×n » ignoré).

_V = True
_F = False
ORACLE: dict[str, dict] = {
    "E01": {"propose": _V, "liste": {TFTV, BHIGH, BOPENING, BFUSION}},
    "E02": {"propose": _V, "liste": {TFTV, BFUSION, BHIGH}},
    "E03": {"propose": _F},
    "E04": {"propose": _F},
    "E05": {"propose": _V, "fusions": {DOGMA, MIXOUSIA, GRANG, SANCTIFIRE},
            "materiaux_grang": {f"{ALBAZ} (main)", f"{CARTESIA} (terrain)"}},
    "E06": {"propose_en_reponse": _V},
    "E07": {"propose": _F, "liste_fin": {TITAN}},
    "E08": {"propose": _V, "fusions": {MIXOUSIA, GRANG}},
    "E08b": {"propose": _V, "mixousia_cartesia_ash": _V},
    "E09": {"propose": _F},
    "E10": {"propose": _V, "fusions": {RIND, SANCTIFIRE}, "rind_albaz_coca_deck": _V},
    "E11": {"propose": _V, "zones_materiaux": {"main", "terrain", "deck"}, "sanctifire_albaz_main_cartesia_terrain": _V},
    "E12": {"fusions": {RIND, SANCTIFIRE}},
    "E13": {"synchros_avant": {EDD, CHAMPIONS}, "synchros_apres": set()},
    "E14": {"propose": _F},
    "E15": {"propose": _F},
    "E16": {"propose": _F},
    "E17": {"propose": _V, "decclesia_terrain": _V},
    "E19": {"propose": _F},
    "E20": {"propose": _F},
    "E21": {"propose": _F},
    "E22": {"propose": _V, "pioche": 1},
    "E23": {"propose": _V},
    "E24": {"propose": _V, "envoyables_tout_extra": _V, "ajoutables": {QUEM, WHITE, ALBAZ, DECCLESIA}},
    "E25": {"ajoutables": {QUEM, DECCLESIA}},
    "E26": {"albaz_cimetiere_dans_liste": _V},
    "E27": {"propose": _F},
    "E28": {"propose_en_reponse": _V, "grang_terrain": _V, "nadir_resolu": _V},
    "E29": {"edd_avant": _V, "edd_apres": _F},
    "E30": {"propose": _F},
    "E31": {"propose": _F},
    "E32": {"propose": _V, "fusions": {RIND}, "skitt_adverse_materiel": _V, "skitt_cimetiere_adverse": _V},
    "E33": {"propose": _F},
    "E34": {"propose": _V, "bopening_en_reponse": _F},
    "E35": {"propose_en_reponse": _V},
    "E36": {"propose": _V, "declenches": {GSWORD, MERC}, "invocables": {CARTESIA}},
    "E37": {"propose_depuis_terrain": _V, "invocables": {DECCLESIA}},
    "E38": {"propose": _F, "declenches": {MERC}},
    "E39": {"propose": _F},
    "E40": {"propose": _V, "liste": {ALBAZ, WHITE, QUEM}, "option_ajouter": _V},
    "E41": {"option_invoquer": _V, "quem_terrain": _V},
    "E42": {"propose": _F},
    "E43": {"propose": _F},
    "E44": {"propose": _V, "liste": {ALBAZ, WHITE, CARTESIA, QUEM, IECCLESIA, SKITT, TBKITT, GSWORD}},
    "E45": {"propose": _V, "liste": {ALBAZ, WHITE, CARTESIA, QUEM, IECCLESIA, SKITT, TBKITT, GSWORD}},
    "E46": {"question": _V, "rind_reste": _V, "bopening_bannie": _V},
    "E47": {"question": _V, "rind_detruit": _V, "bopening_reste": _V},
    "E48": {"question": _F, "aluber_detruit": _V},
    "E49": {"question": _F, "rind_adverse_detruit": _V},
    "E50": {"question": _V},
    "E51": {"propose": _V, "liste_fin": {BHIGH, TITAN}},
    "E52": {"propose": _F},
    "E53": {"propose": _F},
    "E54": {"propose": _F, "liste_fin": {DOGMA}},
    "E55": {"propose": _V, "question_annuler": _V, "atk_lulu": 3000, "atk_aluber": 2300},
    "E56": {"cibles_annulation": {LULU, ALUBER}},
    "E57": {"propose": _V, "declenches": {LULU, GRANG}, "atk_lulu": 3000, "atk_grang": 3000},
    "E58": {"propose": _F},
    "E59": {"propose": _F},
    "E60": {"propose": _V, "liste": {DECCLESIA, IECCLESIA, CARTESIA, QUEM}},
    "E61": {"cartesia_main_dans_liste": _V, "cartesia_terrain": _V},
    "E62": {"propose": _F, "liste_fin": {TITAN}},
    "E63": {"propose_en_reponse": _V, "quem_detruit": _V, "albaz_envoye": _V},
    "E64": {"propose_en_reponse": _V, "aluber_detruit": _V, "aluber_resolu": _V},
    "E65": {"propose_en_reponse": _F},
    "E66": {"propose_en_reponse": _F},
    "E67": {"propose_en_reponse": _F},
    "E68": {"propose": _V, "bannissables": {AEON, SPOLY, GRANG, RIND, ASH}, "minimum_1": _V, "maximum_2": _V},
    "E69": {"une_carte_acceptee": _V},
    "E70": {"propose": _F},
    "E71": {"propose": _V, "liste": {IECCLESIA, QUEM, DECCLESIA, CARTESIA}, "iecclesia_deck_et_cimetiere": _V},
    "E72": {"cartesia_cimetiere": _V},
    "E73": {"champions_cible_tftv": _V, "propose": _F},
    "E74": {"cibles": {CHAMPIONS, ALUBER}, "question_detruire": _V, "aluber_detruit": _V},
    "E75": {"aluber_reste": _V},
    "E76": {"question_detruire": _F, "aluber_reste": _V},
    "E77": {"question_detruire": _V},
    "E78": {"propose": _F},
    "E79": {"atk_titan": 3700, "fusions": {TITAN, DRAGO, MIXOUSIA, MIRROR, SANCTIFIRE}},
    "E80": {"atk_titan": 3700},
    "E81": {"atk_titan": 2500},
    "E82": {"titan_propose": _V, "titan_reste": _V, "atk_titan": 3700},
    "E83": {"titan_banni": _V},
    "E84": {"titan_detruit": _V},
    "E85": {"titan_ciblable": _V, "question_detruire": _F, "titan_reste": _V, "titan_annule": _F},
}


# ── Exécution et comparaison ───────────────────────────────────────────────────────────────────

@dataclass
class Comparaison:
    id: str
    effets: list[str]
    issue: str                      # accord | desaccord | non_tranche
    ecarts: list[str]
    releve: dict
    exerces: set
    conventions: list[str]
    refus: tuple | None = None      # (carte, n° d'effet) de l'étape refusée par le moteur, s'il y en a une


def comparer(s: dict, jeu, deck, cat) -> Comparaison:
    sid = s["id"]
    effets = list(s.get("effets") or [])
    if sid in NON_TESTABLES:
        return Comparaison(sid, effets, "non_tranche", [NON_TESTABLES[sid]], {}, set(), [])
    fn = globals().get(sid.lower())
    d = construire_depart_echantillon(s, jeu, deck)
    if d.etat is None:
        return Comparaison(sid, effets, "desaccord", [f"départ refusé : {d.erreurs}"], {}, set(), d.conventions)
    regles.EXERCES.clear()
    c = Ctx(cat, d.etat)
    try:
        releve = fn(c)
    except EtapeRefusee as exc:
        refus = (exc.decl.carte, exc.decl.effet or 1) if exc.decl is not None else None
        return Comparaison(sid, effets, "desaccord", [f"étape refusée par le moteur : {exc}"], {}, set(regles.EXERCES),
                           d.conventions, refus)
    attendu = ORACLE[sid]
    ecarts = [f"{k} : moteur {_court(releve.get(k))}, oracle {_court(v)}" for k, v in attendu.items()
              if releve.get(k) != v]
    refus = (c.refus.carte, c.refus.effet or 1) if c.refus is not None else None
    return Comparaison(sid, effets, "desaccord" if ecarts else "accord", ecarts, releve, set(regles.EXERCES),
                       d.conventions, refus)


def _court(v):
    if isinstance(v, set):
        return "{" + ", ".join(sorted(x.split(",")[0] for x in v)) + "}"
    return repr(v)


def comparer_tout(cat, deck) -> list[Comparaison]:
    jeu = charger_tests(ECHANTILLON_YAML)
    return [comparer(s, jeu, deck, cat) for s in jeu.situations]


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    demi = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, centre - demi), min(1.0, centre + demi))


def compter(comparaisons: list[Comparaison]) -> dict:
    """Règle figée (§ 8 de `j1-rapport.md`) : unité = effet tiré ; erreur = au moins un désaccord avéré."""
    par_effet: dict[str, list[Comparaison]] = {e: [] for e in EFFETS_TIRES}
    for c in comparaisons:
        for e in c.effets:
            par_effet[e].append(c)
    statut = {}
    for e, cs in par_effet.items():
        issues = {c.issue for c in cs}
        if "desaccord" in issues:
            statut[e] = "erreur"
        elif "accord" in issues:
            statut[e] = "juste_avec_non_tranche" if "non_tranche" in issues else "juste"
        else:
            statut[e] = "non_tranche"
    tranches = [e for e, s in statut.items() if s != "non_tranche"]
    k_pr = sum(1 for e in tranches if statut[e] == "erreur")
    k_pe = sum(1 for e, s in statut.items() if s in ("erreur", "juste_avec_non_tranche", "non_tranche"))
    out = {"statut": statut, "principal": (k_pr, len(tranches)), "pessimiste": (k_pe, len(statut))}
    for nom, (k, n) in (("principal", out["principal"]), ("pessimiste", out["pessimiste"])):
        ea = sum(1 for e in statut if EFFETS_TIRES[e][0] == "a" and _erreur(statut[e], nom))
        eb = sum(1 for e in statut if EFFETS_TIRES[e][0] == "b" and _erreur(statut[e], nom))
        na = sum(1 for e in statut if EFFETS_TIRES[e][0] == "a" and (nom == "pessimiste" or statut[e] != "non_tranche"))
        nb = sum(1 for e in statut if EFFETS_TIRES[e][0] == "b" and (nom == "pessimiste" or statut[e] != "non_tranche"))
        out[f"{nom}_wilson"] = wilson(k, n)
        out[f"{nom}_pondere"] = 30 / 57 * (ea / na if na else 0) + 27 / 57 * (eb / nb if nb else 0)
        out[f"{nom}_strates"] = ((ea, na), (eb, nb))
    out["j1_atteint"] = out["principal_wilson"][1] <= 0.20
    out["j1_atteint_pessimiste"] = out["pessimiste_wilson"][1] <= 0.20
    return out


def _erreur(statut: str, variante: str) -> bool:
    if statut == "erreur":
        return True
    return variante == "pessimiste" and statut in ("juste_avec_non_tranche", "non_tranche")


# ── Second compte (30 situations J1) et statuts `verifiee` ──────────────────────────────────────

# Réponses de l'oracle au lot C2 bis (`reponses-oracle.md` § 7.1, 7.2) : issue de chaque situation J1 selon la règle
# figée. J07 : texte OCG ≠ TCG (R23) → non tranché. J17-J19 : N04 (restriction de script) → désaccord avéré, litige.
# J26 (N09) et J30 (N01, le moteur du lot C2 répondait « non couvert ») : désaccords du moteur du lot C2, corrigés au
# lot C3 (le moteur actuel rend la réponse de l'oracle).
J1_NON_TRANCHEES = {"J07": "R23 : texte OCG de la base de l'oracle"}
J1_DESACCORDS_C2 = {"J17": "N04", "J18": "N04", "J19": "N04", "J26": "N09", "J30": "N01 (non couvert)"}
J1_DESACCORDS_ACTUELS = {"J17": "N04", "J18": "N04", "J19": "N04"}
J30_EFFET = (LULU, 1)   # J30 n'exerce aucun effet : la clause en question est le déclencheur de `Luluwalilith` (N01)

# Questions résiduelles ouvertes (`questions-residuelles.md` § 2, effets nommés) : une carte touchée ne passe pas.
QUESTIONS_OUVERTES = {
    "Q1 (R23)": [(IECCLESIA, 3)], "Q2 (R22)": [(GSWORD, 2), (QUEM, 1), (QUEM, 2), (CHAMPIONS, 1)],
    "Q3 (N01)": [(LULU, 1)], "Q4 (N04)": [(AEON, 2), (MIXOUSIA, 1), (MIXOUSIA, 3)], "Q5 (R34)": [(TFTV, 1)],
    "Q6 (texte)": [(MIRROR, 2)], "Q7 (N12)": [(SANCTIFIRE, 3)],
}


def situations_des_lots_precedents(cat, deck):
    """(id, issue, effets exercés) des situations du jeu de tests et des situations J1, avec le moteur actuel.
    Jeu de tests : seules les situations rejouées en entier par l'oracle et conformes au moteur comptent."""
    from .scenarios import SCENARIOS, SCENARIOS_J1, executer_situation
    non_jouees = {"T52", "T53", "T67", "T68"}
    en_partie = {"T06", "T08", "T09", "T10", "T13", "T14", "T17", "T19", "T49", "T57", "T61", "T72"}
    out = []
    for fichier, scen in ((chemins.TESTS_YAML, SCENARIOS), (chemins.SITUATIONS_J1, SCENARIOS_J1)):
        jeu = charger_tests(fichier)
        for s in jeu.situations:
            sid = s["id"]
            if sid not in scen:
                continue
            regles.EXERCES.clear()
            ex = executer_situation(s, construire_depart(s, jeu, deck).etat, jeu.alias, cat, scen)
            exerces = set(regles.EXERCES)
            if sid == "J30":
                exerces.add(J30_EFFET)
            if sid.startswith("T"):
                if sid in non_jouees or sid in en_partie:
                    issue = "non_compte"
                elif sid == "T37":
                    issue = "non_tranche"
                else:
                    issue = "accord" if ex is not None and ex.statut == "verifie" else "desaccord"
            else:
                issue = ("non_tranche" if sid in J1_NON_TRANCHEES else
                         "desaccord" if sid in J1_DESACCORDS_ACTUELS else
                         "accord" if ex is not None and ex.statut == "verifie" else "desaccord")
            out.append((sid, issue, exerces))
    return out


def second_compte(lots) -> dict:
    """Effets exercés par les 30 situations J1 ; erreur = au moins un désaccord avéré (moteur du lot C2, moteur
    actuel)."""
    j1 = [(sid, ex) for sid, _, ex in lots if sid.startswith("J")]
    effets = sorted({e for _, ex in j1 for e in ex})
    out = {}
    for nom, desaccords in (("lot_C2", J1_DESACCORDS_C2), ("actuel", J1_DESACCORDS_ACTUELS)):
        statut = {}
        for e in effets:
            sits = [sid for sid, ex in j1 if e in ex]
            if any(s in desaccords for s in sits):
                statut[e] = "erreur"
            elif any(s not in J1_NON_TRANCHEES for s in sits):
                statut[e] = "juste"
            else:
                statut[e] = "non_tranche"
        tranches = [e for e, s in statut.items() if s != "non_tranche"]
        k = sum(statut[e] == "erreur" for e in tranches)
        k_pe = sum(statut[e] != "juste" for e in statut)
        out[nom] = {"statut": statut, "principal": (k, len(tranches)), "wilson": wilson(k, len(tranches)),
                    "pessimiste": (k_pe, len(statut)), "wilson_pessimiste": wilson(k_pe, len(statut))}
    return out


def statuts_verifiee(cat, comparaisons, lots, couverture) -> dict[str, tuple[bool, list[str]]]:
    """Règle figée (§ 8 de `j1-rapport.md`) appliquée au moteur tel qu'au moment de la comparaison."""
    accords: dict[tuple, list[str]] = {}
    bloquants: dict[tuple, list[str]] = {}
    non_tranches: dict[tuple, list[str]] = {}
    lignes = [(sid, issue, ex) for sid, issue, ex in lots]
    for c in comparaisons:
        concernes = set(c.exerces)
        if c.issue == "desaccord":
            concernes |= {(EFFETS_TIRES[e][1], EFFETS_TIRES[e][2]) for e in c.effets}
            if c.refus:
                concernes.add(c.refus)
        if c.issue == "non_tranche":
            concernes |= {(EFFETS_TIRES[e][1], EFFETS_TIRES[e][2]) for e in c.effets}
        lignes.append((c.id, c.issue, concernes))
    for sid, issue, ex in lignes:
        for e in ex:
            {"accord": accords, "desaccord": bloquants, "non_tranche": non_tranches}.get(issue, {}).setdefault(
                e, []).append(sid)
    questions = {e: q for q, effs in QUESTIONS_OUVERTES.items() for e in effs}
    out = {}
    for nom, effs in sorted(couverture.items()):
        pilote = sorted(effs)
        raisons = []
        if not pilote:
            raisons.append("aucun effet du pilote (rien d'exercé)")
        for n in pilote:
            e = (nom, n)
            if e in bloquants:
                raisons.append(f"effet {n} : désaccord ({', '.join(sorted(bloquants[e]))})")
            elif e not in accords:
                raisons.append(f"effet {n} : aucune situation en accord"
                               + (f" (non tranché : {', '.join(non_tranches[e])})" if e in non_tranches else ""))
        f = cat.get(nom)
        for e2 in (f.formalisation.effets if f is not None and f.formalisation is not None else ()):
            if (nom, e2.numero) in questions:
                raisons.append(f"effet {e2.numero} : question résiduelle {questions[(nom, e2.numero)]}")
        out[nom] = (not raisons, raisons)
    return out
