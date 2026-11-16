# 0004 — Ban Radar : vue par défaut « Pièces d'archétype »

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Recommandation de l'agent retenue par défaut (Thomas n'a rien coché pour les points 1 à 10 ; à corriger s'il le souhaite)
- Tickets : TOK-94, TOK-53

## Contexte
Le Ban Radar mélange les pièces de moteur d'archétype et les staples génériques.

## Options
- Options détaillées dans `docs/audit-front/rapport.md` et `3-proposition.md`, non reprises ici.

## Décision
Vue par défaut « Pièces d'archétype » ; les staples génériques passent dans un second onglet.

## Raison
Raison non consignée dans le tableau ; `context.md` documente que l'omniprésence seule ne prédit pas les cartes touchées par une liste.

## Conséquences
Un filtre `?kind=archetype|generic`, appliqué en SQL, existe (`context.md`, section Ban Radar) ; le défaut actuel de la page n'a pas été vérifié pour cette note.

## Sources
- `docs/audit-front/decisions-2026-11-16.md` (décision 4)
