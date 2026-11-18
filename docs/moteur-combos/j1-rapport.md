# J1 — formalisation des 37 cartes du pilote Branded (lot C2, TOK-118)

> **18/11/2026**, agent du lot C2 (Opus), branche `claude/c2-j1-formalisation-a044b3`. Rien n'est poussé ni fusionné.
> Commandes : `python scripts/combos_harnais.py` (harnais, statuts dans `data/combos.db`),
> `python scripts/combos_echantillon_j1.py` (tirage de l'échantillon), `python -m pytest moteur_combos/tests`.

> **Jalon n°7 (TOK-144, 18/11)** : taux mesuré contre l'oracle sur l'échantillon, **3 effets sur 20 en erreur, Wilson
> 95 % [5,2 % ; 36,0 %] : J1 non atteint** ; 20 cartes `verifiee`. Règle figée au § 8, résultats au § 9. Les § 1 à 7
> décrivent l'état du lot C2 et ne sont pas réécrits.

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

### Volet oracle (recensement complet), rempli le 18/11 au lot C3 (étape 0)

Source : `reponses-oracle.md` § 7 (lot C2 bis), 30 situations J1 et points N01 à N13 rejoués par l'oracle. Lecture seule
des réponses ; le code de l'oracle n'a pas été lu. **Indicateur secondaire, pas le taux de J1** : un recensement des
chemins que l'oracle a joués, sur les 57 effets du pilote, sans tirage au hasard.

| Effets du pilote dont un chemin contredit l'oracle | Avant correction | Après correction (lot C3) |
|---|---|---|
| Désaccord ferme (règle) | **2** : `Titaniklad` 2, `Mirrorjade` 1 (une seule règle, N09) | **0** |
| Litige (N04, seconde moitié : déclarer l'Attribut déjà porté) | 3 : `Aeon` 2, `Mixousia` 1 et 3 | 3, **tranchés par le texte TCG** (permis, voir ci-dessous) |
| Désaccord de texte (R23, `Incredible Ecclesia` 3) | 1 | 1, inchangé (le texte TCG fait foi) |
| Taux arbitré (ferme seulement) | 2/57 = 3,5 % | 0/57 |
| Taux pessimiste (litige non tranché par un humain = erreur) | 5/57 = 8,8 % | 3/57 = 5,3 % |

- **N09 corrigé** : un effet sans cible qui choisit à la résolution propose aussi un monstre insensible ; l'effet est
  alors sans effet sur lui (`Mirrorjade` 1, et par la même règle générale `Luluwalilith` 1, `Aeon` 1, `Rindbrumm` 1 :
  ces trois derniers n'ont pas été joués par l'oracle sur ce point). Situation J26 réécrite sur la réponse de l'oracle
  (`Titaniklad` choisi, reste sur le terrain), test `test_n09_mirrorjade_peut_choisir_titaniklad_insensible`.
- **N04** : DIVIN est déclarable (oracle, adopté). Attribut déjà porté : le texte TCG d'`Aeon` (« declare 1 Attribute;
  all other monsters on the field become that Attribute ») et de `Mixousia` (« declare 1 Attribute; it becomes that
  Attribute ») ne l'interdit pas ; la restriction vue chez l'oracle vient probablement de son script. **Gardé permis**,
  lu par l'agent : à confirmer par un juge (sans conséquence de jeu, une liste de choix seulement).
- **N01 adopté** : `Luluwalilith` ne se déclenche pas sur sa propre sortie de l'Extra Deck (J30 passe de « non couvert »
  à « légal, aucun déclenchement »). Toute Invocation Synchro de `Luluwalilith` est désormais couverte.
- **Confirmés sans changement** : N02, N03, N05 à N08, N10, N11, N13 (la formalisation répondait déjà comme l'oracle ;
  les notes ⚖ correspondantes sont levées). N12 reste non testable (hors pilote).
