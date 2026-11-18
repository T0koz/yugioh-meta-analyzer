# J2 — le moteur retrouve-t-il seul les combos des guides ? (lot C3, TOK-119)

> **18/11/2026**, agent du lot C3 (Opus), branche `claude/c3-j2-exploration-ff7592`. Rien n'est poussé ni fusionné.
> Commande : `python scripts/combos_j2.py` (≈ 12 min avec les budgets ci-dessous ; `--sans-ecriture` pour ne rien
> écrire). Combos relevés : [`combos-guides.md`](combos-guides.md). Méthode du taux : avis de `data-scientist-ygo`.

## 1. En bref

| Mesure | Valeur |
|---|---|
| Combos de guides relevés | **5** (6 pages publiques datées, juin à août 2026, 4 auteurs) ; aucun n'est entièrement réalisable avec la liste du pilote (cartes absentes, § 4) |
| **Parcours en largeur, sans cible** (chiffre principal) | **4 sur 5** séquences retrouvées en 60 s au plus (Wilson 95 % : 37,6 à 96,4 %) ; G2 manqué (borne de temps) |
| Recherche dirigée vers le plateau du guide | **5 sur 5** séquences retrouvées, de 0,1 à 25 s (Wilson 95 % : 56,6 à 100 %) |
| Méthode naïve : joueur au hasard, même budget (60 s) | **0 sur 5** en séquence (G5 : 8 parties sur 3 725 ; les 4 autres : 0 sur plus de 3 200 parties chacune) |
| Erreur de règle mise en évidence par les guides | **0** : chaque séquence de guide réalisable avec la liste est légale pour le moteur |
| Branches « non couvert » rencontrées | **0** (les 37 cartes du pilote sont formalisées ; l'exploration ne touche que la liste) |
| Verdict | **J2 atteint sous réserve**, horloge de la règle d'arrêt (13/01/2027) **maintenue** (§ 6) |

Écrire « 4 sur 5 », jamais « 80 % » : n = 5, guides non tirés au hasard (§ 5).

## 2. Ce qui a été construit

- **Exploration** (`moteur_combos/exploration.py`) : le moteur de règles n'est pas modifié. Une transition se complète
  de toutes les façons légales par **rejeu** : le script d'exploration répond selon un préfixe, et à la première
  décision non couverte il rend la liste des options ; une relance par option. Graphe d'états dédoublonnés par
  l'empreinte complète (§ 2.3 des définitions) ; bornes de profondeur, de temps, de nombre d'états ; deux stratégies,
  **largeur** (chemins les plus courts, aucune indication) et **cible** (priorité de type A* : profondeur + exemplaires
  de la cible manquants). La stratégie change l'ordre de développement, jamais les actions légales.
- **Filtres déclarés (D4)**, enregistrés avec chaque exploration (`cb_run.filters_json`) : pas de réponse à ses
  propres maillons ; cartes de réponse (`Ash`, `Ghost Ogre`, `Droll`, `Fuwalos`) jamais activées ni Invoquées
  Normalement ; position Attaque ; Zone Monstre Extra d'abord ; pas de changement d'Attribut ; `Luluwalilith` sans
  annulation de soi ; `Aeon` sans bannissement ; pioche à une branche. Exhaustivité « à filtres près ».
- **« Non couvert » (D5)** : une option non couverte n'est jamais cachée ; elle est rejouée, le moteur rend
  `non_couvert`, la branche s'arrête et l'exploration est marquée incomplète.
- **Stockage** (`moteur_combos/stockage_combos.py`, schéma inchangé) : runs, chemins retenus (combos), transitions,
  pas, cartes des pas, relations dérivées. Requêtes du ticket : `combos_passant_par(con, X)` et
  `a_puis_directement_b(con, A, B)` (§ 3.6 des définitions) ; un micro-combo est un segment de `cb_combo_step`. Sur la
  base du passage définitif : 261 combos passent par `Guiding Quem`, 5 jouent `Nadir Servant` puis directement
  `Fallen of the White Dragon`.
- **Bug trouvé en route** (corrigé, test dédié) : une décision à une seule option consommait une entrée du préfixe au
  rejeu ; des branches entières disparaissaient **sans erreur** (le premier essai de G1 « épuisait » 60 000 états sans
  trouver la cible). Trouvé en rejouant la séquence du guide pas à pas.

## 3. Combos des guides : retrouvés / manqués

Main : la carte de départ seule ; les 4 autres cartes de la main sont retirées du jeu (§ 5). Budgets : dirigée 120 s,
largeur 60 s, profondeur 16. « Séquence » = plateau du guide **et** jalons du guide dans l'ordre.

| Combo | Dirigée | Largeur (sans cible) | Hasard (60 s) | Transitions | Ce qui manque (après la partie réalisable) |
|---|---|---|---|---|---|
| G1 Nadir seule | ✓ 0,19 s, 298 états | ✓ 8,2 s, 10 704 états | 0 / 3 581 | 5 | carte absente (`Albion the Branded Dragon`, `Branded Retribution`, `Khaos Starsource`) |
| G2 White → EDD → Granguignol | ✓ 8,5 s, 11 849 états | **✗** 60 s, 70 931 états (borne de temps) | 0 / 3 292 | 8 | borne (largeur) ; puis carte absente (`Albion the Branded Dragon`, `Branded in Red`) |
| G3 White → EDD → Quem → Three Champions → Granguignol | ✓ 25,1 s, 33 455 états | ✓ 15,1 s, 19 853 états | 0 / 3 359 | 6 | carte absente (`Albion the Branded Dragon`) |
| G4 White → Dogmatika Ecclesia → Quem | ✓ 0,35 s, 552 états | ✓ 9,7 s, 13 123 états | 0 / 3 340 | 5 | carte absente (`Albion the Branded Dragon`) |
| G5 Nadir seule, sous Droll | ✓ 0,11 s, 174 états | ✓ 2,8 s, 3 959 états | 8 / 3 725 | 4 | page incomplète (aucune séquence au-delà) |

**Aucun manque n'est dû à une règle ni à une carte non couverte** : un manque de borne (G2 en largeur), les autres
sont des cartes absentes de la liste (décision D1). Aucun guide relevé ne passe par `Lubellion the Searing Dragon`.

**Différences avec les guides** (le moteur trouve la séquence, parfois raccourcie) :
- G1 : `Dogmatika Ecclesia` cherche directement `The Fallen & The Virtuous`, que le moteur active en Phase de Fin ; la
  seconde copie ajoutée par `Dogma` dans le guide n'est pas nécessaire (la Pose n'est pas codée : la carte reste en main).
