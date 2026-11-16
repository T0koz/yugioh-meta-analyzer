# 0018 — Moteur de combos (D2) : deux niveaux, le pas et la transition

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude, par délégation de Thomas (« tu peux pas prendre ces décisions tout seul ? »)
- Tickets : TOK-84, TOK-85, TOK-87

## Contexte
Le pas est une décision élémentaire (choisir une cible) ; la transition va d'un état stable au suivant.

## Options
- A : deux niveaux (pas pour moteur/oracle, transitions pour les combos)
- B : transitions seulement
- C : pas seulement

## Décision
Option A.

## Raison
Sans les pas on ne peut pas dire où le moteur et l'oracle divergent ; sans les transitions, les combos sont illisibles (5 à 10 lignes par carte jouée). Coût : plus de lignes stockées.

## Conséquences
Rouvrir si l'oracle ne donne pas la liste des actions légales (question ouverte n° 3). Réversible tant que le moteur n'existe pas ; Thomas peut rouvrir le choix.

## Sources
- `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` (décision D2)
