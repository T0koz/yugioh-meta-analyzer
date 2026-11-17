"""Tranche 0 (TOK-90) : le combo Branded de bout en bout, les trois négatifs, « non couvert », et les règles
codées (limites dans leurs cinq formes, coût, vitesse) sur des cartes d'essai qui ne demandent aucune base."""

from dataclasses import replace

import pytest

from moteur_combos import chemins
from moteur_combos.base import ouvrir_reference
from moteur_combos.cartes import ALBAZ, ALUBER, BFUSION, FORMALISATIONS, RIND, TBKITT, Effet, Formalisation, _albaz_cout
from moteur_combos.catalogue import Catalogue, Fiche, construire_catalogue
from moteur_combos.deck import CarteDeck, DeckSource, TexteCarte, charger_deck, lire_textes, tous_les_noms
from moteur_combos.modele import Cadre, Etat, Instance, LimiteConsommee, MemoireTour, ZonesJoueur
from moteur_combos.regles import Declaration, Moteur, Partie, Script
from moteur_combos.scenarios import COMBO, SCENARIOS, executer_situation
from moteur_combos.situations import charger_tests, construire_depart

REF = chemins.base_de_reference()
avec_base = pytest.mark.skipif(not REF.exists(), reason=f"base de référence absente ({REF})")


# ── Avec la base : le deck réel ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def monde():
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(REF)
    try:
        textes = lire_textes(con, [c.card_id for c in deck.cartes])
        noms = tous_les_noms(con)
    finally:
        con.close()
    cat = construire_catalogue(deck, textes, noms, FORMALISATIONS)
    jeu = charger_tests(chemins.TESTS_YAML)
    return deck, cat, jeu


def _depart(monde, tid):
    deck, _, jeu = monde
    s = next(x for x in jeu.situations if x["id"] == tid)
    return s, construire_depart(s, jeu, deck)


@avec_base
def test_cinq_cartes_formalisees_sur_le_texte_actuel(monde):
    _, cat, _ = monde
    for nom in (ALUBER, BFUSION, ALBAZ, TBKITT, RIND):
        assert cat[nom].declaree, f"{nom} : formalisation écartée ({cat[nom].formalisation_ecartee})"
    assert not cat["Lava Golem"].declaree
    assert [n for n, f in FORMALISATIONS.items() if not f.complete] == [RIND]  # effet 1 : résolution non codée


