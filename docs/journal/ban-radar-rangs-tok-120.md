# TOK-120 — Ban Radar : critères en rangs par liste, logit conditionnel, pont daté (lot 22, 2026-11-18)

Branche `claude/j1-tok-120-132-ban-radar-pont-d32da4` (Jalon 1), session sur Opus 5.5. Suite du diagnostic TOK-115
(`ban-radar-tcg-diagnostic.md`) et du ticket B5 de l'audit de rigueur. **Lecture seule** de la base de référence
(`data/yugioh.db`, `mode=ro`). **Aucun poids modifié, rien d'affiché ne change** : `build_ban_radar.py` et
`backend/app/routers/ban_radar.py` sont intacts (`git diff` vide) et `--backtest` redonne les chiffres de référence
(TCG 2026-05-18 rang médian 84/889, OCG 2026-07-01 19/1236 ; les 20 listes identiques).
Dépend de TOK-121 (table `banlist_announcements`, coupure « contenu ») et de TOK-115 (`diagnose_ban_radar.py`).

Reproduire (≈ 1 min par coupure, graine 120, sorties identiques d'une exécution à l'autre) :

```
python scripts/diagnose_ban_radar_rangs.py --db <dépôt principal>/data/yugioh.db --out <dossier>
python scripts/diagnose_ban_radar_rangs.py --db <dépôt principal>/data/yugioh.db --out <dossier> --coupure contenu
python scripts/diagnose_ban_radar.py --rangs [--coupure contenu] --db … --out …     # même chose, depuis TOK-115
```

Fichiers : `scripts/bridge_date.py` (pont daté, réutilisé par TOK-132), `scripts/diagnose_ban_radar_rangs.py`,
option `--rangs` / `--coupure` de `scripts/diagnose_ban_radar.py`. Formulaire : `docs/planning/2026-11-18/decisions-prises.md`.

---

## La réponse en quatre phrases

1. **Mettre les critères en rangs centiles rend les poids écrits presque égaux aux poids effectifs** (part des decks
   33 %, porteur 27,5 %, exemplaires 21 %, tendance 10 %, pont 4 % ; seule « déjà restreinte » tombe de 10 à 5 %, parce
   que 93 % des cartes y sont à égalité à 0), et **le logit conditionnel, estimé sur les rangs, retrouve presque les poids
   écrits** (0,29 / 0,20 / 0,17 / 0,16 / 0,12), sauf le pont, qui reçoit un poids **négatif** (−0,05 [−0,10 ; −0,01]).
2. **Les deux candidats battent nettement les poids actuels en TCG** (rang médian meilleur de 5,4 à 6,3 points d'univers,
   AUC meilleure sur 7 listes sur 7, p = 0,016) **mais pas de façon démontrée les staples** (au mieux −0,15 à −0,27 point,
   5 listes sur 7, p = 0,45). Ils battent les staples en OCG (6 listes sur 7) et placent 2 à 3 fois plus de cartes
   touchées dans leur top 25 que les staples (TCG 29 à 31 contre 13, OCG 32 à 35 contre 10 à 12).
3. **La règle d'adoption figée n'est pas remplie** : le logit conditionnel la remplit à la veille de l'entrée en vigueur
   (TCG et OCG), mais pas à la veille du contenu, où il ne fait mieux que les poids actuels en OCG que sur 3 listes sur 7
   (et place 32 cartes touchées dans son top 25 contre 33). Les rangs avec les poids écrits échouent en TCG face aux
   staples (+0,7 à +0,8 point, 4 listes sur 7).
4. **Le pont daté ne change rien** (AUC seul 0,52 en TCG, au niveau du hasard ; ±0,1 point de rang médian sur le score),
   et la table servie `card_graph_metrics` est **périmée** : 663 nœuds contre 1 402 dans le graphe recalculé aujourd'hui
   (corrélation de rang 0,31). Le pont n'apporte rien de mesurable et sa seule valeur estimée est négative.

---

## Démarche (pour Thomas)

### Étape 1 — Le pont daté (B5)

Le critère « pont » lit `card_graph_metrics.betweenness`, calculé une fois sur toutes les données : le classement d'une
liste de 2024 voyait des decks de 2026 (fuite). `scripts/bridge_date.py` refait, pour chaque date de coupure, la chaîne
des notebooks 02 (co-occurrences pondérées) et 03 (graphe, intermédiarité) avec les seuls decks **mis en ligne** avant
la coupure (`uploaded ≤ as_of`, plus strict que la date du tournoi), la récence étant mesurée depuis la coupure.

