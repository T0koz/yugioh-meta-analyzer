# Évaluation honnête de la prédiction et du signal OCG → TCG (TOK-73)

Date : 2026-11-16. Données : `data/yugioh.db` rafraîchie (decks jusqu'au 2026-11-14), consommateurs
rebranchés sur `deck_legality` (legal = 1). Accès en **lecture seule** (`mode=ro`), rien n'est écrit.

Reproduire : `.venv/bin/python scripts/evaluate_prediction.py` (≈ 1 min ; options `--part A|B`,
`--boot`, `--perm`, `--json`). Graine fixe (42) : les chiffres ci-dessous sortent à l'identique.

Légende : **[VÉRIFIÉ]** = calculé par le script ou lu dans le code/la base ; **[SUPPOSÉ]** = hypothèse
plausible non testée ici.

---

## 0. Trois constats avant les chiffres

1. **`meta_scores` mélange TCG et OCG [VÉRIFIÉ].** Le notebook 04 n'a aucun filtre sur `ocg`. Le script
   recalcule la table à partir de `tournament_decks` sans filtre : 2 129 lignes sur 2 129 identiques
   (écart max 0). 12 053 decks sur 22 422 (**53,8 %**) sont OCG. Le modèle du notebook 05 (« prédire le
   TCG ») est donc entraîné et évalué sur une méta mixte, avec une banlist 100 % TCG en feature.
   `meta_scores_regional` existe mais utilise une autre formule (échelle différente, mois = `uploaded`,
   jointure sur `deck_cards`) : je ne l'ai pas utilisée, j'ai recalculé un TCG pur avec la formule du
   notebook 04 (`ocg = 0`).
2. **Le « TCG » du notebook 09 est la table mélangée [VÉRIFIÉ].** Le signal « OCG(t) → TCG(t+L) » est donc
   mesuré contre une cible qui contient l'OCG. À lag 0 : r = **+0,918** (table mélangée) contre **+0,523**
   (TCG pur). La contamination est mécanique, pas un signal.
3. **Je ne retrouve pas r = 0,771 (n = 43) [VÉRIFIÉ].** Le même code du notebook 09 sur les données
   actuelles donne, à lag 4, r = **+0,522, n = 863** (cible mélangée) et **+0,475, n = 656** (TCG pur).
   Le n = 43 venait d'un état antérieur des données (avant rafraîchissement et filtre `deck_legality`) ;
   je ne peux pas le reconstituer. **[SUPPOSÉ]** : un n = 43 et un « meilleur lag parmi 6 » produisent un
   r élevé et fragile.

---

## Partie A : le modèle de prédiction (70 % naïf + 30 % Ridge)

### Méthode (fidèle au notebook 05, rien n'est modifié)

Features, `StandardScaler` fitté sur le train, Ridge(α = 50), fenêtre glissante 9 mois, test = mois suivant,
`pred_meta_score = niveau + 0,3 × delta_prédit`. Walk-forward strict, aucune fuite repérée :

- le train du mois i ne contient que des cibles connues à la date i (la cible du mois i−1 est le mois i) ;
- lags, `rolling` : décalés d'au moins 1 ; banlist : liste en vigueur au 1er du mois
  (`scripts/build_banlist_features.py`) ; le scaler et le coefficient des baselines sont refittés par fold.

**Pour l'évaluation je regarde la variation** `delta = score(t+1) − score(t)`. Prédire le niveau est
presque gratuit (un archétype fort ce mois-ci l'est le mois prochain) : c'est ce que mesure le ρ « 0,63 ».

Bootstrap **par mois** (2 000 réplicats, on rééchantillonne les 24 mois test, pas les lignes) et, en
robustesse, par **blocs de 3 mois consécutifs** (les mois voisins sont corrélés). Les IC ci-dessous sont les
IC 95 % « mois iid » ; les IC « blocs de 3 » sont quasi identiques (voir le script).

**Points d'évaluation : 909 lignes (archétype × mois), 24 mois test (2024-11 → 2026-10)**, sur un dataset de
1 275 lignes. Les 9 premiers mois servent uniquement d'entraînement.

### Résultats (table `meta_scores`, fidèle au notebook)

| Métrique | Valeur | IC 95 % (mois) |
|---|---|---|
| ρ poolé niveau, naïf | +0,679 | [+0,634 ; +0,719] |
| ρ poolé niveau, ensemble 70/30 | +0,688 | [+0,644 ; +0,728] |
| **Différence ensemble − naïf** (poolé) | **+0,009** | [+0,003 ; +0,016] |
| Différence ensemble − naïf (moyenne par mois) | +0,008 | [+0,002 ; +0,015] |
| ρ poolé **delta**, Ridge (= ensemble, même rang) | **+0,347** | [+0,264 ; +0,434] |
| MAE delta : persistance (delta = 0) | 0,02059 | [0,01882 ; 0,02259] |
| MAE delta : ensemble 0,3 | 0,01977 | [0,01809 ; 0,02165] |
| MAE delta : Ridge seul | 0,01933 | [0,01775 ; 0,02101] |
| **Différence MAE ensemble − persistance** | **−0,00083 (−4 %)** | [−0,00116 ; −0,00051] |
| Gain de MSE vs persistance : ensemble / Ridge | +6,6 % / +9,9 % | [+3,5 ; +9,4] % / [−0,9 ; +19,3] % |
| Signe du delta correct (Ridge) | 62,8 % | [58,9 ; 66,6] % |
| Part de delta < 0 (taux de base) | 52,8 % | — |

Comparaison avec les chiffres annoncés : « ρ poolé ≈ 0,64 vs naïf 0,63 » (écart +0,01). Sur les données
actuelles : **0,688 vs 0,679, écart +0,009**. L'ordre de grandeur de l'écart est le même ; les niveaux sont
plus hauts parce que les données ont changé (je n'ai pas l'ancien état pour isoler la cause). Le ρ moyen
par mois du naïf est de +0,672 (le « +0,508 » du contexte vient aussi d'un autre état des données).

### Baseline de « retour à la moyenne » (ce que fait vraiment le Ridge)

Le delta est en grande partie du retour vers la moyenne : un archétype au sommet ce mois-ci redescend en
moyenne (le score est bruité, ~30 decks par archétype et par mois). Deux baselines fittées sur le train
(OLS, walk-forward) :

| Modèle du delta | ρ poolé delta | MAE delta |
|---|---|---|
| Ridge 20 features | +0,347 | 0,01933 |
| OLS(niveau) : 1 feature | +0,337 | 0,01952 |
| OLS(niveau, delta_1m) : 2 features | +0,343 | 0,01929 |

**Ridge − OLS(niveau)** : ρ +0,009 [−0,057 ; +0,085], MAE −0,00019 [−0,00076 ; +0,00031]. **Les 20 features
n'apportent rien de distinguable par rapport à une régression à une variable.** [VÉRIFIÉ]

### Verdict A

- **Le gain sur la persistance est distinguable du bruit, mais minuscule.** IC du ρ delta et de la
  différence de MAE excluent 0 ; l'ensemble bat la persistance en MAE sur 20 mois sur 24 (test des signes
  p = 0,002). Mais le gain est de **4 %** de MAE, et la différence de ρ de niveau (+0,009) ne bat le naïf que
  sur 17 mois sur 24 (p = 0,064 : non significatif au seuil de 5 %).
- **La valeur ajoutée est du retour à la moyenne, pas de la prévision de ruptures.** Une régression à une
  variable fait aussi bien (voir plus haut). Le signe est juste à 62,8 % contre 52,8 % pour « toujours à la
  baisse ».
- **Le modèle ne prédit jamais l'entrée d'un nouvel archétype** [VÉRIFIÉ dans le code] : le `dropna` sur
  `meta_score_t1` supprime la première apparition. Ce qui intéresse le plus une boutique est donc hors champ
  du modèle.
- **Sur TCG pur (519 lignes, 24 mois)** : ρ delta +0,421 [+0,250 ; +0,567], mais ensemble − naïf en niveau
  +0,012 [−0,014 ; +0,041] (13 mois sur 24, p = 0,84) : **indistinguable de zéro**. La MAE gagne −0,00199
  [−0,00300 ; −0,00101].
- Sensibilité : exclure le dernier mois test (cible partielle, 2026-11 au 14/11) ne change rien
  (écart ensemble − naïf +0,009).
- **Poids W = 0,3** : choisi sur ces mêmes données d'après le notebook. Sur la grille, le ρ niveau passe de
  0,679 (W = 0) à 0,692 (W = 0,5) ; W = 0,3 n'est pas un optimum établi, juste dans un plateau. Ne pas le
  présenter comme « validé ».
- **Ce que je peux affirmer** : « le modèle réduit l'erreur de variation d'environ 4 % et classe les
  variations avec un ρ d'environ 0,35, comme une régression à une variable ». **Ce que je ne peux pas
  affirmer** : qu'il anticipe des changements de méta.

---

## Partie B : signal OCG → TCG

### Construction

- Scores OCG et TCG pur recalculés avec la formule du notebook 09 : `sqrt(share × placement_norm)`, mois =
  date `created`, `deck_legality.legal = 1`.
- Panneau archétype × mois : **273 archétypes × 35 mois** (2024-01 → 2026-11), zéros pour les absents.
- Contrôle : ma jointure interne sur le panneau 2024+ redonne exactement les r du code pandas du notebook
  (ex. 0,6049 / 0,6083 / 0,5286 aux lags 2 / 3 / 4).
- Trois univers : **inner** = jointure interne du notebook (garde seulement les paires où l'archétype est
  présent aux deux dates : **sélection sur la cible**, biais) ; **visible** = archétypes présents en OCG ou en
  TCG à la date t (ne dépend que de l'information à t : l'univers honnête d'une prévision) ; **full** = toutes
  les cellules, zéros inclus.
- Tous les r sont des Pearson poolés sur des paires non indépendantes (même archétype sur plusieurs mois) :
  **les p-values classiques du notebook (10⁻⁶¹) sont inutilisables**, d'où permutations et bootstrap par
  archétype.

### B1. Reproduction (lag 4, jointure interne)

| Version | r | n paires | archétypes |
|---|---|---|---|
| Notebook annoncé | 0,771 | 43 | n/d |
| Même code, données actuelles, cible mélangée | +0,522 | 863 | 129 |
| Même code, TCG pur | +0,475 | 656 | 106 |
| TCG pur, OCG ≥ 2024 (panneau) | +0,529 | 652 | 105 |
| Univers visible (TCG pur) | +0,577 | 1 835 | 273 |

Le meilleur lag de la plage 2-7 est le **lag 2** dans le notebook refait (r = 0,705 mélangé, 0,574 pur), pas 4.

### B2. Test de permutation (2 000 permutations, une queue, TCG pur)

**Choix :** permutation **par blocs d'archétype** (on échange les séries OCG entières entre archétypes et on
laisse la série TCG intacte). Permuter des lignes isolées détruirait l'autocorrélation temporelle et
surestimerait la significativité. Statistique recalculée à l'identique sur chaque permutation (y compris
l'univers inner, qui dépend des données permutées).

- r interne, lags 0-6 : p = 0,0005 à 0,0025 (plancher = 1/2001) ; lag 7 : 0,016 ; lag 8 : 0,020.
- r partiel (OCG(t) ~ TCG(t+L) | TCG(t)), lags 1-8 : p = 0,0005 partout ; r = +0,40 à +0,53, nul ≈ 0 ± 0,03.
- Spearman transversal moyen par mois : +0,35 à +0,50, p = 0,0005 à tous les lags.
- Avec la cible **mélangée**, r interne à lag 0 = 0,918 (contamination).

**Test complémentaire, plus dur : décalage circulaire** de chaque série OCG (l'archétype garde son identité,
seul le calage temporel est détruit). Le nul n'est plus à 0 : il vaut ≈ +0,25 en r univers complet, ce qui
mesure la part « les archétypes forts le sont partout ». Observé à lag 4 : +0,629 (q95 du nul +0,330, p =
0,0005). **Le calage temporel apporte donc réellement de l'information** aux lags 1 à 6. Lags 7-8 en r
interne : p = 0,24 et 0,32 (non distinguable du nul).

**Limite [SUPPOSÉ]** : l'échange d'archétypes casse aussi la durée de vie des archétypes ; une p-value à
0,0005 prouve un lien archétype-spécifique, pas un mécanisme causal. Le fait que le calendrier de sortie des
cartes TCG suit celui de l'OCG est l'explication naturelle, non testée ici.

### B4. Balayage des lags 0-8 : 4 mois est-il vraiment le meilleur ?

**Non, c'est un plateau.** r interne par lag, avec correction pour comparaisons multiples (9 lags) :

| Lag | r interne | p brut | p Bonferroni | p BH | p du max (0-8) |
|---|---|---|---|---|---|
| 0 | +0,523 | 0,0005 | 0,0045 | 0,0009 | 0,0005 |
| 1 | +0,602 | 0,0005 | 0,0045 | 0,0009 | 0,0005 |
| 2 | +0,605 | 0,0005 | 0,0045 | 0,0009 | 0,0005 |
| 3 | +0,608 | 0,0005 | 0,0045 | 0,0009 | 0,0005 |
| **4** | **+0,529** | 0,0005 | 0,0045 | 0,0009 | 0,0005 |
| 5 | +0,471 | 0,0015 | 0,0135 | 0,0022 | 0,0035 |
| 6 | +0,448 | 0,0025 | 0,0225 | 0,0032 | 0,0050 |
| 7 | +0,316 | 0,0155 | 0,139 | 0,017 | 0,0405 |
| 8 | +0,297 | 0,0200 | 0,180 | 0,020 | 0,0475 |

(p du max : probabilité que le MAX de r sur les 9 lags dépasse la valeur observée sous le nul, ce qui corrige
le fait de choisir le meilleur.) Après Bonferroni, les lags 7-8 ne sont plus significatifs.

Bootstrap par archétype (2 000 rééchantillonnages d'archétypes) :

- **Meilleur lag (fréquence d'être l'argmax, plage 0-8)** : univers visible : lag 3 = 58 %, lag 4 = 28 %,
  lag 5 = 7 %, lag 6 = 4 %, lag 2 = 3 % ; r partiel : **lag 4 = 43 %**, lag 3 = 36 %, lag 6 = 14 % ;
  r interne : lag 3 = 41 %, lag 1 = 31 %, lag 2 = 28 %, **lag 4 = 0 %**.
- Écart r(4) − r(L), IC 95 % : visible, lags 2/3/5/6 tous contiennent 0 (ex. L3 [−0,04 ; +0,03]) ; interne :
  r(4) − r(3) = [−0,13 ; −0,03] (le lag 3 est significativement meilleur), r(4) − r(5) = [+0,01 ; +0,10].
- Conclusion : le signal est **présent et à peu près constant entre 2 et 6 mois** (visible : 0,55 → 0,58 →
  0,58 → 0,56 → 0,54), puis décline. Le lag « optimal » de 4 mois est un artefact du choix du max. L'argument
  commercial honnête est « un signal utilisable à 2-6 mois d'avance », pas « 4 mois précis ».

**Sens inverse (TCG(t) → OCG(t+L))** [VÉRIFIÉ] : r visible à lag 4 = +0,227 (partiel +0,055) contre +0,577 (partiel +0,534) dans le sens
direct ; l'écart direct − inverse est positif à tous les lags ≥ 1 (IC 95 %, visible, lag 4 : [+0,25 ; +0,43] ;
partiel : [+0,33 ; +0,60]). L'asymétrie va dans le sens « l'OCG précède le TCG ». **[SUPPOSÉ]** : elle peut
aussi refléter que l'OCG a plus de decks et un méta plus « en avance » sur le calendrier de sortie des cartes.

**Baseline autorégressive (le TCG prédit son propre futur)**, univers visible :

| Lag | r TCG(t) → TCG(t+L) | r OCG(t) → TCG(t+L) | r partiel OCG, contrôlé par TCG(t) |
|---|---|---|---|
| 1 | +0,646 | +0,490 | +0,399 |
| 2 | +0,501 | +0,551 | +0,480 |
| 4 | +0,296 | +0,577 | +0,534 |
| 6 | +0,221 | +0,539 | +0,507 |

À partir de 2 mois l'OCG corrèle mieux avec le TCG futur que le TCG lui-même ; à 1 mois, la persistance TCG
gagne (0,646 vs 0,490), mais l'OCG ajoute encore +0,40 en partiel.

### B3. Validation croisée par archétype et walk-forward

Modèle linéaire `TCG(t+L) ~ OCG(t)`, univers visible. Métrique : MSE et R² relatif au modèle constant.
M0 constante, M1 = AR(TCG(t)), M2 = OCG(t), M3 = AR + OCG.

**Leave-one-archetype-out** (244 archétypes, n = 1 835 lignes, lag 4 ; attention : ce n'est PAS un test de
prévision, l'entraînement contient des mois postérieurs, il mesure si la relation se généralise à un archétype
jamais vu) :

| Modèle | R² vs constante | ρ |
|---|---|---|
| M1 AR | +0,086 | +0,222 |
| M2 OCG | +0,330 | +0,387 |
| M3 AR + OCG | +0,342 | +0,464 |

ΔMSE(M3 − M1) = −4,6e-4, IC 95 % bootstrap par archétype [−7,1e-4 ; −2,3e-4] (le bootstrap rééchantillonne les
erreurs hors-échantillon, sans refitter).

**Walk-forward temporel** (fit uniquement sur les paires dont la cible est connue à la date de prédiction,
blocs de 3 mois pour l'IC) : lag 4, 20 mois test, 1 134 lignes : R² M1 = +0,107, M2 = +0,328, M3 = +0,347 ;
ΔMSE(M3 − M1) = −4,4e-4 [−6,7e-4 ; −2,3e-4], M3 meilleur que M1 sur 15 mois sur 20. Lag 8 : M3 meilleur sur
12 mois sur 12. Lag 1 : 16 mois sur 26 (l'OCG apporte moins à court terme).

**Verdict B3** : l'OCG apporte quelque chose **au-delà de la persistance du TCG**, de façon distinguable du
bruit, hors échantillon, sur la base de 20 à 26 mois test selon le lag. Aux lags ≥ 5, M2 ≈ M3 : le TCG
courant n'apporte plus rien une fois l'OCG connu.

### B5. IC bootstrap par archétype (clusters, 2 000 rééchantillonnages)

| Lag 4 | r | IC 95 % |
|---|---|---|
| Interne (notebook), n = 652 | +0,529 | [+0,427 ; +0,589] |
| Visible, n = 1 835 | +0,577 | [+0,481 ; +0,642] |
| Partiel | +0,534 | [+0,448 ; +0,599] |

Les ~105 archétypes de la jointure interne sont l'unité réelle d'information, pas les 652 paires.

---

## Verdict global

1. **Prédiction (Partie A)** : un gain réel mais petit (≈ 4 % de MAE sur la variation, ρ delta ≈ 0,35),
   indiscernable d'une régression à une variable ; l'écart de ρ de niveau avec le naïf (+0,009) est à la
   limite de la significativité. À ne pas vendre comme une capacité d'anticipation.
2. **Signal OCG → TCG (Partie B)** : **il existe et résiste** à : cible TCG pure, permutation par archétype,
   décalage temporel, correction des lags multiples, baseline autorégressive, validation par archétype et
   walk-forward, bootstrap par cluster. C'est le résultat solide du projet.
3. **Mais les chiffres de vitrine sont faux** : r = 0,771 / n = 43 n'est plus reproductible (r ≈ 0,53 à lag 4
   sur un TCG propre, IC [0,43 ; 0,59]) ; la cible était contaminée par l'OCG ; « lag 4 mois » est un plateau
   2-6 mois, pas un pic.
4. Corrections suggérées (non faites, hors périmètre) : refaire `meta_scores` en séparant les régions
   (TOK-69/72) ; mettre à jour `src/lib/site-facts.ts` (r, n, lag) ; annoncer « 2 à 6 mois ».

## Limites générales

- 35 mois et 273 archétypes : peu de régimes de méta distincts. **[SUPPOSÉ]** : 2026 (Kewl Tune) domine et
  tire les corrélations.
- Genesys, banlist amendée, fenêtres ambiguës autour des changements de liste : non traités ici (voir
  `deck_legality.days_to_boundary`).
- Les mois `created` (partie B) et `uploaded` (table `meta_scores`, partie A) diffèrent pour 3 265 decks sur
  23 948 (13,6 %) : les deux parties ne sont pas strictement comparables entre elles.
- La cible OCG vaut ce que valent les données yugiohmeta (dépendance TOK-76).
- Aucune modification de `WEIGHTS` ni du Ban Radar : le backtest n'est pas concerné.
