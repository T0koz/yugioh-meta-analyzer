# J1 — formalisation des 37 cartes du pilote Branded (lot C2, TOK-118)

> **18/11/2026**, agent du lot C2 (Opus), branche `claude/c2-j1-formalisation-a044b3`. Rien n'est poussé ni fusionné.
> Commandes : `python scripts/combos_harnais.py` (harnais, statuts dans `data/combos.db`),
> `python scripts/combos_echantillon_j1.py` (tirage de l'échantillon), `python -m pytest moteur_combos/tests`.

## 1. En bref

| Mesure | Valeur |
|---|---|
| Cartes du pilote (Main + Extra, distinctes) | 37, toutes au statut **`formalisee`** (0 `brouillon`, 0 `non_formalisable`, 0 `verifiee`) |
| Effets déclarés | 72 : **57 du pilote** (résolution écrite) + 15 **hors périmètre** (adversaire, combat, tour adverse) |
| Effets du pilote exercés par au moins un test | **57 sur 57** (30 par le jeu de tests rejoué par l'oracle, 27 seulement par les situations J1) |
| Situations du jeu de tests (`tests-branded.yaml`) exécutées et conformes | **69 sur 72** (T67 : exploration, lot C3 ; T71, T72 : hors pilote) — 10 avant ce lot |
| Situations J1 (`situations-j1.yaml`, écrites par l'agent) | **30 sur 30** conformes |
| Erreurs de formalisation trouvées par les tests | **0** (3 erreurs de script de scénario, corrigées) |
| Taux d'erreur J1 (échantillon indépendant) | **pas encore mesuré** : échantillon tiré (§ 4), relecture et oracle à venir |
| Tests pytest | 173 |

**J1 n'est pas déclaré atteint** : le critère « taux d'erreur chiffré sur un échantillon vérifié » demande une
vérification indépendante de l'auteur (avis de l'agent `data-scientist-ygo`, § 4). Ce qui est livré : toutes les
cartes formalisées et testées, la méthode écrite, l'échantillon tiré, la cible fixée **avant** la relecture.

## 2. Ce qui a été codé

**Moteur** (`moteur_combos/regles.py`, en plus de la tranche 0) : effets déclenchés **simultanés** (R22, ordre libre,
obligatoires d'abord, facultatifs laissables — demandé par le brief, déclaré), Invocation **Synchro**, Invocation
Spéciale **par procédure** (R15), coûts par **Sacrifice** et **bannissement**, défausse, destruction et effet de
remplacement, retour au Deck (mélangé, au-dessous), **cibles** à l'activation, **annulation** d'un maillon, chaîne
**sans réponse** (R19), Magie Jeu-Rapide posée ce tour (R18), caractéristiques modifiées (nom, Type, Attribut, Niveau,
ATK), effets annulés, insensibilité, verrous `extra_aucune` et `extra_fusion_synchro_n8`, pioche (branche de hasard),
**Phase de Fin** (passage, effets « During the End Phase », retours différés, fin de tour refusée si un effet
obligatoire attend, R23), Phase de Combat refusée au tour 1 (R31). Fusion : lignes de matériels décrites par groupe
(« 2 monsters with the same Type… », « 2+ Fusion Monsters… ») et caractéristique inconnue → « indéterminé ».

**Cartes** : `moteur_combos/cartes_j1.py` (32 cartes) ; `cartes.py` (tranche 0) complété : catégories d'effet (lues
par `Ash Blossom`) et résolution de l'effet 1 de `Rindbrumm` (annuler, renvoyer en main), qui passe de `brouillon` à
`formalisee`. Chaque formalisation est écrite contre l'empreinte `text_sha256` du texte TCG de la base.

**Statut `formalisee` durci** (décision par défaut, § 7) : il faut toutes les résolutions écrites **et** chaque effet
du pilote exercé par au moins un test exécuté (`regles.EXERCES`, compté par le harnais) ; sinon `brouillon`
(« écrite, non testée », sens d'origine de D6). Les 4 cartes sans effet du pilote (`Droll & Lock Bird`, `Fallen of
Albaz` — effet de Fusion avec des monstres adverses —, `Predaplant Dragostapelia`) sont `formalisee` au sens de la
décision C1 (effets hors périmètre écrits comme tels).

## 3. Statut par carte

| Carte | Zone | Statut | Effets (pilote / hors périmètre) | Exercés par le YAML | Exercés par J1 seulement |
|---|---|---|---|---|---|
| Albion the Sanctifire Dragon | extra | formalisee | 1 / 2 | 1 | — |
| Despian Luluwalilith | extra | formalisee | 2 / 0 | — | 1, 2 |
| Ecclesia and the Dark Dragon | extra | formalisee | 2 / 0 | — | 1, 2 |
| Garura, Wings of Resonant Life | extra | formalisee | 1 / 1 | 2 | — |
| Granguignol the Dusk Dragon | extra | formalisee | 1 / 1 | 1 | — |
| Hyperinvoked Aeon | extra | formalisee | 2 / 0 | — | 1, 2 |
| Mirrorjade the Iceblade Dragon | extra | formalisee | 1 / 1 | 1 | — |
| Mixousia the Confounder | extra | formalisee | 2 / 1 | — | 1, 3 |
| Predaplant Dragostapelia | extra | formalisee | 0 / 2 | — | — |
| Rindbrumm the Striking Dragon | extra | formalisee | 1 / 1 | — | 1 |
| Sprind the Irondash Dragon | extra | formalisee | 2 / 0 | — | 1, 2 |
| The Dragon that Devours the Dogma | extra | formalisee | 3 / 0 | — | 1, 2, 3 |
| The Three Champions of Swordsoul | extra | formalisee | 2 / 0 | — | 1, 2 |
| Titaniklad the Ash Dragon | extra | formalisee | 3 / 0 | 3 | 1, 2 |
| Aluber the Jester of Despia | main | formalisee | 1 / 1 | 1 | — |
| Ash Blossom & Joyous Spring | main | formalisee | 1 / 0 | 1 | — |
| Blazing Cartesia, the Virtuous | main | formalisee | 3 / 0 | 1, 2 | 3 |
| Branded Fusion | main | formalisee | 1 / 0 | 1 | — |
| Branded Opening | main | formalisee | 2 / 0 | 1 | 2 |
| Branded in High Spirits | main | formalisee | 2 / 0 | 1 | 2 |
| Cocatorium the Heavy Metal Avian | main | formalisee | 2 / 0 | 2 | 1 |
| Dogmatika Ecclesia, the Virtuous | main | formalisee | 2 / 1 | 2, 3 | — |
| Droll & Lock Bird | main | formalisee | 0 / 1 | — | — |
| Fallen of Albaz | main | formalisee | 0 / 1 | — | — |
| Fallen of the White Dragon | main | formalisee | 2 / 0 | 1, 2 | — |
| Ghost Ogre & Snow Rabbit | main | formalisee | 1 / 0 | — | 1 |
| Gold Sarcophagus | main | formalisee | 1 / 0 | 1 | — |
| Guiding Quem, the Virtuous | main | formalisee | 2 / 0 | 1, 2 | — |
| Incredible Ecclesia, the Virtuous | main | formalisee | 3 / 0 | 2 | 1, 3 |
| Mulcharmy Fuwalos | main | formalisee | 1 / 0 | 1 | — |
| Nadir Servant | main | formalisee | 1 / 0 | 1 | — |
| Springans Kitt | main | formalisee | 2 / 0 | 1, 2 | — |
| Super Polymerization | main | formalisee | 1 / 0 | 1 | — |
| The Fallen & The Virtuous | main | formalisee | 2 / 0 | — | 1, 2 |
| The Golden Swordsoul | main | formalisee | 1 / 1 | 2 | — |
| Tri-Brigade Mercourier | main | formalisee | 1 / 1 | 2 | — |
| Tri-Brigade Springans Kitt | main | formalisee | 2 / 0 | 1, 2 | — |

Effectifs : **37 `formalisee`**, 0 `brouillon`, 0 `non_formalisable`, 0 `verifiee`, 0 `non_traitee` (les 8 cartes du
Side Deck restent `non_traitee`, hors pilote).

## 4. Taux d'erreur : méthode (validée par `data-scientist-ygo`), constat d'aujourd'hui, échantillon

**Unité : l'effet**, verdict « toutes ses clauses correctement formalisées » (une situation ne montre qu'un chemin ;
la carte est trop grossière ; la situation mesurerait le jeu de tests).

**Constat d'aujourd'hui (pas le taux de J1)** : 0 erreur détectée sur les 30 effets exercés par 69 situations écrites
avant ce lot et rejouées par l'oracle. Échantillon **non tiré au hasard**, un seul chemin par effet, verdicts écrits
par un LLM (erreurs possiblement corrélées avec la formalisation, en partie cassées par l'oracle). Pour mémoire
seulement, Wilson 95 % sur 0/30 : [0 ; 11,4 %] — ses hypothèses (tirage au hasard, vérification de l'effet entier) ne
sont pas remplies, ce n'est pas une borne du vrai taux. Les 30 situations J1 passent aussi, mais l'agent en a écrit les
verdicts : elles détectent une erreur de code, pas de lecture.

**Mesure de J1, en deux volets, non additionnés** :
1. **Oracle, recensement complet** : rejouer les 30 situations J1 et les points N01 à N13
   ([`situations-pour-oracle.md`](situations-pour-oracle.md)). Indicateur secondaire : « effets dont un chemin au
   moins contredit l'oracle ».
2. **Relecture humaine, chiffre de tête** : 20 effets tirés au hasard, **stratifiés 10 / 10** entre la strate a
   (exercés par le YAML, 30 effets) et la strate b (exercés seulement par J1, 27 effets, la plus risquée), graine
   **20260118**, tirage simple sans remise sur les listes triées (`moteur_combos/echantillon.py`, reproductible). Le
   relecteur lit la formalisation clause par clause contre le texte TCG, **à l'aveugle** (sans le verdict de
   l'oracle), et note la gravité (bloquante : verdict faux ; mineure : bon verdict pour une mauvaise raison).
   Estimation ponctuelle pondérée par strate (30/57, 27/57) ; intervalle de Wilson 95 % sur l'échantillon poolé (20
   effets, allocation quasi proportionnelle).
3. **Hors périmètre** : les 15 effets relus en exhaustif, à part (erreur possible : un effet utile en jeu solo rangé
   hors périmètre) ; taux de classement publié séparément.
4. **Combinaison** : tout désaccord (oracle ou humain) ouvre un litige tranché par le texte TCG ; deux chiffres
   publiés : taux **arbitré** et taux **pessimiste** (litige non tranché = erreur). Noter le nombre de cartes
   distinctes de l'échantillon (effets d'une même carte dépendants).

**Cible écrite avant le tirage (à valider, § 7)** : J1 atteint si la **borne haute de Wilson 95 % du taux arbitré
≤ 20 %**. Puissance : 0 erreur sur 20 → borne haute 16,1 % ; descendre sous 10 % avec 0 erreur demande ≈ 35 effets.

**Naïf de comparaison** : la lecture directe par un LLM sans moteur, mesurée sur les points de règle le 17/11 : 1
erreur sur 34 (Wilson 95 % : 0,5 à 14,9 %). Repère, pas un test : 1/34 contre 0/20 ne se départagent pas.

**Réserves** : un seul relecteur, joueur et non arbitre (fiabilité non mesurée) ; l'oracle casse la corrélation sur
les verdicts, pas sur le choix des chemins testés (une clause mal lue peut n'être jamais exercée) ; seule la relecture
clause par clause couvre ce risque.

### Échantillon tiré (graine 20260118) — à relire par le juge ou un joueur, pas par Thomas

Strate a (YAML + oracle) : 30 effets ; strate b (situations J1 seules) : 27 ; hors périmètre : 15. Graine 20260118, 10 par strate.

| # | Strate | Carte | Effet | Formalisation (paraphrase, `cartes*.py`) | Correct ? | Gravité | Note |
|---|---|---|---|---|---|---|---|
| 1 | a | Aluber the Jester of Despia | 1 | Invoqué Normalement ou Spécialement : ajouter 1 Magie/Piège « Branded » du Deck à la main. | [ ] oui [ ] non | | |
| 2 | a | Blazing Cartesia, the Virtuous | 2 | Phase Principale, effet rapide : Invocation Fusion d'un monstre Fusion de Niveau 8 ou plus, matériels de la main ou du terrain. Rien d'invocable (verrou, R14) : pas d'activation. | [ ] oui [ ] non | | |
| 3 | a | Branded Fusion | 1 | Invocation Fusion d'un monstre qui mentionne Albaz comme matériel, avec 2 monstres de la main, du Deck ou du terrain ; verrou « Extra Deck = Fusion » posé dès l'activation, pour tout le tour. | [ ] oui [ ] non | | |
| 4 | a | Dogmatika Ecclesia, the Virtuous | 2 | Un monstre Invoqué Spécialement depuis l'Extra Deck est sur le terrain (l'un ou l'autre côté) : s'Invoquer Spécialement depuis la main. Un monstre de l'Extra Deck revenu des bannies (retour d'Ecclesia and the Dark Dragon) ne compte pas. | [ ] oui [ ] non | | |
| 5 | a | Garura, Wings of Resonant Life | 2 | Envoyée au Cimetière (depuis l'Extra Deck aussi) : piocher 1 carte (branche de hasard). | [ ] oui [ ] non | | |
| 6 | a | Nadir Servant | 1 | Envoyer 1 monstre de l'Extra Deck au Cimetière, puis ajouter du Deck ou du Cimetière 1 monstre « Dogmatika » ou « Fallen of Albaz » d'ATK inférieure ou égale à l'ATK imprimée du monstre envoyé (R12) ; verrou « aucune Invocation Spéciale depuis l'Extra Deck » après résolution (R13). | [ ] oui [ ] non | | |
| 7 | a | Super Polymerization | 1 | Magie Jeu-Rapide. Coût : défausser 1 carte (R17) ; Invocation Fusion avec des monstres des deux terrains (pas la main). Personne ne peut répondre à l'activation (R19). | [ ] oui [ ] non | | |
| 8 | a | The Golden Swordsoul | 2 | Un monstre est banni face visible (bannir en coût compte, R27b) : se bannir du terrain ou du Cimetière ; Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du Cimetière dont l'ATK égale la DEF. ⚖ Son propre bannissement ne la déclenche pas (elle ne serait plus là). | [ ] oui [ ] non | | |
| 9 | a | Titaniklad the Ash Dragon | 3 | Phase de Fin, envoyé au Cimetière ce tour : ajouter ou Invoquer Spécialement 1 « Fallen of Albaz » ou 1 monstre « Dogmatika » du Deck (le verrou de Nadir ne vise que l'Extra Deck, R13). | [ ] oui [ ] non | | |
| 10 | a | Tri-Brigade Mercourier | 2 | Bannie (en coût aussi, R27b) : ajouter du Deck « Fallen of Albaz » ou 1 **monstre** qui le mentionne, sauf lui. | [ ] oui [ ] non | | |
| 11 | b | Branded Opening | 2 | Effet de remplacement, ne s'active pas : un monstre Fusion du joueur serait détruit par un effet → bannir cette carte du Cimetière à la place (codé dans `Partie.detruire`). | [ ] oui [ ] non | | |
| 12 | b | Branded in High Spirits | 2 | Phase de Fin, si un monstre Fusion a été envoyé au Cimetière ce tour : revenir en main. Un seul effet de la carte par tour (T46). | [ ] oui [ ] non | | |
| 13 | b | Despian Luluwalilith | 1 | Une carte quitte l'Extra Deck : les monstres contrôlés gagnent 500 ATK (permanent), puis on peut annuler les effets d'1 carte face visible jusqu'à la fin du tour. ⚖ Sa propre sortie de l'Extra Deck : non couvert. | [ ] oui [ ] non | | |
| 14 | b | Despian Luluwalilith | 2 | Phase de Fin, envoyée au Cimetière ce tour : Invoquer Spécialement 1 monstre LUMIÈRE Magicien de la main ou du Deck dont l'ATK égale la DEF. | [ ] oui [ ] non | | |
| 15 | b | Ghost Ogre & Snow Rabbit | 1 | En réponse à l'effet d'un monstre sur le terrain (ou d'une Magie/Piège déjà face visible : aucune dans le deck) : s'envoyer au Cimetière ; détruire cette carte. Contre ses propres cartes aussi. | [ ] oui [ ] non | | |
| 16 | b | Hyperinvoked Aeon | 1 | Invoquée par Fusion : bannir des cartes du terrain et/ou des Cimetières, jusqu'au nombre de matériels ; avec 3 matériels ou plus, regarder l'Extra Deck adverse : hors pilote. | [ ] oui [ ] non | | |
| 17 | b | The Three Champions of Swordsoul | 1 | Invoquée par Synchro : ajouter du Deck ou du Cimetière 1 Magicien de Niveau 4 ou 8 dont l'ATK égale la DEF. Limite sur le nom cité par la clause (« The Three Brave Swordsouls »). | [ ] oui [ ] non | | |
| 18 | b | The Three Champions of Swordsoul | 2 | Cibler 1 carte face visible ; annuler ses effets, puis, avec un monstre « Ecclesia » ou « Fallen of Albaz » au Cimetière, on peut la détruire. | [ ] oui [ ] non | | |
| 19 | b | Titaniklad the Ash Dragon | 1 | Gagne 100 ATK par Niveau d'origine des matériels de son Invocation Fusion (codé : `bonus_atk`). | [ ] oui [ ] non | | |
| 20 | b | Titaniklad the Ash Dragon | 2 | Après son Invocation Fusion, pour le reste du tour : insensible aux effets activés des autres monstres Invoqués Spécialement depuis l'Extra Deck (codé : `insensible`). | [ ] oui [ ] non | | |

Hors périmètre (relecture exhaustive du classement) :

| Carte | Effet | Raison du classement | Bien classé ? |
|---|---|---|---|
| Albion the Sanctifire Dragon | 2 | Tour adverse seulement. | [ ] oui [ ] non |
| Albion the Sanctifire Dragon | 3 | ⚖ Lecture : les 2 zones centrales = la zone M3 de chaque joueur ; demande des monstres adverses. | [ ] oui [ ] non |
| Aluber the Jester of Despia | 2 | Monstre Fusion détruit au combat ou quittant le terrain par un effet adverse : impossible au tour 1 du pilote (pas de combat, pas d'adversaire). | [ ] oui [ ] non |
| Dogmatika Ecclesia, the Virtuous | 1 | Indestructible au combat contre un monstre Invoqué Spécialement depuis l'Extra Deck : combat, hors du pilote. | [ ] oui [ ] non |
| Droll & Lock Bird | 1 | Répond à un ajout du Deck à la main de l'adversaire : n'arrive jamais dans le pilote. | [ ] oui [ ] non |
| Fallen of Albaz | 1 | Coût : défausser 1 carte. Fusion avec cette carte et des monstres adverses seulement : sans monstre adverse, aucune Fusion (2 matériels au moins) n'est possible. | [ ] oui [ ] non |
| Garura, Wings of Resonant Life | 1 | Dégâts de combat doublés : combat, hors pilote. | [ ] oui [ ] non |
| Granguignol the Dusk Dragon | 2 | Un monstre est Invoqué Spécialement par un effet de monstre adverse : hors pilote. | [ ] oui [ ] non |
| Mirrorjade the Iceblade Dragon | 2 | Quitte le terrain à cause d'une carte adverse : hors pilote. | [ ] oui [ ] non |
| Mixousia the Confounder | 2 | Phase Principale adverse : hors pilote. | [ ] oui [ ] non |
| Predaplant Dragostapelia | 1 | Cible un monstre adverse : hors pilote. | [ ] oui [ ] non |
| Predaplant Dragostapelia | 2 | Annule les effets activés des monstres adverses à Compteur Prédateur : hors pilote. | [ ] oui [ ] non |
| Rindbrumm the Striking Dragon | 2 | Tour adverse seulement. | [ ] oui [ ] non |
| The Golden Swordsoul | 1 | Déclaration d'attaque : pas de Phase de Combat au tour 1 (R31), hors du pilote. | [ ] oui [ ] non |
| Tri-Brigade Mercourier | 1 | Répond à un effet de monstre adverse : hors du pilote. | [ ] oui [ ] non |

Le texte officiel n'est pas recopié ici (dépôt public, texte de Konami) : le relecteur le lit dans la base ou sur la
carte. 16 cartes distinctes dans l’échantillon de 20 effets.

## 5. Désaccords avec les réponses existantes de l'oracle

| Point | Oracle | Formalisation | Statut |
|---|---|---|---|
| **R23 / T37** | `Incredible Ecclesia`, effet de Phase de Fin **facultatif** (texte OCG de BabelCDB, « You can ») | **Obligatoire** (texte TCG de notre base, sans « You can ») : la fin du tour est refusée tant qu'il attend | Désaccord de **texte**, pas de règle ; le texte TCG fait foi (brief). Non compté comme erreur. |
| R22 | Ordre libre (réglage par défaut) ; ordre imposé avec `DUEL_TCG_SEGOC_FIRSTTRIGGER` | Ordre libre | Accord avec le réglage par défaut ; le réglage TCG actuel reste à confirmer (N-liste) |
| R34 | Envoi de l'Extra Deck traité en coût | Traité en coût | Accord |

Aucun autre désaccord : sur les 68 situations que l'oracle a rejouées, la formalisation donne le même verdict et les
mêmes listes que le YAML (lui-même identique à l'oracle sauf T37).

## 6. Tests

- **Exécutés** : 69 situations du YAML (59 de plus qu'à la tranche 0), 30 situations J1, 173 tests pytest
  (`test_j1.py` : 37 cartes, empreintes, situations J1, couverture des 57 effets, R22 avec effet obligatoire, fin de
  tour refusée, annulation par `Ash Blossom`, errata d'une carte J1).
- **En attente, expliqués** : T67 (explorer toutes les lignes d'une main : algorithme d'exploration, lot C3) ; T71 et
  T72 (hors pilote : monstre adverse, `Ash Blossom` adverse ; T71 répond aujourd'hui `hors_perimetre`).
- **Erreurs trouvées pendant les tests** : aucune erreur de formalisation. Trois erreurs de scénario (T45 et T53 :
  ordre des matériels dans le libellé ; J13 : déclencheur d'`Aluber` oublié dans le script), corrigées.
- **Relecture de l'auteur** (après les tests, non indépendante) : aucune erreur trouvée ; 13 points non tranchés par
  le texte relevés (N01 à N13).
