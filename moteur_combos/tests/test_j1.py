"""Lot C2 (J1, TOK-118) : les 37 cartes du pilote, les situations J1, la couverture des effets, et les règles ajoutées
(déclencheurs simultanés, annulation, chaîne sans réponse, Phase de Fin) sur des cartes d'essai sans base."""

from dataclasses import replace

import pytest

from moteur_combos import chemins, regles
from moteur_combos.base import ouvrir_reference
from moteur_combos.cartes import FORMALISATIONS, Effet, Formalisation
from moteur_combos.catalogue import Catalogue, Fiche, construire_catalogue
from moteur_combos.deck import charger_deck, lire_textes, tous_les_noms
from moteur_combos.modele import Cadre, Etat, Instance, MemoireTour, ZonesJoueur
from moteur_combos.regles import HORS_PERIMETRE, NE_PAS_ACTIVER, Declaration, Moteur, Script
from moteur_combos.scenarios import SCENARIOS, SCENARIOS_J1, executer_situation
from moteur_combos.situations import charger_tests, construire_depart

REF = chemins.base_de_reference()
avec_base = pytest.mark.skipif(not REF.exists(), reason=f"base de référence absente ({REF})")


@pytest.fixture(scope="module")
def monde():
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(REF)
    try:
        textes = lire_textes(con, [c.card_id for c in deck.cartes])
        noms = tous_les_noms(con)
    finally:
        con.close()
    return deck, construire_catalogue(deck, textes, noms, FORMALISATIONS), charger_tests(chemins.TESTS_YAML), \
        charger_tests(chemins.SITUATIONS_J1)


def test_37_cartes_formalisees_toutes_resolutions_ecrites():
    deck = charger_deck(chemins.DECK_SOURCE)
    pilote = {c.nom for c in deck.cartes if c.zone in ("main", "extra")}
    assert len(pilote) == 37 and set(FORMALISATIONS) == pilote
    assert all(f.complete for f in FORMALISATIONS.values())
    # Les empreintes sont celles du fichier source (le texte TCG de notre base fait foi).
    sha = {c.nom: c.text_sha256 for c in deck.cartes}
    assert all(f.text_sha256 == sha[n] for n, f in FORMALISATIONS.items())


@avec_base
def test_empreintes_identiques_au_texte_lu(monde):
    _, cat, _, _ = monde
    assert all(cat[n].declaree for n in FORMALISATIONS), [n for n in FORMALISATIONS if not cat[n].declaree]


@avec_base
@pytest.mark.parametrize("jid", sorted(SCENARIOS_J1))
def test_situations_j1(monde, jid):
    deck, cat, _, jeu = monde
    s = next(x for x in jeu.situations if x["id"] == jid)
    d = construire_depart(s, jeu, deck)
    ex = executer_situation(s, d.etat, jeu.alias, cat, SCENARIOS_J1)
    assert ex.statut == "verifie", ex.detail


@avec_base
def test_chaque_effet_du_pilote_est_exerce(monde):
    deck, cat, yaml_, jeu = monde
    regles.EXERCES.clear()
    for j, scen in ((yaml_, SCENARIOS), (jeu, SCENARIOS_J1)):
        for s in j.situations:
            if s["id"] in scen:
                executer_situation(s, construire_depart(s, j, deck).etat, j.alias, cat, scen)
    pilote = {(n, e.numero) for n, f in FORMALISATIONS.items() for e in f.effets if e.resolution != HORS_PERIMETRE}
    assert pilote - regles.EXERCES == set()


@avec_base
def test_ash_annule_l_effet_d_aluber(monde):
    """T70 : Ash Blossom contre son propre Aluber : rien n'est ajouté à la main."""
    deck, cat, yaml_, _ = monde
    s = next(x for x in yaml_.situations if x["id"] == "T70")
    ex = executer_situation(s, construire_depart(s, yaml_, deck).etat, yaml_.alias, cat)
    main = sorted(i.carte for i in ex.resultat.etat.joueurs[0].main)
    assert main == sorted(["Ash Blossom & Joyous Spring", "Ghost Ogre & Snow Rabbit", "Droll & Lock Bird"])
    assert any("annulé" in n for n in ex.resultat.notes)


@avec_base
def test_un_errata_desactive_une_carte_j1(monde):
    deck, _, _, _ = monde
    from moteur_combos.deck import TexteCarte
    con = ouvrir_reference(REF)
    try:
        textes = lire_textes(con, [c.card_id for c in deck.cartes])
    finally:
        con.close()
    quem = next(c for c in deck.cartes if c.nom == "Guiding Quem, the Virtuous")
    textes[quem.card_id] = TexteCarte(quem.card_id, quem.nom, "texte changé", "effect")
    cat = construire_catalogue(deck, textes, set(), FORMALISATIONS)
    assert not cat[quem.nom].declaree and "errata" in cat[quem.nom].formalisation_ecartee


