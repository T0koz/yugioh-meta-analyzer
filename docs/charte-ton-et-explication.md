# Charte « ton et explication »

Lot 15, étape 1 (2026-11-17). Statut : **validée par Thomas le 17/11** (réponses au formulaire, §8). L'étape 2
(composants communs, page `/methode`) vient après les lots 11 et 12 ; le lot 16 (réécriture des textes) s'appuie
sur ce document. Décision de départ : `docs/decisions/0034-…` (ton sobre, statistique, l'explication passe par le
graphique).

## 1. Ton

- Un texte est un **constat chiffré** : une mesure, une période, une source. Sans les trois, la phrase disparaît.
- Jamais de promesse ni de conseil. Le site décrit ce qui a été mesuré, il ne dit pas quoi acheter, jouer ou croire.
- Pas d'impératif adressé au lecteur (« regarde », « essaie »), pas de vouvoiement commercial, pas de point
  d'exclamation.
- Les limites s'écrivent au même endroit que le résultat, avec la même taille de police. Un résultat mauvais
  (listes TCG de septembre et octobre 2026, signal boutique de juin 2026) reste visible.
- Les mots du lecteur avant les noms de colonnes : « part des decks », pas `meta_score`. Aucun nom de variable
  sur le site.
- **Titres** : une courte description, en langage simple, de ce que montre la page. Ni question ni promesse ; un
  chiffre n'est pas obligatoire. Un mot en `<Em>`, comme aujourd'hui.

Registre visé, résumé avec nos mots :
- **Our World in Data** : chaque graphique a sa source, sa date et un onglet de données ; la méthode est à un clic,
  jamais dans le graphique.
- **FT et Bloomberg** : le titre énonce ce qu'on voit, le graphique le montre, une ou deux annotations posées sur la
  courbe remplacent la légende ; peu de couleurs, la couleur désigne la série commentée.
- **The Pudding** : le récit avance par le défilement, le graphique change d'état plutôt que d'ajouter du texte.
  Repris seulement sur l'accueil (déjà en place pour Kewl Tune), pas sur les pages d'outil.

## 2. Ordre de préférence pour expliquer

On passe à l'étage suivant seulement si le précédent ne suffit pas.

1. **Encodage visuel** : position, longueur, ordre. Un seuil se dessine (graduation sur la barre), il ne s'écrit pas.
2. **Annotation sur le graphique** : un libellé court accroché au point concerné (« pic : avril 2026, 18 % »).
   Au plus deux par graphique.
3. **Incertitude dessinée** : intervalle, bande, effectif n, données faibles atténuées (§3).
4. **Légende sobre** : en ligne au-dessus du graphique, une entrée par marque, sans phrase.
5. **Infobulle de définition** (`InfoTooltip`) : une phrase qui fait comprendre un mot à une personne qui n'est ni
   développeuse ni mathématicienne. Jamais de formule, de seuil chiffré en série ni de résultat de validation.
   À l'étape 2, elle s'ouvre aussi au toucher et au clavier (aujourd'hui : survol et focus seulement).
6. **Pied de données** (`DataFooter`) : source, date, échantillon, et une ligne de lecture si nécessaire.
7. **Couche « Méthode » repliée** : un `<details>` en bas de bloc, renvoyant à `/methode#…`, sans formule.

**Formules : aucune n'est affichée sur le site**, ni dans une infobulle, ni dans le texte, ni dans `/methode`.
Elles restent dans le code et la documentation du dépôt.

## 3. Incertitude : règles

Le projet a déjà trois seuils mesurés ; la charte les généralise et ajoute celui des 100 decks.

| Situation | Règle | Appui existant |
|---|---|---|
| Une part ou un pourcentage s'affiche | toujours avec son effectif : « 15 sur 16 », « 38 decks sur 412 » | Decks : « k sur n » |
| Effectif d'un archétype sous 8 listes | pas de part calculée, on montre les listes | Decks : fiche dès 8 listes (9 à 13 % d'étiquettes instables à 8, 19 à 24 % à 5) |
| Fenêtre de backtest sous 600 decks | liste écartée, affichée comme écartée | `BACKTEST_MIN_DECKS` |
| Archétype sous 5 decks | classé Rogue, pas de tendance | tier list |
| **Mois de moins de 100 decks** (tous archétypes confondus) | point et segment **en pointillé et plus pâles** ; nombre de decks au survol et dans le tableau | validé le 17/11 |
| Mois en cours | dernier segment en pointillé, annotation « en cours, n = … » | page d'archétype (aujourd'hui en pied seulement) |
| Un intervalle est déjà calculé | **dessiné par défaut**, avec son niveau (« 80 % », « IC 95 % ») | r ≈ 0,53 de l'accueil (déjà conforme), fenêtre d'arrivée TCG |
| Part mensuelle d'un archétype | bande d'incertitude à 95 % (intervalle de Wilson, à partir de k et n déjà servis), sans formule affichée ; **calcul relu par la collaboratrice data scientist avant mise en ligne** | validé le 17/11, étape 2 |
| Aucun intervalle n'existe | le pied le dit et dit pourquoi | Prédictions (déjà conforme) |
| Score de classement sans échelle absolue | afficher un rang (« 4e sur 89 ») plutôt qu'un score relatif au premier | libellé boutique |
| Tests multiples | le nombre de faux positifs attendus s'écrit une fois, dans `/methode` | tendance de la tier list (≈ 3 sur 60 au seuil de 5 %) |

