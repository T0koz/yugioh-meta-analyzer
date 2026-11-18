# Fenêtre d'arrivée en TCG par analyse de survie (TOK-130, B1, 2026-11-18)

Ticket B1 de l'audit de rigueur (`audit-rigueur-statistique.md` § 2). Script : `scripts/build_arrival_survival.py`
(lecture seule par défaut, ≈ 8 s). **Rien de ce que le site affiche ne change** : le notebook 10 garde sa fenêtre
75-202 jours en attendant le formulaire de Thomas.

## Verdict

**Critère non atteint, et non testable sur 2024-2025.** Le critère de l'audit (couverture annoncée = couverture
observée ± 5 points, origine glissante, 2024-2025) porte, pour la méthode de survie, sur **5 prévisions** (4 cohortes) :
les données OCG commencent en janvier 2024, et il faut attendre mi-2025 pour avoir 8 arrivées connues, le minimum
pour estimer la courbe. Sur ces 5 prévisions : 85 % annoncés, 60 % observés (3 sur 5), écart −25 points, IC 95 %
[−60 ; +15].

Sur la période élargie 2025-2026 (hors critère) : **18 fenêtres sur 23 justes (78 %)**, alors que la courbe
annonçait 89 % en moyenne. La méthode est donc **trop confiante d'environ 11 points** (IC de l'écart [−34 ; +4],
8 cohortes). Sur les mêmes 23 prévisions, la fenêtre actuelle 75-202 fait 15 sur 23 (65 %), à largeur égale
(127 jours contre 124) : avantage à la survie, **non démontré** (5 contre 2, test du signe p = 0,45).

