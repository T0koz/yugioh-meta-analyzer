"""Formalisation des cartes de la tranche 0 (TOK-90) : les cinq cartes du combo, et elles seules.

Chaque carte est écrite contre l'empreinte du texte TCG de notre base (`text_sha256`) : si le texte change
(errata), la formalisation ne s'applique plus et la carte redevient « non couverte » (catalogue.py).
Les textes eux-mêmes ne sont pas recopiés ici (ils appartiennent à Konami, la base est hors du dépôt).

Une formalisation **déclare tous les effets** de la carte (zone, genre, déclencheur ou condition, limites) :
le moteur sait donc quand la carte pourrait agir. Une résolution peut rester :
- `NON_CODEE` : l'effet s'activerait dans le pilote, mais sa résolution n'est pas écrite → l'option apparaît
  comme non couverte, la choisir renvoie `non_couvert` (carte au statut `brouillon`) ;
- `HORS_PERIMETRE` : l'effet suppose l'adversaire ou un autre tour (§ 2.5) ; sa condition est écrite et
  fausse dans le pilote ; s'il devenait activable, le moteur renverrait `hors_perimetre`.

Numéro d'effet : ordre d'apparition dans le texte. Limites : formes du lot 18 (`modele.FORMES_LIMITE`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .modele import Instance, Verrou
from .regles import HORS_PERIMETRE, NON_CODEE, Decision, HorsPerimetre, Option, Pas

ALBAZ = "Fallen of Albaz"
ALUBER = "Aluber the Jester of Despia"
BFUSION = "Branded Fusion"
TBKITT = "Tri-Brigade Springans Kitt"
RIND = "Rindbrumm the Striking Dragon"


@dataclass(frozen=True)
class Effet:
    numero: int
    genre: str                                  # declenche | ignition | rapide | activation_carte | restriction
    zones: tuple[str, ...]                      # zones d'où il s'active : main, terrain, cimetiere
    limites: tuple[tuple[str, str | None], ...] = ()
    facultatif: bool = True                     # « You can »
    timing: str | None = None                   # déclenchés : 'if' | 'when'
    vitesse: int = 1
    declencheur: Callable | None = None         # (partie, evenement, lieu, nom) -> bool
    condition: Callable | None = None           # (partie, lieu, nom) -> raison | None
    cout: Callable | None = None                # (partie, lieu, nom) -> [Option] (donnees : paiement)
    possible: Callable | None = None            # (partie, lieu, nom) -> True | False | None (indécidable)
    a_l_activation: Callable | None = None      # (partie, lieu, nom) : ce qui s'applique dès l'activation
    resolution: Callable | str = NON_CODEE      # (partie, maillon) | NON_CODEE | HORS_PERIMETRE
    note: str = ""
    cible: Callable | None = None               # (partie, lieu, nom) -> [Option] : cible choisie à l'activation
    categories: tuple[str, ...] = ()            # ce que fait l'effet (lu par Ash Blossom) : recherche_deck…
    sans_reponse: bool = False                  # « Neither player can activate … in response » (R19)
    phases: tuple[str, ...] = ()                # « During the Main Phase » : phases permises (vide = toutes)


@dataclass(frozen=True)
class Formalisation:
    nom: str
    text_sha256: str
    effets: tuple[Effet, ...]
    materiels: tuple[Callable | None, ...] = ()  # un prédicat par élément décrit en mots (None : élément nommé)
    interdit_materiel_fusion: bool = False
    invocation_normale_interdite: bool = False
    sources: str = ""
    materiels_groupe: Callable | None = None     # (partie, [(fiche, exemplaire)]) -> True | False | None
    synchro_niveau_syntoniseur: int | None = None  # « 1 Level 4 Tuner + … » ; None : tout Syntoniseur
    un_seul_controle: bool = False               # « You can only control 1 "X" »
    insensible: Callable | None = None           # (partie, exemplaire, source, effet_active) -> bool
    bonus_atk: Callable | None = None            # (partie, exemplaire) -> int : gain d'ATK d'un effet continu
    effet_insensible: int = 1                    # n° de l'effet continu qui porte `insensible` (couverture)

    def effet(self, numero: int) -> Effet:
        for e in self.effets:
            if e.numero == numero:
                return e
        raise KeyError(f"{self.nom} : pas d'effet n° {numero}")

    @property
    def complete(self) -> bool:
        """Toutes les résolutions écrites (ou hors du pilote) : statut `formalisee`, sinon `brouillon`."""
        return all(e.resolution != NON_CODEE for e in self.effets)

    def manquantes(self) -> list[int]:
        return [e.numero for e in self.effets if e.resolution == NON_CODEE]


# ── Aides communes ─────────────────────────────────────────────────────────────────────────────

def _soi_invoque(p, ev, lieu, nom) -> bool:
    """« If this card is Normal or Special Summoned » : l'événement porte sur cet exemplaire, à cette case."""
    return (ev.type in ("invocation_normale", "invocation_speciale") and ev.carte == nom
            and lieu[0] == "terrain" and ev.cellule == lieu[1])


