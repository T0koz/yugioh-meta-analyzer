# Charte « ton et explication »

Lot 15, étape 1 (2026-11-17). Statut : **à valider par Thomas** (formulaire en fin de document). Rien n'est appliqué
au site avant validation. Le lot 16 (réécriture des textes) et l'étape 2 (composants) s'appuient sur ce document.
Décision de départ : `docs/decisions/0034-…` (ton sobre, statistique, l'explication passe par le graphique).

## 1. Ton

- Un texte est un **constat chiffré** : une mesure, une période, une source. Sans les trois, la phrase disparaît.
- Jamais de promesse ni de conseil. Le site décrit ce qui a été mesuré, il ne dit pas quoi acheter, jouer ou croire.
- Pas d'impératif adressé au lecteur (« regarde », « essaie »), pas de vouvoiement commercial, pas de point
  d'exclamation, pas de question rhétorique dans un titre.
- Les limites s'écrivent au même endroit que le résultat, avec la même taille de police. Un résultat mauvais
  (listes TCG de septembre et octobre 2026, signal boutique de juin 2026) reste visible.
- Les mots du lecteur avant les noms de colonnes : « part des decks », pas `meta_score` ; une variable de code
  n'apparaît que dans la page Méthode.
- Titres : une idée, un mot en `<Em>`, descriptifs. Ils sont dispensés de chiffre si l'eyebrow ou l'intro le porte
  (question 6 du formulaire).

Registre visé, résumé avec nos mots :
- **Our World in Data** : chaque graphique a sa source, sa date et un onglet de données ; la méthode est à un clic,
  jamais dans le graphique.
- **FT et Bloomberg** : le titre énonce le constat, le graphique le montre, une ou deux annotations posées sur la
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
5. **Pied de données** (`DataFooter`) : source, date, échantillon, et une ligne de lecture si nécessaire.
6. **Couche « Méthode » repliée** : un `<details>` en bas de bloc, renvoyant à `/methode#…`.

L'infobulle `InfoTooltip` sort de cet ordre : invisible au toucher, lue au survol seulement, elle cache aujourd'hui
des formules et des limites importantes (6 occurrences, annexe A). Recommandation : la supprimer (question 2).

## 3. Incertitude : règles

Le projet a déjà trois seuils mesurés. La charte les généralise sans en inventer d'autres que celui de la question 1.

| Situation | Règle | Appui existant |
|---|---|---|
| Une part ou un pourcentage s'affiche | toujours avec son effectif : « 15 sur 16 », « 38 decks sur 412 » | Decks : « k sur n » |
| Effectif d'un archétype sous 8 listes | pas de part calculée, on montre les listes | Decks : fiche dès 8 listes (9 à 13 % d'étiquettes instables à 8, 19 à 24 % à 5) |
| Fenêtre de backtest sous 600 decks | liste écartée, affichée comme écartée | `BACKTEST_MIN_DECKS` |
| Archétype sous 5 decks | classé Rogue, pas de tendance | tier list |
| Mois dont l'effectif total est faible | point et segment **atténués** (opacité réduite, trait pointillé), n écrit au survol et dans le tableau | seuil à fixer, question 1 |
| Mois en cours | dernier segment en pointillé, annotation « en cours, n = … » | page d'archétype (aujourd'hui en pied seulement) |
| Un intervalle est déjà calculé | il est **dessiné** par défaut, avec son niveau (« 80 % », « IC 95 % ») | r ≈ 0,53 de l'accueil (déjà conforme), fenêtre d'arrivée TCG |
| Aucun intervalle n'existe | le pied le dit et dit pourquoi | Prédictions (déjà conforme) |
| Score de classement sans échelle absolue | afficher un rang (« 4e sur 89 ») plutôt qu'un score relatif au premier | libellé boutique |
| Tests multiples | le nombre de faux positifs attendus s'écrit une fois, en Méthode | tendance de la tier list (≈ 3 sur 60 au seuil de 5 %) |

Ordre de grandeur pour la question 1 : l'erreur type d'une part de 10 % vaut 3 points à 100 decks, 4,2 points à
50 decks (√(p(1−p)/n)). L'intervalle à 95 % fait donc ±6 points à 100 decks, autant que l'écart entre T2 et T1.