Pourquoi 100 decks : l'erreur type d'une part de 10 % vaut 3 points à 100 decks et 4,2 points à 50. L'intervalle à
95 % fait donc environ ±6 points à 100 decks, autant que l'écart entre T2 et T1. Le nombre de mois concernés est
à relever sur `decks_by_month` à l'étape 2.

## 4. Couche « Méthode » et page `/methode`

**Couche repliée de chaque bloc** : une à trois lignes en langage simple (fenêtre, population, seuil appliqué) et
un lien vers l'ancre de `/methode`.

**Page `/methode`, sans formule** (une section par outil, même ordre que la navigation) : sources et dates de
collecte ; seuils et leur origine (8 listes, 600 decks, 100 decks, 10 % et 25 %) ; résultats des validations,
**échecs compris** (listes TCG de septembre et octobre 2026, signal de juin 2026) ; limites connues. Chaque
méthode y est décrite par ce qu'elle mesure (« le score rapproche chaque carte du profil des cartes déjà
touchées »), jamais par son équation. Un résultat de validation se montre en tableau ou en graphique, pas en
paragraphe.

## 5. Interdit

- Toute formule affichée, où que ce soit sur le site.
- Infobulle qui dépasse une phrase de définition, ou qui contient une formule, un nom de variable, une série de
  seuils ou un résultat de validation.
- Pourcentage sans effectif ; graphique sans source ni date ; intervalle calculé mais caché.
- Promesse (« avant tout le monde », « les cartes qui montent »), conseil (« à croiser avec »), impératif, question
  dans un titre, point d'exclamation, superlatif non mesuré.
- Texte qui répète ce que le graphique montre déjà.
- Image de chiffres : tout chiffre est du texte HTML, lisible par un lecteur d'écran.
- Scène ou personnage de l'anime ; illustration de carte présentée comme une donnée.

## 6. Dix exemples avant / après

« Avant » cité depuis `frontend/src/` (branche `claude/front-nuit-17-11`). Les chiffres de l'« après » sont ceux
que le site affiche déjà ; les variables entre accolades sont servies par l'API.