- Le volet humain (20 effets à l'aveugle) attend toujours un relecteur : rien n'est rempli ci-dessous.

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

> **Mise à jour du 18/11 (lot C3)** : le passage de l'oracle sur J1 (C2 bis) ajoute N09 (désaccord ferme, **corrigé**)
> et N04 seconde moitié (litige, **tranché par le texte TCG**, permis) ; voir « Volet oracle » au § 4. Le tableau
> ci-dessous reste celui du jeu de tests (lot 17).

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

<!-- REGLE-JALON-7-DEBUT -->
## 8. Jalon n°7 (TOK-144) : règle de comptage figée avant la comparaison

> Écrite et commitée le 18/11 **avant** d'exécuter le moteur sur une seule situation de
> `situations-echantillon-j1.yaml`. Cette section ne change plus ; une règle qui se révèle inapplicable est déclarée au
> § 9 et le résultat y est donné selon la règle figée **et** selon la variante. Ce que la session avait déjà lu en
> écrivant : les réponses de l'oracle (`reponses-oracle.md` § 8 et § 9), les 30 réponses J1 du lot C2 bis (§ 7), le
> code du moteur ; **pas** le comportement du moteur sur les situations E01 à E85.

**Référence.** La réponse de l'oracle (colonne « Réponse de l'oracle » du § 9.2 de `reponses-oracle.md`), jamais le
champ `attendu` du fichier (lecture écrite avant de jouer) ni le moteur. Moteur mesuré : `moteur_combos/` tel qu'au
commit `b463f13` (règles et cartes) ; seule la **traduction** des situations en décisions est écrite par cette session
(module de scénarios séparé). Le taux se mesure sur ce moteur ; toute correction vient après, et le taux après
correction est donné à part, « après correction, non revalidé par l'oracle ».