## 4. Couche « Méthode » et page `/methode`

**Va dans la couche repliée de chaque bloc** : une à trois lignes, sans formule (fenêtre, population, seuil
appliqué), et un lien vers l'ancre de `/methode`.

**Va dans `/methode`** (une section par outil, même ordre que la navigation) : formules (`alert_score`, score de
tier, score de pont, Jaccard, mélange naïf + Ridge α = 50), sources et dates de collecte, seuils et leur origine
(8 listes, 600 decks, 10 % et 25 %), validations et leurs résultats, y compris les échecs, limites connues.
La page Méthode suit la même charte : un tableau ou un graphique par résultat de validation, pas de paragraphe
qui recopie un tableau.

## 5. Interdit

- Formule dans une infobulle, un titre, une intro ou une cellule.
- Pourcentage sans effectif ; graphique sans source ni date ; intervalle calculé mais caché.
- Promesse (« avant tout le monde », « les cartes qui montent »), conseil (« à croiser avec »), impératif, question
  rhétorique, point d'exclamation, superlatif non mesuré.
- Texte qui répète ce que le graphique montre déjà.
- Image de chiffres : tout chiffre est du texte HTML, lisible par un lecteur d'écran.
- Scène ou personnage de l'anime ; illustration de carte présentée comme une donnée.

## 6. Dix exemples avant / après

« Avant » cité depuis `frontend/src/` (branche `claude/front-nuit-17-11`). Les chiffres de l'« après » sont ceux
que le site affiche déjà ; les variables entre accolades sont servies par l'API.

