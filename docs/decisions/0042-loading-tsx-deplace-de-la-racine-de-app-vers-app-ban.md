# 0042 — loading.tsx déplacé de la racine de app/ vers app/ban/

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lot 2, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-106

## Contexte
`app/loading.tsx` rendait l'accueil vide sans JavaScript et coûtait ≈ 0,4 s de LCP.

## Options
- Déplacer le fichier dans `app/ban/` (une seule route dynamique)
- Groupes de routes (déplace 7 dossiers)

## Décision
Fichier déplacé dans `app/ban/loading.tsx`.

## Raison
Un seul fichier déplacé, réversible par `git mv`. Mesuré : LCP mobile ≈ 1,65 à 1,75 s au lieu de ≈ 2,0 s sur les pages statiques, sans régression.

## Conséquences
Touche toutes les pages statiques. Piège documenté dans `context.md`.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 2)
