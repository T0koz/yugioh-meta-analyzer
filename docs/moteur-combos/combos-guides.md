# Combos des guides publics, deck Branded (lot C3, J2, TOK-119)

> **18/11/2026**, agent du lot C3 (Opus). Relevé factuel : cartes et ordre des actions, source et date. **Aucun texte
> des guides n'est recopié** (dépôt public) ; chaque étape est une paraphrase en une ligne. Les mêmes données, sous
> forme exécutable (main, cible, jalons), sont dans `moteur_combos/guides.py`.

## 1. Sources consultées

Recherche web du 18/11 (« Branded combo », noms de cartes du pilote, 2026). Les combos détaillés et lisibles en texte
sont des **pages communautaires de masterduelmeta.com** (Master Duel : même texte de cartes que le TCG, mais un autre
ensemble de cartes ; les guides utilisent donc des cartes absentes de notre liste).

| Page | Auteur | Date | Lisible ? | Retenue |
|---|---|---|---|---|
| [Nadir Servant 1 Card Combo](https://www.masterduelmeta.com/combo/6a5d272ce5036dbe654fdf31) | TwilightSalt | 19/07/2026 | oui (texte coupé en fin de page) | G1, G5 |
| [Fallen of the White Dragon (One Card Combo)](https://www.masterduelmeta.com/combo/6a21b7fbd4f6ca4f21e03920) | rickytau | 04/06/2026 | oui | G2 |
| [Fallen of the White Dragon (One Card Combo)](https://www.masterduelmeta.com/combo/6a311f8ee8dd21fae6043715) | nerfmepls | 16/06/2026 | oui | G2 (même séquence) |
| [Fallen Of White Dragon](https://www.masterduelmeta.com/combo/6a91053ec87cb24c69a2b7b7) | Mordred | 28/08/2026 | oui (étape 6 mal étiquetée) | G3 |
| [Nadir Servant](https://www.masterduelmeta.com/combo/6a91128eb14e41d19f2eeca5) | Mordred | 28/08/2026 | en partie | G1 (même ligne) |
| [Suspect Fuwa With Fallen Of White Dragon](https://www.masterduelmeta.com/combo/6a9111ec57082c8c7e7b8a90) | Mordred | 28/08/2026 | oui | G4 |
| [Cartesia + discard + Darklord](https://www.masterduelmeta.com/combo/6a78792044a89469595dc8ce) | OUSSAMA | 09/08/2026 | oui | non : deck Darklord, hors pilote |
| Tableurs « Branded » ([1](https://www.masterduelmeta.com/spreadsheet/6a0f865953596fd3c08d10ff), [2](https://www.masterduelmeta.com/spreadsheet/6a330c969c34892f16f76059)) | kanna ogata, flygon727, FuSiioN, combatant | mai-juin 2026 | **non** : mains et séquences en images | non |

**Ce qui manque** : aucun guide TCG daté de l'automne 2026 en texte (les guides vidéo cités par une page YGOPRODeck ne
sont pas lisibles ici) ; les lignes classiques à partir d'`Aluber` et de `Branded Fusion` ne sont dans les tableurs
qu'en images. Ces lignes sont proposées au § 4 **à faire confirmer par un joueur**, pas comptées.

## 2. Cartes absentes de la liste du pilote

La liste du pilote est la liste de tournoi du 08/11/2026 (décision D1). Les guides passent, après une partie commune,
par : `Albion the Branded Dragon`, `Branded Retribution`, `Branded in Red`, `Khaos Starsource Dragon`. Chaque combo est
donc mesuré **jusqu'à la dernière étape réalisable avec la liste** ; la suite est classée « manqué : carte absente de
la liste », pas comme un échec du moteur. Aucun guide relevé ne passe par `Lubellion the Searing Dragon`.

**Substitution déclarée** : quand le guide paie un coût avec `Albion the Branded Dragon` (« un monstre de l'Extra Deck
qui mentionne Fallen of Albaz », coût de `Fallen of the White Dragon` et de `The Fallen & The Virtuous`), le moteur
choisit librement parmi les monstres de notre Extra Deck qui remplissent la même clause.

## 3. Les cinq combos relevés

Main de départ : la carte de départ **seule** (combos « à une carte ») ; les 4 autres cartes de la main sont des
cartes de réponse retirées du jeu. Les étapes marquées ✗ passent par une carte absente.

### G1 — Nadir Servant seule, branche « sans Droll » (TwilightSalt 19/07, Mordred 28/08)
1. Nadir Servant : envoie Titaniklad, ajoute Fallen of the White Dragon.
2. White, effet 1 : envoie The Dragon that Devours the Dogma, s'Invoque.
3. White, effet 2 : Dogmatika Ecclesia du Deck ; elle ajoute The Fallen & The Virtuous (posée chez le guide).
4. Phase de Fin : Titaniklad Invoque Guiding Quem du Deck ; Quem envoie Blazing Cartesia au Cimetière.
5. Dogma (Phase de Fin) ajoute The Fallen & The Virtuous ; celle-ci, coût un monstre de l'Extra Deck (guide : Albion
   the Branded Dragon), détruit Dogmatika Ecclesia ; Quem, effet 2, Invoque Cartesia du Cimetière.
6. ✗ Albion the Branded Dragon pose Branded Retribution ; ✗ suite en Khaos Starsource Dragon.

Cible : White, Quem, Cartesia sur le terrain ; Titaniklad et Dogma au Cimetière.

### G2 — White seule, vers Ecclesia and the Dark Dragon et Granguignol (rickytau 04/06, nerfmepls 16/06)
1. White, effet 1 (coût : guide Albion the Branded Dragon), s'Invoque ; effet 2 : Incredible Ecclesia du Deck.
2. Incredible Ecclesia se Sacrifie : The Golden Swordsoul du Deck.
3. Synchro : White + Golden Swordsoul → Ecclesia and the Dark Dragon.
4. EDD se bannit : Cartesia du Deck ; Golden Swordsoul (un monstre banni) ramène Incredible Ecclesia du Cimetière.
5. Cartesia fusionne Granguignol (Cartesia + Incredible Ecclesia) ; Granguignol envoie Titaniklad au Cimetière.
6. Phase de Fin : Cartesia et Incredible Ecclesia reviennent en main, EDD revient.
7. ✗ Albion the Branded Dragon, Branded Opening, Branded in Red…

Cible : Granguignol et EDD sur le terrain ; Cartesia et Incredible Ecclesia en main ; Titaniklad au Cimetière.

### G3 — White seule, par Quem et The Three Champions of Swordsoul (Mordred 28/08)
1. White, effet 1 (coût : guide Albion the Branded Dragon), s'Invoque ; effet 2 : Incredible Ecclesia du Deck.
2. Synchro : White + Incredible Ecclesia → EDD ; EDD se bannit : Quem du Deck.
3. Quem envoie Tri-Brigade Springans Kitt ; White revient du Cimetière (page : étiquette ambiguë).
4. Synchro : White + Quem → The Three Champions of Swordsoul ; elle ajoute Cartesia.
5. Cartesia s'Invoque de la main, puis fusionne Granguignol (Cartesia + Three Champions).
6. ✗ suite (branches Droll / sans Droll) par Albion the Branded Dragon.

Cible : Granguignol sur le terrain ; Three Champions, White et Quem au Cimetière.

### G4 — White seule, ligne « Fuwalos suspect » (Mordred 28/08)
1. White, effet 1 : envoie Dogma, s'Invoque ; effet 2 : Dogmatika Ecclesia du Deck ; elle ajoute Guiding Quem.
2. Invocation Normale de Quem ; Quem envoie Cartesia au Cimetière.
3. Phase de Fin : Dogma ajoute The Fallen & The Virtuous ; celle-ci (coût : guide Albion the Branded Dragon) vise
   Dogmatika Ecclesia ; Quem, effet 2, Invoque Cartesia du Cimetière.
4. ✗ Albion the Branded Dragon pose The Fallen & The Virtuous.

Cible : White, Quem, Cartesia sur le terrain ; Dogma au Cimetière.

### G5 — Nadir Servant seule, branche « sous Droll » (TwilightSalt 19/07)
1. Nadir Servant : envoie Titaniklad, ajoute White.
2. White, effet 1 (coût : guide Albion the Branded Dragon), s'Invoque ; effet 2 : Incredible Ecclesia du Deck.
3. Phase de Fin : Titaniklad Invoque Quem du Deck. ✗ La page s'arrête là (plateau annoncé sans séquence).

Cible : White, Incredible Ecclesia et Quem sur le terrain ; Titaniklad au Cimetière.

## 4. Lignes à faire confirmer par un joueur (non comptées)

Lignes connues du deck, mais dont aucune séquence n'est lisible dans les sources du jour. Ne pas les compter avant
qu'un joueur les ait écrites (cartes, ordre, plateau visé), source et date à l'appui :
- `Aluber the Jester of Despia` seul (Invocation Normale, recherche de `Branded Fusion`, Fusion depuis le Deck) ;
- `Branded Fusion` seule ;
- `Aluber` + une carte « Branded in High Spirits » (tableur de combatant, 17/06, en image) ;
- `Incredible Ecclesia` + `Blazing Cartesia` (tableur de kanna ogata, 31/05, en image).

## 5. Lot J2 plein, 18/11 (TOK-139, jalon n°5)

> **18/11/2026**, session du jalon n°5 (Opus). Transcription faite **avant toute lecture du code du moteur**
> (`moteur_combos/`, `scripts/combos_*.py`) : seules ont été lues cette page (§ 1 à 4), la liste du pilote
> (`deck-branded-source.json`) et les sources ci-dessous. Même règle qu'au lot C3 : aucune phrase des guides ni aucun
> texte de carte recopié, une paraphrase par étape ; étapes ✗ = carte absente de la liste du pilote. Cette section est
> **figée** par le commit `docs(TOK-139)` (empreinte sha256 dans le message) ; toute correction ultérieure se fait par un
> nouveau commit expliqué, signalé au compte rendu.

### 5.1 Sources consultées (recherche web du 18/11)

| Page | Auteur | Date | Lisible ? | Retenue |
|---|---|---|---|---|
| [Branded Fusion](https://www.masterduelmeta.com/combo/6a2585f47c53112dc8c296ff) | Master Game | 07/06/2026 | oui | G6 |
| [Aluber + BIHS-type (modified from FuSiioN)](https://www.masterduelmeta.com/combo/6a330ada9026d5cfa564d08e) | combatant | 17/06/2026 | oui (coûts non écrits) | G7 |
| [Aluber + High Spirits Send Full Combo](https://www.masterduelmeta.com/combo/6a3a064927d579237da6ca51) | SirRichard Alt | 23/06/2026 | oui | G7 : seulement la carte révélée (Mulcharmy Fuwalos) et l'envoi de Rindbrumm |
| [[IN PROGRESS] Aluber + Fallen of Albaz/Fallen of the White Dragon](https://www.masterduelmeta.com/combo/6a2e53bbc1791e881a6e4489) | mikethaguy | 14/06/2026 | oui (numérotation répétée après l'étape 9) | G8 (branche sans Bystial) |
| [gold sarc (no golden swordsoul)](https://www.masterduelmeta.com/combo/6a0d96f302b04933a7d3effb) | kanna ogata | 20/05/2026 | oui | G9 |
| [branded combo](https://www.masterduelmeta.com/combo/6a244c9d24e0dc6684a2ab22) | critboi (alt) | 06/06/2026 | oui (page coupée après l'étape 17) | G10 |
| [Quem Bystial Route](https://www.masterduelmeta.com/combo/6a6a417c1a29123450329184) | Koraxtu | 29/07/2026 | oui | non : main avec un `Bystial`, absent de la liste |
| [Branded Opening + discard (or) Aluber… (or) Branded Fusion](https://www.masterduelmeta.com/combo/6a0bef878b2d717cfdac0963) | flygon727 | 19/05/2026 | oui | non : `Branded Fusion` y fait `Albion the Branded Dragon`, absent dès l'étape 2 |
| [Aluber + Cartesia + Shrouded](https://www.masterduelmeta.com/combo/6a25e73a0e155c831ca7783a) (et [variante](https://www.masterduelmeta.com/combo/6a269e27112c28c6d52c24c4)) | Luscens, Cyan | 07-08/06/2026 | oui | non : main avec `Albion the Shrouded Dragon`, absent |
| [White Albaz + Cart + Discard](https://www.masterduelmeta.com/combo/6a2335f5a0b3f2bf953a49a2) | Master Game | 05/06/2026 | en partie (étape 6 incohérente) | non : matériaux de Fusion illisibles |
| [White Albaz + Cartesia + 1card](https://www.masterduelmeta.com/combo/6a9e33561853502f81b3e14a) | のQuỷ Đá | 07/09/2026 | en partie (étape 4 confuse) | non : étapes 3-4 illisibles |
| [Aluber + Bihs Target](https://www.masterduelmeta.com/combo/6a91294b5c0b478846f8bb7d) | Mordred | 28/08/2026 | en partie (branches par Type, page tronquée) | non : séquence non suivie jusqu'au bout |

**Choix** : cinq départs différents des cinq du lot C3 (G1-G5 partaient de `Nadir Servant` ou de `Fallen of the White
Dragon` seuls) : `Branded Fusion` seule, `Aluber` + une cible de `Branded in High Spirits`, `Aluber` + `Fallen of
Albaz`, `Gold Sarcophagus` seule, `Aluber` + `Fallen of the White Dragon`. G6 est la première ligne relevée qui passe
par `Cocatorium the Heavy Metal Avian` et `Tri-Brigade Mercourier` ; G7 la première qui finit sur `Mirrorjade`.

### 5.2 Règles de lecture, fixées avant exécution

- **Main de départ** : les cartes nommées seules ; les autres cartes de la main sont retirées du jeu (règle du lot C3).
- **Substitutions déclarées** (en plus de celle du § 2, coûts de `Fallen of the White Dragon` et de `The Fallen & The
  Virtuous`) : quand le guide envoie `Albion the Branded Dragon` par `Branded in High Spirits`, le moteur choisit
  librement parmi les monstres de notre Extra Deck qui remplissent la même condition. Quand le guide cherche ou envoie
  une carte absente (`Branded in Red`, `Branded Sword`, `Lubellion the Searing Dragon`), le moteur choisit librement
  une carte de la liste qui remplit la condition ; ce choix n'est **jamais** un jalon.
- **Jalons** : les actions clés ci-dessous, dans cet ordre, à retrouver en **sous-suite** de la séquence du moteur
  (d'autres actions peuvent s'intercaler). Un jalon nomme le type d'action et la carte, rien d'autre (ni coût ni cible,
  sauf mention). Les étapes ✗ ne sont pas des jalons.
- **Cible** : le plateau décrit, évalué à la fin du tour (Phase de Fin résolue) ; « au moins » ces cartes à ces endroits.
- **Exemplaires** : la liste n'a qu'un `Guiding Quem` et qu'un `Tri-Brigade Mercourier` ; une étape qui en demanderait
  un deuxième est classée ✗ (« un seul exemplaire dans la liste »), pas comme un échec du moteur.

### G6 — Branded Fusion seule (Master Game 07/06)
1. Branded Fusion : envoie Cocatorium the Heavy Metal Avian et Fallen of Albaz du Deck, Fusion de Rindbrumm.
2. Cocatorium, effet au Cimetière : Sacrifie Rindbrumm, revient sur le terrain.
3. Cocatorium, effet : bannit Tri-Brigade Mercourier du Deck.
4. Mercourier (banni) : ajoute Fallen of the White Dragon.
5. White, effet 1 : envoie Titaniklad the Ash Dragon, s'Invoque ; effet 2 : Dogmatika Ecclesia du Deck ; elle ajoute
   The Fallen & The Virtuous.
6. Phase de Fin : Titaniklad Invoque Guiding Quem du Deck ; Quem envoie Blazing Cartesia au Cimetière.
7. The Fallen & The Virtuous (coût : guide Albion the Branded Dragon, substitution) vise et détruit Cocatorium ;
   Quem, effet 2, Invoque Cartesia du Cimetière.
8. ✗ Albion the Branded Dragon pose The Fallen & The Virtuous.

Jalons : (1) activation de Branded Fusion ; (2) Invocation Fusion de Rindbrumm ; (3) Invocation Spéciale de Cocatorium
depuis le Cimetière ; (4) effet de Mercourier banni ; (5) Invocation Spéciale de White depuis la main ; (6) Invocation
Spéciale de Dogmatika Ecclesia ; (7) Invocation Spéciale de Quem par Titaniklad ; (8) activation de The Fallen & The
Virtuous ; (9) Invocation Spéciale de Cartesia depuis le Cimetière.

Cible : White, Dogmatika Ecclesia, Quem et Cartesia sur le terrain ; Rindbrumm, Titaniklad et Cocatorium au Cimetière ;
Mercourier banni.

### G7 — Aluber + Mulcharmy Fuwalos, vers Mirrorjade (combatant 17/06 ; carte révélée : SirRichard Alt 23/06)
1. Invocation Normale d'Aluber ; Aluber ajoute Branded in High Spirits.
2. Branded in High Spirits : Mulcharmy Fuwalos (main) et Rindbrumm (Extra Deck) au Cimetière, ajoute Fallen of the
   White Dragon.
3. White, effet 1, s'Invoque ; effet 2 : Incredible Ecclesia du Deck.
4. Incredible Ecclesia se Sacrifie : The Golden Swordsoul du Deck.
5. Synchro : White + Golden Swordsoul → Ecclesia and the Dark Dragon.
6. EDD se bannit : Guiding Quem du Deck ; en chaîne, effet de Golden Swordsoul ; Quem envoie Tri-Brigade Springans
   Kitt ; effet de Kitt (le guide ne dit pas lequel ; le plateau final suppose White de retour sur le terrain).
7. Synchro : Incredible Ecclesia + Aluber → The Three Champions of Swordsoul ; son effet (guide : « chaîne 1 »).
8. Effet de Blazing Cartesia : Fusion de Mirrorjade the Iceblade Dragon (White + Three Champions).
9. ✗ PSY-Framelord Omega (facultatif, absent) ; ✗ Albion the Branded Dragon pose une carte.
10. Phase de Fin : Incredible Ecclesia revient en main ; EDD revient.

Jalons : (1) Invocation Normale d'Aluber ; (2) activation de Branded in High Spirits ; (3) Invocation Spéciale de White
depuis la main ; (4) Invocation Spéciale d'Incredible Ecclesia ; (5) Invocation Spéciale de The Golden Swordsoul ;
(6) Invocation Synchro d'Ecclesia and the Dark Dragon ; (7) Invocation Spéciale de Quem ; (8) Invocation Synchro de
The Three Champions of Swordsoul ; (9) Invocation Fusion de Mirrorjade.

Cible : Mirrorjade, Ecclesia and the Dark Dragon, Quem et Cartesia sur le terrain ; Rindbrumm et Three Champions au
Cimetière.

### G8 — Aluber + Fallen of Albaz, branche sans Bystial (mikethaguy 14/06)
1. Invocation Normale d'Aluber ; Aluber ajoute Branded in High Spirits.
2. Branded in High Spirits : révèle Fallen of Albaz, envoie (guide : Albion the Branded Dragon, substitution) un
   monstre de l'Extra Deck, défausse Albaz, ajoute Fallen of the White Dragon.
3. White, effet 1 : envoie The Dragon that Devours the Dogma, s'Invoque ; effet 2 : Incredible Ecclesia du Deck.
4. Synchro : Incredible Ecclesia + Aluber → Ecclesia and the Dark Dragon.
5. EDD se bannit : Blazing Cartesia du Deck.
6. Cartesia, effet : Fusion de Granguignol the Dusk Dragon (Cartesia + White) ; Granguignol envoie Titaniklad au
   Cimetière.
7. (Branche sans Bystial : rien d'autre en Phase Principale.)
8. Phase de Fin : Cartesia et Incredible Ecclesia reviennent en main ; Titaniklad Invoque Quem du Deck ; Quem envoie
   Tri-Brigade Mercourier (ou Cartesia) au Cimetière ; ✗ Albion the Branded Dragon pose une carte ; Dogma ajoute The
   Fallen & The Virtuous ; celle-ci, coût Rindbrumm, vise et détruit Granguignol ; Quem, effet 2, Invoque Mercourier
   (ou Cartesia) du Cimetière.

Jalons : (1) Invocation Normale d'Aluber ; (2) activation de Branded in High Spirits ; (3) Invocation Spéciale de White
depuis la main ; (4) Invocation Spéciale d'Incredible Ecclesia ; (5) Invocation Synchro d'Ecclesia and the Dark Dragon ;
(6) Invocation Spéciale de Cartesia depuis le Deck ; (7) Invocation Fusion de Granguignol ; (8) Invocation Spéciale de
Quem par Titaniklad ; (9) activation de The Fallen & The Virtuous ; (10) Invocation Spéciale par Quem depuis le
Cimetière.

Cible : Ecclesia and the Dark Dragon et Quem sur le terrain, plus Mercourier ou Cartesia ; Granguignol, Titaniklad,
Dogma, Rindbrumm et Fallen of Albaz au Cimetière ; Incredible Ecclesia en main.

### G9 — Gold Sarcophagus seule (kanna ogata 20/05)
1. Gold Sarcophagus : bannit Tri-Brigade Mercourier du Deck.
2. Mercourier (banni) : ajoute Fallen of the White Dragon.
3. White, effet 1, s'Invoque (coût non écrit par le guide : libre) ; effet 2 : Incredible Ecclesia du Deck.
4. Synchro : White + Incredible Ecclesia → Ecclesia and the Dark Dragon.
5. EDD se bannit : Guiding Quem du Deck.
6. Quem envoie (guide : ✗ Branded Sword) une carte au Cimetière ; ✗ Branded Sword rend Mercourier.
7. Phase de Fin : Incredible Ecclesia revient en main ; ✗ Albion the Branded Dragon (trois branches, toutes par une
   carte posée ou ajoutée par Albion) ; EDD revient.

Jalons : (1) activation de Gold Sarcophagus ; (2) effet de Mercourier banni ; (3) Invocation Spéciale de White depuis
la main ; (4) Invocation Spéciale d'Incredible Ecclesia ; (5) Invocation Synchro d'Ecclesia and the Dark Dragon ;
(6) Invocation Spéciale de Quem.

Cible : Ecclesia and the Dark Dragon et Quem sur le terrain ; Incredible Ecclesia en main ; Mercourier banni.

### G10 — Aluber + Fallen of the White Dragon, par Three Champions et Granguignol (critboi 06/06)
1. White, effet 1 : envoie Titaniklad, s'Invoque ; effet 2 : Incredible Ecclesia du Deck.
2. Synchro : White + Incredible Ecclesia → Ecclesia and the Dark Dragon.
3. EDD se bannit : Guiding Quem du Deck ; Quem envoie Tri-Brigade Springans Kitt.
4. Kitt, effet au Cimetière : Invoque White du Cimetière.
5. Synchro : Quem + White → The Three Champions of Swordsoul ; elle ajoute Blazing Cartesia.
6. Cartesia s'Invoque de la main.
7. Invocation Normale d'Aluber ; Aluber ajoute (guide : ✗ Branded in Red) une carte « Branded ».
8. Cartesia, effet : Fusion de Granguignol (Cartesia + Aluber) ; Granguignol envoie (guide : ✗ Lubellion) un monstre
   au Cimetière.
9. ✗ Branded in Red, Albion the Branded Dragon, Lubellion, Etude of the Branded (étapes 13 à 16).
10. Phase de Fin : EDD revient ; ✗ Titaniklad Invoque Quem du Deck (un seul Quem dans la liste, déjà au Cimetière).

Jalons : (1) Invocation Spéciale de White depuis la main ; (2) Invocation Spéciale d'Incredible Ecclesia ;
(3) Invocation Synchro d'Ecclesia and the Dark Dragon ; (4) Invocation Spéciale de Quem ; (5) Invocation Spéciale de
White depuis le Cimetière ; (6) Invocation Synchro de The Three Champions of Swordsoul ; (7) Invocation Spéciale de
Cartesia depuis la main ; (8) Invocation Normale d'Aluber ; (9) Invocation Fusion de Granguignol.

Cible : The Three Champions of Swordsoul, Granguignol et Ecclesia and the Dark Dragon sur le terrain ; Titaniklad,
Quem, White, Cartesia et Aluber au Cimetière.
<!-- fin du lot J2 plein -->