- G3 : la page étiquette mal l'étape où White revient du Cimetière ; le chemin trouvé lève l'ambiguïté : c'est
  `Tri-Brigade Springans Kitt`, envoyé par `Quem`, qui ramène White.
- Coûts payés à la place d'`Albion the Branded Dragon` (substitution déclarée) : `Albion the Sanctifire Dragon`,
  `Titaniklad`, `Despian Luluwalilith` selon le chemin.
- Premier essai sans jalons : pour G3, la cible était remplie par un autre chemin (Three Champions envoyée en coût par
  White au lieu d'être Invoquée par Synchro) ; d'où les deux niveaux « plateau » et « séquence ».

## 4. Temps de calcul et mains réalistes

≈ 1 200 états par seconde (≈ 3 rejeux de transition par état), un seul cœur, Python. L'espace croît d'un facteur 3 à
4 par transition : un parcours en largeur ne dépasse pas 6 transitions en 60 s depuis une main de 5 cartes.

Cinq mains de 5 cartes tirées au hasard dans la liste (graine 20261118), parcours en largeur, 60 s chacune :

| Main | États | Plateaux finaux distincts | Profondeur atteinte | Non couvert |
|---|---|---|---|---|
| 2 × Aluber, Ash, Droll, Quem | 24 188 | 727 | 6 | 0 |
| Albaz, Gold Sarcophagus, Fuwalos, Nadir, Super Polymerization | 38 518 | 93 | 4 | 0 |
| Aluber, Branded in High Spirits, Droll, Albaz, The Fallen & The Virtuous | 25 323 | 69 | 4 | 0 |
| Aluber, Ash, Droll, Ghost Ogre, Incredible Ecclesia | 28 045 | 841 | 6 | 0 |
| Cartesia, Droll, Incredible Ecclesia, Super Polymerization, The Fallen & The Virtuous | 30 308 | 385 | 6 | 0 |

Aucune de ces explorations n'est complète (borne de temps) : les plateaux listés sont ceux des 4 à 6 premières
transitions, pas les meilleurs possibles. 200 chemins au plus par main sont écrits dans `combos.db`.

## 5. Réserves (obligatoires, avis `data-scientist-ygo`)

1. **Sélection** : les guides sont les seules pages lisibles en texte, pas un tirage ; 4 auteurs pour 5 combos (combos
   non indépendants). Wilson les suppose indépendants : l'incertitude réelle est plus large.
2. **Combos tronqués** : on s'arrête à la dernière étape réalisable avec la liste, avec une substitution déclarée ; on
   teste des combos plus courts (4 à 8 transitions) que ceux des guides.
3. **Cible fournie par le guide** (recherche dirigée) : elle mesure qu'un plateau est atteignable, pas que le moteur
   découvre le combo. C'est pourquoi le chiffre principal est celui du parcours en largeur, sans cible.
4. **Jalons écrits par l'agent qui connaissait la réponse**, ajoutés après l'écart de G3 : critère ajusté sur le
   résultat. Le parcours en largeur s'arrête pourtant sur le premier état qui remplit la cible **et** passe les jalons.
5. **Main d'une seule carte** : pas une main réelle ; avec 4 cartes de réponse en main, le moteur prenait `Ghost Ogre`
   comme matériel (G2), le combo n'était plus « à une carte ».
6. **Filtres D4** : ils injectent une connaissance du jeu et peuvent écarter des lignes légales.
7. **Formalisation non vérifiée** : toutes les cartes sont `formalisee`, aucune `verifiee` ; les combos sont étiquetés
   `non_verifie` en base. Le volet humain de J1 (20 effets) attend toujours un relecteur.

## 6. Verdict et suite

**J2 atteint sous réserve ; horloge du 13/01/2027 maintenue.** Pour un J2 plein (proposition du data scientist) :
- figer la cible et les jalons de chaque combo dans un fichier commité **avant** l'exécution, écrits par un humain ou
  rejoués par l'oracle ;
- au moins 5 combos de plus, d'autres auteurs (les tableurs en images, transcrits par un joueur ; les lignes `Aluber`
  et `Branded Fusion` du § 4 de `combos-guides.md`) ;
