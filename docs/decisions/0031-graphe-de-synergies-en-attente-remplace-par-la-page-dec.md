# 0031 — Graphe de synergies en attente, remplacé par la page Decks (TOK-102 → TOK-114)

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (soir du 2026-11-16)
- Tickets : TOK-102, TOK-114

## Contexte
Le graphe de synergies (vis-network) ne montre que des cartes jouées ensemble ; une liste de deck le dit mieux (brief du lot 9).

## Options
- Refondre le graphe (Sigma.js ou PixiJS, TOK-102)
- Mettre le graphe en attente et construire la page Decks (index des archétypes et fiche de composition, TOK-114)

## Décision
TOK-102 est en attente (« ne pas y toucher ») ; TOK-114 (Decks) prend la priorité.

## Raison
Le graphe montre des co-occurrences ; une fiche de deck donne la dépendance d'un archétype à une carte (« 95 % des listes ») sans calcul.

## Conséquences
Le graphe reste tel quel : canvas masqué dans les captures visuelles (non déterministe), palette de données non appliquée. L'option 3D (TOK-105) dépend de lui. Ambiguïté : les sources lues ne disent pas si le graphe est abandonné ou seulement différé ; `BACKLOG.md` garde TOK-102 « Backlog ».

## Sources
- `docs/planning/sprint-2/00-orchestrateur.md`
- `docs/planning/sprint-2/01-decks.md`
- `docs/planning/file.md` (lot 9)
