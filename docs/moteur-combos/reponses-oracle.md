# Réponses de l'oracle Project Ignis (TOK-86) — relance du 18 novembre 2026

**Statut : oracle installé et utilisé. Les 34 points de règle ont une réponse de l'oracle** (aucun « non testable »),
avec un seul **désaccord franc (R23)** et trois nuances. Rien de Project Ignis n'est dans ce dépôt : ce fichier ne
contient que des résultats (données), jamais du code du cœur, d'un script de carte ou de la base de cartes.

> Principe d'indépendance (décision du 16/11) : l'oracle ne doit être lu par aucune session qui code le moteur.
> Ce fichier donne les **réponses** (« l'action est-elle légale ? », « que propose le cœur ? »), pas l'implémentation.
> Une session de moteur peut lire ce fichier comme elle lit les réponses du juge ; elle ne doit pas aller lire
> `~/code/oracle-ignis/`.

## 1. Désaccords et nuances (à lire d'abord)

| N° | Lecture supposée / relecteur | Oracle | Pourquoi, et ce que ça change |
|---|---|---|---|
| **R23** | Obligatoire (lecture : oui ; relecteur : « le deux-points déclare l'effet, effet obligatoire ») | **Facultatif.** Le cœur propose l'effet d'`Incredible Ecclesia` à la Phase de Fin dans une liste non forcée : on peut passer sans l'activer, le tour se termine. | **Désaccord de comportement, mais cause probable : le texte, pas la règle.** Le texte de la base du dépôt (`cards`) n'a pas « You can » ; le texte de la base de l'oracle (BabelCDB) dit « You can add this card… » et porte la mention « texte non officiel, décrit le fonctionnement OCG ». Le script de la carte est donc écrit pour un effet facultatif. **L'oracle ne peut pas trancher R23 pour le TCG** : il faut le texte officiel TCG imprimé ou un ruling. Conséquence directe : **T37** (verdict `illegal` : « terminer le tour sans résoudre l'effet ») est **contredit par l'oracle** ; le verdict de T37 reste non validé. La seconde moitié de R23 (ordre des effets de Phase de Fin) est confirmée, voir le tableau. |
| R22 (ordre) | Le joueur choisit l'ordre librement ; il peut n'en activer qu'un | **Confirmé** avec les réglages de jeu retenus (voir § 2). Nuance : avec l'option `DUEL_TCG_SEGOC_FIRSTTRIGGER` du cœur (ordre « premier déclenché d'abord », prévue pour d'anciennes règles), le cœur **interroge les effets un par un dans un ordre qu'il fixe** (T45 : `Tri-Brigade Springans Kitt` d'abord, `Granguignol` ensuite) ; on peut toujours n'en activer qu'un, mais pas toujours choisir l'ordre. | Le comportement libre vient de la liste unique proposée en fin de chaîne (T45, T62). **Le moteur doit rendre cette règle configurable** ou documenter laquelle il suit ; je n'ai pas pu établir laquelle des deux options correspond au TCG actuel (aucune documentation de l'oracle consultée, volontairement). |
| R34 (nature de l'envoi) | (a) non, (b) cible choisie à l'activation, (c) non : **confirmé sur les trois** | Même verdict. Nuance : le script traite l'envoi du monstre de l'Extra Deck comme un **coût** (raison « coût » dans le journal du cœur), payé avant le choix de la cible. | Aucun effet sur les trois sous-questions. Mais si l'activation était annulée après paiement (`Solemn Judgment`), le monstre reste au Cimetière. À ne pas confondre avec un effet de résolution. |
| R10 | « If … : You can » ne rate pas son moment ; seuls les « When … you can » le ratent | Moitié testée : tous les « If » rencontrés (`Tri-Brigade Mercourier`, `Tri-Brigade Springans Kitt`, `Guiding Quem`) sont proposés **après** la fin de la chaîne en cours, dans une nouvelle chaîne. | La moitié « When … rate son moment » n'a pas été éprouvée (aucun « When » dans les situations jouées). |

**Aucun désaccord entre l'oracle et le relecteur ailleurs.** R22 : l'objection du relecteur (« il peut activer les
deux ») venait d'un malentendu de formulation ; l'oracle montre que les deux options existent, on peut aussi n'en
activer qu'un.

## 2. Installation et méthode

**Installation réussie** (hors dépôt, `~/code/oracle-ignis/`, jamais commité) :

| Élément | Source autorisée | Version |
|---|---|---|
| Cœur de jeu | `github.com/edo9300/ygopro-core` | `1e3bcfd` (16/11/2026), AGPL-3.0-or-later, API 11.0 |
| Scripts de cartes | `github.com/ProjectIgnis/CardScripts` | `ed5ed45b` (17/11/2026) |
| Base de cartes | `github.com/ProjectIgnis/BabelCDB` | `a40b0ef` (16/11/2026) |
| Lua | dépendance épinglée du cœur (sous-module `lua/src`, `github.com/lua/lua`, `6e22fed`), Lua 5.4 compilé en C++ avec l'en-tête de configuration du cœur | — |

- Compilation : `premake5 gmake` puis `make config=release ocgcoreshared` (une minute). **Le Lua de Homebrew
  (`lua@5.4`) n'a pas servi** : le cœur compile son propre Lua en C++ avec un en-tête de configuration maison. J'ai
  donc récupéré la dépendance Lua épinglée par le cœur lui-même (sous-module), ce que le brief prévoyait
  (« compiler les sources de Lua 5.4 dans le dossier de l'oracle »). Rien n'a été installé au niveau du système.
- Le dossier `~/code/oracle-ignis/core/` de la première tentative (coquille `EDOPro-Core`, un seul README) est resté en
  place : le garde-fou a refusé un `rm -rf` et je n'ai rien contourné. Thomas peut le supprimer.
- **Lanceur** (`~/code/oracle-ignis/lanceur/`, Python, bibliothèque dynamique chargée par `ctypes`) : crée un duel avec
  les 40 + 15 cartes du deck source (`deck-branded-source.json`), place l'état de départ de chaque situation avec
  l'API du cœur, fait tourner le cœur, décode les messages de choix (`SELECT_IDLECMD`, `SELECT_CHAIN`, `SELECT_CARD`,
  `SELECT_OPTION`…) et répond par une consigne écrite à la main. La **liste des actions que propose le cœur** est la
  réponse « légal / illégal » : une action absente de la liste est illégale. Tout est déterministe (graine fixe, pas de
  mélange au démarrage).
- **Réglages du duel** : Master Rule 5 + `DUEL_TCG_SEGOC_NONPUBLIC` (choix par défaut, **ma supposition** : je n'ai pas
  consulté le code d'EDOPro). Les points de comportement sensibles (R10, R22, R27 b) ont été rejoués avec « MR5 seul » :
  mêmes réponses. Seul l'ordre des déclencheurs simultanés change avec `FIRSTTRIGGER` (voir R22 ci-dessus).
- Convention du banc : tour 1, nous commençons, pas de pioche, terrain adverse vide ; les états « mémoire du tour »
  du YAML sont reproduits en **jouant réellement** les actions (jamais par un marqueur), sauf quand la mémoire ne
  change rien à la question posée.

### Situations jouées

**Touchées : 68 sur 72.** Rejouées en entier ou par leur point critique (variante témoin comprise) : T01 à T51, T54 à T66,
T69 à T72. Parmi elles, **rejouées en partie seulement** : T06 (pas de Phase de Combat, pas de pioche), T08, T09 et T10
(par la liste des Fusions que propose `Branded Fusion`), T13 (`Branded Opening` activable, liste de choix non relevée),
T14 (équivalent de R08), T17 (verrou sans effet sur le Deck ; la liste exacte du YAML n'est pas reproduite, une autre
carte ayant été prise en main), T19 (liste de `Nadir Servant`, pas l'effet de `Garura`), T49 (mélange et pose au-dessous
du Deck), T57 et T72 (variantes), T61 (liste de `Mirrorjade`, pas la suite).

**Non rejouées (4)** : T52 (moitié positive de R09 : il faut deux Fusions successives, trop long à reconstituer),
T53 (liste de `Granguignol`, sans point de règle), T67 et T68 (carte `Lava Golem` non formalisée : question de périmètre
du moteur, pas de règle ; **non testable par l'oracle**).

Verdict global : **sur ce qui a été rejoué, l'oracle donne le même verdict que le YAML**, sauf T37 (R23). Aucune autre
contradiction avec `tests-branded.yaml`.

## 3. Les 34 points : trois colonnes

Ordre : points à un seul avis humain d'abord (R08, R27 b, R34), puis R22, puis le reste. « Confiance » = confiance dans la
réponse de l'oracle, pas dans la règle : **forte** quand le comportement vient du cœur (activation, chaîne, limite
par nom), **moyenne** quand il vient du script d'une carte (écrit par la communauté, en Lua).

| N° | Lecture supposée | Relecteur | **Oracle** | Preuves (situations) | Confiance |
|---|---|---|---|---|---|
| **R08** | Effet annulé : limite consommée et verrou actifs. Activation annulée : la carte ne compte pas comme activée. | d'accord | **Confirmé sur les deux moitiés.** `Ash` annule l'effet de `Branded Fusion` : la 2ᵉ copie n'est plus activable (limite consommée) **et** l'Invocation Synchro est retirée de la liste (verrou actif). `Solemn Judgment` annule l'activation : la 2ᵉ copie **est** activable et l'Invocation Synchro est de nouveau proposée (le cœur rend la limite et retire le verrou). | T72 (variante), T14, T21 | forte |
| **R27 (b)** | Bannir du Deck en coût est face visible ; déclenche `Mercourier` et `The Golden Swordsoul` | d'accord | **Oui aux deux.** Après la fin de la chaîne de `Cocatorium`, le cœur propose `Mercourier` (banni) et `The Golden Swordsoul` (Cimetière) dans la même liste. Banni en coût = banni face visible. Ils se chaînent dans les deux ordres. Seule réserve : `Golden Swordsoul` n'est proposée que s'il existe un monstre LUMIÈRE Magicien à Invoquer (`Cartesia` en main dans T62) : sans cible, rien. | T33, T62 | forte |
| **R27 (a)** | `Cocatorium` prend le nom `Mercourier` : compte comme « Tri-Brigade » | d'accord | **Oui.** `Tri-Brigade Springans Kitt` n'est pas activable avec `Cocatorium` seul ; elle l'est après la copie de nom. | T32 | forte |
| **R34** | (a) non ; (b) je ne sais pas ; (c) non | (a)(c) justes ; (b) à l'activation | **(a) non** : la liste de cibles ne contient pas la carte elle-même ; **(b) à l'activation** : le coût (envoi de l'Extra Deck) puis le choix de la cible se font **avant** la fin de l'activation ; **(c) non** : sans carte face visible, la carte n'est pas dans la liste des activations. | T65 (et variante avec `Aluber` sur le terrain) | moyenne (script) |
| **R22** | Le joueur choisit l'ordre ; il peut n'en activer qu'un | « choisit l'ordre » : oui ; « n'en activer qu'un » : jugé faux (probable malentendu) | **Confirmé** (réglage par défaut) : liste unique, choix de l'ordre libre, on peut n'en activer qu'un. Voir la nuance `FIRSTTRIGGER` au § 1. | T45, T62 | forte (réglage dépendant) |
| R01 | Activer un effet qui ne peut rien faire est illégal | d'accord | **Oui.** `Aluber` sans Magie/Piège « Branded » dans le Deck : effet non proposé ; avec : proposé. `Branded Fusion` sans matériel exploitable : absente des activations. `Albaz` : effet proposé seulement si une Fusion est possible. | T02, T05, T11, T71 | forte |
| R02 | Recherche suivie d'un mélange ; carte au-dessous du Deck y reste | d'accord | **Oui aux deux.** Mélange du Deck après chaque recherche ; la carte posée au-dessous (`Springans Kitt`) arrive en bas **sans** mélange ensuite. | T01, T33, T49 | forte |
| R03 | `Fallen of the White Dragon` compte comme `Fallen of Albaz` partout | d'accord | **Oui.** Matériel pris dans le Deck par `Branded Fusion`, cartes cherchées par `Nadir Servant` et `Mercourier`, condition de `Blazing Cartesia` (activable avec `White` seul au Cimetière). | T07, T11, T17, T18, T25, T28 | forte |
| R04 | « Mentionne » = nom entre guillemets dans le texte ; Synchro et Magies comptent | d'accord | **Oui aux trois.** Liste de `Quem` identique à T23 (12 cartes, dont `Branded Fusion`, `Branded in High Spirits`, `Nadir Servant`, `The Fallen & The Virtuous`) ; liste de `White` identique à T29 (dont `Ecclesia and the Dark Dragon`, `The Three Champions of Swordsoul`). | T23, T29, T33, T50 | forte |
| R05 | « Mentionne … comme matériel » : le nom doit être dans la ligne de matériels | d'accord | **Oui.** `Branded Fusion` ne propose que `Rindbrumm` et `Albion the Sanctifire Dragon` ; `Granguignol` exclue ; `Springans Kitt` non activable avec `Granguignol` et `Ecclesia and the Dark Dragon` au Cimetière. | T07, T08, T47, T48 | forte |
| R06 | `Branded Fusion` ne peut pas invoquer `The Dragon that Devours the Dogma` | d'accord | **Oui** (absente de la liste). | T09 | forte |
| R07 | `Branded Fusion` impossible après une Synchro ; `Branded Opening` possible | d'accord | **Oui aux deux** : après une Invocation Synchro, `Branded Fusion` n'est plus activable, `Branded Opening` l'est. | T12, T13 | forte |
| R09 | Un Fusion envoyé directement au Cimetière ne peut pas être ressuscité ; invoqué puis envoyé, oui | d'accord | **Moitié négative confirmée** : avec `Titaniklad` seul au Cimetière (envoyé par `Nadir Servant`), l'effet de `Guiding Quem` n'est pas proposé ; avec `Albaz` au Cimetière, il l'est. **Moitié positive non rejouée** (T52). | T22, T24 | forte (négatif) / non rejouée (positif) |
| R10 | « If … » : nouvelle chaîne après la chaîne en cours | d'accord | **Oui** (voir § 1 pour la moitié « When »). Déclencheurs pendant un coût (`Cocatorium` → `Mercourier`) ou à la résolution (`Branded Fusion` → `Tri-Brigade Springans Kitt`, `Nadir Servant` → `Guiding Quem`) : proposés après `CHAIN_END`. | T15, T24, T33, T62, T63 (T19 et T61 : partielles) | forte |
| R11 | Archétypes par nom ou « always treated as » ; `Albaz` n'est pas « Dogmatika » | d'accord | **Oui.** `Quem` : Dogmatika **et** Despia (listes de `Nadir Servant`, de `Branded Opening`) ; recherche de `Dogmatika Ecclesia` : `Quem` et `The Fallen & The Virtuous` seulement, pas `Albaz` ; `Incredible Ecclesia` et `Dogmatika Ecclesia` sont « Ecclesia », pas `Blazing Cartesia` ni `Ecclesia and the Dark Dragon` (Extra Deck). `The Fallen & The Virtuous` compte comme « Branded » (`Aluber`). | T01, T02, T17, T18, T28, T30, T35, T50 | forte |
| R12 | `Nadir Servant` compare à l'ATK imprimée du monstre envoyé | d'accord | **Oui.** Envoi de `Titaniklad` (2500) : `Albaz`, `White`, `Dogmatika Ecclesia`, `Quem`. Envoi de `Garura` (1500) : `Dogmatika Ecclesia` et `Quem` seulement. | T18, T19 | forte |
| R13 | Un verrou « pas d'Extra Deck » n'empêche pas Deck/Cimetière | d'accord | **Oui.** Sous le verrou de `Nadir Servant`, l'effet de `Titaniklad` propose l'Invocation depuis le Deck, et celui de `Quem` depuis le Cimetière. | T17, T24 | forte |
| R14 | Un effet dont le seul résultat est interdit ne s'active pas | d'accord | **Oui.** Sous le verrou de `Nadir Servant`, l'effet de `Cartesia` (Fusion) et l'Invocation Synchro disparaissent des listes. | T20, T31 | forte |
| R15 | `Incredible Ecclesia` : invocation de procédure sans chaîne ; `Cartesia` : effet avec chaîne | d'accord | **Oui.** `Incredible Ecclesia` apparaît dans la liste des **Invocations Spéciales** (pas des activations) dès que l'adversaire a plus de monstres ; `Cartesia` apparaît dans la liste des **activations**. | T25, T27 | forte |
| R16 | 0 contre 0 : pas d'invocation | d'accord | **Oui** (absente de la liste à 0 contre 0, présente à 0 contre 1). | T27 | forte |
| R17 | « Discard 1 card, then take… » et « Reveal… and send… » sont des effets, mais il faut pouvoir les faire | d'accord | **Oui aux deux.** `Branded Opening` et `Branded in High Spirits` : défausse / révélation à la **résolution**, non payées à l'activation ; `Branded Opening` seule en main n'est pas activable ; `Super Polymerization` (coût `;`) demande une autre carte en main. | T34, T35, T38, T43, T44 | forte |
| R18 | Quick-Play depuis la main : oui ; posée ce tour : non | d'accord | **Oui aux deux.** `Super Polymerization` posée ce tour absente des activations ; `Branded Opening` et `Super Polymerization` activables en main, `Branded Opening` en réponse à `Aluber`. | T35, T39, T41, T59 | forte |
| R19 | `Super Polymerization` : personne ne peut enchaîner | d'accord | **Oui.** Après l'activation, aucune fenêtre de réponse ne propose de carte (ni `Branded Opening` en main, ni `Ash` adverse). | T42 | forte |
| R20 | `Garura` avec `Cartesia` + `Quem` | d'accord | **Oui** (proposée). | T39 | forte |
| R21 | `Branded in High Spirits` : DEF 2500 compte ; pas de reprise après activation | d'accord | **Oui aux deux.** Révélation de `Springans Kitt` : propose `The Dragon that Devours the Dogma` (3000/2500) ; liste complète identique à T43. Reprise : non proposée à la Phase de Fin après activation. | T43, T44, T46 | forte |
| **R23** | Obligatoire ; effets de Phase de Fin un par un, chacun dans sa chaîne | d'accord | **Désaccord sur « obligatoire »** (voir § 1). **Confirmé sur l'ordre** : `Incredible Ecclesia` puis `Titaniklad`, chacun dans sa propre chaîne (séparés par `CHAIN_END`). | T37 | forte (ordre) / non concluant (obligatoire) |
| R24 | Un monstre ne remplit qu'une ligne ; `Albion` ne sert pas de matériel | d'accord | **Oui aux deux.** `The Dragon that Devours the Dogma` absente avec deux monstres seulement, présente avec un 3ᵉ ; `Super Polymerization` non activable avec `Albaz` + `Albion`. | T54, T55, T56 | forte |
| R25 | `Sprind` : un monstre Invoqué Normalement ne convient pas | d'accord | **Oui.** `Albaz` Normal + `Cartesia` Spécial ce tour : `Sprind` proposé ; sans monstre Spécial ce tour, `Super Polymerization` n'est pas activable. La variante exacte de T57 (`Albaz` Spécial + `Aluber` Normal) n'a pas été rejouée. | T57 (variante), T58 | moyenne |
| R26 | Deux Syntoniseurs : pas de Synchro ; `Luluwalilith` interdite sous le verrou de `White` | d'accord | **Oui aux deux.** `Cartesia` + `Quem` : `Ecclesia and the Dark Dragon` absente ; `Incredible Ecclesia` + `Aluber` : présente. `Luluwalilith` est proposée sans le verrou et **disparaît** après l'effet de `White`, alors que `Ecclesia and the Dark Dragon` reste proposée. | T31, T36, T64 | forte |
| R28 | `Mirrorjade` peut bannir son propre monstre ; ne cible pas | d'accord (« il doit ») | **Oui aux deux.** Choix à la résolution (pas de message de ciblage), parmi tous les monstres du terrain, le sien compris, y compris `Mirrorjade` elle-même ; le choix est obligatoire (au moins une carte, annulation impossible). | T61 | forte |
| R29 | `Gold Sarcophagus` : retour en main au tour 5 | d'accord | **Oui.** Activée au tour 1 : la carte revient en main à la Standby Phase du **tour 5** (3ᵉ tour du joueur), pas du tour 3. | T63 | forte |
| R30 | `Fuwalos` à son propre tour et `Ash` contre soi : légaux | d'accord | **Oui aux deux.** `Fuwalos` est dans les activations au tour 1 (aucune carte contrôlée) ; `Ash` en main s'enchaîne à l'effet de `Aluber` du même joueur. | T69, T70 | forte |
| R31 | Pas de pioche ni de Phase de Combat au tour 1 | d'accord | **Oui.** Aucun message de pioche au tour 1, la main reste à 5 ; la Phase de Combat est indisponible. Les tours suivants piochent. | T06 | forte |
| R32 | Un Fusion envoyé sans invocation suffit pour `Springans Kitt` | d'accord | **Oui** (`Titaniklad` envoyé directement : `Springans Kitt` activable). Avec `Granguignol` et `Ecclesia and the Dark Dragon` : non (voir R05). | T47, T48 | forte |
| R33 | `Tri-Brigade Springans Kitt` ne cible pas ; il faut un monstre éligible | d'accord | **Oui aux deux.** Choix à la résolution, sans ciblage ; sans monstre éligible au Cimetière (elle-même exclue), l'effet n'est pas proposé. | T15 | forte |

## 4. Autres constats du banc (utiles au moteur, hors des 34 points)

- **Le cœur fait de la liste des actions légales la source de vérité** : toute action absente de la liste est illégale,
  y compris pour les cartes dont la légalité vient d'une condition de résolution (R01, R14). C'est la forme de
  vérification à reproduire côté moteur : comparer **la liste des actions possibles**, pas seulement le verdict d'une action.
- **Les effets déclenchés simultanés d'un même joueur** sont proposés dans une seule liste ; le premier choisi est le
  maillon 1 et résout en dernier (T62 : `Golden Swordsoul` en maillon 2 résout avant `Mercourier`).
- **Carte posée face cachée** : son activation le tour de la pose est refusée (R18) ; un monstre placé directement sur
  le terrain par le lanceur ne porte pas d'historique d'invocation (il faut jouer l'invocation pour tester `Sprind`).
- **Divergence de texte entre sources** : `Incredible Ecclesia` (R23) et `Mirrorjade` portent la mention « texte non officiel, fonctionnement OCG » dans la base de l'oracle. Les réponses les concernant
  (R23, R28) sont à lire avec cette réserve.
- La limite de **trois exemplaires par nom** pour `Albaz` + `White` (relevée par le relecteur) n'est pas appliquée par
  le lanceur (il ne contrôle pas la légalité d'un deck).

## 5. Limites de ce banc

- **Un seul oracle** : les scripts de cartes sont écrits par une communauté, pas par l'éditeur. Un accord entre
  l'oracle et la lecture est un indice fort, pas une preuve ; un désaccord (R23) oriente vers le texte source.
- **Réglages du duel supposés** (voir § 2). Le TCG actuel et le mode d'EDOPro ne sont pas documentés ici.
- **Un passage par situation**, sans graine variable : le cœur est déterministe, mais je n'ai pas fait varier l'ordre
  du Deck. Les listes de choix (Deck, Extra Deck) ont été comparées aux listes du YAML : identiques sur T07, T18, T19,
  T23, T28, T29, T30, T35, T43, T50, T62.
- Le relecteur n'a vu que des lectures déjà écrites (risque d'ancrage). L'oracle, lui, n'a lu aucune de ces lectures
  avant de répondre : chaque réponse ci-dessus a été obtenue en posant la situation au cœur, puis comparée.

## 6. Reproduire

Tout est dans `~/code/oracle-ignis/` (non versionné). Reconstruire : `premake5 gmake` puis `make config=release
ocgcoreshared` dans `ygopro-core/build`. Les scénarios sont des scripts courts dans `lanceur/` (un fichier par groupe de
points ; `RESULTATS.txt` en garde le résumé). Si le cœur ou les scripts sont mis à jour, rejouer au moins R08, R22,
R27 (b), R34 : ce sont les points qui n'avaient qu'un avis humain.
