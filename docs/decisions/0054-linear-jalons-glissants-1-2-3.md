# 0054 — Linear : trois jalons glissants pour lire la file

- Date : 2026-11-18
- Statut : acceptée
- Décidé par : Thomas (avec Claude, session d'orchestration du 18/11)
- Tickets : TOK-120, TOK-123, TOK-129 à TOK-135

## Contexte
Avec plusieurs sessions par jour et des branches pas encore dans `main`, Thomas ne voyait plus rapidement la file ni où
reprendre. Les « lots » n'existaient que dans `docs/planning/etat.md`, un lot correspondant le plus souvent à un ticket.

## Options
- A : une étiquette « Lot NN » par lot, un lot = un ticket (essayée le matin du 18/11, rejetée).
- B : un jalon Linear par lot, nommé par thème (un jalon de plus à chaque lot, accumulation).
- C : trois jalons fixes et glissants (Jalon 1, 2, 3), chacun = un groupe de fonctionnalités composé selon la charge.

## Décision
Option C : une fonctionnalité a le jalon 1, 2 ou 3, ou pas de jalon ; quand le Jalon 1 est fini, le 2 devient le 1, le 3
devient le 2, un nouveau 3 est composé.

## Raison
Un lot est un sprint court taillé selon la charge, pas un thème ni un ticket : on peut en faire passer plusieurs par jour
en consommant bien les tokens. Trois jalons fixes donnent une barre d'avancement lisible sans s'accumuler. On perd le
rattachement durable d'un ticket à son lot dans Linear : l'historique est tenu dans `etat.md`.

## Conséquences
- L'orchestrateur compose les jalons (charge S/M/L = 1/2/3 points dans « estimate ») et fait le glissement.
- Les anciens jalons « File de nuit 16-17/11 » et « File du 18/11 » sont à supprimer à la main par Thomas.
- « Fini » = fusionné dans la branche d'intégration et vérifié (choix par défaut, à confirmer dans
  `docs/planning/2026-11-18/decisions-prises.md`).
- Question encore ouverte : Linear source de vérité de l'avancement (statut) et dépôt pour le contenu.