| # | Avant | Après |
|---|---|---|
| 1 | `app/tier-list/page.tsx:50` — infobulle de 5 phrases : seuils de tier, test de deux proportions, faux positifs, échelle de la barre, formule du score. | Seuils dessinés : graduations T3 3 %, T2 7 %, T1 15 %, T0 40 % sur l'axe des barres de part. Infobulle « Tier » : « Niveau de l'archétype selon la part des decks de tournoi qui le jouent. » Flèche de tendance seulement si le test passe ; test et faux positifs attendus dans `/methode`. Formule du score retirée. |
| 2 | `app/predictions/page.tsx:44-50` — titre « La méta du mois *prochain*. », intro de 3 phrases, infobulle (Ridge α = 50, validation glissante). | Titre : « Le score de chaque archétype, *prévu* pour le mois suivant. » Intro : « Score méta ×100 de {n} archétypes TCG, observé en {mois}, prévu pour {mois + 1}. » Infobulle « Prévision » : « Valeur attendue si la situation récente se prolonge, en ramenant les écarts vers la moyenne. » Annotation : « erreur −5 % contre "rien ne change" ». Le pied « aucun intervalle par archétype » reste. |
| 3 | `app/boutique/page.tsx:80` — infobulle « Score » : formule `alert_score`, filtre ≥ 3 cartes clés, r ≈ 0,53 et IC, échec de juin 2026. | Infobulle : « Ordre d'affichage dans la liste : le premier vaut 100. Ce n'est pas une force de signal. » r ≈ 0,53 dessiné dans le hero : point + IC 95 % 0,43 à 0,59, composant repris de l'accueil. Juin 2026 en annotation datée : « juin 2026 : −35 % contre −1 % pour le marché ». Formule retirée. |
| 4 | `app/boutique/page.tsx:86` — infobulle « Arrivée TCG » : intervalle 8 fois sur 10, 75 à 202 jours, 1 897 cartes, non vérifié. | Dans la cellule, un segment début–fin sur une échelle de mois commune à toutes les lignes, libellé « 80 % ». Infobulle : « Période où l'archétype est arrivé en TCG 8 fois sur 10 par le passé. » Pied : « délai mesuré sur 1 897 cartes, 2022 à 2025, non vérifié sur des cas nouveaux ». |
| 5 | `app/boutique/page.tsx:74` — infobulle « Signal » : rang, formule de classement, coupes à 10 % et 25 %. | La cellule montre déjà « 4e sur 89 ». Jauge de rang de 89 positions avec deux graduations (10 %, 25 %). Infobulle : « Place de l'archétype parmi les 89 archétypes suivis en OCG. » « Seuils provisoires, non validés hors échantillon » dans le pied. |
| 6 | `app/boutique/page.tsx:52-55` — titre « Les cartes à surveiller *avant* le TCG. » ; intro : « signal modéré, à croiser avec la banlist et le prix. » | Titre : « Cartes jouées en OCG, *pas encore* sorties en TCG. » Intro : « Archétypes joués en OCG au {date}, dont au moins 3 cartes clés ne sont pas sorties en TCG : {n} cartes, {k} archétypes. » Le conseil disparaît. |
| 7 | `app/early-signals/page.tsx:39-46` — titre « Les cartes qui montent *avant* la méta. », intro sans chiffre, infobulle de composition du score. | Titre : « Les cartes récentes et leur *place* dans les decks. » Intro : « {n} cartes, calcul du {date}. » Infobulle « Score » : « Note de 0 à 100 : plus elle est haute, plus la carte est consultée et jouée avec les decks du moment. » Composition en barre empilée, comme le Ban Radar, si l'API sert les composantes (à vérifier). |
| 8 | `app/ban/BanRadarView.tsx:118-156` — titre « Qui sera *banni* ensuite ? » ; encart de 5 paragraphes et une liste sur le backtest. | Titre : « Les cartes qui ressemblent le plus aux cartes déjà *bannies*. » Graphique en points : rang médian des cartes touchées pour chacune des 20 listes rejouées, ligne du hasard en repère, listes TCG de septembre et octobre 2026 annotées. Reste une phrase : « Score de risque, pas une probabilité. » |
| 9 | `app/ban/BanSimulatorView.tsx:53` — « Retire une carte du graphe de synergies et regarde ce qui casse » ; `:81` « Essaie « Ash Blossom… » ». `app/ban/CardImpactView.tsx:77` : formule du score de pont. | « Effet du retrait d'une carte sur le graphe de co-occurrences : archétypes touchés, score de pont, fragmentation de sa communauté. » Erreur : « Carte absente de la table des cartes. » Infobulle « Score de pont » : « Plus il est haut, plus la carte relie des archétypes différents. » Formule retirée. |
| 10 | `app/evolution/EvolutionChart.tsx:248-262` — bande des effectifs mensuels présente, mais les mois de faible effectif sont tracés comme les autres ; `app/archetype/[slug]/page.tsx:229` « le dernier mois est en cours » en pied seulement. | Mois de moins de 100 decks : point et segment en pointillé et plus pâles, nombre de decks au survol. Mois en cours : dernier segment en pointillé, annotation « en cours, n = {n} ». Le pied n'a plus à le dire. |

