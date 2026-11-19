"""Jalon n°7 (TOK-144) : situations de l'échantillon J1 jouées par l'oracle, rejouées par le moteur.

Ces tests figent l'état **après correction** des trois désaccords mesurés (E32, E49, E68) : ce n'est pas le taux de
J1 (mesuré avant correction, `j1-rapport.md` § 9), seulement la garantie que les corrections tiennent.
"""

import pytest

from moteur_combos import chemins
from moteur_combos.base import ouvrir_reference
from moteur_combos.cartes import FORMALISATIONS
from moteur_combos.catalogue import construire_catalogue
from moteur_combos.deck import charger_deck, lire_textes, tous_les_noms
from moteur_combos.echantillon_oracle import (
    ECHANTILLON_YAML, EFFETS_TIRES, NON_TESTABLES, ORACLE, comparer, compter, wilson,
)
from moteur_combos.situations import charger_tests

REF = chemins.base_de_reference()
avec_base = pytest.mark.skipif(not REF.exists(), reason=f"base de référence absente ({REF})")


@pytest.fixture(scope="module")
def monde():
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(REF)
    try:
        cat = construire_catalogue(deck, lire_textes(con, [c.card_id for c in deck.cartes]), tous_les_noms(con),
                                   FORMALISATIONS)
    finally:
        con.close()
    return deck, cat, charger_tests(ECHANTILLON_YAML)


def test_chaque_situation_a_une_reponse_ou_est_non_testable():
    jeu = charger_tests(ECHANTILLON_YAML)
    ids = {s["id"] for s in jeu.situations}
    assert len(ids) == 86
    assert ids == set(ORACLE) | set(NON_TESTABLES)
    assert {e for s in jeu.situations for e in s["effets"]} == set(EFFETS_TIRES)


def test_wilson_valeurs_connues():
    assert wilson(0, 20)[1] == pytest.approx(0.1611, abs=1e-4)
    assert wilson(1, 20)[1] == pytest.approx(0.2361, abs=1e-4)   # 24,9 % = Clopper-Pearson, pas Wilson
    assert wilson(3, 20) == pytest.approx((0.0524, 0.3604), abs=1e-4)


@avec_base
@pytest.mark.parametrize("sid", sorted(ORACLE))
def test_situation_en_accord_apres_correction(monde, sid):
    deck, cat, jeu = monde
    s = next(x for x in jeu.situations if x["id"] == sid)
    c = comparer(s, jeu, deck, cat)
    assert c.issue == "accord", c.ecarts


@avec_base
def test_comptage_apres_correction(monde):
    deck, cat, jeu = monde
    r = compter([comparer(s, jeu, deck, cat) for s in jeu.situations])
    assert r["principal"] == (0, 20)
    assert r["pessimiste"] == (1, 20)          # DECCLESIA/2 : E18 non testable par l'oracle
    assert r["statut"]["DECCLESIA/2"] == "juste_avec_non_tranche"
