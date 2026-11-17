"""Schéma SQLite de combos.db : création idempotente, contraintes, garde-fous."""

import sqlite3

import pytest

from moteur_combos.base import SCHEMA_VERSION, ouvrir_combos, ouvrir_reference

TABLES = {
    "cb_card", "cb_card_name_tag", "cb_effect", "cb_effect_limit", "cb_deck", "cb_deck_card", "cb_state",
    "cb_target", "cb_run", "cb_transition", "cb_step", "cb_step_card", "cb_window", "cb_condition",
    "cb_transition_condition", "cb_relation", "cb_combo", "cb_combo_step", "cb_test_situation",
}
SHA = "a" * 64


@pytest.fixture
def con(tmp_path):
    c = ouvrir_combos(tmp_path / "combos.db")
    yield c
    c.close()


def test_tables_et_version(con):
    noms = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert TABLES <= noms
    assert all(n.startswith("cb_") for n in noms)
    assert con.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_schema_idempotent(tmp_path):
    ouvrir_combos(tmp_path / "combos.db").close()
    ouvrir_combos(tmp_path / "combos.db").close()  # ne lève pas


def test_refuse_les_bases_du_projet(tmp_path):
    for nom in ("yugioh.db", "serving.db"):
        with pytest.raises(ValueError):
            ouvrir_combos(tmp_path / nom)
    assert not (tmp_path / "yugioh.db").exists()


def test_reference_en_lecture_seule(tmp_path):
    chemin = tmp_path / "ref.db"
    sqlite3.connect(chemin).execute("CREATE TABLE t (x)").connection.commit()
    con = ouvrir_reference(chemin)
    with pytest.raises(sqlite3.OperationalError):
        con.execute("INSERT INTO t VALUES (1)")
    con.close()
    with pytest.raises(FileNotFoundError):
        ouvrir_reference(tmp_path / "absente.db")


def _etat(con, state_id=SHA):
    con.execute("INSERT INTO cb_state VALUES (?, '{}', 1, 0, 'principale_1', 1, NULL)", (state_id,))


def _run(con, **kw):
    valeurs = dict(mode="absolu", deck_ref=None, start_state=SHA, target_id=None, max_depth=10,
                   columns_enumerated=0, filters_json="{}", rules_version="test", engine_version="0",
                   complete=1, started_at="2026-11-18")
    valeurs.update(kw)
    con.execute(
        "INSERT INTO cb_run (mode, deck_ref, start_state, target_id, max_depth, columns_enumerated, filters_json,"
        " rules_version, engine_version, complete, started_at) VALUES (:mode, :deck_ref, :start_state, :target_id,"
        " :max_depth, :columns_enumerated, :filters_json, :rules_version, :engine_version, :complete, :started_at)",
        valeurs,
    )
    return con.execute("SELECT last_insert_rowid()").fetchone()[0]


def test_motifs_d_arret_boucle_et_cible(con):
    _etat(con)
    run = _run(con)
    for motif in ("boucle", "cible_atteinte", "retour_etat_connu", None):
        con.execute("INSERT INTO cb_transition (run_id, from_state, to_state, action_type, stop_reason, verified)"
                    " VALUES (?, ?, ?, 'phase', ?, 0)", (run, SHA, SHA, motif))
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO cb_transition (run_id, from_state, to_state, action_type, stop_reason, verified)"
                    " VALUES (?, ?, ?, 'phase', 'abandon', 0)", (run, SHA, SHA))


def test_cible_d_exploration_rattachee_au_run(con):
    _etat(con)
    con.execute("INSERT INTO cb_target (description, conditions_json, created_at) VALUES"
                " ('Albion', '[{\"zone\":\"terrain\",\"carte\":\"Albion the Sanctifire Dragon\",\"minimum\":1}]', 'x')")
    _run(con, target_id=1)
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO cb_target (description, conditions_json, created_at) VALUES ('x', 'pas du json', 'x')")
    with pytest.raises(sqlite3.IntegrityError):
        _run(con, target_id=99)  # clé étrangère


def test_mode_decklist_demande_un_deck(con):
    _etat(con)
    with pytest.raises(sqlite3.IntegrityError):
        _run(con, mode="decklist", deck_ref=None)


def test_case_d_arrivee_et_option_de_placement(con):
    _etat(con)
    run = _run(con)
    con.execute("INSERT INTO cb_card (card_id, name, text, text_sha256, text_fetched, updated_at)"
                " VALUES (1, 'Carte', 't', ?, 'x', 'x')", (SHA,))
    con.execute("INSERT INTO cb_transition (run_id, from_state, to_state, action_type, verified)"
                " VALUES (?, ?, ?, 'activation', 0)", (run, SHA, SHA))
    con.execute("INSERT INTO cb_step (transition_id, position, step_type, option) VALUES (1, 1, 'placer',"
                " 'zone_monstre_extra')")
    con.execute("INSERT INTO cb_step_card VALUES (1, 1, 'deplacee', 'extra', 'terrain', 'ZME_G')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO cb_step_card VALUES (1, 1, 'acteur', 'extra', 'terrain', 'M6')")


def test_limites_d_effet(con):
    con.execute("INSERT INTO cb_card (card_id, name, text, text_sha256, text_fetched, updated_at)"
                " VALUES (1, 'Carte', 't', ?, 'x', 'x')", (SHA,))
    con.execute("INSERT INTO cb_effect (card_id, position, kind, optional, text_span, status)"
                " VALUES (1, 1, 'ignition', 1, 't', 'brouillon')")
    con.execute("INSERT INTO cb_effect_limit VALUES (1, 'par_nom_effet', 'Carte', 't')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO cb_effect_limit VALUES (1, 'par_exemplaire', 'Carte', 't')")  # sans nom
    con.execute("INSERT INTO cb_effect_limit VALUES (1, 'par_exemplaire', NULL, 't')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO cb_effect_limit VALUES (1, 'deux_fois', 'Carte', 't')")


def test_statut_de_formalisation(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO cb_card (card_id, name, text, text_sha256, text_fetched, status, updated_at)"
                    " VALUES (2, 'X', 't', ?, 'x', 'presque', 'x')", (SHA,))