Contrôle de fidélité : à la date du jour, le module reproduit **exactement** la table `card_cooccurrence`
(10 741 paires sur 10 741, écart de Jaccard nul, mêmes comptes). Le graphe qui en découle a 1 402 nœuds ; la table
`card_graph_metrics` n'en a que 663 : elle a été calculée sur une version plus ancienne des co-occurrences et n'a pas
été refaite depuis (corrélation de rang 0,31 sur les 608 cartes communes). Le score servi lit donc un pont **périmé**
en plus d'être **non daté**.

Deux écarts assumés avec le notebook 03 : intermédiarité exacte (le notebook tire 500 sources au hasard sans graine)
et `weight = jaccard` repris tel quel, bien que networkx le lise comme une distance (un lien fort allonge le chemin) :
c'est le calcul qui alimente le score servi, le corriger serait un autre critère.

### Étape 2 — Les rangs centiles

Dans chaque liste, chaque critère est remplacé par son rang centile (de 0 à 1, égalités au rang moyen). Tous les
critères ont alors à peu près la même dispersion, donc le poids écrit est le poids qui joue. Le score
`rangs_poids_ecrits` applique les `WEIGHTS` actuels à ces rangs : **aucun paramètre estimé**, rien n'est appris des
listes.

### Étape 3 — Le logit conditionnel par liste

La logistique de TOK-115 estimait une probabilité « absolue » d'être touchée, avec un intercept. Le Ban Radar ne fait
que classer les cartes **d'une même liste**. Le logit conditionnel modélise exactement cela : « parmi les n cartes de
la liste, pourquoi ces k-là ? ». Tout ce qui est commun à la liste (nombre de cartes touchées, format, époque) disparaît
du modèle. Estimation : approximation de Breslow (softmax dans chaque liste, une fois par carte touchée), exacte à
O(k/n) près (k/n ≈ 1 %) ; vérifiée contre la vraisemblance exacte (polynôme symétrique élémentaire, maximisée en partant
de zéro) sur les 20 listes : poids identiques à ±0,01 près, log-vraisemblance exacte −887,45 au point de Breslow contre
−887,04 à son propre maximum. Sans pénalité. Candidat retenu : sur les rangs, listes TCG et OCG ensemble.

### Étape 4 — Validation et règle d'adoption, figées avant lecture

Identiques à TOK-115 : fenêtre croissante, au moins 3 listes d'entraînement, une liste ne sert que si elle est entrée
en vigueur avant la coupure de la liste testée ; 7 listes tenues à l'écart par format ; bootstrap par liste
(10 000 tirages) et test du signe. La règle (docstring du script, écrite avant la première exécution) :

