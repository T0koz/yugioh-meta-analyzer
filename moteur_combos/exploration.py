"""Exploration bornée des combos (lot C3, jalon J2, TOK-119).

Le moteur de règles (`regles.Moteur`) joue **une transition** quand on lui donne une déclaration et un script de
réponses. L'exploration s'en sert sans le modifier :

1. **Déclarations candidates** d'un état stable (`declarations`) : Invocation Normale, procédure, Synchro, activation
   de chaque effet de chaque carte publique, passage à la Phase de Fin, fin du tour. Le moteur dit lesquelles sont
   légales (une déclaration illégale coûte un appel et rien d'autre).
2. **Toutes les façons de compléter une transition** (`developper`) : un script d'exploration rejoue la transition
   avec un préfixe de réponses ; à la première décision non couverte par le préfixe, il lève `Branche` avec la liste
   des options ; on relance une fois par option. Une décision à une seule option se prend seule (comme dans
   `Partie.choisir`). Une option non couverte (carte non formalisée, D5) est rejouée : le moteur rend
   `non_couvert`, la branche s'arrête avec ce motif.
3. **Graphe d'états** (`explorer`) : parcours en largeur, états dédoublonnés par leur empreinte complète (§ 2.3 des
   définitions) ; une arête vers un état déjà vu est un `retour_etat_connu` (pas ré-exploré) ; bornes : profondeur
   (en transitions), temps, nombre d'états. Un état non développé faute de temps ou de profondeur rend
   l'exploration **incomplète**.

**Filtres déclarés (D4)** : l'exhaustivité s'entend « à filtres près ». Chaque filtre est nommé, décrit, enregistré
avec le résultat (`cb_run.filters_json`) et peut être levé. Ils écartent des actions légales sans intérêt au tour 1
sans adversaire ; ils ne rendent jamais légale une action illégale.

Le parcours en largeur trouve, pour chaque état, un chemin **le plus court** en transitions ; un combo est un chemin
sans répétition d'état (§ 2.4 c). Aucune heuristique de qualité de plateau n'est utilisée (le système recense sans
juger) ; la **cible** (§ 2.4 e) ne sert qu'à signaler les états qui la remplissent.
"""

from __future__ import annotations

import heapq
import time
from collections import Counter, deque
from dataclasses import dataclass, field

from .catalogue import Catalogue
from .modele import CibleExploration, Etat, Instance, MemoireTour, ZonesJoueur, Cadre
from .regles import NE_PAS_ACTIVER, PASSER, Decision, Declaration, Moteur, Resultat, Script

VERSION_EXPLORATION = "c3-2026-11-18"

# ── Filtres déclarés (D4) ──────────────────────────────────────────────────────────────────────

CARTES_DE_REPONSE = ("Ash Blossom & Joyous Spring", "Ghost Ogre & Snow Rabbit", "Droll & Lock Bird",
                     "Mulcharmy Fuwalos")
EFFETS_D_ATTRIBUT = (("Hyperinvoked Aeon", 2), ("Mixousia the Confounder", 1), ("Mixousia the Confounder", 3))

