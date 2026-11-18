#!/usr/bin/env python3
"""Export des séquences de combos trouvées par le moteur, pour les rejouer dans l'oracle (TOK-140, jalon n°5).

Lit le JSON écrit par `scripts/combos_j2.py --json …`, rejoue chaque séquence trouvée depuis son état de départ
(le moteur est déterministe : la séquence brute « déclaration + réponses » redonne les mêmes états) et écrit
`docs/moteur-combos/sequences-pour-oracle.md` **dans le langage des règles du jeu** : main, Deck et Extra Deck de
départ, puis chaque action, ses coûts, ses choix et les déplacements de cartes, puis le plateau attendu. Aucune
structure interne du moteur : la session de l'oracle (jalon n°6, isolée, AGPL) ne lit pas `moteur_combos/`.

Usage : python scripts/combos_export_oracle.py sortie_j2.json [--sortie docs/moteur-combos/sequences-pour-oracle.md]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "scripts"))

from combos_j2 import charger  # noqa: E402
from moteur_combos.exploration import FILTRES_PAR_DEFAUT, ScriptExploration, etat_depart  # noqa: E402
from moteur_combos.regles import Declaration, Moteur  # noqa: E402

SORTIE = RACINE / "docs" / "moteur-combos" / "sequences-pour-oracle.md"
ZONES = {"deck": "Deck", "main": "main", "terrain": "terrain", "cimetiere": "Cimetière", "extra": "Extra Deck",
         "bannies": "bannie (face recto)", None: "—"}
ROLES = {"cout": "coût", "materiel": "matériel"}
ESSAIS = (("dirigee", "main du guide, recherche vers le plateau du guide"),
          ("largeur", "main du guide, parcours en largeur sans cible"),
          ("reelle_dirigee", "main réelle de 5 cartes, recherche vers le plateau du guide"),
          ("reelle_largeur", "main réelle de 5 cartes, parcours en largeur sans cible"))


def case(c: str | None) -> str:
    if not c:
        return ""
    if c.startswith("ZME"):
        return " (Zone Monstre Extra " + ("gauche" if c.endswith("G") else "droite") + ")"
    if c[0] == "M":
        return f" (Zone Monstre principale {c[1:]})"
    if c[0] == "S":
        return f" (Zone Magie/Piège {c[1:]})"
    return f" ({c})"


def ligne_pas(p) -> str | None:
    lib = p.libelle
    if lib.startswith("fenêtre adverse") or lib.startswith("cout :"):
        return None  # pas de réponse adverse (adversaire sans cartes) ; « cout : » double « coût : »
    lib = re.sub(r"^activer_declenche : (.+)/(\d+)$", r"choix : activer l'effet déclenché n° \2 de \1", lib)
    lib = re.sub(r"^activation : (.+) \(effet (\d+)\)$", r"activation de l'effet n° \2 de \1", lib)
    lib = re.sub(r"^résolution du maillon (\d+) : (.+) \(effet (\d+)\)$",
                 r"résolution du maillon \1 (effet n° \3 de \2)", lib)
    lib = re.sub(r"^carte : ", "choix : ", lib)
    lib = lib.replace("position : attaque", "position : Attaque").replace("(attaque)", "(Attaque)")
    lib = lib.replace("placement : zone_monstre_extra", "placement : Zone Monstre Extra")
    lib = re.sub(r" : (deck|main|terrain|cimetiere|extra|bannies) → (deck|main|terrain|cimetiere|extra|bannies)",
                 lambda m: f" : {ZONES[m.group(1)]} → {ZONES[m.group(2)]}", lib)
    mouvements = []
    for carte, role, de, vers, c in p.cartes:
        if vers is None or de is None:
            continue
        if role in ROLES or "→" not in lib:
            mouvements.append(f"{carte} : {ZONES[de]} → {ZONES[vers]}{case(c)}"
                              + (f" ({ROLES[role]})" if role in ROLES else ""))
        elif c:
            lib += case(c)
    return lib + (" — " + " ; ".join(mouvements) if mouvements else "")


def titre_declaration(d: dict, zone: str | None) -> str:
    t, carte, effet = d["type"], d["carte"], d["effet"]
    if t == "invocation_normale":
        return f"Invocation Normale de {carte}"
    if t == "invocation_synchro":
        return f"Invocation Synchro de {carte}"
    if t == "invocation_procedure":
        return f"Invocation Spéciale de {carte} par sa propre procédure (sans chaîne)"
    if t == "phase_de_fin":
        return "Passer à la Phase de Fin (pas de Phase de Combat au tour 1)"
    if t == "fin_de_tour":
        return "Terminer le tour"
    return f"Activer l'effet n° {effet} de {carte}" + (f" (depuis : {ZONES.get(zone, zone)})" if zone else "")


def zones_joueur(etat) -> dict[str, list[str]]:
    j = etat.joueurs[0]
    terrain = [f"{i.carte}{case(k)}" for k, i in j.cases]
    terrain += [f"{o.instance.carte}{case(o.cellule)}"
                for o in etat.zones_monstre_extra if o.controleur == 0]
    return {"Terrain": terrain, "Main": sorted(i.carte for i in j.main),
            "Cimetière": sorted(i.carte for i in j.cimetiere), "Bannies": sorted(i.carte for i in j.bannies)}


def compte(noms) -> str:
    c = Counter(noms)
    return ", ".join(f"{n} ×{k}" if k > 1 else n for n, k in sorted(c.items())) or "—"


def note_effet(cat, carte: str, numero: int) -> str:
    f = cat.get(carte)
    e = next((x for x in f.formalisation.effets if x.numero == numero), None) if f and f.declaree else None
    if e is None:
        return "—"
    note = re.sub(r"\s*\((R|T|N)\d+[a-z]?[^)]*\)", "", e.note or "")
    note = re.sub(r"\*\*|`|⚖", "", note).strip()
    return (note[:240] + "…") if len(note) > 240 else note


def rejouer(cat, depart, brut):
    m = Moteur(cat)
    fs = frozenset(FILTRES_PAR_DEFAUT)
    etat = depart
    etapes = []
    for d in brut:
        zone = None
        res = m.jouer(etat, Declaration(d["type"], d["carte"], d["effet"]), ScriptExploration(tuple(d["reponses"]), fs))
        if res.verdict != "legal":
            raise RuntimeError(f"rejeu impossible : {d} → {res.verdict} ({res.raison})")
        for p in res.pas:
            if p.type == "declarer" and p.cartes and p.cartes[0][0] == d["carte"]:
                zone = p.cartes[0][2]
                break
        lignes = [x for x in (ligne_pas(p) for p in res.pas) if x]
        etapes.append((titre_declaration(d, zone), lignes))
        etat = res.etat
    return etapes, etat


def bloc(cat, deck, g: dict, nom: str, desc: str, info: dict, k: int) -> list[str]:
    reelle = nom.startswith("reelle")
    main = g["main_reelle"] if reelle else g["main"]
    hors = [] if reelle else g["hors_jeu"]
    depart = etat_depart(deck, main, hors)
    etapes, fin = rejouer(cat, depart, info["brut_sequence"])
    j0 = depart.joueurs[0]
    out = [f"### {g['id']}.{k} — {g['titre']} ({desc})", ""]
    out.append("Départ : tour 1, nous commençons, Phase Principale 1, nos zones et celles de l'adversaire vides, "
               "adversaire sans carte en main ni réponse. Positions : Attaque partout.")
    out += ["", f"- **Main** ({len(main)}) : {compte(main)}",
            f"- **Deck** ({len(j0.deck)}) : {compte(i.carte for i in j0.deck)}",
            f"- **Extra Deck** ({len(j0.extra)}) : {compte(i.carte for i in j0.extra)}"]
    if hors:
        out.append(f"- **Retirées du jeu** (ni main, ni Deck) : {compte(hors)}")
    out.append("")
    effets = []
    for n, (titre, lignes) in enumerate(etapes, start=1):
        out.append(f"{n}. **{titre}**")
        out += [f"   - {x}" for x in lignes]
    for d in info["brut_sequence"]:
        if d["type"] == "activer" and (d["carte"], d["effet"]) not in effets:
            effets.append((d["carte"], d["effet"]))
    for d in info["brut_sequence"]:
        for rep in d["reponses"]:
            mm = re.fullmatch(r"(.+)/(\d+)", rep)
            if mm and (mm.group(1), int(mm.group(2))) not in effets:
                effets.append((mm.group(1), int(mm.group(2))))
    out += ["", "Plateau attendu à la fin de la séquence :"]
    for zone, cartes in zones_joueur(fin).items():
        out.append(f"- {zone} : {compte(cartes) if zone != 'Terrain' else (', '.join(cartes) or '—')}")
    out += ["", "<details><summary>Effets cités (numéro = rang de l'effet dans notre lecture du texte TCG ; le "
            "texte imprimé fait foi)</summary>", ""]
    out += [f"- {c}, effet n° {e} : {note_effet(cat, c, e)}" for c, e in effets]
    out += ["", "</details>", ""]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("json", type=Path)
    ap.add_argument("--sortie", type=Path, default=SORTIE)
    args = ap.parse_args(argv)
    donnees = json.loads(args.json.read_text())
    deck, cat = charger()
    out = ["# Séquences de combos à rejouer dans l'oracle (TOK-140, jalon n°5)", "",
           "> **18/11/2026**, généré par `scripts/combos_export_oracle.py` depuis la sortie de "
           "`scripts/combos_j2.py`. Pour la session de l'oracle (jalon n°6, isolée) : chaque séquence est écrite "
           "dans le langage des règles, sans référence au code du moteur. **À vérifier dans l'oracle** : (1) chaque "
           "action est légale à son moment, avec les coûts et choix indiqués ; (2) les déplacements de cartes sont "
           "ceux qu'écrit l'oracle ; (3) le plateau final est le même. Combos et sources : `combos-guides.md` "
           "(G1-G5 lot C3, G6-G10 lot J2 plein). Statut : **non vérifié** tant que l'oracle n'a pas rejoué.", "",
           "Conventions : les cartes de réponse (Ash Blossom, Ghost Ogre, Droll & Lock Bird, Mulcharmy Fuwalos) ne "
           "sont jamais activées (filtre déclaré) ; le joueur ne répond pas à ses propres maillons ; un monstre "
           "venu de l'Extra Deck va en Zone Monstre Extra si elle est libre. Une séquence identique à une autre "
           "n'est écrite qu'une fois.", ""]
    n = 0
    for g in donnees["guides"]:
        vues = set()
        k = 0
        out += [f"## {g['id']} — {g['titre']}", "", f"Sources : " + " ; ".join(
            f"{s['auteur']} ({s['date']}) {s['url']}" for s in g.get("sources", [])), f"Cible du guide : {g['cible']}",
            ""]
        for nom, desc in ESSAIS:
            info = g.get(nom)
            if not info or not info.get("brut_sequence"):
                if info is not None:
                    out += [f"*{desc} : séquence non trouvée dans le budget ({info.get('arret')}).*", ""]
                continue
            cle = json.dumps(info["brut_sequence"]) + str(nom.startswith("reelle"))
            if cle in vues:
                out += [f"*{desc} : même séquence que ci-dessus.*", ""]
                continue
            vues.add(cle)
            k += 1
            n += 1
            out += bloc(cat, deck, g, nom, desc, info, k)
    out.insert(2, f"{n} séquences distinctes, {len(donnees['guides'])} combos.\n")
    args.sortie.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"✓ {n} séquences écrites dans {args.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
