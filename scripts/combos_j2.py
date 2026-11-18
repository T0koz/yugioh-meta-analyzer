#!/usr/bin/env python3
"""Jalon J2 (lot C3, TOK-119) : le moteur retrouve-t-il seul les combos des guides publics ?

Pour chaque combo relevé (`moteur_combos/guides.py`, détail dans `docs/moteur-combos/combos-guides.md`) :
1. **recherche dirigée** : exploration « meilleur d'abord » vers la cible (plateau atteint à la dernière étape
   réalisable avec la liste), bornée en profondeur et en temps ; arrêt à la première fois que la cible est remplie ;
2. **parcours en largeur sans cible** (contrôle) : la cible est-elle atteinte quand le moteur n'a aucune indication,
   dans le même budget ?
Puis des **mains réalistes** tirées au hasard (graine fixée) : parcours en largeur borné, nombre d'états, de plateaux
finaux distincts, temps, branches « non couvert ».

Écrit dans `data/combos.db` (jamais `yugioh.db`) : runs, chemins retenus (combos), transitions, pas, relations.
Le harnais (`scripts/combos_harnais.py`) doit avoir tourné une fois avant (tables `cb_card` et `cb_deck`).

Lot J2 plein (TOK-140, jalon n°5) : 10 combos (G1-G5 du lot C3, G6-G10 figés par TOK-139) ; pour G6-G10 la cible
est évaluée en fin de tour (`combos-guides.md` § 5.2). Pour chaque combo, un essai de plus avec la **main réelle de
5 cartes** (cartes de départ + les cartes de réponse que le combo « à une carte » retire du jeu) : même cible, mêmes
jalons ; on note si le moteur se sert des cartes de réponse. Les séquences brutes (déclaration + réponses) sont dans
le JSON, pour `scripts/combos_export_oracle.py`.

Usage : python scripts/combos_j2.py [--secondes 120] [--largeur 60] [--mains 5] [--json sortie.json] [--sans-ecriture]
        [--guides G6,G7] [--sans-main-reelle]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from moteur_combos import chemins  # noqa: E402
from moteur_combos.base import ouvrir_combos, ouvrir_reference  # noqa: E402
from moteur_combos.cartes import FORMALISATIONS  # noqa: E402
from moteur_combos.catalogue import construire_catalogue  # noqa: E402
from moteur_combos.deck import charger_deck, lire_textes, tous_les_noms  # noqa: E402
from moteur_combos.exploration import FILTRES_PAR_DEFAUT, etat_depart, explorer, parties_au_hasard  # noqa: E402
from moteur_combos.guides import G6_FIGE, TOUS_LES_GUIDES, jalons_restants  # noqa: E402
from moteur_combos.stockage_combos import (  # noqa: E402
    Ecrivain, a_puis_directement_b, combos_passant_par, lire_combo, ouvrir_run,
)

GRAINE_MAINS = 20261118


def charger():
    deck = charger_deck(chemins.DECK_SOURCE)
    con = ouvrir_reference(chemins.base_de_reference())
    try:
        cat = construire_catalogue(deck, lire_textes(con, [c.card_id for c in deck.cartes]), tous_les_noms(con),
                                   FORMALISATIONS)
    finally:
        con.close()
    return deck, cat


def chemin_lisible(r, sid: str) -> list[str]:
    out = []
    for a in r.chemin(sid):
        d = a.declaration
        quoi = {"invocation_normale": "Invocation Normale", "activer": f"activer (effet {d.effet})",
                "invocation_synchro": "Invocation Synchro", "invocation_procedure": "Invocation par procédure",
                "phase_de_fin": "Phase de Fin", "fin_de_tour": "fin du tour"}.get(d.type, d.type)
        carte = "" if d.carte == "—" else f" {d.carte}"
        choix = [x for x in a.reponses if x not in ("passer", "attaque")]
        out.append(f"{quoi}{carte}" + (f" [{' ; '.join(choix)}]" if choix else ""))
    return out


def brut(r, sid: str) -> list[dict]:
    """Séquence rejouable : déclaration et réponses du script, transition par transition."""
    return [{"type": a.declaration.type, "carte": a.declaration.carte, "effet": a.declaration.effet,
             "reponses": list(a.reponses)} for a in r.chemin(sid)]


def resume(r) -> dict:
    return {"etats": len(r.etats), "aretes": r.aretes, "retours": r.retours, "rejouees": r.rejouees,
            "plateaux_finaux": len(set(r.finals.values())), "etats_finaux": len(r.finals),
            "profondeur_max_atteinte": max(r.profondeur.values()) if r.profondeur else 0,
            "non_couverts": sum(r.non_couverts.values()), "raisons_non_couvert": dict(r.non_couverts.most_common(5)),
            "hors_perimetre": sum(r.hors_perimetre.values()), "tronques": r.tronques,
            "non_developpes": r.non_developpes, "arret": r.arret, "complete": r.complete,
            "secondes": round(r.secondes, 2)}


def mains_realistes(deck, n: int) -> list[list[str]]:
    rng = random.Random(GRAINE_MAINS)
    paquet = sorted(c.nom for c in deck.cartes if c.zone == "main" for _ in range(c.nombre))
    return [sorted(rng.sample(paquet, 5)) for _ in range(n)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--secondes", type=float, default=120.0, help="budget de la recherche dirigée, par combo")
    ap.add_argument("--largeur", type=float, default=60.0, help="budget du parcours en largeur, par combo et par main")
    ap.add_argument("--profondeur", type=int, default=16, help="profondeur maximale (transitions)")
    ap.add_argument("--mains", type=int, default=5, help="nombre de mains réalistes tirées au hasard")
    ap.add_argument("--max-combos", type=int, default=200, help="combos écrits par parcours en largeur")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--sans-ecriture", action="store_true")
    ap.add_argument("--guides", default="", help="sous-ensemble, ex. G1,G3")
    ap.add_argument("--sans-main-reelle", action="store_true", help="pas d'essai avec la main réelle de 5 cartes")
    ap.add_argument("--sans-hasard", action="store_true", help="pas de joueur au hasard (passage à budget long)")
    ap.add_argument("--sans-largeur", action="store_true", help="recherche dirigée seulement")
    ap.add_argument("--avec-g6-fige", action="store_true", help="ajoute G6 avec sa cible figée (avant correction)")
    ap.add_argument("--max-etats", type=int, default=200_000, help="borne du nombre d'états par exploration")
    ap.add_argument("--guidee", action="store_true",
                    help="diagnostic HORS J2 : recherche dirigée guidée par les jalons du guide (« guidée par la solution »)")
    ap.add_argument("--largeur-sans-filtres", action="store_true",
                    help="base naïve plus forte : parcours en largeur sans les filtres D4, même budget")
    args = ap.parse_args(argv)

    deck, cat = charger()
    con = None if args.sans_ecriture else ouvrir_combos(chemins.COMBOS_DB)
    if con is not None and con.execute("SELECT COUNT(*) FROM cb_card").fetchone()[0] == 0:
        print("✗ combos.db n'a pas de cartes : lancer d'abord python scripts/combos_harnais.py")
        return 1
    sortie = {"filtres": list(FILTRES_PAR_DEFAUT), "guides": [], "mains": [], "requetes": {}}
    choisis = {g.strip() for g in args.guides.split(",") if g.strip()}

    print("▶ Combos des guides")
    liste = TOUS_LES_GUIDES + ((G6_FIGE,) if args.avec_g6_fige else ())
    for g in liste:
        if choisis and g.gid not in choisis and not (g is G6_FIGE and args.avec_g6_fige):
            continue
        accepter = g.accepteur(cat)
        depart = etat_depart(deck, g.main_de_depart, g.hors_jeu)
        ligne = {"id": g.gid, "lot": g.lot, "titre": g.titre, "main": g.main_de_depart, "hors_jeu": g.hors_jeu,
                 "cible": g.cible.description, "en_fin_de_tour": g.en_fin_de_tour,
                 "sources": [s.__dict__ for s in g.sources], "substitutions": list(g.substitutions),
                 "etapes_guide": len(g.etapes), "etapes_realisables": g.etapes_realisables}
        essais = [("guidee" if args.guidee else "dirigee", "cible", args.secondes, depart)]
        if not args.sans_largeur:
            essais.append(("largeur", "largeur", args.largeur, depart))
        if args.largeur_sans_filtres:
            essais.append(("largeur_sans_filtres", "largeur", args.largeur, depart))
        if not args.sans_main_reelle and g.hors_jeu:
            reelle = etat_depart(deck, g.main_de_depart + g.hors_jeu)
            ligne["main_reelle"] = g.main_de_depart + g.hors_jeu
            essais.append(("reelle_dirigee", "cible", args.secondes, reelle))
            if not args.sans_largeur:
                essais.append(("reelle_largeur", "largeur", args.largeur, reelle))
        for nom, strat, budget, dep in essais:
            t_cpu = time.process_time()
            r = explorer(cat, dep, max_profondeur=args.profondeur, max_secondes=budget, cible=g.cible,
                         arreter_a_la_cible=True, strategie=strat, accepter=accepter, max_etats=args.max_etats,
                         filtres=() if nom == "largeur_sans_filtres" else FILTRES_PAR_DEFAUT,
                         priorite=(lambda rr, s: jalons_restants(rr.chemin(s), g.jalons, rr.etats))
                         if nom == "guidee" else None)
            info = resume(r) | {"plateau": bool(r.cibles_atteintes), "sequence": bool(r.cibles_acceptees),
                                "secondes_cpu": round(time.process_time() - t_cpu, 1)}
            if r.cibles_atteintes:
                sid = r.cibles_atteintes[0]
                info["chemin_plateau"] = chemin_lisible(r, sid)
                info["longueur_plateau"] = len(r.chemin(sid))
            if r.cibles_acceptees:
                sid = r.cibles_acceptees[0]
                info["chemin_sequence"] = chemin_lisible(r, sid)
                info["longueur_sequence"] = len(r.chemin(sid))
                info["brut_sequence"] = brut(r, sid)
                if nom.startswith("reelle"):
                    fin = Counter(i.carte for i in r.etats[sid].joueurs[0].main)
                    info["cartes_de_reponse_utilisees"] = sorted((Counter(g.hors_jeu) - fin).elements())
            if con is not None:
                run = ouvrir_run(con, r, deck.ref, dep, g.cible, complement={
                    "guide": g.gid, "recherche": nom, "jalons": [asdict(j) for j in g.jalons],
                    "hors_jeu": [] if nom.startswith("reelle") else g.hors_jeu})
                info["run_id"] = run
                ecr = Ecrivain(con, cat, deck, r, run)
                vus = set()
                for sid in r.cibles_atteintes[:1] + r.cibles_acceptees[:1]:
                    if sid not in vus:
                        vus.add(sid)
                        info.setdefault("combo_ids", []).append(ecr.combo(sid, "cible_atteinte"))
                con.commit()
            ligne[nom] = info
        # Méthode naïve (avis data-scientist-ygo) : joueur au hasard, même budget que le parcours en largeur.
        ligne["hasard"] = {"parties": 0, "plateau": 0, "sequence": 0, "secondes": 0} if args.sans_hasard else \
            parties_au_hasard(cat, depart, graine=GRAINE_MAINS, max_secondes=args.largeur,
                                            cible=g.cible, accepter=accepter)
        sortie["guides"].append(ligne)
        d = ligne.get("dirigee") or ligne["guidee"]
        l = ligne.get("largeur", {"sequence": False, "plateau": False, "secondes": 0, "etats": 0, "arret": "—"})
        def etat(x):
            return ("séquence ✓" if x["sequence"] else ("plateau seul" if x["plateau"] else "✗"))
        print(f"  {g.gid} : dirigée {etat(d)} {d['secondes']} s, {d['etats']} états ({d['arret']})"
              f" | largeur {etat(l)} {l['secondes']} s, {l['etats']} états ({l['arret']})"
              f" | hasard : séquence {ligne['hasard']['sequence']}, plateau {ligne['hasard']['plateau']}"
              f" sur {ligne['hasard']['parties']} parties")
        for cle in ("reelle_dirigee", "reelle_largeur"):
            if cle in ligne:
                x = ligne[cle]
                print(f"      main réelle ({cle.split('_')[1]}) : {etat(x)} {x['secondes']} s, {x['etats']} états "
                      f"({x['arret']}) ; cartes de réponse utilisées : {x.get('cartes_de_reponse_utilisees', '—')}")
        for pas in d.get("chemin_sequence", d.get("chemin_plateau", [])):
            print(f"      - {pas}")

    if args.mains:
        print(f"▶ Mains réalistes (graine {GRAINE_MAINS}, parcours en largeur, {args.largeur} s chacune)")
    for k, main in enumerate(mains_realistes(deck, args.mains), start=1):
        depart = etat_depart(deck, main)
        r = explorer(cat, depart, max_profondeur=args.profondeur, max_secondes=args.largeur, strategie="largeur")
        ligne = {"main": main} | resume(r)
        # Plateaux les plus fournis (affichage seulement : nombre de monstres, puis de cartes en main) : piste J3.
        par_plateau = {}
        for sid, board in r.finals.items():
            if board not in par_plateau or r.profondeur[sid] < r.profondeur[par_plateau[board]]:
                par_plateau[board] = sid
        def poids(sid):
            e = r.etats[sid]
            j = e.joueurs[0]
            return (len(j.cases) + len(e.zones_monstre_extra), len(j.main))
        retenus = sorted(par_plateau.values(), key=lambda s: (-poids(s)[0], -poids(s)[1], r.profondeur[s]))
        ligne["plateaux_les_plus_fournis"] = []
        for sid in retenus[:3]:
            e = r.etats[sid]
            j = e.joueurs[0]
            ligne["plateaux_les_plus_fournis"].append({
                "terrain": sorted([i.carte for _, i in j.cases] + [o.instance.carte for o in e.zones_monstre_extra]),
                "main": sorted(i.carte for i in j.main), "chemin": chemin_lisible(r, sid)})
        if con is not None:
            run = ouvrir_run(con, r, deck.ref, depart, complement={"main_realiste": k, "graine": GRAINE_MAINS})
            ecr = Ecrivain(con, cat, deck, r, run)
            ligne["run_id"] = run
            ligne["combos_ecrits"] = 0
            for sid in retenus[: args.max_combos]:
                ecr.combo(sid, "fin_volontaire", avec_fin=True)
                ligne["combos_ecrits"] += 1
            con.commit()
        sortie["mains"].append(ligne)
        print(f"  main {k} : {', '.join(main)}")
        print(f"      {ligne['etats']} états, {ligne['plateaux_finaux']} plateaux finaux distincts, "
              f"profondeur {ligne['profondeur_max_atteinte']}, {ligne['secondes']} s ({ligne['arret']}), "
              f"non couvert : {ligne['non_couverts']}")

    if con is not None:
        q = sortie["requetes"]
        q["combos_passant_par_Guiding_Quem"] = len(combos_passant_par(con, "Guiding Quem, the Virtuous"))
        q["Nadir_puis_directement_White"] = len(a_puis_directement_b(con, "Nadir Servant",
                                                                     "Fallen of the White Dragon"))
        ex = combos_passant_par(con, "Blazing Cartesia, the Virtuous")
        q["exemple_combo_passant_par_Cartesia"] = lire_combo(con, ex[0]) if ex else []
        print("▶ Requêtes (§ 3.6) sur combos.db")
        for cle, v in q.items():
            print(f"  {cle} : {v}")
        con.close()
    if args.json:
        args.json.write_text(json.dumps(sortie, ensure_ascii=False, indent=1))
        print(f"  JSON : {args.json}")
    return 0


if __name__ == "__main__":
    t0 = time.monotonic()
    code = main()
    print(f"  durée totale : {time.monotonic() - t0:.0f} s")
    sys.exit(code)
