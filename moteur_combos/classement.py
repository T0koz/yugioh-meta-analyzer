"""Classement des situations selon les points de règle dont elles dépendent (lot 18).

Trois classes, exclusives, appliquées dans cet ordre (décision par défaut du 18/11, voir
`docs/planning/2026-11-18/decisions-prises.md`) :

1. `un_seul_avis` : dépend d'un point à confiance basse qui n'a reçu qu'un avis (R08, R27 b, R34) ;
2. `non_executable_sans_regles` : ne dépend d'**aucun** point relu : son verdict repose entièrement sur
   des règles à coder en tranche 0 (livret, texte) ou sur l'exploration, et le harnais ne peut pas le
   vérifier aujourd'hui ;
3. `regles_confirmees` : tous ses points confirmés par la relecture 1 (R22 compris, levé par
   cohérence), ou verdict vérifiable dès aujourd'hui sans règle de jeu (T68 : « non couvert »).

Le statut de chaque point est **lu** dans `points-de-regle-a-valider.md` (colonnes « Confiance » et
« Relecture 1 »), pas recopié ici : si la relecture change, le classement suit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CLASSES = ("regles_confirmees", "un_seul_avis", "non_executable_sans_regles")

# R27 a deux parties (a : nom temporaire de COCA ; b : bannissement en coût, face visible, déclencheurs).
# Le YAML écrit « R27 » ; la partie dépend de la question posée, lue dans l'action de chaque test.
SOUS_POINTS = {
    "T32": {"R27": "R27a"},  # COCA porte le nom de MERC → compte comme « Tri-Brigade » pour TBKITT
    "T33": {"R27": "R27b"},  # MERC banni en coût depuis le Deck : son effet se déclenche
    "T62": {"R27": "R27b"},  # bannissement face visible : déclenche GSWORD (et MERC)
}


@dataclass(frozen=True)
class PointDeRegle:
    numero: str          # R01… ou R27a / R27b
    confiance: str       # texte de la colonne « Confiance »
    relecture: str       # texte de la colonne « Relecture 1 »
    tests: tuple[str, ...]
    confirme: bool       # confirmé par la relecture 1 (ou levé par cohérence)
    un_seul_avis: bool   # confiance basse : le dossier prévoyait deux avis, il n'y en a qu'un


def lire_points(chemin: Path) -> dict[str, PointDeRegle]:
    """Lit les tableaux `| Rxx | question | lecture | confiance | tests | relecture 1 |`."""
    points: dict[str, PointDeRegle] = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if not cellules or not re.fullmatch(r"R\d{2}", cellules[0]):
            continue
        if len(cellules) != 6:
            raise ValueError(f"ligne de point de règle mal formée : {ligne[:60]}…")
        numero, _question, _lecture, confiance, tests, relecture = cellules
        tests_ = tuple(re.findall(r"T\d{2}", tests))
        rel = relecture.lower()
        confirme = rel.startswith("confirmé") or "tenu pour résolu" in rel or "confirmés" in rel
        if numero == "R27":
            # « moyenne (a), basse (b) » : deux sous-points, de confiances différentes.
            for partie, conf in (("a", "moyenne"), ("b", "basse")):
                points[f"R27{partie}"] = PointDeRegle(f"R27{partie}", conf, relecture, tests_, confirme,
                                                      conf == "basse")
            continue
        points[numero] = PointDeRegle(numero, confiance, relecture, tests_, confirme, "basse" in confiance)
    return points


def regles_precisees(situation: dict) -> list[str]:
    """Points de règle du test, avec R27 remplacé par sa partie (a ou b)."""
    sous = SOUS_POINTS.get(situation["id"], {})
    out = [sous.get(r, r) for r in (situation.get("regles") or [])]
    if "R27" in out:
        raise ValueError(f"{situation['id']} : dépend de R27 sans partie précisée (ajouter à SOUS_POINTS)")
    return out


def classer(situation: dict, points: dict[str, PointDeRegle], verifiable_sans_regles: bool) -> tuple[str, str]:
    """(classe, raison). Lève ValueError sur un point inconnu ou non confirmé : rien n'est classé en silence."""
    regles = regles_precisees(situation)
    for r in regles:
        if r not in points:
            raise ValueError(f"{situation['id']} : point de règle inconnu {r}")
    seuls = [r for r in regles if points[r].un_seul_avis]
    if seuls:
        return "un_seul_avis", f"dépend de {', '.join(seuls)} (un seul relecteur, confiance basse)"
    non_confirmes = [r for r in regles if not points[r].confirme]
    if non_confirmes:
        raise ValueError(f"{situation['id']} : point(s) non confirmé(s) par la relecture : {non_confirmes}")
    if not regles:
        if verifiable_sans_regles:
            return "regles_confirmees", "aucun point de règle ; verdict vérifiable sans règle de jeu (D5)"
        return "non_executable_sans_regles", "aucun point relu : verdict tiré du livret ou du texte, à coder en tranche 0"
    return "regles_confirmees", f"{', '.join(regles)} confirmés par la relecture 1"


def ecarts_croises(situations: list[dict], points: dict[str, PointDeRegle]) -> list[str]:
    """Le YAML (`regles`) et le tableau des points (colonne « Tests ») disent-ils la même chose ?"""
    ecarts = []
    yaml_par_point: dict[str, set[str]] = {}
    for s in situations:
        for r in s.get("regles") or []:
            yaml_par_point.setdefault(r, set()).add(s["id"])
    for numero, p in points.items():
        base = numero[:3]
        if numero == "R27b":
            continue  # même colonne « Tests » que R27a
        md = set(p.tests)
        yml = yaml_par_point.get(base, set())
        if md - yml:
            ecarts.append(f"{base} : cité pour {sorted(md - yml)} dans le tableau, absent de leurs `regles`")
        if yml - md:
            ecarts.append(f"{base} : listé dans `regles` de {sorted(yml - md)}, absent de la colonne « Tests »")
    return ecarts
