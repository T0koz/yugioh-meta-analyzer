# Session front du 2026-11-16 (soir) — file d'attente — brief de l'orchestrateur

Tu es l'ORCHESTRATEUR. Tu coordonnes, tu ne codes pas les chantiers toi-même. Réponds en français.
Thomas a validé cette file en avance : lancer les sessions ci-dessous **l'une après l'autre** vaut son accord
(c'est la seule exception à « aucune session sans accord »). Lancement manuel par Thomas vers 20 h (réinitialisation de ses crédits) ; il peut s'absenter : travaille en autonomie, sans l'attendre.

## Lis d'abord
`CLAUDE.md`, `context.md` (§ Travail en sessions parallèles, § À faire), `BACKLOG.md`, puis `regles.md` (ce dossier).

## File d'attente (dans cet ordre, une session neuve par ticket, sans attendre Thomas entre deux)
1. `01-seuil-boutique.md` — données : demande le modèle Sonnet pour cette session si tu le peux, sinon garde le tien
2. `02-tok-106-accueil.md` — front
3. `03-tok-99-dataviz.md` — front
4. `04-tok-101-archetype.md` — front
5. `05-tok-100-seo-tests-visuels.md` — front, EN DERNIER (images de référence sur l'interface finale)

**Modèle** : tu tournes sur le modèle le plus puissant (Fable) ; les sessions front héritent de ton modèle ou
reçoivent explicitement le plus puissant disponible (règle du projet). Note dans le compte rendu le modèle
réellement utilisé par chaque session. Une seule session à la fois : attends la fin de l'une avant de lancer
la suivante.

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
