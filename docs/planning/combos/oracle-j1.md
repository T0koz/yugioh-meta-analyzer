# Lot C2 bis — l'oracle rejoue les situations de J1 (TOK-86, mesure de TOK-118)

Modèle : Sonnet. **Agent séparé**, mêmes règles d'isolement que le lot 17 (`combos/tok-86-banc-oracle.md`) : cette
session ne formalise ni ne code le moteur, ne lit jamais `moteur_combos/` ni `docs/moteur-combos/cartes*` côté code ;
aucune session du moteur ne lit son code ni `~/code/oracle-ignis/`. Elle produit des **résultats** seulement.

Ajouté par l'orchestrateur le 18/11 : le brief de J1 (`combos/j1-formalisation.md`) prévoit que « l'oracle compare quand
il est disponible » ; le lot C2 a écrit ce qu'il faut lui demander dans `docs/moteur-combos/situations-pour-oracle.md`.

## À faire
1. Réutiliser l'installation du lot 17 (`~/code/oracle-ignis/`, cœur, scripts, base, lanceur). Ne rien installer au
   niveau du système.
2. Jouer les **30 situations J1** (`docs/moteur-combos/situations-j1.yaml`) et les **points N01 à N13** de
   `situations-pour-oracle.md` (priorité aux N, qui ne sont pas tranchés par le texte), avec les réglages du lot 17
   (rejouer R22 aussi sous `DUEL_TCG_SEGOC_FIRSTTRIGGER` si c'est utile, en le disant).
3. Écrire les réponses dans `docs/moteur-combos/reponses-oracle.md`, **dans une section nouvelle** « J1 (18/11) » :
   pour chaque situation, accord / désaccord / non testable, avec la liste proposée par le cœur ; pour chaque N, la
   réponse et la situation qui l'appuie. Désaccords en tête de la section. Signaler tout cas où l'oracle lit un texte
   OCG différent du texte TCG (précédent R23).
4. Compter : effets du pilote dont au moins un chemin contredit l'oracle (indicateur secondaire du rapport J1, § 4).

**Critères** : rien de Project Ignis dans le dépôt (`git status` propre hors `reponses-oracle.md` et ta section de
`docs/moteur-combos/chronometrage.md`) ; chaque situation et chaque N a une réponse ou « non testable » ; désaccords
listés ; temps noté. Ne pas pousser, ne pas fusionner : l'orchestrateur fusionne dans `claude/moteur-18-11`.
