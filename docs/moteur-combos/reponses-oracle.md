# Réponses de l'oracle Project Ignis (TOK-86) — relance du 18 novembre 2026

**Statut : oracle installé et utilisé. Les 34 points de règle ont une réponse de l'oracle** (aucun « non testable »),
avec un seul **désaccord franc (R23)** et trois nuances. Rien de Project Ignis n'est dans ce dépôt : ce fichier ne
contient que des résultats (données), jamais du code du cœur, d'un script de carte ou de la base de cartes.

> **Jalon n°6 (18/11) : sections « J2 (18/11) » (§ 8, séquences du jalon n°5, TOK-142) et « J1 échantillon » (§ 9,
> TOK-143) en fin de fichier.**

> **Suite du 18/11 (lot C2 bis) : voir la section « J1 (18/11) » en fin de fichier (§ 7)** : les 30 situations J1 et
> les points N01 à N13, avec un désaccord ferme (N09, `Titaniklad` / `Mirrorjade`).

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

---

# J1 (18/11) — l'oracle rejoue les 30 situations J1 et les points N01 à N13 (lot C2 bis)

**Statut : les 30 situations J1 et les 13 points N ont une réponse** (un seul « non testable » : N12, hors pilote). Même
installation, mêmes réglages que le lot 17 (Master Rule 5 + `DUEL_TCG_SEGOC_NONPUBLIC`, tour 1, nous commençons, terrain
adverse vide sauf mention). Même principe : ce fichier ne contient que des résultats ; rien du cœur, des scripts de
cartes ni de la base de cartes n'est dans ce dépôt, et aucune session du moteur ne doit lire `~/code/oracle-ignis/`.
La session qui a joué ces situations n'a pas lu le code du moteur (`moteur_combos/`) : elle a joué les actions de
`situations-j1.yaml` et de `situations-pour-oracle.md`, puis comparé les listes.

**Bilan** : sur 30 situations, **27 en accord franc**, **1 désaccord (J26, N09)**, **1 accord partiel (J07 : verdict
juste, caractère « obligatoire » contredit, cas R23 déjà connu)**, **1 réponse à une question ouverte (J30, N01)**.
Sur les 13 points N : **9 confirmés** (N02, N03, N05, N06, N07, N08, N10, N11, N13), **1 répondu « non »**
(N01, que la formalisation laissait « non couvert »), **2 contredits en tout ou partie** (N09 ferme, N04 en seconde
moitié), **1 non testable** (N12). **Effets du pilote dont un chemin contredit l'oracle : 2 fermes** (`Titaniklad`
effet 2 et `Mirrorjade` effet 1, une seule règle commune, N09), **3 litigieux** (`Aeon` effet 2, `Mixousia` effets 1
et 3 : N04, seconde moitié), **1 tranché par le texte TCG** (`Incredible Ecclesia` effet 3 : R23).

## 7.1 Désaccords et écarts (à lire d'abord)