**Traduction.** Chaque situation devient une déclaration et une suite de réponses aux décisions du moteur, comme
`SCENARIOS_J1`. Conventions du lanceur de l'oracle reprises : position Attaque, Zone Monstre Extra de gauche pour un
monstre de l'Extra Deck, plus basse zone principale libre. « Posé » = placé sans historique d'invocation. Une erreur de
traduction (script qui ne dit pas l'action écrite) se corrige ; chaque correction faite après une première exécution
est listée au § 9 avec sa raison, et ne touche jamais au moteur ni à la référence.

**Ce qu'on compare, par situation.** Chaque élément écrit dans la réponse de l'oracle : action ou effet proposé / non
proposé ; listes de choix (comparées comme **ensembles de noms distincts** : multiplicité « ×n » ignorée ; la zone
d'origine comparée quand l'oracle l'écrit) ; question posée ou non ; état d'arrivée écrit (carte détruite, bannie,
restée, Invoquée ; ATK). Un élément que l'oracle n'écrit pas n'est pas comparé.

**Trois issues par situation.**
1. **Accord** : tous les éléments écrits par l'oracle sont identiques côté moteur.
2. **Désaccord avéré** : au moins un élément diffère, y compris une réponse « non couvert » du moteur ou une erreur du
   moteur pendant l'exécution. Un désaccord que la session croit dû à l'oracle (script, réglage) reste **avéré** dans le
   chiffre principal ; il est signalé comme « litige » et donné à part, sans changer le compte.
3. **Non tranché par l'oracle** : (a) la situation est déclarée non testable par l'oracle (E18) ; (b) l'élément en
   désaccord porte sur une clause dont le texte de la base de l'oracle diffère du texte TCG par le sens (liste du § 7.4
   de `reponses-oracle.md`) ; (c) le moteur ne peut pas représenter le départ (limite du modèle, déclarée situation par
   situation) — ce dernier cas est listé à part, comme défaut de couverture à corriger.

**Unité : l'effet tiré** (20 effets, graine 20260118, `echantillon-j1.md` § 1), pas la situation. Un effet est **en
erreur** si au moins une de ses situations est en désaccord avéré ; **juste** sinon, s'il a au moins une situation en
accord ; **non tranché** si toutes ses situations sont non tranchées (il sort alors du dénominateur).

**Deux taux, toujours donnés ensemble.**
- **Principal** : effets en erreur / effets tranchés (non tranchés exclus du dénominateur).
- **Pessimiste** : un effet qui a au moins une situation non tranchée et aucun désaccord avéré compte comme **erreur** ;
  dénominateur 20.
- Pour chacun : intervalle de Wilson à 95 % sur l'échantillon poolé, et estimation ponctuelle pondérée par strate
  (30/57 pour la strate a, 27/57 pour la strate b), comme au § 4. Nombre de cartes distinctes rappelé (16).

**Critère J1 (fixé au lot C2, inchangé).** J1 atteint si la **borne haute de Wilson à 95 % du taux principal ≤ 20 %**.
Repère : 0 erreur sur 20 → 16,1 % ; 1 erreur sur 20 → 24,9 %. Si la variante pessimiste donne un autre verdict, les
deux verdicts sont écrits côte à côte.

**Second compte, séparé (30 situations J1, `situations-j1.yaml`).** Unité : effet du pilote exercé par au moins une
situation J1 ; même définition de l'accord, du désaccord avéré et du non tranché (R23 = texte, donc non tranché ; N04 =
désaccord avéré, litige signalé). Deux valeurs : moteur du lot C2 (comparé par l'oracle au lot C2 bis) et moteur
actuel (après les corrections du lot C3). Ces réponses étaient connues avant d'écrire cette règle : compte descriptif,
jamais additionné à l'échantillon ni utilisé pour le critère J1.

**Critère J2 : celui du § 0 de `j2-rapport.md`, tel quel** (largeur sans cible, 60 s, profondeur 16, filtres D4 ;
« retrouvé » = cible remplie et jalons en sous-suite ; G6 compté tel que figé ; G1-G5 et G6-G10 sur deux lignes).
S'ajoute la condition du jalon n°7 : une séquence ne compte retrouvée que si l'oracle la rejoue **légale pas à pas** et
avec le **même plateau final** ; un pas illégal = combo non retrouvé. Le § 0 ne fixe pas de seuil chiffré : le verdict
(atteint / sous réserve / non atteint) est proposé au formulaire avec les chiffres, sans en inventer un. Les résultats
du rejeu (`reponses-oracle.md` § 8) étaient lus avant d'écrire cette règle.

**Statut `verifiee` (dans `data/combos.db` seulement).** Une carte passe en `verifiee` (`verified_by = oracle`) si
**chaque effet du pilote** (résolution écrite) est exercé (résolu au moins une fois, `regles.EXERCES`) par au moins une
situation en accord avec l'oracle, et si aucune situation jouée par l'oracle qui l'exerce n'est en désaccord non
corrigé. Situations prises en compte : jeu de tests (lot 17, rejouées en entier seulement : celles marquées `*` ou
non rejouées ne comptent pas), situations J1 (lot C2 bis), échantillon (jalon n°7) ; un désaccord du lot C2 bis corrigé
au lot C3 ne bloque pas. Ne passent pas : une carte sans effet du pilote (rien d'exercé) ; une carte dont un effet
dépend d'une question résiduelle ouverte (`questions-residuelles.md`, décision 0055) ; une carte dont un effet n'est
exercé que par une situation non tranchée.
<!-- REGLE-JALON-7-FIN -->

## 9. Jalon n°7 (TOK-144) : résultats, mesurés contre l'oracle

> 18/11/2026, session du jalon n°7. **Mesuré contre l'oracle**, jamais « vérifié par un juge ». Règle : § 8 (figée,
> commit `5fb4193`, empreinte `bac542c5…`). Moteur mesuré : règles et cartes du commit `b463f13`, traduction des
> situations au commit `2902df8` (`moteur_combos/echantillon_oracle.py`). Commande : `python scripts/combos_jalon7.py`.

### 9.1 En bref

| Mesure | Valeur |
|---|---|
| Situations de l'échantillon | 86 : **82 accords**, **3 désaccords** (E32, E49, E68), **1 non tranchée** (E18, non testable par l'oracle) |
| Effets tirés en erreur, **taux principal** | **3 sur 20** (15 %), Wilson 95 % **[5,2 % ; 36,0 %]** ; strate a 1/10, strate b 2/10 ; pondéré par strate 14,7 % |
| Taux pessimiste (non tranché = erreur) | 4 sur 20 (20 %), Wilson 95 % [8,1 % ; 41,6 %] ; pondéré 20,0 % |
| **J1** (borne haute de Wilson ≤ 20 %) | **non atteint**, selon la règle figée comme selon la variante pessimiste |
| Causes distinctes des 3 erreurs | **2** : terrain adverse ignoré par le moteur (E32, E49) ; « up to » lu comme « 0 à N » (E68) |
| Second compte (30 situations J1, descriptif) | moteur du lot C2 : 7 effets sur 31 ; moteur actuel : 3 sur 31 (tous N04) |
| Après correction (non revalidé par l'oracle) | 0 sur 20 sur ces mêmes situations : **pas une mesure**, ne compte pas pour J1 (§ 9.6) |
| Cartes passées en `verifiee` (`data/combos.db`) | **20** sur 37 (21 remplissent la règle ; `Ecclesia and the Dark Dragon` réservée, § 9.7) |

Lecture (avis `data-scientist-ygo`, relecture du 18/11 : comptage conforme à la règle, intervalles recalculés) : avec 3
erreurs sur 20, aucune méthode raisonnable ne descend sous 20 % ; un intervalle stratifié avec correction de population
finie (57 effets) donne environ [2 % ; 27 %], borne haute toujours au-dessus de 20 % (calcul descriptif, non prévu
par la règle). J1 mesure si les effets répondent juste, pas le nombre de défauts : « 3 effets en erreur, 2 causes
distinctes » se donnent côte à côte, sans les fusionner.

### 9.2 Les 20 effets tirés

| # | Strate | Effet | Situations | Issue |
|---|---|---|---|---|
| 1 | a | `Aluber` 1 | E01-E04 | juste (4 accords) |
| 2 | a | `Blazing Cartesia` 2 | E05-E09 (E08b compris) | juste (6) |
| 3 | a | `Branded Fusion` 1 | E10-E16 | juste (7) |
| 4 | a | `Dogmatika Ecclesia` 2 | E17-E21 | juste (4) ; E18 non tranchée |
| 5 | a | `Garura` 2 | E22, E23 | juste (2) |
| 6 | a | `Nadir Servant` 1 | E24-E30 | juste (7) |
| 7 | a | `Super Polymerization` 1 | E31-E35 | **erreur** (E32) |
| 8 | a | `The Golden Swordsoul` 2 | E36-E39 | juste (4) |
| 9 | a | `Titaniklad` 3 | E40-E43 | juste (4) |
| 10 | a | `Tri-Brigade Mercourier` 2 | E44, E45 | juste (2) |
| 11 | b | `Branded Opening` 2 | E46-E50 | **erreur** (E49) |
| 12 | b | `Branded in High Spirits` 2 | E51-E54 | juste (4) |
| 13 | b | `Luluwalilith` 1 | E55-E59 | juste (5) |
| 14 | b | `Luluwalilith` 2 | E60-E62 | juste (3) |
| 15 | b | `Ghost Ogre` 1 | E63-E67 | juste (5) |
| 16 | b | `Hyperinvoked Aeon` 1 | E68-E70 | **erreur** (E68) |
| 17 | b | `Three Champions` 1 | E71-E73 | juste (3) |
| 18 | b | `Three Champions` 2 | E74-E78 | juste (5) |
| 19 | b | `Titaniklad` 1 | E79-E81 | juste (3) ; ATK lues des deux côtés (3700, 3700, 2500) |
| 20 | b | `Titaniklad` 2 | E82-E85 | juste (4) ; E85 : ciblée, ni annulée ni détruite, pas de question « détruire ? » |

Les trois situations où la lecture écrite avant de jouer différait de l'oracle (E05, E08, E08b : `Ash Blossom` en main
sert de matériel à `Cartesia`) sont en **accord** : le moteur proposait déjà ce que l'oracle propose.

