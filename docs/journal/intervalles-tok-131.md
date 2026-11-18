# Intervalles de prévision par archétype (TOK-131, B4)

Date : 2026-11-18. Branche `claude/jalon-2-survie-intervalles-ocg-af6a73`. Données : clone de la base de référence
du 18/11 (decks jusqu'au 14/11), ouvert en lecture seule. **Rien d'affiché ne change** : ni le front, ni l'API,
ni `SERVED_TABLES`, ni le notebook 05. Aucun `WEIGHTS` touché.

Reproduire : `python scripts/build_prediction_intervals.py` (≈ 6 s, graine 42, 2 000 tirages ; `--json out.json`,
`--no-ocg`, `--boot N`). Table optionnelle : `--db <copie> --write` (voir § 7).

## 1. Ce qui est mesuré

- **Prévision évaluée : celle qui est servie**, `p = max(niveau + 0,3 × delta_Ridge, 0)` (ensemble 70 % naïf + 30 %
  Ridge, notebook 05), sur `meta_scores` (TCG pur depuis TOK-80), unité « score méta » (la page l'affiche × 100).
- **Résidus du walk-forward strict** de `scripts/evaluate_prediction.py` (`build_dataset`, `walk_forward` importés,
  pas recopiés) : 582 lignes (archétype × mois), 27 mois de test (2024-08 → 2026-10).
- **Amorce** : les 3 premiers mois (2024-08 à 2024-10, 75 résidus) servent seulement à calibrer le premier mois.
  **Critère sur les 24 suivants** (2024-11 → 2026-10, **507 prévisions**), même fenêtre que `evaluation-prediction.md`.
- **Règle temporelle** : pour le mois de test t, quantiles et échelles ne voient que les résidus des mois < t. La
  cible d'une ligne du mois s est s + 1 : à la fin du mois t, les cibles des lignes s < t sont connues. C'est la
  même règle que l'entraînement du walk-forward ; aucune information postérieure n'entre dans un intervalle.
- **Protocole figé avant la première exécution** (docstring du script) : candidats, règle d'adoption, niveaux,
  bootstrap. Deux variantes asymétriques ont été ajoutées **après lecture** et sont marquées exploratoires.

## 2. Méthodes

Toutes à 80 % nominal, calibration **cumulative** (tous les résidus passés) : la part d'un archétype dérive, mais un
mois compte ~20 résidus ; une fenêtre courte rend le quantile instable. La sensibilité en fenêtre de 12 mois
(ABS-12M) ne change rien (80,1 % contre 79,3 %), ce qui justifie le choix a posteriori.

| Code | Méthode | Pourquoi |
|---|---|---|
| ABS | conformité « split » séquentielle : p ± quantile conforme d'ordre ⌈(n+1)·0,8⌉ des \|résidus\| passés | la référence la plus simple, garantie sous échangeabilité |
| MONDRIAN | ABS par classe de niveau (terciles du niveau courant, calculés sur la calibration passée ; repli global sous 20 résidus) | les résidus sont hétéroscédastiques : \|résidu\| ~ niveau, Pearson +0,51, Spearman +0,40 (582 lignes) |
| NORM | \|résidu\| / s(niveau), s = a + b·niveau (MCO sur le passé, plancher 0,25 × médiane, réglé à la main) | même motif, échelle continue au lieu de classes |
| ACI | ABS à niveau adaptatif (Gibbs et Candès 2021), γ = 0,05 (réglé à la main) | dérive non stationnaire |
| N-PERS (naïve a) | niveau du mois (« le mois dernier ») ± quantile des \|y − niveau\| passés | naïf demandé |
| N-GAUSS (naïve b) | p ± 1,2816 × écart type des résidus passés | naïf demandé |
| ASYM, MONDRIAN-ASYM *(exploratoires)* | quantiles signés séparés pour chaque queue, global ou par classe | ajoutées après lecture (§ 4) |

**Règle d'adoption figée** : (1) couverture globale dans [75 ; 85] % ; (2) couverture du tiers supérieur de niveau
dans [70 ; 90] % ; (3) plus petit score de Winkler parmi les candidats qui passent ; (4) comparaison aux naïves.

**Troncature à 0** : la cible est toujours ≥ 0, donc tronquer la borne basse ne retire jamais une valeur couverte.
Vérifié : couverture identique avec et sans troncature pour toutes les méthodes. Seule la largeur baisse. La borne
basse est à 0 pour 15 % des intervalles MONDRIAN évalués (42 % pour ABS, 52 % pour N-GAUSS).

## 3. Résultats TCG (prévision servie)

Couverture poolée sur 507 prévisions, IC 95 % par bootstrap des 24 mois (iid, puis blocs de 3 mois consécutifs ;
autocorrélation d'ordre 1 de la couverture mensuelle entre −0,07 et +0,24, les deux IC sont proches). Largeur et
Winkler en points de score × 100. Terciles du niveau : < 4,01 / 4,01 à 6,96 / > 6,96 (169 prévisions chacun) ;
« top 5 » = 5 premiers archétypes du mois par niveau (120 prévisions).

| Méthode | Couverture | IC 95 % mois | IC 95 % blocs | Largeur | Winkler | Bas | Milieu | Haut | Top 5 | Sans le dernier mois |
|---|---|---|---|---|---|---|---|---|---|---|
| ABS | 79,3 % | [70,5 ; 86,1] | [70,0 ; 85,5] | 8,83 | 16,26 | 89,3 % | 88,2 % | **60,4 %** | **56,7 %** | 78,9 % |
| **MONDRIAN (retenu)** | **75,7 %** | **[67,7 ; 82,0]** | [67,4 ; 81,0] | 8,99 | **15,13** | 75,1 % | 79,3 % | **72,8 %** | **68,3 %** | 75,2 % |
| NORM | 73,6 % | [64,5 ; 81,2] | [63,2 ; 80,5] | 8,51 | 14,60 | 71,6 % | 81,1 % | 68,0 % | 64,2 % | 73,2 % |
| ACI | 79,3 % | [70,9 ; 86,0] | [69,3 ; 86,2] | 9,21 | 16,30 | 89,3 % | 87,6 % | 60,9 % | 55,8 % | 78,9 % |
| N-PERS | 78,7 % | [70,7 ; 85,4] | [69,0 ; 84,7] | 9,10 | 16,72 | 87,6 % | 90,5 % | 58,0 % | 55,8 % | 78,1 % |
| N-GAUSS | 82,8 % | [75,4 ; 88,8] | [73,9 ; 88,7] | 10,00 | 15,89 | 90,5 % | 91,7 % | 66,3 % | 61,7 % | 82,4 % |
| ABS-12M | 80,1 % | [71,5 ; 86,8] | [70,5 ; 86,4] | 9,13 | 16,26 | 90,5 % | 88,8 % | 60,9 % | 57,5 % | 79,5 % |
| ASYM *(expl.)* | 77,7 % | [68,6 ; 85,0] | [67,5 ; 84,4] | 8,45 | 16,33 | 85,2 % | 85,8 % | 62,1 % | 57,5 % | 77,5 % |
| MONDRIAN-ASYM *(expl.)* | 76,5 % | [67,4 ; 83,9] | [67,7 ; 82,0] | 9,00 | 14,98 | 75,7 % | 79,3 % | 74,6 % | 69,2 % | 76,0 % |

**Écart de Winkler du retenu (MONDRIAN)** : contre N-GAUSS −0,76 [−1,60 ; +0,17] (pas démontré) ; contre N-PERS
−1,59 [−2,72 ; −0,43] (démontré). Largeur MONDRIAN : 14,2 points dans le tiers haut, 5,4 dans le tiers bas.

**Couverture par mois** (n = prévisions du mois ; decks = decks TCG du mois cible) :

| Mois (→ cible) | n | Decks cible | ABS | MONDRIAN | N-GAUSS |
|---|---|---|---|---|---|
| 2024-11 | 27 | 243 | 88,9 % | 81,5 % | 88,9 % |
| 2024-12 | 12 | 187 | 100 % | 66,7 % | 100 % |
| 2025-01 | 12 | 338 | 58,3 % | 66,7 % | 58,3 % |
| 2025-02 | 19 | 375 | 73,7 % | 57,9 % | 73,7 % |
| 2025-03 | 16 | 175 | 87,5 % | 87,5 % | 87,5 % |
| 2025-04 | 19 | 540 | 63,2 % | 78,9 % | 68,4 % |
| 2025-05 | 20 | 315 | 100 % | 85,0 % | 100 % |
| 2025-06 | 18 | 211 | 88,9 % | 72,2 % | 94,4 % |
| 2025-07 | 13 | 370 | 100 % | 92,3 % | 100 % |
| 2025-08 | 14 | 367 | 92,9 % | 78,6 % | 100 % |
| 2025-09 | 21 | 200 | 85,7 % | 81,0 % | 90,5 % |
| 2025-10 | 18 | 342 | 83,3 % | 83,3 % | 83,3 % |
| 2025-11 | 21 | 218 | 95,2 % | 95,2 % | 100 % |
| 2025-12 | 23 | 152 | 34,8 % | 30,4 % | 39,1 % |
| 2026-01 | 24 | 351 | 41,7 % | 54,2 % | 50,0 % |
| 2026-02 | 28 | 313 | 75,0 % | 60,7 % | 75,0 % |
| 2026-03 | 32 | 279 | 87,5 % | 93,8 % | 90,6 % |
| 2026-04 | 29 | 405 | 55,2 % | 58,6 % | 69,0 % |
| 2026-05 | 28 | 281 | 100 % | 92,9 % | 100 % |
| 2026-06 | 16 | 131 | 62,5 % | 68,8 % | 75,0 % |
| 2026-07 | 14 | 272 | 42,9 % | 42,9 % | 57,1 % |
| 2026-08 | 30 | 519 | 93,3 % | 93,3 % | 93,3 % |
| 2026-09 | 34 | 240 | 94,1 % | 85,3 % | 94,1 % |
| 2026-10 (→ 11, partiel) | 19 | 156 | 89,5 % | 89,5 % | 94,7 % |

Les ratés se concentrent sur quelques mois de rupture (2025-12, 2026-01, 2026-04, 2026-07 : 30 à 59 %) où tous les
archétypes bougent ensemble. **Pas d'effet banlist systématique** : mois cibles avec une liste TCG entrée en vigueur
77,4 % (8 mois, 195 prévisions), autres 74,7 % (16 mois, 312).

### Lecture

1. **Le critère du ticket est atteint au sens strict, mais il est faible.** MONDRIAN : 75,7 %, dans [75 ; 85] ; mais
   ABS, ACI et **les deux naïves** y sont aussi. Une couverture moyenne de 80 % est facile à obtenir ; elle ne dit pas
   où sont les ratés.
2. **Il n'est pas démontré.** Avec 24 mois, l'IC 95 % de la couverture fait environ ± 7 points pour toutes les
   méthodes ; celui de MONDRIAN, [67,7 ; 82,0], n'exclut ni 70 % ni 80 %.
3. **Couverture conditionnelle : les gros archétypes sont sous-couverts**, là où l'intervalle compte. ABS et les
   naïves couvrent le tiers haut à 58-66 % et le top 5 à 56-62 % (et sur-couvrent les petits à ~90 %). MONDRIAN
   rééquilibre (72,8 % et 68,3 %), sans atteindre 80 %.
4. **Le centre est biaisé vers la persistance.** Dans le tiers haut, les ratés tombent surtout sous la borne basse
   (MONDRIAN 18,9 % sous la borne contre 8,3 % au-dessus ; ABS 29,0 % contre 10,7 %) ; dans le tiers bas, au-dessus
   (22,5 % contre 2,4 %). La prévision n'applique que 30 % du retour à la moyenne prédit : un archétype en tête
   redescend plus que prévu. Les quantiles signés par classe (MONDRIAN-ASYM, exploratoire) rééquilibrent les queues
   (14,8 % / 10,7 % dans le tiers haut) mais gagnent peu en couverture (74,6 %, top 5 69,2 %).

### Niveau 90 % (exploratoire, choisi après lecture)

Même code avec 90 % nominal (500 tirages) : MONDRIAN 88,0 % [81,0 ; 93,5], tiers haut 88,8 %, top 5 82,5 %, largeur
12,2 points ; ABS 87,6 %, tiers haut 70,4 %. Un intervalle « à 90 % » donne donc environ 80 % de couverture observée
sur les gros archétypes. **C'est une sélection sur les mêmes données** : à confirmer sur les mois à venir avant d'en
faire un libellé.

## 4. Par format

Seul le TCG a une prévision servie. En **sensibilité**, le même modèle (variables de banlist TCG, donc mal spécifié
pour l'OCG) et les mêmes méthodes sur `meta_scores_ocg` : 643 lignes, 22 mois évalués (2025-01 → 2026-10, 572
prévisions). La règle figée y retiendrait NORM (80,1 % [76,0 ; 84,0], tiers haut 79,6 %, top 5 82,7 %) ; MONDRIAN
80,2 % [75,7 ; 83,9], tiers haut 84,8 %, top 5 80,0 %, Winkler −1,39 [−1,99 ; −0,72] contre N-GAUSS (démontré).
Les méthodes par niveau tiennent en OCG, où la série est plus régulière (aucun mois sous 50 %) ; **la difficulté
TCG vient des ruptures de méta, pas de la méthode**. Le choix pour le TCG reste MONDRIAN (règle appliquée au TCG).

## 5. Prévisions servies et contrat de la table

- **Reconstruction** : la cellule 11 du notebook 05 (absente d'`evaluate_prediction.py`) est reproduite par
  `production_predictions`. 44 prévisions sur 44 appariées, `data_month` identiques, niveaux identiques ; écart
  maximal de prévision **1,0e-4** (Power Patron ; les 43 autres < 1,5e-5, soit 0,01 point × 100 au plus). Cause
  probable, non vérifiée : une entrée (nombre de cartes ou banlist d'un archétype) modifiée entre le calcul du
  16/11 et le clone du 18/11. Les intervalles se centrent sur la valeur **servie** (`meta_predictions.pred_meta_score`).
- **La prévision servie n'est pas exactement celle du walk-forward** : le modèle de production est entraîné sur
  les 9 derniers mois **y compris** la ligne 2026-10, dont la cible est novembre partiel, puis prédit ces mêmes
  lignes. Écart avec la prévision stricte du même mois : 0,11 point × 100 en moyenne, 0,27 au plus (19 archétypes),
  contre des demi-largeurs de 3 à 8 points. Négligeable pour l'intervalle, à corriger dans le notebook (hors lot).
- **Lignes périmées** : `meta_predictions` contient 25 lignes de `data_month` 2026-08 et 2026-09 (cibles septembre et
  octobre, déjà observées). L'API ne sert que le dernier `data_month` ; la table d'intervalles aussi (19 lignes).
- Calibration des intervalles courants : 563 résidus (mois 2024-08 → 2026-09, ceux dont la cible est connue).

## 6. Limites

- **Échangeabilité** : la garantie conforme suppose des résidus échangeables. Ici, les résidus d'un même mois partagent
  un choc commun (rupture de méta), et la série dérive. La garantie n'est donc qu'approximative ; seule la couverture
  observée compte, et elle est mesurée sur 24 mois seulement.
- **NORM et MONDRIAN** calibrent échelle ou classes et quantile sur les mêmes résidus passés : garantie exacte perdue,
  effet faible à n ≥ 75.
- **Mois partiel** : la dernière ligne évaluée (2026-10 → novembre au 14/11) a une cible partielle ; la retirer fait
  passer MONDRIAN de 75,7 % à 75,2 %. L'intervalle courant vise la valeur finale de novembre.
- **Sélection sur la cible** : le notebook ne garde que les archétypes présents le mois suivant ; un archétype qui
  disparaît (valeur réelle 0) n'est ni prédit ni évalué. Pour la prévision courante, la présence dans novembre
  partiel est déjà acquise, donc les lignes servies ne sont pas concernées ; l'évaluation, elle, l'est.
- **Réglages à la main déclarés** : γ = 0,05 (ACI), plancher 0,25 × médiane (NORM), 20 résidus minimum par classe
  (MONDRIAN), tolérance [70 ; 90] pour le tiers haut, 3 mois d'amorce.
- Variables de banlist en production lues au dernier statut connu (défaut signalé par l'audit, non traité ici).

## 7. Table `meta_prediction_intervals` (non créée sur la référence)

`--write` crée une **table nouvelle** (jamais une table existante ; si elle existe déjà, elle est remplacée, c'est
la sienne), en transaction unique, pour le dernier `data_month` de `meta_predictions`. Refus sur la base du dépôt
principal sans `--reference`. Testé sur une copie supprimée ensuite : 19 lignes, relance idempotente, refus vérifié.

```
archetype TEXT, data_month TEXT, target_month TEXT, pred REAL, lo REAL, hi REAL, level REAL,
method TEXT, calibration_n INTEGER, computed_at TEXT, PRIMARY KEY (archetype, data_month, method)
```

Exemple : `Elfnote | 2026-10 | 2026-11 | 0.15236 | 0.06878 | 0.23594 | 0.8 | MONDRIAN | 563 | 2026-11-18`.
Ordre si la table est adoptée : notebook 05 → `build_prediction_intervals.py --db data/yugioh.db --write
--reference` → ajout à `SERVED_TABLES` → `build_serving_db.py`.

## 7 bis. Code prêt derrière une option (rien d'affiché)

- **API** : `GET /meta/predictions` sert `interval_lo` / `interval_hi` par archétype et `interval_level` /
  `interval_method` (méthode `MONDRIAN`, constante `INTERVAL_METHOD` de `backend/app/routers/meta.py`) **seulement si**
  `meta_prediction_intervals` existe dans la base lue ; sinon `null`, réponse inchangée. Vérifié sur une copie avec la
  table : 19 archétypes sur 19 ont un intervalle ; sans la table : `null`.
- **Garde de couverture** : le routeur cite « FROM meta_prediction_intervals ». Dès que la table existe dans `yugioh.db`,
  `build_serving_db.py` refuse de construire tant qu'elle n'est pas dans `SERVED_TABLES` : c'est l'ordre voulu
  (écrire, ajouter à `SERVED_TABLES`, construire). Ne pas l'écrire sur la référence avant le formulaire.
- **Front** : `/predictions` ne dessine la fourchette (trait épais `--cat-1` à 35 % derrière l'haltère, légende
  « fourchette visée à 80 % », pied d'incertitude remplacé par la couverture observée) que si
  `NEXT_PUBLIC_PREDICTION_INTERVALS=1` au build **et** si l'API sert les intervalles. Par défaut : page identique
  (51 captures inchangées). Capture avec l'option : `docs/planning/2026-11-18/tok-131-intervalles-option.jpg`.
- Le libellé de couverture est écrit dans `predictions/page.tsx` (`INTERVAL_COVERAGE_NOTE`, chiffres du 2026-11-18) :
  à recalculer avant toute mise en ligne.

## 8. À relire par la collaboratrice

- La règle temporelle (calibration sur les mois < t, cible d'une ligne = mois suivant) et l'amorce de 3 mois.
- Le choix MONDRIAN par terciles calculés sur la calibration passée (et non sur les lignes évaluées).
- Le bootstrap par mois et par blocs (IC de la couverture poolée, écarts de Winkler appariés).
- L'interprétation du biais vers la persistance (§ 3, point 4) et la piste 90 % (sélection a posteriori).
- La reconstruction de la cellule 11 (`groupby().last()` prend la dernière valeur non nulle par colonne : les NaN
  d'origine sont conservés exprès).

Temps d'exécution : 5,6 s (évaluation TCG + OCG, 2 000 tirages), 1,3 s avec `--no-ocg --boot 200`.
