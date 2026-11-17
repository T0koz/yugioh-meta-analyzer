"""Formalisation des 32 autres cartes du pilote Branded (lot C2, jalon J1, TOK-118).

Même contrat que `cartes.py` (tranche 0) : chaque carte est écrite contre l'empreinte `text_sha256` du texte TCG de
notre base ; tous les effets sont déclarés (zone, genre, déclencheur ou condition, limites, coût, cible) ; une
résolution est écrite, `NON_CODEE` (carte `brouillon`) ou `HORS_PERIMETRE` (suppose l'adversaire, la Phase de
Combat ou un autre tour ; condition écrite et fausse dans le pilote).

Méthode (décision du 16/11) : un LLM propose la formalisation depuis le texte officiel, le moteur la teste sur
`tests-branded.yaml`. **Le texte TCG de notre base fait foi** (R23 : `Incredible Ecclesia`, effet de Phase de Fin
obligatoire, contre l'oracle qui lit le texte OCG). Les points de règle que le texte ne tranche pas sont marqués ⚖
dans la note de l'effet et listés dans `docs/moteur-combos/situations-pour-oracle.md`.

Genres : `declenche`, `ignition`, `rapide`, `activation_carte`, `procedure` (Invocation Spéciale par procédure,
sans chaîne, R15), `fin` (« During the End Phase, if … : »), `restriction` (effet continu ou de remplacement :
ne s'active pas).
"""

from __future__ import annotations

from .cartes import (
    ALBAZ, Effet, Formalisation, _materiaux, _option_carte, _soi_envoye_cimetiere, _soi_invoque,
)
from .modele import EffetDiffere, Modification, Verrou
from .regles import HORS_PERIMETRE, Decision, HorsPerimetre, Illegal, NonCouvert, Option, Pas

ASH = "Ash Blossom & Joyous Spring"
CARTESIA = "Blazing Cartesia, the Virtuous"
BOPENING = "Branded Opening"
BHIGH = "Branded in High Spirits"
COCA = "Cocatorium the Heavy Metal Avian"
DECCLESIA = "Dogmatika Ecclesia, the Virtuous"
DROLL = "Droll & Lock Bird"
WHITE = "Fallen of the White Dragon"
OGRE = "Ghost Ogre & Snow Rabbit"
SARC = "Gold Sarcophagus"
QUEM = "Guiding Quem, the Virtuous"
IECCLESIA = "Incredible Ecclesia, the Virtuous"
FUWALOS = "Mulcharmy Fuwalos"
NADIR = "Nadir Servant"
SKITT = "Springans Kitt"
SPOLY = "Super Polymerization"
TFTV = "The Fallen & The Virtuous"
GSWORD = "The Golden Swordsoul"
MERC = "Tri-Brigade Mercourier"
SANCTIFIRE = "Albion the Sanctifire Dragon"
LULU = "Despian Luluwalilith"
EDD = "Ecclesia and the Dark Dragon"
GARURA = "Garura, Wings of Resonant Life"
GRANG = "Granguignol the Dusk Dragon"
AEON = "Hyperinvoked Aeon"
MIRROR = "Mirrorjade the Iceblade Dragon"
MIXOUSIA = "Mixousia the Confounder"
DRAGO = "Predaplant Dragostapelia"
SPRIND = "Sprind the Irondash Dragon"
DOGMA = "The Dragon that Devours the Dogma"
CHAMPIONS = "The Three Champions of Swordsoul"
TITAN = "Titaniklad the Ash Dragon"

PRINCIPALES = ("principale_1", "principale_2")
MODES_SPECIALES = ("invocation_speciale", "invocation_fusion", "invocation_synchro")
ATTRIBUTS = ("DARK", "EARTH", "FIRE", "LIGHT", "WATER", "WIND")
CATS_ASH = frozenset({"recherche_deck", "invocation_deck", "envoi_deck_cimetiere"})


# ── Aides ───────────────────────────────────────────────────────────────────────────────────────

def _continu(p, m):  # effet continu ou de remplacement : jamais résolu par une chaîne
    raise Illegal("effet continu : il ne s'active pas")


def _jamais(p, ev, lieu, nom) -> bool:
    return False


def _soi_invoque_special(p, ev, lieu, nom) -> bool:
    return (ev.type == "invocation_speciale" and ev.carte == nom and lieu[0] == "terrain" and ev.cellule == lieu[1])


def _soi_par(mode):
    def f(p, ev, lieu, nom):
        return _soi_invoque_special(p, ev, lieu, nom) and ev.a("mode") == mode
    return f


def _soi_banni(p, ev, lieu, nom) -> bool:
    return ev.type == "bannie" and ev.carte == nom and lieu[0] == "bannies"


def _quitte_extra(p, ev, lieu, nom) -> bool:
    return ev.type == "quitte_extra" and lieu[0] == "terrain"


def _porte_albaz(p, nom) -> bool:
    f = p.cat.get(nom)
    return f is not None and ALBAZ in f.noms


def _mentionne_albaz(p, nom) -> bool:
    f = p.cat.get(nom)
    return f is not None and ALBAZ in f.mentions


def _peut_revenir(p, inst) -> bool | None:
    """Un monstre de l'Extra Deck ne revient du Cimetière ou des bannies que s'il a été correctement invoqué (R09)."""
    f = p.cat.get(inst.carte)
    if f is None or not f.est_extra:
        return True
    return inst.correctement_invoquee


def _sous_condition(p, lieu, nom, test) -> str | None:
    return None if test else "condition fausse"


def _ss_cible_ok(p, lieu, nom) -> bool:
    return bool(p.cases_monstre_libres())


def _candidats(p, zones, filtre, zone_extra_verif=True) -> list[tuple[str, str, bool | None]]:
    """(zone, nom, admissible) des cartes des zones qui passent le filtre ; un exemplaire par (zone, nom), en
    gardant un exemplaire admissible s'il en existe un (R09)."""
    vus = {}
    for zone in zones:
        for inst in p._multi(zone) if zone in ("deck", "main", "cimetiere", "bannies", "extra") else []:
            if not filtre(inst):
                continue
            ok = _peut_revenir(p, inst) if (zone_extra_verif and zone in ("cimetiere", "bannies")) else True
            cle = (zone, inst.carte)
            if cle not in vus or (ok is True and vus[cle] is not True):
                vus[cle] = ok
    return [(z, n, ok) for (z, n), ok in sorted(vus.items())]


def _choisir_carte(p, question: str, candidats, quoi: str):
    """Choix d'une carte parmi (zone, nom, admissible) : décision sur le nom, puis sur la zone si le nom est dans
    plusieurs zones. Renvoie (zone, nom) ou None."""
    admis = [(z, n) for z, n, ok in candidats if ok is True]
    douteux = [(z, n) for z, n, ok in candidats if ok is None]
    noms = sorted({n for _, n in admis})
    if not noms and not douteux:
        return None
    options = [_option_carte(p, n, quoi) for n in noms]
    indet = [Option(n, False, "« correctement invoqué » non précisé (R09)", n) for _, n in douteux if n not in noms]
    o = p.choisir(Decision("choisir", question, options, indet))
    zones = sorted({z for z, n in admis if n == o.valeur})
    if len(zones) > 1:
        oz = p.choisir(Decision("choisir", "zone", [Option(z) for z in zones]))
        return oz.valeur, o.valeur
    return zones[0], o.valeur


def _ajouter_depuis(p, zone, nom):
    p.pas.append(Pas("resoudre", f"{nom} : {zone} → main"))
    p.ajouter_main(zone, nom, "choisie")
    if zone == "deck":
        p.melanger()


def _ss_depuis(p, zone, nom, position=None, restrictions=()):
    ok = p.invoquer_dans_case_libre(zone, nom, None, position, restrictions)
    if ok and zone == "deck":
        p.melanger()
    return ok


def _ajouter_ou_invoquer(p, zone, nom):
    options = [Option("ajouter à la main")]
    if p.cases_monstre_libres():
        options.append(Option("Invoquer Spécialement"))
    o = p.choisir(Decision("choisir", "option", options))
    if o.valeur == "ajouter à la main":
        _ajouter_depuis(p, zone, nom)
    else:
        _ss_depuis(p, zone, nom)


def _cout_soi(action: str):
    """Coût « discard this card » / « send this card … to the GY » / « Tribute this card » / « banish this card »."""
    def cout(p, lieu, nom):
        def payer(partie):
            if action == "defausser":
                partie.defausser(nom)
            elif action == "envoyer":
                partie.envoyer_cimetiere(lieu[0], nom, lieu[1], "cout", "cout")
            elif action == "sacrifier":
                partie.sacrifier(nom, lieu[1])
            elif action == "bannir":
                partie.bannir(lieu[0], nom, lieu[1], "cout", "cout")
        return [Option(f"{action} {nom}", True, None, payer)]
    return cout


def _monstres_visibles(p, joueurs=(0, 1)):
    return [(j, c, i) for j in joueurs for c, i in p.monstres(j) if i.face == "visible"]


def _cartes_visibles_terrain(p, sauf: tuple[str, str] | None = None):
    """(case, exemplaire) des cartes face visible du terrain du joueur (le terrain adverse est vide dans le pilote)."""
    out = []
    for c, i in p.monstres() + [x for x in p.j.cases if x[0] not in ("M1", "M2", "M3", "M4", "M5")]:
        if i.face == "visible" and (sauf is None or (c, i.carte) != sauf):
            out.append((c, i))
    return out


def _evt_fusion_envoyee(p) -> bool:
    return "fusion_envoyee_cimetiere" in p.etat.memoire.evenements


def _cond_fusion_envoyee(p, lieu, nom):
    return None if _evt_fusion_envoyee(p) else "aucun monstre Fusion envoyé au Cimetière ce tour"


def _cond_envoyee_ce_tour(p, lieu, nom):
    if any(i.carte == nom and i.envoyee_cimetiere_ce_tour for i in p.j.cimetiere):
        return None
    return "cette carte n'a pas été envoyée au Cimetière ce tour"


def _soi_vers_main(p, m):
    if any(i.carte == m.carte for i in p.j.cimetiere):
        p.pas.append(Pas("resoudre", f"{m.carte} : Cimetière → main"))
        p.ajouter_main("cimetiere", m.carte, "acteur")


def _ss_soi_main(p, m):
    if not any(i.carte == m.carte for i in p.j.main):
        p.notes.append(f"{m.carte} n'est plus en main à la résolution")
        return
    p.invoquer_dans_case_libre("main", m.carte)


def _options_attribut(p):
    return [Option(a) for a in ATTRIBUTS], [Option("DIVINE", False, "⚖ déclarer DIVIN : non tranché (situation pour l'oracle)", None)]


# ── Ash Blossom & Joyous Spring ────────────────────────────────────────────────────────────────