def _soi_envoye_cimetiere(p, ev, lieu, nom) -> bool:
    return ev.type == "envoyee_cimetiere" and ev.carte == nom and lieu[0] == "cimetiere"


def _jamais(p, ev, lieu, nom) -> bool:
    return False


def _option_carte(p, nom: str, quoi: str) -> Option:
    couverte = p.declaree(nom)
    return Option(nom, couverte, None if couverte else f"non formalisée : {quoi}, ses effets sont inconnus", nom)


def _materiaux(p, zones: tuple[str, ...]) -> list:
    """(zone, cellule, exemplaire) des monstres disponibles, au plus 2 copies par (zone, nom) : un effet du
    pilote n'utilise jamais plus de 2 matériels."""
    out, compte = [], {}
    for zone in zones:
        if zone == "terrain":
            pris = [("terrain", c, i) for c, i in p.monstres()]
        else:
            pris = [(zone, None, i) for i in p._multi(zone)]
        for z, c, i in pris:
            f = p.cat.get(i.carte)
            if f is None or not f.est_monstre:
                continue
            cle = (z, i.carte)
            if z != "terrain" and compte.get(cle, 0) >= 2:
                continue
            compte[cle] = compte.get(cle, 0) + 1
            out.append((z, c, i))
    return out


# ── Aluber the Jester of Despia ────────────────────────────────────────────────────────────────

def _aluber_cibles(p) -> list[str]:
    noms = sorted({i.carte for i in p._multi("deck")})
    return [n for n in noms if (f := p.cat.get(n)) and (f.est_magie or f.est_piege) and "Branded" in f.archetypes]


def _aluber_resolution(p, m) -> None:
    cibles = _aluber_cibles(p)
    if not cibles:
        p.notes.append("Aluber : plus aucune Magie/Piège « Branded » dans le Deck à la résolution")
        return
    o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée à la main") for n in cibles]))
    p.pas.append(Pas("resoudre", f"{o.valeur} : Deck → main"))
    p.ajouter_main("deck", o.valeur, "choisie")
    p.melanger()


ALUBER_F = Formalisation(
    nom=ALUBER,
    text_sha256="10b548571cd6b28eb488949a8e49cd078c9f40b101e0f746f952d7effddfd4fe",
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_nom_carte", ALUBER),), timing="if",
              declencheur=_soi_invoque, possible=lambda p, l, n: bool(_aluber_cibles(p)),
              resolution=_aluber_resolution, categories=("recherche_deck",),
              note="Invoqué Normalement ou Spécialement : ajouter 1 Magie/Piège « Branded » du Deck à la main."),
        Effet(2, "declenche", ("cimetiere",), (("par_nom_carte", ALUBER),), timing="if",
              declencheur=_jamais, resolution=HORS_PERIMETRE,
              note="Monstre Fusion détruit au combat ou quittant le terrain par un effet adverse : impossible au "
                   "tour 1 du pilote (pas de combat, pas d'adversaire)."),
    ),
    sources="T01, T02, T04, T59, T60 ; R01, R02, R11",
)


# ── Branded Fusion ─────────────────────────────────────────────────────────────────────────────

