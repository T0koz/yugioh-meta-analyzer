"""Situations du YAML : alias, départs, classement, harnais de bout en bout."""

from collections import Counter

import pytest

from moteur_combos import chemins
from moteur_combos.classement import CLASSES, classer, lire_points, regles_precisees
from moteur_combos.deck import charger_deck
from moteur_combos.harnais import executer
from moteur_combos.situations import charger_tests, construire_depart, verifier_jeu

REF = chemins.base_de_reference()


@pytest.fixture(scope="module")
def deck():
    return charger_deck(chemins.DECK_SOURCE)


@pytest.fixture(scope="module")
def jeu():
    return charger_tests(chemins.TESTS_YAML)


@pytest.fixture(scope="module")
def departs(jeu, deck):
    return {s["id"]: construire_depart(s, jeu, deck) for s in jeu.situations}


@pytest.fixture(scope="module")
def situations(jeu):
    return {s["id"]: s for s in jeu.situations}


def test_jeu_coherent(jeu, deck):
    assert len(jeu.situations) == 72
    assert verifier_jeu(jeu, deck) == []


def test_tous_les_departs_construits(departs):
    invalides = {k: d.erreurs for k, d in departs.items() if not d.valide}
    assert invalides == {}


def test_conservation_des_cartes(departs, deck):
    """« deck = les 40 cartes moins celles placées ailleurs » : rien ne se crée, rien ne se perd."""
    cote_main = {c.nom for c in deck.cartes if c.zone == "main"}
    cote_extra = {c.nom for c in deck.cartes if c.zone == "extra"}
    for tid, d in departs.items():
        j = d.etat.joueurs[0]
        toutes = Counter(i.carte for i in j.toutes_les_instances())
        toutes.update(o.instance.carte for o in d.etat.zones_monstre_extra if o.controleur == 0)
        assert sum(n for c, n in toutes.items() if c in cote_main) == 40, tid
        assert sum(n for c, n in toutes.items() if c in cote_extra) == 15, tid


def test_t22_titan_envoye_non_invoque(departs):
    """T22 : TITAN au Cimetière, venu de l'Extra Deck, « correctement invoqué » non affirmé."""
    titan = [i for i in departs["T22"].etat.joueurs[0].cimetiere if i.carte == "Titaniklad the Ash Dragon"][0]
    assert titan.venue_extra_deck and titan.correctement_invoquee is not True


def test_t52_rind_invoque_puis_envoye(departs):
    rind = [i for i in departs["T52"].etat.joueurs[0].cimetiere if i.carte == "Rindbrumm the Striking Dragon"][0]
    assert rind.correctement_invoquee is True and rind.arrivee == "invocation_fusion"
    assert any(o.instance.carte == "Mirrorjade the Iceblade Dragon" for o in departs["T52"].etat.zones_monstre_extra)


def test_t32_nom_temporaire(departs):
    coca = departs["T32"].etat.joueurs[0].case("M1")
    assert coca.carte == "Cocatorium the Heavy Metal Avian"
    assert coca.nom_courant() == "Tri-Brigade Mercourier"
    assert departs["T32"].etat.cadre.invocation_normale_utilisee


def test_t41_magie_posee(departs):
    spoly = departs["T41"].etat.joueurs[0].case("S1")
    assert spoly.carte == "Super Polymerization" and spoly.face == "cachee" and spoly.posee_ce_tour


def test_t16_phase_de_fin_et_memoire_libre(departs):
    d = departs["T16"]
    assert d.etat.cadre.phase == "fin"
    assert not d.complet and d.etat.memoire.faits_libres  # mémoire en texte libre (D7)


def test_t67_carte_du_side(departs):
    j = departs["T67"].etat.joueurs[0]
    assert "Lava Golem" in [i.carte for i in j.main] and len(j.deck) == 36


def test_departs_identiques_meme_empreinte(departs):
    """Équivalence : T08 et T09 ont le même départ écrit → le même état."""
    assert departs["T08"].etat.empreinte() == departs["T09"].etat.empreinte()
    assert departs["T08"].etat.empreinte() != departs["T07"].etat.empreinte()


def test_classement(situations):
    points = lire_points(chemins.POINTS_DE_REGLE)
    assert points["R08"].un_seul_avis and points["R27b"].un_seul_avis and points["R34"].un_seul_avis
    assert points["R22"].confirme and not points["R22"].un_seul_avis and not points["R27a"].un_seul_avis
    assert regles_precisees(situations["T32"]) == ["R27a"]
    assert classer(situations["T32"], points, False)[0] == "regles_confirmees"
    assert classer(situations["T33"], points, False)[0] == "un_seul_avis"
    assert classer(situations["T45"], points, False)[0] == "regles_confirmees"  # R22, levé par cohérence
    assert classer(situations["T03"], points, False)[0] == "non_executable_sans_regles"
    assert classer(situations["T68"], points, True)[0] == "regles_confirmees"
    for s in situations.values():
        assert classer(s, points, s["id"] == "T68")[0] in CLASSES


def test_point_inconnu_refuse(situations):
    points = lire_points(chemins.POINTS_DE_REGLE)
    faux = dict(situations["T02"], regles=["R99"])
    with pytest.raises(ValueError):
        classer(faux, points, False)


@pytest.mark.skipif(not REF.exists(), reason=f"base de référence absente ({REF})")
def test_harnais_de_bout_en_bout(tmp_path):
    rapport = executer(tmp_path / "combos.db", REF)
    assert rapport.echecs == []
    assert len(rapport.lignes) == 72
    compte = Counter(lt.classe for lt in rapport.lignes)
    assert sum(compte.values()) == 72 and set(compte) <= set(CLASSES)
    # Tranche 0 : les situations à scénario sont exécutées par le moteur et conformes au YAML.
    from moteur_combos.scenarios import SCENARIOS

    assert [lt.test_id for lt in rapport.lignes if lt.statut == "verifie"] == sorted(SCENARIOS)
    import sqlite3

    con = sqlite3.connect(tmp_path / "combos.db")
    assert con.execute("SELECT COUNT(*) FROM cb_test_situation").fetchone()[0] == 72
    assert con.execute("SELECT COUNT(*) FROM cb_card WHERE status = 'non_traitee'").fetchone()[0] == 40
    assert dict(con.execute("SELECT status, COUNT(*) FROM cb_card WHERE status <> 'non_traitee' GROUP BY status")
                .fetchall()) == {"formalisee": 4, "brouillon": 1}
    orphelins = con.execute("SELECT COUNT(*) FROM cb_test_situation t LEFT JOIN cb_state s"
                            " ON s.state_id = t.start_state WHERE s.state_id IS NULL").fetchone()[0]
    assert orphelins == 0
    # Relancer ne duplique rien (états adressés par leur contenu).
    n = con.execute("SELECT COUNT(*) FROM cb_state").fetchone()[0]
    con.close()
    executer(tmp_path / "combos.db", REF)
    con = sqlite3.connect(tmp_path / "combos.db")
    assert con.execute("SELECT COUNT(*) FROM cb_state").fetchone()[0] == n
    con.close()
