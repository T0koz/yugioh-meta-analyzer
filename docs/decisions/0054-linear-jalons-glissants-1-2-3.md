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

## Retirer une fonctionnalité d'un jalon (complément validé par Thomas le 18/11)
Une fonctionnalité qui a un problème ou bloque le déploiement sort du jalon ; le jalon peut finir sans elle.
- **Pas encore fusionnée** : on ne la fusionne pas.
- **Fusionnée dans la branche d'intégration** : `git revert` du ou des commits du ticket (`git log --grep TOK-xxx` ;
  `git revert -m 1 <fusion>` si le lot ne contenait qu'elle), puis `python scripts/check.py --all` et `serving.db`
  reconstruite. La table qu'elle a ajoutée en base peut rester (plus rien ne la lit) ou être supprimée après sauvegarde.
  Pour la réintégrer plus tard : revert du revert, pas une nouvelle fusion de sa branche.
- **Déjà poussée ou déployée** : retour au déploiement précédent sur Vercel (sur Hobby, seulement le précédent), puis
  revert sur `main` et nouveau déploiement.
- Dans tous les cas : le ticket passe au Jalon 2 ou sans jalon, la raison va en commentaire Linear et une ligne dans
  `etat.md` ; les tickets qui en dépendent (« bloqué par » dans Linear) sont examinés avant le revert.

Conditions imposées à chaque session pour que le retrait reste possible :
- un commit par ticket, avec le TOK dans le message ;
- écriture en base additive seulement (table ou colonne nouvelle ; jamais de modification d'une table existante sans
  sauvegarde dédiée et formulaire) ;
- dépendances entre tickets déclarées dans Linear (« bloqué par ») par l'orchestrateur à la composition du jalon.

**Passage dans `main` jalon par jalon** : un jalon fini et vérifié forme un lot de commits prêt à pousser ; une
fonctionnalité retirée n'y entre jamais. Pas d'interrupteur par variable d'environnement pour l'instant (rien n'est
déployé) ; à reconsidérer après le premier déploiement (TOK-35).
