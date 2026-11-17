# 0037 — Contexte chargé à chaque session allégé : journaux déplacés dans docs/journal/

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas avec Claude (commit `0a9476b`)
- Tickets : —

## Contexte
`context.md` (54 Ko) et `BACKLOG.md` (22 Ko) étaient chargés à chaque session.

## Options
- Non consignées dans les sources.

## Décision
`context.md` passe à 20 Ko et `BACKLOG.md` à 10 Ko ; journaux détaillés et tickets terminés déplacés tels quels dans `docs/journal/` (avec `backlog-archive.md`), pointeurs et pièges durables conservés dans `context.md`.

## Raison
Réduire le contexte chargé (message du commit) ; aucun statut modifié.

## Conséquences
Les détails vivent dans `docs/journal/` ; `context.md` ne garde que l'essentiel.

## Sources
- Commit `0a9476b`
- `context.md`
- `docs/journal/backlog-archive.md`
