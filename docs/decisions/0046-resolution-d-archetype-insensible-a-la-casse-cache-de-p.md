# 0046 — Résolution d'archétype insensible à la casse (cache de pages corrompu sur macOS)

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lot 4, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-101

## Contexte
Une variante de casse (`/archetype/Branded`) écrasait le cache de la bonne page sur un disque insensible à la casse.

## Options
- Réécriture par expression régulière dans `next.config.ts` (essayée puis retirée : motifs insensibles à la casse)
- Résolution du slug sans tenir compte de la casse dans l'API

## Décision
L'API résout le slug sans tenir compte de la casse : même page pour toute casse ; adresse canonique = slug servi.

## Raison
Réversible ; seule option qui marche.

## Conséquences
Lien canonique laissé au lot 5 (réalisé par `pageMetadata`).

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 4)
