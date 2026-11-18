# J2 — le moteur retrouve-t-il seul les combos des guides ? (lot C3, TOK-119 ; lot J2 plein, TOK-140)

> **18/11/2026.** § 0 et § 8 : **lot J2 plein** (jalon n°5, branche `claude/jalon-5-moteur-j2-plein-53a6ad`), 10 combos,
> **verdict en attente de l'oracle (jalon n°6)**. § 1 à § 7 : lot C3 (agent Opus, branche
> `claude/c3-j2-exploration-ff7592`), inchangés. Rien n'est poussé. Commande : `python scripts/combos_j2.py` (options
> du passage long au § 8.6) ; export pour l'oracle : `python scripts/combos_export_oracle.py <sortie.json>`.

## 0. Lot J2 plein (TOK-140, jalon n°5) : protocole écrit avant le passage long

> Écrit et commité **avant** le passage à budget long (avis `data-scientist-ygo` du 18/11). Les résultats viendront
> au § 8 ; ce paragraphe ne change plus.

- **Combos** : G1-G5 (lot C3, mis au point en les connaissant : combos de développement) et G6-G10 (figés par le commit
  TOK-139 `f19f864` avant toute exécution : **seul test hors échantillon**). Deux lignes séparées, le total sur 10 vient
  en second.
- **Condition principale (déclarée au lot C3, inchangée)** : parcours en largeur sans cible, 60 s, profondeur 16, filtres
  D4 ; « retrouvé » = cible remplie **et** jalons en sous-suite ; pour G6-G10, cible évaluée sur un état d'où le tour
  peut se terminer. Trois issues par combo : retrouvé / plateau atteint par un autre chemin / non trouvé.
- **G6 compte tel que figé** (cible inatteignable, erreur de transcription) dans le chiffre principal ; le résultat après
  la correction `73cc104` (une condition retirée, cible plus facile) est donné à côté, jamais seul.
- **Secondaires** : recherche dirigée vers la cible (120 s) ; joueur au hasard (60 s, test exact apparié) ; base naïve
  plus forte : largeur **sans** les filtres D4 (60 s) ; main réelle de 5 cartes (à part).
- **Passage long, exploratoire, décidé après avoir vu les échecs de G7, G8, G10 en 120 s** : recherche dirigée, 900 s
  de budget, sur **les 10 combos et G6 figé**, un processus par combo (plusieurs cœurs), même code, même cible, mêmes
  jalons ; on rapporte le palier (60, 120, 900 s), les états explorés et le temps CPU. **Aucune heuristique guidée par
  les jalons** : elle ne mesurerait plus « seul » (hors J2).
- Accélération du code : mémoïsation exacte de la clé de tri de l'empreinte d'état (×1,24 mesuré sur G8, mêmes
  empreintes, test `test_multi_memoise_identique`).

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

## 8. Lot J2 plein (TOK-140) : résultats du 18/11

### 8.1 En bref

| Mesure (condition principale du § 0 : largeur sans cible, 60 s) | G1-G5 (développement) | G6-G10 (figés, hors échantillon) | Total sur 10 |
|---|---|---|---|
| **Retrouvés tel que figé** (G6 compté manqué) | **4 sur 5** [37,6 ; 96,4] | **1 sur 5** [3,6 ; 62,4] | **5 sur 10** [23,7 ; 76,3] |
| Retrouvés, G6 après correction (cible plus facile, jamais seul) | 4 sur 5 | 2 sur 5 [11,8 ; 76,9] | 6 sur 10 [31,3 ; 83,2] |
| Recherche dirigée vers la cible, 120 s (G6 figé / corrigé) | 5 sur 5 | 2 / 3 sur 5 | 7 / 8 sur 10 |
| Recherche dirigée, 900 s (passage long, exploratoire) | 5 sur 5 | 3 / 4 sur 5 (+ G7) | 8 / 9 sur 10 |
| Joueur au hasard, 60 s (séquence au moins une fois) | 1 sur 5 (G5 : 3 parties sur 1 016) | 1 sur 5 (G9 : 2 sur 10 296) | 2 sur 10 |
| Base naïve plus forte : largeur **sans** les filtres D4, 60 s | 0 sur 5 (plateau seul : G1, G4, G5) | 0 sur 5 (plateau seul : G6) | 0 sur 10 [0 ; 27,8] |
| Recherche guidée par la solution (jalons du guide, **hors J2**) | — | G7, G8, G10 : séquences jouables dans le moteur | — |

Intervalles de Wilson à 95 % entre crochets. Écrire « sur ces 10 combos », jamais « taux de réussite du moteur » : guides
choisis par commodité (pages lisibles en texte), 10 pseudonymes sur une seule source (masterduelmeta), lignes qui se
recopient en partie (6 combos sur 10 passent par `Ecclesia and the Dark Dragon`) : le n efficace est inférieur à 10.

