# Moteur de combos — journal de chronométrage (TOK-88)

> Décision du 16 novembre 2026 : chaque étape est chronométrée pour calibrer les estimations futures.
> Une ligne par étape, ajoutée à la fin de la session qui l'a faite. Ne pas réécrire les lignes passées.

## Comment lire ces durées

- Les heures viennent de la commande `date`, lancée entre les étapes. La colonne « durée » est un
  **temps d'horloge** d'un agent (Claude), pas un temps de travail humain.
- Ce temps mesure la **rédaction**. Il ne contient ni la relecture par Thomas, ni la validation par un
  juge, ni les corrections qui en sortiront : ce sont elles qui coûteront le plus, et elles ne sont
  pas encore mesurées.
- Pour calibrer, la bonne unité est donc double : temps d'agent (ci-dessous) + temps humain de
  validation (colonne à remplir).

## Session du 16 novembre 2026 — préparation (TOK-85, TOK-87)

| # | Étape | Début | Fin | Durée (agent) | Produit | Temps humain de validation |
|---|---|---|---|---|---|---|
| 1 | Lecture des décisions, de la mémoire du projet et des tickets Linear TOK-85 et TOK-87 | 16:36:33 | ≈ 16:38 | ≈ 1 min 30 | rien d'écrit | — |
| 2 | Choix du deck source (comparaison des decks Branded TCG légaux), lecture des textes de ses cartes (33 textes pour 37 cartes distinctes), contrôle de représentativité | ≈ 16:38 | 16:40:50 | ≈ 2 min 45 | deck retenu ; 4 cartes sans texte repérées | à mesurer (D1) |
| 3 | Script d'extraction en lecture seule + définitions formelles et schéma (TOK-85) | 16:40:50 | 16:43:40 | 2 min 50 | `scripts/combos_extract_deck.py`, `deck-branded-source.json`, `definitions-et-schema.md` | à mesurer |
| 4 | Jeu de tests : 72 situations en YAML, contrôle automatique (syntaxe, alias, numérotation) (TOK-87) | 16:43:40 | 16:48:46 | 5 min 06 | `tests-branded.yaml` | à mesurer (juge, TOK-89) |
| 5 | Mode d'emploi du jeu de tests, 33 points de règle pour le juge, 9 formulaires de décision, vérification des chiffres cités | 16:48:46 | 16:51:21 | 2 min 35 | `jeu-de-tests-branded.md`, `points-de-regle-a-valider.md`, `decisions-a-prendre-tok-85-87.md` | à mesurer |
| 6 | Journal de chronométrage, section TOK-84 du backlog | 16:51:21 | voir total | — | `chronometrage.md`, `BACKLOG.md` | — |
| | **Total de la session** | 16:36:33 | ≈ 16:53 | **≈ 17 min** | 8 fichiers créés, `BACKLOG.md` modifié | |

Les bornes des étapes 1 et 2 sont approximatives : l'heure n'a pas été relevée entre les deux.

## Session du 16 novembre 2026 — cartes manquantes (décision D8)

| # | Étape | Début | Fin | Durée (agent) | Produit | Temps humain de validation |
|---|---|---|---|---|---|---|
| 7 | Lecture de `fetch_cards.py` et `init_db.py`, téléchargement, comparaison à la base sans écrire | ≈ 16:53 | ≈ 16:58 | ≈ 5 min (dont 2 min perdues sur une requête de contrôle trop lente, arrêtée) | diagnostic : 3 cartes absentes, 1 mal nommée | — |
| 8 | Insertion des 288 cartes nouvelles (dont un doublon de nom, retiré après relecture : 287 nettes), correction d'un nom, contrôle d'intégrité, test de fumée de l'API | ≈ 16:58 | ≈ 17:02 | ≈ 4 min | `cards` : 13 797 → 14 085 | — |
| 9 | Lecture des 4 textes, correction de 14 situations, mise à jour des documents | ≈ 17:02 | ≈ 17:09 | ≈ 7 min | version 2 du jeu de tests, 34 points de règle | à mesurer |

Heures approximatives : seule l'heure de 17:07:32 a été relevée pendant cette session.

**Leçon pour les estimations** : quatre textes de cartes ont obligé à retoucher 14 situations sur 72
(19 %), dont une qui était fausse (T02). Une carte ajoutée au périmètre ne coûte pas seulement sa
formalisation : elle remet en cause les listes exactes des tests existants.

## Session du 16 novembre 2026 — pipeline des cartes et dossier du juge (D8 bis, TOK-89)