def _bfusion_analyse(p):
    candidats, exclues = [], {}
    for nom in sorted({i.carte for i in p.j.extra}):
        f = p.cat.get(nom)
        if f is None:
            continue
        if not f.est_fusion:
            exclues[nom] = "pas un monstre Fusion"
        elif not f.mentionne_comme_materiel(ALBAZ):
            exclues[nom] = f"ne mentionne pas « {ALBAZ} » comme matériel (R05)"
        else:
            candidats.append(f)
    possibles, indeterminees, exclues2 = p.analyser_fusions(
        candidats, _materiaux(p, ("main", "deck", "terrain")), nombre_exact=2)
    return possibles, indeterminees, {**exclues, **exclues2}


def _bfusion_possible(p, lieu, nom):
    possibles, indeterminees, _ = _bfusion_analyse(p)
    if any(o.couverte and o.donnees["paires"] for o in possibles):
        return True
    return None if (possibles or indeterminees) else False


def _bfusion_condition(p, lieu, nom):
    autres = [n for n, mode in p.etat.memoire.invocations_extra if mode != "fusion"]
    if autres:
        return (f"{autres[0]} a déjà été Invoqué depuis l'Extra Deck ce tour (non-Fusion) : « the turn you "
                f"activate this card » vaut pour tout le tour (R07)")
    return None


def _bfusion_resolution(p, m) -> None:
    possibles, indeterminees, exclues = _bfusion_analyse(p)
    if not possibles:
        p.notes.append("Branded Fusion : aucune Fusion possible à la résolution")
        return
    o = p.choisir(Decision("choisir", "fusion", possibles, indeterminees, exclues))
    paires = o.donnees["paires"]
    inconnues = [Option(lib, False, raison, None) for lib, _, raison in o.donnees["inconnues"]]
    om = p.choisir(Decision("choisir", "materiaux", [Option(lib, True, None, ch) for lib, ch, _ in paires], inconnues))
    p.invoquer_par_fusion(p.cat[o.valeur], om.donnees)


BFUSION_F = Formalisation(
    nom=BFUSION,
    text_sha256="6ced11a62d6eda163626750515e9d72f18b5fd9b184934313117d58a48642ff8",
    effets=(
        Effet(1, "activation_carte", ("main",), (("activation_par_nom", BFUSION),), vitesse=1,
              condition=_bfusion_condition, possible=_bfusion_possible,
              a_l_activation=lambda p, l, n: p.ajouter_verrou(Verrou(BFUSION, "extra_fusion_seulement")),
              resolution=_bfusion_resolution, categories=("envoi_deck_cimetiere",),
              note="Invocation Fusion d'un monstre qui mentionne Albaz comme matériel, avec 2 monstres de la main, "
                   "du Deck ou du terrain ; verrou « Extra Deck = Fusion » posé dès l'activation, pour tout le tour."),
    ),
    sources="T07 à T15, T72 ; R01, R03, R05, R06, R07, R08, R24",
)


# ── Fallen of Albaz ────────────────────────────────────────────────────────────────────────────

def _albaz_cout(p, lieu, nom) -> list[Option]:
    def payer(carte):
        return lambda partie: partie.envoyer_cimetiere("main", carte, None, "cout", "defausse")
    return [Option(f"défausser {c}", p.declaree(c), None if p.declaree(c) else
                   "non formalisée : envoyée au Cimetière, ses effets sont inconnus", payer(c))
            for c in sorted({i.carte for i in p.j.main})]


def _albaz_possible(p, lieu, nom):
    # « using monsters on either field …, including this card, but you cannot use other monsters you
    # control » : les autres matériels sont forcément des monstres adverses.
    adverses = p.monstres(1)
    fusions = [f for n in {i.carte for i in p.j.extra} if (f := p.cat.get(n)) and f.est_fusion]
    disponibles = 1 + len(adverses)
    if all(f.bornes_materiels()[0] > disponibles for f in fusions):
        return False
    raise HorsPerimetre("Fallen of Albaz : Fusion avec des monstres adverses (hors pilote)")


ALBAZ_F = Formalisation(
    nom=ALBAZ,
    text_sha256="30398e5ce1a2ea75fbc0c123ff76384694763915c7ffec58841e4af3e83ce367",
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_nom_effet", ALBAZ),), timing="if",
              declencheur=_soi_invoque, cout=_albaz_cout, possible=_albaz_possible, resolution=HORS_PERIMETRE,
              note="Coût : défausser 1 carte. Fusion avec cette carte et des monstres adverses seulement : sans "
                   "monstre adverse, aucune Fusion (2 matériels au moins) n'est possible."),
    ),
    sources="T05, T15, T71 ; R01",
)


