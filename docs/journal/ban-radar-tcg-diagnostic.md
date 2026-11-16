# TOK-115 — Ban Radar TCG : pourquoi il ne bat pas la méthode « cartes les plus jouées » (lot 15a, 2026-11-17)

Branche `claude/lot15a-tok-115-diagnostic-d81236`, non fusionnée. Session sur Opus 5.5 (`claude-opus-5-5`).
Lecture seule de `data/yugioh.db` (copie de référence du 2026-11-16). **Aucun poids modifié** : `build_ban_radar.py`
et `backend/app/routers/ban_radar.py` sont inchangés (`git diff` vide sur les deux). Le formulaire de décision est à
la fin.

Reproduire (≈ 50 s, graine fixée, deux exécutions comparées avec `cmp` : sorties identiques) :

```
python scripts/diagnose_ban_radar.py --db <dépôt principal>/data/yugioh.db --out <dossier>
```

Le script écrit dans `<dossier>` le jeu de données (`dataset.csv`, 18 600 lignes) et les tableaux intermédiaires
(`par_liste.csv`, `bootstrap.csv`, `poids_par_pas.csv`, `auc_univariee.csv`, `references_20_listes.csv`).

---

## La réponse en trois phrases

1. **Les poids écrits ne sont pas ceux qui jouent.** Dans une somme pondérée, ce qui départage les cartes est le
   poids multiplié par la dispersion du critère. La part des decks (30 % écrits) varie peu d'une carte à l'autre et ne
   pèse que **17 %** du classement ; le critère porteur (25 % écrits) **5 %**. Les exemplaires joués (20 % écrits) et
   la tendance (10 % écrits) en pèsent **40 % et 24 %**.
2. **Or en TCG ces deux critères départagent mal les cartes touchées** : pris seuls, ils les classent à peine mieux
   que le hasard (AUC 0,61 et 0,59, contre 0,83 pour la part des decks). **47 % des cartes touchées en TCG sont jouées
   à moins de 1,5 exemplaire** (22 % en OCG) : des staples jouées à un exemplaire, que le score fait descendre.
3. **Le score gagne en tête de liste et perd sur le reste.** Son top 25 est fait de pièces jouées à 3 et en hausse
   (médiane 2,84 exemplaires), ce qui attrape les moteurs de deck visés par Konami ; mais les cartes touchées jouées à
   un exemplaire tombent loin, ce qui dégrade le rang médian. En OCG, où les cartes touchées sont jouées à 2,5
   exemplaires en médiane, ce même biais est un atout.

## Ce qu'on peut en conclure, et pas plus

- Une régression logistique estimée sur les seules listes passées **fait mieux que les poids actuels en TCG** sur les
  7 listes tenues à l'écart (rang médian meilleur sur 7 listes sur 7 ; top 25 inchangé). En OCG, elle fait jeu égal.
- Elle **ne bat pas les staples en rang médian en TCG** (mieux sur 4 listes sur 7, moins bien en moyenne, écart dans le
  bruit). Elle les bat nettement en top 25 (25 cartes touchées contre 13).
