# Moteur de combos — définitions formelles et schéma de données (TOK-85)

> **Statut : choix techniques arbitrés le 16 novembre 2026 (D1 à D8 bis), validés par Thomas le 17/11 (D3 révisée
> le 18/11) ; points de règle relus une fois le 17/11 (32 confirmés sur 34, un seul relecteur, non arbitre).**
> Part des définitions du § 4 de [`decisions-2026-11-16.md`](decisions-2026-11-16.md) et les précise.
> **Sources utilisées** : textes des cartes de la table `cards` (YGOPRODeck), règles officielles de
> Konami citées de mémoire (livret de règles, non relu en ligne pendant cette session), decklists de
> la base. **Aucun script de simulateur n'a été consulté** (condition d'indépendance, § 6 des décisions).
> **Limite** : je ne suis pas un juge. Tout point de règle marqué ⚖ est à soumettre à un juge humain
> (TOK-89). La liste complète est dans [`points-de-regle-a-valider.md`](points-de-regle-a-valider.md).
>
> **Mise à jour du 18 novembre 2026 (lot 18)** : report de la relecture 1 du 17/11
> ([`reponses-juge-2026-11-17.md`](reponses-juge-2026-11-17.md)) et de D3 révisée (« entre-deux ») ; schéma
> implémenté dans `moteur_combos/schema.sql` (base à part `data/combos.db`, ignorée par Git). Les passages
> modifiés portent la mention **(relecture 1)** ou **(lot 18)**. Aucune règle de jeu n'est codée : la
> consommation des limites, les verrous et la légalité restent à la tranche 0 (TOK-90).
>
> **Mise à jour du 18 novembre 2026 (tranche 0, TOK-90)** : premières règles de jeu codées dans
> `moteur_combos/regles.py` (Invocation Normale, Invocation Spéciale et Fusion, activation, coût, limites dans les
> cinq formes, chaîne simple), cinq cartes formalisées dans `moteur_combos/cartes.py`, situations traduites en
> scénarios dans `moteur_combos/scenarios.py`. Application de D5 au niveau de l'effet : voir § 3.4 (tranche 0).
>
> **Mise à jour du 18 novembre 2026 (J1, lot C2, TOK-118)** : les 37 cartes du pilote sont formalisées
> (`moteur_combos/cartes_j1.py`), règles ajoutées dans `regles.py` (R22 codé, Synchro, procédure, Phase de Fin…),
> statut `formalisee` durci (§ 3.4, J1). Rapport : [`j1-rapport.md`](j1-rapport.md).

Les exemples viennent du deck source du jeu de tests (voir
[`jeu-de-tests-branded.md`](jeu-de-tests-branded.md)), et les numéros `T..` renvoient à ses situations.

---

## 1. Vocabulaire minimal (pour lire la suite sans jouer)