def _ash_condition(p, lieu, nom):
    if not p.chaine:
        return "aucune carte ni aucun effet en cours d'activation"
    if not (p.chaine[-1].categories & CATS_ASH):
        return "le dernier maillon n'ajoute pas du Deck à la main, n'invoque pas du Deck, n'envoie pas du Deck au Cimetière"
    return None


def _ash_resolution(p, m):
    cible = m.donnees["cible_maillon"]
    if cible < len(p.chaine):
        p.chaine[cible].annule = True
        p.notes.append(f"Ash Blossom annule l'effet du maillon {cible + 1} ({p.chaine[cible].carte})")


ASH_F = Formalisation(
    nom=ASH, text_sha256="7100d7fc2d46d6c4b55c8cef3f3c38495cb974a0aa6155eccc99ac8f7afb9838",
    effets=(
        Effet(1, "rapide", ("main",), (("par_nom_effet", ASH),), vitesse=2, cout=_cout_soi("defausser"),
              condition=_ash_condition, a_l_activation=lambda p, l, n: {"cible_maillon": len(p.chaine) - 1},
              resolution=_ash_resolution,
              note="En réponse à une activation qui ajoute du Deck à la main, invoque du Deck ou envoie du Deck au "
                   "Cimetière (catégories déclarées par chaque effet) : se défausser ; annuler cet effet. Contre "
                   "son propre effet aussi (R30)."),
    ),
    sources="T70 ; R30",
)


# ── Blazing Cartesia, the Virtuous ─────────────────────────────────────────────────────────────

def _cartesia_condition_main(p, lieu, nom):
    if any(ALBAZ in p.noms_de(i) for _, i in p.monstres() if i.face == "visible"):
        return None
    if any(ALBAZ in p.noms_de(i) for i in p.j.cimetiere):
        return None
    return "ni « Fallen of Albaz » contrôlé, ni dans le Cimetière"


def _cartesia_candidats(p):
    out = []
    for nom in sorted({i.carte for i in p.j.extra}):
        f = p.cat.get(nom)
        if f is not None and f.est_fusion and (f.niveau or 0) >= 8:
            out.append(f)
    return out


def _cartesia_exclues(p):
    return {n: "Niveau inférieur à 8" for n in {i.carte for i in p.j.extra}
            if (f := p.cat.get(n)) is not None and f.est_fusion and (f.niveau or 0) < 8}


def _cartesia_possible(p, lieu, nom):
    possibles, indet, _ = p.analyser_fusions(_cartesia_candidats(p), _materiaux(p, ("main", "terrain")), None)
    if any(o.couverte for o in possibles):
        return True
    return None if (possibles or indet) else False


def _cartesia_fusion(p, m):
    p.fusionner(_cartesia_candidats(p), _materiaux(p, ("main", "terrain")), None, _cartesia_exclues(p))


CARTESIA_F = Formalisation(
    nom=CARTESIA, text_sha256="6dc4e4d7f580ef19d08aa88dc231fac45683291ef7642a33aad5c05a1a969e5c",
    effets=(
        Effet(1, "ignition", ("main",), (("par_nom_effet", CARTESIA),), condition=_cartesia_condition_main,
              possible=_ss_cible_ok, resolution=_ss_soi_main,
              note="« Fallen of Albaz » contrôlé ou au Cimetière (noms « always treated as » compris, R03) : "
                   "s'Invoquer Spécialement depuis la main."),
        Effet(2, "rapide", ("terrain",), (("par_nom_effet", CARTESIA),), vitesse=2, phases=PRINCIPALES,
              possible=_cartesia_possible, resolution=_cartesia_fusion,
              note="Phase Principale, effet rapide : Invocation Fusion d'un monstre Fusion de Niveau 8 ou plus, "
                   "matériels de la main ou du terrain. Rien d'invocable (verrou, R14) : pas d'activation."),
        Effet(3, "fin", ("cimetiere",), (("par_nom_effet", CARTESIA),), condition=_cond_fusion_envoyee,
              resolution=_soi_vers_main,
              note="Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main."),
    ),
    sources="T16, T20, T25, T26, T45, T51, T53 à T55, T66 ; R03, R14, R15",
)


# ── Branded Opening ────────────────────────────────────────────────────────────────────────────

def _bopening_despia(p):
    return sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and f.est_monstre
                   and "Despia" in f.archetypes})


def _bopening_possible(p, lieu, nom):
    autres = len(p.j.main) - (1 if lieu[0] == "main" else 0)
    if autres < 1:
        return False
    return bool(_bopening_despia(p))


def _bopening_resolution(p, m):
    main = sorted({i.carte for i in p.j.main})
    if main:
        o = p.choisir(Decision("choisir", "defausse", [_option_carte(p, n, "défaussée") for n in main]))
        p.pas.append(Pas("resoudre", f"défausse : {o.valeur}"))
        p.defausser(o.valeur, "effet")
        cibles = _bopening_despia(p)
        if cibles:
            oc = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "prise du Deck") for n in cibles]))
            options = [Option("ajouter à la main")]
            if p.cases_monstre_libres():
                options.append(Option("Invoquer Spécialement en Défense"))
            oo = p.choisir(Decision("choisir", "option", options))
            if oo.valeur == "ajouter à la main":
                _ajouter_depuis(p, "deck", oc.valeur)
            else:
                _ss_depuis(p, "deck", oc.valeur, "defense")
    p.ajouter_verrou(Verrou(BOPENING, "extra_fusion_seulement"))


BOPENING_F = Formalisation(
    nom=BOPENING, text_sha256="4f3ae2ea21c70207b892bb0ff17017145338a58653590cc3d66dc20b7cb5f669",
    effets=(
        Effet(1, "activation_carte", ("main", "terrain"), (("par_nom_effet", BOPENING),), vitesse=2,
              possible=_bopening_possible, resolution=_bopening_resolution,
              categories=("recherche_deck", "invocation_deck"),
              note="Magie Jeu-Rapide. À la résolution (pas de « ; », R17) : défausser 1 carte, puis prendre 1 monstre "
                   "« Despia » du Deck, l'ajouter à la main ou l'Invoquer en Défense ; verrou « Extra Deck = Fusion » "
                   "après résolution (non rétroactif, R07). ⚖ Activation refusée s'il n'y a aucun « Despia » dans "
                   "le Deck (lecture de R01 sur « then »)."),
        Effet(2, "restriction", ("cimetiere",), (("par_nom_effet", BOPENING),), resolution=_continu,
              note="Effet de remplacement, ne s'active pas : un monstre Fusion du joueur serait détruit par un effet → "
                   "bannir cette carte du Cimetière à la place (codé dans `Partie.detruire`)."),
    ),
    sources="T13, T34, T35, T42, T59 ; R07, R11, R17, R18",
)


# ── Branded in High Spirits ────────────────────────────────────────────────────────────────────

def _bhigh_paires(p) -> list[tuple[str, str]]:
    """(monstre révélé, monstre Fusion envoyé) : Fusion de Niveau 8 de l'Extra Deck, même Type que le monstre
    révélé, 2500 en ATK ou en DEF (R21)."""
    out = []
    for r in sorted({i.carte for i in p.j.main if (f := p.cat.get(i.carte)) and f.est_monstre}):
        fr = p.cat[r]
        for e in sorted({i.carte for i in p.j.extra}):
            fe = p.cat.get(e)
            if fe and fe.est_fusion and fe.niveau == 8 and fe.race == fr.race and 2500 in (fe.atk, fe.defense):
                out.append((r, e))
    return out


def _bhigh_resolution(p, m):
    paires = _bhigh_paires(p)
    if not paires:
        p.notes.append("Branded in High Spirits : rien à révéler ni à envoyer à la résolution")
        return
    revelables = sorted({r for r, _ in paires})
    o = p.choisir(Decision("choisir", "revele", [Option(r, True, None, r) for r in revelables]))
    envois = sorted({e for r, e in paires if r == o.valeur})
    oe = p.choisir(Decision("choisir", "envoi", [_option_carte(p, e, "envoyée au Cimetière") for e in envois]))
    p.pas.append(Pas("resoudre", f"révèle {o.valeur}, envoie {oe.valeur} de l'Extra Deck au Cimetière"))
    p.envoyer_cimetiere("extra", oe.valeur, None, "effet", "effet")
    cibles = sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and f.est_monstre
                     and (ALBAZ in f.noms or ALBAZ in f.mentions)})
    if not any(i.carte == o.valeur for i in p.j.main):
        return
    oa = p.choisir(Decision("choisir", "appliquer", [Option("appliquer"), Option("ne pas appliquer")]))
    if oa.valeur == "ne pas appliquer":
        return
    p.pas.append(Pas("resoudre", f"défausse du monstre révélé : {o.valeur}"))
    p.defausser(o.valeur, "effet")
    if cibles:
        oc = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée à la main") for n in cibles]))
        _ajouter_depuis(p, "deck", oc.valeur)


BHIGH_F = Formalisation(
    nom=BHIGH, text_sha256="e67b9a8e5bc7da508dd0d54d6a7238cdbe74f8f5d67427c39952698928ea1098",
    effets=(
        Effet(1, "activation_carte", ("main", "terrain"), (("par_nom_carte", BHIGH),), vitesse=2,
              possible=lambda p, l, n: bool(_bhigh_paires(p)), resolution=_bhigh_resolution,
              categories=("recherche_deck",),
              note="Magie Jeu-Rapide. À la résolution (R17) : révéler 1 monstre de la main et envoyer de l'Extra Deck "
                   "au Cimetière 1 monstre Fusion de Niveau 8 du même Type avec 2500 en ATK ou en DEF (R21), puis "
                   "on peut défausser le monstre révélé et ajouter « Fallen of Albaz » ou un monstre qui le "
                   "mentionne, du Deck."),
        Effet(2, "fin", ("cimetiere",), (("par_nom_carte", BHIGH),), condition=_cond_fusion_envoyee,
              resolution=_soi_vers_main,
              note="Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main. Un seul "
                   "effet de la carte par tour (T46)."),
    ),
    sources="T43, T44, T46 ; R17, R21",
)


# ── Cocatorium the Heavy Metal Avian ───────────────────────────────────────────────────────────

RACES_BETE = {"Beast", "Beast-Warrior", "Winged Beast"}


def _coca_cout_tribut(p, lieu, nom):
    def payer(c, n):
        return lambda partie: partie.sacrifier(n, c)
    return [Option(f"Sacrifier {i.carte} ({c})", p.declaree(i.carte),
                   None if p.declaree(i.carte) else "non formalisée : envoyée au Cimetière", payer(c, i.carte))
            for c, i in p.monstres() if p.race_de(i) in RACES_BETE]


def _coca_ss(p, m):
    zone = m.lieu[0]
    if not any(i.carte == COCA for i in p._multi(zone)):
        p.notes.append("Cocatorium a quitté sa zone avant la résolution")
        return
    p.invoquer_dans_case_libre(zone, COCA, restrictions=("bannir_si_quitte_terrain",))


