"""Deck source : chargement, noms « always treated as », validité, clauses « per turn ».

Les tests qui lisent les textes demandent la base de référence (yugioh.db, lecture seule) ; ils sont
ignorés, avec la raison, quand elle est absente (CI, poste sans base).
"""

from dataclasses import replace

import pytest

from moteur_combos import chemins
from moteur_combos.base import ouvrir_combos, ouvrir_reference
from moteur_combos.deck import (
    analyser_limites, archetypes_traites_comme, charger_deck, controle_validite, enregistrer_carte, etiquettes,
    lire_textes, noms_traites_comme, tous_les_noms, verifier_empreintes, vocabulaire_archetypes,
)

REF = chemins.base_de_reference()
avec_base = pytest.mark.skipif(not REF.exists(), reason=f"base de référence absente ({REF})")


@pytest.fixture(scope="module")
def deck():
    return charger_deck(chemins.DECK_SOURCE)


@pytest.fixture(scope="module")
def textes(deck):
    con = ouvrir_reference(REF)
    try:
        return lire_textes(con, [c.card_id for c in deck.cartes]), tous_les_noms(con)
    finally:
        con.close()


def test_deck_source(deck):
    assert deck.ref == "6af240d29e8b7a3a8eb28d8d"
    assert (deck.total("main"), deck.total("extra"), deck.total("side")) == (40, 15, 15)
    assert len([c for c in deck.cartes if c.zone in ("main", "extra")]) == 37


def test_clauses_de_nom_et_d_archetype():
    # Fragments de syntaxe, pas des textes de cartes.
    assert noms_traites_comme('(This card is always treated as "Fallen of Albaz".)') == ["Fallen of Albaz"]
    assert archetypes_traites_comme('(always treated as a "Dogmatika" and "Despia" card.)') == ["Dogmatika", "Despia"]
    assert noms_traites_comme('always treated as a "Dogmatika" card') == []
    assert archetypes_traites_comme('always treated as "Fallen of Albaz"') == []


def test_limite_de_trois_par_nom_traite_comme_compris(deck):
    """Relecture 1 (R03) : Albaz ×1 + White Dragon ×2 = 3, partagent la même limite."""
    noms = {c.nom: {c.nom} for c in deck.cartes}
    noms["Fallen of the White Dragon"] = {"Fallen of the White Dragon", "Fallen of Albaz"}
    assert controle_validite(deck, noms) == []
    # Un White Dragon de plus : 4 cartes portent le nom « Fallen of Albaz ».
    cartes = tuple(replace(c, nombre=3) if c.nom == "Fallen of the White Dragon" else c for c in deck.cartes)
    trop = replace(deck, cartes=cartes)
    violations = controle_validite(trop, noms)
    assert any("Fallen of Albaz" in v and "4 exemplaires" in v for v in violations)


def test_banlist_et_tailles(deck):
    noms = {c.nom: {c.nom} for c in deck.cartes}
    cartes = tuple(replace(c, nombre=2) if c.nom == "Branded Fusion" else c for c in deck.cartes)
    assert any("Limited" in v for v in controle_validite(replace(deck, cartes=cartes), noms))
    petit = replace(deck, cartes=tuple(c for c in deck.cartes if c.nom != "Branded Fusion"))
    assert any("Main Deck de 39" in v for v in controle_validite(petit, noms))


def test_clauses_par_tour_reconnues():
    a = analyser_limites("X", 'You can only activate 1 "X" per turn.')
    assert a.clauses == [("activation_par_nom", "X")]
    a = analyser_limites("X", 'Once per turn: You can do things.')
    assert a.clauses == [("par_exemplaire", None)]
    a = analyser_limites("X", 'You can only use each effect of "Y" once per turn.')
    assert a.clauses == [("par_nom_effet", "Y")] and a.nom_different == ["Y"]
    a = analyser_limites("X", "You can only do this twice per turn.")
    assert a.non_reconnues


@avec_base
def test_empreintes_identiques(deck, textes):
    assert verifier_empreintes(deck, textes[0]) == []


@avec_base
def test_etiquettes_r11(deck, textes):
    """R11 confirmé : Quem est Dogmatika et Despia ; Albaz n'est pas Dogmatika ; TFTV est Branded et Dogmatika."""
    txt, noms = textes
    vocab = vocabulaire_archetypes([t.texte for t in txt.values()], noms)
    assert {"Branded", "Despia", "Dogmatika", "Ecclesia"} <= vocab
    assert "Fallen of Albaz" not in vocab  # nom de carte, pas archétype
    par_nom = {c.nom: etiquettes(c.nom, txt[c.card_id].texte, vocab) for c in deck.cartes}

    def arch(nom):
        return {t for t, k, _ in par_nom[nom] if k == "archetype"}

    assert arch("Guiding Quem, the Virtuous") >= {"Dogmatika", "Despia"}
    assert "Dogmatika" not in arch("Fallen of Albaz")
    assert arch("The Fallen & The Virtuous") >= {"Branded", "Dogmatika"}
    assert "Ecclesia" in arch("Incredible Ecclesia, the Virtuous")
    assert arch("Blazing Cartesia, the Virtuous") & {"Dogmatika", "Ecclesia"} == set()
    assert arch("Tri-Brigade Springans Kitt") >= {"Tri-Brigade", "Springans"}
    noms_white = {t for t, k, _ in par_nom["Fallen of the White Dragon"] if k == "nom"}
    assert noms_white == {"Fallen of the White Dragon", "Fallen of Albaz"}


@avec_base
def test_toutes_les_clauses_du_deck_representables(deck, textes):
    txt, _ = textes
    for c in deck.cartes:
        assert analyser_limites(c.nom, txt[c.card_id].texte).non_reconnues == [], c.nom


@avec_base
def test_errata_remet_le_statut_a_non_traitee(tmp_path, deck, textes):
    txt, _ = textes
    carte = deck.par_nom()["Fallen of Albaz"]
    con = ouvrir_combos(tmp_path / "combos.db")
    t = replace(txt[carte.card_id])  # copie : la fixture est partagée
    assert enregistrer_carte(con, carte, t, set()) == "nouvelle"
    con.execute("UPDATE cb_card SET status = 'verifiee', verified_by = 'juge' WHERE card_id = ?", (carte.card_id,))
    assert enregistrer_carte(con, carte, t, set()) == "inchangee"
    assert con.execute("SELECT status FROM cb_card").fetchone()[0] == "verifiee"  # jamais rétrogradé
    t.texte += " (errata)"
    assert enregistrer_carte(con, carte, t, set()) == "texte_change"
    statut, raison = con.execute("SELECT status, status_reason FROM cb_card").fetchone()
    assert statut == "non_traitee" and "errata" in raison
    # Les effets formalisés sur l'ancien texte repassent aussi à non_traitee.
    con.execute("INSERT INTO cb_effect (card_id, position, kind, optional, text_span, text_sha256, status)"
                " VALUES (?, 1, 'ignition', 1, 'x', 'y', 'verifiee')", (carte.card_id,))
    t.texte += " (errata 2)"
    assert enregistrer_carte(con, carte, t, set()) == "texte_change"
    assert con.execute("SELECT status FROM cb_effect").fetchone()[0] == "non_traitee"
    # Renumérotation YGOPRODeck : même nom, autre id → refus explicite.
    with pytest.raises(ValueError, match="renumérotation"):
        enregistrer_carte(con, replace(carte, card_id=carte.card_id + 1), t, set())
    con.close()