> dans un format, le candidat fait mieux que les poids actuels ET que les staples en rang médian (moyenne en % de
> l'univers), sur au moins 5 des 7 listes pour chacune des deux comparaisons, sans placer moins de cartes touchées dans
> son top 25 que les poids actuels ; adoption proposée seulement si c'est vrai en TCG ET en OCG, aux deux coupures.

Deux candidats seulement (`rangs_poids_ecrits`, `clogit_rangs`) ; les autres méthodes sont des lectures.

---

## Résultats

### 1. Poids écrits et poids effectifs (20 listes, veille de l'entrée en vigueur)

| Critère | Écrit | Effectif, critères bruts (TCG / OCG) | Effectif, rangs centiles (TCG / OCG) |
|---|---|---|---|
| Part des decks | 30 % | 17 % / 17 % | **33 % / 33 %** |
| Critère porteur | 25 % | 5 % / 6 % | **27,5 % / 27,5 %** |
| Exemplaires joués | 20 % | 40 % / 39 % | **21 % / 21 %** |
| Déjà restreinte | 10 % | 13 % / 13 % | 5 % / 5 % |
| Tendance | 10 % | 24 % / 24 % | **10 % / 10 %** |
| Pont | 5 % | 2 % / 2 % | 4 % / 4 % |

« Déjà restreinte » ne prend que trois valeurs (0, 0,6, 1) et vaut 0 pour 93 % des cartes de l'univers : en rangs, ces
cartes sont à égalité au même rang moyen, ce qui écrase sa dispersion. C'est le seul critère où « écrit » et
« effectif » restent éloignés.

### 2. Validation temporelle, veille de l'entrée en vigueur (7 listes tenues à l'écart par format)

| Méthode | TCG : rang médian (médiane des listes) | TCG : rang médian moyen, % univers | TCG : top 25 | TCG : AUC | OCG : rang médian moyen, % | OCG : top 25 | OCG : AUC |
|---|---|---|---|---|---|---|---|
| Hasard | 418 | 50,1 % | 3,0 | 0,500 | 50,0 % | 1,7 | 0,500 |
| Staples | 98 | **11,7 %** | 13 | **0,828** | 6,7 % | 12 | 0,884 |
| Poids actuels | 84 | 17,8 % | 24 | 0,758 | 5,1 % | 30 | 0,881 |
| Poids actuels, pont daté | 87 | 17,9 % | 24 | 0,758 | 5,2 % | 30 | 0,880 |
| **Rangs, poids écrits** | **44** | 12,4 % | 29 | 0,823 | 4,0 % | 33 | 0,912 |
| Rangs, pont actuel | 46 | 12,4 % | 31 | 0,825 | **3,5 %** | 34 | 0,913 |
| **Logit conditionnel, rangs** | 50,5 | **11,5 %** | **31** | 0,823 | 4,0 % | 32 | **0,915** |
| Logit conditionnel, rangs, format seul | 81,5 | 12,6 % | 25 | 0,815 | 4,0 % | 33 | 0,914 |
| Logit conditionnel, critères bruts | 54 | 15,8 % | 29 | 0,792 | 3,6 % | **36** | 0,900 |
| Logistique TOK-115 (`logit_6`) | 51 | 14,4 % | 25 | 0,799 | 6,4 % | 31 | 0,884 |

À la veille du contenu (dates du lot 21) : mêmes ordres de grandeur ; poids actuels 17,8 % / 4,5 %, staples 11,7 % /
7,2 %, rangs 12,4 % / 3,3 %, logit conditionnel 11,5 % / 3,6 % (TCG / OCG) ; top 25 TCG 25 / 13 / 29 / 30.

### 3. Écarts aux deux références (bootstrap par liste, intervalle 90 %, listes où le candidat fait mieux, test du signe)

Rang médian en points de % de l'univers (négatif = mieux).

| Coupure | Comparaison | TCG : rang médian | TCG : top 25 | OCG : rang médian | OCG : top 25 |
|---|---|---|---|---|---|
| entrée en vigueur | rangs − poids actuels | −5,4 [−7,6 ; −3,2], 7/7, p = 0,016 | +5 [−2 ; +12] | −1,1 [−4,0 ; +2,0], 6/7, p = 0,13 | +3 [−2 ; +8] |
| entrée en vigueur | rangs − staples | +0,8 [−2,6 ; +4,6], 4/7, p = 1 | +16 [+8 ; +24] | −2,7 [−4,9 ; 0,0], 6/7, p = 0,13 | +21 [+14 ; +30], 7/7, p = 0,016 |
| entrée en vigueur | logit cond. − poids actuels | −6,3 [−9,1 ; −3,5], 6/7, p = 0,13 | +7 [−2 ; +16] | −1,1 [−3,8 ; +1,8], 6/7, p = 0,13 | +2 [−1 ; +5] |
| entrée en vigueur | logit cond. − staples | −0,15 [−3,2 ; +3,1], 5/7, p = 0,45 | +18 [+10 ; +26] | −2,7 [−4,8 ; −0,4], 6/7, p = 0,13 | +20 [+13 ; +28], p = 0,03 |
| contenu | rangs − staples | +0,7 [−2,9 ; +4,5], 4/7 | +16 [+8 ; +24] | −3,9 [−5,7 ; −2,1], 6/7 | +25 [+18 ; +33], 7/7 |
| contenu | logit cond. − poids actuels | −6,3 [−9,1 ; −3,6], 6/7 (1 égalité), p = 0,03 | +5 [−3 ; +13] | −0,9 [−2,8 ; +0,8], **3/7**, p = 1 | **−1** [−4 ; +3] |
| contenu | logit cond. − staples | −0,3 [−3,4 ; +3,1], 5/7, p = 0,45 | +17 [+9 ; +25] | −3,6 [−5,4 ; −1,9], 6/7 | +22 [+15 ; +29] |

Autres écarts utiles (veille de l'entrée en vigueur) : en TCG, le logit conditionnel bat les poids actuels en AUC et en
précision moyenne sur 7 listes sur 7 (p = 0,016 chacun) et la logistique de TOK-115 en rang médian (−2,9 points, 5/7).
Le pont daté contre le pont actuel : +0,1 point de rang médian, aucun écart de top 25 dans 5 listes sur 7.

### 4. Règle d'adoption

| Coupure | Format | Rangs, poids écrits | Logit conditionnel, rangs |
|---|---|---|---|
| entrée en vigueur | TCG | non (staples : +0,8 point, 4/7) | **oui** (de justesse : −0,15 point, 5/7, p = 0,45) |
| entrée en vigueur | OCG | oui | oui |
| contenu | TCG | non (staples : +0,7 point, 4/7) | **oui** (−0,3 point, 5/7, p = 0,45) |
| contenu | OCG | non (poids actuels : 4/7 seulement) | **non** (poids actuels : 3/7, top 25 32 < 33) |

**Règle non remplie** pour les deux candidats. En OCG, les poids actuels sont déjà bons (rang médian ≈ 4,5 % de
l'univers) et l'écart avec le candidat tient dans le bruit ; en TCG, l'écart avec les staples tient dans le bruit.

### 5. Listes postérieures au calage des poids (2026-08-14)

Les seules où les poids actuels n'ont rien vu. Rang médian des cartes touchées / cartes touchées dans le top 25,
veille de l'entrée en vigueur (veille du contenu entre parenthèses quand elle diffère).

| Liste | n / k | Poids actuels | Staples | Rangs, poids écrits | Logit cond., rangs | Hasard |
|---|---|---|---|---|---|---|
| OCG 2026-10-01 | 1 212 / 15 | 52 (44) / 6 | 63 (65,5) / 1 | **20** (22) / **8** | 27 (29) / 7 | 606 |
| TCG 2026-09-21 | 981 / 9 | 206 / 2 | 99 / 0 | 110 / **4** | **87** / 3 | 491 |
| TCG 2026-10-19 | 905 / 37 | 308 (310) / **6** | **128,5** (130,5) / 4 | 211 (213) / 4 | 199 (204) / 4 | 453 |

Sur ces trois listes, les deux candidats font mieux que les poids actuels en rang médian ; face aux staples, mieux sur
deux (OCG 2026-10-01, TCG 2026-09-21), nettement moins bien sur la liste TCG du 2026-10-19 (37 cartes touchées, dont
beaucoup presque absentes des decks). Trois listes ne permettent aucune conclusion ; le tableau est à prolonger à
chaque nouvelle banlist (`--rangs`).

### 6. Poids estimés sur les rangs

Logit conditionnel sur les 20 listes, |somme| = 1, intervalle bootstrap par liste à 90 % (1 000 tirages).

| Critère | Écrit | Estimé (entrée en vigueur) [90 %] | Estimé (contenu) |
|---|---|---|---|
| Part des decks | 0,30 | 0,30 [0,08 ; 0,46] | 0,29 |
| Critère porteur | 0,25 | 0,21 [0,02 ; 0,47] | 0,20 |
| Exemplaires joués | 0,20 | 0,17 [0,11 ; 0,21] | 0,17 |
| Déjà restreinte | 0,10 | 0,17 [0,10 ; 0,22] | 0,16 |
| Tendance | 0,10 | 0,12 [0,07 ; 0,15] | 0,12 |
| Pont (daté) | 0,05 | **−0,05** [−0,10 ; −0,01] | −0,05 |

Les poids estimés à chaque pas de la validation sont stables à partir de 12 listes d'entraînement (part des decks
0,16 à 0,23, porteur 0,34 à 0,41, exemplaires 0,19 à 0,21) ; au début, le modèle met presque tout sur le porteur, comme
en TOK-115 (part des decks et porteur portent la même information, corrélation 0,94). Lecture : **les poids posés à la
main en août sont, sur l'échelle des rangs, très proches de ce que les données estiment** ; ce qui les trahissait,
c'était l'échelle brute des critères (§ 1), pas leur valeur.

---

## Relecture `data-scientist-ygo`

Méthode et chiffres relus et en partie recalculés : les 8 lignes de la règle d'adoption reproduites, le rang médian de
`rangs_poids_ecrits` sur TCG 2026-05-18 refait de zéro (`radar.build`, rangs, poids écrits : 36/889, comme le script ;
84 pour les poids actuels, comme `--backtest`). Verdict : règle fidèle à TOK-115 (plus stricte), conclusion « non
remplie » juste, **recommandation A (ne rien changer)** ; pont à retirer au prochain changement de poids sans le
recalculer par date. Corrections appliquées : vérification de Breslow partie de zéro, colonne `n_train_lists_tcg_ocg`
dans `par_liste.csv` (le logit commun s'entraîne sur les deux formats). Biais signalé, qui renforce la prudence : les
poids actuels ont été calés sur TCG 2026-05-18 (tenue à l'écart ici) et validés sur OCG 2026-07-01 (19 pour eux, 115 et
130 pour les candidats).

## Fuites de données

| Variable | Donnée | Connue à quelle date | Risque |
|---|---|---|---|
| Critères du score (part, porteur, exemplaires, tendance, restriction) | `build_ban_radar.backtest_lists`, inchangé | coupure (`created ≤ as_of`) | Préexistant : le filtre porte sur la date du tournoi (`created`), pas sur la mise en ligne. Mesuré par le data scientist : 925 decks sur 36 917 (2,5 %) des fenêtres du backtest mis en ligne après la coupure (jusqu'à 141 sur 2 363, OCG 2026-10-01), tous des derniers jours, donc surtout dans le critère « tendance ». Non corrigé ici (changerait `--backtest`) : formulaire. |
| Pont daté | decks `uploaded ≤ as_of` | coupure | Aucun. |
| Rangs centiles | calculés dans la liste testée, sur ses seuls critères | coupure | Aucun (pas de cible). |
| Poids du logit conditionnel | listes entrées en vigueur avant la coupure de la liste testée | coupure | Aucun. |
| Coupure « contenu » | `banlist_announcements.content_date` (veille) | coupure | Dates collectées en novembre 2026 (lot 21), sans fuite sur les decks. |
| Poids actuels | calés le 2026-08-14 en voyant les listes jusqu'à juillet 2026 | août 2026 | Avantage indu des poids actuels sur les listes antérieures (et des `WEIGHTS` utilisés par `rangs_poids_ecrits`). |
| Choix d'analyse | 2 candidats et règle figés avant exécution ; 8 lectures | — | 2 candidats × 2 formats × 2 coupures × 2 références : les p ≈ 0,016 ne survivent pas à une correction stricte. |

---

## À relire par la collaboratrice

1. `bridge_date.py` : fidélité aux notebooks 02 et 03 (filtre `uploaded`, poids de place, récence depuis la coupure,
   intermédiarité exacte au lieu de 500 sources), et le choix de garder `weight = jaccard` comme distance.
2. L'approximation de Breslow (`_breslow`) et sa vérification (`exact_loglik`) ; absence de pénalité au début de la
   validation (3 listes, ≈ 25 cartes touchées).
3. L'opérationnalisation de la règle d'adoption (moyenne des rangs médians en %, 5 listes sur 7, top 25) et l'exigence
   « aux deux coupures ». Une autre lecture raisonnable (rang médian médian au lieu de la moyenne) donnerait-elle un autre verdict ?
4. Le traitement de « déjà restreinte » en rangs (égalités) : faut-il le laisser en 0 / 0,6 / 1 dans un score en rangs ?
5. Les 20 listes ne sont pas indépendantes (fenêtres de 6 mois qui se recouvrent) : bootstrap optimiste.

## Sorties brutes

Les tableaux ci-dessus sont recopiés des sorties de `diagnose_ban_radar_rangs.py` (CSV : `par_liste.csv`,
`bootstrap.csv`, `adoption.csv`, `poids_effectifs.csv`, `poids_clogit_rangs.csv`, `poids_clogit_par_pas.csv`,
`graphe_date.csv`, `toutes_listes.csv`). La sortie texte complète des deux coupures fait ≈ 250 lignes chacune ;
la relancer plutôt que la recopier.