**Tests exacts appariés (McNemar)** sur les 10 combos, condition principale : contre le joueur au hasard, 3 combos
retrouvés par le moteur seul et aucun par le hasard seul, p = 0,25 (4 contre 0, p = 0,125 avec G6 corrigé) ; contre
la largeur sans filtres, 5 contre 0, p = 0,06. **Aucun écart n'est démontré à n = 10** : le hasard est une base faible,
mais 10 combos appariés ne suffisent pas à le prouver.

### 8.2 Combo par combo

« Tr. » : transitions de la séquence trouvée. ✓ séquence (cible **et** jalons) ; ◐ plateau atteint par un autre
chemin, sans les jalons ; ✗ rien. Secondes de machine chargée (4 à 6 processus en parallèle) : comparer les états.

| Combo | Tr. | Largeur 60 s | Dirigée 120 s | Dirigée 900 s | Guidée (hors J2) | Hasard 60 s | Sans filtres 60 s |
|---|---|---|---|---|---|---|---|
| G1 Nadir seule | 5 | ✓ 10 704 états | ✓ 298 | ✓ | — | 0 / 947 | ◐ |
| G2 White → EDD → Granguignol | 8 | ✗ (temps) | ✓ 11 849 | ✓ | — | 0 / 3 053 | ✗ |
| G3 White → Quem → Three Champions | 6 | ✓ 19 853 | ✓ 33 455 | ✓ | — | 0 / 3 297 | ✗ |
| G4 White → Dogmatika Ecclesia | 5 | ✓ 13 123 | ✓ 552 | ✓ | — | 0 / 926 | ◐ |
| G5 Nadir seule, sous Droll | 4 | ✓ 3 959 | ✓ 174 | ✓ | — | **3** / 1 016 | ◐ |
| **G6 Branded Fusion, figé** | — | ✗ | ✗ | ✗ **épuisé** (33 958 états, exploration complète) | — | 0 | ✗ |
| G6 corrigé | 7 | ✓ 3 929 | ✓ 401 | ✓ | — | 0 / 246 | ◐ |
| G7 Aluber + Fuwalos → Mirrorjade | 11 | ✗ (temps) | ◐ | ✓ **219,6 s**, 150 683 états | ✓ 6 236 | 0 / 1 272 | ✗ |
| G8 Aluber + Albaz | 11 | ✗ (temps) | ✓ 73 446 (56,8 s) | ✓ | ✓ 454 | 0 / 1 419 | ✗ |
| G9 Gold Sarcophagus | 6 | ✓ 6 524 | ✓ 880 | ✓ | — | **2** / 10 296 | ✗ |
| G10 Aluber + White → Granguignol | 9 | ✗ (temps) | ◐ | ◐ 1 080 607 états (temps) | ✓ 93 095 (67,6 s) | 0 / 1 132 | ✗ |

Les nombres d'états de G1-G5 sont **identiques** à ceux du lot C3 (même code d'exploration, résultat déterministe) :
seules les secondes changent avec la charge de la machine.

**Ce qui fait échouer** : la longueur. Le parcours en largeur ne dépasse pas 6 transitions en 60 s (facteur 3 à 4 par
transition) ; les quatre combos manqués en largeur ont 8 à 11 transitions. G10 manqué même en 900 s mais **jouable**
(recherche guidée : 67,6 s) : limite de recherche, pas désaccord de règle. **Aucun manque n'est dû à une règle ou à une
carte non couverte** (0 branche « non couvert » sur tous les passages).

### 8.3 Main réelle de 5 cartes (à part du chiffre principal)

La main du guide + les cartes de réponse qu'un combo « à une carte » retire du jeu (Ash Blossom, Ghost Ogre). Dirigée
120 s : **7 sur 10** séquences (G1-G6, G9 ; G8 et G10 plateau seul, G7 rien) ; largeur 60 s : **5 sur 10** (G1, G3,
G5, G6, G9). **Ce que fait le moteur des cartes de réponse** : il ne les active jamais (filtre D4) ; une seule fois il
s'en sert comme matériel (G3, dirigée : `Ghost Ogre` matériel de Synchro, séquence de 7 transitions au lieu de 6) ;
ailleurs elles restent en main. Les cinq mains tirées au hasard du lot C3 (graine 20261118) redonnent les mêmes ordres
de grandeur (9 199 à 30 144 états en 60 s, profondeur 3 à 6, 0 non couvert).

### 8.4 Écarts entre les séquences trouvées et les guides

