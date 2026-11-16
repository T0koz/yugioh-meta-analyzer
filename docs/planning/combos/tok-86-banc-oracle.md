# TOK-86 — Banc d'oracle Project Ignis en local

Modèle : Sonnet. **Agent séparé** : cette session ne formalise ni ne code le moteur de combos, et aucun agent qui
formalise ou code le moteur ne lit son code ni le code de Project Ignis (décision du 16/11). Elle ne produit que des
**résultats** (données), jamais du code destiné au moteur.

**But** : faire jouer à un moteur de référence (Project Ignis / EDOPro, cœur `ygopro-core` et scripts de cartes) les
situations de `docs/moteur-combos/tests-branded.yaml`, pour répondre automatiquement à une partie des 34 points de
règle (`points-de-regle-a-valider.md`) avant le retour du juge.

**À faire**
1. Installer l'oracle **hors du dépôt** (dossier à part, par ex. `~/code/oracle-ignis/`, jamais commité dans ce
   dépôt public). Respecter les licences (AGPL / GPL) : usage local, aucune copie de leur code dans ce dépôt.
2. Un petit lanceur, dans ce même dossier hors dépôt, qui place l'état de départ d'une situation et demande à
   l'oracle si l'action est légale / quel est l'état d'arrivée.
3. Jouer les 72 situations ; pour chacun des 34 points de règle, écrire dans
   `docs/moteur-combos/reponses-oracle.md` : réponse de l'oracle, situations qui l'appuient, confiance, et
   « non testable par l'oracle » quand c'est le cas.
4. Comparer aux « lectures supposées » : liste des désaccords, à soumettre en priorité au juge.

**Si l'installation échoue** (build, dépendances, réseau) : s'arrêter proprement, écrire ce qui a été tenté et ce
qu'il manque dans le compte rendu. Ne pas contourner.

**Critères** : rien de Project Ignis dans le dépôt (`git status` propre hors `docs/moteur-combos/reponses-oracle.md`) ;
chaque point de règle a une réponse ou la mention « non testable » ; désaccords listés ; temps noté dans
`docs/moteur-combos/chronometrage.md`.
