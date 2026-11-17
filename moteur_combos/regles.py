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

Non codé (renvoie `non_couvert`, jamais un résultat faux) : plusieurs effets déclenchés en même temps (ordre
de chaîne, R22), Invocation par Tribut, Pose, effets « When » qui ratent leur moment, Phase de Combat et Phase
de Fin, tour adverse (`hors_perimetre`).

Interface : `Moteur(catalogue).jouer(etat, declaration, script)` joue **une transition** (§ 2.2 des
définitions) et rend un `Resultat`. Chaque décision du joueur passe par le `Script` : le moteur calcule la
liste des options légales, le script en choisit une ; une réponse absente de la liste est illégale.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import permutations
from typing import Any

from .catalogue import Catalogue, Fiche
from .modele import (
    CELLULES_MAGIE, CELLULES_MONSTRE, ZONES_MONSTRE_EXTRA, Etat, Instance, LimiteConsommee, OccupantZoneExtra,
    Verrou,
)

NON_CODEE = "non_codee"            # résolution d'un effet déclaré mais pas encore formalisée
HORS_PERIMETRE = "hors_perimetre"  # résolution qui suppose l'adversaire (tour adverse, ses monstres)
NE_PAS_ACTIVER = "ne pas activer"
PASSER = "passer"

PHASES_PRINCIPALES = ("principale_1", "principale_2")
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
    type: str                      # 'invocation_normale' | 'activer' | 'declenche'
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
    def envoyer_cimetiere(self, zone: str, nom: str, cellule: str | None, role: str, comme: str) -> None:
        self.exiger_declaree(nom, f"envoyée au Cimetière ({comme}) : ses effets déclenchés sont inconnus")
        ancienne = self.retirer(zone, nom, cellule)
        f = self.fiche(nom)
        correcte = ancienne.correctement_invoquee if (f.est_extra and zone == "terrain") else (
            False if zone == "extra" else None)
        self.ajouter("cimetiere", Instance(carte=nom, venue_extra_deck=f.est_extra, correctement_invoquee=correcte,
                                           envoyee_cimetiere_ce_tour=True))
        self.evenements.append(Evenement("envoyee_cimetiere", nom, "cimetiere",
                                         detail=(("depuis", zone), ("comme", comme))))
        self.pas[-1].cartes.append((nom, role, zone, "cimetiere", None))

    def ajouter_main(self, zone: str, nom: str, role: str) -> None:
        self.exiger_declaree(nom, "ajoutée à la main : ses effets sont inconnus")
        self.retirer(zone, nom)
        self.ajouter("main", Instance(carte=nom))
        self.evenements.append(Evenement("ajoutee_main", nom, "main", detail=(("depuis", zone),)))
        self.pas[-1].cartes.append((nom, role, zone, "main", None))

    def invoquer_specialement(self, zone: str, nom: str, cellule_depart: str | None, cellule: str, position: str,
                              mode: str = "invocation_speciale") -> None:
        self.exiger_declaree(nom, "Invoquée Spécialement : ses effets sont inconnus")
        self.retirer(zone, nom, cellule_depart)
        f = self.fiche(nom)
        inst = Instance(carte=nom, face="visible", position=position, arrivee=mode, arrivee_ce_tour=True,
                        venue_extra_deck=f.est_extra, correctement_invoquee=True if f.est_extra else None)
        self.ajouter("terrain", inst, cellule)
        if zone == "extra":
            m = self.etat.memoire
            self.etat = replace(self.etat, memoire=replace(m, invocations_extra=m.invocations_extra + (
                (nom, mode.replace("invocation_", "")),)))
        self.evenements.append(Evenement("invocation_speciale", nom, "terrain", cellule,
                                         detail=(("depuis", zone), ("mode", mode))))
        self.pas[-1].cartes.append((nom, "deplacee", zone, "terrain", cellule))

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
            paires, inconnues, raison = self._affectations(f, materiaux, obligatoire)
            if paires:
                couverte = f.declaree
                possibles.append(Option(f.nom, couverte, None if couverte else "monstre Fusion non formalisé",
                                        {"paires": paires, "inconnues": inconnues}))
            elif inconnues or raison is None:
                indeterminees.append(Option(f.nom, False, raison or "matériels non formalisés", f.nom))
            else:
                exclues[f.nom] = raison
        return possibles, indeterminees, exclues

    def _affectations(self, f: Fiche, materiaux, obligatoire):
        """Affectations matériel → élément (un matériel par élément, R24). Renvoie (couvertes, indéterminées,
        raison d'impossibilité ou None si la ligne n'est pas lisible sans formalisation)."""
        elements = list(f.materiels)
        if any(e.minimum != 1 or e.plus for e in elements):
            return [], [], None  # éléments « 2 monstres… », « 2+ … » : lisibles seulement formalisés (aucun ici)
        predicats = getattr(f.formalisation, "materiels", None) if f.declaree else None
        couvertes, inconnues = [], []
        nommes_satisfaits = True
        for e in elements:
            if e.nom and not any(e.nom in self.noms_de(i) for _, _, i in materiaux):
                nommes_satisfaits = False
        if not nommes_satisfaits:
            noms = [e.nom for e in elements if e.nom]
            return [], [], f"aucun monstre « {noms[0]} » parmi les matériels disponibles"
        if predicats is None:
            return [], [("?", "ligne de matériels non formalisée")], None
        vus = set()
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
                elif fi is None or not pred(fi, inst):
                    ok = False
                    break
                if fi is None or not fi.declaree:
                    inconnu = f"{inst.carte} non formalisée : restrictions de matériel inconnues"
                elif getattr(fi.formalisation, "interdit_materiel_fusion", False):
                    ok = False
                    break
            if not ok:
                continue
            libelle = " + ".join(f"{inst.carte} ({zone})" for zone, _, inst in choisis)
            if libelle in vus:
                continue
            vus.add(libelle)
            (inconnues if inconnu else couvertes).append((libelle, choisis, inconnu))
        return couvertes, inconnues, ("aucune combinaison de matériels ne remplit la ligne" if not inconnues else None)

    def placements_extra(self, liberes: int = 0) -> list[str]:
        out = []
        if self.zme_disponible():
            out.append("zone_monstre_extra")
        if self.cases_monstre_libres() or liberes:
            out.append("zone_principale")
        return out

    def invoquer_par_fusion(self, f: Fiche, choisis) -> None:
        """Matériels au Cimetière, puis Invocation Fusion depuis l'Extra Deck (placement et position décidés)."""
        self.pas.append(Pas("resoudre", f"matériels de {f.nom}"))
        depuis_deck = False
        for zone, cellule, inst in choisis:
            self.envoyer_cimetiere(zone, inst.carte, cellule, "materiel", "materiel_fusion")
            depuis_deck |= zone == "deck"
        if depuis_deck:
            self.melanger()
        placements = self.placements_extra()
        p = self.choisir(Decision("placer", "placement", [Option(x) for x in placements]))
        cellule = self.zme_disponible() if p.valeur == "zone_monstre_extra" else self.cases_monstre_libres()[0]
        pos = self.choisir(Decision("choisir", "position", [Option("attaque"), Option("defense")]))
        self.pas.append(Pas("resoudre", f"Invocation Fusion de {f.nom}"))
        self.invoquer_specialement("extra", f.nom, None, cellule, pos.valeur, mode="invocation_fusion")

    # ── Activation ─────────────────────────────────────────────────────────────────────────────
    def legalite(self, nom: str, effet, lieu, evenement: Evenement | None = None) -> str | None:
        """None si l'activation est légale ; sinon la raison. NonCouvert / HorsPerimetre si indécidable."""
        inst = self.instance_en(lieu, nom)
        if inst is None:
            return f"{nom} n'est pas en {lieu[0]}"
        if lieu[0] not in effet.zones:
            return f"l'effet {effet.numero} de {nom} ne s'active pas depuis la zone {lieu[0]}"
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
        if effet.possible is not None:
            possible = effet.possible(self, lieu, nom)
            if possible is False:
                return "l'effet ne peut rien faire à la résolution (R01)"
            if possible is None:
                raise NonCouvert(f"effet {effet.numero} de {nom} : résolution indécidable (cartes non formalisées)")
        return None

    def activer(self, nom: str, effet, lieu) -> None:
        """Activation légale : poser la Magie, payer le coût, consommer les limites, ouvrir le maillon."""
        f = self.fiche(nom)
        self.pas.append(Pas("declarer", f"activation : {nom} (effet {effet.numero})", [(nom, "acteur", lieu[0], None, None)]))
        if effet.genre == "activation_carte" and lieu[0] == "main":
            cellule = self.cases_magie_libres()[0]
            inst = self.retirer("main", nom)
            self.ajouter("terrain", replace(inst, face="visible"), cellule)
            lieu = ("terrain", cellule)
            self.pas[-1].cartes[-1] = (nom, "acteur", "main", "terrain", cellule)
        if effet.cout is not None:
            options = effet.cout(self, lieu, nom)
            o = self.choisir(Decision("cout", "cout", options))
            self.pas.append(Pas("cout", f"coût : {o.valeur}"))
            o.donnees(self)
        self.consommer_limites(effet, lieu, nom)
        if effet.a_l_activation is not None:
            effet.a_l_activation(self, lieu, nom)
        self.chaine.append(Maillon(nom, effet.numero, lieu, effet.vitesse, f.est_monstre))
        self.notes.append(f"maillon {len(self.chaine)} : {nom} (effet {effet.numero})")

    def fenetre_reponse(self) -> None:
        """Après chaque maillon : l'adversaire (aucune réponse, pilote), puis le joueur du tour."""
        self.pas.append(Pas("enchainer", f"fenêtre adverse après le maillon {len(self.chaine)} : aucune réponse (pilote)"))
        dernier = self.chaine[-1]
        options, indeterminees, exclues = [Option(PASSER)], [], {}
        for zone in ("main", "terrain", "cimetiere"):
            vus = set()
            for lieu, inst in self._instances_publiques(zone):
                if inst.carte in vus:
                    continue
                vus.add(inst.carte)
                f = self.cat.get(inst.carte)
                if f is None:
                    continue
                if not f.declaree:
                    if f.magie_normale and zone == "main":
                        exclues[inst.carte] = "Magie Normale : vitesse 1, elle ne répond à aucun effet"
                    elif f.est_piege and zone == "main":
                        exclues[inst.carte] = "un Piège ne s'active pas depuis la main"
                    else:
                        indeterminees.append(Option(inst.carte, False, "non formalisée : effets rapides inconnus",
                                                    inst.carte))
                    continue
                for e in f.formalisation.effets:
                    rapide = e.genre == "rapide" or (e.genre == "activation_carte" and e.vitesse >= 2)
                    if not rapide:
                        if e.genre == "activation_carte" and zone == "main":
                            exclues.setdefault(inst.carte, f"vitesse {e.vitesse} : ne répond à aucun effet")
                        continue
                    if e.vitesse < dernier.vitesse:
                        exclues[f"{inst.carte}/{e.numero}"] = "vitesse insuffisante"
                        continue
                    raison = self.legalite(inst.carte, e, lieu)
                    if raison:
                        exclues[f"{inst.carte}/{e.numero}"] = raison
                        continue
                    couverte = e.resolution not in (NON_CODEE,)
                    options.append(Option(f"{inst.carte}/{e.numero}", couverte,
                                          None if couverte else "résolution non formalisée", (inst.carte, e, lieu)))
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
            if e.resolution == NON_CODEE:
                raise NonCouvert(f"résolution de l'effet {m.effet} de {m.carte} non formalisée")
            if e.resolution == HORS_PERIMETRE:
                raise HorsPerimetre(f"effet {m.effet} de {m.carte} : suppose l'adversaire ou un autre tour")
            e.resolution(self, m)
            if e.genre == "activation_carte" and f.est_magie and f.race in ("Normal", "Quick-Play"):
                if self.instance_en(m.lieu, m.carte) is not None:
                    self.pas.append(Pas("resoudre", f"{m.carte} va au Cimetière après résolution"))
                    self.envoyer_cimetiere(m.lieu[0], m.carte, m.lieu[1], "acteur", "apres_resolution")

    # ── Effets déclenchés ──────────────────────────────────────────────────────────────────────
    def declencheurs(self) -> bool:
        """Effets déclenchés par les événements en attente. Renvoie True si une nouvelle chaîne a été jouée."""
        evenements, self.evenements = self.evenements, []
        if not evenements:
            return False
        actives, exclues, obligatoires = [], {}, []
        for zone in ZONES_PUBLIQUES:
            for lieu, inst in self._instances_publiques(zone) if zone != "bannies" else []:
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
                    raison = self.legalite(inst.carte, e, lieu, evt)
                    if raison:
                        exclues[libelle] = raison
                        self.notes.append(f"déclencheur {libelle} non activable : {raison}")
                        continue
                    opt = Option(libelle, e.resolution != NON_CODEE, None if e.resolution != NON_CODEE
                                 else "résolution non formalisée", (inst.carte, e, lieu))
                    (actives if e.facultatif else obligatoires).append(opt)
        if not actives and not obligatoires and not exclues:
            return False
        if len(actives) + len(obligatoires) > 1:
            raise NonCouvert("plusieurs effets déclenchés en même temps : ordre de chaîne (R22) non codé en tranche 0")
        options = obligatoires or actives + [Option(NE_PAS_ACTIVER)]
        o = self.choisir(Decision("declarer", "activer_declenche", options, [], exclues))
        if o.valeur == NE_PAS_ACTIVER:
            return False
        nom, e, lieu = o.donnees
        self.activer(nom, e, lieu)
        self.fenetre_reponse()
        self.resoudre_chaine()
        return True

    def jouer_declencheurs(self) -> None:
        while self.declencheurs():
            pass

    # ── Déclarations (état stable) ─────────────────────────────────────────────────────────────
    def verifier_etat_ouvert(self) -> None:
        c = self.etat.cadre
        if c.joueur_actif != 0:
            raise HorsPerimetre("tour adverse")
        if c.phase not in PHASES_PRINCIPALES:
            raise NonCouvert(f"phase « {c.phase} » : seules les Phases Principales sont codées")
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
            raise NonCouvert("Invocation par Tribut non codée en tranche 0")
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
        self.verifier_etat_ouvert()
        f = self.fiche(nom)
        lieux = [((z, None), i) for z in ("main", "cimetiere") for i in getattr(self.j, z) if i.carte == nom]
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
        raisons = []
        for lieu, _ in lieux:
            raison = self.legalite(nom, e, lieu)
            if raison is None:
                self.activer(nom, e, lieu)
                self.fenetre_reponse()
                self.resoudre_chaine()
                return
            raisons.append(raison)
        raise Illegal(raisons[0])

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
            if declaration.type == "invocation_normale":
                p.invocation_normale(declaration.carte)
            elif declaration.type == "activer":
                p.activer_declaration(declaration.carte, declaration.effet)
            elif declaration.type == "declenche":
                if declaration.evenement is None:
                    raise ErreurScript("déclaration « declenche » sans événement")
                p.declenchement_initial(declaration.evenement)
            else:
                raise ErreurScript(f"déclaration inconnue : {declaration.type}")
            p.jouer_declencheurs()
            if declaration.type == "declenche" and not any(d.question == "activer_declenche" for d in p.decisions):
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