def _coca_cout_bannir(p, lieu, nom):
    noms = sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and f.est_monstre
                   and (f.niveau or 0) <= 4 and f.race in RACES_BETE})

    def payer(n):
        def f(partie):
            partie.bannir("deck", n, None, "cout", "cout")
            partie.melanger()
            return {"banni": n}
        return f
    return [Option(n, p.declaree(n), None if p.declaree(n) else "non formalisée : bannie", payer(n)) for n in noms]


def _coca_nom(p, m):
    lieu = m.lieu
    inst = p.instance_en(lieu, COCA)
    if inst is None or inst.face != "visible":
        p.notes.append("Cocatorium n'est plus face visible sur le terrain : rien ne change")
        return
    b = p.cat[m.donnees["banni"]]
    p.pas.append(Pas("resoudre", f"Cocatorium prend le nom, le Type, l'Attribut et le Niveau de {b.nom}"))
    p.modifier(lieu, COCA, (Modification("nom", b.nom, "phase_de_fin"), Modification("race", b.race, "phase_de_fin"),
                            Modification("attribut", b.attribut, "phase_de_fin"),
                            Modification("niveau", str(b.niveau), "phase_de_fin")))


COCA_F = Formalisation(
    nom=COCA, text_sha256="2dddf00eb1767c97c47d2feabc1cb6e24f6e10dfc3286f18c4a7bdf53cb778aa",
    effets=(
        Effet(1, "ignition", ("main", "cimetiere"), (("par_nom_effet", COCA),), cout=_coca_cout_tribut,
              possible=lambda p, l, n: True, resolution=_coca_ss,
              note="Main ou Cimetière. Coût : Sacrifier 1 monstre Bête, Bête-Guerrier ou Bête Ailée contrôlé ; "
                   "s'Invoquer Spécialement, banni quand il quitte le terrain."),
        Effet(2, "ignition", ("terrain",), (("par_nom_effet", COCA),), cout=_coca_cout_bannir,
              resolution=_coca_nom,
              note="Coût : bannir du Deck (face visible, R27b) 1 Bête, Bête-Guerrier ou Bête Ailée de Niveau 4 ou "
                   "moins ; cette carte prend son nom, son Type, son Attribut et son Niveau jusqu'à la Phase de "
                   "Fin (R27a)."),
    ),
    sources="T32, T33, T62 ; R10, R27",
)


# ── Dogmatika Ecclesia, the Virtuous ───────────────────────────────────────────────────────────

def _monstre_ss_depuis_extra_sur_terrain(p) -> bool:
    for j in (0, 1):
        for _, i in p.monstres(j):
            if i.face == "visible" and i.venue_extra_deck and i.arrivee != "autre":
                return True
    return False


def _dec_cibles(p):
    return sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and "Dogmatika" in f.archetypes
                   and i.carte != DECCLESIA})


def _dec_recherche(p, m):
    cibles = _dec_cibles(p)
    if cibles:
        o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée à la main") for n in cibles]))
        _ajouter_depuis(p, "deck", o.valeur)
    p.ajouter_verrou(Verrou(DECCLESIA, "extra_aucune"))


DECCLESIA_F = Formalisation(
    nom=DECCLESIA, text_sha256="b1df591121476c63afa17a8e7034bc769b184e5901df1964259d1d6bc88f2319",
    effets=(
        Effet(1, "restriction", ("terrain",), (), resolution=HORS_PERIMETRE,
              note="Indestructible au combat contre un monstre Invoqué Spécialement depuis l'Extra Deck : combat, "
                   "hors du pilote."),
        Effet(2, "ignition", ("main",), (("par_nom_effet", DECCLESIA),),
              condition=lambda p, l, n: None if _monstre_ss_depuis_extra_sur_terrain(p) else
              "aucun monstre Invoqué Spécialement depuis l'Extra Deck sur le terrain",
              possible=_ss_cible_ok, resolution=_ss_soi_main,
              note="Un monstre Invoqué Spécialement depuis l'Extra Deck est sur le terrain (l'un ou l'autre côté) : "
                   "s'Invoquer Spécialement depuis la main. Un monstre de l'Extra Deck revenu des bannies (retour "
                   "d'Ecclesia and the Dark Dragon) ne compte pas."),
        Effet(3, "declenche", ("terrain",), (("par_nom_effet", DECCLESIA),), timing="if", declencheur=_soi_invoque,
              possible=lambda p, l, n: bool(_dec_cibles(p)), resolution=_dec_recherche,
              categories=("recherche_deck",),
              note="Invoqué Normalement ou Spécialement : ajouter 1 carte « Dogmatika » du Deck (sauf lui) ; verrou "
                   "« aucune Invocation Spéciale depuis l'Extra Deck » pour le reste du tour. ⚖ Activation refusée "
                   "sans carte « Dogmatika » à ajouter (R01 appliqué malgré la partie « also »)."),
    ),
    sources="T50 ; R04, R11",
)


# ── Droll & Lock Bird ──────────────────────────────────────────────────────────────────────────

DROLL_F = Formalisation(
    nom=DROLL, text_sha256="2e329ca3d34c612fbd0c0cb1f1cb15313b90cb9274679fb93d248eb2c68b379f",
    effets=(
        Effet(1, "rapide", ("main",), (), vitesse=2,
              condition=lambda p, l, n: "aucune carte ajoutée du Deck à la main de l'adversaire (pilote : adversaire passif)",
              resolution=HORS_PERIMETRE,
              note="Répond à un ajout du Deck à la main de l'adversaire : n'arrive jamais dans le pilote."),
    ),
    sources="—",
)


# ── Fallen of the White Dragon ─────────────────────────────────────────────────────────────────

def _white_cout(p, lieu, nom):
    noms = sorted({i.carte for i in p.j.extra if (f := p.cat.get(i.carte)) and f.est_monstre and ALBAZ in f.mentions})

    def payer(n):
        return lambda partie: partie.envoyer_cimetiere("extra", n, None, "cout", "cout")
    return [Option(n, p.declaree(n), None if p.declaree(n) else "non formalisée : envoyée au Cimetière", payer(n))
            for n in noms]


def _white_ss(p, m):
    if any(i.carte == WHITE for i in p.j.main):
        p.invoquer_dans_case_libre("main", WHITE)
    p.ajouter_verrou(Verrou(WHITE, "extra_fusion_synchro_n8"))


def _white_ecclesia(p):
    return _candidats(p, ("main", "deck", "cimetiere"),
                      lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre and "Ecclesia" in f.archetypes)


def _white_ecclesia_ss(p, m):
    if not p.cases_monstre_libres():
        p.notes.append("plus de zone libre")
        return
    r = _choisir_carte(p, "carte", _white_ecclesia(p), "Invoquée Spécialement")
    if r:
        _ss_depuis(p, *r)


WHITE_F = Formalisation(
    nom=WHITE, text_sha256="dc106b2585e84ee61223bf170f5bfb9e3c8020bef6de9c6abbb7793207f581fe",
    effets=(
        Effet(1, "ignition", ("main",), (("par_nom_effet", WHITE),), cout=_white_cout, possible=_ss_cible_ok,
              resolution=_white_ss,
              note="Coût : envoyer de l'Extra Deck au Cimetière 1 monstre qui mentionne « Fallen of Albaz » (R04 : "
                   "Synchro compris) ; s'Invoquer Spécialement, verrou « Extra Deck = Fusion ou Synchro de Niveau 8 » "
                   "pour le reste du tour."),
        Effet(2, "declenche", ("terrain",), (("par_nom_effet", WHITE),), timing="if", declencheur=_soi_invoque,
              possible=lambda p, l, n: bool(p.cases_monstre_libres()) and any(ok for _, _, ok in _white_ecclesia(p)),
              resolution=_white_ecclesia_ss, categories=("invocation_deck",),
              note="Invoqué Normalement ou Spécialement : Invoquer Spécialement 1 monstre « Ecclesia » de la main, du "
                   "Deck ou du Cimetière (R11 : le nom contient « Ecclesia »)."),
    ),
    sources="T29, T30, T31, T36 ; R04, R11, R26",
)


# ── Ghost Ogre & Snow Rabbit ───────────────────────────────────────────────────────────────────

def _ogre_condition(p, lieu, nom):
    if not p.chaine:
        return "aucun effet en cours d'activation"
    d = p.chaine[-1]
    if not (d.est_effet_de_monstre and d.lieu[0] == "terrain"):
        return "le dernier maillon n'est pas l'effet d'un monstre sur le terrain ni d'une Magie/Piège déjà face visible"
    return None


def _ogre_resolution(p, m):
    zone, cellule = m.donnees["cible_lieu"]
    nom = m.donnees["cible_carte"]
    inst = p.instance_en((zone, cellule), nom)
    if inst is None:
        p.notes.append(f"Ghost Ogre : {nom} n'est plus sur le terrain")
        return
    if p.insensible(inst, OGRE):
        p.notes.append(f"Ghost Ogre : {nom} n'est pas affecté")
        return
    p.detruire(nom, cellule, "cible", OGRE)


OGRE_F = Formalisation(
    nom=OGRE, text_sha256="0c4129524b3ba5c27a951dfc2b052c0a8853aeecc8e83250e58ce1974e5200b8",
    effets=(
        Effet(1, "rapide", ("main", "terrain"), (("par_nom_effet", OGRE),), vitesse=2, cout=_cout_soi("envoyer"),
              condition=_ogre_condition,
              a_l_activation=lambda p, l, n: {"cible_lieu": p.chaine[-1].lieu, "cible_carte": p.chaine[-1].carte},
              resolution=_ogre_resolution,
              note="En réponse à l'effet d'un monstre sur le terrain (ou d'une Magie/Piège déjà face visible : aucune "
                   "dans le deck) : s'envoyer au Cimetière ; détruire cette carte. Contre ses propres cartes aussi."),
    ),
    sources="—",
)


# ── Gold Sarcophagus ───────────────────────────────────────────────────────────────────────────

def _sarc_resolution(p, m):
    noms = sorted({i.carte for i in p._multi("deck")})
    if not noms:
        return
    o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "bannie") for n in noms]))
    p.pas.append(Pas("resoudre", f"{o.valeur} bannie face visible du Deck"))
    p.bannir("deck", o.valeur, None, "choisie", "effet")
    p.melanger()
    c = p.etat.cadre
    tour = c.tour + 4 if c.joueur_actif == 0 else c.tour + 3   # 2e Standby Phase du joueur après l'activation
    me = p.etat.memoire
    from dataclasses import replace
    p.etat = replace(p.etat, memoire=replace(me, effets_differes=me.effets_differes + (
        EffetDiffere(SARC, f"standby_tour_{tour}", f"ajouter {o.valeur} (bannie) à la main"),)))