- **G7** : mêmes jalons, autres matériaux. `Ecclesia and the Dark Dragon` = `Aluber` + `The Golden Swordsoul` (guide :
  White + Golden Swordsoul) ; `The Golden Swordsoul` Invoque `Cartesia` du Deck ; `The Three Champions of Swordsoul` =
  White + Cartesia (guide : Incredible Ecclesia + Aluber) ; `Quem` ramène White. En 120 s, le moteur atteint le plateau
  de G7 par un chemin plus court **sans** `The Golden Swordsoul` (Kitt ramène Incredible Ecclesia) : à faire juger par
  l'oracle (règle mal codée, ou ligne réelle ? piste J3).
- **G8** : mêmes actions, coûts permutés : `Branded in High Spirits` envoie `Titaniklad`, White paie `Rindbrumm`,
  `Granguignol` envoie `Dogma`, `The Fallen & The Virtuous` paie `Albion the Sanctifire Dragon` ; `Quem` ramène `Cartesia`.
- **G10** (recherche guidée) : `Aluber` cherche `Branded Fusion` (substitution déclarée de `Branded in Red`),
  `Granguignol` envoie `Albion the Sanctifire Dragon` (substitution de `Lubellion`).
- G6, G9 : séquences conformes au guide (substitution d'`Albion the Branded Dragon` par `Albion the Sanctifire Dragon`).

### 8.5 Erreurs trouvées pendant le lot (toutes signalées)

1. **Transcription de G6** (document figé) : « Cocatorium au Cimetière » ; corrigé par le commit séparé `73cc104`.
   Une cible erronée sur cinq : les autres cibles sont à faire vérifier par l'oracle aussi (avis `data-scientist-ygo`).
2. **Traduction du jalon (10) de G8** (code, pas le document) : « une carte arrive du Cimetière » comptait le solde net du
   terrain, masqué par la destruction de `The Fallen & The Virtuous` dans la même transition ; jalon impossible. Corrigé
   (`Mouvement(None, …)` : au moins un nom arrive), test ajouté, G8 rejoué en entier. Avant la correction : plateau
   seul en 120 s et en 900 s (892 060 états) ; après : séquence en 56,8 s.
3. **Borne de 200 000 états** (réglage par défaut, absente du protocole écrit) : elle avait arrêté G8 et G10 vers 130 à
   165 s du passage long. Relancés avec la borne levée (3 millions), 900 s pleines ; mémoire ≤ 1 Go par processus.

### 8.6 Passage long et accélération

`python scripts/combos_j2.py --guides G7 --secondes 900 --sans-largeur --sans-hasard --sans-main-reelle --mains 0
--max-etats 3000000 --largeur-sans-filtres --largeur 60` (un processus par combo, 3 à 6 cœurs) ; `--avec-g6-fige` ajoute
G6 tel que figé ; `--guidee` lance le diagnostic guidé par la solution (hors J2). Mémoïsation exacte de la clé de tri de
l'empreinte : ×1,24 (375 → 460 états/s sur G8, mêmes empreintes). Débit observé : 700 à 1 230 états par seconde de
temps CPU selon le combo.

### 8.7 Réserves (en plus de celles du § 5)

1. **Le chiffre hors échantillon est 1 sur 5** (G9) : c'est le seul résultat qui ne dépend d'aucune décision prise après
   avoir vu les données. Le reste (G6 corrigé, 900 s, recherche guidée) est exploratoire.
2. **Le résultat dépend de la longueur des combos choisis** : de 4 à 7 transitions, la largeur les retrouve tous (6 sur
   6, G6 corrigé compris) ; de 8 à 11 transitions, aucun (0 sur 4).
3. **Aucune séquence n'est vérifiée** : 23 séquences distinctes exportées pour l'oracle (`sequences-pour-oracle.md`) ;
   tant qu'il ne les a pas rejouées, ce sont des candidates. Cartes `formalisee`, aucune `verifiee`.
4. **Jalons traduits par la session qui exécute** : le texte des jalons est figé avant exécution, leur traduction en
   code a été écrite ensuite (et corrigée une fois, § 8.5 point 2). L'oracle doit rejouer les séquences, pas les jalons.
5. Charge machine variable (3 à 6 explorations en parallèle) : les secondes ne se comparent pas d'un passage à l'autre.

### 8.8 Verdict

**J2 : en attente de l'oracle, jalon n°6.** Horloge de la règle d'arrêt (13/01/2027) maintenue. Ce que le lot établit
côté moteur : les combos de 4 à 7 transitions sont retrouvés seuls ; les combos de 9 à 11 transitions sont jouables
dans le moteur (G7, G8, G10) mais ne sont retrouvés qu'avec une cible (G8 en 120 s, G7 en 900 s) ou un guidage (G10).