FILTRES_DISPONIBLES: dict[str, str] = {
    "pas_de_reponse_a_soi": "Fenêtres de réponse : le joueur passe toujours (il n'enchaîne pas ses propres effets "
                            "rapides en réponse à ses propres maillons). Les effets déclenchés simultanés restent "
                            "ordonnés librement (R22).",
    "cartes_de_reponse_inertes": "Ash Blossom, Ghost Ogre, Droll & Lock Bird et Mulcharmy Fuwalos ne sont jamais "
                                 "activés ni Invoqués Normalement (ils répondent à l'adversaire ; contre soi : légal, "
                                 "sans intérêt, D4). Ils restent défaussables en coût et utilisables comme matériels "
                                 "s'ils arrivent sur le terrain autrement.",
    "position_attaque": "Position des monstres Invoqués Spécialement : Attaque seulement (la position ne change rien "
                        "au tour 1 sans combat ; `Ecclesia and the Dark Dragon` revient dans la position qu'elle "
                        "avait, sans effet sur la suite).",
    "zone_monstre_extra_d_abord": "Placement depuis l'Extra Deck : la Zone Monstre Extra si elle est libre, sinon une "
                                  "zone principale (une des deux options de D3 seulement ; peut manquer une ligne qui "
                                  "manque de zones principales).",
    "pas_de_changement_d_attribut": "Effets qui ne font que changer un Attribut (`Aeon` 2, `Mixousia` 1 et 3) non "
                                    "déclarés : aucune carte du pilote ne lit un Attribut changé au tour 1 sauf "
                                    "comme matériel (ligne écartée, à lever si un combo en dépend).",
    "pas_d_annulation_de_soi": "`Luluwalilith` : « ne pas annuler » seulement (annuler ses propres cartes au tour 1 "
                               "sans adversaire).",
    "aeon_sans_bannissement": "`Hyperinvoked Aeon`, effet 1 : « terminer » tout de suite (bannir ses propres cartes "
                              "ou celles de son Cimetière ; chaque sous-ensemble serait une branche).",
    "pioche_une_branche": "Pioche (`Garura`) : une seule branche (première carte de la liste triée), étiquetée "
                          "« hasard » ; un combo ne doit pas dépendre d'une pioche.",
}
FILTRES_PAR_DEFAUT = tuple(FILTRES_DISPONIBLES)


class Branche(Exception):
    """Décision non couverte par le préfixe de réponses : le script d'exploration rend la main."""

    def __init__(self, decision: Decision, valeurs: list[str]):
        super().__init__(decision.question)
        self.decision = decision
        self.valeurs = valeurs


def options_filtrees(d: Decision, filtres: frozenset[str]) -> list[str]:
    """Valeurs explorées pour une décision : les options légales (et indéterminées, rejouées → non couvert), moins
    ce que les filtres déclarés écartent."""
    valeurs = [o.valeur for o in d.options] + [o.valeur for o in d.indeterminees]
    q = d.question
    if q == "reponse" and "pas_de_reponse_a_soi" in filtres and PASSER in valeurs:
        return [PASSER]
    if q == "position" and "position_attaque" in filtres and "attaque" in valeurs:
        return ["attaque"]
    if q == "placement" and "zone_monstre_extra_d_abord" in filtres:
        return ["zone_monstre_extra"] if "zone_monstre_extra" in valeurs else valeurs[:1]
    if q == "annuler" and "pas_d_annulation_de_soi" in filtres and "ne pas annuler" in valeurs:
        return ["ne pas annuler"]
    if q == "bannir" and "aeon_sans_bannissement" in filtres and "terminer" in valeurs:
        return ["terminer"]
    if q == "pioche" and "pioche_une_branche" in filtres:
        return sorted(valeurs)[:1]
    if q == "activer_declenche" and "cartes_de_reponse_inertes" in filtres:
        valeurs = [v for v in valeurs if v.split("/")[0] not in CARTES_DE_REPONSE] or valeurs
    return valeurs


class ScriptExploration(Script):
    """Rejoue un préfixe de réponses, puis lève `Branche` à la première décision à plusieurs options explorées."""

    def __init__(self, prefixe: tuple[str, ...], filtres: frozenset[str]):
        super().__init__([])
        self.prefixe = prefixe
        self.i = 0
        self.filtres = filtres

    def repondre(self, d: Decision) -> str | None:
        # Décision forcée (une seule option légale) : `Partie.choisir` la prend seule ; elle ne consomme jamais
        # d'entrée du préfixe, au premier passage comme au rejeu (sinon le préfixe se décale).
        if len(d.options) == 1 and not d.indeterminees:
            return None
        if self.i < len(self.prefixe):
            v = self.prefixe[self.i]
            self.i += 1
            return v
        valeurs = options_filtrees(d, self.filtres)
        if len(valeurs) == 1:
            self.prefixe = self.prefixe + (valeurs[0],)
            self.i += 1
            return valeurs[0]
        raise Branche(d, valeurs)


# ── Déclarations candidates ────────────────────────────────────────────────────────────────────

