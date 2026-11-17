# Lot 17 — TOK-86, banc d'oracle Project Ignis en local (relance du 18/11)

Modèle : Sonnet. **Agent séparé** : cette session ne formalise ni ne code le moteur de combos, et aucun agent qui
formalise ou code le moteur ne lit son code ni le code de Project Ignis (décision du 16/11). Elle ne produit que des
**résultats** (données), jamais du code destiné au moteur. Elle tourne **en même temps que le lot 18** (accord de
Thomas du 18/11) : ne lis pas le code produit par le lot 18, ne touche à aucun fichier hors de ceux listés ici.

**But** : faire jouer à un moteur de référence (cœur `ygopro-core` et scripts de cartes de Project Ignis) les
situations de `docs/moteur-combos/tests-branded.yaml`, pour trancher indépendamment les points de règle, en priorité
ceux qui n'ont qu'un avis humain.

## Ce qui a changé depuis la première tentative (17/11)
- **Sources autorisées par Thomas** : `github.com/edo9300/ygopro-core` (cœur), `github.com/ProjectIgnis/CardScripts`
  (scripts de cartes), `github.com/ProjectIgnis/BabelCDB` (base de cartes). Usage local hors dépôt, aucune copie de
  leur code dans ce dépôt (licences AGPL / GPL).
- **Outils installés par Thomas** : `premake5` 5.0.0 (`/opt/homebrew/bin/premake5`) et Lua 5.4.9 via la formule
  `lua@5.4`, **non liée** : en-têtes et bibliothèque sous `/opt/homebrew/opt/lua@5.4` (`include/lua5.4`, `lib`).
  `brew install lua` donnerait la 5.5, que le cœur n'accepte pas. Si le cœur exige un Lua compilé autrement, compiler
  les sources de Lua 5.4 dans le dossier de l'oracle.
- **La relecture humaine est faite** (`docs/moteur-combos/reponses-juge-2026-11-17.md`) : 32 points confirmés par un
  joueur de tournoi. Points à traiter en priorité : **R08, R27 (b), R34** (un seul avis), puis **R22** (levé par
  cohérence seulement), puis les autres.

## À faire
1. Installer l'oracle **hors du dépôt**, dans `~/code/oracle-ignis/` (jamais commité ici).
2. Un petit lanceur, dans ce même dossier, qui place l'état de départ d'une situation et demande à l'oracle si
   l'action est légale et quel est l'état d'arrivée (le cœur est une bibliothèque sans interface : C++ ou liaison
   Python, au choix).
3. Jouer les 72 situations ; pour chacun des 34 points de règle, écrire dans `docs/moteur-combos/reponses-oracle.md` :
   réponse de l'oracle, situations qui l'appuient, confiance, ou « non testable par l'oracle ».
4. **Trois colonnes à comparer** : lecture supposée, verdict du relecteur, réponse de l'oracle. Lister les désaccords
   en tête du fichier.

**Si l'installation échoue** (build, dépendances, réseau) : s'arrêter proprement, écrire ce qui a été tenté et ce qu'il
manque dans `reponses-oracle.md`. Ne pas contourner, ne rien installer au niveau du système (Thomas le fait).

## Critères
Rien de Project Ignis dans le dépôt (`git status` propre hors `docs/moteur-combos/reponses-oracle.md` et
`docs/moteur-combos/chronometrage.md`) ; chaque point de règle a une réponse ou la mention « non testable » ;
désaccords listés ; temps noté dans `chronometrage.md` (section à toi, ne réécris pas celle du lot 18). Ne pas
pousser, ne pas fusionner : l'orchestrateur fusionne dans `claude/moteur-18-11`.
