# Échantillon J1 et effets du pilote, pour l'oracle (TOK-143, jalon n°5)

> **18/11/2026**, généré par `scripts/combos_export_echantillon.py`. Pour la session de l'oracle (jalon n°6, isolée) : tout est dit en termes de jeu ; aucune structure du moteur, aucun texte de carte recopié (les descriptions sont nos paraphrases). **Numéro d'effet** = rang de l'effet dans **notre lecture du texte TCG**, dans l'ordre du texte (une phrase continue, comme un gain d'ATK, compte comme un effet) : il peut différer des numéros ①②③ imprimés ; en cas de doute, se fier à la description.

## 1. Les 20 effets tirés (graine 20260118)

Tirage simple sans remise, 10 par strate, listes triées par (carte, numéro) avant le tirage (`moteur_combos/echantillon.py`, méthode validée par `data-scientist-ygo`). **Strate a** : effets exercés par au moins une situation de `tests-branded.yaml` (30 effets). **Strate b** : effets exercés seulement par `situations-j1.yaml` (27 effets). Verdict attendu par effet : toutes ses clauses jouées comme l'oracle les joue (unité = l'effet). Taux global pondéré par strate : 30/57 et 27/57.

| # | Strate | Carte | Effet n° | Genre, zone, déclencheur ou condition | Situations déjà jouées dans l'oracle |
|---|---|---|---|---|---|
| 1 | a | Aluber the Jester of Despia | 1 | effet déclenché (terrain) — Invoqué Normalement ou Spécialement : ajouter 1 Magie/Piège « Branded » du Deck à la main | T01, T59 |
| 2 | a | Blazing Cartesia, the Virtuous | 2 | effet rapide (terrain) — Phase Principale, effet rapide : Invocation Fusion d'un monstre Fusion de Niveau 8 ou plus, matériels de la main ou du terrain | J22, T45, ~~T53~~, T55 |
| 3 | a | Branded Fusion | 1 | activation de la carte (main) — Invocation Fusion d'un monstre qui mentionne Albaz comme matériel, avec 2 monstres de la main, du Deck ou du terrain ; verrou « Extra Deck = Fusion » posé dès… | T07, T15 |
| 4 | a | Dogmatika Ecclesia, the Virtuous | 2 | effet d'ignition (main) — Un monstre Invoqué Spécialement depuis l'Extra Deck est sur le terrain (l'un ou l'autre côté) : s'Invoquer Spécialement depuis la main | T50 |
| 5 | a | Garura, Wings of Resonant Life | 2 | effet déclenché (Cimetière) — Envoyée au Cimetière (depuis l'Extra Deck aussi) : piocher 1 carte (branche de hasard) | T19* |
| 6 | a | Nadir Servant | 1 | activation de la carte (main) — Envoyer 1 monstre de l'Extra Deck au Cimetière, puis ajouter du Deck ou du Cimetière 1 monstre « Dogmatika » ou « Fallen of Albaz » d'ATK inférieure ou égale à l'ATK… | J14, T18, T19* |
| 7 | a | Super Polymerization | 1 | activation de la carte (main, terrain) — Magie Jeu-Rapide | J10, J16, J25, J26†, T39, T58 |
| 8 | a | The Golden Swordsoul | 2 | effet déclenché (terrain, Cimetière) — Un monstre est banni face visible (bannir en coût compte) : se bannir du terrain ou du Cimetière ; Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du… | T62 |
| 9 | a | Titaniklad the Ash Dragon | 3 | effet de Phase de Fin (Cimetière) — Phase de Fin, envoyé au Cimetière ce tour : ajouter ou Invoquer Spécialement 1 « Fallen of Albaz » ou 1 monstre « Dogmatika » du Deck (le verrou de Nadir ne vise que… | T17* |
| 10 | a | Tri-Brigade Mercourier | 2 | effet déclenché (bannie) — Bannie (en coût aussi) : ajouter du Deck « Fallen of Albaz » ou 1 monstre qui le mentionne, sauf lui | T33, T61*, T62, T63 |
| 11 | b | Branded Opening | 2 | effet continu (Cimetière) — Effet de remplacement, ne s'active pas : un monstre Fusion du joueur serait détruit par un effet → bannir cette carte du Cimetière à la place | J29 |
| 12 | b | Branded in High Spirits | 2 | effet de Phase de Fin (Cimetière) — Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main | J06 |
| 13 | b | Despian Luluwalilith | 1 | effet déclenché (terrain) — Une carte quitte l'Extra Deck : les monstres contrôlés gagnent 500 ATK (permanent), puis on peut annuler les effets d'1 carte face visible jusqu'à la fin du tour | J14 |
| 14 | b | Despian Luluwalilith | 2 | effet de Phase de Fin (Cimetière) — Phase de Fin, envoyée au Cimetière ce tour : Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du Deck dont l'ATK égale la DEF | J15 |
| 15 | b | Ghost Ogre & Snow Rabbit | 1 | effet rapide (main, terrain) — En réponse à l'effet d'un monstre sur le terrain (ou d'une Magie/Piège déjà face visible : aucune dans le deck) : s'envoyer au Cimetière ; détruire cette carte | J11 |
| 16 | b | Hyperinvoked Aeon | 1 | effet déclenché (terrain) — Invoquée par Fusion : bannir des cartes du terrain et/ou des Cimetières, jusqu'au nombre de matériels ; avec 3 matériels ou plus, regarder l'Extra Deck adverse : hors… | J16 |
| 17 | b | The Three Champions of Swordsoul | 1 | effet déclenché (terrain) — Invoquée par Synchro : ajouter du Deck ou du Cimetière 1 Magicien de Niveau 4 ou 8 dont l'ATK égale la DEF | J27 |
| 18 | b | The Three Champions of Swordsoul | 2 | effet d'ignition (terrain) — Cibler 1 carte face visible ; annuler ses effets, puis, avec un monstre « Ecclesia » ou « Fallen of Albaz » au Cimetière, on peut la détruire | J28 |
| 19 | b | Titaniklad the Ash Dragon | 1 | effet continu (terrain) — Gagne 100 ATK par Niveau d'origine des matériels de son Invocation Fusion | J25 |
| 20 | b | Titaniklad the Ash Dragon | 2 | effet continu (terrain) — Après son Invocation Fusion, pour le reste du tour : insensible aux effets activés des autres monstres Invoqués Spécialement depuis l'Extra Deck | J26† |

## 2. Les 57 effets du pilote et les situations qui les exercent

Situations : `T..` = `tests-branded.yaml`, `J..` = `situations-j1.yaml`. Marques : `*` rejouée **en partie** seulement par l'oracle ; `~~T52~~` **non rejouée** ; `†` désaccord ou accord partiel avec l'oracle (T37, J07 : R23 ; J26 : N09, corrigé depuis). J14, J24, J25 : accord sur la légalité et les déplacements, valeurs d'ATK non lues par l'oracle.

**Effets jamais exercés devant l'oracle : 0**. **Exercés seulement par des situations rejouées en partie : 3** — Garura, Wings of Resonant Life 2, Springans Kitt 2, Titaniklad the Ash Dragon 3. **Exercés seulement par une situation en désaccord avec l'oracle : 2** — Incredible Ecclesia, the Virtuous 3, Titaniklad the Ash Dragon 2. « Exercé » = l'effet est résolu au moins une fois quand le moteur rejoue la situation ; une situation où l'effet est seulement proposé dans une liste ne compte pas.

| Carte | Effet n° | Strate | Tiré | Genre, zone, déclencheur ou condition | Situations |
|---|---|---|---|---|---|
| Albion the Sanctifire Dragon | 1 | a |  | effet continu (terrain) — Ne sert pas de matériel de Fusion | T56 |
| Aluber the Jester of Despia | 1 | a | oui | effet déclenché (terrain) — Invoqué Normalement ou Spécialement : ajouter 1 Magie/Piège « Branded » du Deck à la main | T01, T59 |
| Ash Blossom & Joyous Spring | 1 | a |  | effet rapide (main) — En réponse à une activation qui ajoute du Deck à la main, invoque du Deck ou envoie du Deck au Cimetière (catégories déclarées par chaque effet) : se défausser ;… | T70 |
| Blazing Cartesia, the Virtuous | 1 | a |  | effet d'ignition (main) — « Fallen of Albaz » contrôlé ou au Cimetière (noms « always treated as » compris) : s'Invoquer Spécialement depuis la main | T25 |
| Blazing Cartesia, the Virtuous | 2 | a | oui | effet rapide (terrain) — Phase Principale, effet rapide : Invocation Fusion d'un monstre Fusion de Niveau 8 ou plus, matériels de la main ou du terrain | J22, T45, ~~T53~~, T55 |
| Blazing Cartesia, the Virtuous | 3 | b |  | effet de Phase de Fin (Cimetière) — Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main | J05 |
| Branded Fusion | 1 | a | oui | activation de la carte (main) — Invocation Fusion d'un monstre qui mentionne Albaz comme matériel, avec 2 monstres de la main, du Deck ou du terrain ; verrou « Extra Deck = Fusion » posé dès… | T07, T15 |
| Branded Opening | 1 | a |  | activation de la carte (main, terrain) — Magie Jeu-Rapide | T13*, T35, T59 |
| Branded Opening | 2 | b | oui | effet continu (Cimetière) — Effet de remplacement, ne s'active pas : un monstre Fusion du joueur serait détruit par un effet → bannir cette carte du Cimetière à la place | J29 |
| Branded in High Spirits | 1 | a |  | activation de la carte (main, terrain) — Magie Jeu-Rapide | T43 |
| Branded in High Spirits | 2 | b | oui | effet de Phase de Fin (Cimetière) — Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main | J06 |
| Cocatorium the Heavy Metal Avian | 1 | b |  | effet d'ignition (main, Cimetière) — Main ou Cimetière | J09, J10 |
| Cocatorium the Heavy Metal Avian | 2 | a |  | effet d'ignition (terrain) — Coût : bannir du Deck (face visible) 1 Bête, Bête-Guerrier ou Bête Ailée de Niveau 4 ou moins ; cette carte prend son nom, son Type, son Attribut et son Niveau… | T33, T62 |
| Despian Luluwalilith | 1 | b | oui | effet déclenché (terrain) — Une carte quitte l'Extra Deck : les monstres contrôlés gagnent 500 ATK (permanent), puis on peut annuler les effets d'1 carte face visible jusqu'à la fin du tour | J14 |
| Despian Luluwalilith | 2 | b | oui | effet de Phase de Fin (Cimetière) — Phase de Fin, envoyée au Cimetière ce tour : Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du Deck dont l'ATK égale la DEF | J15 |
| Dogmatika Ecclesia, the Virtuous | 2 | a | oui | effet d'ignition (main) — Un monstre Invoqué Spécialement depuis l'Extra Deck est sur le terrain (l'un ou l'autre côté) : s'Invoquer Spécialement depuis la main | T50 |
| Dogmatika Ecclesia, the Virtuous | 3 | a |  | effet déclenché (terrain) — Invoqué Normalement ou Spécialement : ajouter 1 carte « Dogmatika » du Deck (sauf lui) ; verrou « aucune Invocation Spéciale depuis l'Extra Deck » pour le reste du tour | T50 |
| Ecclesia and the Dark Dragon | 1 | b |  | effet rapide (terrain) — Phase Principale, effet rapide : se bannir jusqu'à la Phase de Fin (effet, pas coût) et, si c'est fait, Invoquer Spécialement « Fallen of Albaz » ou 1 monstre de… | J02, J03 |
| Ecclesia and the Dark Dragon | 2 | b |  | effet d'ignition (Cimetière) — Au Cimetière : cibler 1 monstre Fusion de Niveau 8 au Cimetière ou banni et 1 carte du terrain ; les mélanger dans le Deck avec cette carte | J04 |
| Fallen of the White Dragon | 1 | a |  | effet d'ignition (main) — Coût : envoyer de l'Extra Deck au Cimetière 1 monstre qui mentionne « Fallen of Albaz » ; s'Invoquer Spécialement, verrou « Extra Deck = Fusion ou Synchro de Niveau 8… | T29 |
| Fallen of the White Dragon | 2 | a |  | effet déclenché (terrain) — Invoqué Normalement ou Spécialement : Invoquer Spécialement 1 monstre « Ecclesia » de la main, du Deck ou du Cimetière | T30 |
| Garura, Wings of Resonant Life | 2 | a | oui | effet déclenché (Cimetière) — Envoyée au Cimetière (depuis l'Extra Deck aussi) : piocher 1 carte (branche de hasard) | T19* |
| Ghost Ogre & Snow Rabbit | 1 | b | oui | effet rapide (main, terrain) — En réponse à l'effet d'un monstre sur le terrain (ou d'une Magie/Piège déjà face visible : aucune dans le deck) : s'envoyer au Cimetière ; détruire cette carte | J11 |
| Gold Sarcophagus | 1 | a |  | activation de la carte (main) — Bannir 1 carte du Deck face visible ; elle rejoint la main à la 2e Standby Phase du joueur après l'activation (tour 5 si activée au tour 1) : effet différé enregistré… | T63 |
| Granguignol the Dusk Dragon | 1 | a |  | effet déclenché (terrain) — Invoquée par Fusion : envoyer au Cimetière 1 monstre LUMIÈRE ou TÉNÈBRES de Niveau 6 ou plus, du Deck ou de l'Extra Deck | T45, ~~T53~~ |
| Guiding Quem, the Virtuous | 1 | a |  | effet déclenché (terrain) — Invoqué Normalement ou Spécialement : envoyer du Deck au Cimetière « Fallen of Albaz » ou 1 carte qui le mentionne | J11, T23 |
| Guiding Quem, the Virtuous | 2 | a |  | effet déclenché (terrain) — Une carte quitte l'Extra Deck : cibler au Cimetière « Fallen of Albaz » ou 1 monstre qui le mentionne (sauf Quem) ; l'Invoquer Spécialement | T24 |
| Hyperinvoked Aeon | 1 | b | oui | effet déclenché (terrain) — Invoquée par Fusion : bannir des cartes du terrain et/ou des Cimetières, jusqu'au nombre de matériels ; avec 3 matériels ou plus, regarder l'Extra Deck adverse : hors… | J16 |
| Hyperinvoked Aeon | 2 | b |  | effet rapide (terrain) — Effet rapide : déclarer 1 Attribut ; les autres monstres du terrain le prennent jusqu'à la fin du tour | J17 |
| Incredible Ecclesia, the Virtuous | 1 | b |  | Invocation par sa propre procédure (main) — Invocation Spéciale par procédure depuis la main, sans chaîne, si l'adversaire contrôle plus de monstres ; une fois par tour de cette façon | J08 |
| Incredible Ecclesia, the Virtuous | 2 | a |  | effet rapide (terrain) — Phase Principale, effet rapide | T28 |
| Incredible Ecclesia, the Virtuous | 3 | b |  | effet de Phase de Fin (Cimetière) — Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main | J07† |
| Mirrorjade the Iceblade Dragon | 1 | a |  | effet rapide (terrain) — Une fois par tour, effet rapide | J26†, T61* |
| Mixousia the Confounder | 1 | b |  | effet d'ignition (terrain) — Cibler 1 monstre face visible et déclarer 1 Attribut : il le prend (tant qu'il reste face visible) | J18 |
| Mixousia the Confounder | 3 | b |  | effet d'ignition (Cimetière) — Au Cimetière : déclarer 1 Attribut ; cette carte le prend au Cimetière jusqu'à la fin du tour | J19 |
| Mulcharmy Fuwalos | 1 | a |  | effet rapide (main) — Effet rapide, si l'on ne contrôle aucune carte (à son propre tour aussi) | T69 |
| Nadir Servant | 1 | a | oui | activation de la carte (main) — Envoyer 1 monstre de l'Extra Deck au Cimetière, puis ajouter du Deck ou du Cimetière 1 monstre « Dogmatika » ou « Fallen of Albaz » d'ATK inférieure ou égale à l'ATK… | J14, T18, T19* |
| Rindbrumm the Striking Dragon | 1 | b |  | effet rapide (terrain) — Effet rapide en réponse à l'effet d'un monstre Fusion/Synchro/Xyz/Lien (les siens aussi) : annuler cet effet, puis on peut renvoyer 1 monstre du terrain en main… | J01 |
| Sprind the Irondash Dragon | 1 | b |  | effet d'ignition (terrain) — Phase Principale du joueur : se déplacer vers une autre de ses zones Monstre principales, puis on peut détruire les autres cartes face visible de sa colonne (D3 :… | J20 |
| Sprind the Irondash Dragon | 2 | b |  | effet de Phase de Fin (Cimetière) — Phase de Fin, envoyé au Cimetière ce tour : ajouter ou Invoquer Spécialement 1 monstre « Springans » ou « Fallen of Albaz » du Deck | J21 |
| Springans Kitt | 1 | a |  | effet d'ignition (main) — Un monstre Fusion qui mentionne Albaz comme matériel sur le terrain ou au Cimetière (présence seulement) : s'Invoquer Spécialement depuis la main | T47 |
| Springans Kitt | 2 | a |  | effet déclenché (terrain) — Invoquée Normalement ou Spécialement : ajouter 1 Magie/Piège « Branded » bannie, du Deck ou du Cimetière, puis placer 1 carte de la main au-dessous du Deck (après le… | T49* |
| Super Polymerization | 1 | a | oui | activation de la carte (main, terrain) — Magie Jeu-Rapide | J10, J16, J25, J26†, T39, T58 |
| The Dragon that Devours the Dogma | 1 | b |  | effet continu (terrain) — Un monstre « Ecclesia » sur le terrain ou dans un Cimetière : +500 ATK et insensible aux effets des autres cartes | J24 |
| The Dragon that Devours the Dogma | 2 | b |  | effet déclenché (terrain) — Invoquée Spécialement : mélanger dans le Deck jusqu'à 2 cartes des Cimetières ou des bannies | J22 |
| The Dragon that Devours the Dogma | 3 | b |  | effet de Phase de Fin (Cimetière) — Phase de Fin, envoyée au Cimetière ce tour : ajouter 1 carte « Dogmatika » ou « Tri-Brigade » du Deck | J23 |
| The Fallen & The Virtuous | 1 | b |  | activation de la carte (main, terrain) — Magie Jeu-Rapide, 1er effet choisi à l'activation | J12, J24, J29 |
| The Fallen & The Virtuous | 2 | b |  | activation de la carte (main, terrain) — 2e effet : un monstre « Ecclesia » sur le terrain ou au Cimetière ; cibler 1 monstre dans un Cimetière ; l'Invoquer Spécialement sur son terrain | J13 |
| The Golden Swordsoul | 2 | a | oui | effet déclenché (terrain, Cimetière) — Un monstre est banni face visible (bannir en coût compte) : se bannir du terrain ou du Cimetière ; Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du… | T62 |
| The Three Champions of Swordsoul | 1 | b | oui | effet déclenché (terrain) — Invoquée par Synchro : ajouter du Deck ou du Cimetière 1 Magicien de Niveau 4 ou 8 dont l'ATK égale la DEF | J27 |
| The Three Champions of Swordsoul | 2 | b | oui | effet d'ignition (terrain) — Cibler 1 carte face visible ; annuler ses effets, puis, avec un monstre « Ecclesia » ou « Fallen of Albaz » au Cimetière, on peut la détruire | J28 |
| Titaniklad the Ash Dragon | 1 | b | oui | effet continu (terrain) — Gagne 100 ATK par Niveau d'origine des matériels de son Invocation Fusion | J25 |
| Titaniklad the Ash Dragon | 2 | b | oui | effet continu (terrain) — Après son Invocation Fusion, pour le reste du tour : insensible aux effets activés des autres monstres Invoqués Spécialement depuis l'Extra Deck | J26† |
| Titaniklad the Ash Dragon | 3 | a | oui | effet de Phase de Fin (Cimetière) — Phase de Fin, envoyé au Cimetière ce tour : ajouter ou Invoquer Spécialement 1 « Fallen of Albaz » ou 1 monstre « Dogmatika » du Deck (le verrou de Nadir ne vise que… | T17* |
| Tri-Brigade Mercourier | 2 | a | oui | effet déclenché (bannie) — Bannie (en coût aussi) : ajouter du Deck « Fallen of Albaz » ou 1 monstre qui le mentionne, sauf lui | T33, T61*, T62, T63 |
| Tri-Brigade Springans Kitt | 1 | a |  | effet d'ignition (main) — Depuis la main, si l'on contrôle un monstre « Tri-Brigade » ou « Springans » (autre que lui) : s'Invoquer Spécialement | T32 |
| Tri-Brigade Springans Kitt | 2 | a |  | effet déclenché (Cimetière) — Envoyé au Cimetière : Invoquer Spécialement en Défense, depuis le Cimetière, 1 monstre « Tri-Brigade », « Springans », ou Fallen of Albaz ou une carte qui le… | T15, T45, ~~T52~~ |

## 3. Effets hors périmètre (15, relus en exhaustif, à part)

Effets qui supposent l'adversaire, la Phase de Combat ou un autre tour : non joués par le moteur au tour 1. À vérifier dans l'oracle : que leur condition est bien fausse au tour 1 du pilote.

| Carte | Effet n° | Genre, zone, déclencheur ou condition |
|---|---|---|
| Albion the Sanctifire Dragon | 2 | effet rapide (terrain) — Tour adverse seulement |
| Albion the Sanctifire Dragon | 3 | effet d'ignition (Cimetière) — ; demande des monstres adverses |
| Aluber the Jester of Despia | 2 | effet déclenché (Cimetière) — Monstre Fusion détruit au combat ou quittant le terrain par un effet adverse : impossible au tour 1 du pilote (pas de combat, pas d'adversaire) |
| Dogmatika Ecclesia, the Virtuous | 1 | effet continu (terrain) — Indestructible au combat contre un monstre Invoqué Spécialement depuis l'Extra Deck : combat, hors du pilote |
| Droll & Lock Bird | 1 | effet rapide (main) — Répond à un ajout du Deck à la main de l'adversaire : n'arrive jamais dans le pilote |
| Fallen of Albaz | 1 | effet déclenché (terrain) — Coût : défausser 1 carte |
| Garura, Wings of Resonant Life | 1 | effet continu (terrain) — Dégâts de combat doublés : combat, hors pilote |
| Granguignol the Dusk Dragon | 2 | effet déclenché (terrain, Cimetière) — Un monstre est Invoqué Spécialement par un effet de monstre adverse : hors pilote |
| Mirrorjade the Iceblade Dragon | 2 | effet déclenché (terrain) — Quitte le terrain à cause d'une carte adverse : hors pilote |
| Mixousia the Confounder | 2 | effet rapide (terrain) — Phase Principale adverse : hors pilote |
| Predaplant Dragostapelia | 1 | effet rapide (terrain) — Cible un monstre adverse : hors pilote |
| Predaplant Dragostapelia | 2 | effet continu (terrain) — Annule les effets activés des monstres adverses à Compteur Prédateur : hors pilote |
| Rindbrumm the Striking Dragon | 2 | effet rapide (Cimetière) — Tour adverse seulement |
| The Golden Swordsoul | 1 | effet déclenché (main) — Déclaration d'attaque : pas de Phase de Combat au tour 1, hors du pilote |
| Tri-Brigade Mercourier | 1 | effet rapide (main, terrain) — Répond à un effet de monstre adverse : hors du pilote |