Déjà conformes, à prendre pour modèles : l'IC dessiné de la corrélation (`app/page.tsx:403-445`), la bande des
effectifs d'Évolution, les « k sur n » et le seuil de 8 listes des Decks, le pied de Prédictions qui dit l'absence
d'intervalle.

## 7. Pistes visuelles (arbitrées le 17/11)

| Piste | Décision de Thomas | Ce qui en découle |
|---|---|---|
| **Composition en couches** (inspirée de solidroad.com) : illustration devant un panneau de données vivant ; chemin OCG → TCG. | **Après une maquette.** | Maquette d'abord, décision ensuite ; rien à l'étape 2 sans validation de la maquette. Contraintes à respecter dans la maquette : données en HTML, illustration `aria-hidden` et non LCP, jamais de scène ni de personnage de l'anime, illustrations de cartes seulement en recadrage décoratif et après TOK-92. |
| **Hero animé local** (`frontend/public/local-hero/`, hors Git). | **Repli en courbes OCG / TCG d'abord**, vidéo locale ensuite en option. | Le repli est la seule version publique : un graphique réel (courbes servies, délai annoté), image fixe en mouvement réduit. La vidéo ne va jamais dans Git ni en ligne. |

## 8. Formulaire de validation (réponses de Thomas, 17/11 vers 0 h 20)

```
1. Seuil d'atténuation d'un mois dans les séries (Évolution, page d'archétype)
[ ] moins de 50 decks dans le mois
[x] moins de 100 decks dans le mois : pointillé, plus pâle, nombre de decks au survol
[ ] moins de 200 decks dans le mois
[ ] pas d'atténuation, effectif affiché seulement

2. Infobulles InfoTooltip
[ ] supprimées
[x] gardées, seulement pour une courte définition compréhensible par une personne non technique ; aucune formule ;
    ouverture au toucher et au clavier à l'étape 2

3. Place des formules
[x] cachées pour le moment : aucune formule affichée sur le site
[ ] page /methode seulement
[ ] couche repliée de chaque bloc
3 bis. Page /methode : gardée, sans formule (sources, dates, seuils, résultats des validations, échecs compris)

4. Intervalles déjà calculés (corrélation OCG → TCG, fenêtre d'arrivée TCG)
[x] dessinés par défaut
[ ] repliés, affichés à la demande

5. Bande d'incertitude sur les parts mensuelles (intervalle de Wilson, à partir de k et n déjà servis)
[x] oui à l'étape 2, calcul relu par la collaboratrice data scientist avant mise en ligne
[ ] plus tard
[ ] non : effectif seulement

6. Titres de page
[x] sans question ni promesse : une courte description de ce que montre la page, en langage simple
[ ] chaque titre porte une mesure
[ ] titres actuels conservés

7. Composition en couches sur l'accueil
[ ] oui, après TOK-92
[ ] non
[x] après une maquette

8. Hero animé local
[x] repli « courbes OCG / TCG » d'abord, vidéo locale ensuite en option
[ ] vidéo locale d'abord
[ ] abandonné

Commentaire libre : idée pour plus tard, « un outil qui permet d'inspecter la donnée d'un point de vue
mathématique » (voir §9).
```

## 9. Pistes pour plus tard (non planifiées)

- **Outil d'inspection mathématique** (idée de Thomas, 17/11) : un espace séparé où l'on peut inspecter la donnée
  d'un point de vue mathématique (formules, distributions, effectifs bruts). C'est le seul endroit où des formules
  pourraient réapparaître ; à concevoir comme un outil à part, pas comme une couche des pages actuelles.
- **clears.ai** (élément central) : idée pour représenter un combo pas à pas, à rattacher au moteur de combos
  (TOK-59). Capture à demander à Thomas ; rien n'a été vérifié.

---

## Annexe A — Inventaire (lecture de `frontend/src/`, 2026-11-17)