| # | Étape | Début | Fin | Durée (agent) | Produit | Temps humain de validation |
|---|---|---|---|---|---|---|
| 10 | Lecture du job du lundi, écriture de `fetch_new_cards.py`, branchement, test sur une copie puis sur la base | 17:16:06 | ≈ 17:17 | ≈ 1 min 30 | 1 script, 2 scripts modifiés | relecture par l'agent `gardien-donnees` (≈ 2 min) : 0 défaut bloquant, 5 mineurs dont un doublon créé par l'étape 8 |
| 11 | Dossier du juge : questionnaire généré depuis les 34 points, messages de contact | ≈ 17:17 | 17:18:05 | ≈ 30 s | `dossier-juge.md` | **temps du juge : à mesurer, c'est la donnée qui manque** |

## Ratios utiles pour les estimations futures

| Mesure | Valeur | Remarque |
|---|---|---|
| Cartes lues (texte officiel) | 33 cartes du deck + 7 cartes voisines | ≈ 3 min, lecture seule, sans formalisation |
| Situations de test écrites | 72 en ≈ 5 min | ≈ 4 s par situation côté agent. **Non validées** : le coût réel est la validation |
| Points de règle à faire trancher | 33 pour 33 cartes lues | presque **un point de règle par carte** : c'est l'indicateur à suivre pour estimer la charge du juge sur 13 800 cartes |
| Cartes du deck sans texte dans la base | 4 sur 37 (11 %) | bloquant pour J1 |

## Ce que cette session n'a pas mesuré

- le temps de **formalisation** d'une carte (aucune carte n'a été formalisée) : c'est l'estimation
  « plusieurs centaines d'heures » du § 9 des décisions, à mesurer sur un lot ;
- le temps du **juge** par point de règle et par test ;
- le temps de **correction** après validation.

## Modèle de ligne à recopier

```
| n | Étape | début | fin | durée (agent) | produit | temps humain de validation |
```

## TOK-86 (2026-11-17)

| Étape | durée (agent) | produit |
|---|---|---|
| Installation de l'oracle | ≈ 10 min, arrêtée | échec : cœur hors organisation officielle, `premake5` et Lua absents ; voir `reponses-oracle.md` |

## Session du 18 novembre 2026 — lot 18, fondations du moteur (TOK-85)

| # | Étape | Début | Fin | Durée (agent) | Produit | Temps humain de validation |
|---|---|---|---|---|---|---|
| 12 | Lecture du brief, de `CLAUDE.md`, `context.md` et des 6 documents du moteur ; contrôle des 45 empreintes de texte | 01:14 | ≈ 01:20 | ≈ 6 min | rien d'écrit ; 45 empreintes identiques | — |
| 13 | Report de la relecture dans `definitions-et-schema.md` (D3 entre-deux, trois formes de limite, Cimetière, limite de 3, cible, boucle) | ≈ 01:20 | ≈ 01:23 | ≈ 3 min | § 1, 2.1 à 2.6 mis à jour | à mesurer (Thomas) |
| 14 | Schéma SQL, modèle de l'état, chargement du deck, départs, classement, harnais | ≈ 01:23 | 01:27 | ≈ 4 min (premier lancement du harnais vert) | `moteur_combos/` (7 modules), `scripts/combos_harnais.py` | — |
| 15 | Tests `pytest` (46), branchement dans `check.py`, § 3 du document, décisions par défaut, `context.md`, `BACKLOG.md` | 01:27 | 01:31 | ≈ 4 min | 4 fichiers de tests, `decisions-prises.md` | à mesurer (formulaire du 18/11) |
| 16 | Relecture du schéma par l'agent `gardien-donnees` (en parallèle de l'étape 15) | ≈ 01:30 | ≈ 01:33 | ≈ 3 min | 3 défauts bloquants, ≈ 15 mineurs | — |
| 17 | Corrections (garde-fou, migrations, `copy_index`, `CHECK`, index, errata des effets), 4 tests de plus, `check.py` complet | ≈ 01:33 | 01:37 | ≈ 4 min | 50 tests verts, `check.py` vert sans étape ignorée | — |
| | **Total de la session** | 01:14 | ≈ 01:38 | **≈ 24 min** | 72 tests classés (54 / 6 / 12), 0 règle de jeu | |

**Leçon** : la relecture par un second agent a trouvé 3 défauts bloquants en 3 minutes, dont un garde-fou
contournable (disque insensible à la casse : `Yugioh.db` est le même fichier que `yugioh.db`). Le coût d'une
relecture est faible devant celui d'une écriture accidentelle dans la base de référence.