GENRES_DECLARABLES = ("ignition", "activation_carte", "rapide")


def declarations(etat: Etat, cat: Catalogue, filtres: frozenset[str]) -> list[Declaration]:
    j = etat.joueurs[0]
    phase = etat.cadre.phase
    publiques: list[str] = []
    for zone in ("main", "cimetiere", "bannies"):
        publiques += [i.carte for i in getattr(j, zone)]
    publiques += [i.carte for _, i in j.cases]
    publiques += [o.instance.carte for o in etat.zones_monstre_extra if o.controleur == 0]
    noms = sorted(set(publiques))
    out: list[Declaration] = []
    if phase == "fin":
        for n in noms:
            f = cat.get(n)
            if f is None or not f.declaree:
                continue
            for e in f.formalisation.effets:
                if e.genre == "fin" or (e.genre == "rapide") or (e.genre == "activation_carte" and e.vitesse >= 2):
                    if _ecarte(n, e.numero, filtres):
                        continue
                    out.append(Declaration("activer", n, e.numero))
        out.append(Declaration("fin_de_tour", "—"))
        return out
    main = sorted({i.carte for i in j.main})
    for n in main:
        f = cat.get(n)
        if (f is not None and f.est_monstre and not etat.cadre.invocation_normale_utilisee
                and not ("cartes_de_reponse_inertes" in filtres and n in CARTES_DE_REPONSE)):
            out.append(Declaration("invocation_normale", n))
        if f is not None and f.declaree and any(e.genre == "procedure" for e in f.formalisation.effets):
            out.append(Declaration("invocation_procedure", n))
    for n in sorted({i.carte for i in j.extra}):
        f = cat.get(n)
        if f is not None and f.frame == "synchro":
            out.append(Declaration("invocation_synchro", n))
    for n in noms:
        f = cat.get(n)
        if f is None:
            continue
        if not f.declaree:
            out.append(Declaration("activer", n, 1))   # le moteur répondra « non couvert » si elle peut agir
            continue
        for e in f.formalisation.effets:
            if e.genre in GENRES_DECLARABLES and not _ecarte(n, e.numero, filtres):
                out.append(Declaration("activer", n, e.numero))
    out.append(Declaration("phase_de_fin", "—"))
    return out


def _ecarte(nom: str, numero: int, filtres: frozenset[str]) -> bool:
    if "cartes_de_reponse_inertes" in filtres and nom in CARTES_DE_REPONSE:
        return True
    if "pas_de_changement_d_attribut" in filtres and (nom, numero) in EFFETS_D_ATTRIBUT:
        return True
    return False


# ── Développement d'une transition ─────────────────────────────────────────────────────────────

@dataclass
class Issue:
    declaration: Declaration
    reponses: tuple[str, ...]
    resultat: Resultat


def developper(moteur: Moteur, etat: Etat, decl: Declaration, filtres: frozenset[str],
               max_branches: int = 5000) -> tuple[list[Issue], int]:
    """Toutes les façons légales de compléter la transition `decl` depuis `etat` (à filtres près).
    Rend (issues, nombre de rejouées). Les issues portent leur verdict (legal, non_couvert, hors_perimetre) ;
    les verdicts `illegal` sont écartés (déclaration ou suite impossible)."""
    issues: list[Issue] = []
    pile: list[tuple[str, ...]] = [()]
    rejouees = 0
    while pile and rejouees < max_branches:
        prefixe = pile.pop()
        s = ScriptExploration(prefixe, filtres)
        rejouees += 1
        try:
            res = moteur.jouer(etat, decl, s)
        except Branche as b:
            for v in reversed(b.valeurs):
                pile.append(s.prefixe + (v,))
            continue
        if res.verdict == "illegal":
            continue
        issues.append(Issue(decl, s.prefixe, res))
    return issues, rejouees


# ── Exploration ────────────────────────────────────────────────────────────────────────────────

@dataclass
class Arete:
    source: str
    cible: str | None            # None si la transition s'arrête (non couvert, hors périmètre)
    declaration: Declaration
    reponses: tuple[str, ...]
    verdict: str
    raison: str | None