| Terme | Sens |
|---|---|
| Zones | Main, Deck, Extra Deck (monstres Fusion, Synchro…), terrain (5 zones Monstre principales, 2 zones Monstre Extra, 5 zones Magie/Piège, 1 zone Terrain), Cimetière (« GY »), cartes bannies. |
| Invocation Normale | Poser un monstre de sa main : **une seule par tour**. |
| Invocation Spéciale | Toute autre façon de mettre un monstre sur le terrain. Pas de limite, sauf texte contraire. |
| Invocation Fusion | Invocation Spéciale d'un monstre de l'Extra Deck en envoyant au Cimetière les « matériels » listés sur lui. |
| Activation / résolution | Un effet est d'abord **activé** (on l'annonce, on paie son coût, on choisit ses cibles), puis **résolu** (il s'applique). Entre les deux, on peut lui répondre. |
| Chaîne | Pile d'effets activés en réponse les uns aux autres. Elle se résout en ordre inverse (le dernier activé s'applique en premier). |
| Vitesse | 1 : effets lents (ne répondent à rien). 2 : effets rapides (répondent). 3 : pièges de contre. |
| Coût / effet | Dans un texte, ce qui précède « ; » est le coût (payé à l'activation, jamais remboursé). Ce qui suit est l'effet. Ce qui précède « : » est la condition d'activation. |
| « Une fois par tour » | **Trois formes (relecture 1)** : *par nom de carte* (« You can only activate 1 "X" per turn » : une seule activation de la carte X, toutes copies confondues) ; *par effet et par nom* (« You can only use this effect of "X" once per turn », ou « each effect of "X" » : chaque effet de X une fois, toutes copies confondues, une autre copie peut encore utiliser un **autre** effet) ; *par exemplaire* (« Once per turn » : vaut pour cette carte-là). Les textes du deck ajoutent deux variantes, enregistrées à part : « You can only use 1 "X" effect per turn, and only once that turn » (un seul effet de X, tous effets confondus : `Aluber`, `Branded in High Spirits`, `Hyperinvoked Aeon`) et « You can only Special Summon "X" once per turn this way » (`Incredible Ecclesia`). Voir § 2.1 D. |
| Verrou | Restriction qui dure tout le tour (« you cannot Special Summon from the Extra Deck, except Fusion Monsters »). |

---

## 2. Les quatre définitions

### 2.1 État

**Définition.** L'état est la photo complète du jeu à un instant donné. Il doit être **suffisant** :
deux états identiques ont exactement les mêmes actions légales et les mêmes suites possibles, quel
que soit le chemin qui y a mené. Tout ce que le passé peut encore changer à l'avenir doit donc être
écrit **dans** la photo. C'est la propriété de Markov, et c'est elle qui rend l'équivalence (§ 2.3) valide.

La photo du § 4 des décisions (main, terrain, cimetière, bannies, deck, « une fois par tour »
consommés) est nécessaire mais **pas suffisante**. Les textes Branded obligent à y ajouter une
« mémoire du tour » et des attributs par exemplaire de carte. L'état a quatre blocs.

**A. Cadre**

- numéro du tour, joueur dont c'est le tour, phase (Pioche, Standby, Principale 1, Combat, Principale 2, Fin) ;
- points de vie des deux joueurs ;
- Invocation Normale du tour déjà utilisée (oui/non) ;
- pile de chaîne (vide dans un état stable, voir § 2.2) et effets déclenchés en attente ;
- **fenêtre d'interruption adverse** : champ réservé, toujours « aucune réponse » dans le pilote (§ 2.5).

**B. Zones, pour chaque joueur**

| Zone | Forme | Remarque |
|---|---|---|
| Main | multi-ensemble | L'ordre n'a pas de sens en jeu. |
| Deck | multi-ensemble **+ segments ordonnés connus** (dessus, dessous) | Après une recherche, le deck est mélangé : l'ordre disparaît. Mais `Springans Kitt` pose une carte **au-dessous** du deck : cette position est connue jusqu'au prochain mélange. |
| Extra Deck | multi-ensemble | |
| Zones Monstre | 5 principales par joueur (`M1` à `M5`, colonnes 1 à 5) + 2 **Zones Monstre Extra** (`ZME_G`, `ZME_D`), **toujours indexées** | **D3 révisée, « entre-deux » (relecture 1, Thomas le 18/11)** : l'état porte **toujours la case exacte** de chaque monstre. Les deux Zones Monstre Extra sont **communes aux deux joueurs** : elles appartiennent au terrain, pas au joueur, et chaque occupant porte son contrôleur. Géométrie enregistrée : `ZME_G` est dans la colonne 2, `ZME_D` dans la colonne 4 (vues depuis le joueur 0). Le relecteur a infirmé l'hypothèse « placer n'importe où » : la Zone Monstre Extra et les colonnes comptent, y compris pour des cartes adverses. Voir § 2.2 (option de placement) et D3. |
| Zones Magie/Piège, Terrain | indexées (`S1` à `S5`, colonnes 1 à 5, et `TERRAIN`) | |
| Cimetière | multi-ensemble | **Confirmé (relecture 1)** : l'ordre du Cimetière ne sert qu'à l'arbitre pour retracer la partie ; aucune carte connue du relecteur ne le lit. L'historique des transitions (`cb_transition`, `cb_step`) suffit à retracer l'ordre. À revoir si une carte modélisée lit l'ordre. |
| Bannies | multi-ensemble, face visible ou cachée | |

**C. Attributs de chaque exemplaire de carte** (une « instance », pas un nom)

- position (Attaque, Défense, face cachée), compteurs ; **case exacte** quand la carte est sur le terrain (D3 révisée, lot 18) ;
- **« Once per turn » déjà consommés par cet exemplaire** (forme *par exemplaire*, relecture 1) : c'est un attribut de
  l'exemplaire, pas de la mémoire du tour, puisqu'une autre copie garde le sien ;
- **comment et quand elle est arrivée** : posée ce tour ou non, par Invocation Normale, Spéciale, Fusion, Synchro ; venue de l'Extra Deck ou non ;
- **« correctement invoquée »** (oui/non) : un monstre de l'Extra Deck envoyé au Cimetière sans avoir été invoqué ne peut pas en être rappelé. Ce drapeau suit la carte au Cimetière et chez les bannies ;
- **« envoyée au Cimetière ce tour »** (plusieurs effets de Phase de Fin le lisent : `Titaniklad`, `Sprind`, `The Dragon that Devours the Dogma`, `Despian Luluwalilith`) ;
- modifications temporaires avec leur échéance : nom, Type, Attribut, Niveau, ATK (`Cocatorium` prend le nom d'un autre monstre « jusqu'à la Phase de Fin »), effets annulés ;
- carte posée face cachée ce tour (une Magie Jeu-Rapide posée ne s'active pas le tour même) ;
- restrictions portées par l'exemplaire (`Mirrorjade` : « ne peut pas utiliser cet effet au tour suivant »).

**D. Mémoire du tour** (ce que le passé interdit ou permet encore)

| Élément | Exemple Branded qui l'impose |
|---|---|
| « Une fois par tour » **par effet et par nom**, déjà consommés | « You can only use this effect of "Guiding Quem" once per turn » : clé (nom, n° d'effet) ; une autre copie de `Quem` peut encore utiliser l'**autre** effet (T24). |
| « Une fois par tour » **par nom, tous effets confondus** (variante) | `Aluber` : un seul des deux effets, une fois (T04). Clé : le nom seul. |
| Cartes dont le nom a déjà été **activé** ce tour (*par nom de carte*) | « You can only activate 1 "Branded Fusion" per turn » (T14), `Nadir Servant` (T21). Clé : le nom. |
| Invocations « this way » déjà faites (variante) | « You can only Special Summon "Incredible Ecclesia" once per turn this way ». Clé : le nom. |
| Verrous actifs | `Nadir Servant` : plus aucune Invocation Spéciale depuis l'Extra Deck (T20). |
| **Historique d'invocations depuis l'Extra Deck** | `Branded Fusion` : « the turn you activate this card » interdit de l'activer si une Synchro a **déjà** été invoquée ce tour (T12). Le passé rend l'action illégale après coup. |
| Événements du tour | « if a Fusion Monster(s) was sent to your GY this turn » (`Blazing Cartesia`, `Incredible Ecclesia`, `Branded in High Spirits`). |
| Effets différés | `Gold Sarcophagus` : « during your second Standby Phase after activation » ; `Ecclesia and the Dark Dragon` revient à la Phase de Fin. Ils traversent les tours. |
| Effets « appliqués ce tour » | `Mulcharmy Fuwalos`. |

**Enregistrement des limites (lot 18).** Une limite consommée s'écrit `(forme, nom, effet)` : `forme` parmi
`activation_par_nom`, `par_nom_effet`, `par_nom_carte`, `invocation_par_nom` (mémoire du tour, clé sur le **nom
imprimé** de la carte cité par la clause), ou `par_exemplaire` (attribut de l'exemplaire, bloc C) ; `effet` est le
numéro de l'effet pour `par_nom_effet` et vide sinon. Le relecteur a confirmé qu'une limite est **consommée dès
l'activation** (question ouverte 1), mais **quand** et **par quoi** elle est consommée relève de la tranche 0 : le
lot 18 ne fait que la structure. Le harnais vérifie que chaque clause « per turn » des textes du deck tombe dans
l'une de ces cinq formes (une seule anomalie : `The Three Champions of Swordsoul` cite « The Three Brave
Swordsouls », voir `jeu-de-tests-branded.md` § 1).

**Ce que l'état ne contient pas** : le chemin suivi (il est dans les transitions), le jugement sur
la qualité du plateau, et les informations cachées de l'adversaire (réservées, § 2.5).

**Tests de la définition sur des exemples Branded**

1. *Même contenu de Cimetière, états différents.* `Titaniklad the Ash Dragon` est au Cimetière.
   Chemin 1 : `Nadir Servant` l'y a envoyé depuis l'Extra Deck. Chemin 2 : il a été invoqué par
   Fusion puis utilisé comme matériel. Les cartes visibles sont les mêmes, mais seul le chemin 2
   permet à `Tri-Brigade Springans Kitt` de le rappeler. Sans le drapeau « correctement invoquée »,
   la définition du § 4 confondrait les deux (T22, T52).
2. *Même plateau, verrou différent.* Deux mains mènent à `Albaz` + `Blazing Cartesia` sur le
   terrain ; dans l'une, `Nadir Servant` a été joué. L'effet de Fusion de `Cartesia` n'est légal que
   dans l'autre (T20). La mémoire du tour fait la différence.
3. *Nom temporaire.* `Cocatorium` bannit `Tri-Brigade Mercourier` du deck et **devient**
   « Tri-Brigade Mercourier » : `Tri-Brigade Springans Kitt` (« si vous contrôlez un monstre
   Tri-Brigade ») peut alors être invoqué (T32). L'état doit porter le nom courant, pas seulement
   le nom imprimé.

### 2.2 Action

**Définition.** Une action est une **décision élémentaire** d'un joueur, prise dans un état, parmi
la liste des décisions légales à cet instant. Le moteur ne fait que deux choses : lister les
décisions légales d'un état, et appliquer celle qui est choisie.

Le § 4 cite « invoquer, activer, choisir une cible ». Liste complète des décisions :

| Famille | Décisions |
|---|---|
| Déclarer | Invocation Normale, Pose, Invocation Spéciale inhérente (sans chaîne), **activation** d'une carte ou d'un effet, changement de position, déclaration d'attaque, changement de phase, fin de tour. |
| Compléter une activation | payer le **coût** (quelle carte défausser, envoyer, bannir), choisir les **cibles**. |
| Répondre | enchaîner un effet (ou passer). |
| Compléter une résolution | choisir les matériels, la carte cherchée, la zone d'arrivée, l'option (« ajouter à la main **ou** invoquer »), appliquer ou non un « then you can ». |
| Placer (D3 révisée, relecture 1) | la **case d'arrivée** d'un monstre ou d'une Magie/Piège. À chaque Invocation **depuis l'Extra Deck**, le choix « Zone Monstre Extra » / « zone principale » est une **option de l'action** : deux décisions distinctes, donc deux transitions. Un monstre Invoqué depuis le Cimetière, les bannies, la main ou le Deck ne peut **pas** aller en Zone Monstre Extra (confirmé par le relecteur, question ouverte 4). Les **colonnes** (laquelle des cases principales) ne sont énumérées que si une carte du deck lit la position (`Sprind the Irondash Dragon`, `Albion the Sanctifire Dragon` : liste déclarée dans `moteur_combos/modele.py`) ; sinon la première case libre est prise. Dans tous les cas, la case réellement occupée est **enregistrée** dans l'état et sur le plateau final. |
| Ordonner | l'ordre de plusieurs effets déclenchés en même temps. |
| Subir le hasard | pioche : ce n'est pas une décision du joueur, c'est une **branche aléatoire** (une par carte possible), étiquetée comme condition (§ 2.4). |

**Deux niveaux** (décision D2) :

- le **pas** : une décision élémentaire. C'est le niveau du moteur et de la comparaison avec l'oracle ;
- la **transition** : tout ce qui se passe entre deux **états stables**. Un état stable est un état
  où la chaîne est vide, où aucun effet déclenché n'attend et où le joueur du tour a la main. Une
  transition regroupe donc une action déclarée, ses coûts, ses cibles, la chaîne qu'elle ouvre, les
  effets déclenchés qui en découlent et tous les choix faits en route. C'est le niveau du combo.

**Ce qu'une action consomme** (question du ticket) : l'Invocation Normale du tour ; un « une fois
par tour » (consommé **à l'activation**, même si l'effet est ensuite annulé ⚖) ; les cartes du coût ;
une zone libre ; et parfois une liberté future (un verrou). Tout cela s'écrit dans l'état d'arrivée.

**Légalité d'une activation.** Une activation est légale si, au moment de l'annoncer : la
condition (avant « : ») est vraie, le coût (avant « ; ») est payable, des cibles valides existent, la
vitesse convient, aucune limite « une fois par tour » ni aucun verrou ne l'interdit, **et l'effet peut
se résoudre au moins en partie** ⚖ (on ne peut pas activer `Aluber` s'il ne reste aucune Magie/Piège
« Branded » dans le deck, T02).

**Tests sur des exemples Branded**

1. `Aluber the Jester of Despia` en Invocation Normale, puis recherche de `Branded Fusion` : une
   transition, trois pas (déclarer l'invocation, activer l'effet déclenché, choisir la carte) (T01).
2. `Branded Opening` (« Discard 1 card, then take… ») : **pas de « ; »**, la défausse fait partie de
   l'effet et non du coût. Avec `Super Polymerization` (« Discard 1 card; … ») c'est un coût. La
   définition distingue donc « payer » (pas d'activation) et « appliquer » (pas de résolution) (T34, T38).
3. `Blazing Cartesia` fusionne `Granguignol` en utilisant `Tri-Brigade Springans Kitt` comme
   matériel : deux effets se déclenchent en même temps (`Granguignol` « si invoqué par Fusion »,
   `Kitt` « si envoyé au Cimetière »). Le joueur choisit l'ordre : c'est un pas « ordonner », et les
   deux ordres sont deux transitions distinctes (T45).

### 2.3 Équivalence

**Définition.** Deux états sont équivalents si leur **forme canonique** est identique. La forme
canonique est l'écriture normalisée de l'état :

1. les exemplaires d'une même carte sont **interchangeables** quand tous leurs attributs (bloc C)
   sont égaux : on ne distingue pas le 1er `Aluber` du 2e ;
2. les multi-ensembles sont triés (par identifiant de carte puis par attributs) ;
3. les zones indexées gardent leur index : deux plateaux qui ne diffèrent que par la case d'un monstre sont
   **deux états** (D3 révisée : la case exacte compte, la Zone Monstre Extra et les colonnes sont lues par des
   cartes adverses). L'élagage possible ne vient pas de l'équivalence mais du nombre d'options de placement
   (§ 2.2, « Placer ») ;
4. le deck s'écrit « multi-ensemble + segments connus » ;
5. la mémoire du tour est écrite en entier, triée.

L'identifiant d'un état est l'empreinte (SHA-256) de cette forme. Deux chemins qui arrivent à la
même empreinte arrivent au même nœud : le résultat de l'exploration est un **graphe**, pas un arbre.

Trois précisions que le § 4 ne donnait pas :

- **L'équivalence porte sur l'état complet, pas sur le plateau visible.** « Même photo » veut dire
  même bloc A, B, C et D. Deux plateaux identiques avec des verrous différents ne sont pas équivalents.
- **Elle ne dit rien du chemin.** Deux combos différents peuvent finir au même état : ce sont deux
  combos (deux chemins), un seul plateau final.
- **Une seconde équivalence, plus large, sert à l'affichage** : le « plateau final » (terrain, main,
  Cimetière, bannies en fin de tour, sans la mémoire du tour écoulé). Elle sert à regrouper les
  résultats pour un humain, jamais à élaguer l'exploration.

**Tests sur des exemples Branded**

1. *Deux ordres, un état.* Main : `Aluber`, `Nadir Servant`. Ordre 1 : `Nadir` (envoie `Titaniklad`,
   ajoute `Fallen of Albaz`) puis Invocation Normale d'`Aluber` (cherche `Branded Fusion`). Ordre 2 :
   l'inverse. Mêmes zones, mêmes « une fois par tour », même verrou : **un seul état**, deux chemins.
2. *Copies interchangeables.* Défausser le 1er ou le 2e `Mulcharmy Fuwalos` donne le même état.
3. *Faux jumeaux.* Exemple 1 du § 2.1 (`Titaniklad` au Cimetière, invoqué ou non) : **deux états**.

### 2.4 Arrêt

Le § 4 dit : « plus d'action légale, ou profondeur maximale, boucles coupées ». Trois précisions.

**a. Fin de ligne.** Au tour d'ouverture, « passer à la Phase de Fin » est toujours légal : il n'y a
donc jamais « plus aucune action légale » au sens strict. Je distingue :

- **fin forcée** : état stable où la seule action légale restante est de passer ;
- **fin volontaire** : le joueur passe alors qu'il lui reste des actions. Tout état stable de Phase
  Principale peut donc conduire à un plateau final.

Dans les deux cas, le **plateau final** est l'état à la fin de la Phase de Fin, **après** : les
effets obligatoires de Phase de Fin (`Incredible Ecclesia` : « Add this card », sans « You can »,
T37), les effets facultatifs choisis, les retours différés (`Ecclesia and the Dark Dragon`) et la
limite de 6 cartes en main. Un état où un effet obligatoire attend n'est jamais final.

**b. Profondeur maximale.** Paramètre de l'exploration, compté en transitions. Un état atteint à la
profondeur maximale et qui a encore des actions est marqué **tronqué** : ce n'est pas un plateau
final, et l'exploration est déclarée **incomplète**. Ce statut est publié avec le résultat (cohérent
avec « n'afficher que ce qui est démontré »).

**c. Boucles.** L'exploration étant un graphe d'états, revenir sur un état déjà vu ne relance rien :
l'arête est enregistrée (marquée « retour ») et le nœud n'est pas ré-exploré. Un combo est un chemin
**sans répétition d'état**. Une boucle qui change l'état à chaque tour (elle gagne des points de vie,
des compteurs…) n'est pas détectée par l'égalité d'états : c'est la profondeur maximale qui la coupe,
et le résultat est alors « tronqué ». Cela tranche la partie « boucles » de la question ouverte n° 6.

**d. Boucles signalées par le relecteur (relecture 1, lot 18).** Le relecteur prévient que Branded peut
« tourner » longtemps sans rien construire. Deux cas, deux motifs :

- `retour_etat_connu` : l'état d'arrivée a déjà été atteint **par un autre chemin** (fusion de deux branches du
  graphe). Ce n'est pas une boucle, c'est une équivalence ; le chemin n'est pas ré-exploré ;
- `boucle` : l'état d'arrivée est déjà sur **le chemin courant** (un ancêtre). Le combo reviendrait en arrière ;
  la branche est coupée et l'arête gardée pour l'audit.

Une boucle qui change l'état à chaque tour reste coupée par la profondeur (`tronque_profondeur`, point c). Seule
la structure est livrée au lot 18 (valeur autorisée du motif) ; la détection est l'algorithme d'exploration.

**e. Cible d'exploration (relecture 1, lot 18).** Le relecteur recommande de donner au moteur le **plateau
final visé** plutôt que d'énumérer tous les plateaux. Une cible est une liste de conditions sur le plateau final
(« telle carte dans telle zone, au moins N exemplaires », zone `terrain`, `main`, `cimetiere`, `bannies`), avec une
description lisible. Elle est rattachée à une exploration (`cb_run.target_id`, table `cb_target`) ; une branche
qui l'atteint s'arrête avec le motif `cible_atteinte`. Sans cible, l'exploration reste exhaustive (à filtres et
profondeur près). Ce que « atteindre » veut dire exactement (égalité ou inclusion) est laissé à l'algorithme
d'exploration ; le lot 18 enregistre les conditions telles qu'écrites.

**Motifs d'arrêt enregistrés** : `fin_forcee`, `fin_volontaire`, `tronque_profondeur`,
`retour_etat_connu`, `boucle` (lot 18), `cible_atteinte` (lot 18), `non_couvert` (une carte non formalisée
intervient, § 3.4), `hors_perimetre` (Phase de Combat, tour adverse : réservés).

**Tests sur des exemples Branded**

1. Main : `Ash Blossom` ×2, `Ghost Ogre` ×2, `Droll & Lock Bird`. Aucune de ces cartes ne peut agir
   seule au tour 1 (elles répondent à l'adversaire), sauf l'Invocation Normale. Fins forcées après une
   Invocation Normale ; fin volontaire possible dès le départ.
2. `Nadir Servant` envoie `Titaniklad` : le plateau « fin de Phase Principale » n'est pas final,
   l'effet de Phase de Fin de `Titaniklad` (ajouter ou invoquer `Albaz` ou un monstre « Dogmatika »)
   ouvre encore plusieurs branches (T18).
3. `Garura, Wings of Resonant Life` envoyé au Cimetière : « piochez 1 carte ». La suite dépend du
   hasard : une branche par carte piochable, chacune portant la condition « pioche = X » (T19).

### 2.5 Places réservées (hors pilote)

- **Point d'interruption adverse.** Chaque pas de type « activation » ou « invocation » ouvre une
  **fenêtre de réponse**. Le modèle l'enregistre toujours, avec la réponse `aucune` dans le pilote.
  Plus tard, la même fenêtre portera une réponse adverse (`Ash Blossom`, `Droll & Lock Bird`…) et
  produira des branches. Le schéma a la table et la colonne ; le pilote ne les remplit pas.
- **Tours suivants.** L'état porte déjà le numéro de tour, le joueur actif, la phase, les effets
  différés et les restrictions « au tour suivant ». Les deux joueurs ont la même structure de zones.
  Rien n'est spécifique au tour 1 dans la forme de l'état ; seule l'exploration s'y limite.
- **Information cachée.** La main et le deck adverses sont dans l'état, avec un drapeau « connu /
  inconnu » par zone. Le pilote les laisse « inconnu ».

### 2.6 Validité d'un deck (relecture 1, lot 18)

Contrôle fait au chargement, avant toute exploration. C'est un contrôle de **construction de deck**, pas une
règle de déroulement du tour.

- Main Deck de 40 à 60 cartes, Extra Deck de 0 à 15.
- **Au plus 3 exemplaires par nom, « always treated as » compris** (ajout du relecteur sur R03) : `Fallen of
  Albaz` (×1) et `Fallen of the White Dragon` (×2, « always treated as "Fallen of Albaz" ») partagent la même
  limite, d'où 1 + 2 = 3 dans la liste. Le compte se fait sur le **groupe de noms** : nom imprimé plus les noms
  donnés par une clause « always treated as "X" » (sans « card » derrière). Une clause « always treated as a
  "X" card » donne un **archétype**, pas un nom, et n'entre pas dans ce compte. Main, Extra et Side Deck comptent
  ensemble.
- Limite de la banlist (`ban_tcg` lu dans `deck-branded-source.json`, statut au jour de l'extraction) : Forbidden
  0, Limited 1, Semi-Limited 2, **par nom imprimé** (⚖ l'extension de la banlist aux noms « always treated as »
  n'est pas vérifiée ; elle ne change rien pour ce deck).

Le deck du pilote passe ces contrôles (`python scripts/combos_harnais.py`).

---

## 3. Schéma de données

**Implémenté au lot 18 (18/11)** dans une base à part, `data/combos.db` (ignorée par Git, jamais dans `yugioh.db`).
La **source de vérité est `moteur_combos/schema.sql`** : le DDL n'est plus recopié ici, pour éviter qu'il diverge.
Préfixe `cb_` (combos) pour ne rien mêler aux tables de méta. Version du schéma : `PRAGMA user_version` (1).
Les structures Python correspondantes (état, exemplaire, mémoire du tour, cible) sont dans
`moteur_combos/modele.py` ; le chargement du deck dans `moteur_combos/deck.py` ; le harnais dans
`moteur_combos/harnais.py` (commande : `python scripts/combos_harnais.py`).

### 3.1 Vue d'ensemble

```
cb_card ──< cb_effect ──< cb_effect_limit       texte figé, effets, limites « par tour » (5 formes)
   │  └──< cb_card_name_tag                       noms et archétypes (nom imprimé, « always treated as »)
   │
   └──< cb_step_card >── cb_step ──> cb_transition ──> cb_state (départ, arrivée)
                              │            │
                              │            ├──< cb_transition_condition >── cb_condition
                              │            └──< cb_relation            (dérivée)
                              └──< cb_window                             (interruption réservée)

cb_deck ──< cb_deck_card >── cb_card             liste source (main, extra, side)
cb_run ──< cb_transition          une exploration : deck, état de départ, cible, paramètres
cb_run >── cb_target              plateau final visé (relecture 1)
cb_run ──< cb_combo ──< cb_combo_step >── cb_transition
cb_test_situation >── cb_state    les 72 situations du jeu de tests, leur départ et leur classe
```

### 3.2 Tables, et ce qui a changé depuis la version sur papier du 16/11

| Table | Rôle | Changement au lot 18 |
|---|---|---|
| `cb_card` | une carte, texte figé et empreinte | `CHECK` : `verifiee` exige `verified_by`, `non_formalisable` exige une raison. Une renumérotation YGOPRODeck (même nom, autre id) est refusée explicitement. + `text` (copie locale, la base n'est pas versionnée : le texte appartient à Konami), caractéristiques (`frame_type`, `attribute`, `race`, `level`, `atk`, `def`), `reads_position` (D3). `text_sha256` obligatoire. Un texte changé remet le statut à `non_traitee` (errata) ; un statut n'est jamais rétrogradé autrement. |
| `cb_card_name_tag` | noms portés et archétypes | + colonne `kind` (`nom` / `archetype`) : « always treated as "X" » donne un **nom** (limite de 3, § 2.6), « always treated as a "X" card » un **archétype**. `origin` : `nom_imprime` / `traite_comme`. |
| `cb_effect` | un effet découpé dans le texte | la colonne `limit_scope` est remplacée par la table `cb_effect_limit` (un effet peut porter plusieurs limites) ; + `text_sha256` (texte formalisé). Un errata remet aussi les effets à `non_traitee`. Vide au lot 18. |
| `cb_effect_limit` | **nouvelle** : limites « une fois par tour » | forme parmi `activation_par_nom`, `par_nom_effet`, `par_nom_carte`, `invocation_par_nom`, `par_exemplaire` (§ 1 et § 2.1 D) ; `name_key` = nom cité par la clause (il peut différer du nom imprimé : `The Three Champions of Swordsoul`). |
| `cb_deck`, `cb_deck_card` | **nouvelles** : la liste source | empreinte du fichier `deck-branded-source.json`, zone, nombre, statut de banlist au jour de l'extraction. |
| `cb_state` | états, adressés par l'empreinte de leur forme canonique | + `CHECK` sur la phase, le joueur, la longueur de l'empreinte. Un état n'est jamais modifié (`INSERT OR IGNORE`). |
| `cb_target` | **nouvelle** : cible d'exploration | conditions en JSON (`zone`, `carte`, `minimum`), § 2.4 e. |
| `cb_run` | une exploration | + `target_id` (cible, facultative), `columns_enumerated` (D3 révisée), `deck_ref` relié à `cb_deck`, obligatoire en mode `decklist`. |
| `cb_transition`, `cb_combo` | transitions et combos | `stop_reason` contrôlé : + `boucle`, `cible_atteinte` (§ 2.4 d, e). |
| `cb_step` | pas élémentaires | + type `placer` et colonne `option` (choix Zone Monstre Extra / zone principale, D3 révisée). |
| `cb_step_card` | cartes nommées par un pas | + `to_cell` (case exacte d'arrivée : `M1`-`M5`, `ZME_G`, `ZME_D`, `S1`-`S5`, `TERRAIN`) ; + `copy_index` dans la clé (deux matériels homonymes dans le même pas). |
| `cb_window`, `cb_condition`, `cb_transition_condition`, `cb_relation`, `cb_combo_step` | inchangées sur le fond | `CHECK` ajoutés sur les valeurs fermées. |
| `cb_test_situation` | **nouvelle** : harnais | une ligne par situation du YAML : empreinte du fichier, points de règle (R27 précisé en R27a / R27b), classe, état de départ, départ complet ou non, faits en texte libre, verdict attendu, statut (`verifie`, `en_attente_tranche_0`, `depart_invalide`, `echec`). |

**Garde-fous et versions** (relecture de l'agent `gardien-donnees`, 18/11, 3 défauts bloquants corrigés) :
`moteur_combos/base.py` résout le chemin de `combos.db` et refuse un nom de base du projet sans tenir compte de la
casse (`yugioh.db`, `serving.db`, `backup_*.db` : le disque du Mac est insensible à la casse), le même fichier que la
base de référence (lien symbolique compris) et toute base existante qui contient une table sans le préfixe `cb_`.
La base de référence s'ouvre par une URI échappée en `mode=ro`. Une base plus ancienne que le code reçoit les
fichiers `moteur_combos/migrations/NNN.sql` dans une transaction avant de changer de numéro (aucun encore) :
`CREATE TABLE IF NOT EXISTS` n'ajoute jamais une colonne, une base ne doit donc jamais être déclarée migrée sans
migration. Index ajoutés pour la requête « combos qui passent par X » et pour chaque clé étrangère.

**Forme canonique de l'état** (`Etat.forme_canonique()`) : blocs A (cadre), B (zones des deux joueurs, cases exactes,
Zones Monstre Extra communes avec leur contrôleur), C (attributs dans chaque exemplaire), D (mémoire du tour). Les
multi-ensembles sont triés, les exemplaires égaux se confondent. Ce qui n'est pas encore formalisé (mémoire décrite
en phrases dans le YAML, annotations non reconnues) est gardé **en texte libre dans l'état** : il compte dans
l'empreinte, pour ne jamais confondre deux états qui pourraient différer (D7). Deux situations écrites pareil
donnent le même état (T08 et T09 : 72 situations, 66 états distincts).

### 3.3 Les quatre familles de relations, sur des cas Branded

Une relation relie la carte qui agit à une autre carte nommée dans la même transition. Les familles
peuvent coexister sur une même paire.

| Famille | Règle de dérivation depuis `cb_step_card` | Exemple |
|---|---|---|
| `deplace` | l'acteur fait changer de zone une autre carte par son **effet** | `Aluber` → `Branded Fusion` (deck → main) |
| `materiel_ou_cout` | l'autre carte a le rôle `materiel` ou `cout` | `Branded Fusion` → `Fallen of Albaz` (matériel) ; `Fallen of the White Dragon` → `Titaniklad` (coût) |
| `conditionne` | l'autre carte a le rôle `condition` : sa présence rend l'action légale | `Blazing Cartesia` ← `Fallen of Albaz` (« si vous contrôlez Albaz ») ; `Springans Kitt` ← `Titaniklad` au Cimetière |
| `interagit_adverse` | la carte visée appartient à l'adversaire, ou l'effet répond à une action adverse | `Super Polymerization` → monstre adverse ; `Ash Blossom` (hors pilote, réservée) |

Une même transition produit souvent plusieurs relations : `Fallen of the White Dragon` paie son
coût avec `Titaniklad` (`materiel_ou_cout`), ce qui fait quitter l'Extra Deck à une carte et déclenche
`Guiding Quem` (`conditionne`, dans la transition suivante).

### 3.4 Statuts de formalisation et « non couvert »

Le ticket cite quatre statuts (non traité, brouillon, vérifié, non formalisable), les décisions
trois (formalisée, vérifiée, non formalisable). Je propose les **cinq**, dans l'ordre du cycle de vie
(décision D6) :

| Statut | Sens | Le moteur l'exécute ? |
|---|---|---|
| `non_traitee` | personne n'a regardé la carte, ou son texte manque dans la source | non → « non couvert » |
| `brouillon` | un LLM a proposé une forme, non testée | non → « non couvert » |
| `formalisee` | la forme passe les tests du moteur | oui, résultats étiquetés **« non vérifié »** |
| `verifiee` | accord avec l'oracle, ou relue par un juge | oui, résultats **« démontrés »** |
| `non_formalisable` | le texte ne s'exprime pas dans le modèle (raison écrite) | non → « non couvert » |

**Application en tranche 0 (TOK-90).** Le statut se calcule depuis la formalisation écrite dans
`moteur_combos/cartes.py` et l'empreinte du texte (un errata la désactive). Une formalisation **déclare tous
les effets** de la carte (zone, déclencheur ou condition, limites) ; une résolution peut manquer (`NON_CODEE`)
ou supposer l'adversaire (`HORS_PERIMETRE`, condition écrite et fausse dans le pilote). D'où : `formalisee` =
toutes les résolutions écrites ou hors du pilote ; `brouillon` = effets déclarés, au moins une résolution
manquante (`Rindbrumm`, effet 1) : le moteur peut déplacer la carte (il sait quand elle pourrait agir) mais
n'exécute jamais l'effet manquant, l'option apparaît « non couverte ». Une carte `non_traitee` jouée, déplacée
ou choisie arrête la transition sur `non_couvert`. En exécution dirigée (un chemin donné, pas une exploration),
le cas 2 ne coupe pas le résultat : il l'accompagne de **réserves** (cartes non formalisées en main, sur le
terrain ou au Cimetière, qui auraient pu agir) ; le cas 3 donne la liste des options **indéterminées**.

**Application en J1 (lot C2, décision par défaut).** `formalisee` exige en plus que **chaque effet du pilote ait été
exercé par au moins un test exécuté** (situations de `tests-branded.yaml` ou de `situations-j1.yaml`), compté par le
moteur (`regles.EXERCES`) et lu par le harnais ; un effet jamais exercé laisse la carte en `brouillon` (« écrite, non
testée »). `verifiee` reste réservé à l'oracle ou au juge (aucune carte au 18/11).

« Exhaustif » (§ 4) = toute carte a l'un de ces statuts ; le taux de couverture publié est la part
de `formalisee` + `verifiee`, et le taux démontré la part de `verifiee`.

**Propagation du « non couvert »** (décision D5). Trois situations, trois réponses :

1. on demande une action **sur** une carte non couverte → réponse `non_couvert`, jamais un résultat ;
2. une exploration rencontre un état où une carte non couverte **pourrait agir** (elle est en main,
   sur le terrain, au Cimetière) → la branche s'arrête avec le motif `non_couvert`, l'exploration est
   `complete = 0` ;
3. une énumération porte sur une zone qui **contient** une carte non couverte (ex. « un monstre
   Fusion de l'Extra Deck qui mentionne Albaz » alors que des cartes de l'Extra Deck ne sont pas
   formalisées) → les résultats trouvés sont donnés, étiquetés « liste peut-être incomplète : N cartes non
   couvertes dans la zone ».

### 3.5 Piège de données trouvé : `cards.archetype` ne dit pas la règle

En jeu, une carte « Dogmatika » est une carte dont le **nom contient** « Dogmatika », ou dont le
texte dit « always treated as ». Or la colonne `cards.archetype` (YGOPRODeck) est un classement
éditorial, à une seule valeur :

| Carte | `cards.archetype` | Réalité du texte |
|---|---|---|
| `Fallen of Albaz` | Dogmatika | Son nom ne contient pas « Dogmatika » : ce n'est **pas** une carte Dogmatika. |
| `Guiding Quem, the Virtuous` | Despia | « always treated as a "Dogmatika" and "Despia" card » : **les deux**. |
| `Tri-Brigade Springans Kitt` | Springans | « Tri-Brigade » **et** « Springans ». |
| `Incredible Ecclesia, the Virtuous` | (vide) | C'est un monstre « Ecclesia » (son nom le contient). |
| `Fallen of the White Dragon` | (vide) | « always treated as "Fallen of Albaz" ». |

D'où la table `cb_card_name_tag`, calculée depuis le nom et les clauses « treated as ». Utiliser
`cards.archetype` ferait, par exemple, chercher `Fallen of Albaz` par `Dogmatika Ecclesia` (illégal).
De même, « une carte qui mentionne Fallen of Albaz » se calcule en cherchant le nom entre guillemets
dans le texte, pas par archétype (T23).

### 3.6 Les deux requêtes demandées par le ticket

**« Tous les combos qui passent par la carte X »** (X joue un rôle quelconque : jouée, matériel,
cherchée, condition) :

```sql
SELECT DISTINCT cs.combo_id
FROM cb_combo_step cs
JOIN cb_step s        ON s.transition_id = cs.transition_id
JOIN cb_step_card sc  ON sc.step_id = s.step_id
WHERE sc.card_id = :x;
-- variante « X est la carte jouée » : WHERE cs.actor_card_id = :x (index direct)
```

**« A puis directement B »** (deux étapes consécutives du combo, A jouée puis B jouée) :

```sql
SELECT a.combo_id, a.position
FROM cb_combo_step a
JOIN cb_combo_step b ON b.combo_id = a.combo_id AND b.position = a.position + 1
WHERE a.actor_card_id = :a AND b.actor_card_id = :b;
```

**« A et B ensemble »** (sans ordre) : intersection de deux fois la première requête.
**« A va chercher B »** (lecture plus fine que la succession) : `cb_relation` avec
`source_card = :a AND target_card = :b AND family = 'deplace'`.

Un **micro-combo** est un segment contigu de `cb_combo_step`. Il n'est pas stocké à part : AB, BC et
CD se lisent dans ABCD par les positions. Un macro-combo sur plusieurs tours sera un chemin dont les
transitions traversent un changement de tour (colonne `turn` de l'état).

---

## 4. Questions ouvertes du § 8 : ce que ces définitions changent

| N° | Question | Position |
|---|---|---|
| 1 | Qui juge ? | **Avancée** : un joueur de tournoi (non arbitre) a relu les 34 points le 17/11 (32 confirmés, R22 levé par cohérence, R34 complété). R08, R27 (b) et R34 n'ont qu'un avis : prochain relecteur ou oracle (TOK-86). |
| 2 | Budget | Reste ouverte. Le chronométrage de cette session donne un premier point de calibrage. |
| 3 | L'oracle liste-t-il toutes les actions légales ? | **Reste ouverte, et devient bloquante** : le niveau « pas » (§ 2.2) suppose qu'on puisse comparer une liste d'actions légales, pas seulement un résultat. Si l'oracle ne la donne pas, la comparaison se fera au niveau « transition » (états d'arrivée), moins fine. |
| 4, 5 | Banc sur Mac, rulings TCG/OCG | Non traitées (TOK-86). |
| 6 | Boucles | **Tranchée** (§ 2.4 c), précisée au lot 18 : motif `boucle` distinct de `retour_etat_connu`, et cible d'exploration (§ 2.4 d, e). |
| — | Ordre du Cimetière, colonnes, Zone Monstre Extra (questions hors tests de `points-de-regle-a-valider.md`) | **Tranchées par la relecture 1** : Cimetière en multi-ensemble ; colonnes et Zone Monstre Extra comptent (D3 révisée, § 2.1 B et § 2.2). |
| 6 | Textes à une date passée | **Préparée, pas tranchée** : `cb_card.text_sha256` et `text_fetched` détectent un errata ; la source de textes anciens reste à trouver. |
| 6 | Textes OCG | Hors périmètre, non traitée. |
| 7 | Hypothèse de Winston | **Fausse telle quelle, vraie sous une forme restreinte**, voir ci-dessous. |

### L'hypothèse de Winston (§ 8, point 7)

> « Une transition ne dépend que des cartes qu'elle nomme », ce qui rendrait « retirer X » peu coûteux.

**Telle quelle, elle est fausse.** La légalité d'une transition dépend aussi de choses qu'elle ne
nomme pas. Quatre contre-exemples tirés du deck :

1. **Verrous.** « `Blazing Cartesia` fusionne `Granguignol` » ne nomme pas `Nadir Servant`, et
   pourtant elle est illégale si `Nadir Servant` a été joué avant (T20).
2. **Conditions d'absence ou de comptage.** `Mulcharmy Fuwalos` : « si vous ne contrôlez aucune
   carte ». `Incredible Ecclesia` : « si l'adversaire contrôle plus de monstres que vous ». La
   transition dépend de cartes qui ne sont **pas** là.
3. **Effets déclenchés par d'autres cartes.** Toute transition qui fait sortir une carte de l'Extra
   Deck déclenche `Guiding Quem` s'il est sur le terrain. La transition `Nadir Servant` ne nomme pas
   `Quem`, mais son état d'arrivée en dépend (T22). Avec un effet **obligatoire**, c'est pire : la
   présence de la carte impose la suite.
4. **Chaînes.** `Super Polymerization` interdit toute réponse à son activation : la légalité d'un
   enchaînement dépend de la carte à laquelle on répond.

**Forme restreinte que je crois vraie** (raisonnement de ma part, **non démontré**, à tester) :

> En mode decklist, si X ne quitte jamais sa zone cachée (Deck ou Extra Deck) le long d'un chemin,
> alors ce chemin reste légal quand on retire X du deck. Et retirer X ne crée aucun chemin nouveau.
> Donc : *les combos du deck sans X = les combos du deck avec X dont aucun pas ne nomme X*.

Pourquoi : une carte qui dort dans le Deck n'a ni effet, ni condition, ni déclencheur. Les quatre
contre-exemples ci-dessus passent tous par une carte qui a **bougé** ou **agi**, donc qui est nommée
quelque part dans le chemin (pas forcément dans la transition concernée : c'est là que la formule de
Winston était trop forte). Le filtre porte sur le **chemin entier**, pas sur la transition.

**Trois exceptions connues**, où le filtre ne suffit pas :

- les effets qui lisent un **agrégat** de la zone cachée : pioche (`Garura`), nombre de cartes
  restantes, cartes du dessus du deck. Le chemin survit, mais sa condition de hasard change ;
- « retirer X » en pratique veut dire **remplacer X par Z** (un deck fait 40 cartes) : les combos
  qui passent par Z sont nouveaux et doivent être calculés ;
- un **ban** qui passe X de 3 à 1 exemplaire : les chemins qui utilisent 2 copies de X disparaissent,
  ce que le filtre « nomme X » ne voit pas (il faut compter les exemplaires distincts utilisés).

**Conséquence pour le schéma** : `cb_step_card` (toutes les cartes nommées, avec leur rôle) est la
table qui rend « retirer X » peu coûteux. **Test à écrire en tranche 0** : sur une main, calculer les
combos avec X, filtrer, puis recalculer sans X et comparer. Tant que ce test n'a pas tourné,
l'affirmation reste une hypothèse.

---

## 5. Décisions à prendre

Formulaires regroupés dans [`decisions-a-prendre-tok-85-87.md`](decisions-a-prendre-tok-85-87.md)
(D1 à D8).