### 9.3 Les trois désaccords, en termes de jeu

- **E32, `Super Polymerization`** : son texte permet de prendre les matériels de Fusion « sur l'un ou l'autre terrain »,
  donc aussi un monstre de l'adversaire. Avec `Albaz` chez nous et `Springans Kitt` chez l'adversaire, l'oracle propose
  la Fusion de `Rindbrumm` et envoie `Kitt` au Cimetière de l'adversaire. Le moteur ne regardait que notre terrain et
  répondait « non activable ». Défaut de **couverture** : le pilote suppose un adversaire sans carte, et le moteur
  rendait un « non » au lieu de dire sa limite.
- **E49, `Branded Opening`** (effet tiré) : l'étape préalable — `The Fallen & The Virtuous` détruit un monstre Fusion
  **de l'adversaire** — était refusée par le moteur (« aucune cible valide ») : il ne savait ni cibler ni détruire une
  carte adverse. Le défaut est dans `The Fallen & The Virtuous` (effet non tiré) et la même cause que E32 ; la clause
  de `Branded Opening` (« un monstre Fusion **que vous contrôlez** ») n'a pas pu être jouée. Compté contre l'effet
  tiré, comme le veut la règle (« au moins une de ses situations »).
- **E68, `Hyperinvoked Aeon`** : « bannir **jusqu'à** autant de cartes que de matériels » impose au moins 1 carte ;
  le moteur permettait de n'en bannir aucune (« terminer » dès le premier choix). Erreur de **lecture** du texte.

