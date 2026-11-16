# 0020 — Moteur de combos (D4) : actions légales mais sans intérêt

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude, par délégation de Thomas (« tu peux pas prendre ces décisions tout seul ? »)
- Tickets : TOK-84, TOK-85, TOK-87

## Contexte
Annuler son propre effet avec `Ash Blossom` est légal, mais chaque carte de ce type double le nombre de lignes. Principe antérieur : « le système recense sans juger ».

## Options
- A : légales pour le moteur ; l'exploration les écarte par des filtres déclarés et enregistrés avec le résultat (`cb_run.filters_json`)
- B : tout explorer, toujours
- C : les interdire dans le moteur

## Décision
Option A : l'exhaustivité s'entend « à filtres près ».

## Raison
B fait exploser le nombre de lignes ; C empêche le moteur de dire la règle.

## Conséquences
Rouvrir si le nombre de lignes reste ingérable malgré les filtres. Réversible tant que le moteur n'existe pas ; Thomas peut rouvrir le choix.

## Sources
- `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` (décision D4)
