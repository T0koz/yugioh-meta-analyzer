"""Enregistrement des explorations dans `combos.db` (lot C3) et les deux requêtes du ticket (§ 3.6 des définitions).

Schéma inchangé (`schema.sql`, version 1) : une exploration = `cb_run` ; un combo = `cb_combo` + `cb_combo_step` ; une
transition = `cb_transition` + ses pas (`cb_step`, `cb_step_card`) + relations dérivées (`cb_relation`). Un
micro-combo n'est pas stocké à part : c'est un segment contigu de `cb_combo_step` (§ 3.6).

**Ce qui est stocké (choix déclaré, décision par défaut du lot C3)** : pas tout le graphe (des centaines de milliers
d'arêtes), mais les chemins retenus — le chemin vers chaque état qui remplit la cible, et, pour un parcours en largeur,
un chemin le plus court par **plateau final distinct** (jusqu'à `max_combos`). Les états et transitions de ces chemins
sont écrits en entier, pas par pas ; les compteurs du parcours complet sont dans le rapport, pas en base.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter

from .base import maintenant
from .exploration import FILTRES_DISPONIBLES, VERSION_EXPLORATION, Arete, Rapport, ScriptExploration
from .regles import Moteur

TYPES_PAS = {"declarer": "declarer", "cout": "cout", "cibler": "cible", "cible": "cible", "enchainer": "enchainer",
             "resoudre": "resoudre", "choisir": "choisir", "placer": "placer", "ordonner": "ordonner",
             "hasard": "hasard"}
ROLES = {"acteur", "cout", "materiel", "cible", "choisie", "deplacee", "revelee", "condition"}
CELLULES = {"M1", "M2", "M3", "M4", "M5", "ZME_G", "ZME_D", "S1", "S2", "S3", "S4", "S5", "TERRAIN"}
VERSION_REGLES = "C2 (J1) + C3 étape 0 (N01, N04, N09), 2026-11-18"


def _state(con: sqlite3.Connection, etat) -> str:
    sid = etat.empreinte()
    con.execute("INSERT OR IGNORE INTO cb_state (state_id, canonical_json, turn, active_player, phase, is_stable, "
                "board_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sid, etat.json_canonique(), etat.cadre.tour, etat.cadre.joueur_actif, etat.cadre.phase,
                 int(etat.est_stable()), etat.empreinte_plateau()))
    return sid


def ouvrir_run(con, rapport: Rapport, deck_ref: str, depart, cible=None, mode="decklist",
               complement: dict | None = None) -> int:
    _state(con, depart)
    target_id = None
    if cible is not None:
        cur = con.execute("INSERT INTO cb_target (description, conditions_json, created_at) VALUES (?, ?, ?)",
                          (cible.description, cible.conditions_json(), maintenant()))
        target_id = cur.lastrowid
    filtres = {"filtres": {f: FILTRES_DISPONIBLES[f] for f in rapport.filtres},
               "strategie": rapport.strategie, **(complement or {})}
    cur = con.execute(
        "INSERT INTO cb_run (mode, deck_ref, start_state, target_id, max_depth, columns_enumerated, filters_json, "
        "rules_version, engine_version, complete, started_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)",
        (mode, deck_ref, depart.empreinte(), target_id, rapport.max_profondeur,
         json.dumps(filtres, ensure_ascii=False), VERSION_REGLES, VERSION_EXPLORATION, int(rapport.complete),
         maintenant()))
    return cur.lastrowid


class Ecrivain:
    """Écrit les chemins d'un rapport. Rejoue chaque transition (déterministe) pour retrouver ses pas."""

    def __init__(self, con: sqlite3.Connection, cat, deck, rapport: Rapport, run_id: int):
        self.con, self.cat, self.rapport, self.run_id = con, cat, rapport, run_id
        self.ids = {c.nom: c.card_id for c in deck.cartes}
        self.moteur = Moteur(cat)
        self.transitions: dict[tuple, int] = {}
        self.fs = frozenset(rapport.filtres)

    def _transition(self, a: Arete) -> int:
        cle = (a.source, a.cible, a.declaration, a.reponses)
        if cle in self.transitions:
            return self.transitions[cle]
        etat = self.rapport.etats[a.source]
        res = self.moteur.jouer(etat, a.declaration, ScriptExploration(a.reponses, self.fs))
        if res.verdict != "legal":
            raise RuntimeError(f"rejeu non conforme : {a.declaration} {a.reponses} → {res.verdict} {res.raison}")
        _state(self.con, etat)
        arrivee = etat if a.declaration.type == "fin_de_tour" else res.etat
        to = _state(self.con, arrivee)
        acteur = self.ids.get(a.declaration.carte)
        cur = self.con.execute(
            "INSERT INTO cb_transition (run_id, from_state, to_state, action_type, actor_card_id, actor_effect, "
            "is_random, stop_reason, verified) VALUES (?, ?, ?, ?, ?, NULL, ?, NULL, 0)",
            (self.run_id, a.source, to, a.declaration.type, acteur,
             int(any(p.type == "hasard" for p in res.pas))))
        tid = cur.lastrowid
        relations = set()
        for k, p in enumerate(res.pas, start=1):
            cur = self.con.execute(
                "INSERT INTO cb_step (transition_id, position, step_type, chain_link, effect_id, option) "
                "VALUES (?, ?, ?, NULL, NULL, ?)", (tid, k, TYPES_PAS.get(p.type, "resoudre"), p.libelle[:300]))
            step_id = cur.lastrowid
            copies: Counter = Counter()
            for carte, role, dep, arr, cellule in p.cartes:
                cid = self.ids.get(carte)
                if cid is None:
                    continue
                role = role if role in ROLES else "deplacee"
                copies[(cid, role)] += 1
                self.con.execute(
                    "INSERT INTO cb_step_card (step_id, card_id, copy_index, role, from_zone, to_zone, to_cell) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (step_id, cid, copies[(cid, role)], role, dep, arr, cellule if cellule in CELLULES else None))
                if acteur is not None and cid != acteur and role != "acteur":
                    famille = "materiel_ou_cout" if role in ("materiel", "cout") else "deplace"
                    relations.add((acteur, cid, famille))
            if p.type == "enchainer":
                self.con.execute("INSERT INTO cb_window (step_id, window_type, response) VALUES (?, ?, 'aucune')",
                                 (step_id, "reponse_activation"))
        for src, tgt, fam in sorted(relations):
            self.con.execute("INSERT OR IGNORE INTO cb_relation (transition_id, source_card, target_card, family) "
                             "VALUES (?, ?, ?, ?)", (tid, src, tgt, fam))
        self.transitions[cle] = tid
        return tid

    def combo(self, etat_id: str, motif: str, avec_fin: bool = False) -> int:
        chemin = self.rapport.chemin(etat_id)
        if avec_fin and etat_id in self.rapport.fin_aretes:
            chemin = chemin + [self.rapport.fin_aretes[etat_id]]
        tids = [(self._transition(a), self.ids.get(a.declaration.carte)) for a in chemin]
        cur = self.con.execute(
            "INSERT INTO cb_combo (run_id, final_state, length, label, stop_reason) VALUES (?, ?, ?, 'non_verifie', ?)",
            (self.run_id, etat_id, len(tids), motif))
        cid = cur.lastrowid
        for k, (tid, acteur) in enumerate(tids, start=1):
            self.con.execute("INSERT INTO cb_combo_step (combo_id, position, transition_id, actor_card_id) "
                             "VALUES (?, ?, ?, ?)", (cid, k, tid, acteur))
        return cid


# ── Les requêtes du ticket (§ 3.6) ─────────────────────────────────────────────────────────────

def _id(con, nom: str) -> int:
    row = con.execute("SELECT card_id FROM cb_card WHERE name = ?", (nom,)).fetchone()
    if row is None:
        raise KeyError(f"carte inconnue de combos.db : {nom}")
    return row[0]


def combos_passant_par(con, nom: str, run_id: int | None = None) -> list[int]:
    """Tous les combos où la carte X joue un rôle quelconque (jouée, matériel, coût, choisie, déplacée)."""
    sql = ("SELECT DISTINCT cs.combo_id FROM cb_combo_step cs JOIN cb_step s ON s.transition_id = cs.transition_id "
           "JOIN cb_step_card sc ON sc.step_id = s.step_id JOIN cb_combo c ON c.combo_id = cs.combo_id "
           "WHERE sc.card_id = ?" + (" AND c.run_id = ?" if run_id else "") + " ORDER BY cs.combo_id")
    return [r[0] for r in con.execute(sql, (_id(con, nom),) + ((run_id,) if run_id else ()))]


def a_puis_directement_b(con, a: str, b: str, run_id: int | None = None) -> list[tuple[int, int]]:
    """(combo, position) où la carte A est jouée, puis la carte B à la transition suivante."""
    sql = ("SELECT x.combo_id, x.position FROM cb_combo_step x JOIN cb_combo_step y "
           "ON y.combo_id = x.combo_id AND y.position = x.position + 1 JOIN cb_combo c ON c.combo_id = x.combo_id "
           "WHERE x.actor_card_id = ? AND y.actor_card_id = ?" + (" AND c.run_id = ?" if run_id else "")
           + " ORDER BY x.combo_id, x.position")
    return [tuple(r) for r in con.execute(sql, (_id(con, a), _id(con, b)) + ((run_id,) if run_id else ()))]


def lire_combo(con, combo_id: int) -> list[str]:
    """Les transitions d'un combo, lisibles : « type carte »."""
    rows = con.execute(
        "SELECT cs.position, t.action_type, c.name FROM cb_combo_step cs JOIN cb_transition t "
        "ON t.transition_id = cs.transition_id LEFT JOIN cb_card c ON c.card_id = t.actor_card_id "
        "WHERE cs.combo_id = ? ORDER BY cs.position", (combo_id,))
    return [f"{p}. {t} {n or ''}".strip() for p, t, n in rows]