| # | Avant | Après |
|---|---|---|
| 1 | `app/tier-list/page.tsx:50` — infobulle de 5 phrases : seuils de tier, test de deux proportions, faux positifs, échelle de la barre, formule du score. | Seuils dessinés : graduations T3 3 %, T2 7 %, T1 15 %, T0 40 % sur l'axe des barres de part. Flèche de tendance seulement si le test passe. Le reste en couche Méthode : « Tendance : test de deux proportions à 5 % contre la fenêtre précédente, ≈ 3 faux positifs attendus sur 60 archétypes. » Formule du score → `/methode#tier-list`. |
| 2 | `app/predictions/page.tsx:49-50` — intro de 3 phrases (mélange, ce que le modèle n'anticipe pas) + infobulle (Ridge α = 50, validation glissante). | Intro : « Score méta ×100 de {n} archétypes TCG, observé en {mois}, prévu pour {mois + 1}. » Annotation sur l'axe : « erreur −5 % contre "rien ne change", validation glissante ». Le pied « aucun intervalle par archétype » reste. Modèle et α → Méthode. |
| 3 | `app/boutique/page.tsx:80` — infobulle « Score » : formule `alert_score`, filtre ≥ 3 cartes clés, r ≈ 0,53 et IC, échec de juin 2026. | Colonne renommée « Ordre » ou retirée (le score relatif au premier ne mesure rien, le libellé le fait). r ≈ 0,53 dessiné dans le hero : point + IC 95 % 0,43 à 0,59, composant repris de l'accueil. Juin 2026 en annotation datée sur ce graphique : « juin 2026 : −35 % contre −1 % pour le marché ». |
| 4 | `app/boutique/page.tsx:86` — infobulle « Arrivée TCG » : intervalle 8 fois sur 10, 75 à 202 jours, 1 897 cartes, non vérifié. | Dans la cellule, un segment début–fin sur une échelle de mois commune à toutes les lignes. En-tête : « Arrivée TCG · intervalle 80 % ». Pied : « délai mesuré sur 1 897 cartes, 2022 à 2025, non vérifié sur des cas nouveaux ». |
| 5 | `app/boutique/page.tsx:74` — infobulle « Signal » : rang, formule de classement, coupes à 10 % et 25 %. | La cellule montre déjà « 4e sur 89 ». Ajouter une jauge de rang de 89 positions avec deux graduations (10 %, 25 %). « Seuils provisoires, non validés hors échantillon » dans le pied ; formule → Méthode. |
| 6 | `app/boutique/page.tsx:55` — intro : « signal modéré, à croiser avec la banlist et le prix. La fenêtre d'arrivée est une estimation, pas une date. » | « Archétypes joués en OCG au {date}, dont au moins 3 cartes clés ne sont pas sorties en TCG : {n} cartes, {k} archétypes. » Le conseil disparaît ; l'incertitude de la fenêtre est portée par l'exemple 4. |
| 7 | `app/early-signals/page.tsx:39-46` — titre « Les cartes qui montent *avant* la méta. », intro sans chiffre, infobulle de composition du score. | Titre : « Cartes récentes, score de *0 à 100*. » Intro : « {n} cartes sorties depuis {date}, calcul du {date}. » Composition du score en barre empilée par composante, comme le Ban Radar, si l'API sert les composantes (à vérifier) ; sinon une ligne dans le pied. |
| 8 | `app/ban/BanRadarView.tsx:133-156` — encart de 5 paragraphes et une liste à puces sur le backtest. | Un graphique en points : rang médian des cartes touchées pour chacune des 20 listes rejouées, ligne du hasard (n/2) en repère, les listes TCG de septembre et octobre 2026 annotées. Reste une phrase : « Score de risque, pas une probabilité. » |
| 9 | `app/ban/BanSimulatorView.tsx:53` — « Retire une carte du graphe de synergies et regarde ce qui casse » ; `:81` « Essaie « Ash Blossom… » ». | « Effet du retrait d'une carte sur le graphe de co-occurrences : archétypes touchés, score de pont, fragmentation de sa communauté. » Erreur : « Carte absente de la table des cartes. » |
| 10 | `app/evolution/EvolutionChart.tsx:248-262` — bande des effectifs mensuels présente, mais les mois à faible effectif sont tracés comme les autres ; `app/archetype/[slug]/page.tsx:229` « le dernier mois est en cours » en pied seulement. | Mois sous le seuil (question 1) : point et segment atténués, n en annotation. Mois en cours : dernier segment en pointillé, annotation « en cours, n = {n} ». Le pied n'a plus à le dire. |

Déjà conformes, à prendre pour modèles : l'IC dessiné de la corrélation (`app/page.tsx:403-445`), la bande des
effectifs d'Évolution, les « k sur n » et le seuil de 8 listes des Decks, le pied de Prédictions qui dit l'absence
d'intervalle.

## 7. Pistes visuelles à arbitrer

| Piste | Apport pour l'explication | Risques | Recommandation |
|---|---|---|---|
| **Composition en couches** (inspirée de solidroad.com) : illustration devant un panneau de données vivant ; chemin OCG → TCG. | Moyen. Le chemin OCG → TCG peut porter le délai de 2 à 6 mois, à condition d'être un vrai axe de temps. L'illustration elle-même n'explique rien. | LCP si l'illustration est l'élément le plus grand du premier écran ; droits : illustrations de cartes Konami, à n'utiliser qu'en recadrage décoratif comme sur la tier list, jamais de scène ni de personnage de l'anime ; accessibilité : illustration `aria-hidden`, chiffres en HTML. | Oui, sur l'accueil seulement, après TOK-92 (images hébergées). Panneau de données en HTML ; illustration non `eager`, dimensions réservées, mesurée au Lighthouse. |
| **Hero animé local** (`frontend/public/local-hero/`, hors Git). | Nul en ligne : la vidéo n'y sera jamais. Le repli (courbes OCG / TCG) est la seule version publique, et c'est lui qui explique. | Vidéo lourde en local ; mouvement : image fixe obligatoire en mouvement réduit ; risque de deux accueils qui divergent. | Construire d'abord le repli comme graphique réel (courbes servies, délai annoté). Vidéo locale en option de démonstration, ensuite. |
| **clears.ai** (élément central). | Potentiel pour montrer un combo pas à pas, plus tard. Aucun lien avec la méta actuelle. | Pas de capture disponible ; aucune page ouverte, rien de vérifié. | Reporter au moteur de combos (TOK-59). Demander une capture à Thomas. |

## 8. Formulaire de validation

```
1. Seuil d'atténuation d'un mois dans les séries (Évolution, page d'archétype)
[ ] moins de 50 decks dans le mois
[x] moins de 100 decks dans le mois (IC 95 % d'une part de 10 % ≈ ±6 points) — à vérifier sur decks_by_month
[ ] moins de 200 decks dans le mois
[ ] pas d'atténuation, effectif affiché seulement

2. Infobulles InfoTooltip (6 aujourd'hui)
[x] supprimées : contenu réparti entre graphique, pied de données et /methode
[ ] gardées pour la définition d'un mot, une phrase, sans formule

3. Place des formules
[x] page /methode seulement, liée depuis une couche « Méthode » repliée sous chaque bloc
[ ] couche repliée de chaque bloc (formule visible sur la page, repliée)

4. Intervalles déjà calculés (corrélation OCG → TCG, fenêtre d'arrivée TCG)
[x] dessinés par défaut
[ ] repliés, affichés à la demande

5. Bande d'incertitude sur les parts mensuelles (intervalle de Wilson, à partir de k et n déjà servis)
[x] oui à l'étape 2, relue par la collaboratrice data scientist
[ ] plus tard
[ ] non : effectif seulement

6. Titres de page
[x] descriptifs, un mot en <Em>, sans chiffre si l'eyebrow porte la période et l'effectif ; ni question ni promesse
[ ] chaque titre porte une mesure
[ ] titres actuels conservés

7. Composition en couches sur l'accueil
[x] oui, après TOK-92, illustration décorative non LCP, données en HTML
[ ] non
[ ] à revoir après une maquette

8. Hero animé local
[x] repli « courbes OCG / TCG » d'abord, vidéo locale ensuite en option
[ ] vidéo locale d'abord
[ ] abandonné

Commentaire libre : ______________________________________________
```

---

## Annexe A — Inventaire (lecture de `frontend/src/`, 2026-11-17)

**6 infobulles** `InfoTooltip`, toutes sur des pages (aucune dans `nav.tsx`, qui n'a qu'un commentaire, l.157).
**8 formules ou notations techniques affichées** (5 dans des infobulles, 3 dans le texte courant).

| Fichier:ligne | Type | Problème |
|---|---|---|
| `app/early-signals/page.tsx:39` | titre | promesse (« qui montent avant la méta ») |
| `app/early-signals/page.tsx:44-45` | intro | aucune mesure, période ni effectif |
| `app/early-signals/page.tsx:46` | infobulle | composition du score cachée ; `alert_score` en nom de variable |
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
| `app/ban/BanRadarView.tsx:118` | titre | question rhétorique (« Qui sera banni ensuite ? ») |
| `app/ban/BanRadarView.tsx:133-162` | encart | 6 paragraphes de backtest qui pourraient être un graphique |
| `app/ban/CardImpactView.tsx:77` | texte, formule | formule du score de pont dans l'encart |
| `app/ban/BanSimulatorView.tsx:53` | intro | impératif, tutoiement (« regarde ce qui casse ») |
| `app/ban/BanSimulatorView.tsx:81` | message | impératif (« Essaie… ») |
| `app/ban/BanSimulatorView.tsx:128` | pied | date absente de la base servie (dit, conforme) |
| `app/graph/page.tsx:34` | intro, notation | « Jaccard ≥ » sans définition à portée de lecture |
| `app/page.tsx:338` | texte, notation | « centralité d'intermédiarité » sans renvoi à la méthode |
| `app/page.tsx:403-445` | graphique | IC de la corrélation dessiné : **modèle à suivre** |
| `app/decks/page.tsx:65, 173` | texte | « k sur n » et stabilité mesurée à 5 et 8 listes : **modèle à suivre** |

## Annexe B — Sources

Pages de référence : **aucune ouverte** pendant cette étape. Les principes attribués à Our World in Data, au FT, à
Bloomberg et à The Pudding sont résumés de mémoire et seront vérifiés sur leurs pages publiques à l'étape 2.
Documents du projet : `docs/planning/sprint-3/12-explication-graphique.md`, `docs/planning/2026-11-17/regles.md`,
`docs/design-system.md` §4 et §7, `docs/decisions/0034-…`, `0038-…`.
