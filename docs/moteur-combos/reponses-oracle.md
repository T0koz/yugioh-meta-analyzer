# Réponses de l'oracle Project Ignis (TOK-86) — installation non réalisée

**Statut au 2026-11-17 : l'oracle n'a pas été installé, donc aucune des 72 situations n'a été jouée.**
Les 34 points de règle de `points-de-regle-a-valider.md` restent tous **non testés à ce jour** : ce n'est pas
« non testable par l'oracle », c'est « l'oracle n'a pas pu être mis en place ». Aucun désaccord avec les lectures
supposées n'a donc été établi ; le juge garde la liste complète des 34 points.

## Ce qui a été tenté (hors dépôt, dans `~/code/oracle-ignis/`)

- Accès réseau à GitHub : fonctionne.
- Dépôts officiels de l'organisation `ProjectIgnis` vérifiés par l'API GitHub : `CardScripts` (scripts de cartes) et
  `BabelCDB` (base de cartes) existent et sont à jour ; **aucun dépôt du cœur de jeu à jour n'y figure**.
  `ProjectIgnis/EDOPro-Core` est une coquille qui ne contient qu'un README renvoyant vers `edo9300/ygopro-core`,
  dépôt d'un autre compte, hors de la liste de sources autorisée pour cette session. Je ne l'ai pas cloné.
- Outils de compilation présents : `cc`/`clang`/`clang++`, `make`, Command Line Tools. **Absents** : `premake5`, Lua
  (ni binaire ni sources), `cmake`.
- Aucun lanceur n'a été écrit : il s'appuie sur le cœur, qui n'est pas disponible.

## Ce qu'il manque pour continuer (décision de Thomas)

1. **Autoriser la source du cœur** : `github.com/edo9300/ygopro-core` (cœur utilisé par EDOPro / Project Ignis ; licence
   à relire avant usage, de type AGPL). Le brief limitait les sources à l'organisation `ProjectIgnis`.
2. **Installer `premake5` et Lua 5.3/5.4** (par exemple `brew install premake lua`), installation système que cette
   session n'a pas le droit de faire. Alternative sans installation système : télécharger les sources de Lua dans
   `~/code/oracle-ignis/`, mais `premake5` reste nécessaire pour le projet de build.
3. Écrire un lanceur en C++ ou via une liaison Python (le cœur est une bibliothèque, il n'a pas d'interface en ligne
   de commande) : travail d'une demi-journée environ, à faire par une session séparée de celle qui formalise le moteur.

Rien de Project Ignis n'est dans ce dépôt.
