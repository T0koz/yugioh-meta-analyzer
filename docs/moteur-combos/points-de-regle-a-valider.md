# Moteur de combos — points de règle à soumettre à un juge humain (TOK-89)

> 33 points. Pour chacun : **ma lecture** (celle d'un modèle de langage, à partir des textes de la
> table `cards` et du livret de règles cité de mémoire), ma confiance, et les tests qui en dépendent.
> Aucun n'est validé. Réponse attendue par point : « d'accord », « faux, parce que… », « ça dépend de… ».
> Les noms de cartes sont en anglais, comme dans les textes officiels utilisés.

## Les points où je doute le plus (à traiter d'abord)

| N° | Question | Ma lecture | Confiance | Tests |
|---|---|---|---|---|
| R01 | Peut-on activer un effet qui ne pourra rien faire à la résolution (aucune carte à chercher dans le Deck, aucune Fusion possible, aucune carte à défausser) ? | Non. L'activation est illégale. Doute : le Deck est une zone privée, et la règle exacte pour « chercher alors qu'il n'y a rien » peut différer. | moyenne | T02, T05, T11, T22, T34, T44 |
| R07 | `Branded Fusion` : « you cannot Special Summon from the Extra Deck, except Fusion Monsters, **the turn you activate this card** ». Si j'ai déjà fait une Invocation Synchro ce tour, puis-je l'activer ? Et `Branded Opening` (« for the rest of this turn **after this card resolves** ») ? | `Branded Fusion` : non (la restriction vaut pour tout le tour, passé compris). `Branded Opening` : oui. | moyenne | T12, T13 |
| R08 | Si l'effet d'une carte « You can only activate 1 per turn » est annulé (par `Ash Blossom`), la limite est-elle consommée et le verrou s'applique-t-il ? | Oui aux deux : l'effet est annulé, pas l'activation. Si c'est l'**activation** qui est annulée, la carte ne compte pas comme activée. | basse | T14, T21, T72 |
| R09 | Un monstre Fusion envoyé au Cimetière directement depuis l'Extra Deck (par `Nadir Servant`) peut-il être ciblé par `Guiding Quem` pour être Invoqué Spécialement ? | Non : il n'a jamais été correctement invoqué. Le même monstre, invoqué par Fusion puis envoyé au Cimetière, peut revenir. | moyenne | T22, T52 |
| R10 | Un effet « If … : You can » dont la condition se réalise **pendant** la résolution d'un autre effet, ou pendant le paiement d'un coût, peut-il être activé ensuite ? | Oui, dans une nouvelle chaîne, après la chaîne en cours. Seuls les effets « When … you can » ratent leur moment. | moyenne | T15, T19, T24, T33, T61, T62, T63 |
| R14 | Un effet dont le seul résultat possible est interdit par un verrou (Fusion depuis l'Extra Deck sous `Nadir Servant`) peut-il être activé ? | Non. | moyenne | T20, T31 |
| R17 | `Branded Opening` : « Discard 1 card, then take… » sans point-virgule. La défausse est-elle un coût ? Et faut-il une carte à défausser pour activer ? Même question pour « Reveal… and send… » de `Branded in High Spirits`. | Ce sont des effets, pas des coûts (ils se font à la résolution). Il faut quand même pouvoir les faire pour activer. | moyenne | T34, T35, T38, T43 |
| R22 | Deux effets facultatifs du même joueur se déclenchent en même temps (`Granguignol` invoqué par Fusion, `Tri-Brigade Springans Kitt` envoyée au Cimetière). Qui choisit l'ordre dans la chaîne ? | Le joueur, librement. Il peut aussi n'en activer qu'un. | moyenne | T45, T62 |
| R23 | `Incredible Ecclesia` : « During the End Phase, if a Fusion Monster(s) was sent to your GY this turn: Add this card from the GY to your hand » (sans « You can »). Obligatoire ? Et dans quel ordre résout-on plusieurs effets de Phase de Fin ? | Obligatoire. Le joueur du tour active ses effets de Phase de Fin un par un, dans l'ordre qu'il veut, chacun dans sa chaîne. | moyenne | T37 |
| R27 | `Cocatorium` bannit `Tri-Brigade Mercourier` du Deck (coût) et prend son nom. (a) Compte-t-il comme monstre « Tri-Brigade » pour `Tri-Brigade Springans Kitt` ? (b) Le bannissement en coût depuis le Deck est-il « face visible », et déclenche-t-il `Mercourier` et `The Golden Swordsoul` ? | (a) oui ; (b) oui aux deux. | moyenne (a), basse (b) | T32, T33, T62 |
| R30 | Est-il légal d'activer `Mulcharmy Fuwalos` pendant son propre tour, ou d'enchaîner son propre `Ash Blossom` à son propre effet ? | Oui : rien dans les textes ne l'interdit. | moyenne | T69, T70 |

## Lecture des textes : noms, « mentionne », archétypes

| N° | Question | Ma lecture | Confiance | Tests |
|---|---|---|---|---|
| R03 | `Fallen of the White Dragon` (« always treated as "Fallen of Albaz" ») compte-t-il comme « Fallen of Albaz » partout : matériel pris dans le Deck par `Branded Fusion`, carte cherchée par `Nadir Servant`, condition de `Blazing Cartesia` ? | Oui, dans toutes les zones. | moyenne | T07, T11, T17, T18, T25, T28 |
| R04 | « A card / monster that mentions "Fallen of Albaz" » : est-ce toute carte dont le texte contient ce nom entre guillemets ? `Ecclesia and the Dark Dragon` (Synchro) compte-t-il ? Les Magies comptent-elles quand le texte dit « card » ? | Oui aux trois. | moyenne | T23, T29, T33 |
| R05 | « A Fusion Monster that mentions "Fallen of Albaz" **as material** » : faut-il que le nom soit dans la ligne de matériels ? | Oui. `Granguignol` (matériels : `Blazing Cartesia` + 1 LIGHT ou DARK) ne compte pas ; `Titaniklad`, `Rindbrumm`, `Mirrorjade`, `Albion the Sanctifire Dragon`, `Sprind`, `The Dragon that Devours the Dogma` comptent. | haute | T07, T08, T47, T48 |
| R11 | Appartenance à un archétype : par le nom ou par « always treated as ». `Guiding Quem` est-il « Dogmatika » et « Despia » ? `Fallen of Albaz` est-il « Dogmatika » ? `Incredible Ecclesia` et `Dogmatika Ecclesia` sont-ils des monstres « Ecclesia » ? | `Quem` : les deux. `Fallen of Albaz` : **non**. Les deux Ecclesia : oui. `Blazing Cartesia` : ni « Dogmatika » ni « Ecclesia ». | moyenne | T01, T17, T18, T28, T30, T35, T50 |
| R32 | `Springans Kitt` : « If you have a Fusion Monster that mentions "Fallen of Albaz" as material on your field or in your GY ». Un monstre Fusion envoyé au Cimetière sans avoir été invoqué suffit-il ? | Oui : la condition ne demande que sa présence. | moyenne | T47 |

## Fusion et Synchro

| N° | Question | Ma lecture | Confiance | Tests |
|---|---|---|---|---|
| R06 | `Branded Fusion` (« using 2 monsters ») peut-il invoquer `The Dragon that Devours the Dogma` (3 matériels) ? | Non. | moyenne | T09 |
| R20 | `Garura` : « 2 monsters with the same Type and Attribute, but different names ». `Blazing Cartesia` + `Guiding Quem` conviennent-ils ? | Oui (LIGHT Spellcaster tous les deux). | haute | T39 |
| R24 | Un monstre peut-il remplir deux lignes de matériel d'une même Fusion ? `Albion the Sanctifire Dragon` peut-il servir de matériel ? | Non et non (« Cannot be used as Fusion Material »). | haute | T54, T55, T56 |
| R25 | `Sprind` : « 1 Effect Monster Special Summoned this turn ». Un monstre Invoqué Normalement ce tour convient-il ? | Non. | haute | T57, T58 |
| R26 | Synchro : `Ecclesia and the Dark Dragon` (« 1 Tuner + 1+ non-Tuners », Niveau 8) avec deux Syntoniseurs de Niveau 4 ? Verrou de `Fallen of the White Dragon` (« except Level 8 Fusion or Synchro Monsters ») : `Despian Luluwalilith` (Niveau 12) est-elle interdite ? | Deux Syntoniseurs : illégal. `Luluwalilith` : interdite sous ce verrou. | moyenne | T31, T36, T64 |

## Verrous, limites, valeurs

| N° | Question | Ma lecture | Confiance | Tests |
|---|---|---|---|---|
| R12 | `Nadir Servant` : « ATK less than or equal to that sent monster in the GY ». On compare à l'ATK imprimée du monstre envoyé ? | Oui (au Cimetière, pas de modification). | moyenne | T18, T19 |
| R13 | Un verrou « cannot Special Summon from the Extra Deck » empêche-t-il d'invoquer depuis le Deck ou le Cimetière ? | Non. | haute | T17, T24 |
| R21 | `Branded in High Spirits` : « Level 8 Fusion Monster … with the same Type that has 2500 ATK or DEF ». `The Dragon that Devours the Dogma` (3000/2500) convient-il par sa DEF ? Et la limite « 1 effect per turn » interdit-elle de reprendre la carte en Phase de Fin après l'avoir activée ? | Oui et oui. | moyenne | T43, T44, T46 |
| R29 | `Gold Sarcophagus` activée à notre tour 1 : « your second Standby Phase after this card's activation » est-elle celle de notre tour 5 ? | Oui (tour 3 = première, tour 5 = seconde). | moyenne | T63 |

## Structure du tour, chaînes, zones

| N° | Question | Ma lecture | Confiance | Tests |
|---|---|---|---|---|
| R02 | Toute recherche dans le Deck est-elle suivie d'un mélange ? Une carte posée au-dessous du Deck (`Springans Kitt`) y reste-t-elle jusqu'au mélange suivant ? | Oui et oui. | haute | T01, T49 |
| R15 | `Incredible Ecclesia` (« you can Special Summon this card (from your hand) ») : invocation sans chaîne. `Blazing Cartesia` (« If you control … : You can Special Summon this card from your hand ») : effet activé, avec chaîne. Exact ? | Oui (la présence de « : » fait la différence). | moyenne | T25, T27 |
| R16 | « If your opponent controls more monsters than you do » avec 0 contre 0 ? | Faux : pas d'invocation. | haute | T27 |
| R18 | Une Magie Jeu-Rapide peut-elle être activée depuis la main pendant son propre tour, en réponse à son propre effet ? Et le tour où elle a été posée face cachée ? | Depuis la main : oui. Posée ce tour : non. | haute | T35, T39, T41, T59 |
| R19 | `Super Polymerization` : puis-je enchaîner ma propre carte à son activation ? | Non (« Neither player »). | haute | T42 |
| R28 | `Mirrorjade` : « banish 1 monster on the field ». Peut-elle bannir un monstre de son propre contrôleur ? L'effet cible-t-il ? | Oui ; il ne cible pas (pas de « target »). | moyenne | T61 |
| R31 | Le joueur qui commence ne pioche pas et n'a pas de Phase de Combat au tour 1 ? | Oui. | haute | T06 |
| R33 | `Tri-Brigade Springans Kitt` (« Special Summon 1 of the following monsters from your GY ») : l'effet cible-t-il ? Faut-il un monstre éligible au Cimetière pour l'activer ? | Il ne cible pas ; il faut au moins un monstre éligible à l'activation. | moyenne | T15 |

## Questions de règle hors des tests, apparues en écrivant les définitions

Elles conditionnent la forme de l'état (definitions-et-schema.md § 2.1) :

1. Un « une fois par tour » est-il consommé **à l'activation**, même si l'effet est annulé ? (ma lecture : oui)
2. L'**ordre des cartes au Cimetière** a-t-il une importance pour une carte TCG actuelle ? (ma lecture : non pour le pilote)
3. La **colonne** d'un monstre ne compte-t-elle que pour les cartes qui en parlent (`Sprind`, `Albion the Sanctifire Dragon`) ? Si oui, peut-on placer les monstres dans une zone par défaut sans perdre de combo ? (décision D3)
4. Un monstre Fusion peut-il être placé au choix en Zone Monstre Extra ou en Zone Monstre Principale ? (ma lecture : oui)