# ── Tri-Brigade Springans Kitt ─────────────────────────────────────────────────────────────────

def _tbkitt_condition_main(p, lieu, nom):
    for _, i in p.monstres():
        if i.face == "visible" and ({"Tri-Brigade", "Springans"} & p.archetypes_de(i)) and TBKITT not in p.noms_de(i):
            return None
    return "aucun monstre « Tri-Brigade » ou « Springans » (autre que Tri-Brigade Springans Kitt) contrôlé"


def _tbkitt_invoquer_main(p, m) -> None:
    if not p.cases_monstre_libres():
        p.notes.append("Tri-Brigade Springans Kitt : plus de zone libre à la résolution")
        return
    pos = p.choisir(Decision("choisir", "position", [Option("attaque"), Option("defense")]))
    p.pas.append(Pas("resoudre", f"{TBKITT} : main → terrain"))
    p.invoquer_specialement("main", TBKITT, None, p.cases_monstre_libres()[0], pos.valeur)


def _tbkitt_cibles(p):
    options, indeterminees, exclues = [], [], {}
    for nom in sorted({i.carte for i in p.j.cimetiere}):
        f = p.cat.get(nom)
        if f is None or not f.est_monstre:
            continue
        inst = next(i for i in p.j.cimetiere if i.carte == nom)
        noms = p.noms_de(inst)
        if TBKITT in noms:
            exclues[nom] = "« except Tri-Brigade Springans Kitt »"
            continue
        if not ({"Tri-Brigade", "Springans"} & f.archetypes or ALBAZ in noms or ALBAZ in f.mentions):
            exclues[nom] = "ni « Tri-Brigade », ni « Springans », ni Fallen of Albaz, ni une carte qui le mentionne"
            continue
        if f.est_extra:
            invoques = [i.correctement_invoquee for i in p.j.cimetiere if i.carte == nom]
            if True not in invoques:
                if None in invoques:
                    indeterminees.append(Option(nom, False, "« correctement invoqué » non précisé (R09)", nom))
                else:
                    exclues[nom] = "jamais correctement invoqué : ne peut pas revenir du Cimetière (R09)"
                continue
        options.append(_option_carte(p, nom, "Invoquée Spécialement"))
    if not p.cases_monstre_libres():
        return [], [], {"*": "aucune zone Monstre principale libre"}
    return options, indeterminees, exclues


def _tbkitt_possible_gy(p, lieu, nom):
    options, indeterminees, _ = _tbkitt_cibles(p)
    if options:
        return True
    return None if indeterminees else False


def _tbkitt_rappeler(p, m) -> None:
    options, indeterminees, exclues = _tbkitt_cibles(p)
    if not options:
        p.notes.append("Tri-Brigade Springans Kitt : aucun monstre éligible à la résolution")
        return
    o = p.choisir(Decision("choisir", "carte", options, indeterminees, exclues))
    p.pas.append(Pas("resoudre", f"{o.valeur} : Cimetière → terrain, en Défense"))
    p.invoquer_specialement("cimetiere", o.valeur, None, p.cases_monstre_libres()[0], "defense")


TBKITT_F = Formalisation(
    nom=TBKITT,
    text_sha256="eb64efdb9639dc4b5ec3a8c17beb340393f86055079bd0d7ad69a6fff300bcd2",
    effets=(
        Effet(1, "ignition", ("main",), (("par_nom_effet", TBKITT),), condition=_tbkitt_condition_main,
              possible=lambda p, l, n: bool(p.cases_monstre_libres()), resolution=_tbkitt_invoquer_main,
              note="Depuis la main, si l'on contrôle un monstre « Tri-Brigade » ou « Springans » (autre que "
                   "lui) : s'Invoquer Spécialement."),
        Effet(2, "declenche", ("cimetiere",), (("par_nom_effet", TBKITT),), timing="if",
              declencheur=_soi_envoye_cimetiere, possible=_tbkitt_possible_gy, resolution=_tbkitt_rappeler,
              note="Envoyé au Cimetière : Invoquer Spécialement en Défense, depuis le Cimetière, 1 monstre "
                   "« Tri-Brigade », « Springans », ou Fallen of Albaz ou une carte qui le mentionne (sauf lui). "
                   "Ne cible pas ; un monstre éligible doit exister à l'activation (R33)."),
    ),
    sources="T15, T32, T47, T48, T52 ; R09, R10, R32, R33",
)


