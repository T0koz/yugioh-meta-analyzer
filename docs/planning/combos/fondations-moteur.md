# Lot 18 — Fondations du moteur de combos (indépendantes des règles de jeu)

Modèle : Opus (code de fond, pas de front). Branche de travail : la tienne (worktree), à fusionner par l'orchestrateur
dans `claude/moteur-18-11`. **Ne lis jamais le code de Project Ignis** ni le dossier de l'oracle (`~/code/oracle-ignis/`),
ni ce que produit la session du lot 17 en dehors de `docs/moteur-combos/reponses-oracle.md` (données seulement).
Pas de logique de règles (timing, chaînes, « une fois par tour » appliqué, verrous) : c'est la tranche 0 (TOK-90),
lot suivant.

**Préalables : remplis.** D1 à D7 validées par Thomas le 17/11 ; D3 révisée et D1 maintenue le 18/11
(`docs/moteur-combos/decisions-a-prendre-tok-85-87.md`) ; relecture des 34 points de règle faite le 17/11
(`docs/moteur-combos/reponses-juge-2026-11-17.md`). L'horloge de la règle d'arrêt (J2 en 8 semaines) démarre avec
ce lot : échéance le **13/01/2027** (`docs/decisions/0053-*.md`).

## À lire d'abord
`docs/moteur-combos/definitions-et-schema.md`, `decisions-a-prendre-tok-85-87.md`, `reponses-juge-2026-11-17.md`,
`jeu-de-tests-branded.md`, `tests-branded.yaml`, `points-de-regle-a-valider.md` (colonne « Relecture 1 »).

## À faire
0. **Reporter dans `definitions-et-schema.md` ce que la relecture a changé** (avant d'écrire le code) :
   - D3 « entre-deux » : l'état porte toujours la case exacte ; à chaque Invocation depuis l'Extra Deck, le choix
     Zone Monstre Extra / zone principale est une option de l'action ; un monstre Invoqué depuis le Cimetière (ou toute
     autre zone que l'Extra Deck) ne peut pas aller en Zone Monstre Extra ; les colonnes ne sont énumérées que si une
     carte du deck lit la position, mais la case est toujours enregistrée sur le plateau final ;
   - « une fois par tour » en **trois** formes : par nom de carte (« You can only activate 1 [nom] per turn »), par
     effet et par nom (« You can only use this effect of [nom] once per turn »), par exemplaire (« Once per turn ») ;
     le schéma doit pouvoir enregistrer les trois (la consommation elle-même est de la tranche 0) ;
   - le Cimetière peut rester un multiensemble (son ordre ne sert qu'à l'arbitre) ; l'historique des transitions suffit ;
   - limite de 3 exemplaires **par nom, « always treated as » compris** pour le contrôle de validité d'un deck ;
   - prévoir dans le schéma une **cible d'exploration** (plateau final visé) et un motif d'arrêt « boucle » : le
     relecteur signale que Branded peut tourner sans fin ; seule la structure est demandée ici, pas l'algorithme.
1. Schéma de données de TOK-85 en code et en tables, dans une base **à part** (`data/combos.db`, ignorée par Git),
   jamais dans `yugioh.db`. Textes des cartes : lecture seule de la base de référence,
   `file:/Users/thomascozian/code/yugioh-meta-analyzer/data/yugioh.db?mode=ro` (un worktree n'a pas de base) ;
   vérifier `text_sha256` de `deck-branded-source.json` contre le texte lu.
2. Chargement du deck (`deck-branded-source.json`) et construction de l'état de départ d'une situation du YAML.
3. Harnais de tests qui lit `tests-branded.yaml`, exécute ce qui est exécutable sans règles (chargement, état de
   départ, cohérence des alias et des zones), et **classe chaque test** selon les points de règle dont il dépend :
   - « règles confirmées » : tous ses Rxx confirmés par la relecture 1 (ou R22, levé par cohérence) ;
   - « un seul avis » : dépend de R08, R27 (b) ou R34 (confiance basse, un seul relecteur) ;
   - « non exécutable sans règles » : tout ce qui demande la tranche 0.
4. Tests unitaires (`pytest`) des structures et du chargement.

## Hors périmètre
Toute règle de jeu, l'algorithme d'exploration, l'API, l'interface, le deck avec `Lubellion` (D1 maintenue).

## Critères
`python scripts/check.py` vert ; harnais lancé par **une** commande ; chaque test des 72 classé ; aucune règle de jeu
codée ; `definitions-et-schema.md` à jour (point 0) ; temps noté dans `docs/moteur-combos/chronometrage.md` ;
décisions prises par défaut dans `docs/planning/2026-11-18/decisions-prises.md`. Faire relire le schéma par l'agent
`gardien-donnees` (nouvelle base). Ne pas pousser, ne pas fusionner : l'orchestrateur fusionne.