SARC_F = Formalisation(
    nom=SARC, text_sha256="593d0d9ac77452f580709bf1f966169c20aa63df3d97622f15247e927fd9e620",
    effets=(
        Effet(1, "activation_carte", ("main",), (), possible=lambda p, l, n: bool(p._multi("deck")),
              resolution=_sarc_resolution,
              note="Bannir 1 carte du Deck face visible ; elle rejoint la main à la 2e Standby Phase du joueur après "
                   "l'activation (tour 5 si activée au tour 1, R29) : effet différé enregistré dans l'état."),
    ),
    sources="T63 ; R10, R29",
)


# ── Guiding Quem, the Virtuous ─────────────────────────────────────────────────────────────────

def _quem_envois(p):
    return sorted({i.carte for i in p._multi("deck") if _porte_albaz(p, i.carte) or _mentionne_albaz(p, i.carte)})


def _quem_envoi(p, m):
    cibles = _quem_envois(p)
    if not cibles:
        return
    o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "envoyée au Cimetière") for n in cibles]))
    p.pas.append(Pas("resoudre", f"{o.valeur} : Deck → Cimetière"))
    p.envoyer_cimetiere("deck", o.valeur, None, "choisie", "effet")
    p.melanger()


def _quem_cibles(p, lieu, nom):
    out, vus = [], set()
    for i in p.j.cimetiere:
        f = p.cat.get(i.carte)
        if f is None or not f.est_monstre or i.carte == QUEM or i.carte in vus:
            continue
        if not (ALBAZ in f.noms or ALBAZ in f.mentions):
            continue
        ok = _peut_revenir(p, i)
        if ok is False:
            continue
        vus.add(i.carte)
        if ok is None:
            out.append(Option(i.carte, False, "« correctement invoqué » non précisé (R09)", i.carte))
        else:
            out.append(Option(i.carte, p.declaree(i.carte), None if p.declaree(i.carte) else "non formalisée", i.carte))
    return out if p.cases_monstre_libres() else []


def _quem_ss(p, m):
    nom = m.donnees["cible"]
    inst = next((i for i in p.j.cimetiere if i.carte == nom and _peut_revenir(p, i)), None)
    if inst is None:
        p.notes.append(f"Guiding Quem : la cible {nom} n'est plus au Cimetière")
        return
    p.invoquer_dans_case_libre("cimetiere", nom)


QUEM_F = Formalisation(
    nom=QUEM, text_sha256="de946cc6964955b12cb6b404637fea4080c6f9d7777b48c096f3d041b6450936",
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_nom_effet", QUEM),), timing="if", declencheur=_soi_invoque,
              possible=lambda p, l, n: bool(_quem_envois(p)), resolution=_quem_envoi,
              categories=("envoi_deck_cimetiere",),
              note="Invoqué Normalement ou Spécialement : envoyer du Deck au Cimetière « Fallen of Albaz » ou 1 carte "
                   "qui le mentionne (R04 : Magies comprises)."),
        Effet(2, "declenche", ("terrain",), (("par_nom_effet", QUEM),), timing="if", declencheur=_quitte_extra,
              cible=_quem_cibles, resolution=_quem_ss,
              note="Une carte quitte l'Extra Deck : cibler au Cimetière « Fallen of Albaz » ou 1 monstre qui le "
                   "mentionne (sauf Quem) ; l'Invoquer Spécialement. Un monstre de l'Extra Deck jamais correctement "
                   "invoqué n'est pas une cible (R09)."),
    ),
    sources="T22, T23, T24 ; R01, R04, R09, R10, R13",
)


# ── Incredible Ecclesia, the Virtuous ──────────────────────────────────────────────────────────

def _iec_condition_procedure(p, lieu, nom):
    a, b = len(p.monstres(1)), len(p.monstres(0))
    return None if a > b else f"l'adversaire contrôle {a} monstre(s), vous {b} : il n'en contrôle pas plus (R16)"


def _iec_cibles(p):
    return _candidats(p, ("main", "deck"), lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre and (
        "Swordsoul" in f.archetypes or ALBAZ in f.noms))


def _iec_ss(p, m):
    r = _choisir_carte(p, "carte", _iec_cibles(p), "Invoquée Spécialement")
    if r:
        _ss_depuis(p, *r)


IECCLESIA_F = Formalisation(
    nom=IECCLESIA, text_sha256="3d916eeb5266cfc0ae897466da7e7a9af836ce6852d757ff18ee3d62aa22be0d",
    effets=(
        Effet(1, "procedure", ("main",), (("invocation_par_nom", IECCLESIA),), condition=_iec_condition_procedure,
              resolution=_continu,
              note="Invocation Spéciale par procédure depuis la main, sans chaîne (R15), si l'adversaire contrôle plus "
                   "de monstres (R16) ; une fois par tour de cette façon."),
        Effet(2, "rapide", ("terrain",), (("par_nom_effet", IECCLESIA),), vitesse=2, phases=PRINCIPALES,
              cout=_cout_soi("sacrifier"), possible=lambda p, l, n: any(ok for _, _, ok in _iec_cibles(p)),
              resolution=_iec_ss, categories=("invocation_deck",),
              note="Phase Principale, effet rapide. Coût : se Sacrifier ; Invoquer Spécialement 1 monstre « Swordsoul » "
                   "ou « Fallen of Albaz » de la main ou du Deck."),
        Effet(3, "fin", ("cimetiere",), (("par_nom_effet", IECCLESIA),), facultatif=False,
              condition=_cond_fusion_envoyee, resolution=_soi_vers_main,
              note="Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main. **Obligatoire** "
                   "(texte TCG sans « You can », R23) ; l'oracle (texte OCG) le traite en facultatif."),
    ),
    sources="T27, T28, T37 ; R03, R11, R15, R16, R23",
)


# ── Mulcharmy Fuwalos ──────────────────────────────────────────────────────────────────────────

def _fuwalos_condition(p, lieu, nom):
    if not p.controle_rien():
        return "vous contrôlez au moins une carte"
    if "mulcharmy_2" in p.etat.memoire.evenements:
        return "deux effets de monstre « Mulcharmy » déjà activés ce tour (« only 1 other »)"
    return None


def _fuwalos_compter(p, lieu, nom):
    p._evenement_memoire("mulcharmy_2" if "mulcharmy_1" in p.etat.memoire.evenements else "mulcharmy_1")


def _fuwalos_resolution(p, m):
    from dataclasses import replace
    me = p.etat.memoire
    p.etat = replace(p.etat, memoire=replace(me, effets_appliques=me.effets_appliques | {FUWALOS}))
    p.notes.append("Mulcharmy Fuwalos : effets appliqués ce tour (pioche sur Invocation adverse : hors pilote ; "
                   "retour aléatoire en Phase de Fin si la main dépasse 6 : non couvert)")


FUWALOS_F = Formalisation(
    nom=FUWALOS, text_sha256="764298a4c79118aaebe2b955381fa108baf01379b4c48228badccf332cac3e11",
    effets=(
        Effet(1, "rapide", ("main",), (), vitesse=2, cout=_cout_soi("defausser"), condition=_fuwalos_condition,
              a_l_activation=_fuwalos_compter, resolution=_fuwalos_resolution,
              note="Effet rapide, si l'on ne contrôle aucune carte (à son propre tour aussi, R30). Coût : se défausser ; "
                   "effets appliqués pour le tour. « Only 1 other Mulcharmy » : au plus deux effets « Mulcharmy » "
                   "par tour."),
    ),
    sources="T69 ; R30",
)


# ── Nadir Servant ──────────────────────────────────────────────────────────────────────────────

def _nadir_cibles(p, atk_max):
    return _candidats(p, ("deck", "cimetiere"), lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre
                      and ("Dogmatika" in f.archetypes or ALBAZ in f.noms) and (f.atk or 0) <= atk_max,
                      zone_extra_verif=False)


def _nadir_possible(p, lieu, nom):
    atks = [p.cat[i.carte].atk or 0 for i in p.j.extra if p.cat.get(i.carte)]
    return bool(atks) and bool(_nadir_cibles(p, max(atks)))


def _nadir_resolution(p, m):
    extra = sorted({i.carte for i in p.j.extra if (f := p.cat.get(i.carte)) and f.est_monstre})
    if extra:
        o = p.choisir(Decision("choisir", "envoi", [_option_carte(p, n, "envoyée au Cimetière") for n in extra]))
        p.pas.append(Pas("resoudre", f"{o.valeur} : Extra Deck → Cimetière"))
        p.envoyer_cimetiere("extra", o.valeur, None, "effet", "effet")
        atk = p.cat[o.valeur].atk or 0
        r = _choisir_carte(p, "carte", _nadir_cibles(p, atk), "ajoutée à la main")
        if r:
            _ajouter_depuis(p, *r)
    p.ajouter_verrou(Verrou(NADIR, "extra_aucune"))


NADIR_F = Formalisation(
    nom=NADIR, text_sha256="cd4dfbcd1a511cb5dca6519b6c495ee2135a29791b38f7a53bc51601e168e05a",
    effets=(
        Effet(1, "activation_carte", ("main",), (("activation_par_nom", NADIR),), possible=_nadir_possible,
              resolution=_nadir_resolution, categories=("recherche_deck",),
              note="Envoyer 1 monstre de l'Extra Deck au Cimetière, puis ajouter du Deck ou du Cimetière 1 monstre "
                   "« Dogmatika » ou « Fallen of Albaz » d'ATK inférieure ou égale à l'ATK imprimée du monstre envoyé "
                   "(R12) ; verrou « aucune Invocation Spéciale depuis l'Extra Deck » après résolution (R13)."),
    ),
    sources="T17 à T22, T60 ; R03, R08, R11, R12, R13",
)


# ── Springans Kitt ─────────────────────────────────────────────────────────────────────────────

def _skitt_condition(p, lieu, nom):
    for _, i in p.monstres():
        f = p.cat.get(i.carte)
        if i.face == "visible" and f and f.est_fusion and f.mentionne_comme_materiel(ALBAZ):
            return None
    for i in p.j.cimetiere:
        f = p.cat.get(i.carte)
        if f and f.est_fusion and f.mentionne_comme_materiel(ALBAZ):
            return None
    return "aucun monstre Fusion qui mentionne « Fallen of Albaz » comme matériel, ni sur le terrain ni au Cimetière (R05)"


def _skitt_branded(p):
    return _candidats(p, ("bannies", "deck", "cimetiere"), lambda i: (f := p.cat.get(i.carte)) is not None and (
        f.est_magie or f.est_piege) and "Branded" in f.archetypes)


def _skitt_recherche(p, m):
    r = _choisir_carte(p, "carte", _skitt_branded(p), "ajoutée à la main")
    if not r:
        return
    _ajouter_depuis(p, *r)
    main = sorted({i.carte for i in p.j.main})
    o = p.choisir(Decision("choisir", "dessous", [_option_carte(p, n, "placée au-dessous du Deck") for n in main]))
    p.pas.append(Pas("resoudre", f"{o.valeur} placée au-dessous du Deck"))
    p.vers_deck("main", o.valeur, None, "choisie", "dessous")