Deux constats changent la lecture de l'audit :
1. **Dans la population du notebook 10, le biais du survivant est faible.** Avec une arrivée définie sur les
   cartes, 42 unités sur 44 sont arrivées, et les 2 autres n'ont que 69-70 jours de suivi. P(jamais arrivé)
   ≤ 6,5 % (IC à 180 jours : jusqu'à 23 %). Le « 37 % jamais arrivés » de `signal-boutique-v3.md` portait sur une
   autre population (94 archétypes, dont beaucoup avec moins de 3 cartes inédites) et sur une arrivée définie par
   le nom. Un intervalle à 80 % existe donc bien, mais il est estimé sur peu de cohortes.
2. **En unité archétype, la fenêtre actuelle est moins fausse qu'en unité carte.** Elle couvre 27 archétypes sur
   36 (75 %, Wilson [59 % ; 86 %], 16 cohortes) sur 2024-2026, contre 62-67 % des cartes (A2). Mais 2024-2025 est en
   partie dans l'échantillon (constantes estimées sur les cartes 2022-2025). Sur les seuls archétypes de 2026,
   postérieurs au calcul, elle fait 12 sur 18 (67 %, 5 cohortes).

Verdict : **à creuser**. Le cadre de survie est le bon (unité, censure, âge), mais l'échantillon est trop petit
pour valider une couverture à ± 5 points. Options au formulaire (réponse de la session, pas dans ce fichier).

## Définitions

Fixées après lecture des délais bruts et **avant** la première validation glissante (docstring du script).

| Élément | Définition | Pourquoi |
|---|---|---|
| Origine de prévision t | 1er de chaque mois, de 2024-02 à 2026-11 | Rejoue un recalcul mensuel du notebook |
| Population à t | Règle du notebook 10 rejouée avec les seules données d'avant t : decks OCG légaux de [t − 3 mois, t), archétype ≥ 5 decks, cartes clés (main, ≥ 30 % des decks), staples OCG exclues, carte inédite si jamais vue en deck TCG avant t et `tcg_date` > t, archétype retenu si ≥ 3 cartes clés inédites | C'est la population pour laquelle le site affiche une fenêtre. Les filtres « staples TCG » et « interdites TCG » sont omis : ils ne retirent que des cartes déjà sorties en TCG, donc ne changent pas le compte des inédites |
| Unité | Composante de libellés dont les cartes inédites se recouvrent à ≥ 50 % | 7 fusions sur 62 libellés (K9 / Vanquish Soul K9 / Crystron K9 / Cyber Dragon, variantes Toon, Clown Crew / Mitsurugi / Resonators...). Sans fusion, le même événement compterait jusqu'à 4 fois |
| Ancre (temps 0) | Médiane du premier deck OCG des cartes inédites | Même ancre que le notebook 10. Elle tombe presque toujours sur une date de sortie de set OCG |
| Burn-in | Ancre ≥ 2024-03-01 | Les decks OCG commencent en janvier 2024 : une ancre de janvier-février 2024 peut être celle d'une carte plus ancienne (troncature à gauche). Retire 5 unités, dont SPYRAL, jamais arrivé |
| Événement | La moitié (arrondie au-dessus) des cartes inédites de l'unité est sortie en TCG. Sortie = `cards.tcg_date` si elle est passée, sinon premier deck TCG | Ce dont la boutique a besoin : que les cartes existent en TCG. Une arrivée par le nom (validateur) n'a pas de sens pour 9 libellés sur 62, joués en TCG sous ce nom avant l'ancre (Branded 185 decks, Mitsurugi 738, Odion 46...) |
| Censure | Pas d'arrivée à la date d'observation (t en validation, 2026-11-14 pour la courbe finale) | Un archétype pas encore arrivé apporte « au moins x jours » : l'ignorer, c'est le biais du survivant |
| Entrée différée | Une unité n'est à risque qu'à partir de son âge à la première rétention | Un archétype arrivé avant d'être retenu n'entre jamais dans la population : le compter dès le jour 0 sous-estimerait le risque aux petits délais |
| Estimateur | Kaplan-Meier à entrée différée, écrit à la main (≈ 15 lignes), variance de Greenwood | `lifelines` n'est pas installé ; la KM ne suppose aucune forme de courbe |
| Fenêtre annoncée | Quantiles 10 % et 90 % de la loi conditionnelle à l'âge u : P(T ≤ x │ T > u) = 1 − S(x)/S(u). Bornes au milieu des paliers. Couverture annoncée = probabilité KM de la fenêtre | Conditionner à l'âge : un archétype retenu à 60 jours n'a plus la même loi qu'au jour 0. Si 90 % n'est pas atteint dans le support observé : pas de fenêtre |

## Effectifs et courbe (au 2026-11-14)

62 libellés retenus au moins une fois → 49 unités → **44 après burn-in**, 42 arrivées, 2 censurées (Raise Moon et
Trirealm Rift, 69-70 jours), **20 cohortes** (mois d'ancre). Délais observés : 54 à 236 jours, médiane 102.

| Jours depuis l'ancre | À risque | P(arrivé) | IC 95 % (bootstrap par cohorte) | ± 1,96 se Greenwood |
|---|---|---|---|---|
| 60 | 35 | 5,6 % | [0 ; 16] | ± 7 |
| 75 | 31 | 23,0 % | [5 ; 45] | ± 13 |
| 90 | 23 | 41,0 % | [19 ; 64] | ± 15 |
| 105 | 12 | 71,9 % | [50 ; 90] | ± 14 |
| 120 | 12 | 74,1 % | [51 ; 91] | ± 13 |
| 150 | 9 | 80,5 % | [63 ; 95] | ± 12 |
| 180 | 5 | 89,2 % | [77 ; 100] | ± 9 |
| 202 | 2 | 97,8 % | [93 ; 100] | ± 4 |

Au-delà de 202 jours, moins de 2 unités à risque : la queue n'est pas estimée (la KM tombe à 0 à 236 jours parce que
la dernière unité à risque arrive, pas parce que tout arrive). Le bootstrap par cohorte est plus large que Greenwood :
les archétypes d'un même set OCG arrivent ensemble en TCG (cohorte de janvier 2026 : 6 unités, toutes arrivées le
2026-05-07). L'effectif utile est plus proche de 20 cohortes que de 44 unités.

