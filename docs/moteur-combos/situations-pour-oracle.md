# Situations à faire jouer à l'oracle (lot C2, J1, TOK-118)

> **Pour qui** : la session séparée qui pilote l'oracle Project Ignis (TOK-86), lancée par l'orchestrateur. La
> session qui a formalisé les cartes ne lit jamais l'oracle (principe d'indépendance) : elle écrit ici ce qu'il faut
> lui demander, et lira seulement la réponse (ajoutée à `reponses-oracle.md`).
> **Écrit le 18/11/2026** par l'agent du lot C2. Verdicts attendus = **lecture de l'agent**, pas d'un juge.

## 1. Pourquoi ces situations

Le jeu de tests `tests-branded.yaml` (rejoué par l'oracle le 18/11) n'exerce que **30 des 57 effets du pilote**
(effets dont la résolution est écrite). Les 27 autres ne sont exercés que par les 30 situations de
[`situations-j1.yaml`](situations-j1.yaml), que l'agent a écrites lui-même : elles prouvent que le code fait ce que
l'agent a lu, pas que la lecture est juste. **Les faire rejouer par l'oracle donne un verdict indépendant sur les
57 effets** (méthode validée par l'agent `data-scientist-ygo`, voir [`j1-rapport.md`](j1-rapport.md) § 4).

Règle de lecture des réponses :
- **même verdict et même liste** que le YAML J1 → accord ;
- **désaccord** → litige, tranché par le **texte TCG de notre base** (précédent R23 / T37 : l'oracle lit le texte OCG
  de BabelCDB). Un litige non tranché compte comme une erreur dans le taux « pessimiste » ;
- l'oracle ne sait pas répondre (situation impossible à mettre en scène) → « non testable », noté tel quel.

## 2. Points de règle que le texte ne tranche pas (N01 à N13)

Choix faits par la formalisation, marqués ⚖ dans `moteur_combos/cartes_j1.py`. Ce sont les questions prioritaires.

| N° | Question | Choix codé | Situation |
|---|---|---|---|
| N01 | `Despian Luluwalilith` se déclenche-t-elle sur **sa propre** sortie de l'Extra Deck (son Invocation Synchro) ? | Non tranché : le moteur répond **« non couvert »** | J30 |
| N02 | `Branded Opening` est-elle activable s'il n'y a **aucun monstre « Despia » dans le Deck** (la défausse, elle, est possible) ? Même question pour `Dogmatika Ecclesia` (effet de recherche) sans carte « Dogmatika » à ajouter, à cause de la partie « also … ». | Non activable (R01 appliqué aux deux parties) | à créer : T35 sans `Aluber` ni `Quem` dans le Deck |
| N03 | `Sprind` peut-il se déplacer **depuis la Zone Monstre Extra** vers une zone principale ? La destruction « dans sa colonne » touche-t-elle la Zone Monstre Extra de cette colonne (colonnes 2 et 4) ? | Oui aux deux | J20 (colonne), à créer : `Sprind` en Zone Monstre Extra |
| N04 | Peut-on **déclarer DIVIN** (`Hyperinvoked Aeon`, `Mixousia`) ? Peut-on déclarer l'Attribut que le monstre a déjà ? | DIVIN : « indéterminé » (liste peut-être incomplète) ; Attribut actuel : permis | J17, J18, J19 |
| N05 | `Ecclesia and the Dark Dragon` revient à la Phase de Fin : dans **quelle zone** (principale seulement ?) et **quelle position** ? | Zone principale, position qu'elle avait | J03 |
| N06 | `Cocatorium` (« banish it when it leaves the field ») utilisée comme **matériel de Fusion** : bannie au lieu d'aller au Cimetière ? | Oui | J10 |
| N07 | Un effet de monstre se résout-il si le monstre a été **détruit en réponse** (`Ghost Ogre` sur `Guiding Quem`, 1er effet) ? | Oui, l'effet se résout | J11 |
| N08 | Peut-on **cibler** avec `The Fallen & The Virtuous` un monstre insensible (`Dogma` avec un « Ecclesia » au Cimetière) ? | Oui ; la destruction ne s'applique pas | J24 |
| N09 | Un effet **sans cible** qui « choisit » à la résolution (`Mirrorjade`, `Luluwalilith`, `Aeon`) peut-il choisir un monstre insensible (`Titaniklad` après son Invocation Fusion, `Dogma`) ? | Non : le monstre insensible n'est pas proposé | J26 |
| N10 | L'effet de remplacement de `Branded Opening` (Cimetière) vaut-il contre une destruction par **sa propre** carte (`The Fallen & The Virtuous`) ? | Oui (« by card effect », sans « opponent's ») | J29 |
| N11 | `Mulcharmy Fuwalos` : « only 1 other "Mulcharmy" monster effect » ; une 2ᵉ copie de `Fuwalos` est-elle cet « autre » effet ? | Au plus 2 effets « Mulcharmy » par tour | à créer : 3 `Fuwalos` en main |
| N12 | `Albion` (Cimetière) : « the 2 in the center Main Monster Zones » = la zone centrale **de chaque joueur** ? | Oui ; demande des monstres adverses → hors pilote | à créer (hors pilote) |
| N13 | `The Golden Swordsoul` se bannissant elle-même en coût : se déclenche-t-elle sur son propre bannissement ? | Non (elle n'est plus sur le terrain ni au Cimetière) | T62 (variante) |

Choix plus structurants, à faire confirmer en même temps :
- **R22 codé** (déclencheurs simultanés) : le joueur met les effets en chaîne un par un, dans l'ordre qu'il choisit ;
  les obligatoires doivent tous y être, les facultatifs peuvent être laissés. C'est le réglage par défaut de l'oracle,
  pas `DUEL_TCG_SEGOC_FIRSTTRIGGER` (T45, T62).
- **Insensibilité** (`Dogma`, `Titaniklad`) : le moteur ne l'applique qu'aux cartes sur le terrain.

## 3. Les 30 situations J1

Départs, actions et listes : [`situations-j1.yaml`](situations-j1.yaml) (mêmes conventions que `tests-branded.yaml`).
Résumé (« effet » = effet exercé, numéroté dans l'ordre du texte) :

| Id | Effet exercé | Action | Attendu (lecture de l'agent) |
|---|---|---|---|
| J01 | `Rindbrumm` 1 | Effet rapide d'`EDD`, `Rindbrumm` l'annule | légal ; `EDD` reste, rien n'est Invoqué |
| J02 | `EDD` 1 | `EDD` se bannit, Invoque un monstre du Deck | légal ; 9 choix (`Albaz`, `White`, 7 monstres de Niveau 4 qui mentionnent Albaz) |
| J03 | `EDD` 1 | J02 puis Phase de Fin | légal ; `EDD` revient en zone principale (N05) |
| J04 | `EDD` 2 | Mélanger `Titaniklad` (Cimetière), `Aluber` (terrain) et `EDD` | légal |
| J05 | `Cartesia` 3 | Phase de Fin, un Fusion envoyé ce tour | légal |
| J06 | `Branded in High Spirits` 2 | idem | légal |
| J07 | `Incredible Ecclesia` 3 | Effet obligatoire résolu, puis fin du tour | légal, fin de tour ensuite légale (R23) |
| J08 | `Incredible Ecclesia` 1 | Procédure, l'adversaire a 1 monstre (hors pilote) | légal, sans chaîne (R15) |
| J09 | `Cocatorium` 1 | Sacrifier `Springans Kitt` | légal ; « bannie si elle quitte le terrain » |
| J10 | `Cocatorium` 1 | J09 puis `Super Polymerization` : `Rindbrumm` avec `Albaz` + `Cocatorium` | légal ; `Cocatorium` bannie (N06) |
| J11 | `Ghost Ogre` 1 | `Ogre` détruit `Quem` en réponse à son effet | légal ; l'effet de `Quem` se résout (N07) |
| J12 | `TFTV` 1 | Détruire `Aluber` | légal |
| J13 | `TFTV` 2 | Invoquer `Aluber` depuis le Cimetière | légal ; cibles `Incredible Ecclesia`, `Aluber` |
| J14 | `Luluwalilith` 1 | `Nadir Servant` fait sortir `Titaniklad` de l'Extra Deck | légal ; +500 ATK |
| J15 | `Luluwalilith` 2 | Phase de Fin | légal ; 4 choix (`Cartesia`, `Quem`, `Incredible Ecclesia`, `Dogmatika Ecclesia`) |
| J16 | `Aeon` 1 | Fusion d'`Aeon` avec `Granguignol` + `Rindbrumm`, bannir `Granguignol` | légal |
| J17 | `Aeon` 2 | Déclarer LUMIÈRE | légal (N04) |
| J18 | `Mixousia` 1 | Cibler `Aluber`, déclarer EAU | légal (N04) |
| J19 | `Mixousia` 3 | Au Cimetière, déclarer LUMIÈRE | légal (N04) |
| J20 | `Sprind` 1 | M1 → M2, détruire `Rindbrumm` (Zone Monstre Extra, colonne 2) | légal (N03) |
| J21 | `Sprind` 2 | Phase de Fin, Invoquer `Tri-Brigade Springans Kitt` | légal ; 4 choix |
| J22 | `Dogma` 2 | Mélanger `Albaz` dans le Deck | légal |
| J23 | `Dogma` 3 | Phase de Fin | légal ; 5 choix |
| J24 | `Dogma` 1 | `TFTV` cible `Dogma` | légal ; `Dogma` reste, 3500 ATK (N08) |
| J25 | `Titaniklad` 1 | Fusion avec `Albaz` + `Granguignol` | légal ; 3700 ATK |
| J26 | `Titaniklad` 2 | `Mirrorjade` ne peut pas choisir `Titaniklad` | légal (N09) |
| J27 | `Three Champions` 1 | Invocation Synchro puis recherche | légal ; 4 choix |
| J28 | `Three Champions` 2 | Annuler puis détruire `Aluber` | légal |
| J29 | `Branded Opening` 2 | Remplacement de la destruction de `Rindbrumm` | légal (N10) |
| J30 | — | Invocation Synchro de `Luluwalilith` | **non couvert** (N01) |

## 4. Comment rendre la réponse

Ajouter à `reponses-oracle.md` une section « Lot C2 » : pour chaque Jxx et chaque Nxx, le verdict de l'oracle, la
liste qu'il propose, et la mention « accord / désaccord / non testable ». Les situations « à créer » de la colonne
N peuvent être mises en scène directement par le lanceur. Rien d'autre (pas de code, pas de script de carte).