SKITT_F = Formalisation(
    nom=SKITT, text_sha256="4cc5bbae2c4dc9c1fa0f8a4482047734908a1e776cd39a221d4535d155c0f856",
    effets=(
        Effet(1, "ignition", ("main",), (("par_nom_effet", SKITT),), condition=_skitt_condition, possible=_ss_cible_ok,
              resolution=_ss_soi_main,
              note="Un monstre Fusion qui mentionne Albaz comme matériel sur le terrain ou au Cimetière (présence "
                   "seulement, R32) : s'Invoquer Spécialement depuis la main."),
        Effet(2, "declenche", ("terrain",), (("par_nom_effet", SKITT),), timing="if", declencheur=_soi_invoque,
              possible=lambda p, l, n: any(ok for _, _, ok in _skitt_branded(p)), resolution=_skitt_recherche,
              categories=("recherche_deck",),
              note="Invoquée Normalement ou Spécialement : ajouter 1 Magie/Piège « Branded » bannie, du Deck ou du "
                   "Cimetière, puis placer 1 carte de la main au-dessous du Deck (après le mélange, R02)."),
    ),
    sources="T14, T47, T48, T49 ; R02, R05, R32",
)


# ── Super Polymerization ───────────────────────────────────────────────────────────────────────

def _spoly_cout(p, lieu, nom):
    main = [i.carte for i in p.j.main]
    if lieu[0] == "main" and nom in main:
        main.remove(nom)

    def payer(n):
        return lambda partie: partie.defausser(n)
    return [Option(f"défausser {n}", p.declaree(n), None if p.declaree(n) else "non formalisée : défaussée", payer(n))
            for n in sorted(set(main))]


def _spoly_candidats(p):
    return [f for n in sorted({i.carte for i in p.j.extra}) if (f := p.cat.get(n)) and f.est_fusion]


def _spoly_possible(p, lieu, nom):
    possibles, indet, _ = p.analyser_fusions(_spoly_candidats(p), _materiaux(p, ("terrain",)), None)
    if any(o.couverte for o in possibles):
        return True
    return None if (possibles or indet) else False


SPOLY_F = Formalisation(
    nom=SPOLY, text_sha256="4a04f201798a8dd85953c1f25d469cd47d8402963aea66bf8a99ea6f7cd179d4",
    effets=(
        Effet(1, "activation_carte", ("main", "terrain"), (), vitesse=2, cout=_spoly_cout, possible=_spoly_possible,
              resolution=lambda p, m: p.fusionner(_spoly_candidats(p), _materiaux(p, ("terrain",)), None),
              sans_reponse=True,
              note="Magie Jeu-Rapide. Coût : défausser 1 carte (R17) ; Invocation Fusion avec des monstres des deux "
                   "terrains (pas la main). Personne ne peut répondre à l'activation (R19)."),
    ),
    sources="T38 à T42, T56 à T58 ; R17, R18, R19, R24, R25",
)


# ── The Fallen & The Virtuous ──────────────────────────────────────────────────────────────────

def _tftv_cout(p, lieu, nom):
    return _white_cout(p, lieu, nom)


def _tftv_cibles_1(p, lieu, nom):
    soi = (lieu[1], nom) if lieu[0] == "terrain" else None
    out = []
    for c, i in _cartes_visibles_terrain(p, sauf=soi):
        if lieu[0] == "main" and i.carte == nom and c.startswith("S"):
            continue
        out.append(Option(f"{i.carte} ({c})", True, None, (c, i.carte)))
    return out


def _tftv_detruire(p, m):
    c, n = m.donnees["cible"]
    inst = p.instance_en(("terrain", c), n)
    if inst is None:
        p.notes.append(f"The Fallen & The Virtuous : la cible {n} n'est plus sur le terrain")
        return
    if p.insensible(inst, TFTV):
        return
    p.detruire(n, c, "cible", TFTV)


def _tftv_condition_2(p, lieu, nom):
    if any("Ecclesia" in p.archetypes_de(i) for _, i in p.monstres() if i.face == "visible"):
        return None
    if any((f := p.cat.get(i.carte)) and f.est_monstre and "Ecclesia" in f.archetypes for i in p.j.cimetiere):
        return None
    return "aucun monstre « Ecclesia » sur le terrain ni au Cimetière"


def _tftv_cibles_2(p, lieu, nom):
    if not p.cases_monstre_libres():
        return []
    out, vus = [], set()
    for i in p.j.cimetiere:
        f = p.cat.get(i.carte)
        if f is None or not f.est_monstre or i.carte in vus:
            continue
        ok = _peut_revenir(p, i)
        if ok is False:
            continue
        vus.add(i.carte)
        out.append(Option(i.carte, ok is True and p.declaree(i.carte),
                          None if ok is True else "« correctement invoqué » non précisé (R09)", i.carte))
    return out


def _tftv_ss(p, m):
    n = m.donnees["cible"]
    if not any(i.carte == n and _peut_revenir(p, i) for i in p.j.cimetiere):
        p.notes.append(f"The Fallen & The Virtuous : {n} n'est plus au Cimetière")
        return
    p.invoquer_dans_case_libre("cimetiere", n)


TFTV_F = Formalisation(
    nom=TFTV, text_sha256="672abc2df26edd16e1c9f8ddc67d2f874a33713ee04107a5fc735934420e5b91",
    effets=(
        Effet(1, "activation_carte", ("main", "terrain"), (("activation_par_nom", TFTV),), vitesse=2,
              cout=_tftv_cout, cible=_tftv_cibles_1, resolution=_tftv_detruire,
              note="Magie Jeu-Rapide, 1er effet choisi à l'activation. Envoi de l'Extra Deck d'un monstre qui mentionne "
                   "Albaz (traité en coût, comme l'oracle, R34) puis cible : 1 carte face visible du terrain, pas "
                   "elle-même (R34 a, b) ; la détruire."),
        Effet(2, "activation_carte", ("main", "terrain"), (("activation_par_nom", TFTV),), vitesse=2,
              condition=_tftv_condition_2, cible=_tftv_cibles_2, resolution=_tftv_ss,
              note="2e effet : un monstre « Ecclesia » sur le terrain ou au Cimetière ; cibler 1 monstre dans un "
                   "Cimetière ; l'Invoquer Spécialement sur son terrain (R09 pour un monstre de l'Extra Deck)."),
    ),
    sources="T65 ; R04, R09, R34",
)


# ── The Golden Swordsoul ───────────────────────────────────────────────────────────────────────

def _gsword_declencheur(p, ev, lieu, nom) -> bool:
    if ev.type != "bannie" or ev.a("face") != "visible":
        return False
    f = p.cat.get(ev.carte)
    return f is not None and f.est_monstre and ev.carte != nom


def _gsword_cibles(p):
    return _candidats(p, ("main", "cimetiere"), lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre
                      and f.attribut == "LIGHT" and f.race == "Spellcaster" and f.atk is not None and f.atk == f.defense
                      and i.carte != GSWORD)


def _gsword_ss(p, m):
    r = _choisir_carte(p, "carte", _gsword_cibles(p), "Invoquée Spécialement")
    if r:
        _ss_depuis(p, *r)


GSWORD_F = Formalisation(
    nom=GSWORD, text_sha256="6fb9788b8ca1985589ba56ca80047fc44baad3318fe8a7d652d5e25e722eeb69",
    effets=(
        Effet(1, "declenche", ("main",), (), timing="when", declencheur=_jamais, resolution=HORS_PERIMETRE,
              note="Déclaration d'attaque : pas de Phase de Combat au tour 1 (R31), hors du pilote."),
        Effet(2, "declenche", ("terrain", "cimetiere"), (("par_nom_effet", GSWORD),), timing="if",
              declencheur=_gsword_declencheur, cout=_cout_soi("bannir"),
              possible=lambda p, l, n: bool(p.cases_monstre_libres()) and any(ok for _, _, ok in _gsword_cibles(p)),
              resolution=_gsword_ss,
              note="Un monstre est banni face visible (bannir en coût compte, R27b) : se bannir du terrain ou du "
                   "Cimetière ; Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du Cimetière dont "
                   "l'ATK égale la DEF. ⚖ Son propre bannissement ne la déclenche pas (elle ne serait plus là)."),
    ),
    sources="T62 ; R10, R22, R27b",
)


# ── Tri-Brigade Mercourier ─────────────────────────────────────────────────────────────────────

def _merc_cibles(p):
    return sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and f.est_monstre and i.carte != MERC
                   and (ALBAZ in f.noms or ALBAZ in f.mentions)})


def _merc_recherche(p, m):
    cibles = _merc_cibles(p)
    if cibles:
        o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée à la main") for n in cibles]))
        _ajouter_depuis(p, "deck", o.valeur)


MERC_F = Formalisation(
    nom=MERC, text_sha256="ee4e21aaa2da5230a541958e1beeb02700e3b7e8a86f63d343bb0a27d0ce4ff7",
    effets=(
        Effet(1, "rapide", ("main", "terrain"), (("par_nom_effet", MERC),), vitesse=2,
              condition=lambda p, l, n: "l'adversaire n'active aucun effet de monstre (pilote)",
              resolution=HORS_PERIMETRE, note="Répond à un effet de monstre adverse : hors du pilote."),
        Effet(2, "declenche", ("bannies",), (("par_nom_effet", MERC),), timing="if", declencheur=_soi_banni,
              possible=lambda p, l, n: bool(_merc_cibles(p)), resolution=_merc_recherche,
              categories=("recherche_deck",),
              note="Bannie (en coût aussi, R27b) : ajouter du Deck « Fallen of Albaz » ou 1 **monstre** qui le "
                   "mentionne, sauf lui."),
    ),
    sources="T33, T61, T62, T63 ; R04, R10, R27b",
)


# ── Albion the Sanctifire Dragon ───────────────────────────────────────────────────────────────

SANCTIFIRE_F = Formalisation(
    nom=SANCTIFIRE, text_sha256="648cb00418ab17861d7f7c898f4d96302a2a83f2cfa42663f4519d762ee3ed9b",
    materiels=(None, lambda fiche, inst, p: fiche.est_monstre and p.attribut_de(inst) == "LIGHT"
               and p.race_de(inst) == "Spellcaster"),
    interdit_materiel_fusion=True,
    effets=(
        Effet(1, "restriction", ("terrain",), (), resolution=_continu,
              note="Ne sert pas de matériel de Fusion (codé : `interdit_materiel_fusion`, R24). L'adversaire ne peut "
                   "pas la cibler : hors pilote."),
        Effet(2, "rapide", ("terrain",), (("par_nom_effet", SANCTIFIRE),), vitesse=2,
              condition=lambda p, l, n: None if p.etat.cadre.joueur_actif == 1 else "pendant le tour adverse seulement",
              resolution=HORS_PERIMETRE, note="Tour adverse seulement."),
        Effet(3, "ignition", ("cimetiere",), (("par_nom_effet", SANCTIFIRE),),
              condition=lambda p, l, n: "il faut Sacrifier les 4 monstres des 2 Zones Monstre Extra et des 2 zones "
                                        "centrales (dont celle de l'adversaire, vide dans le pilote)",
              resolution=HORS_PERIMETRE,
              note="⚖ Lecture : les 2 zones centrales = la zone M3 de chaque joueur ; demande des monstres adverses."),
    ),
    sources="T07, T56 ; R05, R24",
)


