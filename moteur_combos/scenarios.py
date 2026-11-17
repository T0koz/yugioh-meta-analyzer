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

from .cartes import ALBAZ, ALUBER, BFUSION, RIND, TBKITT
from .catalogue import Catalogue
from .modele import Etat, LimiteConsommee, Verrou
from .regles import NE_PAS_ACTIVER, PASSER, Declaration, Evenement, Moteur, Resultat, Script

MATERIAUX_RIND = f"{ALBAZ} (deck) + {TBKITT} (deck)"


@dataclass(frozen=True)
class Scenario:
    test_id: str
    declaration: Declaration
    script: tuple[tuple[str, str], ...] = ()
    question_choix: str | None = None       # décision dont les options valent `attendu.choix`
    faits_sans_effet: str | None = None     # pourquoi les faits restés en texte libre ne changent pas le verdict
    role: str = ""                          # rôle dans la tranche 0


# Le combo de la tranche 0 : deux transitions.
SCRIPT_ALUBER = (("activer_declenche", f"{ALUBER}/1"), ("reponse", PASSER), ("carte", BFUSION))
SCRIPT_BFUSION_RIND = (
    ("reponse", PASSER), ("fusion", RIND), ("materiaux", MATERIAUX_RIND), ("placement", "zone_monstre_extra"),
    ("position", "attaque"), ("activer_declenche", f"{TBKITT}/2"), ("reponse", PASSER), ("carte", ALBAZ),
)

SCENARIOS: dict[str, Scenario] = {s.test_id: s for s in (
    # Combo, étape 1 : Invocation Normale d'Aluber, recherche de Branded Fusion.
    Scenario("T01", Declaration("invocation_normale", ALUBER), SCRIPT_ALUBER, question_choix="carte",
             role="combo, étape 1 (attendu)"),
    # Combo, étape 2 : Branded Fusion → Rindbrumm (Albaz + Tri-Brigade Springans Kitt du Deck) → Kitt rappelle Albaz.
    Scenario("T15", Declaration("activer", BFUSION, 1), SCRIPT_BFUSION_RIND, question_choix="carte",
             role="combo, étape 2 (attendu)"),
    # Négatif « hors timing » : une Magie Normale ne répond pas à un effet.
    Scenario("T60", Declaration("invocation_normale", ALUBER),
             (("activer_declenche", f"{ALUBER}/1"), ("reponse", "Nadir Servant")), role="négatif : hors timing"),
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
    # Exécutés en plus, sans règle supplémentaire.
    Scenario("T03", Declaration("invocation_normale", ALBAZ), role="en plus : une Invocation Normale par tour"),
    Scenario("T05", Declaration("invocation_normale", ALBAZ), (("activer_declenche", f"{ALBAZ}/1"),),
             role="en plus : effet qui ne peut rien faire (R01)"),
    Scenario("T08", Declaration("activer", BFUSION, 1),
             (("reponse", PASSER), ("fusion", "Granguignol the Dusk Dragon")), role="en plus : R05"),
    Scenario("T09", Declaration("activer", BFUSION, 1),
             (("reponse", PASSER), ("fusion", "The Dragon that Devours the Dogma")), role="en plus : R06"),
)}

COMBO = (SCENARIOS["T01"], SCENARIOS["T15"])


# ── Mémoire du tour : phrases traduites ────────────────────────────────────────────────────────

_EFFET_ACTIVE = re.compile(r"^effet d'([A-Z][A-Z0-9_]*) activé ce tour")
_VERROU_FUSION = re.compile(r"^verrou ([A-Z][A-Z0-9_]*) : Extra Deck = Fusion seulement$")


def traduire_memoire(etat: Etat, alias: dict[str, str], catalogue: Catalogue) -> tuple[Etat, list[str]]:
    """Traduit les phrases sans ambiguïté ; renvoie le nouvel état et la liste des traductions faites."""
    m = etat.memoire
    limites, verrous, restent, faites = set(m.limites), list(m.verrous), [], []
    for fait in m.faits_libres:
        e = _EFFET_ACTIVE.match(fait)
        v = _VERROU_FUSION.match(fait)
        if e and e.group(1) in alias:
            nom = alias[e.group(1)]
            f = catalogue.get(nom)
            jeux = {tuple(x.limites) for x in f.formalisation.effets} if f is not None and f.declaree else set()
            if len(jeux) == 1 and next(iter(jeux)):
                for forme, cle in next(iter(jeux)):
                    if forme != "par_exemplaire":
                        limites.add(LimiteConsommee(forme, cle, None))
                faites.append(f"« {fait} » → limite(s) {sorted(next(iter(jeux)))}")
                continue
        if v and v.group(1) in alias:
            verrous.append(Verrou(alias[v.group(1)], "extra_fusion_seulement"))
            faites.append(f"« {fait} » → verrou extra_fusion_seulement")
            continue
        restent.append(fait)
    memoire = replace(m, limites=frozenset(limites), verrous=tuple(verrous), faits_libres=tuple(restent))
    return replace(etat, memoire=memoire), faites


# ── Exécution d'une situation ──────────────────────────────────────────────────────────────────

@dataclass
class Execution:
    test_id: str
    statut: str                 # verifie | echec | en_attente_tranche_0
    detail: str
    resultat: Resultat | None
    traductions: list[str]


def executer_situation(situation: dict, etat: Etat, alias: dict[str, str], catalogue: Catalogue) -> Execution | None:
    sc = SCENARIOS.get(situation["id"])
    if sc is None:
        return None
    etat, faites = traduire_memoire(etat, alias, catalogue)
    res = Moteur(catalogue).jouer(etat, sc.declaration, Script(list(sc.script)))
    attendu = situation["attendu"]
    ecarts = []
    if res.verdict != attendu["verdict"]:
        ecarts.append(f"verdict {res.verdict} ({res.raison}), attendu {attendu['verdict']}")
    if attendu.get("choix") and sc.question_choix:
        d = res.decision(sc.question_choix)
        obtenus = set(d.valeurs()) | {o.valeur for o in d.indeterminees}
        attendus = {alias[a] for a in attendu["choix"]}
        if obtenus != attendus:
            ecarts.append(f"choix {sorted(obtenus)}, attendu {sorted(attendus)}")
    if res.faits_libres and not sc.faits_sans_effet:
        return Execution(sc.test_id, "en_attente_tranche_0",
                         f"faits en texte libre non traduits : {res.faits_libres}", res, faites)
    if ecarts:
        return Execution(sc.test_id, "echec", " ; ".join(ecarts), res, faites)
    return Execution(sc.test_id, "verifie", f"{res.verdict} — {res.raison or 'résolu'}", res, faites)


__all__ = ["SCENARIOS", "COMBO", "Scenario", "executer_situation", "traduire_memoire", "NE_PAS_ACTIVER"]
