"""Structures de l'état (definitions-et-schema.md § 2) : forme canonique, équivalence, validations."""

import pytest

from moteur_combos.modele import (
    CARTES_LISANT_LA_POSITION, COLONNE, FORMES_LIMITE, MOTIFS_ARRET, Cadre, CibleExploration, ConditionCible,
    Etat, Instance, LimiteConsommee, MemoireTour, Modification, OccupantZoneExtra, ZonesJoueur,
    verifier_motif_arret,
)

ALUBER = "Aluber the Jester of Despia"
TITAN = "Titaniklad the Ash Dragon"


def etat(main=(), cimetiere=(), cases=(), zme=(), memoire=None, cadre=None):
    return Etat(
        cadre=cadre or Cadre(),
        joueurs=(ZonesJoueur(main=tuple(main), cimetiere=tuple(cimetiere), cases=tuple(cases)),
                 ZonesJoueur(main_connue=False, deck_connu=False)),
        zones_monstre_extra=tuple(zme),
        memoire=memoire or MemoireTour(),
    )


def test_copies_interchangeables_ordre_sans_effet():
    """§ 2.3 point 1 et 2 : l'ordre des exemplaires d'un multi-ensemble ne change pas l'empreinte."""
    a, b = Instance("Mulcharmy Fuwalos"), Instance(ALUBER)
    assert etat(main=[a, b, a]).empreinte() == etat(main=[a, a, b]).empreinte()


def test_faux_jumeaux_correctement_invoque():
    """§ 2.1 test 1 : même Cimetière visible, drapeau « correctement invoqué » différent → deux états."""
    envoye = Instance(TITAN, venue_extra_deck=True, correctement_invoquee=False)
    invoque = Instance(TITAN, venue_extra_deck=True, correctement_invoquee=True)
    assert etat(cimetiere=[envoye]).empreinte() != etat(cimetiere=[invoque]).empreinte()


def test_case_exacte_compte():
    """D3 révisée : la case est toujours portée ; deux cases différentes → deux états."""
    m = Instance(ALUBER, face="visible")
    assert etat(cases=[("M1", m)]).empreinte() != etat(cases=[("M3", m)]).empreinte()
    titan = Instance(TITAN, face="visible", correctement_invoquee=True)
    en_zme = etat(zme=[OccupantZoneExtra("ZME_G", 0, titan)])
    en_principale = etat(cases=[("M2", titan)])
    assert en_zme.empreinte() != en_principale.empreinte()


def test_zone_monstre_extra_commune_et_validee():
    with pytest.raises(ValueError):
        ZonesJoueur(cases=(("ZME_G", Instance(TITAN)),))  # la ZME n'appartient pas à un joueur
    with pytest.raises(ValueError):
        OccupantZoneExtra("M1", 0, Instance(TITAN))
    with pytest.raises(ValueError):
        etat(zme=[OccupantZoneExtra("ZME_D", 0, Instance(TITAN)), OccupantZoneExtra("ZME_D", 1, Instance(TITAN))])
    assert COLONNE["ZME_G"] == 2 and COLONNE["ZME_D"] == 4


def test_deux_cartes_meme_case_refusees():
    with pytest.raises(ValueError):
        ZonesJoueur(cases=(("M1", Instance(ALUBER)), ("M1", Instance(ALUBER))))


def test_memoire_compte_dans_l_etat_pas_dans_le_plateau():
    """§ 2.3 : même plateau, verrou différent → deux états, un seul « plateau final »."""
    m = Instance(ALUBER, face="visible")
    sans = etat(cases=[("M1", m)])
    avec = etat(cases=[("M1", m)], memoire=MemoireTour(faits_libres=("verrou NADIR",)))
    assert sans.empreinte() != avec.empreinte()
    assert sans.empreinte_plateau() == avec.empreinte_plateau()