- La règle fixée par Thomas (« adoptés seulement s'ils battent les poids actuels **et** les staples sur les listes
  tenues à l'écart ») **n'est donc pas remplie**. Recommandation : ne pas changer `WEIGHTS` maintenant (formulaire).
- Sur 10 listes TCG, « les staples font mieux en rang médian sur 7 listes » n'est **pas** un écart démontré (test du
  signe p = 0,34). L'écart en top 25 en faveur du score (6 listes, 1 contraire, 3 égalités) ne l'est pas non plus
  (p = 0,13). Ce qui est net : le score fait moins bien que la part des decks sur l'**ensemble** du classement TCG
  (AUC plus basse sur 7 listes sur 7 tenues à l'écart, et sur les 10 listes).

---

## La démarche pas à pas (pour Thomas)

### Étape 1 — Le jeu de données

Pour chacune des 20 banlists retenues par le backtest (10 TCG, 10 OCG, avril 2024 à octobre 2026), on prend le
classement que le Ban Radar aurait produit **la veille de l'entrée en vigueur**, tel que le calcule
`build_ban_radar.backtest_lists` (la fonction du backtest, sans copie). Chaque carte de cet univers donne une ligne :
ses six critères ce jour-là, et une cible qui vaut 1 si la liste l'a touchée (son statut devient plus sévère), 0 sinon.

Résultat : 18 600 lignes, dont **225 cartes touchées** (126 en TCG, 99 en OCG). Moins de 1,5 % de lignes positives :
c'est un problème « déséquilibré », ce qui oriente les choix suivants.

### Étape 2 — La régression logistique

C'est le modèle le plus simple qui fasse ce qu'on veut : il cherche **un poids par critère** tel que la somme
pondérée sépare au mieux les cartes touchées des autres. La somme est ensuite passée dans une courbe en S qui la
transforme en nombre entre 0 et 1. Ce qui compte ici, c'est la somme elle-même : comme le score actuel, elle classe
les cartes, et ses coefficients se lisent comme des poids. On peut donc comparer terme à terme « poids choisis à la
main » et « poids appris des données ».

- **Pourquoi `class_weight="balanced"`** : avec 1,5 % de cartes touchées, un modèle qui répond « jamais touchée »
  a raison 98,5 % du temps et n'apprend rien. L'option donne à chaque carte touchée un poids d'environ 70 dans le
  calcul de l'erreur, pour que les deux classes comptent autant. Elle ne change pas la nature du modèle, seulement
  ce qu'il cherche à bien faire.
- **Critères standardisés** (moyenne 0, écart type 1, calculés sur les seules listes d'entraînement) : sinon le
  modèle pénaliserait inégalement des critères d'échelles très différentes.
- **Régularisation fixée d'avance** (C = 1, la valeur par défaut) : pas de réglage, donc pas de choix fait en
  regardant les listes de test.

### Étape 3 — La validation temporelle

On ne mélange jamais les dates. Pour tester la liste n° 4 d'un format, le modèle est entraîné sur les listes 1 à 3 ;
pour la n° 5, sur 1 à 4 ; et ainsi de suite (« fenêtre croissante »). Une liste ne sert à l'entraînement que si elle
est entrée en vigueur **avant la veille** de la liste testée : le modèle ne voit jamais l'avenir.

Pourquoi c'est indispensable : un mélange aléatoire laisserait le modèle apprendre sur la liste d'octobre 2026 pour
« prédire » celle d'avril 2025. Les cartes et les decks se ressemblent d'une liste à l'autre (les fenêtres de 6 mois
se chevauchent) : le résultat serait flatteur et faux.

On obtient **7 listes tenues à l'écart par format** (TCG : avril 2025 à octobre 2026 ; OCG : janvier 2025 à
octobre 2026). Trois variantes : TCG seul, OCG seul, et les deux ensemble avec une variable de format.

### Étape 4 — Les mesures

- **Rang médian des cartes touchées** et **cartes touchées dans le top 25** : les deux mesures de la page Historique.
- **AUC** : la probabilité qu'une carte touchée tirée au hasard soit classée au-dessus d'une carte non touchée tirée
  au hasard. 0,5 = hasard, 1 = parfait. Elle regarde **tout** le classement, sans privilégier la tête.
- **Précision moyenne** : elle récompense surtout les cartes touchées placées **tout en haut**. Le hasard y vaut la
  part de cartes touchées (≈ 0,01 à 0,02).
- **Incertitude** : deux outils, parce que 7 listes c'est peu.
  - Bootstrap **par liste** : on retire 10 000 fois 7 listes avec remise parmi les 7, on recalcule l'écart, on garde
    le 5e et le 95e centile (intervalle à 90 %). On rééchantillonne des listes et non des cartes : les cartes d'une
    même liste ne sont pas indépendantes (même fenêtre, mêmes decks).
  - **Test du signe** : sur combien de listes une méthode fait mieux, et quelle est la probabilité d'un tel compte
    si les deux méthodes se valaient (pile ou face). Plus prudent que le bootstrap, qui est optimiste sur si peu de
    listes et sur des fenêtres qui se chevauchent.