**6 infobulles** `InfoTooltip`, toutes sur des pages (aucune dans `nav.tsx`, qui n'a qu'un commentaire, l.157).
**8 formules ou notations techniques affichées** (5 dans des infobulles, 3 dans le texte courant). Avec la charte
validée, les 6 infobulles sont gardées mais réécrites en une phrase de définition, et les 8 formules sont retirées.

| Fichier:ligne | Type | Problème |
|---|---|---|
| `app/early-signals/page.tsx:39` | titre | promesse (« qui montent avant la méta ») |
| `app/early-signals/page.tsx:44-45` | intro | aucune mesure, période ni effectif |
| `app/early-signals/page.tsx:46` | infobulle | composition du score au lieu d'une définition ; `alert_score` en nom de variable |
| `app/early-signals/page.tsx:51-84` | tableau | score sans décomposition ni effectif de co-occurrence |
| `app/boutique/page.tsx:52` | titre | consigne implicite (« à surveiller ») |
| `app/boutique/page.tsx:55` | intro | conseil (« à croiser avec la banlist et le prix ») |
| `app/boutique/page.tsx:74` | infobulle, formule | formule de classement ; seuils 10 % / 25 % non dessinés |
| `app/boutique/page.tsx:80` | infobulle, formule | `alert_score = …` ; r et IC, échec de juin 2026 cachés au survol |
| `app/boutique/page.tsx:86` | infobulle | intervalle 80 % écrit, non dessiné |
| `app/boutique/page.tsx:122` | cellule | score relatif au premier du lot, sans échelle absolue |
| `app/tier-list/page.tsx:50` | infobulle, formule | seuils, test multiple et formule du score réunis au survol |
| `app/tier-list/ArchetypeRow.tsx:104` | barre | part relative au max, seuils de tier non dessinés |
| `app/predictions/page.tsx:44` | titre | promesse (« la méta du mois prochain ») |
| `app/predictions/page.tsx:49` | intro | trois phrases de méthode dans l'intro |
| `app/predictions/page.tsx:50` | infobulle, formule | Ridge α = 50, validation glissante |
| `app/predictions/PredictionsChart.tsx` | graphique | aucun intervalle ; le pied le dit (conforme) |
| `app/evolution/EvolutionChart.tsx:248-262` | graphique | effectif mensuel dessiné (bien) ; mois faibles non atténués ; pas de bande |
| `app/archetype/[slug]/ShareChart.tsx` | graphique | k sur n au survol (bien) ; mois en cours non distingué sur le tracé |
| `app/archetype/[slug]/page.tsx:229` | pied | « dernier mois en cours » écrit au lieu d'être dessiné |
| `app/ban/BanRadarView.tsx:118` | titre | question (« Qui sera banni ensuite ? ») |
| `app/ban/BanRadarView.tsx:133-162` | encart | 6 paragraphes de backtest qui pourraient être un graphique |
| `app/ban/CardImpactView.tsx:77` | texte, formule | formule du score de pont dans l'encart |
| `app/ban/BanSimulatorView.tsx:53` | intro | impératif, tutoiement (« regarde ce qui casse ») |
| `app/ban/BanSimulatorView.tsx:81` | message | impératif (« Essaie… ») |
| `app/ban/BanSimulatorView.tsx:128` | pied | date absente de la base servie (dit, conforme) |
| `app/graph/page.tsx:34` | intro, notation | « Jaccard ≥ » : notation à remplacer par « souvent jouées dans les mêmes decks » |
| `app/page.tsx:338` | texte, notation | « centralité d'intermédiarité » : à remplacer par une définition simple |
| `app/page.tsx:403-445` | graphique | IC de la corrélation dessiné : **modèle à suivre** |
| `app/decks/page.tsx:65, 173` | texte | « k sur n » et stabilité mesurée à 5 et 8 listes : **modèle à suivre** |

## Annexe B — Sources

Pages de référence : **aucune ouverte** pendant cette étape. Les principes attribués à Our World in Data, au FT, à
Bloomberg et à The Pudding sont résumés de mémoire et seront vérifiés sur leurs pages publiques à l'étape 2.
Documents du projet : `docs/planning/sprint-3/12-explication-graphique.md`, `docs/planning/2026-11-17/regles.md`,
`docs/design-system.md` §4 et §7, `docs/decisions/0034-…`, `0038-…`.