def test_trois_formes_de_limite_enregistrables():
    """Relecture 1 : par nom de carte, par effet et par nom, par exemplaire (+ deux variantes)."""
    assert {"activation_par_nom", "par_nom_effet", "par_exemplaire"} <= set(FORMES_LIMITE)
    LimiteConsommee("activation_par_nom", "Branded Fusion")
    LimiteConsommee("par_nom_effet", "Guiding Quem, the Virtuous", effet=2)
    LimiteConsommee("par_nom_carte", ALUBER)
    with pytest.raises(ValueError):
        LimiteConsommee("par_nom_effet", "Guiding Quem, the Virtuous")  # numéro d'effet manquant
    with pytest.raises(ValueError):
        LimiteConsommee("par_exemplaire", ALUBER)  # attribut de l'exemplaire, pas de la mémoire
    # La forme par exemplaire suit l'exemplaire : deux copies, l'une a consommé, l'autre non.
    a = Instance("Mirrorjade the Iceblade Dragon", limites_exemplaire=(1,))
    b = Instance("Mirrorjade the Iceblade Dragon")
    assert a.canon() != b.canon()


def test_limites_ordre_sans_effet():
    l1 = LimiteConsommee("activation_par_nom", "Branded Fusion")
    l2 = LimiteConsommee("par_nom_carte", ALUBER)
    assert etat(memoire=MemoireTour(limites=frozenset({l1, l2}))).empreinte() == \
        etat(memoire=MemoireTour(limites=frozenset({l2, l1}))).empreinte()


def test_historique_extra_deck_ordonne():
    """T12 : l'ordre des invocations depuis l'Extra Deck est gardé (une Synchro AVANT Branded Fusion)."""
    m1 = MemoireTour(invocations_extra=(("Ecclesia and the Dark Dragon", "synchro"), (TITAN, "fusion")))
    m2 = MemoireTour(invocations_extra=((TITAN, "fusion"), ("Ecclesia and the Dark Dragon", "synchro")))
    assert etat(memoire=m1).empreinte() != etat(memoire=m2).empreinte()


def test_nom_temporaire():
    coca = Instance("Cocatorium the Heavy Metal Avian",
                    modifications=(Modification("nom", "Tri-Brigade Mercourier", "phase_de_fin"),))
    assert coca.nom_courant() == "Tri-Brigade Mercourier"
    assert Instance(ALUBER).nom_courant() == ALUBER


def test_cadre_et_stabilite():
    with pytest.raises(ValueError):
        Cadre(phase="combat_imaginaire")
    with pytest.raises(ValueError):
        Cadre(tour=0)
    assert etat().est_stable()
    assert not etat(cadre=Cadre(chaine=("maillon 1",))).est_stable()


def test_cible_et_motifs_d_arret():
    """Relecture 1 : cible d'exploration et motif « boucle » (structure seulement)."""
    assert {"boucle", "cible_atteinte", "retour_etat_connu"} <= set(MOTIFS_ARRET)
    assert verifier_motif_arret("boucle") == "boucle"
    with pytest.raises(ValueError):
        verifier_motif_arret("plus_envie")
    cible = CibleExploration("Albion sur le terrain", (ConditionCible("terrain", "Albion the Sanctifire Dragon"),))
    assert '"minimum": 1' in cible.conditions_json()
    with pytest.raises(ValueError):
        CibleExploration("vide", ())
    with pytest.raises(ValueError):
        ConditionCible("extra", "Albion the Sanctifire Dragon")


def test_empreinte_stable_entre_deux_constructions():
    e1 = etat(main=[Instance(ALUBER)], cadre=Cadre(invocation_normale_utilisee=True))
    e2 = etat(main=[Instance(ALUBER)], cadre=Cadre(invocation_normale_utilisee=True))
    assert e1.empreinte() == e2.empreinte() and len(e1.empreinte()) == 64


def test_cartes_lisant_la_position_declarees():
    assert CARTES_LISANT_LA_POSITION == {"Sprind the Irondash Dragon", "Albion the Sanctifire Dragon"}
