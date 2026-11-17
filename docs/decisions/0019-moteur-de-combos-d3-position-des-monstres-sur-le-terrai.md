# 0019 — Moteur de combos (D3) : position des monstres sur le terrain

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude, par délégation de Thomas (« tu peux pas prendre ces décisions tout seul ? »)
- Tickets : TOK-84, TOK-85, TOK-87

## Contexte
Deux cartes du deck lisent la position (`Sprind`, colonne ; `Albion the Sanctifire Dragon`, zones centrales). Énumérer les 5 zones à chaque invocation multiplie les états.

## Options
- A : l'état porte la zone, le moteur place par défaut (première zone libre) et n'énumère que si une carte du deck lit la position
- B : énumérer toutes les zones, toujours
- C : ignorer les zones (effets de Sprind et d'Albion « non couverts »)

## Décision
Option A, avec hypothèse à faire confirmer par un juge.

## Raison
B est exact sans hypothèse mais produit beaucoup plus d'états ; C rend deux cartes non couvertes.

## Conséquences
Rouvrir si le juge infirme l'hypothèse. Réversible tant que le moteur n'existe pas ; Thomas peut rouvrir le choix.

## Sources
- `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` (décision D3)