---

## Résultats

### 1. Ce que chaque critère vaut seul (20 listes, AUC moyenne, listes au-dessus de 0,5)

| Critère | TCG | OCG |
|---|---|---|
| Part des decks (`ubiquity`) | **0,827** (10/10) | **0,895** (10/10) |
| Critère porteur (`carrier`) | **0,823** (10/10) | **0,901** (10/10) |
| Exemplaires joués (`copies`) | 0,610 (8/10) | 0,745 (10/10) |
| Déjà restreinte (`restriction`) | 0,530 (7/10) | 0,592 (9/10) |
| Tendance (`momentum`) | 0,586 (7/10) | 0,552 (7/10) |
| Pont dans le graphe (`bridge`) | 0,537 (7/10) | 0,549 (8/10) |
| **Score actuel** | 0,773 (10/10) | 0,887 (10/10) |

En TCG, le score combiné classe l'ensemble des cartes **moins bien que la part des decks seule** : il dilue les deux
bons critères dans quatre critères faibles. Part des decks et critère porteur sont presque la même information
(corrélation de rang 0,94 en TCG).

### 2. Poids écrits et poids effectifs du score actuel

Poids effectif = poids × écart type du critère dans la liste (moyenné sur les listes), ramené à 100 %.

| Critère | Poids écrit | Écart type (TCG) | Poids effectif TCG | Poids effectif OCG |
|---|---|---|---|---|
| Part des decks | 30 % | 0,102 | **17 %** | 17 % |
| Critère porteur | 25 % | 0,040 | **5 %** | 6 % |
| Exemplaires joués | 20 % | 0,362 | **40 %** | 39 % |
| Déjà restreinte | 10 % | 0,231 | 13 % | 13 % |
| Tendance | 10 % | 0,430 | **24 %** | 24 % |
| Pont | 5 % | 0,080 | 2 % | 2 % |

C'est le cœur du diagnostic. La phrase du script « testés à ±0,10 sans changer le classement » se comprend : bouger
le poids de la part des decks de 0,10 change peu, car ce critère varie peu. Le classement est piloté à 64 % par les
exemplaires et la tendance, les deux critères les plus faibles en TCG.

### 3. Profil des cartes touchées

| | TCG | OCG |
|---|---|---|
| Cartes touchées classées | 126 | 99 |
| Jouées à moins de 1,5 exemplaire | **47 %** | 22 % |
| Exemplaires joués, médiane (touchées / autres) | 1,66 / 1,07 | 2,48 / 1,04 |
| Génériques (pas d'archétype d'attache) | 38 % | 34 % |
| Déjà Limited ou Semi-Limited | 16 % | 25 % |
| Top 25 du score actuel : exemplaires, médiane | 2,84 | 2,73 |

La leçon d'août sur les exemplaires (« 2,50 chez les touchées contre 1,10 ») **tient en OCG (2,48 / 1,04) mais
beaucoup moins en TCG (1,66 / 1,07)**. Exemple, liste TCG du 2026-10-19 : *Called by the Grave* (1 exemplaire, 92 %
des decks), *Triple Tactics Talent*, *Crossout Designator*, *Anti-Spell Fragrance* sont des cartes jouées à un
exemplaire ; plusieurs touchées de cette liste sont presque absentes des decks (*Amorphage Goliath*, *Naturia
Beast* : moins de 1 % des decks) et ne sont prévisibles par aucune méthode fondée sur le jeu.

### 4. Retirer un critère du score actuel (poids restants inchangés, 20 listes, aucun ajustement)

| Variante | TCG : AUC | TCG : top 25 | TCG : rang médian (médiane des listes) | OCG : AUC | OCG : top 25 |
|---|---|---|---|---|---|
| Score actuel | 0,773 | 30 | 81 | 0,887 | 41 |
| sans part des decks | 0,723 | 16 | 152 | 0,834 | 15 |
| sans critère porteur | 0,752 | 24 | 103 | 0,870 | 30 |
| sans exemplaires | **0,798** | **19** | 106 | 0,843 | 19 |
| sans déjà restreinte | 0,758 | 29 | 84 | 0,857 | 38 |
| sans tendance | 0,753 | 33 | 119 | 0,884 | 46 |
| sans pont | 0,773 | 28 | 84 | 0,887 | 41 |

