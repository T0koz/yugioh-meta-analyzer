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
