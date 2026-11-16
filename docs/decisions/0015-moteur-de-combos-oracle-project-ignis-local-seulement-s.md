# 0015 — Moteur de combos : oracle Project Ignis, local seulement, sans contact avec le LLM

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (réunion du 2026-11-16)
- Tickets : TOK-84, TOK-86

## Contexte
Pour tester le moteur, on compare ses réponses à une source de vérité externe (un « oracle »). Le spike a vérifié que les 23 cartes Branded et 56 cartes de soutien ont un script, et que la licence est AGPL-3.0.

## Options
- Project Ignis (EDOPro), repli sur Fluorohydride si le branchement coince.

## Décision
Project Ignis comme oracle de test, trois conditions : local seulement (jamais intégré ni exposé dans le produit), indépendance (les scripts de l'oracle ne sont jamais fournis au LLM qui formalise ni à l'agent qui code le moteur), effort estimé à 3 à 6 jours (estimation, pas mesure).

## Raison
L'AGPL imposerait de publier notre code si l'oracle entrait dans le produit. Limite connue : le LLM a pu voir ces scripts publics à l'entraînement.

## Conséquences
Le banc d'oracle (TOK-86) n'est pas encore construit. Les textes et images de cartes appartiennent à Konami : risque distinct, sans conclusion juridique.

## Sources
- `docs/moteur-combos/decisions-2026-11-16.md` (§ 6)