(Top 25 « score actuel » à 30 ici contre 29 sur la page : égalités de score départagées par rang moyen.)

En TCG, retirer les exemplaires **améliore l'ensemble** du classement (AUC 0,773 → 0,798) mais **vide le top 25**
(30 → 19) : ce critère fait exactement le compromis décrit plus haut. La leçon « le retirer fait tomber le rappel du
haut de liste » reste vraie ; elle ne dit rien du reste du classement.

### 5. Validation temporelle : listes tenues à l'écart

**TCG, 7 listes (2025-04-07 → 2026-10-19), 102 cartes touchées**

| Méthode | Rang médian (médiane des 7 listes) | Rang médian moyen, en % de l'univers | Top 25 (total) | AUC moyenne | Précision moyenne |
|---|---|---|---|---|---|
| Hasard (espérance) | 418 | 50,1 % | 3,0 | 0,500 | 0,017 |
| Staples (part des decks) | 98 | **11,7 %** | 13 | **0,828** | 0,085 |
| Poids actuels | 84 | 17,8 % | 24 | 0,758 | 0,101 |
| Régression, 6 critères, TCG | **51** | 14,4 % | 25 | 0,799 | 0,168 |
| Régression, sans pont, TCG | **51** | 14,6 % | 25 | 0,800 | **0,184** |
| Régression, TCG + OCG | 59 | 12,7 % | **26** | 0,812 | 0,167 |
| Arbres boostés (comparaison) | 99 | 16,5 % | 19 | 0,794 | 0,139 |

Les deux colonnes de rang médian ne disent pas la même chose : la médiane des 7 listes favorise la régression ; la
moyenne en % favorise les staples, parce que deux listes (2025-10-27 et 2026-10-19) pèsent lourd et que les staples
y sont nettement meilleures (rangs 224 et 129 contre 346 et 238).

**OCG, 7 listes (2025-01-01 → 2026-10-01), 73 cartes touchées**

| Méthode | Rang médian (médiane) | Rang médian moyen, % | Top 25 | AUC | Précision moyenne |
|---|---|---|---|---|---|
| Hasard | 504 | 50,0 % | 1,7 | 0,500 | 0,010 |
| Staples | 54 | 6,7 % | 12 | 0,884 | 0,106 |
| Poids actuels | 30 | 5,1 % | 30 | 0,881 | 0,154 |
| Régression, 6 critères, OCG | 29 | 6,4 % | 31 | 0,884 | 0,175 |
| Régression, sans pont | 30 | **3,2 %** | 31 | **0,906** | 0,177 |
| Régression, TCG + OCG | 36 | 3,6 % | 31 | 0,905 | **0,205** |
| Arbres boostés | 54 | 6,1 % | 27 | 0,895 | 0,212 |

**Écarts et incertitude (TCG, 7 listes)** — intervalle bootstrap par liste à 90 %, listes où la première méthode fait
mieux, test du signe bilatéral. Rang médian en points de % de l'univers (négatif = mieux).

| Comparaison | Rang médian | Top 25 | AUC | Précision moyenne |
|---|---|---|---|---|
| Régression − poids actuels | −3,5 pts [−5,0 ; −2,0], 7/7, p = 0,016 | +1 [−8 ; +10], 3/7 (2 égalités), p = 1 | +0,041 [+0,019 ; +0,058], 6/7, p = 0,13 | +0,067 [+0,016 ; +0,122], 5/7 |
| Régression − staples | +2,7 pts [−1,9 ; +7,5], 4/7, p = 1 | +12 [+1 ; +24], 5/7, p = 0,22 | −0,029 [−0,061 ; +0,003], 2/7 | +0,083 [+0,015 ; +0,166], 5/7 |
| Régression TCG + OCG − staples | +1,1 pt [−3,0 ; +5,4], 5/7, p = 0,45 | +13 [+5 ; +22], 5/7, p = 0,06 | −0,016 [−0,039 ; +0,006], 2/7 | +0,081 [+0,024 ; +0,154], 5/7 |
| Poids actuels − staples | +6,2 pts [+0,9 ; +11,7], 2/7, p = 0,45 | +11 [+2 ; +21], 4/7, p = 0,38 | −0,070 [−0,093 ; −0,047], 0/7, p = 0,016 | +0,016 [−0,007 ; +0,048], 3/7 |
| Arbres − staples | +4,8 pts [+0,9 ; +9,2], 3/7 | +6 [−1 ; +13], 4/7 | −0,034 [−0,054 ; −0,015], 1/7 | +0,054 [+0,003 ; +0,108], 5/7 |