- un essai avec des mains de 5 cartes ;
- continuer à battre nettement le joueur au hasard (aujourd'hui 0 sur 5 contre 4 sur 5).

**Combos hors guides (piste J3, à faire vérifier par un joueur, non jugés)** — plateaux les plus fournis des mains
réalistes (tri d'affichage : nombre de monstres) :
- `Aluber` (Invocation Normale) → `Branded Fusion` → `Rindbrumm` avec `Fallen of the White Dragon` et `Tri-Brigade
  Springans Kitt` pris dans le Deck → `Kitt` ramène White → White Invoque `Dogmatika Ecclesia` → recherche ; 5 monstres
  en 4 transitions (mains 1 et 4). C'est une ligne connue des joueurs, pas une découverte, à confirmer comme telle.
- `Blazing Cartesia` (Invocation Normale) → Fusion `Granguignol` (avec `Incredible Ecclesia` de la main) qui envoie
  `Despian Luluwalilith` → `The Fallen & The Virtuous` ramène Cartesia → Phase de Fin : `Luluwalilith` Invoque `Quem`,
  `Quem` envoie `Tri-Brigade Springans Kitt` (main 5). Ligne non citée par les guides relevés : **candidate J3**.
- `Aluber` → `Branded Opening` (`Incredible Ecclesia` défaussée, `Quem` du Deck en Défense) → `Quem` envoie
  `Tri-Brigade Springans Kitt`, qui ramène `Incredible Ecclesia` du Cimetière (elle mentionne Albaz ; seul choix, donc
  pris automatiquement) → `Incredible Ecclesia` se Sacrifie pour White → White Invoque `Dogmatika Ecclesia` (main 4,
  5 monstres en 4 transitions). Vérifié en relisant le chemin ; à faire relire par un joueur.

## 7. Formulaire pour Thomas

```
C3 — Suite du moteur après J2
[x] Consolider J2 d'abord : un joueur transcrit 5 combos de plus (tableurs en images, lignes Aluber / Branded Fusion), cible et jalons figés avant exécution
[ ] Passer à J3 tout de suite (faire vérifier par un joueur les lignes hors guides du § 6)
[ ] Les deux en parallèle
Commentaire libre :

C3 — J3 (combo qu'aucun guide ne cite)
[x] Après J2 plein ; d'abord faire vérifier la ligne « Cartesia → Granguignol → Luluwalilith → Quem » (main 5) par un joueur
[ ] Lancer une recherche dédiée maintenant (explorations plus longues, la nuit)
Commentaire libre :

C3 — Extension à un deuxième deck
[x] Pas avant J2 plein et le volet humain de J1 (le coût est la formalisation et sa vérification, pas l'exploration)
[ ] Choisir un deuxième deck maintenant (lequel ?)
Commentaire libre :

C3 — Interface
[x] Rien d'affiché sur le site tant qu'aucune carte n'est `verifiee` ; une page interne (requêtes « passe par X », « A puis B ») pour le juge
[ ] Une page publique « combos » dès maintenant, étiquetée « non vérifié »
[ ] Pas d'interface avant J3
Commentaire libre :

C3 — Performance
[ ] Accélérer l'exploration (mémoïsation des transitions, plusieurs cœurs) avant d'ajouter des combos
[x] Seulement si les combos de J2 plein dépassent 8 transitions (les budgets actuels suffisent jusque-là)
Commentaire libre :
```