@avec_base
def test_combo_de_bout_en_bout(monde):
    """Aluber (Invocation Normale) → Branded Fusion → Rindbrumm (Albaz + Tri-Brigade Springans Kitt du Deck)
    → Kitt rappelle Albaz. Deux transitions, d'état stable à état stable."""
    _, cat, jeu = monde
    _, d = _depart(monde, "T01")
    moteur = Moteur(cat)
    etape1 = moteur.jouer(d.etat, COMBO[0].declaration, Script(list(COMBO[0].script)))
    assert etape1.verdict == "legal", etape1.raison
    assert etape1.etat.est_stable()
    etape2 = moteur.jouer(etape1.etat, COMBO[1].declaration, Script(list(COMBO[1].script)))
    assert etape2.verdict == "legal", etape2.raison
    e = etape2.etat
    j = e.joueurs[0]
    assert e.est_stable()
    terrain = {c: (i.carte, i.position) for c, i in j.cases}
    assert terrain == {"M1": (ALUBER, "attaque"), "M2": (ALBAZ, "defense")}
    assert [(o.cellule, o.instance.carte, o.instance.correctement_invoquee) for o in e.zones_monstre_extra] == [
        ("ZME_G", RIND, True)]
    assert sorted(i.carte for i in j.main) == sorted(["Ash Blossom & Joyous Spring"] * 2
                                                     + ["Ghost Ogre & Snow Rabbit", "Droll & Lock Bird"])
    assert sorted(i.carte for i in j.cimetiere) == [BFUSION, TBKITT]
    assert all(i.envoyee_cimetiere_ce_tour for i in j.cimetiere)
    m = e.memoire
    assert m.limites == frozenset({
        LimiteConsommee("par_nom_carte", ALUBER), LimiteConsommee("activation_par_nom", BFUSION),
        LimiteConsommee("par_nom_effet", TBKITT, 2)})
    assert [(v.source, v.cle) for v in m.verrous] == [(BFUSION, "extra_fusion_seulement")]
    assert m.invocations_extra == ((RIND, "fusion"),)
    assert e.cadre.invocation_normale_utilisee
    assert sum(1 for i in j.deck if i.carte in (ALBAZ, TBKITT, BFUSION)) == 0
    # Le déclencheur d'Albaz rappelé est vu, et écarté pour la bonne raison (aucun monstre adverse).
    assert any("Fallen of Albaz/1 non activable" in n and "R01" in n for n in etape2.notes)
    # Réserves : les cartes non formalisées restées en main auraient pu agir ; rien n'est caché.
    assert etape2.reserves == {"Ash Blossom & Joyous Spring", "Ghost Ogre & Snow Rabbit", "Droll & Lock Bird"}
    # Listes peut-être incomplètes : 4 Fusions dont la ligne de matériels n'est pas formalisée, et les paires de
    # matériels qui font intervenir une carte non formalisée (Fallen of the White Dragon, Springans Kitt…).
    fusions = {x for x in etape2.incomplet if "(" not in x}
    assert fusions == {"Albion the Sanctifire Dragon", "Mirrorjade the Iceblade Dragon",
                       "Sprind the Irondash Dragon", "Titaniklad the Ash Dragon"}
    paires = etape2.incomplet - fusions
    assert f"{ALBAZ} (deck) + Springans Kitt (deck)" in paires
    assert f"{ALBAZ} (deck) + {TBKITT} (deck)" not in paires
    # Déterminisme : rejouer donne la même empreinte d'état.
    bis = moteur.jouer(moteur.jouer(d.etat, COMBO[0].declaration, Script(list(COMBO[0].script))).etat,
                       COMBO[1].declaration, Script(list(COMBO[1].script)))
    assert bis.etat.empreinte() == e.empreinte()


@avec_base
@pytest.mark.parametrize("tid", sorted(SCENARIOS))
def test_scenarios_du_jeu_de_tests(monde, tid):
    _, cat, jeu = monde
    s, d = _depart(monde, tid)
    ex = executer_situation(s, d.etat, jeu.alias, cat)
    assert ex.statut == "verifie", ex.detail


@avec_base
def test_les_trois_negatifs_et_non_couvert(monde):
    """Raisons attendues, pas seulement le verdict : un « illégal » pour une autre raison serait un faux positif."""
    _, cat, jeu = monde
    raisons = {}
    for tid in ("T60", "T04", "T11", "T68"):
        s, d = _depart(monde, tid)
        raisons[tid] = executer_situation(s, d.etat, jeu.alias, cat).resultat.raison
    assert "vitesse 1" in raisons["T60"]
    assert "par_nom_carte" in raisons["T04"] and "déjà consommée" in raisons["T04"]
    assert "R01" in raisons["T11"]
    assert "Lava Golem" in raisons["T68"] and "non formalisée" in raisons["T68"]


@avec_base
def test_choisir_une_carte_non_formalisee_renvoie_non_couvert(monde):
    """Aluber peut légalement chercher Branded Opening ; la suite ferait intervenir une carte non formalisée."""
    _, cat, _ = monde
    _, d = _depart(monde, "T01")
    script = Script([("activer_declenche", f"{ALUBER}/1"), ("reponse", "passer"), ("carte", "Branded Opening")])
    r = Moteur(cat).jouer(d.etat, Declaration("invocation_normale", ALUBER), script)
    assert r.verdict == "non_couvert" and "Branded Opening" in r.raison


@avec_base
def test_materiel_non_formalise_renvoie_non_couvert(monde):
    _, cat, _ = monde
    _, d = _depart(monde, "T15")
    script = Script([("reponse", "passer"), ("fusion", RIND), ("materiaux", f"{ALBAZ} (deck) + Springans Kitt (deck)")])
    r = Moteur(cat).jouer(d.etat, Declaration("activer", BFUSION, 1), script)
    assert r.verdict == "non_couvert" and "Springans Kitt" in r.raison


