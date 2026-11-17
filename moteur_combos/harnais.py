"""Harnais du jeu de tests Branded (lot 18) : tout ce qui s'exécute sans règle de jeu.

    python scripts/combos_harnais.py            # rapport + écriture dans data/combos.db
    python scripts/combos_harnais.py --detail   # une ligne par test
    python scripts/combos_harnais.py --sans-base-reference   # sans yugioh.db (textes non lus)

Étapes :
1. deck source : chargement, textes lus en lecture seule dans yugioh.db, empreintes `text_sha256`,
   noms et archétypes, validité (3 par nom, « always treated as » compris), clauses « per turn » ;
2. jeu de tests : alias, identifiants, verdicts, cohérence avec le tableau des points de règle ;
3. pour chaque situation : état de départ construit (zones, deck, Extra Deck), empreinte, classe ;
4. verdicts vérifiables sans règle : seulement « non couvert » (D5 : action sur une carte dont le
   statut n'est ni `formalisee` ni `verifiee`). Les autres attendent la tranche 0 : ce n'est pas un échec.

Code de sortie : 0 si tout ce qui est structurel passe, 1 sinon.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from . import chemins
from .base import maintenant, ouvrir_combos, ouvrir_reference
from .classement import CLASSES, classer, ecarts_croises, lire_points, regles_precisees
from .deck import (
    analyser_limites, charger_deck, controle_validite, enregistrer_carte, enregistrer_deck, etiquettes,
    lire_textes, tous_les_noms, verifier_empreintes, vocabulaire_archetypes,
)
from .modele import STATUTS_EXECUTABLES
from .situations import cartes_citees, charger_tests, construire_depart, verifier_jeu


@dataclass
class LigneTest:
    test_id: str
    perimetre: str
    regles: list[str]
    classe: str
    raison: str
    attendu: str
    depart_valide: bool
    depart_complet: bool
    faits_libres: list[str]
    erreurs: list[str]
    etat_id: str | None
    statut: str


@dataclass
class Rapport:
    echecs: list[str] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)
    lignes: list[LigneTest] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)

    def echec(self, titre: str, details: list[str]) -> None:
        self.echecs.append(titre)
        print(f"  ✗ {titre}")
        for d in details[:40]:
            print(f"      {d}")

    def ok(self, msg: str) -> None:
        print(f"  ✓ {msg}")

    def avert(self, msg: str) -> None:
        self.avertissements.append(msg)
        print(f"  ⚠ {msg}")


def executer(base_combos: Path | None, base_ref: Path | None, detail: bool = False,
             sortie_json: Path | None = None) -> Rapport:
    r = Rapport()

    # ── 1. Deck source ─────────────────────────────────────────────────────────────────────────
    print("▶ Deck source")
    deck = charger_deck(chemins.DECK_SOURCE)
    r.ok(f"{deck.ref} : {deck.total('main')} Main, {deck.total('extra')} Extra, {deck.total('side')} Side, "
         f"{len(deck.cartes)} cartes distinctes")
    textes = {}
    noms_base: set[str] | None = None
    if base_ref is not None:
        con_ref = ouvrir_reference(base_ref)
        try:
            textes = lire_textes(con_ref, [c.card_id for c in deck.cartes])
            noms_base = tous_les_noms(con_ref)
        finally:
            con_ref.close()
        ecarts = verifier_empreintes(deck, textes)
        if ecarts:
            r.echec("empreintes text_sha256 différentes du texte lu (errata ?)", ecarts)
        else:
            r.ok(f"{len(textes)} textes lus en lecture seule, empreintes identiques au fichier source")
    else:
        r.avert("base de référence non lue : empreintes, archétypes et clauses non vérifiés")

    noms_portes: dict[str, set[str]] = {c.nom: {c.nom} for c in deck.cartes}
    tags_par_carte: dict[str, set] = {}
    if textes:
        vocab = vocabulaire_archetypes([t.texte for t in textes.values()], noms_base or set())
        r.ok(f"archétypes cités par les textes : {', '.join(sorted(vocab))}")
        for c in deck.cartes:
            tags = etiquettes(c.nom, textes[c.card_id].texte, vocab)
            tags_par_carte[c.nom] = tags
            noms_portes[c.nom] = {t for t, k, _ in tags if k == "nom"}
        partages = {c.nom: sorted(noms_portes[c.nom] - {c.nom}) for c in deck.cartes if noms_portes[c.nom] - {c.nom}}
        for nom, autres in partages.items():
            r.ok(f"nom partagé : {nom} porte aussi {', '.join(autres)}")
    violations = controle_validite(deck, noms_portes)
    if violations:
        r.echec("deck invalide", violations)
    else:
        r.ok("deck valide : 40 à 60 / 15 / 15, 3 au plus par nom (« always treated as » compris), banlist")

    if textes:
        formes: Counter[str] = Counter()
        non_reconnues, noms_differents = [], []
        for c in deck.cartes:
            a = analyser_limites(c.nom, textes[c.card_id].texte)
            formes.update(f for f, _ in a.clauses)
            non_reconnues += [f"{c.nom} : « {p[:90]} »" for p in a.non_reconnues]
            noms_differents += [f"{c.nom} cite « {n} »" for n in a.nom_different]
        r.ok("clauses « per turn » : " + ", ".join(f"{f} {n}" for f, n in sorted(formes.items())))
        if non_reconnues:
            r.echec("clause « per turn » qu'aucune forme du schéma ne représente", non_reconnues)
        for n in noms_differents:
            r.avert(f"clause au nom différent du nom imprimé (anomalie connue de la source) : {n}")

    # ── 2. Jeu de tests ────────────────────────────────────────────────────────────────────────
    print("\n▶ Jeu de tests (alias, identifiants, verdicts, points de règle)")
    jeu = charger_tests(chemins.TESTS_YAML)
    erreurs = verifier_jeu(jeu, deck, noms_base)
    if erreurs:
        r.echec("tests-branded.yaml incohérent", erreurs)
    else:
        r.ok(f"{len(jeu.situations)} situations, {len(jeu.alias)} alias tous présents dans le deck source")
    points = lire_points(chemins.POINTS_DE_REGLE)
    r.ok(f"{len(points)} points de règle lus ({sum(p.confirme for p in points.values())} confirmés, "
         f"un seul avis : {', '.join(sorted(n for n, p in points.items() if p.un_seul_avis))})")
    for e in ecarts_croises(jeu.situations, points):
        r.avert(f"YAML et tableau des points diffèrent : {e}")

    # ── 3. Départs et classement ───────────────────────────────────────────────────────────────
    print("\n▶ États de départ et classement des situations")
    con = ouvrir_combos(base_combos) if base_combos is not None else None
    statut_carte: dict[str, str] = {}
    try:
        if con is not None:
            if textes:
                for c in deck.cartes:
                    enregistrer_carte(con, c, textes[c.card_id], tags_par_carte[c.nom])
                enregistrer_deck(con, deck, str(chemins.DECK_SOURCE.relative_to(chemins.ROOT)))
                statut_carte = {row["name"]: row["status"] for row in con.execute("SELECT name, status FROM cb_card")}
            elif con.execute("SELECT COUNT(*) FROM cb_deck WHERE deck_ref = ?", (deck.ref,)).fetchone()[0] == 0:
                r.avert("combos.db sans deck chargé et base de référence absente : rien n'est écrit")
                con.close()
                con = None
            else:
                statut_carte = {row["name"]: row["status"] for row in con.execute("SELECT name, status FROM cb_card")}

        for s in jeu.situations:
            r.lignes.append(_traiter(s, jeu, deck, points, statut_carte, con))
        if con is not None:
            con.commit()
    finally:
        if con is not None:
            con.close()

    invalides = [f"{lt.test_id} : {'; '.join(lt.erreurs)}" for lt in r.lignes if not lt.depart_valide]
    if invalides:
        r.echec("départs impossibles à construire", invalides)
    else:
        partiels = [lt for lt in r.lignes if not lt.depart_complet]
        r.ok(f"{len(r.lignes)} départs construits ; {len(r.lignes) - len(partiels)} complets, {len(partiels)} "
             f"partiels (faits en texte libre, à formaliser en tranche 0)")
    echecs_verdict = [lt.test_id for lt in r.lignes if lt.statut == "echec"]
    if echecs_verdict:
        r.echec("verdict vérifiable sans règle, mais différent de l'attendu", echecs_verdict)
    verifies = [lt.test_id for lt in r.lignes if lt.statut == "verifie"]
    r.ok(f"verdicts vérifiés sans règle de jeu : {', '.join(verifies) or 'aucun'} ; "
         f"{sum(lt.statut == 'en_attente_tranche_0' for lt in r.lignes)} en attente de la tranche 0")
    if len({lt.test_id for lt in r.lignes}) != len(jeu.situations):
        r.echec("situations non classées", [])

    if detail:
        print("\n  Test  Classe                      Départ           Statut                Règles")
        for lt in r.lignes:
            depart = "invalide" if not lt.depart_valide else ("complet" if lt.depart_complet
                                                               else f"partiel ({len(lt.faits_libres)})")
            print(f"  {lt.test_id:<5} {lt.classe:<27} {depart:<16} {lt.statut:<21} {', '.join(lt.regles) or '—'}")

    print("\n▶ Classement des 72 situations")
    compte = Counter(lt.classe for lt in r.lignes)
    for c in CLASSES:
        ids = [lt.test_id for lt in r.lignes if lt.classe == c]
        print(f"  {c:<27} {compte[c]:>3}   {' '.join(ids)}")
    print(f"  {'total':<27} {sum(compte.values()):>3}")

    if sortie_json is not None:
        sortie_json.write_text(json.dumps(
            {"classes": dict(compte), "tests": [lt.__dict__ for lt in r.lignes],
             "echecs": r.echecs, "avertissements": r.avertissements},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return r


def _traiter(s: dict, jeu, deck, points, statut_carte: dict[str, str], con: sqlite3.Connection | None) -> LigneTest:
    depart = construire_depart(s, jeu, deck)
    attendu = s["attendu"]["verdict"]
    # Verdict vérifiable sans règle : « non couvert » (D5, niveau 1). Si une carte citée dans l'action
    # n'est pas exécutable, la seule réponse permise au moteur est « non couvert ».
    citees = [jeu.alias[a] for a in cartes_citees(s.get("action", ""), jeu.alias)]
    non_couvertes = [n for n in citees if statut_carte.get(n, "non_traitee") not in STATUTS_EXECUTABLES]
    verifiable = attendu == "non_couvert"
    if not depart.valide:
        statut = "depart_invalide"
    elif verifiable:
        statut = "verifie" if non_couvertes else "echec"
    else:
        statut = "en_attente_tranche_0"
    classe, raison = classer(s, points, verifiable_sans_regles=verifiable and statut == "verifie")
    regles = regles_precisees(s)
    etat_id = depart.etat.empreinte() if depart.etat is not None else None
    if con is not None:
        if depart.etat is not None:
            e = depart.etat
            con.execute(
                "INSERT OR IGNORE INTO cb_state (state_id, canonical_json, turn, active_player, phase, is_stable,"
                " board_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (etat_id, e.json_canonique(), e.cadre.tour, e.cadre.joueur_actif, e.cadre.phase,
                 int(e.est_stable()), e.empreinte_plateau()),
            )
        con.execute(
            "INSERT OR REPLACE INTO cb_test_situation (test_id, yaml_sha256, deck_ref, perimetre, rules_json, classe,"
            " start_state, start_complete, free_facts_json, expected, status, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (s["id"], jeu.sha256, deck.ref, s["perimetre"], json.dumps(regles), classe, etat_id,
             int(depart.complet), json.dumps(depart.faits_libres, ensure_ascii=False), attendu, statut, maintenant()),
        )
    return LigneTest(
        test_id=s["id"], perimetre=s["perimetre"], regles=regles, classe=classe, raison=raison, attendu=attendu,
        depart_valide=depart.valide, depart_complet=depart.complet, faits_libres=depart.faits_libres,
        erreurs=depart.erreurs, etat_id=etat_id, statut=statut,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Harnais du jeu de tests Branded (moteur de combos, lot 18)")
    parser.add_argument("--base", type=Path, default=chemins.COMBOS_DB, help="combos.db à écrire")
    parser.add_argument("--reference", type=Path, default=None, help="yugioh.db à lire (mode=ro)")
    parser.add_argument("--sans-base-reference", action="store_true", help="ne pas lire yugioh.db")
    parser.add_argument("--sans-ecriture", action="store_true", help="ne rien écrire dans combos.db")
    parser.add_argument("--detail", action="store_true", help="une ligne par situation")
    parser.add_argument("--json", type=Path, default=None, help="écrit aussi le rapport en JSON")
    args = parser.parse_args(argv)

    base_ref = None
    if not args.sans_base_reference:
        base_ref = args.reference or chemins.base_de_reference()
        if not base_ref.exists():
            print(f"✗ base de référence introuvable : {base_ref} (YGO_DB_PATH, ou --sans-base-reference)")
            return 1
    rapport = executer(None if args.sans_ecriture else args.base, base_ref, args.detail, args.json)
    print()
    for a in rapport.avertissements:
        print(f"⚠ {a}")
    if rapport.echecs:
        print(f"✗ {len(rapport.echecs)} échec(s) : {', '.join(rapport.echecs)}")
        return 1
    print("✓ Harnais : tout ce qui est structurel passe (aucune règle de jeu exécutée).")
    if not args.sans_ecriture:
        print(f"  Écrit dans {args.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
