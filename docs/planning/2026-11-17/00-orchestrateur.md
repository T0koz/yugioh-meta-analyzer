# Session front du 2026-11-16 (soir) — file d'attente — brief de l'orchestrateur

Tu es l'ORCHESTRATEUR. Tu coordonnes, tu ne codes pas les chantiers toi-même. Réponds en français.
Thomas a validé cette file en avance : lancer les sessions ci-dessous **l'une après l'autre** vaut son accord
(c'est la seule exception à « aucune session sans accord »). Lancement manuel par Thomas vers 20 h (réinitialisation de ses crédits) ; il peut s'absenter : travaille en autonomie, sans l'attendre.

## Lis d'abord
`CLAUDE.md`, `context.md` (§ Travail en sessions parallèles, § À faire), `BACKLOG.md`, puis `regles.md` (ce dossier).

## File d'attente
Tu ne lances QUE le lot 1, puis tu t'arrêtes et écris le compte rendu.
1. `01-seuil-boutique.md` — seuil absolu Fort / Modéré / Faible (données, Sonnet)

Les lots front (02 accueil, 03 dataviz, 04 page d'archétype, 05 SEO et tests visuels) sont lancés **à la main
par Thomas**, un par session, sur le modèle le plus puissant disponible (règle du projet : le front se fait
toujours avec le modèle le plus puissant). Chaque session de lot fusionne elle-même sa branche dans la branche
d'intégration (voir `regles.md`). Ordre : 02 → 03 → 04 → 05.

## Méthode
- Branche d'intégration : `claude/front-nuit-17-11`, créée depuis `main` à jour (vérifie d'abord `git status` propre
  et `main` = `origin/main`). Rien n'est fusionné dans `main`, rien n'est poussé.
- Pour chaque ticket : un worktree neuf `.claude/worktrees/<ticket>` depuis la branche d'intégration, une session
  avec le brief du fichier (copie son contenu + `regles.md`), modèle indiqué dans le brief.
- Quand la session a fini : fusionne sa branche dans la branche d'intégration (`--no-ff`), résous les conflits
  (`context.md` et `BACKLOG.md` : garde les deux), lance `python scripts/check.py`, ajoute une ligne au fichier
  `compte-rendu.md` (ce dossier), puis archive la session et supprime son worktree. Passe au ticket suivant.
- Le fichier `decisions-prises.md` (ce dossier) reçoit chaque décision imprévue prise par défaut.

## Quand t'arrêter (puis écrire le compte rendu final)
- `check.py` échoue deux fois de suite sur la même cause ;
- une décision irréversible ou hors du brief se présente ;
- un message de limite d'usage apparaît ou approche : termine proprement le ticket en cours (état propre sur la
  branche, rien de cassé) et ne lance pas le suivant ;
- plafond d'effort par ticket : une session qui dépasse environ 2 h ou 250 appels d'outils s'arrête et rend l'état.

## Compte rendu final (bref)
Tableau ticket / résultat / critères atteints ou non, tokens si disponibles, ce qui reste, lien vers
`decisions-prises.md`, et UN formulaire à cocher pour moi (fusion dans `main`, push, mise à jour de Linear).