| N° | Lecture de la formalisation | Oracle | Cause probable et ce que ça change |
|---|---|---|---|
| **N09 / J26** (désaccord ferme) | Un effet **sans cible** qui « choisit » à la résolution ne propose pas un monstre insensible (`Titaniklad` après son Invocation Fusion, `Dogma` avec un « Ecclesia » au Cimetière) | **Le monstre insensible est proposé et peut être choisi ; l'effet est alors sans effet sur lui.** `Mirrorjade` (envoyer `Albion`, bannir 1 monstre du terrain) liste `Cartesia`, `Mirrorjade` et `Titaniklad` ; en choisissant `Titaniklad` (réellement Invoqué par Fusion, `Mirrorjade` réellement Invoquée de l'Extra Deck), aucun bannissement n'a lieu, l'effet se termine normalement. Même résultat avec `Dogma` insensible (liste : `Mirrorjade`, `Dogma` ; choisie, `Dogma` reste). Témoin : choisir `Cartesia` la bannit. | **Cause : la formalisation retire le monstre de la liste ; le cœur le laisse choisir et applique l'insensibilité au résultat.** Texte TCG et texte de l'oracle identiques sur ce point (« unaffected by the activated effects of any other monsters Special Summoned from the Extra Deck », « unaffected by other cards' effects »). Conséquence pour le moteur : la liste de choix doit contenir le monstre insensible ; la protection s'applique ensuite (aucun déplacement). Le coût du choix change : un joueur peut « gaspiller » l'effet en visant un monstre insensible. Non testé : `Luluwalilith` effet 1 et `Aeon` effet 1, qui suivent probablement la même règle. |
| **N04, seconde moitié** (J17, J18, J19 ; litige) | « Attribut actuel : permis » (on peut déclarer l'Attribut que le monstre a déjà) | **Non.** `Aeon` : l'Attribut déclarable exclut tout Attribut que **tous** les autres monstres ont déjà (avec `Aluber` seul, DARK est absent de la liste ; avec `Aluber` DARK et `Cartesia` LUMIÈRE, tous les Attributs sont déclarables). `Mixousia` : l'Attribut actuel de la cible (DARK pour `Aluber`) est refusé (essai de DARK : « RETRY »), et celui de `Mixousia` elle-même au Cimetière aussi (DARK absent). `Aeon` seule sur le terrain : effet non proposé (aucun autre monstre). | **Cause probable : restriction de script**, pas de texte : le texte TCG de `Aeon` et de `Mixousia` n'interdit pas de déclarer l'Attribut actuel. Le choix de la formalisation tient donc par le texte (précédent R23 : le texte TCG fait foi), mais l'oracle ne le confirme pas. Sans conséquence de jeu (déclarer un Attribut déjà porté est une action sans effet) ; ça ne change qu'une liste de choix. **Première moitié (DIVIN) : confirmée**, l'oracle propose DIVIN dans les trois cas. |
| **R23 / J07** (déjà connu, accord partiel) | `Incredible Ecclesia` effet 3 : obligatoire (lecture : fin de tour illégale sans le résoudre) | **Facultatif** : le cœur propose l'effet à la Phase de Fin dans une liste non forcée, on peut passer et le tour se termine. Il se résout bien quand on l'active (la carte revient en main). | **Cause : le texte OCG de l'oracle** (« You can add this card… », mention « texte non officiel, fonctionnement OCG »). Le texte TCG de la base du dépôt n'a pas « You can » : l'oracle ne peut pas trancher pour le TCG. Le verdict de J07 (« légal ») est confirmé ; la partie « obligatoire » reste **non validée par l'oracle**. |
| **N12** | `Albion` (Cimetière) : « les 2 monstres des zones centrales » = la zone centrale de chaque joueur | **Non testable** : l'effet n'a été proposé dans **aucune** des 8 configurations essayées (2 Zones Monstre Extra chez nous + zone centrale chez nous et chez l'adversaire ; + une zone non centrale ; plateau plein des deux côtés ; Zone Monstre Extra droite côté adverse ; zones 0 et 4, 1 et 3, 2 et 3, 1-2-3). | Cause non identifiée (peut-être une condition du script que les états posés ne remplissent pas ; je n'ai pas lu le script). Hors pilote : sans conséquence pour J1. |

Aucun autre écart. Les valeurs d'ATK ne sont **pas** observables par le lanceur (pas de requête d'état dans le
lanceur) : J14 (+500 ATK), J24 (`Dogma` à 3500), J25 (`Titaniklad` à 3700) sont en accord sur la **légalité, les
listes et les déplacements de cartes**, pas sur les valeurs numériques.

## 7.2 Les 30 situations J1

Colonne « liste » = ce que propose le cœur (noms distincts ; le cœur liste une ligne par exemplaire). « Accord » =
même verdict **et** même liste que `situations-j1.yaml`.

| Id | Effet | Ce que fait le cœur (liste, état d'arrivée) | Verdict |
|---|---|---|---|
| J01 | `Rindbrumm` 1 | `Rindbrumm` annule l'effet d'`EDD` (« chaîne désactivée ») ; question « renvoyer un monstre » : non ; `EDD` reste, rien n'est Invoqué. | accord |
| J02 | `EDD` 1 | `EDD` banni (coût de l'effet) ; liste d'Invocation : `Tri-Brigade Springans Kitt`, `Tri-Brigade Mercourier`, `The Golden Swordsoul`, `Springans Kitt`, `Incredible Ecclesia`, `Guiding Quem`, `Fallen of the White Dragon`, `Fallen of Albaz`, `Blazing Cartesia` = les 9 du YAML. | accord |
| J03 | `EDD` 1 | À la Phase de Fin, `EDD` revient en **zone principale** (le cœur refuse les Zones Monstre Extra, même libres), **dans la position qu'elle avait** (ATK→ATK, DEF→DEF, testé). **N05 confirmé.** | accord |
| J04 | `EDD` 2 | Du Cimetière : cibles `Titaniklad` (Cimetière) puis `Aluber` (terrain) ; `Aluber` → Deck, `Titaniklad` et `EDD` → Extra Deck. | accord |
| J05 | `Cartesia` 3 | Après envoi de `Titaniklad` par `Nadir Servant`, la Phase de Fin propose `Blazing Cartesia` (Cimetière) et `Titaniklad` ; `Cartesia` retourne en main. | accord |
| J06 | `Branded in High Spirits` 2 | Même situation : proposée avec `Titaniklad` ; retourne en main. | accord |
| J07 | `Incredible Ecclesia` 3 | Proposée à la Phase de Fin avec `Titaniklad` ; retourne en main ; **liste non forcée** (R23). Les deux effets de Phase de Fin sont deux chaînes. | **accord partiel** (« légal » oui, « obligatoire » non : voir 7.1) |
| J08 | `Incredible Ecclesia` 1 | Hors pilote. L'adversaire a 1 monstre, nous 0 : `Incredible Ecclesia` est dans la liste des **Invocations Spéciales**, **sans chaîne** (aucun maillon). **R15 confirmé.** | accord |
| J09 | `Cocatorium` 1 | Tribut de `Springans Kitt` (liste de tribut : `Springans Kitt` seul) ; `Cocatorium` Invoquée Spécialement, sans chaîne de déclencheur. | accord |
| J10 | `Cocatorium` 1 | Puis `Super Polymerization` (`Ash Blossom` défaussée) : liste de Fusions `Sprind`, `Rindbrumm` ; matériels `Cocatorium` + `Fallen of Albaz` : **`Cocatorium` est bannie** (jamais au Cimetière) ; `Albaz` au Cimetière ; `Rindbrumm` Invoquée. **N06 confirmé.** | accord |
| J11 | `Ghost Ogre` 1 | `Guiding Quem` Invoquée Normalement, son effet 1 activé ; `Ghost Ogre` (main) chaînée : `Quem` détruite, `Ogre` au Cimetière ; l'effet de `Quem` **se résout quand même** (liste du Deck, un monstre envoyé). **N07 confirmé.** | accord |
| J12 | `TFTV` 1 | Extra Deck proposé (monstres qui mentionnent `Albaz`) : `Titaniklad`, `The Three Champions of Swordsoul`, `Dogma`, `Sprind`, `Rindbrumm`, `Mirrorjade`, `EDD`, `Albion` ; cible `Aluber` (seule carte face visible) détruite. | accord |
| J13 | `TFTV` 2 | `Incredible Ecclesia` au Cimetière : le choix d'effet est unique (le 1ᵉʳ demande une carte face visible sur le terrain) ; cibles : `Incredible Ecclesia`, `Aluber` ; `Aluber` Invoquée Spécialement, son effet proposé. | accord |
| J14 | `Luluwalilith` 1 | `Nadir Servant` envoie `Titaniklad` : `Luluwalilith` est proposée à la fin de la chaîne (question « activer »), puis « annuler un effet : oui/non ». Avec `Quem` en plus (`Quem` 2ᵉ effet, `Albaz` au Cimetière), les deux sont dans **une seule liste**. +500 ATK : non observable. | accord (ATK non lue) |
| J15 | `Luluwalilith` 2 | `Luluwalilith` détruite par `TFTV`, Phase de Fin : `Luluwalilith` et `Titaniklad` proposées ; liste d'Invocation : `Incredible Ecclesia`, `Guiding Quem`, `Dogmatika Ecclesia`, `Blazing Cartesia` = les 4 du YAML. | accord |
| J16 | `Aeon` 1 | Fusions proposées avec `Granguignol` + `Rindbrumm` : `Predaplant Dragostapelia`, `Mixousia`, `Hyperinvoked Aeon` ; `Aeon` Invoquée ; effet : « jusqu'à 2 », liste = `Aeon`, `Super Polymerization`, `Granguignol` (Cimetière), `Rindbrumm` (Cimetière), `Ash Blossom` ; **`Granguignol` du Cimetière est bannissable**. | accord |
| J17 | `Aeon` 2 | LUMIÈRE déclarable (légal) ; `Aluber` (DARK) change d'Attribut (non lu). Nuance N04 (7.1). | accord (+ N04) |
| J18 | `Mixousia` 1 | Cibles : `Mixousia` et `Aluber` (elle peut se cibler) ; EAU déclarable. Nuance N04. | accord (+ N04) |
| J19 | `Mixousia` 3 | Du Cimetière : LUMIÈRE déclarable. Nuance N04. | accord (+ N04) |
| J20 | `Sprind` 1 | `Sprind` M1 → colonne 2 ; « détruire ? : oui » : `Rindbrumm` en Zone Monstre Extra gauche → Cimetière. Même résultat colonne 4 / Zone Monstre Extra droite. Colonne différente : épargnée. **N03 confirmé** (voir § 7.3). | accord |
| J21 | `Sprind` 2 | `Sprind` détruite par `TFTV`, Phase de Fin : `Sprind` et `Titaniklad` proposées ; liste : `Tri-Brigade Springans Kitt`, `Springans Kitt`, `Fallen of the White Dragon`, `Fallen of Albaz` = les 4 du YAML. | accord |
| J22 | `Dogma` 2 | `Cartesia` (effet rapide) : Fusions `Dogma`, `Mixousia`, `Granguignol`, `Albion` ; `Dogma` avec `Albaz` + `Cartesia` + `Aluber` ; son effet : liste de Cimetière `Albaz`, `Cartesia`, `Aluber` (« jusqu'à 2 ») ; `Albaz` mélangeable. | accord |
| J23 | `Dogma` 3 | `Dogma` détruite par `TFTV`, Phase de Fin : liste `Tri-Brigade Springans Kitt`, `Tri-Brigade Mercourier`, `The Fallen & The Virtuous`, `Guiding Quem`, `Dogmatika Ecclesia` = les 5 du YAML. | accord |
| J24 | `Dogma` 1 | `TFTV` cible `Dogma` (proposée comme cible) avec `Incredible Ecclesia` au Cimetière : `Dogma` **reste** sur le terrain (aucun déplacement). 3500 ATK non lu. **N08 confirmé.** | accord (ATK non lue) |
| J25 | `Titaniklad` 1 | `Super Polymerization` : liste `Titaniklad`, `Predaplant Dragostapelia`, `Mixousia`, `Mirrorjade`, `Albion` ; `Titaniklad` avec `Albaz` + `Granguignol` Invoquée. 3700 ATK non lu. | accord (ATK non lue) |
| J26 | `Titaniklad` 2 | Voir N09 (7.1) : `Titaniklad` est **proposée** à `Mirrorjade`, choisie, **non bannie**. | **désaccord** |
| J27 | `Three Champions` 1 | Synchro (`Incredible Ecclesia` Syntoniseur + `Aluber`) ; liste de recherche : `Incredible Ecclesia` (Deck et Cimetière), `Guiding Quem`, `Dogmatika Ecclesia`, `Blazing Cartesia` = les 4 du YAML. | accord |
| J28 | `Three Champions` 2 | Cible `Aluber` (elle peut aussi se cibler) ; avec `Albaz` au Cimetière, « détruire ? » est proposé, `Aluber` détruit ; sans `Albaz` ni « Ecclesia » au Cimetière, pas de destruction. | accord |
| J29 | `Branded Opening` 2 | `TFTV` cible `Rindbrumm` ; à la résolution : « bannir `Branded Opening` à la place ? » ; oui : `Branded Opening` bannie, `Rindbrumm` reste. **N10 confirmé** (contre sa propre `TFTV`). | accord |
| J30 | — | Synchro de `Luluwalilith` (`Quem` Syntoniseur + `Dogmatika Ecclesia` + `Aluber`) : **aucun déclenchement** (ni question d'activation, ni liste), le tour reprend la main. **N01 : non.** | répond à la question (la formalisation : « non couvert ») |

## 7.3 Les points N01 à N13

| N° | Question | Réponse de l'oracle | Situation | Confiance |
|---|---|---|---|---|
| N01 | `Luluwalilith` se déclenche-t-elle sur sa propre sortie de l'Extra Deck ? | **Non.** Rien n'est proposé après son Invocation Synchro. Elle se déclenche bien sur la sortie d'**une autre** carte (J14). | J30, J14 | moyenne (comportement de script) |
| N02 | `Branded Opening` activable sans monstre « Despia » dans le Deck ? `Dogmatika Ecclesia` sans carte « Dogmatika » à chercher ? | **Non aux deux.** `Branded Opening` absente des activations (3 `Aluber` et `Quem` au Cimetière ; témoin : activable avec eux dans le Deck). L'effet de recherche de `Dogmatika Ecclesia` n'est pas proposé sans `Quem` ni `TFTV` dans le Deck (témoin : proposé, liste `TFTV` ×3 + `Quem`). **R01 appliqué aux deux parties : confirmé.** | essais dédiés | forte |
| N03 | `Sprind` peut-elle bouger depuis la Zone Monstre Extra ? La destruction « dans sa colonne » touche-t-elle la Zone Monstre Extra des colonnes 2 et 4 ? | **Oui aux deux.** Effet proposé avec `Sprind` en Zone Monstre Extra (destinations : zones principales libres). Colonne 2 → la carte en Zone Monstre Extra gauche est détruite ; colonne 4 → celle de droite ; colonne 2 avec la carte à droite → épargnée. | J20 | forte |
| N04 | Peut-on déclarer DIVIN ? l'Attribut actuel ? | **DIVIN : oui** (proposé pour `Aeon` et `Mixousia`, sur le terrain et au Cimetière). **Attribut actuel : non** (voir 7.1 : restriction de script, litige avec le texte TCG). | J17, J18, J19 | forte (DIVIN) / moyenne (actuel) |
| N05 | `EDD` revient dans quelle zone, quelle position ? | **Zone principale** (jamais une Zone Monstre Extra, même libre), **position conservée** (ATK ou DEF). | J03 | forte |
| N06 | `Cocatorium` matériel de Fusion : bannie ? | **Oui**, bannie (pas au Cimetière). | J10 | forte |
| N07 | L'effet d'un monstre se résout-il s'il est détruit en réponse ? | **Oui.** | J11 | forte |
| N08 | Peut-on cibler un monstre insensible avec `TFTV` ? | **Oui**, il est proposé comme cible ; il reste, la destruction ne s'applique pas. | J24 | forte |
| N09 | Un effet sans cible qui « choisit » peut-il choisir un monstre insensible ? | **Oui, il est proposé et choisissable ; l'effet n'a aucun effet sur lui.** Contredit la formalisation (7.1). | J26 + essai `Dogma` | forte |
| N10 | Le remplacement de `Branded Opening` vaut-il contre sa propre carte ? | **Oui.** | J29 | forte |
| N11 | `Mulcharmy Fuwalos` : une 2ᵉ copie est-elle « l'autre effet Mulcharmy » ? | **Oui** : la 2ᵉ copie reste activable, la 3ᵉ ne l'est plus (au plus 2 effets « Mulcharmy » par tour). `Ash Blossom` n'est pas « Mulcharmy ». | essais dédiés (3 `Fuwalos` en main) | forte |
| N12 | `Albion` (Cimetière) : « les 2 zones centrales » = celle de chaque joueur ? | **Non testable** (voir 7.1). | — | — |
| N13 | `The Golden Swordsoul` se déclenche-t-elle sur son propre bannissement ? | **Non.** Après son activation (qui la bannit en coût), la liste suivante ne contient plus que `Tri-Brigade Mercourier`. Les deux déclencheurs de départ (`Golden Swordsoul`, `Mercourier`) sont dans une **seule liste**. | variante de T62 | forte |

**R22** (déclencheurs simultanés), rejoué sous `DUEL_TCG_SEGOC_FIRSTTRIGGER` sur J14 (`Luluwalilith` + `Quem`) et J21
(`Titaniklad` + `Sprind`) : **même liste unique que sous le réglage par défaut**, rien de nouveau (tous les déclencheurs
y sont facultatifs). La différence du lot 17 (T45) demande des déclencheurs de natures différentes.

## 7.4 Texte de l'oracle différent du texte TCG (comparaison faite sur les 45 cartes du deck et du pilote)

34 cartes ont un texte **identique** (espaces et sauts de ligne mis à part) dans la base de l'oracle et dans celle du
dépôt. 11 diffèrent ; classement par effet sur J1 :

- **Sens différent (OCG), concerne J1** : `Incredible Ecclesia` (« You can add » contre « Add », mention « texte non
  officiel », R23, J07) ; `Mirrorjade` (2ᵉ effet : « If your opponent makes this Fusion Summoned card … leave the field »
  contre « leaves the field because of an opponent's card », texte non officiel ; le 1ᵉʳ effet, seul exercé, est
  identique) ; `Predaplant Dragostapelia` (2ᵉ effet, texte non officiel ; hors pilote).
- **Formulation seule (même sens)** : `Branded Fusion` (« Fusion Material » / « material », « Special Summon monsters from
  the Extra Deck » / « Special Summon from the Extra Deck »), `Gold Sarcophagus` (« 2nd » / « second »), `Albion` (« central »
  / « center »), `Ash Blossom`, `Mistaken Arrest`, `Harpie's Feather Duster`, `Titaniklad` (l'ordre « "Dogmatika" monster or
  "Fallen of Albaz" » est inversé, même contenu), `The Three Champions of Swordsoul` (« if an "Ecclesia" monster or "Fallen of
  Albaz" is in your GY » / « if you have an "Ecclesia" monster or "Fallen of Albaz" in your GY », même sens).
- **Défaut de la base du dépôt (observation, hors du périmètre de ce lot)** : le texte `cards` de `The Three Champions
  of Swordsoul` se termine par « You can only use each effect of "The Three Brave Swordsouls" once per turn » (nom
  d'une autre carte, probablement le nom de la carte d'origine OCG traduit). Un moteur qui rattache la limite d'un effet
  au nom écrit dans le texte pourrait mal la compter ; à vérifier côté moteur.

## 7.5 Réglages, méthode, limites de ce passage

- **Mêmes réglages que le lot 17** (cœur `1e3bcfd`, scripts `ed5ed45b`, base `a40b0ef`) ; déterministe (graine fixe, pas de
  mélange). Un passage par situation. Les listes d'actions de `situations-j1.yaml` ont été comparées aux listes du cœur :
  identiques sur J02, J13, J15, J21, J23, J27 (et sur l'effet de recherche de `Dogmatika Ecclesia`, N02).
- **États de départ** : les monstres « Invocation Fusion / Synchro » sont **posés** par le lanceur (sans historique
  d'Invocation) sauf quand l'historique compte. J26 : `Mirrorjade` est réellement Invoquée par Fusion
  (effet rapide de `Cartesia`) et `Titaniklad` réellement Invoquée par `Super Polymerization` ; sans cela l'insensibilité
  de `Titaniklad` ne s'applique pas à un monstre simplement posé. Les cartes « envoyées ce tour » sont réellement
  envoyées (`Nadir Servant`, `TFTV`).
- **Lanceur étendu** (hors dépôt) : décodage des déclarations d'Attribut, choix de zone de déplacement, listes de choix
  affichées en entier, position des cartes déplacées. **Pas de requête d'état** : les ATK courants ne sont pas lus.
- **Un seul oracle** : les scripts de cartes sont écrits par la communauté. Un accord est un indice fort, pas une preuve.
  Les confiances « moyenne » ci-dessus désignent un comportement qui dépend d'un script plutôt que du cœur.
- **Ce que ce passage ne couvre pas** : les valeurs d'ATK, les situations non reproduites faute de scénario (aucune
  parmi J01 à J30), et N12.

---

# J2 (18/11) — l'oracle rejoue pas à pas les 23 séquences du jalon n°5 (TOK-142, jalon n°6)

**Statut : 23 séquences sur 23 en accord avec l'oracle.** Chaque action (149 pas en tout) est dans la liste que propose
le cœur à son moment, chaque choix écrit est parmi les candidats du cœur, les déplacements de cartes sont les mêmes pas
par pas, et le plateau final est le même (terrain avec les zones, main, Cimetière, bannies). **Aucun premier pas en
désaccord.** Aucun cas où le texte OCG de la base de l'oracle change un verdict. Une différence de modèle à signaler
(retour d'`Ecclesia and the Dark Dragon` en Phase de Fin, ci-dessous), sans effet sur les 23 plateaux.

Même installation et mêmes réglages que les passages précédents (cœur `1e3bcfd`, scripts `ed5ed45b`, base `a40b0ef` ;
Master Rule 5 + `DUEL_TCG_SEGOC_NONPUBLIC`, tour 1, nous commençons, adversaire sans carte). La session qui a joué ces
séquences n'a lu ni `moteur_combos/` ni `scripts/combos_*.py` : elle n'a lu que `sequences-pour-oracle.md` (langage
des règles). Rien de Project Ignis n'entre dans le dépôt.

## 8.1 Désaccords et différences de modèle (à lire d'abord)

**Aucun désaccord de légalité, de choix, de déplacement ni de plateau.**

| N° | Ce qu'écrivent les séquences | Oracle | Ce que ça change |
|---|---|---|---|
| **J2-a** (différence de modèle) | `Ecclesia and the Dark Dragon`, bannie « jusqu'à la Phase de Fin », **revient au passage** en Phase de Fin, avant tout autre effet (8 séquences : G2.1, G2.2, G7.1, G8.1, G8.2, G9.1, G9.2, G10.1) | Le retour est un **effet obligatoire placé dans la liste des effets de Phase de Fin** (avec `Titaniklad`, `Blazing Cartesia`, `Incredible Ecclesia`, `Dogma`…) ; **le joueur choisit quand le jouer** parmi eux (le banc joue chaque effet de Phase de Fin dans sa propre chaîne). Joué en premier, il donne exactement les déplacements et le plateau des séquences (8 sur 8). | **Aucun écart sur les 23 plateaux** (le banc joue le retour en premier, ordre que l'oracle accepte). Mais l'oracle permet aussi de le jouer **après** les autres : au premier passage du banc (retour joué en dernier), G8.1 et G8.2 finissaient avec les mêmes cartes **dans d'autres zones** (`Quem` zone 1, `Cartesia` zone 2, `Ecclesia and the Dark Dragon` zone 3, au lieu de 2, 3, 1). Le moteur ne propose donc qu'un ordre parmi plusieurs : liste d'options plus courte que celle de l'oracle, sans conséquence sur les cartes, avec conséquence sur les zones (pertinent pour `Sprind`, colonnes). À trancher côté moteur (jalon n°7). |

Autres constats, **sans désaccord** :
- **Décisions à une seule option non écrites** : `The Golden Swordsoul` ramène `Incredible Ecclesia` (seul candidat, G2.1,
  G2.2) ; `Branded in High Spirits` envoie `Rindbrumm` (seul candidat, G7.1). Le cœur pose bien la question, avec un
  seul candidat, celui de la séquence. Conforme à la règle du moteur (une décision à une option n'est pas écrite).
- **Coûts sur soi-même** : `Incredible Ecclesia` se Sacrifie et `The Golden Swordsoul` se bannit sans que le cœur demande
  de choisir (3 séquences chacun) ; le choix écrit « coût : sacrifier / bannir X » n'est pas une question chez l'oracle.
- **Effets facultatifs que le cœur propose et que les séquences n'utilisent pas** (refusés par le banc) : 3ᵉ effet de
  `The Dragon that Devours the Dogma` en Phase de Fin (G1.1 à G1.4, après le dernier pas), 3ᵉ effet de `Blazing
  Cartesia` (G5.1 à G5.4, G8.1, G8.2, G9.1, G9.2), réponses `Ash Blossom` / `Ghost Ogre` des mains réelles,
  `Rindbrumm` au Cimetière (G8). Ce ne sont pas des désaccords ; ils indiquent au jalon n°7 des options que la liste du
  moteur doit contenir à ces moments.
- **Déclencheurs simultanés** : G7.1 (`The Golden Swordsoul` maillon 1, `Guiding Quem` maillon 2) et G7.1 étape 7
  (`Quem` effet 2, puis `Three Champions` effet 1) : ordre accepté par le cœur, aussi sous `DUEL_TCG_SEGOC_FIRSTTRIGGER`.

## 8.2 Les 23 séquences

« Pas » = actions numérotées de la séquence. « Premier désaccord » = premier pas où l'oracle refuse l'action ou un choix,
ou produit d'autres déplacements. Toutes les séquences ont été jouées jusqu'au bout.

| Séquence | Pas | Légaux | Premier désaccord | Plateau final | Notes |
|---|---|---|---|---|---|
| G1.1 | 5 | 5 | aucun | identique | — |
| G1.2 | 5 | 5 | aucun | identique | — |
| G1.3 | 5 | 5 | aucun | identique | main réelle (`Ash`, `Ghost Ogre` non activés) |
| G1.4 | 5 | 5 | aucun | identique | main réelle |
| G2.1 | 8 | 8 | aucun | identique | J2-a ; choix unique (`Incredible Ecclesia` par `Golden Swordsoul`) |
| G2.2 | 8 | 8 | aucun | identique | J2-a ; choix unique ; main réelle |
| G3.1 | 6 | 6 | aucun | identique | — |
| G3.2 | 7 | 7 | aucun | identique | `Ghost Ogre` de la main comme matériel de `Granguignol` : accepté ; « détruire ? » de `Three Champions` : oui |
| G3.3 | 6 | 6 | aucun | identique | main réelle |
| G4.1 | 5 | 5 | aucun | identique | — |
| G4.2 | 5 | 5 | aucun | identique | main réelle |
| G5.1 | 4 | 4 | aucun | identique | `Titaniklad` proposé par une question oui/non (seul effet de Phase de Fin) |
| G5.2 | 4 | 4 | aucun | identique | idem |
| G5.3 | 4 | 4 | aucun | identique | idem ; main réelle |
| G5.4 | 4 | 4 | aucun | identique | idem ; main réelle |
| G6.1 | 7 | 7 | aucun | identique | `Cocatorium` détruite par `TFTV` : bannie (comme écrit) |
| G6.2 | 7 | 7 | aucun | identique | main réelle |
| G7.1 | 11 | 11 | aucun | identique | J2-a ; choix unique (`Rindbrumm` par `High Spirits`) ; révélation de `Mulcharmy Fuwalos` acceptée |
| G8.1 | 11 | 11 | aucun | identique | J2-a (zones différentes si le retour est joué en dernier, voir 8.1) |
| G8.2 | 11 | 11 | aucun | identique | J2-a, idem |
| G9.1 | 6 | 6 | aucun | identique | J2-a |
| G9.2 | 6 | 6 | aucun | identique | J2-a ; main réelle |
| G10.1 | 9 | 9 | aucun | identique | J2-a |
| **Total** | **149** | **149** | **0** | **23 / 23** | |

**Compte** : 23 séquences jouées, 0 non testable, 0 désaccord ; 1 différence de modèle (J2-a, 8 séquences concernées).

## 8.3 Texte de l'oracle différent du texte TCG

Cartes des séquences dont le texte de la base de l'oracle diffère (relevé du § 7.4) : `Incredible Ecclesia` (3ᵉ effet,
« You can add » contre « Add », R23) est activée dans 8 séquences (G2.1, G2.2, G7.1, G8.1, G8.2, G9.1, G9.2, G10.1) :
le verdict ne dépend pas du caractère obligatoire, puisque l'effet est joué. Aucune séquence ne termine son tour avec
cet effet disponible et non joué. `Mirrorjade` (G7.1) : seul son Invocation Fusion est jouée, son 2ᵉ effet (texte
différent) n'est pas exercé. **0 cas de texte OCG ≠ TCG qui change un verdict.**

## 8.4 Méthode, contrôles, limites

- **Traduction automatique** de `sequences-pour-oracle.md` en consignes (lanceur hors dépôt, `~/code/oracle-ignis/lanceur/jalon6/`) :
  action numérotée → activation (filtrée par l'emplacement « depuis : … »), Invocation Normale, Invocation Synchro ou
  passage en Phase de Fin ; « choix : activer l'effet déclenché » → choix dans la liste de chaîne ou réponse « oui » ;
  « choix / envoi / coût / cible / fusion / matériaux » → choix parmi les candidats du cœur ; « option », « appliquer »,
  « détruire » → réponse correspondante. Position Attaque ; plus basse zone libre, Zone Monstre Extra gauche pour un
  monstre de l'Extra Deck. La convention « Zone Monstre principale k » = zone k−1 du cœur est **ma supposition** ;
  elle donne les mêmes zones sur les 23 plateaux.
- **Comparé** : présence de chaque action dans la liste du cœur ; présence de chaque carte choisie parmi les candidats ;
  déplacements pas par pas (carte, origine, destination, relevés des messages `MOVE` du cœur) ; plateau final.
- **Replis déclarés** : (1) choix pris dans les déplacements écrits quand la séquence n'écrit pas la décision (3 cas,
  listés en 8.1, tous à candidat unique) ; (2) choix unique ; (3) retour d'`Ecclesia and the Dark Dragon` joué en
  premier quand la séquence l'écrit au passage en Phase de Fin (8 séquences).
- **Témoins négatifs** (le banc sait-il dire non ?) : coût de `Fallen of the White Dragon` remplacé par `Garura` (ne
  mentionne pas `Albaz`) → refusé ; `Dogmatika Ecclesia` retirée du Deck (G4.1) → choix impossible ; étapes 3 et 4 de
  G10.1 inversées → Invocation Synchro absente de la liste ; G5.1 sans son étape 2 → plateau différent. **4 sur 4 détectés.**
  Limite du repli (1) : une séquence qui écrirait un mauvais choix **et** le déplacement correspondant au bon choix ne
  serait pas vue ; les 3 choix concernés ont été vérifiés un par un (candidat unique).
- **Réglages** : rejoué sous Master Rule 5 seul et sous Master Rule 5 + `DUEL_TCG_SEGOC_FIRSTTRIGGER` : **23 sur 23** dans les deux cas.
- **Limites** : un seul oracle (scripts communautaires) ; adversaire sans carte, donc aucune réponse adverse testée ;
  ATK non lus ; zones comparées sous la convention ci-dessus ; un passage par séquence (cœur déterministe).

---

# J1 échantillon (18/11) — l'oracle joue les 86 situations des 20 effets tirés (TOK-143, jalon n°6)

**Statut : 85 situations jouées sur 86, 1 non testable (E18).** Les situations sont dans
`situations-echantillon-j1.yaml`, écrites à partir du texte TCG **avant** de jouer et figées par le commit `59ef481`
(sha256 `c3b49e76d98042c81da5f619c6a03ce9df2f67bd9c0b3588e42706fa95865515`). Ce passage **ne compare pas au moteur**
(la session de l'oracle ne le lit pas) : il donne, pour chaque situation, ce que propose le cœur. Le jalon n°7
exécutera le moteur sur les mêmes situations et comptera les accords (unité : l'effet). Mêmes réglages que § 8.

## 9.1 À lire d'abord

- **Non testable (1)** : **E18** (`DECCLESIA` effet 2, monstre de l'Extra Deck **chez l'adversaire**). Le cœur exige
  que le monstre ait été réellement Invoqué depuis l'Extra Deck ; le lanceur sait poser un monstre adverse, pas lui
  donner un historique d'invocation (témoin : un `RIND` posé **chez nous** ne remplit pas non plus la condition ; un
  `RIND` réellement Invoqué par `BFUSION` la remplit). La moitié « l'un ou l'autre côté » de cette clause reste sans
  réponse de l'oracle.
- **Trois situations où la réponse de l'oracle diffère de la lecture écrite avant de jouer** (champ `attendu`, qui
  n'est pas la référence) : E05, E08, E08b. Cause unique : `Ash Blossom` **en main** est un matériel de Fusion permis
  pour `CARTESIA` (« monstres de la main ou du terrain »), ce que la lecture avait oublié. E05 : `DOGMA` est proposée
  (`ALBAZ` + `CARTESIA` LUMIÈRE + `ASH` monstre à effet) ; E08 : `MIXOUSIA` est proposée (Magicien + `ASH` Zombie) ;
  E08b : l'effet est **proposé** (`MIXOUSIA` avec `CARTESIA` + `ASH`), alors que la clause visée (matériel du
  Cimetière exclu) supposait l'effet impossible. Variante **hors fichier**, déclarée : sans `ASH` en main, l'effet
  n'est pas proposé (le Cimetière ne fournit pas de matériel). Le jalon n°7 compare le moteur à la réponse de
  l'oracle, pas à la lecture.
- **E85** : `CHAMPIONS` (effet 2) peut **cibler** `TITAN` insensible, mais le cœur ne pose **pas** la question
  « détruire ? » : l'effet ne s'applique pas du tout à `TITAN` (ni annulation, ni destruction). À comparer tel quel
  (un moteur qui poserait la question proposerait une décision de plus que l'oracle).
- **Texte OCG ≠ TCG** : aucune des 20 clauses jouées ne porte sur un passage dont le texte diffère (relevé du § 7.4 :
  `Titaniklad`, `Three Champions`, `Gold Sarcophagus` diffèrent par la forme seulement ; `Mirrorjade` et
  `Incredible Ecclesia` par le sens, sur des effets non tirés). **0 cas.** Rappel : le texte TCG de la base du dépôt
  nomme « The Three Brave Swordsouls » dans la limite de `CHAMPIONS` ; l'oracle applique la limite à la carte (E78).
- **Clauses non exerçables** (déclarées dans l'en-tête du fichier, sans situation) : limites par tour de `GARURA/2`,
  `MERC/2`, `TITAN/3`, `CHAMPIONS/1` (un exemplaire), bannissement face cachée et limite de `GSWORD/2`, « 3 matériels
  ou plus » d'`AEON/1`.

## 9.2 Ce que propose le cœur, situation par situation

« proposé » / « non proposé » : l'action ou l'effet figure ou non dans la liste du cœur. Listes : noms distincts, ×n
pour plusieurs exemplaires. ATK lus par une requête d'état du cœur (nouvelle dans le lanceur, voir 9.3).

| Id | Effet | Réponse de l'oracle |
|---|---|---|
| E01 | ALUBER/1 | proposé ; liste : TFTV×3, BHIGH, BOPENING, BFUSION |
| E02 | ALUBER/1 | proposé après l'Invocation Spéciale en Défense ; liste : TFTV×3, BFUSION, BHIGH |
| E03 | ALUBER/1 | non proposé |
| E04 | ALUBER/1 | non proposé (2e copie) |
| E05 | CARTESIA/2 | proposé ; Fusions : DOGMA×2, MIXOUSIA, GRANG, SANCTIFIRE ; matériels de GRANG : ALBAZ (main), CARTESIA (terrain), ASH exclue |
| E06 | CARTESIA/2 | proposé en réponse à l'effet d'ALUBER (maillon 2) |
| E07 | CARTESIA/2 | non proposé : à la Phase de Fin, seul TITAN (question oui/non), aucune fenêtre avec CARTESIA |
| E08 | CARTESIA/2 | proposé ; Fusions : MIXOUSIA, GRANG ; GARURA absente |
| E08b | CARTESIA/2 | **proposé** (MIXOUSIA avec CARTESIA + ASH) ; variante sans ASH : non proposé |
| E09 | CARTESIA/2 | non proposé (2e copie) |
| E10 | BFUSION/1 | proposé ; Fusions : RIND, SANCTIFIRE ; matériels pris dans le Deck (ALBAZ, COCA) |
| E11 | BFUSION/1 | proposé ; matériels de la main, du terrain et du Deck ; SANCTIFIRE avec ALBAZ (main) + CARTESIA (terrain) |
| E12 | BFUSION/1 | Fusions : RIND, SANCTIFIRE ; DOGMA absente |
| E13 | BFUSION/1 | EDD (et CHAMPIONS) proposées avant, absentes après |
| E14 | BFUSION/1 | non proposé après l'Invocation Synchro |
| E15 | BFUSION/1 | 2e copie non proposée |
| E16 | BFUSION/1 | non proposé |
| E17 | DECCLESIA/2 | proposé ; DECCLESIA Invoquée |
| E18 | DECCLESIA/2 | **non testable** (voir 9.1) |
| E19 | DECCLESIA/2 | non proposé |
| E20 | DECCLESIA/2 | non proposé |
| E21 | DECCLESIA/2 | 2e copie non proposée |
| E22 | GARURA/2 | proposé (question oui/non après NADIR) ; 1 carte piochée |
| E23 | GARURA/2 | proposé après la Fusion de MIRROR |
| E24 | NADIR/1 | proposé ; envoyables : les 15 de l'Extra Deck ; ajoutables : QUEM, WHITE×2, ALBAZ, DECCLESIA |
| E25 | NADIR/1 | ajoutables : QUEM, DECCLESIA |
| E26 | NADIR/1 | ALBAZ du Cimetière dans la liste |
| E27 | NADIR/1 | non proposé |
| E28 | NADIR/1 | CARTESIA proposée en réponse (maillon 2), GRANG Invoquée, NADIR se résout ensuite |
| E29 | NADIR/1 | EDD proposée avant, absente après |
| E30 | NADIR/1 | 2e copie non proposée |
| E31 | SPOLY/1 | non proposé |
| E32 | SPOLY/1 | proposé ; Fusion : RIND seule ; SKITT adverse proposé comme matériel, envoyé au Cimetière adverse |
| E33 | SPOLY/1 | non proposé |
| E34 | SPOLY/1 | proposé ; aucune fenêtre de réponse après l'activation (BOPENING jamais proposée) |
| E35 | SPOLY/1 | proposé en réponse à l'effet d'ALUBER |
| E36 | GSWORD/2 | proposé (même liste que MERC) ; Invocables : CARTESIA (main) |
| E37 | GSWORD/2 | proposé depuis le terrain ; Invocables : DECCLESIA (Cimetière) |
| E38 | GSWORD/2 | non proposé (seul MERC) |
| E39 | GSWORD/2 | non proposé après le bannissement de BOPENING |
| E40 | TITAN/3 | proposé ; liste : ALBAZ, WHITE×2, QUEM ; option « ajouter » |
| E41 | TITAN/3 | option « Invoquer Spécialement » ; QUEM Invoqué |
| E42 | TITAN/3 | non proposé |
| E43 | TITAN/3 | non proposé |
| E44 | MERC/2 | proposé ; liste : ALBAZ, WHITE×2, CARTESIA×2, QUEM, IECCLESIA×2, SKITT, TBKITT, GSWORD ; DECCLESIA et MERC absentes |
| E45 | MERC/2 | proposé ; même liste |
| E46 | BOPENING/2 | question proposée ; RIND reste, BOPENING bannie |
| E47 | BOPENING/2 | question proposée, refusée : RIND détruit, BOPENING reste |
| E48 | BOPENING/2 | pas de question ; ALUBER détruit |
| E49 | BOPENING/2 | pas de question ; RIND adverse détruit |
| E50 | BOPENING/2 | question proposée (après le 1er effet de BOPENING ce tour) |
| E51 | BHIGH/2 | proposé ; liste de Phase de Fin : BHIGH, TITAN |
| E52 | BHIGH/2 | non proposé |
| E53 | BHIGH/2 | non proposé |
| E54 | BHIGH/2 | non proposé (seul DOGMA à la Phase de Fin) |
| E55 | LULU/1 | proposé ; question « annuler ? » : non ; LULU 3000, ALUBER 2300 |
| E56 | LULU/1 | cibles d'annulation : LULU, ALUBER |
| E57 | LULU/1 | proposé (même liste que GRANG) ; LULU 3000, GRANG 3000 |
| E58 | LULU/1 | non proposé |
| E59 | LULU/1 | non proposé |
| E60 | LULU/2 | proposé ; liste : DECCLESIA, IECCLESIA×2, CARTESIA×2, QUEM |
| E61 | LULU/2 | CARTESIA de la main dans la liste et Invoquée |
| E62 | LULU/2 | non proposé (seul TITAN) |
| E63 | OGRE/1 | proposé ; QUEM détruit ; l'effet de QUEM se résout (ALBAZ envoyé) |
| E64 | OGRE/1 | proposé depuis le terrain ; ALUBER détruit ; l'effet d'ALUBER se résout |
| E65 | OGRE/1 | non proposé (seule ASH en réponse) |
| E66 | OGRE/1 | non proposé (aucune fenêtre de réponse) |
| E67 | OGRE/1 | 2e copie non proposée |
| E68 | AEON/1 | proposé ; bannissables : AEON (terrain), SPOLY, GRANG, RIND, ASH (Cimetière) ; au moins 1, au plus 2 |
| E69 | AEON/1 | 1 carte acceptée |
| E70 | AEON/1 | 2e effet non proposé |
| E71 | CHAMPIONS/1 | proposé ; liste : IECCLESIA, QUEM, DECCLESIA, CARTESIA×2 (Deck), IECCLESIA (Cimetière) |
| E72 | CHAMPIONS/1 | CARTESIA du Cimetière |
| E73 | CHAMPIONS/1 | non proposé après la résurrection par TFTV (CHAMPIONS est une cible de TFTV) |
| E74 | CHAMPIONS/2 | cibles : CHAMPIONS, ALUBER ; question « détruire ? » ; ALUBER détruit |
| E75 | CHAMPIONS/2 | question refusée ; ALUBER reste |
| E76 | CHAMPIONS/2 | pas de question ; ALUBER reste |
| E77 | CHAMPIONS/2 | question proposée (WHITE au Cimetière) |
| E78 | CHAMPIONS/2 | 2e activation non proposée |
| E79 | TITAN/1 | TITAN 3700 ; Fusions proposées : TITAN, DRAGOSTAPELIA, MIXOUSIA, MIRROR, SANCTIFIRE |
| E80 | TITAN/1 | TITAN 3700 |
| E81 | TITAN/1 | TITAN 2500 |
| E82 | TITAN/2 | TITAN proposé à MIRROR, choisi, reste sur le terrain (3700) |
| E83 | TITAN/2 | TITAN banni |
| E84 | TITAN/2 | TITAN détruit |
| E85 | TITAN/2 | TITAN ciblable par CHAMPIONS ; pas de question « détruire ? » ; TITAN reste |

**Compte** : 86 situations, **85 jouées**, **1 non testable** (E18), **0 cas de texte OCG ≠ TCG** qui change une
réponse. Les 20 effets ont tous au moins 2 situations jouées. Lecture écrite avant de jouer et réponse de l'oracle :
82 accords sur 85 (écarts E05, E08, E08b, une seule cause).

## 9.3 Méthode et limites

- Chaque situation est jouée par un scénario court (lanceur hors dépôt, `~/code/oracle-ignis/lanceur/jalon6/`) qui place
  le départ, joue l'action et relève les listes de choix, les fenêtres de chaîne et les déplacements (`MOVE`). « Posé »
  = placé sans historique d'invocation ; quand l'historique compte (DECCLESIA/2, CHAMPIONS/1, TITAN/1 et 2), il est
  produit en jouant réellement l'invocation.
- **Correctif du lanceur** : la recherche de carte par nom du lanceur rapprochait aussi par l'**alias** de la base ;
  `Fallen of the White Dragon` ayant `Fallen of Albaz` pour alias, un choix « ALBAZ » pouvait prendre WHITE. Corrigé pour
  ce passage (rapprochement par nom exact) et pour le § 8. **Les passages précédents (lots 17 et C2 bis) utilisaient
  l'ancienne recherche** : leurs listes (relevées sur les noms réels) ne sont pas en cause, mais un choix « ALBAZ » a pu
  y jouer WHITE. Les deux cartes ont le même texte de jeu pour l'essentiel (WHITE est traité comme ALBAZ) ; aucune
  réponse publiée n'en dépend à ma connaissance, à revérifier si un point litigieux porte sur ce choix.
- **Requête d'état ajoutée** (ATK des monstres sur le terrain) : les valeurs d'ATK de LULU/1 et TITAN/1 sont lues dans
  le cœur, ce que les passages précédents ne faisaient pas.
- Un seul oracle ; adversaire passif (aucune réponse adverse) ; un passage par situation (cœur déterministe).
