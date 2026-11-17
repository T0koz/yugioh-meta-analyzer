"""Situations du jeu de tests exécutées par le moteur (tranche 0, TOK-90).

L'action d'une situation est écrite en français dans le YAML ; ici, elle est traduite **une fois, à la main**,
en une déclaration et une suite de réponses aux décisions du moteur. Le verdict attendu et la liste `choix`
restent ceux du YAML : ce fichier ne dit jamais ce qui est légal, il dit seulement quoi demander.

Mémoire du tour : quelques phrases du YAML sont traduites en objets formels (limites, verrous), seulement
pour les cartes formalisées et seulement quand la phrase n'a qu'une lecture. Les autres restent en texte
libre ; un verdict obtenu malgré elles n'est accepté que si le scénario dit pourquoi elles ne jouent pas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from typing import Callable

from .cartes import ALBAZ, ALUBER, BFUSION, RIND, TBKITT
from .cartes_j1 import (
    CHAMPIONS, MIXOUSIA, ASH, BHIGH, BOPENING, CARTESIA, COCA, DECCLESIA, DOGMA, EDD, FUWALOS, GARURA, GRANG, GSWORD, IECCLESIA, LULU,
    MERC, MIRROR, NADIR, OGRE, QUEM, SANCTIFIRE, SARC, SKITT, SPOLY, SPRIND, TFTV, TITAN, WHITE, AEON,
)
from .catalogue import Catalogue
from .modele import Etat, LimiteConsommee, Verrou
from .regles import NE_PAS_ACTIVER, PASSER, Declaration, ErreurScript, Evenement, Moteur, Partie, Resultat, Script

MATERIAUX_RIND = f"{ALBAZ} (deck) + {TBKITT} (deck)"


@dataclass(frozen=True)
class Scenario:
    test_id: str
    declaration: Declaration
    script: tuple[tuple[str, str], ...] = ()
    question_choix: str | None = None       # décision dont les options valent `attendu.choix`
    faits_sans_effet: str | None = None     # pourquoi les faits restés en texte libre ne changent pas le verdict
    role: str = ""                          # rôle dans la tranche 0 / J1
    prealables: tuple = ()                  # (Declaration, script) joués avant, tous légaux (lot C2)
    choix_rang: int = 0                     # rang de la décision `question_choix` quand elle revient plusieurs fois
    controle: Callable | None = None        # (res, situation, alias, catalogue, etat) -> [écarts] : contrôles en plus


PASSE = ("reponse", PASSER)


def D(nom: str, n: int) -> tuple[str, str]:
    return ("activer_declenche", f"{nom}/{n}")


def M(*parts: tuple[str, str]) -> str:
    return " + ".join(f"{n} ({z})" for n, z in parts)


# Le combo de la tranche 0 : deux transitions.
SCRIPT_ALUBER = (("activer_declenche", f"{ALUBER}/1"), ("reponse", PASSER), ("carte", BFUSION))
SCRIPT_BFUSION_RIND = (
    ("reponse", PASSER), ("fusion", RIND), ("materiaux", MATERIAUX_RIND), ("placement", "zone_monstre_extra"),
    ("position", "attaque"), ("activer_declenche", f"{TBKITT}/2"), ("reponse", PASSER), ("carte", ALBAZ),
)
FUSION_ZME = (("placement", "zone_monstre_extra"), ("position", "attaque"))


# ── Contrôles en plus (lot C2) : listes structurées du YAML ────────────────────────────────────

def _partie(catalogue, etat):
    return Partie(catalogue, etat, Script())


def _ctl_t07(res, s, alias, cat, etat):
    from .cartes import _bfusion_analyse
    possibles, _, _ = _bfusion_analyse(_partie(cat, etat))
    obtenu = {o.valeur: (sorted({ch[0][2].carte for _, ch, _ in o.donnees["paires"]}),
                         sorted({ch[1][2].carte for _, ch, _ in o.donnees["paires"]})) for o in possibles}
    attendu = {alias[c["fusion"]]: (sorted(alias[x] for x in c["materiel_1"]), sorted(alias[x] for x in c["materiel_2"]))
               for c in s["attendu"]["choix"]}
    return [] if obtenu == attendu else [f"Fusions et matériels {obtenu}, attendu {attendu}"]


def _ctl_t43(res, s, alias, cat, etat):
    from .cartes_j1 import _bhigh_paires
    obtenu = set(_bhigh_paires(_partie(cat, etat)))
    attendu = {(alias[c["revele"]], alias[e]) for c in s["attendu"]["choix"] for e in c["envoi"]}
    return [] if obtenu == attendu else [f"paires (révélé, envoyé) {sorted(obtenu)}, attendu {sorted(attendu)}"]


def _ctl_options(question, attendus_fn, rang=0):
    def ctl(res, s, alias, cat, etat):
        d = res.decision(question, rang)
        obtenus = set(d.valeurs()) | {o.valeur for o in d.indeterminees}
        attendus = attendus_fn(s, alias)
        return [] if obtenus == attendus else [f"{question} : {sorted(obtenus)}, attendu {sorted(attendus)}"]
    return ctl


def _ctl_t45(res, s, alias, cat, etat):
    d = res.decision("activer_declenche")
    attendu = {f"{GRANG}/1", f"{TBKITT}/2", NE_PAS_ACTIVER}
    ecarts = [] if set(d.valeurs()) == attendu else [f"premier choix {sorted(d.valeurs())}, attendu {sorted(attendu)}"]
    # Après le premier, le second reste facultatif : on peut n'activer que l'un des deux.
    d2 = res.decision("activer_declenche", 1)
    if set(d2.valeurs()) != {f"{TBKITT}/2", NE_PAS_ACTIVER}:
        ecarts.append(f"second choix {sorted(d2.valeurs())}")
    return ecarts


def _ctl_t49(res, s, alias, cat, etat):
    ecarts = _ctl_options("dessous", lambda s, a: {BFUSION, ASH, OGRE})(res, s, alias, cat, etat)
    if res.etat is None or [i.carte for i in res.etat.joueurs[0].deck_dessous] != [ASH]:
        ecarts.append("la carte placée n'est pas connue comme dernière carte du Deck")
    return ecarts


def _ctl_t59(res, s, alias, cat, etat):
    d = res.decision("activer_declenche", 1)
    raison = d.exclues.get(f"{ALUBER}/1", "")
    return [] if "déjà consommée" in raison else [f"2e Aluber : {d.exclues}"]


def _ctl_t61(res, s, alias, cat, etat):
    if res.etat is None:
        return ["pas d'état final"]
    occ = [o.instance for o in res.etat.zones_monstre_extra if o.instance.carte == MIRROR]
    return [] if occ and "effet_1_interdit_tour_suivant" in occ[0].restrictions else ["restriction de Mirrorjade absente"]


def _ctl_t63(res, s, alias, cat, etat):
    if res.etat is None:
        return ["pas d'état final"]
    d = [(e.source, e.echeance) for e in res.etat.memoire.effets_differes]
    return [] if (SARC, "standby_tour_5") in d else [f"effets différés {d}"]


def _ctl_t65(res, s, alias, cat, etat):
    r2 = Moteur(cat).jouer(etat, Declaration("activer", TFTV, 2), Script())
    return [] if r2.verdict == "illegal" else [f"2e effet de TFTV : {r2.verdict} ({r2.raison})"]


def _ctl_t19(res, s, alias, cat, etat):
    d = res.decision("pioche")
    deck = {i.carte for i in etat.joueurs[0].deck} - {DECCLESIA}
    return [] if d.type == "hasard" and set(d.valeurs()) == deck else [f"pioche : {d.type} {sorted(d.valeurs())}"]


def _ctl_t50(res, s, alias, cat, etat):
    v = [(x.source, x.cle) for x in res.etat.memoire.verrous] if res.etat else []
    return [] if (DECCLESIA, "extra_aucune") in v else [f"verrous {v}"]


def _ctl_t55(res, s, alias, cat, etat):
    d = res.decision("activer_declenche")
    return [] if f"{DOGMA}/2" in d.valeurs() else [f"effet de DOGMA non proposé : {d.valeurs()} {d.exclues}"]


def _ctl_t35(res, s, alias, cat, etat):
    d = res.decision("option")
    return [] if d.valeurs() == ["ajouter à la main", "Invoquer Spécialement en Défense"] else [f"options {d.valeurs()}"]


SCENARIOS: dict[str, Scenario] = {s.test_id: s for s in (
    # ── Tranche 0 (C1) ──────────────────────────────────────────────────────────────────────────
    # Combo, étape 1 : Invocation Normale d'Aluber, recherche de Branded Fusion.
    Scenario("T01", Declaration("invocation_normale", ALUBER), SCRIPT_ALUBER, question_choix="carte",
             role="combo, étape 1 (attendu)"),
    # Combo, étape 2 : Branded Fusion → Rindbrumm (Albaz + Tri-Brigade Springans Kitt du Deck) → Kitt rappelle Albaz.
    Scenario("T15", Declaration("activer", BFUSION, 1), SCRIPT_BFUSION_RIND, question_choix="carte",
             role="combo, étape 2 (attendu)"),
    # Négatif « hors timing » : une Magie Normale ne répond pas à un effet.
    Scenario("T60", Declaration("invocation_normale", ALUBER),
             (("activer_declenche", f"{ALUBER}/1"), ("reponse", NADIR)), role="négatif : hors timing"),
    # Négatif « effet déjà utilisé » : limite « 1 effet d'Aluber par tour », toutes copies confondues.
    Scenario("T04", Declaration("declenche", ALUBER, 1, Evenement("invocation_speciale", ALUBER, "terrain", "M2")),
             (("activer_declenche", f"{ALUBER}/1"),),
             faits_sans_effet="la note sur le 2e ALUBER (« invoqué en Défense par BOPENING ») dit comment il est "
                              "arrivé ; une limite consommée ne redevient disponible par aucun fait du tour",
             role="négatif : effet déjà utilisé"),
    # Négatif « matériel manquant » : aucun « Fallen of Albaz » en main, dans le Deck ni sur le terrain.
    Scenario("T11", Declaration("activer", BFUSION, 1), role="négatif : matériel manquant"),
    # Carte non encodée : « non couvert », jamais un résultat.
    Scenario("T68", Declaration("invocation_normale", "Lava Golem"), role="non couvert"),
    Scenario("T03", Declaration("invocation_normale", ALBAZ), role="en plus : une Invocation Normale par tour"),
    Scenario("T05", Declaration("invocation_normale", ALBAZ), (("activer_declenche", f"{ALBAZ}/1"),),
             role="en plus : effet qui ne peut rien faire (R01)"),
    Scenario("T08", Declaration("activer", BFUSION, 1),
             (PASSE, ("fusion", GRANG)), role="en plus : R05"),
    Scenario("T09", Declaration("activer", BFUSION, 1),
             (PASSE, ("fusion", DOGMA)), role="en plus : R06"),

    # ── J1 (C2) : les autres situations ────────────────────────────────────────────────────────
    Scenario("T02", Declaration("declenche", ALUBER, 1, Evenement("invocation_normale", ALUBER, "terrain", "M1")),
             (D(ALUBER, 1),), role="R01 : rien à chercher"),
    Scenario("T06", Declaration("phase_combat", "—"), role="R31 : pas de Phase de Combat au tour 1"),
    Scenario("T07", Declaration("activer", BFUSION, 1),
             (PASSE, ("fusion", SANCTIFIRE), ("materiaux", M((ALBAZ, "deck"), (CARTESIA, "deck")))) + FUSION_ZME,
             controle=_ctl_t07, role="R03, R05 : liste des Fusions et des matériels"),
    Scenario("T10", Declaration("activer", BFUSION, 1), (PASSE, ("fusion", MIRROR)), role="matériel Extra manquant"),
    Scenario("T12", Declaration("activer", BFUSION, 1), role="R07 : verrou rétroactif"),
    Scenario("T13", Declaration("activer", BOPENING, 1),
             (PASSE, ("defausse", ASH), ("carte", ALUBER), ("option", "ajouter à la main")), question_choix="carte",
             role="R07 : verrou non rétroactif"),
    Scenario("T14", Declaration("activer", BFUSION, 1), role="R08 : une activation par tour"),
    Scenario("T16", Declaration("activer", CARTESIA, 3), role="condition de Phase de Fin fausse"),
    Scenario("T17", Declaration("activer", TITAN, 3),
             (PASSE, ("carte", WHITE), ("option", "ajouter à la main")), question_choix="carte",
             role="R13 : verrou sur l'Extra Deck seulement"),
    Scenario("T18", Declaration("activer", NADIR, 1), (PASSE, ("envoi", TITAN), ("carte", ALBAZ)),
             question_choix="carte", role="R12 : ATK du monstre envoyé"),
    Scenario("T19", Declaration("activer", NADIR, 1),
             (PASSE, ("envoi", GARURA), ("carte", DECCLESIA), D(GARURA, 2), PASSE, ("pioche", ALUBER)),
             question_choix="carte", controle=_ctl_t19, role="R12 et hasard (pioche de Garura)"),
    Scenario("T20", Declaration("activer", CARTESIA, 2), role="R14 : verrou, rien d'invocable"),
    Scenario("T21", Declaration("activer", NADIR, 1), role="R08 : une activation par tour"),
    Scenario("T22", Declaration("declenche", QUEM, 2, Evenement("quitte_extra", TITAN, "cimetiere")),
             (D(QUEM, 2),), role="R09 : monstre de l'Extra Deck jamais invoqué"),
    Scenario("T23", Declaration("invocation_normale", QUEM), (D(QUEM, 1), PASSE, ("carte", ALBAZ)),
             question_choix="carte", role="R04 : « mentionne »"),
    Scenario("T24", Declaration("declenche", QUEM, 2, Evenement("quitte_extra", TITAN, "cimetiere")),
             (D(QUEM, 2), ("cible", ALBAZ), PASSE, ("position", "defense")), role="R10, R13"),
    Scenario("T25", Declaration("activer", CARTESIA, 1), (PASSE, ("position", "attaque")), role="R03, R15"),
    Scenario("T26", Declaration("activer", CARTESIA, 1), role="condition de présence fausse"),
    Scenario("T27", Declaration("invocation_procedure", IECCLESIA), role="R15, R16"),
    Scenario("T28", Declaration("activer", IECCLESIA, 2), (PASSE, ("carte", ALBAZ), ("position", "attaque")),
             question_choix="carte", role="R03, R11 : Sacrifice en coût"),
    Scenario("T29", Declaration("activer", WHITE, 1),
             (("cout", TITAN), PASSE, ("position", "attaque"), ("activer_declenche", NE_PAS_ACTIVER)),
             question_choix="cout", role="R04 : coût depuis l'Extra Deck"),
    Scenario("T30", Declaration("declenche", WHITE, 2, Evenement("invocation_speciale", WHITE, "terrain", "M1")),
             (D(WHITE, 2), PASSE, ("carte", IECCLESIA), ("position", "defense")), question_choix="carte",
             role="R11 : « Ecclesia »"),
    Scenario("T31", Declaration("invocation_synchro", LULU), role="R14, R26 : verrou avec exception"),
    Scenario("T32", Declaration("activer", TBKITT, 1), (PASSE, ("position", "attaque")), role="R27a : nom temporaire"),
    Scenario("T33", Declaration("activer", COCA, 2),
             (("cout", MERC), PASSE, D(MERC, 2), PASSE, ("carte", ALBAZ)), question_choix="carte",
             prealables=((Declaration("invocation_normale", COCA), ()),),
             controle=_ctl_options("cout", lambda s, a: {a[x] for x in s["attendu"]["choix_cout_coca"]}),
             role="R10, R27b : déclencheur pendant un coût"),
    Scenario("T34", Declaration("activer", BOPENING, 1), role="R17 : défausse impossible"),
    Scenario("T35", Declaration("activer", BOPENING, 1),
             (PASSE, ("defausse", ASH), ("carte", ALUBER), ("option", "ajouter à la main")), question_choix="carte",
             controle=_ctl_t35, role="R11, R17, R18"),
    Scenario("T36", Declaration("invocation_synchro", EDD),
             (("materiaux", M((WHITE, "M1"), (IECCLESIA, "M2"))),) + FUSION_ZME, role="R26 : Invocation Synchro"),
    Scenario("T37", Declaration("fin_de_tour", "—"), role="R23 : effet obligatoire (texte TCG)"),
    Scenario("T38", Declaration("activer", SPOLY, 1), role="R17 : coût impossible"),
    Scenario("T39", Declaration("activer", SPOLY, 1),
             (("cout", f"défausser {ASH}"), PASSE, ("fusion", GARURA),
              ("materiaux", M((CARTESIA, "terrain"), (QUEM, "terrain")))) + FUSION_ZME, role="R18, R20"),
    Scenario("T40", Declaration("activer", SPOLY, 1), role="la main n'est pas une source de matériel"),
    Scenario("T41", Declaration("activer", SPOLY, 1), role="R18 : posée ce tour"),
    Scenario("T42", Declaration("activer", SPOLY, 1), (("cout", f"défausser {ASH}"), ("reponse", f"{BOPENING}/1")),
             role="R19 : aucune réponse"),
    Scenario("T43", Declaration("activer", BHIGH, 1),
             (PASSE, ("revele", ALBAZ), ("envoi", SANCTIFIRE), ("appliquer", "ne pas appliquer")),
             controle=_ctl_t43, role="R17, R21 : Type et 2500"),
    Scenario("T44", Declaration("activer", BHIGH, 1), role="R01, R21"),
    Scenario("T45", Declaration("activer", CARTESIA, 2),
             (PASSE, ("fusion", GRANG), ("materiaux", M((CARTESIA, "terrain"), (TBKITT, "main")))) + FUSION_ZME
             + (D(GRANG, 1), D(TBKITT, 2), PASSE, ("carte", CARTESIA), ("carte", TITAN)),
             controle=_ctl_t45, role="R22 : déclencheurs simultanés (codé au lot C2)"),
    Scenario("T46", Declaration("activer", BHIGH, 2), role="R21 : un seul effet par tour"),
    Scenario("T47", Declaration("activer", SKITT, 1),
             (PASSE, ("position", "attaque"), ("activer_declenche", NE_PAS_ACTIVER)), role="R05, R32"),
    Scenario("T48", Declaration("activer", SKITT, 1), role="R05"),
    Scenario("T49", Declaration("declenche", SKITT, 2, Evenement("invocation_speciale", SKITT, "terrain", "M1")),
             (D(SKITT, 2), PASSE, ("carte", BFUSION), ("dessous", ASH)), question_choix="carte", controle=_ctl_t49,
             role="R02 : dessous du Deck"),
    Scenario("T50", Declaration("activer", DECCLESIA, 2),
             (PASSE, ("position", "attaque"), D(DECCLESIA, 3), PASSE, ("carte", QUEM)), question_choix="carte",
             controle=_ctl_t50, role="R04, R11"),
    Scenario("T51", Declaration("activer", CARTESIA, 2), (PASSE, ("fusion", GARURA)), role="Niveau 8 ou plus"),
    Scenario("T52", Declaration("declenche", TBKITT, 2, Evenement("envoyee_cimetiere", TBKITT, "cimetiere")),
             (D(TBKITT, 2), PASSE, ("carte", RIND)), question_choix="carte", role="R09 : correctement invoqué"),
    Scenario("T53", Declaration("activer", CARTESIA, 2),
             (PASSE, ("fusion", GRANG), ("materiaux", M((CARTESIA, "terrain"), (ALUBER, "main")))) + FUSION_ZME
             + (D(GRANG, 1), PASSE, ("carte", TITAN)), question_choix="carte", role="liste de Granguignol"),
    Scenario("T54", Declaration("activer", CARTESIA, 2),
             (PASSE, ("fusion", DOGMA), ("materiaux", M((ALBAZ, "terrain"), (CARTESIA, "terrain")))), role="R24"),
    Scenario("T55", Declaration("activer", CARTESIA, 2),
             (PASSE, ("fusion", DOGMA), ("materiaux", M((ALBAZ, "terrain"), (CARTESIA, "terrain"), (ALUBER, "main"))))
             + FUSION_ZME + (("activer_declenche", NE_PAS_ACTIVER),), controle=_ctl_t55, role="R24"),
    Scenario("T56", Declaration("activer", SPOLY, 1), role="R24 : Albion ne sert pas de matériel"),
    Scenario("T57", Declaration("activer", SPOLY, 1), role="R25 : Invoqué Normalement"),
    Scenario("T58", Declaration("activer", SPOLY, 1),
             (("cout", f"défausser {ASH}"), PASSE, ("fusion", SPRIND),
              ("materiaux", M((ALBAZ, "terrain"), (CARTESIA, "terrain")))) + FUSION_ZME, role="R25"),
    Scenario("T59", Declaration("invocation_normale", ALUBER),
             (D(ALUBER, 1), ("reponse", f"{BOPENING}/1"), PASSE, ("defausse", ASH), ("carte", ALUBER),
              ("option", "Invoquer Spécialement en Défense"), ("carte", BFUSION)), controle=_ctl_t59,
             role="R18 : chaîne de deux maillons"),
    Scenario("T61", Declaration("activer", MIRROR, 1),
             (("cout", TITAN), PASSE, ("bannir", f"{MERC} (M1)"), D(MERC, 2), PASSE, ("carte", WHITE)),
             controle=_ctl_t61, role="R10, R28"),
    Scenario("T62", Declaration("activer", COCA, 2),
             (("cout", MERC), PASSE, D(GSWORD, 2), D(MERC, 2), PASSE, ("carte", ALBAZ), ("carte", CARTESIA),
              ("position", "attaque")), question_choix="carte", choix_rang=1, role="R10, R22, R27b"),
    Scenario("T63", Declaration("activer", SARC, 1), (PASSE, ("carte", MERC), D(MERC, 2), PASSE, ("carte", ALBAZ)),
             controle=_ctl_t63, role="R10, R29"),
    Scenario("T64", Declaration("invocation_synchro", EDD), role="R26 : deux Syntoniseurs"),
    Scenario("T65", Declaration("activer", TFTV, 1), controle=_ctl_t65, role="R34"),
    Scenario("T66", Declaration("activer", CARTESIA, 2), (PASSE, ("fusion", AEON)), role="matériels d'Aeon"),
    Scenario("T69", Declaration("activer", FUWALOS, 1), (PASSE,), role="R30"),
    Scenario("T70", Declaration("invocation_normale", ALUBER), (D(ALUBER, 1), ("reponse", f"{ASH}/1"), PASSE),
             role="R30 : Ash contre son propre effet"),
)}

COMBO = (SCENARIOS["T01"], SCENARIOS["T15"])

# ── Situations J1 (lot C2) : `situations-j1.yaml`, verdicts = lecture de l'agent, à faire jouer à l'oracle ──

def _etat_final(res):
    return res.etat if res.etat is not None else None


def _ctl_ou(nom, zone, present=True):
    def ctl(res, s, alias, cat, etat):
        e = _etat_final(res)
        if e is None:
            return ["pas d'état final"]
        if zone == "terrain":
            ici = any(i.carte == nom for _, i in e.joueurs[0].cases) or any(
                o.instance.carte == nom for o in e.zones_monstre_extra)
        else:
            ici = any(i.carte == nom for i in getattr(e.joueurs[0], zone))
        return [] if ici == present else [f"{nom} {'absent de' if present else 'présent en'} {zone}"]
    return ctl


def _tous(*ctls):
    def ctl(res, s, alias, cat, etat):
        return [x for c in ctls for x in c(res, s, alias, cat, etat)]
    return ctl


def _ctl_modif(nom, champ, valeur):
    def ctl(res, s, alias, cat, etat):
        e = _etat_final(res)
        insts = [i for _, i in e.joueurs[0].cases if i.carte == nom] + [
            o.instance for o in e.zones_monstre_extra if o.instance.carte == nom] + [
            i for i in e.joueurs[0].cimetiere if i.carte == nom]
        ok = any((m.champ, m.valeur) == (champ, valeur) for i in insts for m in i.modifications)
        return [] if ok else [f"{nom} : modification {champ}={valeur} absente"]
    return ctl


def _ctl_atk(nom, atk):
    def ctl(res, s, alias, cat, etat):
        e = _etat_final(res)
        p = Partie(cat, e, Script())
        insts = [i for _, i in p.monstres() if i.carte == nom]
        obtenu = [p.atk_de(i) for i in insts]
        return [] if obtenu == [atk] else [f"ATK de {nom} : {obtenu}, attendu {atk}"]
    return ctl


def _ctl_j01(res, s, alias, cat, etat):
    e = _etat_final(res)
    ecarts = _ctl_ou(EDD, "terrain")(res, s, alias, cat, etat)
    if any(i.carte == ALBAZ for _, i in e.joueurs[0].cases):
        ecarts.append("ALBAZ Invoqué malgré l'annulation")
    return ecarts


def _ctl_j03(res, s, alias, cat, etat):
    e = _etat_final(res)
    cases = [(c, i.arrivee, i.position) for c, i in e.joueurs[0].cases if i.carte == EDD]
    return [] if cases and cases[0][0].startswith("M") and cases[0][1] == "autre" else [f"EDD : {cases}"]


def _ctl_j07(res, s, alias, cat, etat):
    r2 = Moteur(cat).jouer(res.etat, Declaration("fin_de_tour", "—"), Script())
    return [] if r2.verdict == "legal" else [f"fin de tour : {r2.verdict} ({r2.raison})"]


def _ctl_j09(res, s, alias, cat, etat):
    e = _etat_final(res)
    r = [i.restrictions for _, i in e.joueurs[0].cases if i.carte == COCA]
    return [] if r and "bannir_si_quitte_terrain" in r[0] else [f"restriction de COCA : {r}"]


def _ctl_j26(res, s, alias, cat, etat):
    d = res.decision("bannir")
    return [] if not any(v.startswith(TITAN) for v in d.valeurs()) else [f"TITAN bannissable : {d.valeurs()}"]


SPOLY_ASH = (("cout", f"défausser {ASH}"), PASSE)
J02_SCRIPT = (PASSE, ("carte", ALBAZ), ("position", "attaque"))
J09_SCRIPT = (("cout", f"Sacrifier {SKITT} (M1)"), PASSE, ("position", "attaque"))
J25_SCRIPT = SPOLY_ASH + (("fusion", TITAN), ("materiaux", M((ALBAZ, "terrain"), (GRANG, "terrain")))) + FUSION_ZME

SCENARIOS_J1: dict[str, Scenario] = {s.test_id: s for s in (
    Scenario("J01", Declaration("activer", EDD, 1), (("reponse", f"{RIND}/1"), PASSE, ("renvoyer", "ne pas renvoyer")),
             controle=_ctl_j01),
    Scenario("J02", Declaration("activer", EDD, 1), J02_SCRIPT, question_choix="carte"),
    Scenario("J03", Declaration("phase_de_fin", "—"), prealables=((Declaration("activer", EDD, 1), J02_SCRIPT),),
             controle=_ctl_j03),
    Scenario("J04", Declaration("activer", EDD, 2), (("cible", f"{TITAN} (cimetiere) + {ALUBER} (M1)"), PASSE),
             controle=_tous(_ctl_ou(TITAN, "extra"), _ctl_ou(EDD, "extra"), _ctl_ou(ALUBER, "deck"))),
    Scenario("J05", Declaration("activer", CARTESIA, 3), (PASSE,), controle=_ctl_ou(CARTESIA, "main")),
    Scenario("J06", Declaration("activer", BHIGH, 2), (PASSE,), controle=_ctl_ou(BHIGH, "main")),
    Scenario("J07", Declaration("activer", IECCLESIA, 3), (PASSE,), controle=_tous(_ctl_ou(IECCLESIA, "main"), _ctl_j07)),
    Scenario("J08", Declaration("invocation_procedure", IECCLESIA), (("position", "attaque"),),
             controle=_ctl_ou(IECCLESIA, "terrain")),
    Scenario("J09", Declaration("activer", COCA, 1), J09_SCRIPT, controle=_ctl_j09),
    Scenario("J10", Declaration("activer", SPOLY, 1),
             SPOLY_ASH + (("fusion", RIND), ("materiaux", M((ALBAZ, "terrain"), (COCA, "terrain"))))
             + FUSION_ZME, prealables=((Declaration("activer", COCA, 1), J09_SCRIPT),),
             controle=_tous(_ctl_ou(COCA, "bannies"), _ctl_ou(COCA, "cimetiere", False))),
    Scenario("J11", Declaration("invocation_normale", QUEM),
             (D(QUEM, 1), ("reponse", f"{OGRE}/1"), PASSE, ("carte", ALBAZ)),
             controle=_tous(_ctl_ou(QUEM, "cimetiere"), _ctl_ou(OGRE, "cimetiere"), _ctl_ou(ALBAZ, "cimetiere"))),
    Scenario("J12", Declaration("activer", TFTV, 1), (("cout", TITAN), ("cible", f"{ALUBER} (M1)"), PASSE),
             controle=_ctl_ou(ALUBER, "cimetiere")),
    Scenario("J13", Declaration("activer", TFTV, 2), (("cible", ALUBER), PASSE, ("position", "attaque"),
                                                       ("activer_declenche", NE_PAS_ACTIVER)),
             question_choix="cible", controle=_ctl_ou(ALUBER, "terrain")),
    Scenario("J14", Declaration("activer", NADIR, 1),
             (PASSE, ("envoi", TITAN), ("carte", ALBAZ), D(LULU, 1), PASSE, ("annuler", "ne pas annuler")),
             controle=_tous(_ctl_atk(ALUBER, 2300), _ctl_atk(LULU, 3000))),
    Scenario("J15", Declaration("activer", LULU, 2), (PASSE, ("carte", CARTESIA), ("position", "defense")),
             question_choix="carte"),
    Scenario("J16", Declaration("activer", SPOLY, 1),
             SPOLY_ASH + (("fusion", AEON), ("materiaux", M((GRANG, "terrain"), (RIND, "terrain")))) + FUSION_ZME
             + (D(AEON, 1), PASSE, ("bannir", f"{GRANG} (cimetiere)"), ("bannir", "terminer")),
             controle=_ctl_ou(GRANG, "bannies")),
    Scenario("J17", Declaration("activer", AEON, 2), (PASSE, ("attribut", "LIGHT")),
             controle=_ctl_modif(ALUBER, "attribut", "LIGHT")),
    Scenario("J18", Declaration("activer", MIXOUSIA, 1), (("cible", f"{ALUBER} (M1)"), PASSE, ("attribut", "WATER")),
             controle=_ctl_modif(ALUBER, "attribut", "WATER")),
    Scenario("J19", Declaration("activer", MIXOUSIA, 3), (PASSE, ("attribut", "LIGHT")),
             controle=_ctl_modif(MIXOUSIA, "attribut", "LIGHT")),
    Scenario("J20", Declaration("activer", SPRIND, 1), (PASSE, ("case", "M2"), ("detruire_colonne", "détruire")),
             controle=_ctl_ou(RIND, "cimetiere")),
    Scenario("J21", Declaration("activer", SPRIND, 2),
             (PASSE, ("carte", TBKITT), ("option", "Invoquer Spécialement"), ("position", "defense")),
             question_choix="carte", controle=_ctl_ou(TBKITT, "terrain")),
    Scenario("J22", Declaration("activer", CARTESIA, 2),
             (PASSE, ("fusion", DOGMA), ("materiaux", M((ALBAZ, "terrain"), (CARTESIA, "terrain"), (ALUBER, "main"))))
             + FUSION_ZME + (D(DOGMA, 2), PASSE, ("melanger", f"{ALBAZ} (cimetiere)"), ("melanger", "terminer")),
             controle=_ctl_ou(ALBAZ, "deck")),
    Scenario("J23", Declaration("activer", DOGMA, 3), (PASSE, ("carte", QUEM)), question_choix="carte"),
    Scenario("J24", Declaration("activer", TFTV, 1), (("cout", TITAN), ("cible", f"{DOGMA} (ZME_G)"), PASSE),
             controle=_tous(_ctl_ou(DOGMA, "terrain"), _ctl_atk(DOGMA, 3500))),
    Scenario("J25", Declaration("activer", SPOLY, 1), J25_SCRIPT, controle=_ctl_atk(TITAN, 3700)),
    Scenario("J26", Declaration("activer", MIRROR, 1), (("cout", SANCTIFIRE), PASSE, ("bannir", f"{MIRROR} (ZME_G)")),
             prealables=((Declaration("activer", SPOLY, 1), SPOLY_ASH + (
                 ("fusion", TITAN), ("materiaux", M((ALBAZ, "terrain"), (GRANG, "terrain"))),
                 ("placement", "zone_principale"), ("position", "attaque"))),),
             controle=_ctl_j26),
    Scenario("J27", Declaration("invocation_synchro", CHAMPIONS),
             (("materiaux", M((IECCLESIA, "M1"), (ALUBER, "M2"))),) + FUSION_ZME
             + (D(CHAMPIONS, 1), PASSE, ("carte", CARTESIA)), question_choix="carte"),
    Scenario("J28", Declaration("activer", CHAMPIONS, 2), (("cible", f"{ALUBER} (M1)"), PASSE, ("detruire", "détruire")),
             controle=_ctl_ou(ALUBER, "cimetiere")),
    Scenario("J29", Declaration("activer", TFTV, 1),
             (("cout", TITAN), ("cible", f"{RIND} (ZME_G)"), PASSE, ("remplacement", "bannir Branded Opening")),
             controle=_tous(_ctl_ou(RIND, "terrain"), _ctl_ou(BOPENING, "bannies"))),
    Scenario("J30", Declaration("invocation_synchro", LULU),
             (("materiaux", M((QUEM, "M1"), (DECCLESIA, "M2"), (ALUBER, "M3"))),) + FUSION_ZME),
)}



# ── Mémoire du tour : phrases traduites ────────────────────────────────────────────────────────
# Lot C2 : une phrase n'est traduite que si elle n'a qu'une lecture ; les autres restent en texte libre. Chaque
# motif dit ce qu'il pose. « par défaut » : la phrase décrit l'état par défaut (rien à poser).

_A = r"([A-Z][A-Z0-9_]*)"
_EFFET_ACTIVE = re.compile(rf"^effet d'{_A} activé ce tour")
_VERROU = re.compile(rf"^verrou {_A}(?: : (.*))?$")
VERROUS_PAR_CARTE = {   # clé de verrou posée par la formalisation de chaque carte, et phrase du YAML qui la décrit
    "Branded Fusion": ("extra_fusion_seulement", "Extra Deck = Fusion seulement"),
    "Branded Opening": ("extra_fusion_seulement", "Extra Deck = Fusion seulement"),
    "Nadir Servant": ("extra_aucune", "aucune Invocation Spéciale depuis l'Extra Deck"),
    "Dogmatika Ecclesia, the Virtuous": ("extra_aucune", "aucune Invocation Spéciale depuis l'Extra Deck"),
    "Fallen of the White Dragon": ("extra_fusion_synchro_n8", "Extra Deck = Fusion ou Synchro de Niveau 8 seulement"),
}
_ACTIVEE = re.compile(rf"^{_A} activée ce tour$")
_NIEME_EFFET = re.compile(rf"^(1er|2e) effet de {_A} utilisé")
_RECHERCHE = re.compile(rf"^effet de recherche de {_A} utilisé")
_ACTIVATION_DE = re.compile(rf"^effet d'activation de {_A} utilisé ce tour$")
_FUSION_ENVOYEE = re.compile(rf"^un monstre Fusion \({_A}\) a été envoyé au Cimetière ce tour$")
_AUCUNE_FUSION = re.compile(r"^aucun monstre Fusion envoyé au Cimetière ce tour$")
_ENVOYE_NON_INVOQUE = re.compile(rf"^{_A} envoyé au Cimetière ce tour \(non invoqué\)$")
_DEUX_ENVOYES = re.compile(rf"^{_A} et {_A} envoyés au Cimetière ce tour$")
_A_QUITTE = re.compile(rf"^{_A} vient de se résoudre : {_A} a quitté l'Extra Deck$")
_NON_FUSION_EXTRA = re.compile(r"^une Invocation Spéciale depuis l'Extra Deck d'un monstre non-Fusion a eu lieu ce tour$")
_FIN_NON_RESOLU = re.compile(rf"^effet de Phase de Fin d'{_A} non encore résolu$")
# Notes d'exemplaire (annotations du terrain ou du Cimetière).
_NOTE_SOURCE = re.compile(rf"^(?:Syntoniseur, Niveau \d+, )?(?:Invocation (?:Fusion|Normale|Synchro)|Invoqué(?:e)? "
                          rf"(?:Spécialement|Normalement)|vient d'être Invoqué(?:e)? Spécialement) par (?:{_A}|son effet)"
                          rf"(?:, matériels {_A} \+ {_A})?$")
_NOTE_1ER_EFFET = re.compile(rf"^1er effet utilisé(?: pour envoyer {_A})?$")
_NOTE_MATERIEL = re.compile(r"^Invoqué par Fusion ce tour, puis utilisé comme matériel$")


def _effets_actifs(f):
    return [e for e in f.formalisation.effets if e.genre not in ("restriction", "procedure")]


def _limites_nom_effet(f, numero_actif: int) -> list[LimiteConsommee]:
    e = _effets_actifs(f)[numero_actif - 1]
    return [LimiteConsommee(forme, cle, e.numero if forme == "par_nom_effet" else None)
            for forme, cle in e.limites if forme != "par_exemplaire"]


def _marquer(etat: Etat, nom: str, zone: str, **attrs) -> Etat:
    j = etat.joueurs[0]
    seq = list(getattr(j, zone))
    for k, i in enumerate(seq):
        if i.carte == nom:
            seq[k] = replace(i, **attrs)
            break
    return replace(etat, joueurs=(replace(j, **{zone: tuple(seq)}), etat.joueurs[1]))


def traduire_memoire(etat: Etat, alias: dict[str, str], catalogue: Catalogue) -> tuple[Etat, list[str]]:
    """Traduit les phrases sans ambiguïté ; renvoie le nouvel état et la liste des traductions faites."""
    m = etat.memoire
    limites, verrous, restent, faites = set(m.limites), list(m.verrous), [], []
    evenements, invocations = set(m.evenements), list(m.invocations_extra)
    marques: list[tuple[str, str, dict]] = []

    def fiche(a):
        f = catalogue.get(alias.get(a, ""))
        return f if f is not None and f.declaree else None

    for fait in m.faits_libres:
        e = _EFFET_ACTIVE.match(fait)
        if e and e.group(1) in alias:
            f = fiche(e.group(1))
            jeux = {tuple(x.limites) for x in f.formalisation.effets if x.limites} if f is not None else set()
            if len(jeux) == 1 and next(iter(jeux)):
                for forme, cle in next(iter(jeux)):
                    if forme != "par_exemplaire":
                        limites.add(LimiteConsommee(forme, cle, None))
                faites.append(f"« {fait} » → limite(s) {sorted(next(iter(jeux)))}")
                continue
        v = _VERROU.match(fait)
        if v and v.group(1) in alias and alias[v.group(1)] in VERROUS_PAR_CARTE:
            cle, phrase = VERROUS_PAR_CARTE[alias[v.group(1)]]
            if v.group(2) is None or v.group(2) == phrase:
                verrous.append(Verrou(alias[v.group(1)], cle))
                faites.append(f"« {fait} » → verrou {cle}")
                continue
        a = _ACTIVEE.match(fait)
        if a and (f := fiche(a.group(1))) is not None:
            formes = {(forme, cle) for x in f.formalisation.effets for forme, cle in x.limites
                      if forme == "activation_par_nom"}
            if len(formes) == 1:
                forme, cle = next(iter(formes))
                limites.add(LimiteConsommee(forme, cle))
                faites.append(f"« {fait} » → limite activation_par_nom")
                continue
        n = _NIEME_EFFET.match(fait)
        if n and (f := fiche(n.group(2))) is not None:
            for lim in _limites_nom_effet(f, 1 if n.group(1) == "1er" else 2):
                limites.add(lim)
            faites.append(f"« {fait} » → limite de l'effet {n.group(1)}")
            continue
        r = _RECHERCHE.match(fait)
        if r and (f := fiche(r.group(1))) is not None:
            effs = [x for x in f.formalisation.effets if "recherche_deck" in x.categories]
            if len(effs) == 1:
                for forme, cle in effs[0].limites:
                    limites.add(LimiteConsommee(forme, cle, effs[0].numero if forme == "par_nom_effet" else None))
                faites.append(f"« {fait} » → limite de l'effet {effs[0].numero}")
                continue
        ad = _ACTIVATION_DE.match(fait)
        if ad and (f := fiche(ad.group(1))) is not None:
            e1 = next(x for x in f.formalisation.effets if x.genre == "activation_carte")
            for forme, cle in e1.limites:
                limites.add(LimiteConsommee(forme, cle, e1.numero if forme == "par_nom_effet" else None))
            faites.append(f"« {fait} » → limite(s) {list(e1.limites)}")
            continue
        fe = _FUSION_ENVOYEE.match(fait)
        if fe and fe.group(1) in alias:
            evenements.add("fusion_envoyee_cimetiere")
            marques.append((alias[fe.group(1)], "cimetiere", dict(envoyee_cimetiere_ce_tour=True)))
            faites.append(f"« {fait} » → événement fusion_envoyee_cimetiere")
            continue
        if _AUCUNE_FUSION.match(fait) or _FIN_NON_RESOLU.match(fait):
            faites.append(f"« {fait} » → état par défaut, rien à poser")
            continue
        en = _ENVOYE_NON_INVOQUE.match(fait)
        if en and en.group(1) in alias:
            marques.append((alias[en.group(1)], "cimetiere", dict(envoyee_cimetiere_ce_tour=True,
                                                                    correctement_invoquee=False)))
            faites.append(f"« {fait} » → envoyé ce tour, jamais correctement invoqué")
            continue
        de = _DEUX_ENVOYES.match(fait)
        if de and de.group(1) in alias and de.group(2) in alias:
            for x in (de.group(1), de.group(2)):
                marques.append((alias[x], "cimetiere", dict(envoyee_cimetiere_ce_tour=True)))
                if (fx := catalogue.get(alias[x])) is not None and fx.est_fusion:
                    evenements.add("fusion_envoyee_cimetiere")
            faites.append(f"« {fait} » → envoyés ce tour")
            continue
        q = _A_QUITTE.match(fait)
        if q and q.group(2) in alias:
            marques.append((alias[q.group(2)], "cimetiere", dict(envoyee_cimetiere_ce_tour=True,
                                                                   correctement_invoquee=False)))
            faites.append(f"« {fait} » → {alias[q.group(2)]} envoyé ce tour sans invocation (l'événement est la "
                          "déclaration du scénario)")
            continue
        if _NON_FUSION_EXTRA.match(fait):
            vus = [(i.carte, i.arrivee) for _, i in etat.joueurs[0].cases] + [
                (o.instance.carte, o.instance.arrivee) for o in etat.zones_monstre_extra]
            nf = [(c, a.replace("invocation_", "")) for c, a in vus if a in ("invocation_synchro",)]
            if len(nf) == 1:
                invocations.append(nf[0])
                faites.append(f"« {fait} » → invocations_extra {nf[0]}")
                continue
        restent.append(fait)

    # Notes d'exemplaire.
    joueurs = list(etat.joueurs)
    zme = list(etat.zones_monstre_extra)

    def traiter(inst):
        garde = []
        for note in inst.notes:
            if _NOTE_SOURCE.match(note):
                faites.append(f"{inst.carte} : « {note} » → descriptif (source de l'invocation), rien à poser")
                continue
            un = _NOTE_1ER_EFFET.match(note)
            if un and (f := catalogue.get(inst.carte)) is not None and f.declaree:
                for lim in _limites_nom_effet(f, 1):
                    limites.add(lim)
                faites.append(f"{inst.carte} : « {note} » → limite de l'effet 1")
                continue
            if _NOTE_MATERIEL.match(note):
                inst = replace(inst, correctement_invoquee=True, envoyee_cimetiere_ce_tour=True)
                faites.append(f"{inst.carte} : « {note} » → correctement invoqué, envoyé ce tour")
                continue
            garde.append(note)
        return replace(inst, notes=tuple(garde))

    j0 = joueurs[0]
    joueurs[0] = replace(j0, cases=tuple((c, traiter(i)) for c, i in j0.cases),
                         cimetiere=tuple(traiter(i) for i in j0.cimetiere), main=tuple(traiter(i) for i in j0.main),
                         bannies=tuple(traiter(i) for i in j0.bannies))
    zme = [replace(o, instance=traiter(o.instance)) for o in zme]
    memoire = replace(m, limites=frozenset(limites), verrous=tuple(verrous), faits_libres=tuple(restent),
                      evenements=frozenset(evenements), invocations_extra=tuple(invocations))
    etat = replace(etat, joueurs=tuple(joueurs), zones_monstre_extra=tuple(zme), memoire=memoire)
    for nom, zone, attrs in marques:
        etat = _marquer(etat, nom, zone, **attrs)
    return etat, faites


# ── Exécution d'une situation ──────────────────────────────────────────────────────────────────

@dataclass
class Execution:
    test_id: str
    statut: str                 # verifie | echec | en_attente_tranche_0
    detail: str
    resultat: Resultat | None
    traductions: list[str]


def executer_situation(situation: dict, etat: Etat, alias: dict[str, str], catalogue: Catalogue,
                       scenarios: dict | None = None) -> Execution | None:
    sc = (SCENARIOS if scenarios is None else scenarios).get(situation["id"])
    if sc is None:
        return None
    etat, faites = traduire_memoire(etat, alias, catalogue)
    moteur = Moteur(catalogue)
    try:
        for decl, script in sc.prealables:
            pre = moteur.jouer(etat, decl, Script(list(script)))
            if pre.verdict != "legal":
                return Execution(sc.test_id, "echec", f"étape préalable {decl.type} {decl.carte} : {pre.verdict} "
                                 f"({pre.raison})", pre, faites)
            etat = pre.etat
        res = moteur.jouer(etat, sc.declaration, Script(list(sc.script)))
    except ErreurScript as exc:
        return Execution(sc.test_id, "echec", f"erreur de scénario : {exc}", None, faites)
    attendu = situation["attendu"]
    ecarts = []
    if res.verdict != attendu["verdict"]:
        ecarts.append(f"verdict {res.verdict} ({res.raison}), attendu {attendu['verdict']}")
    elif attendu.get("choix") and sc.question_choix:
        d = res.decision(sc.question_choix, sc.choix_rang)
        obtenus = set(d.valeurs()) | {o.valeur for o in d.indeterminees}
        attendus = {alias[a] for a in attendu["choix"]}
        if obtenus != attendus:
            ecarts.append(f"choix {sorted(obtenus)}, attendu {sorted(attendus)}")
        exclus = {alias[a] for a in attendu.get("exclus") or [] if a in alias}
        if obtenus & exclus:
            ecarts.append(f"options exclues par le YAML présentes : {sorted(obtenus & exclus)}")
    if sc.controle is not None and not ecarts:
        try:
            ecarts += sc.controle(res, situation, alias, catalogue, etat)
        except (IndexError, KeyError) as exc:
            ecarts.append(f"contrôle impossible : {exc!r}")
    if res.faits_libres and not sc.faits_sans_effet:
        return Execution(sc.test_id, "en_attente_tranche_0",
                         f"faits en texte libre non traduits : {res.faits_libres}", res, faites)
    if ecarts:
        return Execution(sc.test_id, "echec", " ; ".join(ecarts), res, faites)
    return Execution(sc.test_id, "verifie", f"{res.verdict} — {res.raison or 'résolu'}", res, faites)


__all__ = ["SCENARIOS", "SCENARIOS_J1", "COMBO", "Scenario", "executer_situation", "traduire_memoire", "NE_PAS_ACTIVER"]