@avec_base
def test_aluber_hors_de_son_declenchement(monde):
    """Hors timing, variante : l'effet d'Aluber ne se déclare pas dans un état ouvert (T06 : Aluber déjà là)."""
    _, cat, _ = monde
    _, d = _depart(monde, "T06")
    r = Moteur(cat).jouer(d.etat, Declaration("activer", ALUBER, 1))
    assert r.verdict == "illegal" and "effet déclenché" in r.raison


@avec_base
def test_branded_fusion_ne_repond_pas_a_aluber(monde):
    """Hors timing, variante sur une carte formalisée : Branded Fusion (Magie Normale) ne s'enchaîne pas."""
    _, cat, _ = monde
    _, d = _depart(monde, "T01")
    etat = replace(d.etat, joueurs=(replace(d.etat.joueurs[0], main=d.etat.joueurs[0].main + (Instance(BFUSION),),
                                            deck=tuple(i for i in d.etat.joueurs[0].deck if i.carte != BFUSION)),
                                    d.etat.joueurs[1]))
    script = Script([("activer_declenche", f"{ALUBER}/1"), ("reponse", BFUSION)])
    r = Moteur(cat).jouer(etat, Declaration("invocation_normale", ALUBER), script)
    assert r.verdict == "illegal" and "vitesse 1" in r.raison


# ── Sans base : cartes d'essai (règles seules) ─────────────────────────────────────────────────

def _fiche(nom, type_carte="Effect Monster", frame="effect", race="Fairy", formalisation=None, niveau=4):
    return Fiche(nom=nom, zone_deck="main", type_carte=type_carte, frame=frame, attribut="LIGHT", race=race,
                 niveau=niveau, atk=1000, defense=1000, text_sha256="0" * 64, noms=frozenset({nom}),
                 archetypes=frozenset(), mentions=frozenset(), formalisation=formalisation)


def _resolu(p, m):
    p.notes.append(f"résolu : {m.carte}/{m.effet}")


ESSAI = Formalisation("Essai", "0" * 64, (
    Effet(1, "ignition", ("terrain",), (("par_exemplaire", None),), cout=_albaz_cout, resolution=_resolu),
    Effet(2, "ignition", ("terrain",), (("par_nom_effet", "Essai"),), resolution=_resolu),
    Effet(3, "ignition", ("terrain",), (("par_nom_effet", "Essai"),), resolution=_resolu),
))
VIDE = Formalisation("Vide", "0" * 64, ())


def _catalogue():
    cat = Catalogue()
    cat.fiches = {
        "Essai": _fiche("Essai", formalisation=ESSAI),
        "Vide": _fiche("Vide", formalisation=VIDE),
        "Inconnue": _fiche("Inconnue"),
        "Magie N": _fiche("Magie N", "Spell Card", "spell", "Normal"),
    }
    return cat


def _etat(main=(), cases=(), limites=frozenset()):
    return Etat(cadre=Cadre(), joueurs=(ZonesJoueur(main=tuple(Instance(n) for n in main), cases=tuple(
        (c, Instance(n, face="visible", position="attaque")) for c, n in cases)),
        ZonesJoueur(main_connue=False, deck_connu=False)), memoire=MemoireTour(limites=limites))


def test_cout_paye_a_l_activation_et_once_per_turn_par_exemplaire():
    cat = _catalogue()
    m = Moteur(cat)
    e0 = _etat(main=("Vide", "Vide"), cases=(("M1", "Essai"), ("M2", "Essai")))
    r = m.jouer(e0, Declaration("activer", "Essai", 1), Script([("cout", "défausser Vide"), ("reponse", "passer")]))
    assert r.verdict == "legal", r.raison
    j = r.etat.joueurs[0]
    assert [i.carte for i in j.main] == ["Vide"] and [i.carte for i in j.cimetiere] == ["Vide"]
    assert dict(j.cases)["M1"].limites_exemplaire == (1,) and dict(j.cases)["M2"].limites_exemplaire == ()
    assert any(p.type == "cout" for p in r.pas) and "résolu : Essai/1" in r.notes
    # L'autre exemplaire garde son « Once per turn » ; le premier ne l'a plus.
    r2 = m.jouer(r.etat, Declaration("activer", "Essai", 1), Script([("cout", "défausser Vide"), ("reponse", "passer")]))
    assert r2.verdict == "legal", r2.raison
    r3 = m.jouer(r2.etat, Declaration("activer", "Essai", 1))
    assert r3.verdict == "illegal" and "Once per turn" in r3.raison