# ── Sans base : cartes d'essai ─────────────────────────────────────────────────────────────────

def _fiche(nom, formalisation, type_carte="Effect Monster", frame="effect"):
    return Fiche(nom=nom, zone_deck="main", type_carte=type_carte, frame=frame, attribut="LIGHT", race="Fairy",
                 niveau=4, atk=1000, defense=1000, text_sha256="0" * 64, noms=frozenset({nom}),
                 archetypes=frozenset(), mentions=frozenset(), formalisation=formalisation)


def _sur_invocation(p, ev, lieu, nom):
    return ev.type == "invocation_normale" and lieu[0] == "terrain"


def _note(p, m):
    p.notes.append(f"résolu : {m.carte}")


def _catalogue(obligatoire: bool):
    cat = Catalogue()
    a = Formalisation("Lanceur", "0" * 64, ())
    b = Formalisation("Oblig", "0" * 64, (Effet(1, "declenche", ("terrain",), facultatif=not obligatoire,
                                                 timing="if", declencheur=_sur_invocation, resolution=_note),))
    c = Formalisation("Facult", "0" * 64, (Effet(1, "declenche", ("terrain",), timing="if",
                                                  declencheur=_sur_invocation, resolution=_note),))
    cat.fiches = {"Lanceur": _fiche("Lanceur", a), "Oblig": _fiche("Oblig", b), "Facult": _fiche("Facult", c)}
    return cat


def _etat():
    return Etat(cadre=Cadre(), joueurs=(ZonesJoueur(main=(Instance("Lanceur"),), cases=(
        ("M2", Instance("Oblig", face="visible", position="attaque")),
        ("M3", Instance("Facult", face="visible", position="attaque")))),
        ZonesJoueur(main_connue=False, deck_connu=False)), memoire=MemoireTour())


def test_r22_obligatoire_d_abord_puis_ordre_libre():
    """Deux déclencheurs simultanés, l'un obligatoire : on ne peut pas s'arrêter avant de l'avoir mis en chaîne ;
    l'ordre reste libre ; le facultatif peut être laissé. Le dernier mis en chaîne se résout le premier."""
    cat = _catalogue(obligatoire=True)
    r = Moteur(cat).jouer(_etat(), Declaration("invocation_normale", "Lanceur"),
                          Script([("activer_declenche", "Facult/1"), ("activer_declenche", "Oblig/1"),
                                  ("reponse", "passer")]))
    assert r.verdict == "legal", r.raison
    d0 = r.decision("activer_declenche")
    assert set(d0.valeurs()) == {"Oblig/1", "Facult/1"}          # pas « ne pas activer » : Oblig attend
    assert [n for n in r.notes if n.startswith("résolu")] == ["résolu : Oblig", "résolu : Facult"]
    # Refuser l'obligatoire est illégal.
    r2 = Moteur(cat).jouer(_etat(), Declaration("invocation_normale", "Lanceur"),
                           Script([("activer_declenche", NE_PAS_ACTIVER)]))
    assert r2.verdict == "illegal"
    # Sans obligatoire : on peut n'en activer qu'un.
    r3 = Moteur(_catalogue(obligatoire=False)).jouer(
        _etat(), Declaration("invocation_normale", "Lanceur"),
        Script([("activer_declenche", "Oblig/1"), ("activer_declenche", NE_PAS_ACTIVER), ("reponse", "passer")]))
    assert r3.verdict == "legal" and [n for n in r3.notes if n.startswith("résolu")] == ["résolu : Oblig"]


def test_fin_de_tour_refusee_avec_un_effet_obligatoire():
    cat = Catalogue()
    f = Formalisation("Retour", "0" * 64, (Effet(1, "fin", ("cimetiere",), facultatif=False, resolution=_note),))
    cat.fiches = {"Retour": _fiche("Retour", f)}
    etat = Etat(cadre=Cadre(phase="fin"), joueurs=(ZonesJoueur(cimetiere=(Instance("Retour"),)),
                                                    ZonesJoueur(main_connue=False, deck_connu=False)))
    r = Moteur(cat).jouer(etat, Declaration("fin_de_tour", "—"))
    assert r.verdict == "illegal" and "R23" in r.raison
    r = Moteur(cat).jouer(etat, Declaration("activer", "Retour", 1), Script([("reponse", "passer")]))
    assert r.verdict == "legal"
    r = Moteur(cat).jouer(replace(etat, cadre=Cadre(phase="principale_1")), Declaration("activer", "Retour", 1))
    assert r.verdict == "illegal" and "Phase de Fin" in r.raison