@dataclass
class Rapport:
    depart: str
    etats: dict[str, Etat] = field(default_factory=dict)
    profondeur: dict[str, int] = field(default_factory=dict)
    parent: dict[str, Arete] = field(default_factory=dict)      # arête du premier chemin (le plus court)
    finals: dict[str, str] = field(default_factory=dict)        # état de Phase de Fin terminable -> board_id
    fin_aretes: dict[str, Arete] = field(default_factory=dict)  # arête « fin du tour » de chaque état final
    cibles_atteintes: list[str] = field(default_factory=list)
    cibles_acceptees: list[str] = field(default_factory=list)
    aretes: int = 0
    retours: int = 0
    rouverts: int = 0
    rejouees: int = 0
    non_couverts: Counter = field(default_factory=Counter)      # raison -> nombre de branches
    hors_perimetre: Counter = field(default_factory=Counter)
    tronques: int = 0                                           # états non développés (profondeur)
    non_developpes: int = 0                                     # états non développés (temps / nombre)
    secondes: float = 0.0
    arret: str = "epuise"                                       # epuise | temps | etats
    max_profondeur: int = 0
    filtres: tuple[str, ...] = ()
    strategie: str = "largeur"

    @property
    def complete(self) -> bool:
        return self.arret == "epuise" and not self.tronques and not self.non_couverts and not self.hors_perimetre

    def chemin(self, etat_id: str) -> list[Arete]:
        out = []
        while etat_id in self.parent:
            a = self.parent[etat_id]
            out.append(a)
            etat_id = a.source
        return list(reversed(out))


class _File:
    """File d'attente : FIFO (largeur) ou tas (meilleur d'abord sur la cible)."""

    def __init__(self, strategie: str, cible: CibleExploration | None):
        self.strategie, self.cible = strategie, cible
        self.fifo: deque = deque()
        self.tas: list = []
        self.n = 0

    def append(self, sid: str, etat: Etat, profondeur: int, bonus: int = 0) -> None:
        if self.strategie == "largeur":
            self.fifo.append(sid)
        else:
            self.n += 1
            # Priorité de type A* : profondeur + exemplaires de la cible encore manquants (le plus petit d'abord).
            # Un « meilleur d'abord » pur (manquants seuls) s'enfonçait dans des branches sans issue (G3).
            manquants = sum(c.minimum for c in self.cible.conditions) - score_cible(etat, self.cible)
            heapq.heappush(self.tas, (profondeur + manquants + bonus, manquants + bonus, self.n, sid))

    def popleft(self) -> str:
        return self.fifo.popleft() if self.strategie == "largeur" else heapq.heappop(self.tas)[3]

    def __len__(self) -> int:
        return len(self.fifo) + len(self.tas)

    def __bool__(self) -> bool:
        return len(self) > 0


def _zones(etat: Etat) -> dict[str, list[str]]:
    j = etat.joueurs[0]
    return {
        "main": [i.carte for i in j.main],
        "cimetiere": [i.carte for i in j.cimetiere],
        "bannies": [i.carte for i in j.bannies],
        "terrain": [i.carte for _, i in j.cases] + [o.instance.carte for o in etat.zones_monstre_extra
                                                     if o.controleur == 0],
    }


def score_cible(etat: Etat, cible: CibleExploration) -> int:
    """Nombre d'exemplaires demandés par la cible déjà présents (ordre de développement seulement)."""
    z = _zones(etat)
    return sum(min(z[c.zone].count(c.carte), c.minimum) for c in cible.conditions)


def cible_remplie(etat: Etat, cible: CibleExploration) -> bool:
    """Inclusion : chaque condition (zone, carte, minimum) est vraie dans l'état (côté joueur 0)."""
    zones = _zones(etat)
    return all(zones[c.zone].count(c.carte) >= c.minimum for c in cible.conditions)