def test_cout_impossible_a_payer():
    r = Moteur(_catalogue()).jouer(_etat(cases=(("M1", "Essai"),)), Declaration("activer", "Essai", 1))
    assert r.verdict == "illegal" and "coût" in r.raison


def test_cout_qui_deplace_une_carte_non_formalisee():
    r = Moteur(_catalogue()).jouer(_etat(main=("Inconnue",), cases=(("M1", "Essai"),)),
                                   Declaration("activer", "Essai", 1), Script([("cout", "défausser Inconnue")]))
    assert r.verdict == "non_couvert" and "Inconnue" in r.raison


def test_par_nom_effet_n_interdit_que_le_meme_effet():
    m = Moteur(_catalogue())
    e0 = _etat(cases=(("M1", "Essai"), ("M2", "Essai")))
    r = m.jouer(e0, Declaration("activer", "Essai", 2), Script([("reponse", "passer")]))
    assert r.verdict == "legal"
    assert LimiteConsommee("par_nom_effet", "Essai", 2) in r.etat.memoire.limites
    assert m.jouer(r.etat, Declaration("activer", "Essai", 2)).verdict == "illegal"  # autre copie : même effet
    assert m.jouer(r.etat, Declaration("activer", "Essai", 3), Script([("reponse", "passer")])).verdict == "legal"


@pytest.mark.parametrize("forme", ["par_nom_carte", "activation_par_nom", "invocation_par_nom"])
def test_formes_par_nom_bloquent_tous_les_effets_cites(forme):
    """par_nom_carte, activation_par_nom, invocation_par_nom : clé sur le nom seul, toutes copies confondues."""
    effet = Effet(1, "ignition", ("terrain",), ((forme, "Essai"),), resolution=_resolu)
    p = Partie(_catalogue(), _etat(cases=(("M1", "Essai"),)), Script())
    assert p.limite_consommee(effet, None) is None
    p.consommer_limites(effet, ("terrain", "M1"), "Essai")
    autre = replace(effet, numero=2)
    assert "déjà consommée" in p.limite_consommee(autre, None)


def test_magie_normale_non_formalisee_exclue_de_la_fenetre_de_reponse():
    cat = _catalogue()
    r = Moteur(cat).jouer(_etat(main=("Magie N",), cases=(("M1", "Essai"),)), Declaration("activer", "Essai", 2),
                          Script([("reponse", "Magie N")]))
    assert r.verdict == "illegal" and "vitesse 1" in r.raison


def test_carte_non_formalisee_dans_la_main_est_une_reserve():
    r = Moteur(_catalogue()).jouer(_etat(main=("Inconnue",), cases=(("M1", "Essai"),)),
                                   Declaration("activer", "Essai", 2), Script([("reponse", "passer")]))
    assert r.verdict == "legal" and r.reserves == {"Inconnue"}


def test_un_errata_desactive_la_formalisation():
    carte = CarteDeck("Fallen of Albaz", 1, "main", 1, "Effect Monster", "DARK", "Dragon", 4, 1800, 0, None, None)
    deck = DeckSource("d", "d", None, None, chemins.DECK_SOURCE, "x", (carte,))
    texte = TexteCarte(1, "Fallen of Albaz", "texte modifié par un errata", "effect")
    cat = construire_catalogue(deck, {1: texte}, set(), FORMALISATIONS)
    assert not cat["Fallen of Albaz"].declaree
    assert "errata" in cat["Fallen of Albaz"].formalisation_ecartee