# ── Despian Luluwalilith ───────────────────────────────────────────────────────────────────────

def _lulu_declencheur(p, ev, lieu, nom) -> bool:
    if ev.type != "quitte_extra" or lieu[0] != "terrain":
        return False
    if ev.carte == nom:
        raise NonCouvert("⚖ Luluwalilith se déclenche-t-elle sur sa propre sortie de l'Extra Deck ? Non tranché "
                         "(situation pour l'oracle)")
    return True


def _lulu_resolution(p, m):
    for c, i in list(p.monstres()):
        if i.face == "visible" and not p.insensible(i, LULU):
            p.modifier(("terrain", c), i.carte, (Modification("atk_gain", "500", "permanente"),))
    cibles = [(c, i) for c, i in _cartes_visibles_terrain(p) if not p.insensible(i, LULU)]
    options = [Option(f"{i.carte} ({c})", True, None, (c, i.carte)) for c, i in cibles] + [Option("ne pas annuler")]
    o = p.choisir(Decision("choisir", "annuler", options))
    if o.valeur != "ne pas annuler":
        c, n = o.donnees
        p.modifier(("terrain", c), n, (Modification("effets_annules", "oui", "fin_de_tour"),))


def _lulu_cibles_fin(p):
    return _candidats(p, ("main", "deck"), lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre
                      and f.attribut == "LIGHT" and f.race == "Spellcaster" and f.atk is not None and f.atk == f.defense)


def _lulu_fin(p, m):
    r = _choisir_carte(p, "carte", _lulu_cibles_fin(p), "Invoquée Spécialement")
    if r:
        _ss_depuis(p, *r)


LULU_F = Formalisation(
    nom=LULU, text_sha256="5b1074022a6daa4565ab77b2d1a6e69f4667708579ed942cc1fbbf6ced92e38e",
    synchro_niveau_syntoniseur=4,
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_exemplaire", None),), timing="if", declencheur=_lulu_declencheur,
              resolution=_lulu_resolution,
              note="Une carte quitte l'Extra Deck : les monstres contrôlés gagnent 500 ATK (permanent), puis on peut "
                   "annuler les effets d'1 carte face visible jusqu'à la fin du tour. ⚖ Sa propre sortie de l'Extra "
                   "Deck : non couvert."),
        Effet(2, "fin", ("cimetiere",), (("par_nom_effet", LULU),), condition=_cond_envoyee_ce_tour,
              possible=lambda p, l, n: bool(p.cases_monstre_libres()) and any(ok for _, _, ok in _lulu_cibles_fin(p)),
              resolution=_lulu_fin, categories=("invocation_deck",),
              note="Phase de Fin, envoyée au Cimetière ce tour : Invoquer Spécialement 1 monstre LUMIÈRE Magicien de "
                   "la main ou du Deck dont l'ATK égale la DEF."),
    ),
    sources="T31 ; R14, R26",
)


# ── Ecclesia and the Dark Dragon ───────────────────────────────────────────────────────────────

def _edd_cibles(p):
    return _candidats(p, ("deck", "cimetiere"), lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre and (
        ALBAZ in f.noms or ((f.niveau or 99) <= 4 and ALBAZ in f.mentions)))


def _edd_possible(p, lieu, nom):
    inst = p.instance_en(lieu, nom)
    libre = bool(p.cases_monstre_libres()) or lieu[1] in ("M1", "M2", "M3", "M4", "M5")
    return libre and any(ok for _, _, ok in _edd_cibles(p)) and not p.insensible(inst, EDD)


def _edd_resolution(p, m):
    inst = p.instance_en(m.lieu, EDD)
    if inst is None:
        p.notes.append("Ecclesia and the Dark Dragon n'est plus sur le terrain : rien")
        return
    p.pas.append(Pas("resoudre", "Ecclesia and the Dark Dragon bannie jusqu'à la Phase de Fin"))
    p.bannir("terrain", EDD, m.lieu[1], "acteur", "effet")
    from dataclasses import replace
    me = p.etat.memoire
    p.etat = replace(p.etat, memoire=replace(me, effets_differes=me.effets_differes + (
        EffetDiffere(EDD, "phase_de_fin_retour", f"position={inst.position}"),)))
    r = _choisir_carte(p, "carte", _edd_cibles(p), "Invoquée Spécialement")
    if r:
        _ss_depuis(p, *r)


def _edd_cibles_gy(p, lieu, nom):
    fusions = [(z, i.carte) for z in ("cimetiere", "bannies") for i in getattr(p.j, z)
               if (f := p.cat.get(i.carte)) and f.est_fusion and f.niveau == 8]
    terrain = [(c, i.carte) for c, i in p.monstres() + list(p.j.cases)]
    out = []
    for z, fu in sorted(set(fusions)):
        for c, t in terrain:
            out.append(Option(f"{fu} ({z}) + {t} ({c})", True, None, ((z, fu), (c, t))))
    return out


def _edd_melanger(p, m):
    (z, fu), (c, t) = m.donnees["cible"]
    if any(i.carte == fu for i in getattr(p.j, z)):
        p.vers_deck(z, fu, None, "cible")
    if p.instance_en(("terrain", c), t) is not None and not p.insensible(p.instance_en(("terrain", c), t), EDD):
        p.vers_deck("terrain", t, c, "cible")
    if any(i.carte == EDD for i in p.j.cimetiere):
        p.vers_deck("cimetiere", EDD, None, "acteur")
    p.melanger()


EDD_F = Formalisation(
    nom=EDD, text_sha256="e8596c1585a776732b1884049dae0201fe0e10f33229f3c14a3d499df028a49b",
    effets=(
        Effet(1, "rapide", ("terrain",), (("par_nom_effet", EDD),), vitesse=2, phases=PRINCIPALES,
              possible=_edd_possible, resolution=_edd_resolution, categories=("invocation_deck",),
              note="Phase Principale, effet rapide : se bannir jusqu'à la Phase de Fin (effet, pas coût) et, si c'est "
                   "fait, Invoquer Spécialement « Fallen of Albaz » ou 1 monstre de Niveau 4 ou moins qui le mentionne, "
                   "du Deck ou du Cimetière. Retour en Phase de Fin, dans sa position, en zone principale (⚖)."),
        Effet(2, "ignition", ("cimetiere",), (("par_nom_effet", EDD),), cible=_edd_cibles_gy, resolution=_edd_melanger,
              note="Au Cimetière : cibler 1 monstre Fusion de Niveau 8 au Cimetière ou banni et 1 carte du terrain ; "
                   "les mélanger dans le Deck avec cette carte."),
    ),
    sources="T12, T13, T36, T64 ; R07, R26",
)


# ── Garura, Wings of Resonant Life ─────────────────────────────────────────────────────────────

def _garura_groupe(p, membres) -> bool | None:
    if len(membres) != 2:
        return False
    (fa, a), (fb, b) = membres
    if fa is None or fb is None or not fa.est_monstre or not fb.est_monstre:
        return False
    if p.race_de(a) != p.race_de(b) or p.attribut_de(a) != p.attribut_de(b):
        return False
    return not (p.noms_de(a) & p.noms_de(b))


GARURA_F = Formalisation(
    nom=GARURA, text_sha256="27591591ecd995601ceb0ce425ef5aded63c36074bb7506bc2fa8a14d5f2bed4",
    materiels_groupe=_garura_groupe,
    effets=(
        Effet(1, "restriction", ("terrain",), (), resolution=HORS_PERIMETRE,
              note="Dégâts de combat doublés : combat, hors pilote."),
        Effet(2, "declenche", ("cimetiere",), (("par_nom_effet", GARURA),), timing="if",
              declencheur=_soi_envoye_cimetiere, possible=lambda p, l, n: bool(p._multi("deck")),
              resolution=lambda p, m: p.piocher(),
              note="Envoyée au Cimetière (depuis l'Extra Deck aussi) : piocher 1 carte (branche de hasard)."),
    ),
    sources="T19, T39, T51 ; R10, R12, R20",
)


# ── Granguignol the Dusk Dragon ────────────────────────────────────────────────────────────────

def _grang_cibles(p):
    return sorted({i.carte for z in ("deck", "extra") for i in p._multi(z)
                   if (f := p.cat.get(i.carte)) and f.est_monstre and (f.niveau or 0) >= 6
                   and f.attribut in ("LIGHT", "DARK")})


def _grang_envoi(p, m):
    cibles = _grang_cibles(p)
    if not cibles:
        return
    o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "envoyée au Cimetière") for n in cibles]))
    zone = "deck" if any(i.carte == o.valeur for i in p._multi("deck")) else "extra"
    p.pas.append(Pas("resoudre", f"{o.valeur} : {zone} → Cimetière"))
    p.envoyer_cimetiere(zone, o.valeur, None, "choisie", "effet")
    if zone == "deck":
        p.melanger()


GRANG_F = Formalisation(
    nom=GRANG, text_sha256="f113efac8f0f62a0f76072f14f9f3e5c8f5f7576bbed1f29d49d677ebddf1d84",
    materiels=(None, lambda fiche, inst, p: fiche.est_monstre and p.attribut_de(inst) in ("LIGHT", "DARK")),
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_nom_effet", GRANG),), timing="if",
              declencheur=_soi_par("invocation_fusion"), possible=lambda p, l, n: bool(_grang_cibles(p)),
              resolution=_grang_envoi, categories=("envoi_deck_cimetiere",),
              note="Invoquée par Fusion : envoyer au Cimetière 1 monstre LUMIÈRE ou TÉNÈBRES de Niveau 6 ou plus, du "
                   "Deck ou de l'Extra Deck."),
        Effet(2, "declenche", ("terrain", "cimetiere"), (("par_nom_effet", GRANG),), timing="if", declencheur=_jamais,
              resolution=HORS_PERIMETRE,
              note="Un monstre est Invoqué Spécialement par un effet de monstre adverse : hors pilote."),
    ),
    sources="T08, T45, T48, T53 ; R05, R22",
)


# ── Hyperinvoked Aeon ──────────────────────────────────────────────────────────────────────────

def _aeon_groupe(p, membres) -> bool | None:
    if len(membres) < 2:
        return False
    attrs = []
    for f, i in membres:
        if f is None or not f.est_fusion:
            return False
        attrs.append(p.attribut_de(i))
    return len(set(attrs)) == len(attrs)