Lecture :
- **Seuls deux écarts passent aussi le test du signe** (p ≈ 0,016) : la régression bat les poids actuels en rang
  médian sur 7 listes sur 7, et les poids actuels font moins bien que les staples en AUC sur 7 listes sur 7.
- Tous les autres écarts sont « probables » au mieux : l'intervalle bootstrap exclut parfois 0, mais le compte de
  listes reste compatible avec le hasard. Avec 7 listes, il faudrait 7 sur 7 pour conclure à 5 %.
- **Les arbres n'apportent pas de gain net** (moins bons que la régression sur toutes les mesures en TCG ; en OCG,
  meilleure précision moyenne mais rang médian et top 25 moins bons) : non retenus, comme prévu par le brief.

### 6. Les poids estimés

Régression sur les 10 listes du format, poids ramenés à l'échelle brute des critères (directement comparables aux
`WEIGHTS`, somme des valeurs absolues = 1), intervalle bootstrap par liste (2 000 tirages, 5e-95e centiles).

| Critère | Actuel | Estimé TCG [90 %] | Estimé OCG [90 %] |
|---|---|---|---|
| Part des decks | 0,30 | 0,07 [−0,07 ; 0,18] | 0,10 [0,04 ; 0,16] |
| Critère porteur | 0,25 | **0,79** [0,60 ; 0,87] | **0,68** [0,51 ; 0,78] |
| Exemplaires joués | 0,20 | 0,01 [−0,02 ; 0,04] | 0,07 [0,05 ; 0,09] |
| Déjà restreinte | 0,10 | 0,05 [0,00 ; 0,07] | 0,07 [0,04 ; 0,10] |
| Tendance | 0,10 | 0,04 [0,03 ; 0,06] | 0,04 [0,01 ; 0,07] |
| Pont | 0,05 | −0,03 [−0,11 ; 0,02] | −0,04 [−0,17 ; 0,01] |

Comment lire ce tableau :
- Les chiffres sont des poids **sur l'échelle brute**, comme ceux du script. Le critère porteur a un petit écart type
  (0,04), il lui faut donc un grand poids brut pour peser : 0,79 en brut correspond à une influence comparable à
  celle de la tendance à 0,04. Les coefficients standardisés (influence réelle) en TCG : porteur 0,76, tendance 0,47,
  déjà restreinte 0,28, part des decks 0,17, exemplaires 0,10, pont −0,07.
- Part des decks et critère porteur se partagent la même information (corrélation 0,94) : le modèle met presque tout
  sur l'un, et la répartition entre les deux est **instable** (la part des decks change de signe dans 23 % des
  tirages en TCG). Ensemble, ils pèsent environ 0,86 en TCG.
- Le pont reçoit un poids légèrement négatif et son retrait ne change rien (variante « sans pont » ci-dessus) : il
  n'apporte pas d'information, et il est le seul critère soupçonné de fuite (voir plus bas).
- Les poids estimés à chaque pas de la validation sont stables en TCG dès 5 listes d'entraînement (porteur entre 0,86 et 0,88).

### 7. La leçon d'août, vérifiée sur les 20 listes

