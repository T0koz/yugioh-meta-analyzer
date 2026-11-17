"""Tests de l'exploration bornée (lot C3, J2)."""

from __future__ import annotations

import sqlite3

import pytest

from moteur_combos import chemins
from moteur_combos.base import appliquer_schema, ouvrir_reference
from moteur_combos.cartes import FORMALISATIONS
from moteur_combos.catalogue import construire_catalogue
from moteur_combos.deck import charger_deck, enregistrer_carte, enregistrer_deck, lire_textes, tous_les_noms
from moteur_combos.exploration import (
    FILTRES_PAR_DEFAUT, Branche, ScriptExploration, declarations, developper, etat_depart, explorer, options_filtrees,
)
from moteur_combos.guides import GUIDES, Jalon, respecte_jalons
from moteur_combos.regles import Decision, Declaration, Moteur, Option
from moteur_combos.stockage_combos import Ecrivain, a_puis_directement_b, combos_passant_par, ouvrir_run

REF = chemins.base_de_reference()
avec_base = pytest.mark.skipif(not REF.exists(), reason=f"base de référence absente ({REF})")
FS = frozenset(FILTRES_PAR_DEFAUT)


@pytest.fixture(scope="module")
def monde():
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(REF)
    try:
        textes = lire_textes(con, [c.card_id for c in deck.cartes])
        cat = construire_catalogue(deck, textes, tous_les_noms(con), FORMALISATIONS)
    finally:
        con.close()
    return deck, cat, textes


# ── Sans base ──────────────────────────────────────────────────────────────────────────────────

def test_filtres_declares_n_ecartent_que_ce_qu_ils_disent():
    d = Decision("enchainer", "reponse", [Option("passer"), Option("Ash Blossom & Joyous Spring/1")])
    assert options_filtrees(d, FS) == ["passer"]
    assert options_filtrees(d, frozenset()) == ["passer", "Ash Blossom & Joyous Spring/1"]
    d = Decision("choisir", "carte", [Option("A"), Option("B")], [Option("C", False)])
    assert options_filtrees(d, FS) == ["A", "B", "C"]   # une option non couverte est rejouée (D5), jamais cachée


def test_decision_forcee_ne_consomme_pas_le_prefixe():
    """Le bug trouvé au lot C3 : une décision à une seule option décalait le préfixe au rejeu."""
    s = ScriptExploration(("x",), FS)
    assert s.repondre(Decision("enchainer", "reponse", [Option("passer")])) is None
    assert s.repondre(Decision("choisir", "carte", [Option("x"), Option("y")])) == "x"
    with pytest.raises(Branche):
        s.repondre(Decision("choisir", "carte", [Option("x"), Option("y")]))


def test_jalons_en_sous_suite():
    class A:
        def __init__(self, t, c, e=None, rep=()):
            self.declaration = Declaration(t, c, e)
            self.reponses = rep
    chemin = [A("activer", "N", 1, ("W",)), A("phase_de_fin", "—"), A("activer", "T", 3, ("Q",))]
    assert respecte_jalons(chemin, (Jalon("activer", "N", 1, "W"), Jalon("activer", "T", 3)))
    assert not respecte_jalons(chemin, (Jalon("activer", "T", 3), Jalon("activer", "N", 1)))
    assert not respecte_jalons(chemin, (Jalon("activer", "N", 1, "Z"),))


def test_guides_bien_formes():
    assert 5 <= len(GUIDES) <= 10
    for g in GUIDES:
        assert g.sources and g.jalons and g.cible.conditions
        assert all(s.date.startswith("2026-") and s.url.startswith("https://") for s in g.sources)
        assert 0 < g.etapes_realisables < len(g.etapes)   # chaque guide passe ensuite par une carte absente


# ── Avec la base de référence ──────────────────────────────────────────────────────────────────

@avec_base
def test_developper_rend_des_transitions_legales_et_rejouables(monde):
    deck, cat, _ = monde
    e = etat_depart(deck, ["Nadir Servant"], ["Ash Blossom & Joyous Spring"] * 2)
    m = Moteur(cat)
    issues, n = developper(m, e, Declaration("activer", "Nadir Servant", 1), FS)
    assert n >= len(issues) > 10
    for iss in issues[:5]:
        assert iss.resultat.verdict == "legal"
        res = m.jouer(e, iss.declaration, ScriptExploration(iss.reponses, FS))
        assert res.etat.empreinte() == iss.resultat.etat.empreinte()   # déterministe


@avec_base
def test_cartes_de_reponse_jamais_declarees(monde):
    deck, cat, _ = monde
    e = etat_depart(deck, ["Ash Blossom & Joyous Spring", "Aluber the Jester of Despia"])
    noms = {d.carte for d in declarations(e, cat, FS)}
    assert "Ash Blossom & Joyous Spring" not in noms and "Aluber the Jester of Despia" in noms


@avec_base
@pytest.mark.parametrize("gid", ["G1", "G4", "G5"])
def test_guides_courts_retrouves_avec_leur_sequence(monde, gid):
    deck, cat, _ = monde
    g = next(x for x in GUIDES if x.gid == gid)
    r = explorer(cat, etat_depart(deck, g.main_de_depart, g.hors_jeu), max_profondeur=10, max_secondes=30,
                 cible=g.cible, arreter_a_la_cible=True, strategie="cible", accepter=g.accepter)
    assert r.cibles_acceptees, f"{gid} non retrouvé ({r.arret}, {len(r.etats)} états)"


@avec_base
def test_largeur_epuise_une_petite_main_et_ecrit_les_requetes(monde, tmp_path):
    deck, cat, textes = monde
    e = etat_depart(deck, ["Fallen of Albaz"], ["Ash Blossom & Joyous Spring"] * 3)
    r = explorer(cat, e, max_profondeur=4, max_secondes=30)
    assert r.arret == "epuise" and r.finals and not r.non_couverts
    con = sqlite3.connect(tmp_path / "combos.db")
    appliquer_schema(con)
    for c in deck.cartes:
        enregistrer_carte(con, c, textes[c.card_id], set())
    enregistrer_deck(con, deck, "deck-branded-source.json")
    run = ouvrir_run(con, r, deck.ref, e)
    ecr = Ecrivain(con, cat, deck, r, run)
    finals = sorted(r.finals, key=lambda s: -r.profondeur[s])[:5]
    for sid in finals:
        ecr.combo(sid, "fin_volontaire", avec_fin=True)
    con.commit()
    assert con.execute("SELECT COUNT(*) FROM cb_combo").fetchone()[0] == len(finals)
    assert con.execute("SELECT COUNT(*) FROM cb_step_card").fetchone()[0] > 0
    # « tous les combos qui passent par X » et « A puis directement B » répondent sans erreur
    assert isinstance(combos_passant_par(con, "Fallen of Albaz"), list)
    assert isinstance(a_puis_directement_b(con, "Fallen of Albaz", "Fallen of Albaz"), list)