def explorer(cat: Catalogue, depart: Etat, max_profondeur: int = 12, max_secondes: float = 60.0,
             max_etats: int = 200_000, filtres: tuple[str, ...] = FILTRES_PAR_DEFAUT,
             cible: CibleExploration | None = None, arreter_a_la_cible: bool = False,
             strategie: str = "largeur", accepter=None, priorite=None) -> Rapport:
    """`strategie` : « largeur » (parcours en largeur, chemins les plus courts) ou « cible » (priorité de type A* :
    profondeur + exemplaires de la cible encore manquants, le plus petit d'abord).
    La stratégie change l'ordre de développement, jamais l'ensemble des actions légales ni les filtres.
    `accepter(rapport, etat_id)` : condition de plus sur le chemin (jalons d'un guide) ; un état qui remplit la cible
    est noté dans `cibles_atteintes`, et dans `cibles_acceptees` si son chemin passe aussi les jalons ; l'arrêt à la
    cible attend un état accepté.
    `priorite(rapport, etat_id)` (stratégie « cible » seulement) : terme ajouté à la priorité. Sert au diagnostic
    « recherche guidée par la solution » (jalons du guide restants, TOK-140) : **hors mesure de J2**, puisque les jalons
    sont la réponse du guide ; il montre seulement qu'une séquence est jouable avec les règles codées."""
    if strategie not in ("largeur", "cible"):
        raise ValueError(f"stratégie inconnue : {strategie}")
    if strategie == "cible" and cible is None:
        raise ValueError("la stratégie « cible » demande une cible")
    moteur = Moteur(cat)
    fs = frozenset(filtres)
    d0 = depart.empreinte()
    r = Rapport(depart=d0, max_profondeur=max_profondeur, filtres=tuple(filtres), strategie=strategie)
    r.etats[d0] = depart
    r.profondeur[d0] = 0
    file = _File(strategie, cible)
    file.append(d0, depart, 0)
    t0 = time.monotonic()
    while file:
        if time.monotonic() - t0 > max_secondes:
            r.arret = "temps"
            r.non_developpes = len(file)
            break
        if len(r.etats) >= max_etats:
            r.arret = "etats"
            r.non_developpes = len(file)
            break
        sid = file.popleft()
        etat = r.etats[sid]
        if sid in r.finals:
            continue
        if r.profondeur[sid] >= max_profondeur:
            r.tronques += 1
            continue
        for decl in declarations(etat, cat, fs):
            issues, n = developper(moteur, etat, decl, fs)
            r.rejouees += n
            for iss in issues:
                res = iss.resultat
                r.aretes += 1
                if res.verdict != "legal":
                    (r.non_couverts if res.verdict == "non_couvert" else r.hors_perimetre)[res.raison or "?"] += 1
                    continue
                arrivee = res.etat
                if decl.type == "fin_de_tour":
                    # La fin du tour ne change pas l'état (elle vérifie seulement qu'aucun effet obligatoire
                    # n'attend, R23) : l'état de Phase de Fin devient un plateau final.
                    r.finals[sid] = etat.empreinte_plateau()
                    r.fin_aretes[sid] = Arete(sid, sid, decl, iss.reponses, res.verdict, res.raison)
                    continue
                aid = arrivee.empreinte()
                if aid in r.etats:
                    r.retours += 1
                    # Meilleur d'abord : un état déjà vu plus profond est rouvert par le chemin plus court (sinon
                    # la borne de profondeur couperait à tort sa suite). En largeur, cela n'arrive jamais.
                    if r.profondeur[sid] + 1 < r.profondeur[aid]:
                        r.profondeur[aid] = r.profondeur[sid] + 1
                        r.parent[aid] = Arete(sid, aid, decl, iss.reponses, res.verdict, res.raison)
                        r.rouverts += 1
                        file.append(aid, arrivee, r.profondeur[aid], priorite(r, aid) if priorite else 0)
                    continue
                r.etats[aid] = arrivee
                r.profondeur[aid] = r.profondeur[sid] + 1
                r.parent[aid] = Arete(sid, aid, decl, iss.reponses, res.verdict, res.raison)
                if cible is not None and cible_remplie(arrivee, cible):
                    r.cibles_atteintes.append(aid)
                    if accepter is not None and not accepter(r, aid):
                        file.append(aid, arrivee, r.profondeur[aid], priorite(r, aid) if priorite else 0)
                        continue
                    r.cibles_acceptees.append(aid)
                    if arreter_a_la_cible:
                        r.secondes = time.monotonic() - t0
                        r.arret = "cible"
                        return r
                file.append(aid, arrivee, r.profondeur[aid], priorite(r, aid) if priorite else 0)
    r.secondes = time.monotonic() - t0
    return r