Les délais suivent le calendrier des sets TCG : paquets vers 54-68, 80-104, 131, 159-202 jours (un, puis deux cycles
de sortie). La courbe en escalier vient de là, et c'est elle qui rend les probabilités annoncées supérieures à 80 % :
une fenêtre qui inclut un palier en prend toute la masse.

## Validation à origine glissante

À chaque origine : courbe estimée avec les seules unités déjà retenues, censurées à t ; prévision pour chaque unité
retenue ; évaluée seulement si la fin de fenêtre est antérieure au 2026-11-14 (suivi complet, quel que soit le
résultat). Une arrivée hors de la fenêtre, avant ou après, est un échec. IC : bootstrap par cohorte (2 000 tirages,
graine 20261118) ; Wilson donné à titre indicatif (il suppose les unités indépendantes, ce qui est faux ici).

### Population du critère : chaque unité à sa première rétention, origines 2024-2025

| Méthode | Période | Prévisions (cohortes) | Annoncée | Observée | IC boot. | Écart (IC) |
|---|---|---|---|---|---|---|
| (a) fixe 75-202 | 2024 | 6 (4) | 80 % | 100 % | [100 ; 100] | +20 |
| | 2025 | 12 (9) | 80 % | 75 % | [45 ; 94] | −5 [−35 ; +14] |
| | 2024-25 | 18 (12) | 80 % | 83 % | [62 ; 96] | +3 [−18 ; +16] |
| (a') par carte, glissante | 2024-25 | 18 (12) | 80 % | 61 % | [33 ; 88] | −19 [−47 ; +8] |
| (b) survivants | 2024-25 | 6 (5) | 80 % | 50 % | [17 ; 83] | −30 [−63 ; +3] |
| **Survie (KM)** | 2024 | 0 | | | | (< 8 arrivées connues) |
| | 2025 | 5 (4) | 85 % | 60 % | [25 ; 100] | **−25 [−60 ; +15]** |

Détail des 5 prévisions KM : D/D/D et Solfachord (même set) sont arrivés à 54-58 jours, plus tôt que toute arrivée
connue alors, sous la borne basse de 74 jours (échecs) ; Kewl Tune, Elfnote, Radiant Typhoon dans la fenêtre ;
Lunalight sans fenêtre (8 arrivées connues, 90 % non atteint).

### Hors critère

| Population | Méthode | Prévisions (cohortes) | Annoncée | Observée | Écart (IC) |
|---|---|---|---|---|---|
| Premières rétentions 2026 | fixe 75-202 | 18 (5) | 80 % | 67 % | −13 [−59 ; +20] |
| | par carte, glissante | 18 (5) | 80 % | 61 % | −19 [−61 ; +14] |
| | survivants | 20 (6) | 80 % | 50 % | −30 [−66 ; +3] |
| | **survie** | 18 (5) | 91 % | **83 %** | −7 [−36 ; +9] |
| Groupé 2024-2026 | fixe 75-202 | 36 (16) | 80 % | 75 % | −5 [−30 ; +15] |
| | par carte, glissante | 36 (16) | 80 % | 61 % | −19 [−47 ; +5] |
| | survivants | 26 (10) | 80 % | 50 % | **−30 [−60 ; −4]** |
| | **survie** | 23 (8) | 89 % | **78 %** | −11 [−34 ; +4] |
| Toutes les paires (unité, mois) 2024-25 | survie | 12 (6) | 93 % | 83 % | −10 [−30 ; +6] |

8 prévisions de 2026 ont une fin de fenêtre après le 2026-11-14 : non évaluées (on n'évalue jamais une prévision
parce qu'elle a déjà réussi). Aucune paire (unité, mois) n'a reçu une fenêtre fixe déjà finie (0 sur 138).

### Comparaison appariée (mêmes 23 prévisions, 8 cohortes)

| Méthode | Annoncée | Observée | k sur n | Largeur médiane restante |
|---|---|---|---|---|
| (a) fixe 75-202 | 80 % | 65 % | 15/23 | 127 j |
| (a') par carte, glissante | 80 % | 61 % | 14/23 | 112 j |
| (b) survivants | 80 % | 57 % | 13/23 | 67 j |
| **Survie** | 89 % | **78 %** | **18/23** | 124 j |

Survie juste et fixe fausse : 5 ; l'inverse : 2 (test du signe p = 0,45).

## En quoi la survie corrige le biais

La méthode naïve (b) prend les délais des seuls archétypes déjà arrivés à la date de la prévision. À une origine
donnée, les archétypes récents qui arriveront tard ne sont pas encore arrivés : ils manquent, et les délais
observés sont trop courts. Résultat : fenêtres étroites (67 jours) et trop précoces, **50 % de couverture pour
80 % annoncés**. C'est le seul écart dont l'IC exclut 0 ([−60 ; −4]). La KM garde ces archétypes comme censurés
(« pas arrivé à x jours ») et conditionne la fenêtre à l'âge : même largeur que la fenêtre fixe, couverture 78 %.

La méthode par carte (a') souffre du même défaut (seules les cartes déjà sorties en TCG à t, `cards` ne connaissant
que les cartes TCG) et du changement d'unité. La fenêtre fixe (a) y échappe en partie parce qu'elle a été estimée en
2026 sur des cartes de 2022-2025, donc avec un suivi long, et en partie sur les mêmes années que la validation.

## Sensibilités (survie, population du critère)

| Variante | Prévisions | Annoncée | Observée | Fixe 75-202 sur la même population |
|---|---|---|---|---|
| Définition retenue (moitié des cartes) | 5 | 85 % | 60 % | 83 % (n = 18) |
| Arrivée = première carte inédite | 6 | 88 % | 100 % | 72 % |
| Arrivée = toutes les cartes inédites | 5 | 87 % | 80 % | 78 % |
| Libellés sans fusion | 6 | 89 % | 67 % | 86 % (n = 22) |
| Sans burn-in | 12 | 94 % | 100 % | 78 % (n = 23) |
| Arrivée par le nom (validateur), 49 libellés sur 57 | 3 | 90 % | 67 % | 81 % (n = 21) |

Avec 3 à 12 prévisions, ces écarts ne distinguent rien. Ils montrent seulement que le résultat du critère dépend
de choix qu'on ne peut pas départager avec ces données.

## Constat post hoc (non revendiqué)

La KM annonce la probabilité exacte de sa fenêtre (89 % en moyenne) parce que les arrivées tombent en paliers.
Si l'on avait annoncé le niveau nominal (80 %), l'écart groupé 2025-2026 serait de −2 points (78 % observés).
Ce constat vient de la lecture des résultats : il ne compte pas comme une validation.

Variante unilatérale, également post hoc : « arrivée avant la fin de la fenêtre » est juste pour 87 % des fenêtres
de survie (n = 23) et 97 % des fenêtres fixes (n = 36). L'erreur des fenêtres fixes est surtout une arrivée trop tôt.

## Limites

- **Effectif** : 44 unités, 20 cohortes au total ; 18 unités sur 2024-2025, dont 5 évaluables par la survie. Aucune
  couverture ne peut être validée à ± 5 points avec cet effectif : il faudrait environ 250 prévisions indépendantes
  pour qu'un IC à 95 % autour de 80 % fasse ± 5 points, et beaucoup plus avec des cohortes corrélées.
- **Début des données OCG en janvier 2024** : pas d'historique d'archétypes plus anciens, d'où une validation qui ne
  démarre qu'à mi-2025.
- **Queue non estimée** au-delà de 202 jours ; P(jamais) n'a qu'une borne haute (6,5 %, IC jusqu'à 23 %). SPYRAL
  (jamais arrivé) est retiré par le burn-in.
- **Indépendance** : les arrivées dépendent du calendrier des sets TCG (une décision Konami pour tout un set). Le
  bootstrap par mois d'ancre en tient compte en partie ; un même set TCG peut recevoir deux mois d'ancre.
- **Ancre** : la médiane du premier deck OCG suit la sortie OCG d'environ 3 jours en médiane (937 cartes depuis
  2024-02, mais jusqu'à plusieurs mois pour une carte peu jouée).
- **Seuils repris du notebook 10 et réglages déclarés** : 50 % de recouvrement pour la fusion, moitié des cartes
  pour l'arrivée, 8 arrivées minimum, burn-in au 2024-03-01, milieu des paliers pour les bornes. Fixés avant la
  validation, mais pas estimés.
- `cards.tcg_date` vient d'un instantané (juin 2026, plus les ajouts de `fetch_new_cards.py`) ; une carte sortie
  depuis et absente de `cards` est datée par son premier deck TCG, quelques jours plus tard.
- **Le validateur** (`validate_predictions.py`, arrivée par le nom) ne mesure pas la même chose que cette analyse :
  il compte comme arrivé un archétype déjà joué en TCG sous ce nom, et rate les noms hybrides (Harpie/Amazoness).

## Options (détail au formulaire de la session)

1. Garder la fenêtre 75-202 et corriger son libellé en unité archétype (27 sur 36, 75 % ; 12 sur 18 pour 2026).
2. La remplacer par la fenêtre de survie, avec la couverture **observée** en libellé (18 sur 23, 78 %), jamais la
   probabilité KM (trop confiante).
3. Élargir l'historique pour rendre le critère testable : liste complète des cartes YGOPRODeck **sans** filtre
   `format=tcg` (cartes OCG seules comprises, avec `ocg_date` et archétype), soit plusieurs centaines d'archétypes
   depuis 2015 avec censure. Nouveau script d'ingestion, à voir avec `gardien-donnees`.
4. Aligner le validateur sur l'arrivée par les cartes (ticket à part).

Pour comparaison, au 2026-11-14 : Raise Moon, fixe 2026-11-19 → 2027-03-26, survie 2026-11-24 → 2027-03-14 ;
Trirealm Rift, fixe 2026-11-20 → 2027-03-27, survie 2026-11-25 → 2027-03-15 ; Harpie/Amazoness, fixe 2027-01-14
→ 2027-05-21, survie 2027-01-01 → 2027-05-09. Aujourd'hui, la différence pratique est de quelques jours.

## À relire par la collaboratrice

- L'estimateur à entrée différée (`km`) : ensemble à risque `entry < x <= exit`, ex aequo, Greenwood.
- La construction de la fenêtre conditionnelle (`km_window`) : choix des bornes au milieu des paliers, et le fait
  d'annoncer la masse exacte plutôt que le niveau nominal.
- Le bootstrap par mois d'ancre : est-ce le bon niveau de grappe (set OCG, set TCG d'arrivée) ?
- La règle d'évaluabilité (fin de fenêtre ≤ dernière date) et l'exclusion des 8 prévisions de 2026 au suivi incomplet.
- Le choix de l'événement (moitié des cartes) et du burn-in, et la reproduction de la règle du notebook 10 à chaque
  origine (staples TCG et interdites omises, argument dans la docstring).

## Reproduction

```
.venv/bin/python scripts/build_arrival_survival.py                              # lecture seule, ≈ 8 s
.venv/bin/python scripts/build_arrival_survival.py --db COPIE.db --write        # tables nouvelles, sur une copie
```

Depuis un worktree, le script lit `data/yugioh.db` du dépôt principal (`git rev-parse --git-common-dir`), en
`mode=ro`. Deux exécutions donnent une sortie identique (graine 20261118). `--write` crée ou remplace
`tcg_arrival_survival` (une ligne par archétype retenu à la dernière date : ancre, âge, fenêtre, probabilité KM,
P(arrivée sous 183 jours) quand le suivi le permet, `as_of`, `computed_at`) et `tcg_arrival_km` (la courbe), en une
transaction. Il refuse la base du dépôt principal et une table homonyme au schéma différent. Testé sur une copie
le 2026-11-18 (50 → 52 tables, relance idempotente). Aucune des deux tables n'est servie (`SERVED_TABLES` inchangé).