def _aeon_bannir(p, m):
    inst = next((i for _, i in p.monstres() if i.carte == AEON and i.arrivee == "invocation_fusion"), None)
    n = int(next((x.valeur for x in inst.modifications if x.champ == "materiaux"), "0")) if inst else 0
    for _ in range(n):
        options = [Option("terminer")]
        for c, i in p.monstres() + list(p.j.cases):
            if not p.insensible(i, AEON):
                options.append(Option(f"{i.carte} ({c})", p.declaree(i.carte), None, ("terrain", c, i.carte)))
        for i in sorted({i.carte for i in p.j.cimetiere}):
            options.append(Option(f"{i} (cimetiere)", p.declaree(i), None, ("cimetiere", None, i)))
        o = p.choisir(Decision("choisir", "bannir", options))
        if o.valeur == "terminer":
            break
        z, c, nom = o.donnees
        p.bannir(z, nom, c, "choisie", "effet")
    if n >= 3:
        o = p.choisir(Decision("choisir", "extra_adverse", [Option("ne pas regarder"), Option("regarder")]))
        if o.valeur == "regarder":
            raise HorsPerimetre("Hyperinvoked Aeon : regarder et bannir l'Extra Deck adverse")


def _aeon_attribut(p, m):
    options, indet = _options_attribut(p)
    o = p.choisir(Decision("choisir", "attribut", options, indet))
    for j in (0, 1):
        for c, i in list(p.monstres(j)):
            if i.carte == AEON and c == m.lieu[1]:
                continue
            if j == 0 and not p.insensible(i, AEON):
                p.modifier(("terrain", c), i.carte, (Modification("attribut", o.valeur, "fin_de_tour"),))


AEON_F = Formalisation(
    nom=AEON, text_sha256="2b2749f2389511ba319b15bfbd1812c803957f4b4e92e7cd94dada0ee7595549",
    materiels_groupe=_aeon_groupe,
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_nom_carte", AEON),), timing="if",
              declencheur=_soi_par("invocation_fusion"), resolution=_aeon_bannir,
              note="Invoquée par Fusion : bannir des cartes du terrain et/ou des Cimetières, jusqu'au nombre de "
                   "matériels ; avec 3 matériels ou plus, regarder l'Extra Deck adverse : hors pilote."),
        Effet(2, "rapide", ("terrain",), (("par_nom_carte", AEON),), vitesse=2, resolution=_aeon_attribut,
              note="Effet rapide : déclarer 1 Attribut ; les autres monstres du terrain le prennent jusqu'à la fin du "
                   "tour. ⚖ Déclarer DIVIN : non tranché."),
    ),
    sources="T66",
)


# ── Mirrorjade the Iceblade Dragon ─────────────────────────────────────────────────────────────

def _mirror_cout(p, lieu, nom):
    noms = sorted({i.carte for i in p.j.extra if (f := p.cat.get(i.carte)) and f.est_fusion
                   and f.mentionne_comme_materiel(ALBAZ)})

    def payer(n):
        return lambda partie: partie.envoyer_cimetiere("extra", n, None, "cout", "cout")
    return [Option(n, p.declaree(n), None if p.declaree(n) else "non formalisée", payer(n)) for n in noms]


def _mirror_condition(p, lieu, nom):
    inst = p.instance_en(lieu, nom)
    if inst is not None and "effet_1_interdit_ce_tour" in inst.restrictions:
        return "« this card cannot use this effect next turn »"
    return None


def _mirror_bannir(p, m):
    cibles = [(c, i) for j, c, i in _monstres_visibles(p, (0,)) if not p.insensible(i, MIRROR)]
    if cibles:
        o = p.choisir(Decision("choisir", "bannir", [Option(f"{i.carte} ({c})", True, None, (c, i.carte))
                                                     for c, i in cibles]))
        c, n = o.donnees
        p.pas.append(Pas("resoudre", f"{n} banni ({c})"))
        p.bannir("terrain", n, c, "choisie", "effet")
    inst = p.instance_en(m.lieu, MIRROR)
    if inst is not None:
        from dataclasses import replace
        i2 = p.retirer(m.lieu[0], MIRROR, m.lieu[1])
        p.ajouter(m.lieu[0], replace(i2, restrictions=i2.restrictions + ("effet_1_interdit_tour_suivant",)), m.lieu[1])


MIRROR_F = Formalisation(
    nom=MIRROR, text_sha256="34ab169f8b91a3779858898e6494a46e7524a92865b28995ae3d734142a2a504",
    materiels=(None, lambda fiche, inst: fiche.est_extra),
    un_seul_controle=True,
    effets=(
        Effet(1, "rapide", ("terrain",), (("par_exemplaire", None),), vitesse=2, cout=_mirror_cout,
              condition=_mirror_condition, resolution=_mirror_bannir,
              note="Une fois par tour, effet rapide. Coût : envoyer de l'Extra Deck 1 monstre Fusion qui mentionne "
                   "Albaz comme matériel ; bannir 1 monstre du terrain, au choix à la résolution, le sien compris "
                   "(R28) ; restriction « pas cet effet au tour suivant » portée par l'exemplaire."),
        Effet(2, "declenche", ("terrain",), (), timing="if", declencheur=_jamais, resolution=HORS_PERIMETRE,
              note="Quitte le terrain à cause d'une carte adverse : hors pilote."),
    ),
    sources="T10, T52, T56, T61 ; R10, R24, R28",
)


# ── Mixousia the Confounder ────────────────────────────────────────────────────────────────────

def _mix_groupe(p, membres) -> bool | None:
    if len(membres) != 2:
        return False
    races = [p.race_de(i) for f, i in membres if f is not None and f.est_monstre]
    if len(races) != 2:
        return False
    return sorted(r == "Spellcaster" for r in races) == [False, True]


def _mix_cibles(p, lieu, nom):
    return [Option(f"{i.carte} ({c})", True, None, (c, i.carte)) for _, c, i in _monstres_visibles(p, (0,))]


def _mix_attribut(p, m):
    c, n = m.donnees["cible"]
    options, indet = _options_attribut(p)
    o = p.choisir(Decision("choisir", "attribut", options, indet))
    inst = p.instance_en(("terrain", c), n)
    if inst is not None and inst.face == "visible" and not p.insensible(inst, MIXOUSIA):
        p.modifier(("terrain", c), n, (Modification("attribut", o.valeur, "tant_que_face_visible"),))


def _mix_gy(p, m):
    options, indet = _options_attribut(p)
    o = p.choisir(Decision("choisir", "attribut", options, indet))
    if any(i.carte == MIXOUSIA for i in p.j.cimetiere):
        p.modifier(("cimetiere", None), MIXOUSIA, (Modification("attribut", o.valeur, "fin_de_tour"),))


MIXOUSIA_F = Formalisation(
    nom=MIXOUSIA, text_sha256="0ccdbda0782284255544ce3c661758989ed81dcd8cac48b0b2a346ff63b55ad4",
    materiels_groupe=_mix_groupe,
    effets=(
        Effet(1, "ignition", ("terrain",), (("par_nom_effet", MIXOUSIA),), cible=_mix_cibles, resolution=_mix_attribut,
              note="Cibler 1 monstre face visible et déclarer 1 Attribut : il le prend (tant qu'il reste face visible)."),
        Effet(2, "rapide", ("terrain",), (("par_nom_effet", MIXOUSIA),), vitesse=2,
              condition=lambda p, l, n: None if p.etat.cadre.joueur_actif == 1 else "Phase Principale adverse seulement",
              resolution=HORS_PERIMETRE, note="Phase Principale adverse : hors pilote."),
        Effet(3, "ignition", ("cimetiere",), (("par_nom_effet", MIXOUSIA),), resolution=_mix_gy,
              note="Au Cimetière : déclarer 1 Attribut ; cette carte le prend au Cimetière jusqu'à la fin du tour."),
    ),
    sources="—",
)


# ── Predaplant Dragostapelia ───────────────────────────────────────────────────────────────────

DRAGO_F = Formalisation(
    nom=DRAGO, text_sha256="34357b40c922edde7da48d83da2f018eeaec0bdab9d14c92918711baf8f1bd84",
    materiels=(lambda fiche, inst: fiche.est_fusion, lambda fiche, inst, p: fiche.est_monstre and p.attribut_de(inst) == "DARK"),
    effets=(
        Effet(1, "rapide", ("terrain",), (("par_exemplaire", None),), vitesse=2,
              condition=lambda p, l, n: None if p.monstres(1) else "aucun monstre adverse face visible (pilote)",
              resolution=HORS_PERIMETRE, note="Cible un monstre adverse : hors pilote."),
        Effet(2, "restriction", ("terrain",), (), resolution=HORS_PERIMETRE,
              note="Annule les effets activés des monstres adverses à Compteur Prédateur : hors pilote."),
    ),
    sources="—",
)


# ── Sprind the Irondash Dragon ─────────────────────────────────────────────────────────────────

def _sprind_mat(fiche, inst, p) -> bool | None:
    if not fiche.est_monstre or "Normal" in fiche.type_carte:
        return False
    if p.lieu_de(inst) is None:
        return False   # main ou Deck : pas Invoqué ce tour
    if inst.arrivee is None:
        return None
    return inst.arrivee in MODES_SPECIALES and inst.arrivee_ce_tour


def _sprind_possible(p, lieu, nom):
    return bool([c for c in p.cases_monstre_libres() if c != lieu[1]])


COLONNE_ZME = {"ZME_G": 2, "ZME_D": 4}


def _sprind_resolution(p, m):
    inst = p.instance_en(m.lieu, SPRIND)
    libres = p.cases_monstre_libres()
    if inst is None or not libres:
        return
    o = p.choisir(Decision("choisir", "case", [Option(c) for c in libres]))
    p.pas.append(Pas("resoudre", f"Sprind passe de {m.lieu[1]} à {o.valeur}"))
    i = p.retirer("terrain", SPRIND, m.lieu[1])
    p.ajouter("terrain", i, o.valeur)
    col = int(o.valeur[1])
    autres = [(c, x) for c, x in p.monstres() + list(p.j.cases) if x.face == "visible" and c != o.valeur and (
        (c[0] in "MS" and c[1:].isdigit() and int(c[1]) == col) or COLONNE_ZME.get(c) == col)]
    if not autres:
        return
    od = p.choisir(Decision("choisir", "detruire_colonne", [Option("détruire"), Option("ne pas détruire")]))
    if od.valeur == "détruire":
        for c, x in autres:
            if not p.insensible(x, SPRIND):
                p.detruire(x.carte, c, "cible", SPRIND)


def _sprind_cibles(p):
    return sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and f.est_monstre
                   and ("Springans" in f.archetypes or ALBAZ in f.noms)})


def _sprind_fin(p, m):
    cibles = _sprind_cibles(p)
    if cibles:
        o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée ou Invoquée") for n in cibles]))
        _ajouter_ou_invoquer(p, "deck", o.valeur)