# ── Méthode naïve : un joueur au hasard (avis data-scientist-ygo, lot C3) ─────────────────────────

def parties_au_hasard(cat: Catalogue, depart: Etat, graine: int, max_secondes: float = 30.0,
                      max_transitions: int = 20, filtres: tuple[str, ...] = FILTRES_PAR_DEFAUT,
                      cible: CibleExploration | None = None, accepter=None) -> dict:
    """Parties où, à chaque état, le joueur prend une transition légale au hasard (uniforme sur toutes les façons de
    compléter toutes les déclarations légales, mêmes filtres), jusqu'à la fin du tour ou `max_transitions`. Rend le
    nombre de parties jouées dans le budget et combien remplissent la cible (et les jalons, via `accepter`)."""
    import random
    rng = random.Random(graine)
    moteur = Moteur(cat)
    fs = frozenset(filtres)
    t0 = time.monotonic()
    parties = plateau = sequence = 0
    while time.monotonic() - t0 < max_secondes:
        r = Rapport(depart=depart.empreinte(), filtres=tuple(filtres))
        sid, etat = r.depart, depart
        r.etats[sid] = etat
        touche_plateau = touche_seq = False
        for _ in range(max_transitions):
            issues = []
            for decl in declarations(etat, cat, fs):
                issues += [i for i in developper(moteur, etat, decl, fs)[0] if i.resultat.verdict == "legal"]
            if not issues:
                break
            iss = rng.choice(issues)
            if iss.declaration.type == "fin_de_tour":
                break
            aid = iss.resultat.etat.empreinte()
            if aid not in r.etats:
                r.etats[aid] = iss.resultat.etat
                r.parent[aid] = Arete(sid, aid, iss.declaration, iss.reponses, "legal", None)
            sid, etat = aid, iss.resultat.etat
            if cible is not None and cible_remplie(etat, cible):
                touche_plateau = True
                if accepter is None or accepter(r, sid):
                    touche_seq = True
        parties += 1
        plateau += touche_plateau
        sequence += touche_seq
    return {"parties": parties, "plateau": plateau, "sequence": sequence,
            "secondes": round(time.monotonic() - t0, 1)}


# ── État de départ ─────────────────────────────────────────────────────────────────────────────

def etat_depart(deck, main: list[str], hors_jeu: list[str] = ()) -> Etat:
    """Tour 1, Phase Principale 1, nous commençons, terrain adverse vide ; Deck = liste moins la main et moins les
    cartes `hors_jeu` (cartes de la main supposées sans rôle dans un combo « à une carte » : ni en main, ni dans le
    Deck, pour qu'elles ne servent ni de matériel ni de coût)."""
    restant = Counter({c.nom: c.nombre for c in deck.cartes if c.zone == "main"})
    for n in list(main) + list(hors_jeu):
        if restant[n] <= 0:
            raise ValueError(f"{n} : plus d'exemplaire dans le Main Deck")
        restant[n] -= 1
    deck_i = tuple(Instance(carte=n) for n, k in sorted(restant.items()) for _ in range(k))
    extra_i = tuple(Instance(carte=c.nom) for c in deck.cartes if c.zone == "extra" for _ in range(c.nombre))
    return Etat(
        cadre=Cadre(tour=1, phase="principale_1"),
        joueurs=(ZonesJoueur(main=tuple(Instance(carte=n) for n in main), deck=deck_i, extra=extra_i),
                 ZonesJoueur(main_connue=False, deck_connu=False)),
        memoire=MemoireTour(),
    )