# ── Rindbrumm the Striking Dragon ──────────────────────────────────────────────────────────────

def _rind_condition_rapide(p, lieu, nom):
    if not p.chaine:
        return "aucun effet de monstre Fusion, Synchro, Xyz ou Lien n'est en cours d'activation"
    dernier = p.chaine[-1]
    f = p.cat.get(dernier.carte)
    if not (dernier.est_effet_de_monstre and f is not None and f.frame in {"fusion", "synchro", "xyz", "link"}):
        return "le dernier maillon n'est pas l'effet d'un monstre Fusion, Synchro, Xyz ou Lien"
    return None


def _rind_annuler(p, m) -> None:
    cible = m.donnees["cible_maillon"]
    if cible < len(p.chaine):
        p.chaine[cible].annule = True
        p.notes.append(f"Rindbrumm annule l'effet du maillon {cible + 1} ({p.chaine[cible].carte})")
    monstres = [(c, i) for c, i in p.monstres() if not p.insensible(i, RIND)]
    options = [Option(f"{i.carte} ({c})", True, None, (c, i.carte)) for c, i in monstres] + [Option("ne pas renvoyer")]
    o = p.choisir(Decision("choisir", "renvoyer", options))
    if o.valeur != "ne pas renvoyer":
        c, n = o.donnees
        f = p.cat[n]
        p.pas.append(Pas("resoudre", f"{n} renvoyé {'dans l’Extra Deck' if f.est_extra else 'en main'}"))
        if f.est_extra:
            p.vers_deck("terrain", n, c, "cible")
        else:
            p.retirer("terrain", n, c)
            p.ajouter("main", Instance(carte=n))
            p.pas[-1].cartes.append((n, "cible", "terrain", "main", None))


RIND_F = Formalisation(
    nom=RIND,
    text_sha256="5ee205d6d432b66ea3dfb1001d549242c6aa3903b11a88c6a47e9ae4b751aee1",
    materiels=(None, lambda fiche, inst: fiche.est_monstre and fiche.race in {"Beast", "Beast-Warrior", "Winged Beast"}),
    effets=(
        Effet(1, "rapide", ("terrain",), (("par_nom_effet", RIND),), vitesse=2, condition=_rind_condition_rapide,
              a_l_activation=lambda p, l, n: {"cible_maillon": len(p.chaine) - 1}, resolution=_rind_annuler,
              note="Effet rapide en réponse à l'effet d'un monstre Fusion/Synchro/Xyz/Lien (les siens aussi) : "
                   "annuler cet effet, puis on peut renvoyer 1 monstre du terrain en main (Extra Deck pour un monstre "
                   "de l'Extra Deck). Résolution écrite au lot C2."),
        Effet(2, "rapide", ("cimetiere",), (("par_nom_effet", RIND),), vitesse=2,
              condition=lambda p, l, n: None if p.etat.cadre.joueur_actif == 1 else "pendant le tour adverse seulement",
              resolution=HORS_PERIMETRE, note="Tour adverse seulement."),
    ),
    sources="T07, T15 ; R03, R05 (effet 1 : lot C2)",
)


FORMALISATIONS_TRANCHE_0: dict[str, Formalisation] = {f.nom: f for f in (ALUBER_F, BFUSION_F, ALBAZ_F, TBKITT_F, RIND_F)}

# Lot C2 (J1, TOK-118) : les 32 autres cartes du pilote, dans `cartes_j1.py` (import en fin de module : il lit les
# classes et aides ci-dessus).
from .cartes_j1 import FORMALISATIONS_J1  # noqa: E402

FORMALISATIONS: dict[str, Formalisation] = {**FORMALISATIONS_TRANCHE_0, **FORMALISATIONS_J1}