SPRIND_F = Formalisation(
    nom=SPRIND, text_sha256="3e61a9ef4b88ff80f28c14657a03745f5561072e67f2aa6003719cd2d299501e",
    materiels=(None, _sprind_mat),
    effets=(
        Effet(1, "ignition", ("terrain",), (("par_nom_effet", SPRIND),), phases=PRINCIPALES, possible=_sprind_possible,
              resolution=_sprind_resolution,
              note="Phase Principale du joueur : se déplacer vers une autre de ses zones Monstre principales, puis on "
                   "peut détruire les autres cartes face visible de sa colonne (D3 : colonnes énumérées). ⚖ Depuis "
                   "la Zone Monstre Extra : permis ici, non tranché."),
        Effet(2, "fin", ("cimetiere",), (("par_nom_effet", SPRIND),), condition=_cond_envoyee_ce_tour,
              possible=lambda p, l, n: bool(_sprind_cibles(p)), resolution=_sprind_fin,
              categories=("recherche_deck", "invocation_deck"),
              note="Phase de Fin, envoyé au Cimetière ce tour : ajouter ou Invoquer Spécialement 1 monstre « Springans » "
                   "ou « Fallen of Albaz » du Deck."),
    ),
    sources="T57, T58 ; R25",
)


# ── The Dragon that Devours the Dogma ──────────────────────────────────────────────────────────

def _ecclesia_presente(p) -> bool:
    if any("Ecclesia" in p.archetypes_de(i) for j in (0, 1) for _, i in p.monstres(j) if i.face == "visible"):
        return True
    return any((f := p.cat.get(i.carte)) and f.est_monstre and "Ecclesia" in f.archetypes
               for j in (0, 1) for i in p.etat.joueurs[j].cimetiere)


def _dogma_insensible(p, inst, source, active) -> bool:
    return source != DOGMA and p.lieu_de(inst) is not None and _ecclesia_presente(p)


def _dogma_melanger(p, m):
    for k in range(2):
        options = ([Option("terminer")] if k > 0 else [])
        for z in ("cimetiere", "bannies"):
            for n in sorted({i.carte for i in getattr(p.j, z)}):
                options.append(Option(f"{n} ({z})", p.declaree(n), None, (z, n)))
        if len(options) <= (1 if k > 0 else 0):
            break
        o = p.choisir(Decision("choisir", "melanger", options))
        if o.valeur == "terminer":
            break
        z, n = o.donnees
        p.vers_deck(z, n, None, "choisie")
    p.melanger()


def _dogma_cibles(p):
    return sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte))
                   and ({"Dogmatika", "Tri-Brigade"} & f.archetypes)})


def _dogma_fin(p, m):
    cibles = _dogma_cibles(p)
    if cibles:
        o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée à la main") for n in cibles]))
        _ajouter_depuis(p, "deck", o.valeur)


DOGMA_F = Formalisation(
    nom=DOGMA, text_sha256="1dbf9da33bc7e4f9eb0ff24c28a16845bc98c6c7ebeee45ad265b5e1e80f4bd1",
    materiels=(None, lambda fiche, inst, p: fiche.est_monstre and p.attribut_de(inst) in ("LIGHT", "DARK"),
               lambda fiche, inst: fiche.est_monstre and "Normal" not in fiche.type_carte),
    insensible=_dogma_insensible,
    bonus_atk=lambda p, inst: 500 if _ecclesia_presente(p) else 0,
    effets=(
        Effet(1, "restriction", ("terrain",), (), resolution=_continu,
              note="Un monstre « Ecclesia » sur le terrain ou dans un Cimetière : +500 ATK et insensible aux effets des "
                   "autres cartes (codé : `insensible`, `bonus_atk`)."),
        Effet(2, "declenche", ("terrain",), (("par_nom_effet", DOGMA),), timing="if", declencheur=_soi_invoque_special,
              possible=lambda p, l, n: bool(p.j.cimetiere or p.j.bannies), resolution=_dogma_melanger,
              note="Invoquée Spécialement : mélanger dans le Deck jusqu'à 2 cartes des Cimetières ou des bannies."),
        Effet(3, "fin", ("cimetiere",), (("par_nom_effet", DOGMA),), condition=_cond_envoyee_ce_tour,
              possible=lambda p, l, n: bool(_dogma_cibles(p)), resolution=_dogma_fin, categories=("recherche_deck",),
              note="Phase de Fin, envoyée au Cimetière ce tour : ajouter 1 carte « Dogmatika » ou « Tri-Brigade » du Deck."),
    ),
    sources="T09, T54, T55 ; R06, R24",
)


# ── The Three Champions of Swordsoul ───────────────────────────────────────────────────────────

NOM_CHAMPIONS_CITE = "The Three Brave Swordsouls"   # nom cité par la clause (anomalie de la source)


def _champ_cibles(p):
    return _candidats(p, ("deck", "cimetiere"), lambda i: (f := p.cat.get(i.carte)) is not None and f.est_monstre
                      and f.race == "Spellcaster" and f.niveau in (4, 8) and f.atk is not None and f.atk == f.defense)


def _champ_recherche(p, m):
    r = _choisir_carte(p, "carte", _champ_cibles(p), "ajoutée à la main")
    if r:
        _ajouter_depuis(p, *r)


def _champ_cibles_terrain(p, lieu, nom):
    return [Option(f"{i.carte} ({c})", True, None, (c, i.carte)) for c, i in _cartes_visibles_terrain(p)]


def _champ_annuler(p, m):
    c, n = m.donnees["cible"]
    inst = p.instance_en(("terrain", c), n)
    if inst is None or inst.face != "visible" or p.insensible(inst, CHAMPIONS):
        return
    p.modifier(("terrain", c), n, (Modification("effets_annules", "oui", "tant_que_face_visible"),))
    if any("Ecclesia" in (p.cat[i.carte].archetypes if p.cat.get(i.carte) else ()) and p.cat[i.carte].est_monstre
           or ALBAZ in p.noms_de(i) for i in p.j.cimetiere):
        o = p.choisir(Decision("choisir", "detruire", [Option("détruire"), Option("ne pas détruire")]))
        if o.valeur == "détruire":
            p.detruire(n, c, "cible", CHAMPIONS)


CHAMPIONS_F = Formalisation(
    nom=CHAMPIONS, text_sha256="ab942e56c87fc4224b1dc79209f106dfec7449c2232bc2cfd9e33fcafb97980e",
    synchro_niveau_syntoniseur=4,
    effets=(
        Effet(1, "declenche", ("terrain",), (("par_nom_effet", NOM_CHAMPIONS_CITE),), timing="if",
              declencheur=_soi_par("invocation_synchro"), possible=lambda p, l, n: any(ok for _, _, ok in _champ_cibles(p)),
              resolution=_champ_recherche, categories=("recherche_deck",),
              note="Invoquée par Synchro : ajouter du Deck ou du Cimetière 1 Magicien de Niveau 4 ou 8 dont l'ATK égale "
                   "la DEF. Limite sur le nom cité par la clause (« The Three Brave Swordsouls »)."),
        Effet(2, "ignition", ("terrain",), (("par_nom_effet", NOM_CHAMPIONS_CITE),), cible=_champ_cibles_terrain,
              resolution=_champ_annuler,
              note="Cibler 1 carte face visible ; annuler ses effets, puis, avec un monstre « Ecclesia » ou « Fallen of "
                   "Albaz » au Cimetière, on peut la détruire."),
    ),
    sources="T29 ; R04",
)


# ── Titaniklad the Ash Dragon ──────────────────────────────────────────────────────────────────

def _titan_mat(fiche, inst, p) -> bool | None:
    if not fiche.est_monstre:
        return False
    atk = p.atk_de(inst, sur_le_terrain=p.lieu_de(inst) is not None)
    return atk is not None and atk >= 2500


def _titan_insensible(p, inst, source, active) -> bool:
    if not active or source == TITAN or p.lieu_de(inst) is None:
        return False
    if not (inst.arrivee == "invocation_fusion" and inst.arrivee_ce_tour):
        return False
    f = p.cat.get(source)
    return f is not None and f.est_monstre and f.est_extra


def _titan_cibles(p):
    return sorted({i.carte for i in p._multi("deck") if (f := p.cat.get(i.carte)) and f.est_monstre
                   and (ALBAZ in f.noms or "Dogmatika" in f.archetypes)})


def _titan_fin(p, m):
    cibles = _titan_cibles(p)
    if cibles:
        o = p.choisir(Decision("choisir", "carte", [_option_carte(p, n, "ajoutée ou Invoquée") for n in cibles]))
        _ajouter_ou_invoquer(p, "deck", o.valeur)


TITAN_F = Formalisation(
    nom=TITAN, text_sha256="e8f39520db29a990d909b184c5b3dfc217f432b03549fbe239b89a6ac3435aa8",
    materiels=(None, _titan_mat),
    insensible=_titan_insensible, effet_insensible=2,
    bonus_atk=lambda p, inst: 100 * int(next((m.valeur for m in inst.modifications if m.champ == "niveaux_materiaux"), "0")),
    effets=(
        Effet(1, "restriction", ("terrain",), (), resolution=_continu,
              note="Gagne 100 ATK par Niveau d'origine des matériels de son Invocation Fusion (codé : `bonus_atk`)."),
        Effet(2, "restriction", ("terrain",), (), resolution=_continu,
              note="Après son Invocation Fusion, pour le reste du tour : insensible aux effets activés des autres "
                   "monstres Invoqués Spécialement depuis l'Extra Deck (codé : `insensible`)."),
        Effet(3, "fin", ("cimetiere",), (("par_nom_effet", TITAN),), condition=_cond_envoyee_ce_tour,
              possible=lambda p, l, n: bool(_titan_cibles(p)), resolution=_titan_fin,
              categories=("recherche_deck", "invocation_deck"),
              note="Phase de Fin, envoyé au Cimetière ce tour : ajouter ou Invoquer Spécialement 1 « Fallen of Albaz » "
                   "ou 1 monstre « Dogmatika » du Deck (le verrou de Nadir ne vise que l'Extra Deck, R13)."),
    ),
    sources="T17, T18, T22, T24, T47, T61 ; R03, R11, R12, R13",
)


FORMALISATIONS_J1: dict[str, Formalisation] = {f.nom: f for f in (
    ASH_F, CARTESIA_F, BOPENING_F, BHIGH_F, COCA_F, DECCLESIA_F, DROLL_F, WHITE_F, OGRE_F, SARC_F, QUEM_F,
    IECCLESIA_F, FUWALOS_F, NADIR_F, SKITT_F, SPOLY_F, TFTV_F, GSWORD_F, MERC_F,
    SANCTIFIRE_F, LULU_F, EDD_F, GARURA_F, GRANG_F, AEON_F, MIRROR_F, MIXOUSIA_F, DRAGO_F, SPRIND_F, DOGMA_F,
    CHAMPIONS_F, TITAN_F,
)}
