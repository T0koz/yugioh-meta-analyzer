# 0021 — Moteur de combos (D5) : propagation du « non couvert »

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude, par délégation de Thomas (« tu peux pas prendre ces décisions tout seul ? »)
- Tickets : TOK-84, TOK-85, TOK-87

## Contexte
Quatre cartes du deck n'ont pas de texte ; d'autres peuvent ne pas être formalisées.

## Options
- A : trois niveaux (action sur la carte → « non couvert » ; carte qui pourrait agir → branche arrêtée, exploration incomplète ; zone qui la contient → liste « peut-être incomplète »)
- B : strict (aucun résultat tant que le deck n'est pas couvert à 100 %)
- C : souple (ignorer la carte sans marquage)

## Décision
Option A.

## Raison
C contredit le principe « n'afficher que ce qui est démontré » ; B n'affiche rien d'utile avant couverture totale.

## Conséquences
Rouvrir si trop de résultats sont « incomplets » pour être utiles. Détail : `definitions-et-schema.md` § 3.4. Réversible tant que le moteur n'existe pas ; Thomas peut rouvrir le choix.

## Sources
- `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` (décision D5)