« L'omniprésence seule ne prédit rien » est **fausse sur données légales**, comme la révision du 17/11 (note
`docs/decisions/0052`) l'avait établi : la part des decks seule classe mieux que le hasard sur 20 listes sur 20 en AUC
(0,83 en TCG, 0,90 en OCG), et son rang médian est meilleur que le hasard sur les 7 listes tenues à l'écart de chaque
format. Ce qui reste vrai de la leçon d'août : la part des decks seule remplit mal le **haut** du classement (top 25 :
16 cartes touchées sur 10 listes TCG contre 29 pour le score), parce que les cartes les plus jouées sont des staples
que Konami ne touche pas toujours.

---

## Fuites de données : ce que chaque variable sait, et quand

| Variable | Donnée utilisée | Connue à quelle date | Risque |
|---|---|---|---|
| Part des decks, critère porteur, exemplaires, tendance | decks légaux (`deck_legality`, banlist en vigueur à la date du tournoi) joués dans les 6 mois jusqu'à la veille de l'**entrée en vigueur** | veille de l'entrée en vigueur | **Écart annonce / entrée en vigueur** : la fenêtre contient les decks joués entre l'annonce et l'entrée en vigueur (1 à 3 semaines, jusqu'à 10 % des decks). Le classement n'est donc pas établi « avant l'annonce ». Effet de sens inconnu : les joueurs gardent les cartes visées tant qu'elles sont légales (peu d'effet), ou passent déjà à d'autres decks. Le test à J-30 du lot 12 (médiane des rangs médians TCG 80 → 120) mélange cet effet et la perte du dernier mois légitime. Sans les dates d'annonce, non tranché. |
| Déjà restreinte | `banlist_history`, statut en vigueur à la veille | veille | Aucun. |
| Pont | `card_graph_metrics.betweenness`, graphe calculé sur **toutes** les données actuelles | aujourd'hui | **Fuite** : le graphe contient des decks postérieurs à chaque liste. Effet mesuré au lot 12 (au plus 7 rangs) ; ici poids estimé ≈ 0 et variante sans pont identique. Négligeable, mais à retirer ou recalculer par date au prochain changement de poids. |
| Univers (≥ 5 decks, Forbidden exclues) | mêmes decks, statut à la veille | veille | Aucun. Les cartes touchées sous 5 decks (11 en TCG sur 10 listes) sont hors univers pour toutes les méthodes. |
| Cible (touchée) | liste suivante comparée à la précédente | date d'entrée en vigueur | Aucun (c'est ce qu'on prédit). |
| **Poids actuels** | calés le 2026-08-14 en voyant les listes jusqu'à juillet 2026 | août 2026 | **Avantage indu des poids actuels** sur les listes antérieures au calage (5 des 7 listes TCG tenues à l'écart, dont la liste de calage du 2026-05-18). La régression, elle, ne voit jamais la liste testée : son avance sur les poids actuels est obtenue malgré ce handicap. |
| Choix d'analyse | C = 1, 3 listes d'entraînement minimum, variantes définies avant de lire les résultats ; le critère porteur seul n'est qu'une description (choisi après avoir vu les AUC) | — | Degrés de liberté du chercheur limités mais réels : 4 modèles × 4 mesures × 2 formats. Les deux résultats à p ≈ 0,016 survivraient mal à une correction stricte pour comparaisons multiples ; ils sont cohérents avec les autres mesures, d'où leur mention. |

---

## Détails techniques (pour la data scientist)

- **Jeu de données** : `ranking` renvoyé par `backtest_lists` (critères arrondis à 4 décimales par `build`), cartes
  Forbidden déjà exclues ; `y = card_name ∈ hits`. Les cartes touchées hors univers (`missing`) ne sont pas dans le
  jeu, comme dans le backtest. Rangs du score actuel = position dans `ranking` (identique au backtest et à la page) ;
  staples = rang moyen sur `ubiquity` (identique au lot 12, 0 écart vérifié sur les 14 listes testées).
