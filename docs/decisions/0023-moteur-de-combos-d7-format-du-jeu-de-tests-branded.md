# 0023 — Moteur de combos (D7) : format du jeu de tests Branded

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude, par délégation de Thomas (« tu peux pas prendre ces décisions tout seul ? »)
- Tickets : TOK-84, TOK-85, TOK-87

## Contexte
Les tests doivent être écrits avant le moteur.

## Options
- A : YAML écrit à la main, état d'arrivée en texte libre jusqu'à la tranche 0
- B : formaliser l'état d'arrivée tout de suite
- C : tests en Python (pytest) directement

## Décision
Option A (`tests-branded.yaml`, 72 situations non validées).

## Raison
B risque de tout réécrire si D2 ou D3 change ; C lie le jeu de tests à un moteur qui n'existe pas.

## Conséquences
Les 72 situations restent des hypothèses tant qu'un juge ne les a pas relues (TOK-89, 34 points de règle).

## Sources
- `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` (décision D7)