### 9.4 Variantes et écarts déclarés (la règle figée n'a pas changé)

1. **Attribution (variante non figée, verdict inchangé)** : si le désaccord de E49 est attribué à l'effet réellement
   fautif (`The Fallen & The Virtuous` 1, non tiré), `Branded Opening` 2 devient juste : **2 sur 20**, Wilson 95 %
   [2,8 % ; 30,1 %], J1 toujours non atteint. Le chiffre principal reste 3 sur 20.
2. **Erratum d'un repère du § 8** (pas de la règle) : « 1 erreur sur 20 → 24,9 % » est une borne de Clopper-Pearson ;
   la borne de Wilson vaut **23,6 %**. Le critère (Wilson ≤ 20 %) n'en dépend pas : une seule erreur suffit toujours à
   le manquer.
3. **Traduction corrigée après la première exécution** (règle du § 8 : listée ici) : « posé » était d'abord traduit par
   « arrivée non précisée » (valeur du modèle qui veut dire « inconnue ») ; le fichier dit « placé sans historique
   d'invocation ». Traduit ensuite par « arrivée connue, qui n'est pas une invocation » (comme le retour d'`Ecclesia and
   the Dark Dragon`). Effet : E05 et E79 seulement — avec la première traduction, `Sprind` figurait dans la liste des
   Fusions comme option **à légalité inconnue** (son matériel doit avoir été Invoqué Spécialement ce tour, ce que
   « non précisé » ne permet pas de trancher). Aucune autre situation ne change. Les autres retouches (ordre des
   réponses, nom d'une décision) ont été faites avant toute comparaison.
4. **Second compte** : J30 n'exerce aucun effet ; il est rattaché à `Luluwalilith` 1 (la clause en question, N01).
   Règle appliquée à la lettre, `Super Polymerization` 1 apparaît en erreur au lot C2 parce qu'elle sert d'étape
   préalable dans J26 (désaccord N09, qui porte sur `Mirrorjade` 1 et `Titaniklad` 2) : variante par attribution,
   6 sur 31.

### 9.5 Second compte : les 30 situations J1 (descriptif, réponses connues avant la règle)

| Moteur | Effets exercés en erreur | Wilson 95 % | Pessimiste | Effets en erreur |
|---|---|---|---|---|
| Lot C2 (comparé au lot C2 bis) | 7 sur 31 | [11,4 % ; 39,8 %] | 8 sur 32 | `Luluwalilith` 1 (J30, « non couvert »), `Aeon` 2, `Mixousia` 1 et 3 (N04), `Mirrorjade` 1, `Titaniklad` 2 (N09), `Super Polymerization` 1 (préalable de J26) |
| Actuel (après le lot C3) | 3 sur 31 | [3,3 % ; 24,9 %] | 4 sur 32 | `Aeon` 2, `Mixousia` 1 et 3 (N04 : restriction de script contre texte TCG, litige) |

Non tranché : `Incredible Ecclesia` 3 (J07, R23, texte OCG). Jamais additionné à l'échantillon.

### 9.6 Après correction (non revalidé par l'oracle)

Corrections (commit `b31e5df`) : `Super Polymerization` prend aussi ses matériels sur le terrain adverse (le
matériel adverse va au Cimetière de l'adversaire) ; `The Fallen & The Virtuous` (effet 1) peut cibler et détruire une
carte face recto de l'adversaire, sans remplacement par `Branded Opening` ; `Hyperinvoked Aeon` (effet 1) bannit au
moins 1 carte. Filtre d'exploration `aeon_sans_bannissement` adapté (l'effet n'est plus activé, au lieu d'être activé
puis arrêté tout de suite).

**Après correction : 0 sur 20 sur ces mêmes situations, non revalidé par l'oracle.** Ce chiffre est optimiste par
construction (corrections faites en voyant ces situations) : ce n'est pas une mesure et il ne compte pas pour J1.
Remesurer demande un nouveau tirage d'effets non vus ; même 0 sur 20 n'y donnerait qu'une borne haute de 16,1 %.
Tests : `moteur_combos/tests/test_echantillon_oracle.py` (85 situations en accord après correction).

Ce qui reste hors des corrections : les autres effets qui visent « une carte du terrain » (`Three Champions` 2,
`Luluwalilith` 1, `Aeon` 1, `Mirrorjade` 1…) ignorent encore le terrain adverse. Sans incidence au tour 1 du pilote
(adversaire sans carte), mais même défaut que E32 et E49.

### 9.7 Statuts `verifiee` (moteur mesuré, avant correction)

Écrits dans `data/combos.db` du checkout (`python scripts/combos_jalon7.py --ecrire-statuts`, après
`python scripts/combos_harnais.py` ; sauvegarde à côté, une transaction ; jamais `yugioh.db` ni `serving.db`).

- **Passées en `verifiee` (20)** : `Aluber`, `Ash Blossom`, `Blazing Cartesia`, `Branded Fusion`, `Branded in High
  Spirits`, `Cocatorium`, `Dogmatika Ecclesia`, `Fallen of the White Dragon`, `Garura`, `Ghost Ogre`, `Gold
  Sarcophagus`, `Granguignol`, `Mulcharmy Fuwalos`, `Nadir Servant`, `Rindbrumm`, `Sprind`, `The Dragon that Devours
  the Dogma`, `Titaniklad`, `Tri-Brigade Mercourier`, `Tri-Brigade Springans Kitt`.
- **Réservée hors règle (1)** : `Ecclesia and the Dark Dragon` remplit la règle, mais le rejeu J2 montre une différence
  de modèle (J2-a, `reponses-oracle.md` § 8.1) que la règle n'avait pas prévue : le moteur la fait revenir au passage
  en Phase de Fin, l'oracle en fait un effet obligatoire de Phase de Fin dont le joueur choisit le moment (liste
  d'options plus courte, zones différentes possibles). La règle est une condition nécessaire, pas suffisante.
- **Restent `formalisee` (16)** : désaccord non corrigé au moment de la mesure (`Super Polymerization`, `Branded
  Opening`, `The Fallen & The Virtuous`, `Hyperinvoked Aeon`, `Mixousia`) ; question résiduelle ouverte (`Incredible
  Ecclesia` Q1, `Guiding Quem`, `The Golden Swordsoul`, `Three Champions` Q2, `Luluwalilith` Q3, `Mirrorjade` Q6,
  `Albion the Sanctifire Dragon` Q7) ; effet exercé seulement par une situation rejouée en partie (`Springans Kitt` 2) ;
  aucun effet du pilote (`Fallen of Albaz`, `Droll & Lock Bird`, `Predaplant Dragostapelia`).
- `data/combos.db` est propre au checkout : après fusion, relancer les deux commandes ci-dessus sur le dépôt principal.

### 9.8 Limite (obligatoire)

Un accord prouve que deux lectures concordent, pas que la règle est juste : quand le texte est ambigu et que l'oracle
et le moteur le lisent de la même façon, l'erreur commune passe inaperçue, donc le taux mesuré est une **borne basse**
du taux réel (formulation `data-scientist-ygo`). S'y ajoutent : un seul oracle (scripts écrits par la communauté),
adversaire passif, 16 cartes distinctes pour 20 effets (effets d'une même carte dépendants), et des clauses non
exerçables au tour 1 avec ce deck (déclarées dans l'en-tête de `situations-echantillon-j1.yaml`).