- **Modèle** : `LogisticRegression(C=1, class_weight="balanced", max_iter=5000)` sur critères standardisés
  (`StandardScaler` ajusté sur l'entraînement). Score de classement = `decision_function` (logit) : l'intercept ne
  change pas l'ordre intra-liste. La variable de format du modèle commun ne change donc pas l'ordre non plus (simple
  déplacement d'intercept) ; le modèle commun gagne par le volume d'entraînement, pas par la variable. Des
  interactions format × critère n'ont pas été testées (21 paramètres pour ≈ 100 positifs par format à la fin).
- **Poids implicites** : `coef / scale_`, normalisés par la somme des valeurs absolues.
- **Arbres** : `HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05)`, poids d'échantillon
  équilibrés, graine 115. Paramètres fixés a priori, non réglés.
- **Fenêtre croissante** : entraînement sur `effective < as_of` de la liste testée ; 3 listes minimum (7 listes
  testées par format). Le modèle commun prend toutes les listes des deux formats antérieures à la veille.
- **Bootstrap** : 10 000 tirages de 7 listes avec remise (graine 115) ; mesure agrégée = moyenne (somme pour le top
  25). Fenêtres de 6 mois qui se chevauchent (2025-09-15 et 2025-10-27, 2026-09-21 et 2026-10-19 : six semaines
  d'écart) : listes non indépendantes, intervalles optimistes. Test du signe bilatéral, égalités retirées.
- **Rang médian en %** : rang médian / taille de l'univers, pour agréger des listes de 731 à 1 236 cartes.
- **Ce qui n'a pas été fait** : modèle logit conditionnel par liste (classement intra-liste exact) ; critères
  transformés en rangs centiles par liste ; sensibilité au nombre minimal de listes d'entraînement ; dates
  d'annonce. Le premier et le deuxième sont les pistes les plus prometteuses (formulaire, question 2).
- **Sorties brutes** : le script imprime tout (≈ 260 lignes) ; les tableaux de ce journal en sont recopiés.

---

## Formulaire de décision (à valider par Thomas)

**1. Poids du Ban Radar (`WEIGHTS`, script et API)**
- [x] A. Ne pas les changer maintenant. La règle n'est pas remplie : les poids estimés battent les poids actuels en TCG
  mais pas les staples en rang médian. Relancer `scripts/diagnose_ban_radar.py` à chaque nouvelle banlist.
- [ ] B. Adopter les poids estimés par la régression commune TCG + OCG (meilleurs que les poids actuels en TCG sur
  7 listes sur 7, à égalité en OCG ; ne battent pas les staples en rang médian TCG). Suppose `--backtest`, les deux
  fichiers modifiés ensemble et l'onglet Historique recalculé.
- [ ] C. Des poids distincts par format (suppose une notion de format dans l'API et la table `ban_radar`).

**2. Suite technique**
- [x] Ouvrir un ticket : critères ramenés en rangs centiles par liste (les poids écrits deviennent les poids
  effectifs) et régression logistique conditionnelle par liste, évalués avec ce script et la même règle d'adoption.
- [ ] Rien pour l'instant.

**3. Critère `bridge` (fuite : graphe actuel)**
- [x] Le laisser jusqu'au prochain changement de poids (effet mesuré négligeable, poids estimé ≈ 0), puis le retirer
  ou le recalculer par date.
- [ ] Le retirer maintenant (changement de `WEIGHTS`, donc `--backtest` et recalcul de l'historique).

**4. Dates d'annonce des banlists**
- [x] Les collecter (ticket) : seul moyen de savoir si le classement « de la veille de l'entrée en vigueur » profite
  des decks joués après l'annonce.
- [ ] Laisser la limite écrite telle quelle sur la page.

**5. Verdict court pour la page Historique** (texte proposé, conforme à la charte : mesure, période, source, sans
formule)
- [x] « Sur les 10 banlists TCG d'avril 2024 à octobre 2026, le Ban Radar place plus de cartes touchées dans son
  top 25 que le classement par part des decks (29 contre 16), mais situe moins bien l'ensemble des cartes touchées
  (rang médian meilleur sur 3 listes sur 10). En OCG, il fait mieux sur les deux mesures (41 contre 18 ; 8 listes sur
  10). Avec 10 listes par format, seul l'écart de top 25 en OCG dépasse ce que le hasard produit couramment. »
- [ ] Autre formulation : ……

Commentaire libre : ……
