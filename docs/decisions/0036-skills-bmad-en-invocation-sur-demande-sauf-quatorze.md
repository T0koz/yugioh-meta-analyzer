# 0036 — Skills BMad en invocation sur demande, sauf quatorze

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (soir du 2026-11-16)
- Tickets : —

## Contexte
Le projet installe de nombreux skills BMad et WDS qui alourdissent le contexte chargé.

## Options
- Non consignées dans les sources.

## Décision
Les skills sont en « sur demande » (`disable-model-invocation`), sauf quatorze.

## Raison
Raison non consignée dans les sources lues (hors brief du lot 7).

## Conséquences
Ambiguïté : le dossier `.claude/skills` du worktree contient 59 skills dont 43 portent `disable-model-invocation`, soit 16 sans ; le « 14 » du brief n'est pas retrouvé. Le dossier n'est pas suivi par Git (non vérifiable dans l'historique).

## Sources
- `docs/planning/sprint-2/00-journal-decisions.md` (liste de décisions)
