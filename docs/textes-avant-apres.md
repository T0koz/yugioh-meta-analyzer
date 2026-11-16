# Textes du site : avant / après (lot 16)

Lot 16, première moitié (2026-11-17, branche `claude/lot16-reecriture-textes-9d97ee`). **Aucun texte du site n’est
modifié dans ce lot** : ce document est à valider par Thomas, l’application vient dans une session suivante.

Références : `docs/charte-ton-et-explication.md` (validée le 17/11, formulaire §8), consigne de ton du 16/11
(`docs/planning/2026-11-17/regles.md`), brief `docs/planning/sprint-3/13-reecriture-textes.md`. Vocabulaire des joueurs
gardé : « Tier list », « Ban Radar », « staples », « Ban Center », « decklists ».

## 1. Formulaire de validation

```
1. Propositions de ce tableau (lignes T01 à T43)
[x] appliquer toutes les propositions, sauf les pages refusées en 2 et les exceptions en 3
[ ] n’appliquer que les titres et les intros (T01 à T08, T13, T14, T17, T18, T23, T24, T30, T33, T34, T38 à T41)
[ ] ne rien appliquer, reprendre le tableau

2. Pages refusées (cocher pour garder les textes actuels de la page)
[ ] refuser la page « Accueil »
[ ] refuser la page « Tier list »
[ ] refuser la page « Évolution »
[ ] refuser la page « Prédictions »
[ ] refuser la page « Ban Center, commun »
[ ] refuser la page « Ban Radar »
[ ] refuser la page « Cartes à impact »
[ ] refuser la page « Simulateur »
[ ] refuser la page « Signaux précoces »
[ ] refuser la page « Graphe de synergies »
[ ] refuser la page « Page d’archétype »
[ ] refuser la page « Commun (erreurs, 404, pied de page) »

3. Exceptions texte par texte (numéro de ligne + décision, ex. « T04 : garder "précède" », « T19 : garder "Ubiquité" ») :
.....................................................................................................

4. Titre de l’accueil (T03, T04, T01, T02) — décision séparée, c’est la phrase la plus visible du site
[x] « La méta OCG, comparée à la méta TCG 2 à 6 mois plus tard. » (décrit ce que montre la page, sans antériorité affirmée)
[ ] garder « La méta OCG précède la méta TCG de 2 à 6 mois. »
[ ] autre : .........................................

5. Script de mots interdits (scripts/check_copy.py)
[x] bloquant (--strict dans check.py) dès que les textes validés sont appliqués
[ ] reste un avertissement

6. Textes du Ban Radar qui jugent le score (lignes B01 à B28, § 4)
[x] en attente du formulaire TOK-115 : rien n’est appliqué avant la décision de Thomas sur le diagnostic
[ ] appliquer les formulations proposées (tirées de la relecture) en même temps que le reste

Commentaire libre : .....................................................................................
```

## 2. Bilan

| Page | Textes relevés | Conformes | À changer | En attente TOK-115 |
|---|---:|---:|---:|---:|
| Accueil (/) | 75 | 61 | 5 | 9 |
| Tier list (/tier-list) | 26 | 19 | 7 | 0 |
| Évolution (/evolution) | 31 | 30 | 1 | 0 |
| Prédictions (/predictions) | 38 | 37 | 1 | 0 |
| Ban Center, commun (/ban) | 20 | 18 | 2 | 0 |
| Ban Radar (/ban, onglet Radar) | 32 | 15 | 6 | 11 |
| Historique (/ban?tab=historique) | 70 | 66 | 0 | 4 |
| Cartes à impact (/ban?tab=impact) | 18 | 11 | 7 | 0 |
| Simulateur (/ban?tab=simulateur) | 16 | 13 | 3 | 0 |
| Signaux boutique (/boutique) | 65 | 65 | 0 | 0 |
| Signaux précoces (/early-signals) | 18 | 16 | 2 | 0 |
| Graphe de synergies (/graph) | 18 | 16 | 2 | 0 |
| Decks, index (/decks) | 30 | 30 | 0 | 0 |
| Fiche de deck (/decks/{slug}) | 57 | 57 | 0 | 0 |
| Page d'archétype (/archetype/{slug}) | 90 | 89 | 1 | 0 |
| Méthode (/methode) | 171 | 167 | 0 | 4 |
| Commun : navigation, pied de page, erreurs, composants | 71 | 65 | 6 | 0 |
| **Total** | **846** | **775** | **43** | **28** |

- **Méthode d’extraction** : `python scripts/check_copy.py --dump` relève les nœuds texte JSX et les chaînes qui
  ressemblent à une phrase dans `frontend/src/` (titres, intros, `metadata` et `pageMetadata`, textes des
  `opengraph-image`, navigation, boutons, infobulles, légendes et annotations, pieds de données, états vides, chargement,
  `error.tsx`, `not-found.tsx`). Le titre de l’accueil (tableau de mots `TITLE`) a été ajouté à la main. Un texte JSX
  coupé par une expression (`{n}`) apparaît en plusieurs morceaux : la proposition donne alors le gabarit entier, avec
  un exemple rendu quand le chiffre est connu. Quelques lignes techniques relevées par l’heuristique (messages d’erreur
  de développement, valeurs CSS) restent dans le tableau, marquées « hors charte ».
- **Pages déjà conformes** : Signaux boutique, Decks (index et fiche) et presque toute la page Méthode ont été réécrits
  aux lots 11, 9 et 15 selon la charte ; aucun changement proposé.
- **Chiffres** : aucune proposition n’ajoute de chiffre que le site n’affiche pas déjà ou que l’API ne sert pas
  (`{n}`, `{n_decks}`, `{période}` sont servis par l’endpoint de la page) ; le seuil de 15 % du graphe et les 6 mois
  du Ban Radar sont déjà écrits ailleurs sur le site. Les chiffres des lignes B viennent de
  `docs/journal/ban-radar-tcg-relecture.md`.

### Les 10 changements les plus importants

1. **T03/T04 Accueil, titre** : « La méta OCG précède la méta TCG de 2 à 6 mois » → « La méta OCG, comparée à la méta TCG
   2 à 6 mois plus tard » (une corrélation de 0,53 ne prouve pas l’antériorité).
2. **T17 Ban Radar, titre** : « Qui sera banni ensuite ? » → « Les cartes qui ressemblent le plus aux cartes déjà bannies. »
3. **T18 Ban Radar, intro** : « les plus exposées à la prochaine banlist » → effectif de cartes, de decks et fenêtre de 6 mois.
4. **T14 Prédictions, titre** : « La méta du mois prochain » → « Le score de chaque archétype, prévu pour le mois suivant. »
5. **T33/T34 Signaux précoces** : « Les cartes qui montent avant la méta » → « Les cartes récentes et leur place dans les
   decks », intro avec effectif et date.
6. **T06/T07 Tier list** : « Ce que joue la méta, maintenant » et « nos decklists » → titre descriptif, intro avec
   effectif, période et source.
7. **T09 à T12 Tier list, bandeau** : 23 948 decklists (tous formats) et la corrélation OCG → TCG remplacés par
   l’effectif réel de la fenêtre et le nombre d’archétypes classés.
8. **T23/T24/T29 Cartes à impact** : « tiennent la méta », « fragmenterait », « trustent » → titre et intro mesurés.
9. **T30 Simulateur, titre** : « Et si Konami la bannissait ? » → « Le graphe de co-occurrences sans une carte. »
10. **T38 à T42 Erreur et 404** : « réessaie », « Voir la tier list », jeux de mots → constats courts, sans impératif.

## 3. Sortie actuelle du script de mots interdits

`python scripts/check_copy.py` (non bloquant dans `check.py` pour l’instant, `--strict` pour le rendre bloquant) :

```
  app/ban/BanRadarView.tsx:119  [promesse] « Qui sera »  —  Qui sera banni ensuite ?
  app/ban/BanRadarView.tsx:119  [question] « ? »  —  Qui sera banni ensuite ?
  app/ban/BanRadarView.tsx:134  [question] « ? »  —  Comment lire ce score ?
  app/ban/BanRadarView.tsx:159  [superlatif] « trustent »  —  Les staples génériques trustent le haut du classement complet parce qu’elles sont jouées partout à 3 exempl…
  app/ban/BanSimulatorView.tsx:50  [question] « ? »  —  Et si Konami la bannissait ?
  app/ban/CardImpactView.tsx:68  [question] « ? »  —  Comment lire ce score ?
  app/ban/CardImpactView.tsx:83  [superlatif] « trustent »  —  Les staples génériques trustent le haut du classement parce qu’elles sont jouées par le plus d’archétypes à…
  app/early-signals/page.tsx:40  [promesse] « qui montent »  —  Les cartes qui montent avant la méta.
  app/error.tsx:30  [appel à l'action] « réessaie »  —  L’API n’a pas répondu ou a renvoyé une erreur. Le reste du site n’est pas touché : réessaie dans un instant.
  app/evolution/page.tsx:34  [promesse] « Qui monte »  —  Qui monte, qui s’efface .
  app/not-found.tsx:24  [appel à l'action] « Voir la »  —  Voir la tier list
  app/predictions/page.tsx:45  [promesse] « mois prochain »  —  La méta du mois prochain .
  lib/ban-criteria.ts:8  [superlatif] « indispensable »  —  La carte est indispensable à un archétype qui pèse dans la méta.
Textes lus : 848 ; occurrences : 13 (promesse 4, question 4, superlatif 3, appel à l'action 2)
```

Toutes ces occurrences ont une proposition dans le tableau (T et B). Règles du script, tirées de la charte §1 et §5 :
appels à l’action et impératifs (« regarde », « essaie », « découvre », « voir la », « réessaie », « agir »…), conseils
(« à surveiller », « à croiser »), promesses (« avant la méta », « qui montent », « qui sera », « mois prochain »,
« garanti »…), superlatifs et termes forts non mesurés (« meilleur » employé seul, « indispensable », « puissant »,
« trustent »…), vouvoiement et tutoiement, point d’exclamation (hors « Yu-Gi-Oh! »), question en fin de texte,
notations de formule et noms de variables (`≥`, `α`, `snake_case`, « Ridge », « Jaccard », `x = y`…). Un faux positif se
déclare dans `ALLOW`, jamais en affaiblissant une règle.

## 4. Textes du Ban Radar en attente du formulaire TOK-115

Ces textes jugent la qualité du score. Ils attendent la décision de Thomas sur le diagnostic
(`docs/journal/ban-radar-tcg-diagnostic.md`) et sa relecture (`docs/journal/ban-radar-tcg-relecture.md`, verdict
« valide avec réserves », question 5 : texte proposé par le data scientist). **Rien n’est appliqué** ; les formulations
ci-dessous reprennent les chiffres de la relecture, mis en forme selon la charte (effectif, période, « écart non établi »
quand le test du signe ne conclut pas). Le bloc « Ban Radar rejoué » de l’accueil n’était pas cité dans le brief : il est
ajouté ici parce qu’il présente 4 listes choisies sur 20 comme lecture du score.

| # | Page | Fichier:ligne | Texte actuel | Pourquoi en attente | Formulation proposée (tirée de la relecture) |
|---|---|---|---|---|---|
| B01 | Accueil | `app/page.tsx:457` | Ban Radar rejoué sur les banlists passées | titre du même bloc | « Ban Radar rejoué sur 20 banlists passées » |
| B02 | Accueil | `app/page.tsx:459` | Rang médian, dans le classement calculé la veille de la banlist, des cartes ensuite restreintes. Trait vertical : rang attendu au hasard (milieu du classement). | bloc « Ban Radar rejoué » de l’accueil : il montre 4 listes sur 20 choisies, et en tire une lecture de la qualité du score (non listé dans le brief, ajouté ici par prudence) | Remplacer le tableau de 4 listes par le bilan par format, tiré de la relecture TOK-115 : « Top 25 de la veille, 10 banlists TCG d’avril 2024 à octobre 2026 : 29 cartes touchées sur 250 places, contre 16 pour le classement par part des decks. » + même ligne OCG (41 contre 18). Lien vers l’onglet Historique. |
| B03 | Accueil | `app/page.tsx:464` | Rang médian des cartes touchées, pour quatre banlists rejouées | légende du même tableau | supprimée avec le tableau de 4 listes |
| B04 | Accueil | `app/page.tsx:467` | Banlist | en-têtes du tableau de 4 listes (Banlist, Rang médian…, Au hasard, Cartes classées) | supprimés avec le tableau |
| B05 | Accueil | `app/page.tsx:468` | Rang médian des cartes touchées | en-tête du tableau de 4 listes | supprimé avec le tableau |
| B06 | Accueil | `app/page.tsx:469` | Au hasard | en-tête du tableau de 4 listes | supprimé avec le tableau |
| B07 | Accueil | `app/page.tsx:470` | Cartes classées | en-tête du tableau de 4 listes | supprimé avec le tableau |
| B08 | Accueil | `app/page.tsx:504` | Top 10 du radar sur {…} banlists TCG (avril 2024 à octobre 2026) : {…} places sur 100 suivies d’une restriction pour les pièces d’archétype, {…} sur 100 pour les staples génériques. | comparaison top 10 pièces d’archétype / staples : chiffres exacts, mais présentée comme une preuve du score | remplacée par la ligne top 25 ci-dessus (même source, comparée à la base staples comme le demande la relecture) |
| B09 | Accueil | `app/page.tsx:507` | Source : backtest du {…}, {…} des {…} listes rejouées (les deux de référence et les deux plus récentes en TCG). Poids du score réglés sur la liste TCG de mai 2026. Trait : milieu du classement ; la bande du hasard à 90 % est dans l’historique du Ban Center. | pied du même bloc | « Source : backtest du 16 novembre 2026, 20 listes rejouées (10 TCG, 10 OCG), banlists Yugipedia. Poids du score réglés sur la liste TCG de mai 2026. » |
| B10 | Ban Radar | `app/ban/BanRadarView.tsx:134` | Comment lire ce score ? | libellé de l’encart : question ; l’encart entier juge la qualité du score | « Lecture du score » (le libellé suit l’encart) |
| B11 | Ban Radar | `app/ban/BanRadarView.tsx:136` | C’est un score de risque , pas une probabilité : il classe les cartes par ressemblance au profil de celles que Konami a historiquement touchées. Il ne dit pas « X % de chances d’être bannie ». | 1er paragraphe : définition (risque, pas probabilité) ; conforme sur le fond, mais dans l’encart en attente | « Score de risque, pas une probabilité : il classe les cartes par ressemblance au profil des cartes déjà touchées par Konami. » (la phrase « X % de chances » disparaît : elle répète la précédente) |
| B12 | Ban Radar | `app/ban/BanRadarView.tsx:140` | Rejoué la veille des banlists passées (listes dont la fenêtre compte au moins 600 decks : dix en TCG, dix en OCG) : | liste de 3 résultats choisis et paragraphe de backtest : la charte §6 ex. 8 veut un graphique, la relecture TOK-115 un verdict avec effectifs | Remplacer la liste par le verdict de la relecture, adapté à la charte : « Sur les 10 banlists TCG d’avril 2024 à octobre 2026, 29 cartes touchées dans le top 25 de la veille (sur 250 places), contre 16 pour le classement par part des decks ; écart non établi (6 listes pour, 1 contre, 3 égalités). Rang médian meilleur sur 3 listes sur 10. En OCG : 41 contre 18 (9 listes sur 10), rang médian meilleur sur 8 listes sur 10. » + lien vers l’onglet Historique. |
| B13 | Ban Radar | `app/ban/BanRadarView.tsx:143` | TCG, 18 mai 2026 : rang médian 84 sur 889 cartes notées pour les cartes réellement touchées (le hasard donnerait environ 445). | élément de la liste de 3 résultats | supprimé (remplacé par le verdict ci-dessus) |
| B14 | Ban Radar | `app/ban/BanRadarView.tsx:147` | OCG, 1er juillet 2026 : rang médian 19 sur 1 236. Le score n’a jamais été calibré sur l’OCG : c’est un test hors distribution, et il y réussit mieux qu’en TCG. | élément de la liste ; « il y réussit mieux » : jugement | supprimé (remplacé par le verdict ci-dessus) |
| B15 | Ban Radar | `app/ban/BanRadarView.tsx:151` | TCG, 21 septembre et 19 octobre 2026 : les deux listes les plus récentes sont mauvaises (rang médian 206 sur 981, puis 308 sur 905, proche du hasard). Le haut du classement tient, mais la liste d’octobre touche 43 cartes dont beaucoup de marginales, et le méta Genesys, exclu des données, échappe au score. | élément de la liste ; « mauvaises », « le haut du classement tient » : jugements | supprimé ; les deux listes restent visibles et annotées dans l’onglet Historique |
| B16 | Ban Radar | `app/ban/BanRadarView.tsx:157` | Résultats mitigés selon les listes : c’est encourageant, ce n’est pas une validation. | verdict sans mesure (« encourageant ») | supprimé (le verdict chiffré le remplace) |
| B17 | Ban Radar | `app/ban/BanRadarView.tsx:159` | Les staples génériques trustent le haut du classement complet parce qu’elles sont jouées partout à 3 exemplaires, mais Konami frappe surtout les pièces de moteur des decks qui gagnent. La page s’ouvre donc sur les « Pièces d’archétype » ; les staples ont leur propre vue. | « trustent » : terme fort non mesuré ; « Konami frappe surtout les pièces de moteur » : affirmation sans chiffre ici | « Sur les 10 banlists TCG rejouées, 6 des 100 places du top 10 des staples génériques ont été suivies d’une restriction, contre 19 pour les pièces d’archétype : la page s’ouvre sur les pièces d’archétype. » |
| B18 | Ban Radar | `app/ban/BanRadarView.tsx:163` | La barre sous chaque carte décompose le score : un segment par critère, en points sur 100. | légende de la barre, conforme ; dans l’encart en attente | inchangé, déplacé au-dessus de la liste (légende en ligne, charte §2.4) |
| B19 | Ban Radar | `app/ban/BanRadarView.tsx:181` | Un score élevé ne suffit pas pour une staple | titre d’encadré qui juge le score sur un sous-ensemble | « Staples génériques et restrictions » |
| B20 | Ban Radar | `app/ban/BanRadarView.tsx:183` | Sur les {…} dernières banlists TCG rejouées, {…} des 100 places du top 10 des staples génériques ont été suivies d’une restriction, contre {…} sur 100 pour les pièces d’archétype. Ash Blossom, première à chaque fois, n’a jamais été touchée. | chiffres exacts ; « Ash Blossom, première à chaque fois, n’a jamais été touchée » sans période | « … contre {19} sur 100 pour les pièces d’archétype. Ash Blossom, première des staples sur les 10 listes, n’a été touchée par aucune. » |
| B21 | Historique | `app/ban/BanHistoryView.tsx:284` | Rang médian meilleur que le hasard | en-tête du bilan : comparaison mesurée | conforme, inchangé (en attente avec le bilan) |
| B22 | Historique | `app/ban/BanHistoryView.tsx:285` | Meilleur que les staples | en-tête du bilan : comparaison mesurée | conforme, inchangé (en attente avec le bilan) |
| B23 | Historique | `app/ban/BanHistoryView.tsx:501` | chaque liste est comparée aux rangs que donneraient 90 % des tirages au sort ; lecture en attente du diagnostic TOK-115 | pied du bilan : emplacement du verdict, laissé vide par consigne de Thomas | « chaque liste est comparée aux rangs que donneraient 90 % des tirages au sort » + ligne de lecture : « Top 25 TCG : 29 cartes touchées sur 250 places contre 16 pour les staples, écart non établi (6 listes pour, 1 contre, 3 égalités) ; OCG : 41 contre 18, 9 listes sur 10. » |
| B24 | Historique | `app/ban/BanHistoryView.tsx:554` | Pour chaque liste, le score est recalculé avec les seules decklists des 6 mois qui précèdent son entrée en vigueur. Une carte compte comme touchée quand son statut se durcit (illimitée vers semi-limitée, limitée ou interdite, et ainsi de suite). | bloc Méthode : la relecture (I6) demande une ligne sur le critère « pont », calculé sur le graphe actuel | texte inchangé + « Le critère « pont » vient du graphe de co-occurrences actuel, pas de celui de la veille ; son effet mesuré est négligeable (top 25 TCG : 30 cartes avec, 28 sans). » |
| B25 | Méthode | `app/methode/page.tsx:367` | Un score de risque, pas une probabilité. Le méta Genesys, exclu des données, lui échappe. | section Ban Radar de /methode : limite conforme ; la section attend le verdict | inchangé + ligne « Résultat » (verdict de la relecture TOK-115, mêmes chiffres que l’onglet Historique) |
| B26 | Méthode | `app/methode/page.tsx:372` | Ban Radar contre l’historique | titre de section, conforme | conforme, inchangé (en attente avec la section) |
| B27 | Méthode | `app/methode/page.tsx:375` | Chaque banlist est rejouée avec les decks des 6 mois qui précèdent son entrée en vigueur, jamais avec des données postérieures. | section « Ban Radar contre l’historique » : la relecture (I6) demande la réserve sur le critère « pont » | texte inchangé + « Exception : le critère « pont » vient du graphe actuel ; effet mesuré négligeable (top 25 TCG : 30 avec, 28 sans). » |
| B28 | Méthode | `app/methode/page.tsx:381` | Rang médian des cartes touchées, liste par liste | titre de la figure, conforme | conforme, inchangé (en attente avec la section) |

## 5. Tableau complet, page par page

Colonnes : numéro (T = à changer, B = en attente TOK-115, — = conforme), fichier et ligne dans `frontend/src/`, texte
actuel (`{…}` = valeur dynamique), problème (règle de la charte enfreinte, ou « conforme »), proposition.

### Accueil (/)

75 textes : 61 conformes, 5 à changer, 9 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/opengraph-image.tsx:11` | Corrélation OCG, TCG {…} plus tard | conforme | conforme, inchangé |
| — | `app/opengraph-image.tsx:12` | IC 95 % : {…} · {…} archétypes | conforme | conforme, inchangé |
| — | `app/opengraph-image.tsx:16` | Source : {…} | conforme | conforme, inchangé |
| T01 | `app/opengraph-image.tsx:19` | YGO Meta. La méta OCG précède la méta TCG de {…} : corrélation {…}, {…}. {…}, {…}. | texte alternatif de l’image : même affirmation | « YGO Meta. Corrélation {0,53} entre le score OCG d’un archétype et son score TCG {2 à 6 mois} plus tard, {IC 95 % : 0,43 à 0,59}, {105 archétypes}. » |
| — | `app/opengraph-image.tsx:25` | Méta Yu-Gi-Oh! · TCG et OCG | conforme | conforme, inchangé |
| T02 | `app/opengraph-image.tsx:26` | La méta OCG précède la méta TCG de {…} | image de partage : même affirmation que le titre | « La méta OCG comparée à la méta TCG {2 à 6 mois} plus tard » |
| T03 | `app/page.tsx:27` | YGO Meta · La méta OCG précède la méta TCG de 2 à 6 mois | titre de partage : affirmation plus forte que la mesure (une corrélation de 0,53 ne montre pas une antériorité) ; la charte veut une description de ce que montre la page | « YGO Meta · Méta OCG et méta TCG, 2 à 6 mois d’écart » |
| — | `app/page.tsx:29` | Méta Yu-Gi-Oh! TCG et OCG mesurée sur 23 948 decklists de tournoi : corrélation OCG → TCG de 0,53, signaux boutique, risque de ban, méthode et limites. | conforme | conforme, inchangé |
| T04 | `app/page.tsx:45` | La méta OCG précède la méta TCG de 2 à 6 mois. (tableau TITLE, mots révélés un à un) | titre (h1, mots révélés un à un) : même affirmation que le titre de partage | « La méta OCG, comparée à la méta TCG *2 à 6 mois* plus tard. » (mot en `<Em>` : « 2 à 6 mois », tiré de `SITE_FACTS.ocgTcgLagRange`) |
| — | `app/page.tsx:76` | Tier list | conforme | conforme, inchangé |
| — | `app/page.tsx:77` | Évolution | conforme | conforme, inchangé |
| — | `app/page.tsx:78` | Prédictions | conforme | conforme, inchangé |
| — | `app/page.tsx:79` | Signaux précoces | conforme | conforme, inchangé |
| — | `app/page.tsx:107` | Part mensuelle des archétypes TCG, mai 2023 à {…}. | conforme | conforme, inchangé |
| — | `app/page.tsx:125` | Méta Yu-Gi-Oh! · données au | conforme | conforme, inchangé |
| — | `app/page.tsx:139` | Corrélation de {…} (IC 95 % : {…} à {…}) entre le score d’un archétype en OCG et son score en TCG {…} plus tard, sur {…} archétypes et {…} decklists de tournoi (yugiohmeta.com, mai 2023 à novembre 2026). | conforme | conforme, inchangé |
| — | `app/page.tsx:143` | Signaux boutique | bouton du hero : un nom de page, pas un appel à l’action | conforme, inchangé |
| — | `app/page.tsx:146` | Méthode et limites | conforme | conforme, inchangé |
| — | `app/page.tsx:182` | Decklists analysées | conforme | conforme, inchangé |
| — | `app/page.tsx:183` | Cartes suivies | conforme | conforme, inchangé |
| — | `app/page.tsx:184` | Corrélation OCG → TCG (r) | conforme | conforme, inchangé |
| — | `app/page.tsx:185` | Écart OCG → TCG | conforme | conforme, inchangé |
| — | `app/page.tsx:197` | Exemple · un archétype, deux formats | conforme | conforme, inchangé |
| — | `app/page.tsx:199` | mois plus tard. | conforme | conforme, inchangé |
| — | `app/page.tsx:203` | 1 · OCG | conforme | conforme, inchangé |
| — | `app/page.tsx:204` | 2 · TCG | conforme | conforme, inchangé |
| — | `app/page.tsx:206` | 3 · Écart | conforme | conforme, inchangé |
| — | `app/page.tsx:207` | Courbe OCG décalée de {…} mois. Un seul archétype : sur {…} archétypes, l’écart observé va de {…}. | conforme | conforme, inchangé |
| — | `app/page.tsx:222` | OCG (Japon, Asie) | conforme | conforme, inchangé |
| — | `app/page.tsx:226` | TCG (Europe, Amériques) | conforme | conforme, inchangé |
| — | `app/page.tsx:231` | Part des decks de tournoi par mois, août 2025 à novembre 2026 (novembre incomplet). Source : decklists yugiohmeta.com, relevé du | conforme | conforme, inchangé |
| — | `app/page.tsx:232` | . Incertitude non dessinée : les effectifs mensuels n’ont pas été relevés avec cette série figée. | conforme | conforme, inchangé |
| — | `app/page.tsx:243` | Outils | conforme | conforme, inchangé |
| T05 | `app/page.tsx:245` | Trois outils sur | titre de section : mesure et source présentes, période absente | « Trois outils sur *23 948* decklists de tournoi, mai 2023 à novembre 2026. » |
| — | `app/page.tsx:247` | decklists de tournoi. | conforme | conforme, inchangé |
| — | `app/page.tsx:255` | Signal boutique | conforme | conforme, inchangé |
| — | `app/page.tsx:264` | archétypes OCG | conforme | conforme, inchangé |
| — | `app/page.tsx:264` | sur | conforme | conforme, inchangé |
| — | `app/page.tsx:275` | Carte suivie : | conforme | conforme, inchangé |
| — | `app/page.tsx:278` | Cardmarket | conforme | conforme, inchangé |
| — | `app/page.tsx:279` | Arrivée TCG | conforme | conforme, inchangé |
| — | `app/page.tsx:283` | Libellé : rang de l’archétype en OCG, seuils provisoires, non validés hors échantillon. | conforme | conforme, inchangé |
| — | `app/page.tsx:284` | Fenêtre d’arrivée : intervalle à 80 %, non validé. | conforme | conforme, inchangé |
| — | `app/page.tsx:295` | Ban Radar · pièces d’archétype | conforme | conforme, inchangé |
| — | `app/page.tsx:297` | Risque de restriction, score sur 100. | conforme | conforme, inchangé |
| — | `app/page.tsx:324` | Barre : | conforme | conforme, inchangé |
| — | `app/page.tsx:335` | Graphe de synergies | conforme | conforme, inchangé |
| — | `app/page.tsx:337` | Cartes jouées ensemble dans les mêmes decks. | conforme | conforme, inchangé |
| — | `app/page.tsx:346` | Schéma d’illustration : positions et liens ne sont pas des données. Graphe réel : cooccurrences dans les decklists de tournoi. | conforme | conforme, inchangé |
| — | `app/page.tsx:377` | Méthode | conforme | conforme, inchangé |
| — | `app/page.tsx:379` | Méthode et limites . | conforme | conforme, inchangé |
| — | `app/page.tsx:385` | Les données | conforme | conforme, inchangé |
| — | `app/page.tsx:388` | decklists de tournoi, mai 2023 à novembre 2026 : {…} en TCG, {…} en OCG, légales à la date du tournoi. | conforme | conforme, inchangé |
| — | `app/page.tsx:390` | mise à jour hebdomadaire. Prédictions datées et archivées depuis le 1ᵉʳ novembre 2026. | conforme | conforme, inchangé |
| — | `app/page.tsx:405` | Le signal OCG → TCG | conforme | conforme, inchangé |
| — | `app/page.tsx:409` | IC 95 % : | conforme | conforme, inchangé |
| — | `app/page.tsx:416` | Corrélation de {…}, intervalle de confiance à 95 % de {…} à {…}, sur une échelle de 0 à 1. | conforme | conforme, inchangé |
| — | `app/page.tsx:447` | Corrélation entre le score d’un archétype en OCG et son score en TCG {…} plus tard, sur {…} archétypes. | conforme | conforme, inchangé |
| — | `app/page.tsx:450` | Libellés Fort, Modéré, Faible des signaux boutique : seuils provisoires, non validés hors échantillon. Premières prédictions datées à échéance en mars 2027. | conforme | conforme, inchangé |
| — | `app/page.tsx:453` | Source : méta TCG et OCG mensuelles, calcul du | conforme | conforme, inchangé |
| B01 | `app/page.tsx:457` | Ban Radar rejoué sur les banlists passées | **en attente du formulaire TOK-115** — titre du même bloc | voir § « Textes du Ban Radar en attente » |
| B02 | `app/page.tsx:459` | Rang médian, dans le classement calculé la veille de la banlist, des cartes ensuite restreintes. Trait vertical : rang attendu au hasard (milieu du classement). | **en attente du formulaire TOK-115** — bloc « Ban Radar rejoué » de l’accueil : il montre 4 listes sur 20 choisies, et en tire une lecture de la qualité du score (non listé dans le brief, ajouté ici par prudence) | voir § « Textes du Ban Radar en attente » |
| B03 | `app/page.tsx:464` | Rang médian des cartes touchées, pour quatre banlists rejouées | **en attente du formulaire TOK-115** — légende du même tableau | voir § « Textes du Ban Radar en attente » |
| B04 | `app/page.tsx:467` | Banlist | **en attente du formulaire TOK-115** — en-têtes du tableau de 4 listes (Banlist, Rang médian…, Au hasard, Cartes classées) | voir § « Textes du Ban Radar en attente » |
| B05 | `app/page.tsx:468` | Rang médian des cartes touchées | **en attente du formulaire TOK-115** — en-tête du tableau de 4 listes | voir § « Textes du Ban Radar en attente » |
| B06 | `app/page.tsx:469` | Au hasard | **en attente du formulaire TOK-115** — en-tête du tableau de 4 listes | voir § « Textes du Ban Radar en attente » |
| B07 | `app/page.tsx:470` | Cartes classées | **en attente du formulaire TOK-115** — en-tête du tableau de 4 listes | voir § « Textes du Ban Radar en attente » |
| B08 | `app/page.tsx:504` | Top 10 du radar sur {…} banlists TCG (avril 2024 à octobre 2026) : {…} places sur 100 suivies d’une restriction pour les pièces d’archétype, {…} sur 100 pour les staples génériques. | **en attente du formulaire TOK-115** — comparaison top 10 pièces d’archétype / staples : chiffres exacts, mais présentée comme une preuve du score | voir § « Textes du Ban Radar en attente » |
| B09 | `app/page.tsx:507` | Source : backtest du {…}, {…} des {…} listes rejouées (les deux de référence et les deux plus récentes en TCG). Poids du score réglés sur la liste TCG de mai 2026. Trait : milieu du classement ; la bande du hasard à 90 % est dans l’historique du Ban Center. | **en attente du formulaire TOK-115** — pied du même bloc | voir § « Textes du Ban Radar en attente » |
| — | `components/home/constellation.tsx:39` | Schéma : trois amas de cartes reliés entre eux par deux cartes pont, en orange. | conforme | conforme, inchangé |
| — | `components/home/constellation.tsx:95` | Archétype {…} | conforme | conforme, inchangé |
| — | `components/home/constellation.tsx:111` | PONT | conforme | conforme, inchangé |
| — | `components/home/proof-chart.tsx:43` | Part de {…} dans les decks de tournoi, par mois, de {…} à {…}. En OCG, pic à {…} % en {…}. En TCG, pic à {…} % en {…}, {…} mois plus tard. | conforme | conforme, inchangé |
| — | `lib/proof-data.ts:9` | Kewl Tune | conforme | conforme, inchangé |
| — | `lib/site-facts.ts:17` | 2 à 6 mois | conforme | conforme, inchangé |

### Tier list (/tier-list)

26 textes : 19 conformes, 7 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/tier-list/ArchetypeRow.tsx:94` | decks · | conforme | conforme, inchangé |
| — | `app/tier-list/ArchetypeRow.tsx:94` | sur | conforme | conforme, inchangé |
| — | `app/tier-list/ArchetypeRow.tsx:95` | score | conforme | conforme, inchangé |
| — | `app/tier-list/ArchetypeRow.tsx:101` | composition | conforme | conforme, inchangé |
| — | `app/tier-list/ArchetypeRow.tsx:117` | Part {…}, intervalle à 95 % de {…} à {…} | conforme | conforme, inchangé |
| — | `app/tier-list/TierList.tsx:14` | En hausse | conforme | conforme, inchangé |
| — | `app/tier-list/TierList.tsx:50` | Aucun archétype dans ce filtre. | conforme | conforme, inchangé |
| — | `app/tier-list/opengraph-image.tsx:3` | Tier list TCG · YGO Meta. Part de decks par archétype, decklists de tournoi TCG. | conforme | conforme, inchangé |
| — | `app/tier-list/opengraph-image.tsx:9` | Méta · TCG | conforme | conforme, inchangé |
| — | `app/tier-list/opengraph-image.tsx:10` | Tier list TCG | conforme | conforme, inchangé |
| — | `app/tier-list/opengraph-image.tsx:11` | Part de decks par archétype, decklists de tournoi TCG | conforme | conforme, inchangé |
| — | `app/tier-list/page.tsx:18` | fenêtre courante | conforme | conforme, inchangé |
| — | `app/tier-list/page.tsx:20` | Tier list TCG | conforme | conforme, inchangé |
| — | `app/tier-list/page.tsx:41` | Tier list · TCG · {…} · {…} decks | conforme | conforme, inchangé |
| T06 | `app/tier-list/page.tsx:44` | Ce que joue la méta, maintenant . | titre : « maintenant » ne dit ni la période ni ce que montre la page | « Les archétypes TCG classés par *part* des decks de tournoi. » |
| T07 | `app/tier-list/page.tsx:49` | Classement calculé sur nos decklists de tournoi TCG. Tier | intro : possessif « nos », aucune mesure ni période | « {n} archétypes classés sur {n_decks} decklists de tournoi TCG, {période} (yugiohmeta.com). Tier ⓘ selon la part des decks, tendance par rapport à la fenêtre précédente. » Exemple : « … sur 396 decklists de tournoi TCG, {période} … » (n et période servis par `/meta/tier-list`) |
| — | `app/tier-list/page.tsx:50` | Niveau de l’archétype selon la part des decks de tournoi qui le jouent. | conforme | conforme, inchangé |
| T08 | `app/tier-list/page.tsx:51` | selon la part de méta, tendance par rapport à la période précédente. | suite de l’intro (même phrase) | voir la ligne précédente |
| T09 | `app/tier-list/page.tsx:57` | Decklists analysées | chiffre de vitrine (23 948, TCG et OCG, mai 2023 à novembre 2026) placé au-dessus d’un classement calculé sur la seule fenêtre TCG : l’effectif ne correspond pas à la page | « Decks de la fenêtre » : {n_decks} (exemple : 396) |
| T10 | `app/tier-list/page.tsx:58` | Cartes suivies | chiffre sans rapport avec le classement des archétypes | « Archétypes classés » : {n} |
| T11 | `app/tier-list/page.tsx:59` | Corrélation OCG → TCG | mesure de la page Boutique / accueil, sans effectif ni intervalle ici | supprimé de cette page (reste sur l’accueil avec son IC 95 %) |
| T12 | `app/tier-list/page.tsx:60` | Fenêtre du signal sur le TCG | libellé obscur (« fenêtre du signal ») pour « 2 à 6 mois », hors sujet sur cette page | supprimé de cette page (sur l’accueil : « Écart OCG → TCG ») |
| — | `app/tier-list/page.tsx:67` | decklists de tournoi TCG, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/tier-list/page.tsx:70` | barre : intervalle à 95 % de la part, point : part observée ; tendance affichée seulement si l’écart dépasse le bruit d’échantillonnage | conforme | conforme, inchangé |
| — | `app/tier-list/page.tsx:73` | Tier : T0 à partir de 40 % des decks de la fenêtre, T1 à partir de 15 %, T2 à partir de 7 %, T3 à partir de 3 % ; Rogue en dessous ou sous 5 decks. | conforme | conforme, inchangé |
| — | `app/tier-list/page.tsx:74` | Sur une soixantaine d’archétypes comparés, deux ou trois tendances peuvent être dues au hasard. | conforme | conforme, inchangé |

### Évolution (/evolution)

31 textes : 30 conformes, 1 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/evolution/EvolutionChart.tsx:72` | 0) setSize( | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:229` | part des decks du mois | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:230` | intervalle à 95 % | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:231` | mois de moins de 100 decks, mois en cours | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:232` | decks relevés par mois | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:239` | Graphique interactif, {…}. Flèches gauche et droite : changer de mois. Échap : quitter. | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:251` | Part mensuelle des decks de tournoi TCG, {…}, avec intervalle à 95 %. Dernière valeur : {…}. | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:252` | Aucune série sélectionnée. | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:260` | part des decks | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:317` | en cours, {…} decks | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:398` | part · intervalle à 95 % | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:418` | decklists de tournoi TCG, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:421` | bande : intervalle à 95 % de chaque part mensuelle ; pointillé : mois de moins de 100 decks et mois en cours | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:423` | un mois sans deck de l’archétype n’a pas de point | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:426` | Part du mois : decks de l’archétype divisés par tous les decks de tournoi TCG relevés ce mois-là. | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:427` | Archétypes proposés : les premiers au score méta du dernier mois, qui combine la part et le classement en tournoi. | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:428` | L’intervalle suppose des decks indépendants ; plusieurs listes d’un même joueur ou d’un même tournoi le rendent trop étroit. | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:433` | Tableau des valeurs | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:441` | Part mensuelle des decks (decks de l’archétype entre parenthèses) et score méta des séries affichées, | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:445` | Mois | conforme | conforme, inchangé |
| — | `app/evolution/EvolutionChart.tsx:451` | Decks | conforme | conforme, inchangé |
| — | `app/evolution/opengraph-image.tsx:3` | Évolution de la méta · YGO Meta. Part mensuelle des decks par archétype, decklists de tournoi TCG. | conforme | conforme, inchangé |
| — | `app/evolution/opengraph-image.tsx:9` | Méta · TCG | conforme | conforme, inchangé |
| — | `app/evolution/opengraph-image.tsx:10` | Évolution de la méta | conforme | conforme, inchangé |
| — | `app/evolution/opengraph-image.tsx:11` | Part mensuelle des decks par archétype, decklists de tournoi TCG | conforme | conforme, inchangé |
| — | `app/evolution/page.tsx:17` | Évolution de la méta | conforme | conforme, inchangé |
| — | `app/evolution/page.tsx:18` | Part mensuelle des decks de tournoi des {…} premiers archétypes Yu-Gi-Oh! TCG{…}, avec intervalle à 95 %. Source : decklists de tournoi, {…}. | conforme | conforme, inchangé |
| — | `app/evolution/page.tsx:31` | Méta · Évolution | conforme | conforme, inchangé |
| T13 | `app/evolution/page.tsx:34` | Qui monte, qui s’efface . | titre : tournure de récit (« qui monte ») sans description de ce que montre la page | « Part mensuelle des decks de tournoi, *archétype* par archétype. » |
| — | `app/evolution/page.tsx:37` | Part mensuelle des decks de tournoi TCG des {…} premiers archétypes{…}, quatre séries au plus. | conforme | conforme, inchangé |
| — | `app/evolution/page.tsx:37` | de {…} | conforme | conforme, inchangé |

### Prédictions (/predictions)

38 textes : 37 conformes, 1 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/predictions/PredictionsChart.tsx:44` | observé | conforme | conforme, inchangé |
| — | `app/predictions/PredictionsChart.tsx:50` | prévu | conforme | conforme, inchangé |
| — | `app/predictions/PredictionsChart.tsx:54` | Archétype | conforme | conforme, inchangé |
| — | `app/predictions/PredictionsChart.tsx:55` | Score méta ×100 | conforme | conforme, inchangé |
| — | `app/predictions/PredictionsChart.tsx:56` | Écart (points) | conforme | conforme, inchangé |
| — | `app/predictions/PredictionsChart.tsx:57` | Direction | conforme | conforme, inchangé |
| — | `app/predictions/PredictionsChart.tsx:62` | score ×100 | conforme | conforme, inchangé |
| — | `app/predictions/opengraph-image.tsx:3` | Prédictions de méta · YGO Meta. Score méta prévu à un mois, valeur attendue si la situation récente se prolonge. | conforme | conforme, inchangé |
| — | `app/predictions/opengraph-image.tsx:9` | Méta · TCG | conforme | conforme, inchangé |
| — | `app/predictions/opengraph-image.tsx:10` | Prédictions de méta | conforme | conforme, inchangé |
| — | `app/predictions/opengraph-image.tsx:11` | Score méta prévu à un mois, valeur attendue si la situation récente se prolonge | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:24` | pour {…} | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:25` | , calcul du {…} | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:27` | Prédictions de méta | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:28` | Score méta prévu{…} sur {…} archétypes Yu-Gi-Oh! TCG{…}. Données : decklists de tournoi, {…}. | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:36` | dernier mois | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:37` | mois suivant | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:42` | Méta · Prédictions | conforme | conforme, inchangé |
| T14 | `app/predictions/page.tsx:45` | La méta du mois prochain . | titre : promesse (« la méta du mois prochain ») ; charte §6, exemple 2 | « Le score de chaque archétype, *prévu* pour le mois suivant. » |
| — | `app/predictions/page.tsx:50` | Score méta ×100 de | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:52` | Prévision | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:53` | Valeur attendue si la situation récente se prolonge, en ramenant les écarts vers la moyenne. | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:55` | . Le modèle n’anticipe ni les ruptures ni l’arrivée d’un nouvel archétype. | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:62` | decklists de tournoi TCG, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:63` | date inconnue | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:63` | observé {…}, calcul du {…} | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:65` | aucun intervalle par archétype : le modèle ne produit qu’une valeur ; son erreur moyenne est mesurée sur l’historique (page Méthode) | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:67` | anneau : observé ; point plein : prévu | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:70` | Prévision : surtout la valeur du mois observé, corrigée d’une part de retour à la moyenne. | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:71` | Rejouée mois par mois sur l’historique, elle se trompe d’environ 5 % de moins que « rien ne change ». | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:76` | Tableau des valeurs | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:84` | , par archétype | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:84` | Score méta ×100 observé en | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:88` | Archétype | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:89` | Observé | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:90` | Prévu | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:91` | Écart | conforme | conforme, inchangé |
| — | `app/predictions/page.tsx:92` | Direction | conforme | conforme, inchangé |

### Ban Center, commun (/ban)

20 textes : 18 conformes, 2 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| T15 | `app/ban/kind-filter.tsx:11` | Cartes rattachées à un deck précis | infobulle du filtre : la règle (au moins 50 %) n’est pas dite | « Au moins la moitié des decks qui la jouent sont d’un même archétype » |
| — | `app/ban/kind-filter.tsx:11` | Pièces d'archétype | conforme | conforme, inchangé |
| T16 | `app/ban/kind-filter.tsx:12` | Cartes jouées un peu partout | infobulle du filtre : « un peu partout » au lieu de la règle appliquée (moins de 50 % des decks dans un même archétype) | « Moins de la moitié des decks qui la jouent sont d’un même archétype » |
| — | `app/ban/kind-filter.tsx:12` | Staples génériques | conforme | conforme, inchangé |
| — | `app/ban/kind-filter.tsx:13` | Toutes les cartes notées | conforme | conforme, inchangé |
| — | `app/ban/loading.tsx:15` | Chargement des données… | conforme | conforme, inchangé |
| — | `app/ban/opengraph-image.tsx:3` | Ban Center · YGO Meta. Risque de restriction, cartes à impact, simulateur. | conforme | conforme, inchangé |
| — | `app/ban/opengraph-image.tsx:9` | Bans · TCG | conforme | conforme, inchangé |
| — | `app/ban/opengraph-image.tsx:10` | Ban Center | conforme | conforme, inchangé |
| — | `app/ban/opengraph-image.tsx:11` | Risque de restriction, cartes à impact, simulateur | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:20` | Ban Radar | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:22` | Cartes à impact | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:40` | Simulateur de ban | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:41` | Archétypes et decks de tournoi Yu-Gi-Oh! TCG reliés à une carte dans le graphe de co-occurrences, et cohésion du graphe sans elle. Source : {…}, date de calcul non enregistrée. | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:50` | Classement du Ban Radar recalculé la veille de {…} banlists Yu-Gi-Oh! TCG et OCG, face aux cartes réellement restreintes, comparé au hasard et aux staples les plus jouées. Calcul du {…}. Sources : {…}, Yugipedia. | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:57` | Cartes à impact | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:58` | Cartes Yu-Gi-Oh! TCG classées par nombre d’archétypes et de decks qui les jouent, sur {…} decks de tournoi, relevé du {…}. Source : {…}. | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:64` | Ban Radar | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:65` | Cartes Yu-Gi-Oh! TCG notées de 0 à 100 sur six critères de risque de restriction, sur {…} decks de tournoi, relevé du {…}. Source : {…}. | conforme | conforme, inchangé |
| — | `app/ban/page.tsx:73` | Ban Center | conforme | conforme, inchangé |

### Ban Radar (/ban, onglet Radar)

32 textes : 15 conformes, 6 à changer, 11 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/ban/BanRadarView.tsx:81` | Générique | conforme | conforme, inchangé |
| — | `app/ban/BanRadarView.tsx:116` | Ban Center · Radar | conforme | conforme, inchangé |
| T17 | `app/ban/BanRadarView.tsx:119` | Qui sera banni ensuite ? | titre : question et promesse (« qui sera banni ») ; charte §6, exemple 8 | « Les cartes qui ressemblent le plus aux cartes déjà *bannies*. » |
| — | `app/ban/BanRadarView.tsx:124` | Données au | conforme | conforme, inchangé |
| — | `app/ban/BanRadarView.tsx:126` | decks · 6 mois | conforme | conforme, inchangé |
| T18 | `app/ban/BanRadarView.tsx:129` | Les cartes les plus exposées à la prochaine banlist TCG, notées sur six critères. | intro : promesse (« les plus exposées à la prochaine banlist »), sans effectif ni période | « {n} cartes TCG notées de 0 à 100 sur six critères, d’après {n_decks} decks de tournoi des 6 derniers mois. » (n et n_decks servis par `/ban-radar`) |
| B10 | `app/ban/BanRadarView.tsx:134` | Comment lire ce score ? | **en attente du formulaire TOK-115** — libellé de l’encart : question ; l’encart entier juge la qualité du score | voir § « Textes du Ban Radar en attente » |
| — | `app/ban/BanRadarView.tsx:134` | Lecture du score | conforme | conforme, inchangé |
| B11 | `app/ban/BanRadarView.tsx:136` | C’est un score de risque , pas une probabilité : il classe les cartes par ressemblance au profil de celles que Konami a historiquement touchées. Il ne dit pas « X % de chances d’être bannie ». | **en attente du formulaire TOK-115** — 1er paragraphe : définition (risque, pas probabilité) ; conforme sur le fond, mais dans l’encart en attente | voir § « Textes du Ban Radar en attente » |
| B12 | `app/ban/BanRadarView.tsx:140` | Rejoué la veille des banlists passées (listes dont la fenêtre compte au moins 600 decks : dix en TCG, dix en OCG) : | **en attente du formulaire TOK-115** — liste de 3 résultats choisis et paragraphe de backtest : la charte §6 ex. 8 veut un graphique, la relecture TOK-115 un verdict avec effectifs | voir § « Textes du Ban Radar en attente » |
| B13 | `app/ban/BanRadarView.tsx:143` | TCG, 18 mai 2026 : rang médian 84 sur 889 cartes notées pour les cartes réellement touchées (le hasard donnerait environ 445). | **en attente du formulaire TOK-115** — élément de la liste de 3 résultats | voir § « Textes du Ban Radar en attente » |
| B14 | `app/ban/BanRadarView.tsx:147` | OCG, 1er juillet 2026 : rang médian 19 sur 1 236. Le score n’a jamais été calibré sur l’OCG : c’est un test hors distribution, et il y réussit mieux qu’en TCG. | **en attente du formulaire TOK-115** — élément de la liste ; « il y réussit mieux » : jugement | voir § « Textes du Ban Radar en attente » |
| B15 | `app/ban/BanRadarView.tsx:151` | TCG, 21 septembre et 19 octobre 2026 : les deux listes les plus récentes sont mauvaises (rang médian 206 sur 981, puis 308 sur 905, proche du hasard). Le haut du classement tient, mais la liste d’octobre touche 43 cartes dont beaucoup de marginales, et le méta Genesys, exclu des données, échappe au score. | **en attente du formulaire TOK-115** — élément de la liste ; « mauvaises », « le haut du classement tient » : jugements | voir § « Textes du Ban Radar en attente » |
| B16 | `app/ban/BanRadarView.tsx:157` | Résultats mitigés selon les listes : c’est encourageant, ce n’est pas une validation. | **en attente du formulaire TOK-115** — verdict sans mesure (« encourageant ») | voir § « Textes du Ban Radar en attente » |
| B17 | `app/ban/BanRadarView.tsx:159` | Les staples génériques trustent le haut du classement complet parce qu’elles sont jouées partout à 3 exemplaires, mais Konami frappe surtout les pièces de moteur des decks qui gagnent. La page s’ouvre donc sur les « Pièces d’archétype » ; les staples ont leur propre vue. | **en attente du formulaire TOK-115** — « trustent » : terme fort non mesuré ; « Konami frappe surtout les pièces de moteur » : affirmation sans chiffre ici | voir § « Textes du Ban Radar en attente » |
| B18 | `app/ban/BanRadarView.tsx:163` | La barre sous chaque carte décompose le score : un segment par critère, en points sur 100. | **en attente du formulaire TOK-115** — légende de la barre, conforme ; dans l’encart en attente | voir § « Textes du Ban Radar en attente » |
| — | `app/ban/BanRadarView.tsx:177` | Top {…} | conforme | conforme, inchangé |
| B19 | `app/ban/BanRadarView.tsx:181` | Un score élevé ne suffit pas pour une staple | **en attente du formulaire TOK-115** — titre d’encadré qui juge le score sur un sous-ensemble | voir § « Textes du Ban Radar en attente » |
| B20 | `app/ban/BanRadarView.tsx:183` | Sur les {…} dernières banlists TCG rejouées, {…} des 100 places du top 10 des staples génériques ont été suivies d’une restriction, contre {…} sur 100 pour les pièces d’archétype. Ash Blossom, première à chaque fois, n’a jamais été touchée. | **en attente du formulaire TOK-115** — chiffres exacts ; « Ash Blossom, première à chaque fois, n’a jamais été touchée » sans période | voir § « Textes du Ban Radar en attente » |
| — | `app/ban/BanRadarView.tsx:195` | decklists de tournoi TCG (yugiohmeta.com), banlists (Yugipedia) | conforme | conforme, inchangé |
| — | `app/ban/BanRadarView.tsx:196` | au {…}, 6 mois glissants | conforme | conforme, inchangé |
| — | `app/ban/BanRadarView.tsx:198` | aucun intervalle : un score de risque classe les cartes, ce n’est pas une probabilité ; sa fiabilité se lit dans l’onglet Historique | conforme | conforme, inchangé |
| — | `app/ban/BanRadarView.tsx:201` | Le score rapproche chaque carte du profil des cartes déjà touchées par Konami, sur six critères ; la barre en donne la part de chacun. | conforme | conforme, inchangé |
| — | `app/ban/BanRadarView.tsx:202` | Fenêtre : les 6 derniers mois de decks de tournoi TCG. | conforme | conforme, inchangé |
| — | `lib/ban-criteria.ts:7` | Part des decks du format qui jouent la carte. | conforme | conforme, inchangé |
| T19 | `lib/ban-criteria.ts:7` | Ubiquité | libellé de critère : mot savant (charte §1 : les mots du lecteur) | « Part des decks » |
| T20 | `lib/ban-criteria.ts:8` | La carte est indispensable à un archétype qui pèse dans la méta. | définition du critère « Porteur » : « indispensable » non mesuré, ne dit pas ce qui est compté | « La carte est jouée par la plupart des decks d’un archétype qui pèse dans la méta. » |
| T21 | `lib/ban-criteria.ts:9` | Nombre moyen d'exemplaires joués : une carte jouée à 3 peut être limitée, une carte déjà à 1 beaucoup moins. | définition + explication en deux temps ; libellé du critère « Copies » (anglicisme, le site dit « exemplaires ») | libellé « Exemplaires » ; définition « Nombre moyen d’exemplaires joués par deck (1 à 3). » |
| T22 | `lib/ban-criteria.ts:10` | La carte est déjà limitée ou semi-limitée : Konami y revient souvent. | « souvent » : affirmation sans mesure dans une définition | « La carte est déjà limitée ou semi-limitée. » |
| — | `lib/ban-criteria.ts:11` | Usage des 3 derniers mois comparé aux 3 précédents. | conforme | conforme, inchangé |
| — | `lib/ban-criteria.ts:11` | Élan | libellé conforme | conforme, inchangé |
| — | `lib/ban-criteria.ts:12` | La carte relie des groupes de cartes qui, sans elle, se jouent rarement ensemble. | conforme | conforme, inchangé |

### Historique (/ban?tab=historique)

70 textes : 66 conformes, 0 à changer, 4 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/ban/BanHistoryView.tsx:15` | decklists de tournoi TCG et OCG (yugiohmeta.com), banlists (Yugipedia) | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:57` | Liste {…} du {…} : rang médian des cartes touchées {…} sur {…} ; hasard entre {…} et {…} ; staples les plus jouées {…}. | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:73` | hasard | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:108` | ↑ rang médian | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:118` | liste de calage | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:119` | vue au calage | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:120` | après calage | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:155` | staples : | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:164` | écartée : {…} decks dans la fenêtre, seuil {…} | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:165` | écartée : {…} cartes touchées, seuil {…} | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:172` | non classée | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:182` | Ban Radar | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:186` | staples les plus jouées | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:190` | hasard (90 % des tirages) | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:194` | une carte touchée | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:210` | Liste | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:222` | Rang médian | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:280` | Bilan des banlists rejouées, par format | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:283` | Format | conforme | conforme, inchangé |
| B21 | `app/ban/BanHistoryView.tsx:284` | Rang médian meilleur que le hasard | **en attente du formulaire TOK-115** — en-tête du bilan : comparaison mesurée | voir § « Textes du Ban Radar en attente » |
| B22 | `app/ban/BanHistoryView.tsx:285` | Meilleur que les staples | **en attente du formulaire TOK-115** — en-tête du bilan : comparaison mesurée | voir § « Textes du Ban Radar en attente » |
| — | `app/ban/BanHistoryView.tsx:286` | Top | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:287` | Top | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:297` | listes sur | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:300` | sur | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:303` | places sur | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:306` | sur | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:317` | non touchée | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:326` | Générique | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:335` | hors classement (moins de 5 decks) | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:353` | classement du | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:353` | decks sur 6 mois | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:358` | Top | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:369` | Cartes touchées | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:381` | classement reconstitué au {…}, decks des 6 mois précédents | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:383` | aucun intervalle : les deux colonnes listent des cartes, elles ne mesurent rien ; le rang de chaque carte est celui du classement reconstitué | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:393` | Tableau des données (toutes les listes) | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Cartes classées | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Hasard (90 %) | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Rang médian | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Top 10 % | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Top 25 % | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Top {…} | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Top {…}, staples | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | Touchées | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:398` | dont classées | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:427` | rejouée après coup | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:434` | moins de 5 cartes touchées | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:434` | moins de 600 decks | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:434` | écartée ( | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:453` | Ban Center · Historique | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:456` | Le classement de la veille, face aux banlists réelles. | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:462` | Calcul du | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:470` | Ban Radar recalculé la veille de {…} banlists TCG et OCG, de {…} à {…}, avec les seuls decks des 6 mois précédant l’entrée en vigueur, puis comparé aux cartes réellement restreintes. | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:482` | Historique non calculé sur cette base. | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:495` | Bilan par format | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:499` | calcul du {…}, listes du {…} au {…} | conforme | conforme, inchangé |
| B23 | `app/ban/BanHistoryView.tsx:501` | chaque liste est comparée aux rangs que donneraient 90 % des tirages au sort ; lecture en attente du diagnostic TOK-115 | **en attente du formulaire TOK-115** — pied du bilan : emplacement du verdict, laissé vide par consigne de Thomas | voir § « Textes du Ban Radar en attente » |
| — | `app/ban/BanHistoryView.tsx:516` | classements reconstitués la veille de chaque liste, calcul du {…} | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:518` | bande grise : rangs médians que donneraient 90 % des tirages au sort | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:520` | position de gauche à droite : du premier au dernier du classement | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:526` | Top | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:526` | prévu et cartes touchées, liste par liste | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:529` | Listes {…} | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:551` | Méthode | conforme | conforme, inchangé |
| B24 | `app/ban/BanHistoryView.tsx:554` | Pour chaque liste, le score est recalculé avec les seules decklists des 6 mois qui précèdent son entrée en vigueur. Une carte compte comme touchée quand son statut se durcit (illimitée vers semi-limitée, limitée ou interdite, et ainsi de suite). | **en attente du formulaire TOK-115** — bloc Méthode : la relecture (I6) demande une ligne sur le critère « pont », calculé sur le graphe actuel | voir § « Textes du Ban Radar en attente » |
| — | `app/ban/BanHistoryView.tsx:559` | Une liste est écartée sous | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:559` | cartes touchées : en dessous, le classement ne se distingue pas du hasard. | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:563` | Les poids du score ont été choisis en août 2026 sur la liste TCG du 18 mai 2026. Seules les listes marquées « après calage » ( | conforme | conforme, inchangé |
| — | `app/ban/BanHistoryView.tsx:568` | Le classement est celui de la veille de l’entrée en vigueur, qui suit l’annonce de une à trois semaines : les decks joués entre les deux sont dans la fenêtre. Les fenêtres de 6 mois de deux listes voisines se chevauchent : les listes ne sont pas des essais indépendants. | conforme | conforme, inchangé |

### Cartes à impact (/ban?tab=impact)

18 textes : 11 conformes, 7 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/ban/CardImpactView.tsx:15` | Générique | conforme | conforme, inchangé |
| — | `app/ban/CardImpactView.tsx:37` | Simuler le ban → | conforme | conforme, inchangé |
| — | `app/ban/CardImpactView.tsx:50` | Ban Center · Cartes à impact | conforme | conforme, inchangé |
| T23 | `app/ban/CardImpactView.tsx:53` | Les cartes qui tiennent la méta. | titre : image (« tiennent la méta ») sans mesure | « Les cartes jouées par le plus d’*archétypes* à la fois. » |
| — | `app/ban/CardImpactView.tsx:58` | Données au | conforme | conforme, inchangé |
| — | `app/ban/CardImpactView.tsx:60` | decks · 6 mois | conforme | conforme, inchangé |
| T24 | `app/ban/CardImpactView.tsx:63` | Les cartes dont le retrait fragmenterait le plus la méta : combien d'archétypes et de decks une interdiction toucherait. | intro : conditionnel spéculatif (« fragmenterait », « toucherait »), sans effectif ni période | « Cartes TCG classées par nombre d’archétypes et de decks qui les jouent, sur {n_decks} decks de tournoi des 6 derniers mois. » |
| T25 | `app/ban/CardImpactView.tsx:68` | Comment lire ce score ? | libellé d’encart : question | « Lecture du score » |
| — | `app/ban/CardImpactView.tsx:68` | Lecture du score | conforme | conforme, inchangé |
| T26 | `app/ban/CardImpactView.tsx:70` | Ce n’est pas un score de risque de ban (voir l’onglet | « voir l’onglet … pour ça » : consigne, registre familier ; « si Konami retire cette carte demain » : scénario | « Score d’impact, distinct du score de risque du Ban Radar : nombre d’archétypes et de decks qui jouent la carte. » (lien « Ban Radar » gardé sur le nom) |
| — | `app/ban/CardImpactView.tsx:72` | Ban Radar | conforme | conforme, inchangé |
| T27 | `app/ban/CardImpactView.tsx:74` | pour ça) mais une mesure d’ impact : si Konami retire cette carte demain, combien d’archétypes et de decks sont concernés. | suite du même paragraphe | voir la ligne précédente |
| T28 | `app/ban/CardImpactView.tsx:78` | Le score de pont grandit avec le nombre d’archétypes qui jouent la carte et, plus lentement, avec le nombre de decks. Une carte adoptée par beaucoup d’archétypes, en volume, est une pièce de connexion : la retirer touche plusieurs decks à la fois. | deuxième phrase (« pièce de connexion : la retirer touche plusieurs decks ») répète la première | « Le score de pont augmente avec le nombre d’archétypes qui jouent la carte et, plus lentement, avec le nombre de decks. » |
| T29 | `app/ban/CardImpactView.tsx:83` | Les staples génériques trustent le haut du classement parce qu’elles sont jouées par le plus d’archétypes à la fois. Le filtre « Pièces d’archétype » isole les cartes rattachées à un deck précis. | « trustent » : terme fort non mesuré | « Les staples génériques occupent le haut du classement : ce sont les cartes jouées par le plus d’archétypes. Le filtre « Pièces d’archétype » isole les cartes rattachées à un deck précis. » |
| — | `app/ban/CardImpactView.tsx:89` | Top {…} | conforme | conforme, inchangé |
| — | `app/ban/CardImpactView.tsx:97` | decklists de tournoi TCG, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/ban/CardImpactView.tsx:98` | au {…}, 6 mois glissants | conforme | conforme, inchangé |
| — | `app/ban/CardImpactView.tsx:100` | aucun intervalle : le score ordonne les cartes à partir de comptes exacts sur la fenêtre | conforme | conforme, inchangé |

### Simulateur (/ban?tab=simulateur)

16 textes : 13 conformes, 3 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/ban/BanSimulatorView.tsx:47` | Ban Center · Simulateur | conforme | conforme, inchangé |
| T30 | `app/ban/BanSimulatorView.tsx:50` | Et si Konami la bannissait ? | titre : question, scénario | « Le graphe de co-occurrences *sans* une carte. » |
| — | `app/ban/BanSimulatorView.tsx:53` | Effet du retrait d’une carte sur le graphe de co-occurrences : archétypes touchés, position de pont, perte de cohésion. | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:69` | Carte à simuler | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:73` | Simulation… | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:73` | Simuler le ban | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:78` | Carte introuvable | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:80` | Carte absente de la table des cartes. Exemples présents : « Ash Blossom &amp; Joyous Spring », « Nibiru, the Primal Being ». | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:98` | Carte retirée | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:107` | Score de pont | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:110` | Fragmentation · communauté inconnue | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:110` | Fragmentation · communauté {…} | conforme | conforme, inchangé |
| T31 | `app/ban/BanSimulatorView.tsx:112` | Archétypes impactés | « impactés » : anglicisme ; le reste de la page dit « touchés » | « Archétypes touchés » |
| T32 | `app/ban/BanSimulatorView.tsx:118` | Archétypes impactés | « impactés » : anglicisme ; le reste de la page dit « touchés » | « Archétypes touchés » |
| — | `app/ban/BanSimulatorView.tsx:130` | date de calcul non enregistrée dans la base servie | conforme | conforme, inchangé |
| — | `app/ban/BanSimulatorView.tsx:131` | aucun intervalle : la simulation recalcule le graphe sans la carte, elle ne prévoit pas ce que joueraient les joueurs | conforme | conforme, inchangé |

### Signaux boutique (/boutique)

65 textes : 65 conformes, 0 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/boutique/ArrivalTimeline.tsx:79` | rang parmi les | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:83` | arrivée en TCG, 8 fois sur 10 par le passé | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:88` | calcul du | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:117` | rang indisponible | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:129` | Arrivée en TCG estimée : {…}, 8 fois sur 10 par le passé | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:132` | , 8 fois sur 10 par le passé | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:132` | Arrivée en TCG estimée de | conforme | conforme, inchangé |
| — | `app/boutique/ArrivalTimeline.tsx:136` | fenêtre indisponible | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:71` | (points: T[], gaps: PriceGap[]): T[][] | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:104` | Prix Cardmarket de {…} : {…} relevé{…} seulement, trop peu pour une courbe. Dernier relevé : {…} le {…}. | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:105` | Prix Cardmarket de {…} : {…} relevés du {…} au {…}, de {…} à {…}. Premier relevé {…}, dernier {…}. {…} période{…} de plus de {…} jours sans relevé, non reliée{…}. | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:178` | maxStepDays ? [ | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:185` | date de relevé ( | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:189` | jours sans relevé : rien n’est tracé | conforme | conforme, inchangé |
| — | `app/boutique/PriceChart.tsx:189` | plus de | conforme | conforme, inchangé |
| — | `app/boutique/opengraph-image.tsx:3` | Signaux boutique · YGO Meta. Archétypes joués en OCG, pas encore sortis en TCG. | conforme | conforme, inchangé |
| — | `app/boutique/opengraph-image.tsx:9` | Boutique · OCG vers TCG | conforme | conforme, inchangé |
| — | `app/boutique/opengraph-image.tsx:10` | Signaux boutique | conforme | conforme, inchangé |
| — | `app/boutique/opengraph-image.tsx:11` | Archétypes joués en OCG, pas encore sortis en TCG | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:19` | decklists OCG (yugiohmeta.com), vues Cardmarket (YGOPRODeck) | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:28` | , calcul du {…} | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:30` | , seuils provisoires, non validés hors échantillon | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:30` | Libellé : rang parmi {…} archétypes OCG{…}. | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:33` | Signaux boutique | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:78` | Relevés de prix en tableau | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:83` | Date du relevé | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:136` | arrivée en TCG : {…}, 8 fois sur 10 | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:136` | fenêtre d’arrivée indisponible | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:141` | page de l’archétype | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:169` | Aucun relevé de prix pour cette carte. Prix du calcul du signal : | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:173` | Cardmarket via YGOPRODeck · | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:173` | aucun relevé | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:183` | aucun relevé de prix servi | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:183` | relevés du {…} au {…} | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:185` | aucun intervalle : chaque point est un prix relevé ; l’écart entre deux relevés n’est pas connu | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:187` | bandes grises : plus de | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:187` | jours sans relevé, rien n’y est tracé | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:199` | au {…} | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:199` | à une date de calcul inconnue | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:206` | Boutique · OCG → TCG | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:209` | Archétypes joués en OCG, pas encore arrivés en TCG. | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:212` | ({…} relevés, {…} → {…}) | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:212` | , seuils provisoires, non validés hors échantillon | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:212` | Libellé : rang de l’archétype parmi les {…} archétypes OCG{…}. | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:216` | Archétypes | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:218` | Relevés de prix | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:221` | Corrélation OCG → TCG, IC 95 % {…} à {…} | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:226` | Corrélation entre le score d’un archétype en OCG et son score en TCG {…} plus tard, sur {…} archétypes. Signal de juin 2026 : ses cartes ont baissé de 35 % contre 1 % pour le marché. | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:230` | Rang en OCG et arrivée en TCG | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:234` | calcul du {…} | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:234` | date de calcul inconnue | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:236` | arrivée en TCG : segment : intervalle à 80 % ; rang OCG sans intervalle, seuils de libellé provisoires | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:238` | fenêtre d’arrivée : délai mesuré sur 1 897 cartes, 2022 à 2025, non vérifié sur des cas nouveaux | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:243` | Dates des relevés de prix | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:252` | du {…} au {…} | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:254` | aucune : dates de relevé, sans mesure | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:256` | relevés pris à la main avant novembre 2026 | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:272` | Tous les signaux en tableau | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:277` | Archétype | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:278` | Signal | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:279` | Arrivée TCG (8 fois sur 10) | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:280` | Carte | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:281` | Dernier prix Cardmarket | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:282` | Banlist TCG | conforme | conforme, inchangé |
| — | `app/boutique/page.tsx:294` | · {…} sur {…} | conforme | conforme, inchangé |

### Signaux précoces (/early-signals)

18 textes : 16 conformes, 2 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/early-signals/opengraph-image.tsx:3` | Signaux précoces · YGO Meta. Vues hebdomadaires et co-occurrences en decks de tournoi. | conforme | conforme, inchangé |
| — | `app/early-signals/opengraph-image.tsx:9` | Boutique · Cartes récentes | conforme | conforme, inchangé |
| — | `app/early-signals/opengraph-image.tsx:10` | Signaux précoces | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:17` | , calcul du {…} | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:19` | Signaux précoces | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:37` | Boutique · Signaux précoces | conforme | conforme, inchangé |
| T33 | `app/early-signals/page.tsx:40` | Les cartes qui montent avant la méta. | titre : promesse (« qui montent avant la méta ») ; charte §6, exemple 7 | « Les cartes récentes et leur *place* dans les decks. » |
| T34 | `app/early-signals/page.tsx:45` | Nouvelles cartes qui entrent dans la méta, repérées par leurs vues, leurs co-occurrences et le tier de leur archétype. Score | intro : promesse (« entrent dans la méta »), aucun effectif ni date | « {n} cartes récentes notées de 0 à 100, calcul du {date} : vues sur une semaine, présence dans les decks de tournoi, tier de l’archétype. Score ⓘ » (n et date servis par `/early-signals`) |
| — | `app/early-signals/page.tsx:49` | Note de 0 à 100 : plus elle est haute, plus la carte est consultée et jouée avec les decks du moment. | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:58` | Carte | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:59` | Score | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:60` | Vues / sem. | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:74` | · score | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:91` | calcul du {…} | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:91` | date de calcul inconnue | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:93` | aucun intervalle : le score classe les cartes entre elles, il n’estime pas une quantité ; les vues sont un relevé unique | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:96` | Le score réunit trois mesures : les vues de la carte sur une semaine, sa présence dans les decks de la méta et le niveau de son archétype. | conforme | conforme, inchangé |
| — | `app/early-signals/page.tsx:97` | Les vues des cartes anciennes ne sont pas rafraîchies au même rythme que celles des cartes nouvelles. | conforme | conforme, inchangé |

### Graphe de synergies (/graph)

18 textes : 16 conformes, 2 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/graph/GraphView.tsx:133` | Staple générique | conforme | conforme, inchangé |
| — | `app/graph/GraphView.tsx:190` | Archétype | conforme | conforme, inchangé |
| — | `app/graph/GraphView.tsx:198` | Tous ( | conforme | conforme, inchangé |
| — | `app/graph/GraphView.tsx:212` | liens · survol : aperçu de la carte | conforme | conforme, inchangé |
| — | `app/graph/opengraph-image.tsx:3` | Graphe de synergies · YGO Meta. Cartes souvent jouées dans les mêmes decks. | conforme | conforme, inchangé |
| — | `app/graph/opengraph-image.tsx:9` | Graphe · Co-occurrence | conforme | conforme, inchangé |
| — | `app/graph/opengraph-image.tsx:10` | Graphe de synergies | conforme | conforme, inchangé |
| — | `app/graph/opengraph-image.tsx:11` | Cartes souvent jouées dans les mêmes decks | conforme | conforme, inchangé |
| — | `app/graph/page.tsx:16` | Graphe de synergies | conforme | conforme, inchangé |
| T35 | `app/graph/page.tsx:17` | Graphe de co-occurrence des cartes Yu-Gi-Oh! : un lien relie deux cartes souvent jouées dans les mêmes decks de tournoi. Source : {…}, date de calcul non enregistrée. | description de partage : « souvent » au lieu du seuil mesuré | « Graphe de co-occurrence des cartes Yu-Gi-Oh! : un lien relie deux cartes jouées ensemble dans au moins 15 % des decks de tournoi qui jouent l’une ou l’autre. Source : {…}, date de calcul non enregistrée. » |
| — | `app/graph/page.tsx:29` | Graphe · Co-occurrences | conforme | conforme, inchangé |
| — | `app/graph/page.tsx:32` | Les cartes qui se jouent ensemble . | conforme | conforme, inchangé |
| T36 | `app/graph/page.tsx:35` | Les {…} cartes les plus connectées. Un lien relie deux cartes souvent jouées dans les mêmes decks. | « souvent jouées » : le seuil est mesuré (15 %), autant l’écrire | « Les {200} cartes les plus connectées. Un lien relie deux cartes jouées ensemble dans au moins 15 % des decks qui jouent l’une ou l’autre. » |
| — | `app/graph/page.tsx:40` | date de calcul non enregistrée dans la base servie | conforme | conforme, inchangé |
| — | `app/graph/page.tsx:42` | pas d’intervalle : le graphe dessine des liens au-dessus d’un seuil, un lien proche du seuil peut apparaître ou disparaître d’un calcul à l’autre | conforme | conforme, inchangé |
| — | `app/graph/page.tsx:45` | % jouent les deux. | conforme | conforme, inchangé |
| — | `app/graph/page.tsx:45` | Deux cartes sont reliées quand, parmi les decks qui jouent l’une ou l’autre, au moins | conforme | conforme, inchangé |
| — | `app/graph/page.tsx:46` | Seules les 200 cartes les plus connectées sont affichées. | conforme | conforme, inchangé |

### Decks, index (/decks)

30 textes : 30 conformes, 0 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/decks/opengraph-image.tsx:3` | Decks TCG · YGO Meta. Composition par archétype : part des listes de tournoi qui jouent chaque carte. | conforme | conforme, inchangé |
| — | `app/decks/opengraph-image.tsx:9` | Decks · TCG | conforme | conforme, inchangé |
| — | `app/decks/opengraph-image.tsx:10` | Composition des decks | conforme | conforme, inchangé |
| — | `app/decks/opengraph-image.tsx:11` | Part des listes de tournoi TCG qui jouent chaque carte, par archétype | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:14` | decklists de tournoi TCG légales à la date du tournoi, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:20` | fenêtre courante | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:22` | Decks TCG : composition par archétype | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:23` | Composition de {…} archétypes Yu-Gi-Oh! TCG relevés dans au moins {…} listes de tournoi, sur {…} decks, {…}. Source : {…}. | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:67` | Cartes de base propres à l’archétype | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:93` | fenêtre inconnue | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:97` | calcul du {…} | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:97` | date de calcul inconnue | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:103` | Decks · TCG · {…} · {…} decks | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:104` | Composition des decks | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:107` | Pour chaque archétype relevé dans au moins | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:114` | Archétypes à {…} listes ou plus | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:115` | Listes couvertes sur {…} | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:116` | Part des decks de la fenêtre | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:117` | Des listes : carte « de base » | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:117` | dès {…} | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:124` | Aucun profil de composition dans la base servie. | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:130` | Archétypes avec fiche | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:137` | pas d’intervalle : à 8 listes il serait trop large pour être lu ; chaque pourcentage est donné avec son effectif | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:138` | carte de base : dans au moins | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:138` | des listes de l’archétype ; pourcentage sous une vignette : part des listes qui jouent la carte ; exemplaires : somme des médianes ; tier : celui de la tier list, même fenêtre | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:147` | Moins de | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:151` | listes, aucune part n’est calculée : la page de l’archétype montre ses listes. | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:171` | sous 8 listes, aucune part n’est calculée : seules les listes sont montrées | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:172` | listes : à 5 listes, 19 à 24 % des étiquettes changent d’un tirage de listes à l’autre, 9 à 13 % à 8 listes (mesuré sur Elfnote et Angelechy) | conforme | conforme, inchangé |
| — | `app/decks/page.tsx:172` | seuil de | conforme | conforme, inchangé |

### Fiche de deck (/decks/{slug})

57 textes : 57 conformes, 0 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/decks/[archetype]/opengraph-image.tsx:7` | Deck Yu-Gi-Oh! TCG : nombre de listes de tournoi relevées, fenêtre de mesure et source. | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:15` | Deck introuvable | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:15` | Decklists de tournoi TCG | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:18` | Deck · TCG | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:18` | Deck · TCG · tier {…} | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:23` | liste de tournoi TCG | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:23` | listes de tournoi TCG | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:24` | sur {…} decks · {…} | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:29` | Part des listes qui jouent chaque carte, exemplaires médians | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/opengraph-image.tsx:30` | Moins de {…} listes : contenu des listes relevées | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:19` | decklists de tournoi TCG légales à la date du tournoi, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:25` | 40 à 60 cartes, la pioche | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:25` | Main deck | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:26` | 15 cartes au plus, tenues à part et posées en cours de partie | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:26` | Extra deck | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:27` | 15 cartes au plus, échangées entre deux manches | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:27` | Side deck | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:55` | Deck introuvable | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:58` | Deck {…} : composition | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:92` | × | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:103` | DE BASE | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:145` | Aucune carte dans | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:145` | listes ou plus. | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:157` | listes qui jouent chaque carte et nombre d’exemplaires médian | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:163` | Carte | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:166` | Part des listes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:170` | Ex. | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:172` | Exemplaires | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:178` | DE BASE | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:178` | au moins {…} des listes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:184` | D’APPOINT | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:184` | de {…} à moins de {…} des listes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:191` | pas d’intervalle : à 8 listes il serait trop large pour être lu ; chaque pourcentage est donné avec son effectif | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:192` | part : listes qui jouent la carte sur | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:198` | des listes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:230` | Tournoi non précisé | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:269` | {…}, calcul du {…} | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:279` | Part des decks TCG | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:283` | Cartes de base au main deck | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:284` | Exemplaires de base, sur 40 à 60 | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:313` | Decks | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:318` | Composition · TCG · | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:326` | Part de méta par mois | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:329` | Zones du deck | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:336` | Listes récentes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:350` | pas d’intervalle : à 8 listes il serait trop large pour être lu ; chaque pourcentage est donné avec son effectif | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:351` | sous 8 listes, aucune part n’est calculée : seules les listes sont montrées | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:356` | de base : dans au moins | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:357` | cartes au main deck) ; exemplaires de base : somme des médianes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:361` | listes, aucune part n’est calculée : seules les listes relevées sont affichées | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:361` | sous | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:375` | Listes récentes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:384` | tournoi du {…} | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:384` | tournois du {…} au {…} | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:385` | listes les plus récentes | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:386` | aucune : listes et résultats relevés tels quels | conforme | conforme, inchangé |
| — | `app/decks/[archetype]/page.tsx:388` | résultat : place finale du joueur dans le tournoi ; ordre : date du tournoi, puis meilleur résultat | conforme | conforme, inchangé |

### Page d'archétype (/archetype/{slug})

90 textes : 89 conformes, 1 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/archetype/[slug]/ShareChart.tsx:83` | part mensuelle des decks TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:84` | intervalle à 95 % | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:88` | mois de moins de 100 decks, mois en cours | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:88` | mois en cours | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:94` | fenêtre de la tier list ({…}{…}) | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:95` | à {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:100` | decks relevés par mois (max. {…}) | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:110` | Part de {…} dans les decks de tournoi TCG, par mois, de {…} à {…}. Maximum {…} en {…} ({…} decks sur {…}). Dernier mois : {…} ({…} decks sur {…}). | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:168` | , en cours, {…} decks | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/ShareChart.tsx:180` | decks | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:8` | Archétype Yu-Gi-Oh! : part des decks de tournoi, fenêtre de mesure et source. | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:16` | Archétype | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:16` | Archétype introuvable | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:16` | Decklists de tournoi | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:19` | Archétype | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:19` | Decklists de tournoi TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:21` | Archétype · TCG · tier {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:25` | des decks de tournoi TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:30` | Archétype · OCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:34` | des decks de tournoi OCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:35` | · calcul du {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:38` | Aucun deck TCG dans la fenêtre courante | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:38` | Source : {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/opengraph-image.tsx:44` | Part mensuelle TCG, {…} à {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:28` | decklists de tournoi TCG, yugiohmeta.com | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:29` | seuils provisoires, non validés hors échantillon | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:60` | , calcul du {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:63` | , dernier relevé en {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:63` | le début des relevés | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:69` | Archétype introuvable | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:91` | Part de méta TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:92` | Decks sur {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:93` | Rang sur {…} archétypes | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:96` | Deck TCG sur {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:97` | Dernier mois joué en TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:100` | Part de méta OCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:101` | Decks OCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:103` | Score méta ×100 | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:106` | Rang OCG sur {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:137` | Tier list | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:144` | Archétype · TCG · {…} · {…} decks | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:145` | Archétype | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:159` | fenêtre précédente : | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:166` | Hors tier list : aucun deck TCG relevé | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:166` | de {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:172` | Composition du deck | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:177` | SIGNAL | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:197` | fenêtre inconnue | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:201` | part calculée sur {…} decks ; la tendance n’est affichée que si l’écart avec la fenêtre précédente dépasse le bruit d’échantillonnage | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:202` | aucun deck TCG dans la fenêtre, pas de part calculée | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:207` | OCG : | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:207` | calcul du {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:207` | date de calcul inconnue | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:213` | Tier : T0 à partir de 40 % des decks de la fenêtre, T1 à partir de 15 %, T2 à partir de 7 %, T3 à partir de 3 %. | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:214` | Tendance : comparaison avec la fenêtre précédente, affichée seulement si l’écart dépasse le bruit d’échantillonnage. | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:222` | Part de méta par mois | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:231` | bande : intervalle à 95 % de chaque part mensuelle ; pointillé : mois de moins de 100 decks et mois en cours | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:234` | Part du mois : decks de l’archétype divisés par tous les decks de tournoi TCG relevés ce mois-là. | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:235` | L’intervalle suppose des decks indépendants ; plusieurs listes d’un même joueur ou d’un même tournoi le rendent trop étroit. | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:239` | Tableau des valeurs | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:246` | Part mensuelle de | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:246` | dans les decks de tournoi TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:249` | Mois | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:250` | Part | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:251` | Decks | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:252` | Decks relevés | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:277` | Cartes clés | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:280` | Les | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:302` | ex. par deck | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:310` | au {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:312` | comptes exacts sur la fenêtre, pas d’intervalle : la liste ordonne les cartes, elle n’estime rien | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:314` | deck d’attache : au moins la moitié des decks qui jouent la carte sont de cet archétype ; statut : banlist TCG en vigueur | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:325` | Signal boutique | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:329` | Libellé | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:334` | indisponible | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:341` | Rang parmi les archétypes OCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:349` | Fort : rang | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:356` | Arrivée en TCG, intervalle à 80 % | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:361` | 75 à 202 jours après le premier deck OCG, délai mesuré sur 1 897 cartes sorties de 2022 à 2025 ; non vérifié sur des cas nouveaux | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:370` | Cartes du signal boutique de | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:373` | Carte | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:374` | Ordre dans le lot | conforme | conforme, inchangé |
| T37 | `app/archetype/[slug]/page.tsx:375` | Prix CM | abréviation « CM » inconnue d’un lecteur | « Prix Cardmarket » |
| — | `app/archetype/[slug]/page.tsx:376` | Banlist TCG | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:412` | decklists OCG (yugiohmeta.com), vues et prix Cardmarket (YGOPRODeck) | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:413` | calcul du {…} | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:413` | date de calcul inconnue | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:415` | arrivée en TCG : intervalle à 80 % ; rang et libellé sans intervalle, seuils provisoires | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:417` | ordre dans le lot : la première carte de tous les signaux affichés vaut 100, ce n’est pas une force de signal · | conforme | conforme, inchangé |
| — | `app/archetype/[slug]/page.tsx:420` | tous les signaux | conforme | conforme, inchangé |

### Méthode (/methode)

171 textes : 167 conformes, 0 à changer, 4 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/methode/opengraph-image.tsx:3` | Méthode · YGO Meta. Sources, seuils et résultats des validations de chaque outil, échecs compris. | conforme | conforme, inchangé |
| — | `app/methode/opengraph-image.tsx:9` | Méthode | conforme | conforme, inchangé |
| — | `app/methode/opengraph-image.tsx:10` | Sources, seuils et validations | conforme | conforme, inchangé |
| — | `app/methode/opengraph-image.tsx:11` | Résultats des validations de chaque outil, échecs compris | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:22` | Méthode | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:24` | Sources, dates de collecte, seuils et résultats des validations de chaque outil, échecs compris. Aucune formule. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:33` | Sources communes | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:35` | Tier list | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:37` | Évolution | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:38` | Prédictions | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:39` | Ban Radar | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:40` | Ban Radar, historique | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:41` | Signaux boutique | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:42` | Signaux précoces | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:115` | Rang médian des cartes touchées, bande du hasard à 90 % et base « staples les plus jouées », par banlist rejouée | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:119` | Liste | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:120` | Decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:121` | Rang médian | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:122` | Face au hasard (90 %) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:123` | Staples les plus jouées | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:137` | cartes touchées | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:137` | écartée ( | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:149` | Rang médian {…} ; hasard de {…} à {…} sur {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:185` | Méthode | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:188` | Sources, seuils et résultats des validations . | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:191` | Une section par outil, dans l’ordre de la navigation. Chaque méthode est décrite par ce qu’elle mesure ; les résultats mauvais restent dans les tableaux. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:194` | Sections de la page | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:202` | Sources communes | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:206` | Decks de tournoi | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:209` | Yugipedia, TCG et OCG, reconstituées à chaque collecte ; une nouvelle liste devient automatiquement un point de validation. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:211` | Cartes, vues et prix | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:212` | , du {…} au {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:212` | YGOPRODeck (fiches, vues par semaine, prix Cardmarket). {…} relevés de prix servis{…}. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:215` | Fenêtre de la tier list | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:222` | Seuils et leur origine | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:225` | Seuils appliqués sur le site et leur origine | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:228` | Mois atténué dans les séries | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:228` | moins de {…} decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:228` | à 100 decks, une part de 10 % est connue à ±6 points près | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:229` | 8 listes | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:229` | 9 à 13 % d’étiquettes instables à 8 listes, 19 à 24 % à 5 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:229` | Fiche de composition d’un archétype | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:230` | 600 decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:230` | Banlist retenue dans le backtest | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:230` | mesure du 14 août 2026 : la seule liste sous ce volume (OCG d’avril 2026, 416 decks à l’époque) tombait au niveau du hasard | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:231` | Archétype classé Rogue | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:231` | moins de 5 decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:231` | pas de part ni de tendance lisible en dessous | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:232` | 10 % / 25 % des archétypes | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:232` | Libellé boutique Fort / Modéré | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:232` | premiers 10 % et 25 % ; provisoires, non validés hors échantillon | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:232` | rang {…} / rang {…} sur {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:236` | documentation du projet et calculs des scripts | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:237` | seuils en vigueur au 17 novembre 2026 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:238` | les seuils de 8 listes et 600 decks viennent de mesures ; ceux du libellé boutique n’ont pas pu être validés (une seule série datée) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:243` | Tier list | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:246` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:246` | La part des decks de tournoi TCG de la fenêtre qui jouent chaque archétype, et l’écart avec la fenêtre précédente. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:247` | T0 dès 40 % des decks, T1 dès 15 %, T2 dès 7 %, T3 dès 3 %, Rogue en dessous ou sous 5 decks. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:248` | Affichée seulement si l’écart avec la fenêtre précédente dépasse le bruit d’échantillonnage, testé archétype par archétype. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:249` | La fenêtre courante compte quelques centaines de decks : un archétype à 2 % repose sur une dizaine de listes. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:252` | Tendances dues au hasard | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:254` | Nombre de tendances attendues par hasard | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:255` | Archétypes comparés | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:255` | Fausses tendances attendues | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:255` | Niveau du test | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:256` | environ 3 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:256` | environ 60 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:259` | tier list | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:260` | fenêtre {…} à {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:261` | ordre de grandeur, pas une mesure : il suppose des archétypes indépendants | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:269` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:269` | Pour chaque archétype, la part de ses listes qui jouent chaque carte, et le nombre médian d’exemplaires. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:270` | Carte de base dans au moins 80 % des listes, d’appoint dans au moins 20 % ; fiche à partir de 8 listes. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:271` | Fenêtre | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:271` | La même que la tier list : les effectifs des deux pages sont égaux. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:272` | Pas d’intervalle affiché : à 8 listes il serait trop large pour être lu ; chaque part est donnée avec son effectif. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:275` | Stabilité des étiquettes selon le nombre de listes | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:277` | Part des étiquettes de base ou d’appoint qui changent d’un tirage de listes à l’autre | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:278` | Listes par archétype | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:278` | Étiquettes qui changent | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:280` | 19 à 24 % | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:281` | 9 à 13 % | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:285` | rééchantillonnage des listes d’Elfnote et d’Angelechy | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:286` | mesure du 16 novembre 2026 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:287` | deux archétypes seulement ; l’écart entre 5 et 8 listes est net, sa valeur exacte ne l’est pas | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:292` | Évolution et parts mensuelles | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:295` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:295` | Chaque mois, la part des decks de tournoi TCG relevés qui jouent l’archétype. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:298` | Une bande à 95 % entoure chaque part. Elle s’élargit quand le mois compte peu de decks ou quand la part est proche de 50 %. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:300` | Moins de {…} decks dans le mois, ou mois en cours de relevé : point et segment en pointillé, plus pâles. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:300` | Mois atténués | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:303` | Intervalle minimal : il suppose des decks indépendants, plusieurs listes d’un même joueur ou d’un même tournoi le rendent trop étroit. Deux bandes qui se chevauchent ou non ne valent pas un test d’écart entre deux mois. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:308` | Mois relevés selon leur nombre de decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:310` | Nombre de mois relevés au-dessus et en dessous de 100 decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:311` | Période | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:314` | au moins {…} decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:319` | moins de {…} decks | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:326` | decks de tournoi TCG, {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:327` | aucun mois | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:329` | comptes exacts ; le dernier mois est incomplet tant qu’il n’est pas terminé | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:335` | Prédictions | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:338` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:338` | Le score méta attendu le mois suivant si la situation récente se prolonge, en ramenant les écarts vers la moyenne. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:339` | Pour l’essentiel la valeur du mois observé, corrigée d’une part de retour à la moyenne apprise sur l’historique. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:340` | Aucun intervalle par archétype : le modèle ne produit qu’une valeur. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:341` | N’anticipe ni les ruptures (banlist, nouvelle extension) ni l’arrivée d’un nouvel archétype. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:344` | Erreur, rejouée mois par mois sur l’historique | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:346` | Erreur de prévision comparée à deux références | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:347` | Erreur du modèle | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:347` | Référence | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:349` | environ 5 % de moins | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:349` | « rien ne change » (valeur du mois observé) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:350` | retour à la moyenne seul | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:350` | équivalente | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:354` | validation glissante dans le temps (notebook 05) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:355` | dernier calcul du modèle | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:356` | gain faible : le modèle fait à peine mieux que la valeur du mois observé | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:361` | Ban Radar | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:364` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:364` | La ressemblance de chaque carte avec le profil des cartes déjà touchées par Konami, sur six critères. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:365` | Critères | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:365` | Part des decks, archétype porteur, exemplaires joués, restriction en cours, élan sur 3 mois, position de pont. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:366` | Fenêtre | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:366` | Les 6 derniers mois de decks de tournoi TCG. | conforme | conforme, inchangé |
| B25 | `app/methode/page.tsx:367` | Un score de risque, pas une probabilité. Le méta Genesys, exclu des données, lui échappe. | **en attente du formulaire TOK-115** — section Ban Radar de /methode : limite conforme ; la section attend le verdict | voir § « Textes du Ban Radar en attente » |
| B26 | `app/methode/page.tsx:372` | Ban Radar contre l’historique | **en attente du formulaire TOK-115** — titre de section, conforme | voir § « Textes du Ban Radar en attente » |
| B27 | `app/methode/page.tsx:375` | Chaque banlist est rejouée avec les decks des 6 mois qui précèdent son entrée en vigueur, jamais avec des données postérieures. | **en attente du formulaire TOK-115** — section « Ban Radar contre l’historique » : la relecture (I6) demande la réserve sur le critère « pont » | voir § « Textes du Ban Radar en attente » |
| — | `app/methode/page.tsx:376` | Rangs médians qu’on obtiendrait en tirant au sort autant de cartes : 90 % des tirages tombent dans la bande. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:377` | Base de comparaison | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:377` | Classer simplement les cartes par part des decks (« staples les plus jouées »). | conforme | conforme, inchangé |
| B28 | `app/methode/page.tsx:381` | Rang médian des cartes touchées, liste par liste | **en attente du formulaire TOK-115** — titre de la figure, conforme | voir § « Textes du Ban Radar en attente » |
| — | `app/methode/page.tsx:384` | decks de tournoi (yugiohmeta.com), banlists (Yugipedia) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:385` | calcul du {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:387` | barre pâle : 90 % des rangs médians d’un tirage au hasard ; point : rang médian des cartes touchées ; rang 1 à gauche | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:391` | détail par liste | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:397` | Signaux boutique | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:400` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:400` | Les archétypes joués en OCG dont au moins 3 cartes clés ne sont pas encore sorties en TCG, classés par leur poids en OCG. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:402` | Libellé | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:404` | Rang parmi les {…} archétypes OCG suivis : Fort jusqu’au rang {…}, Modéré jusqu’au rang {…}. Seuils provisoires. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:405` | Rang parmi les archétypes OCG suivis. Seuils provisoires. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:407` | Arrivée en TCG | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:407` | Période où 8 archétypes sur 10 sont arrivés en TCG par le passé : 75 à 202 jours après le premier deck OCG, mesurée sur 1 897 cartes sorties de 2022 à 2025. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:408` | Rien n’est encore échu pour juger les signaux actuels ; la fenêtre d’arrivée n’a pas été vérifiée sur des cas nouveaux. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:411` | Lien entre OCG et TCG | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:414` | corrélation, | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:422` | Corrélation {…}, intervalle à 95 % de {…} à {…} | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:433` | parts OCG et TCG des archétypes, decks de tournoi | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:434` | décalage de {…}, recalcul du 16 novembre 2026 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:436` | segment : intervalle à 95 % ; l’ancienne valeur affichée (0,77 sur 43 archétypes) n’est plus reproductible | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:439` | Signal de juin 2026 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:441` | Évolution des prix des cartes du signal de juin 2026 comparée au marché | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:442` | Évolution du prix | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:444` | cartes du signal de juin 2026 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:445` | marché (toutes cartes suivies) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:449` | prix Cardmarket (YGOPRODeck) | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:450` | signal de juin 2026 | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:451` | une seule série datée : un échec net, mais pas une mesure de la fiabilité générale | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:456` | Signaux précoces | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:459` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:459` | Une note de 0 à 100 qui réunit les vues d’une carte récente sur une semaine, sa présence dans les decks de la méta et le niveau de son archétype. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:460` | Aucune à ce jour : la note ordonne les cartes, elle n’a pas été confrontée à ce que les cartes sont devenues. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:461` | Les vues des cartes anciennes ne sont pas rafraîchies au même rythme que celles des cartes nouvelles. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:466` | Graphe de synergies | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:469` | Ce que mesure | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:469` | Deux cartes sont reliées quand, parmi les decks qui jouent l’une ou l’autre, au moins 15 % jouent les deux. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:470` | Les 200 cartes les plus connectées ; {…} communautés de cartes détectées. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:471` | Cartes pont | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:471` | Cartes qui relient des groupes de cartes qui, sans elles, se jouent rarement ensemble. | conforme | conforme, inchangé |
| — | `app/methode/page.tsx:472` | La date du calcul n’est pas enregistrée dans la base servie ; un lien proche du seuil peut changer d’un calcul à l’autre. | conforme | conforme, inchangé |

### Commun : navigation, pied de page, erreurs, composants

71 textes : 65 conformes, 6 à changer, 0 en attente TOK-115.

| # | Fichier:ligne | Texte actuel | Problème | Proposition |
|---|---|---|---|---|
| — | `app/card-images/[...path]/route.ts:16` | Not found | réponse HTTP 404 d’une image, jamais lue par une personne | conforme, inchangé |
| — | `app/card-images/[...path]/route.ts:24` | Not found | réponse HTTP 404 d’une image, jamais lue par une personne | conforme, inchangé |
| T38 | `app/error.tsx:27` | Les données ne répondent pas. | titre : personnification (« les données ne répondent pas ») | « Données *indisponibles*. » |
| T39 | `app/error.tsx:30` | L’API n’a pas répondu ou a renvoyé une erreur. Le reste du site n’est pas touché : réessaie dans un instant. | impératif et tutoiement (« réessaie ») ; le bouton « Réessayer » suffit | « L’API n’a pas répondu ou a renvoyé une erreur. Les autres pages ne sont pas touchées. » |
| — | `app/error.tsx:34` | Réessayer | conforme | conforme, inchangé |
| — | `app/error.tsx:36` | Référence : | conforme | conforme, inchangé |
| — | `app/layout.tsx:20` | YGO Meta · Analyse de la méta Yu-Gi-Oh! | conforme | conforme, inchangé |
| — | `app/layout.tsx:21` | %s · YGO Meta | conforme | conforme, inchangé |
| — | `app/layout.tsx:24` | Analyse de la méta Yu-Gi-Oh! TCG et OCG à partir des decklists de tournoi : tier list, prédictions, risque de ban et signaux pour les boutiques. | conforme | conforme, inchangé |
| — | `app/not-found.tsx:6` | Page introuvable | conforme | conforme, inchangé |
| — | `app/not-found.tsx:12` | Erreur 404 | conforme | conforme, inchangé |
| T40 | `app/not-found.tsx:15` | Cette page n’est pas dans le deck . | titre : jeu de mots, ne décrit pas la situation | « Page *introuvable*. » |
| T41 | `app/not-found.tsx:18` | L’adresse est fausse ou la page a été déplacée. Les outils sont toujours là. | deuxième phrase sans information | « L’adresse est fausse ou la page a été déplacée. » |
| — | `app/not-found.tsx:22` | Retour à l’accueil | conforme | conforme, inchangé |
| T42 | `app/not-found.tsx:24` | Voir la tier list | appel à l’action (« voir ») | « Tier list » |
| — | `components/ds/explain.tsx:48` | L{…} {…} | tracé SVG relevé par l’extracteur, pas un texte | conforme, inchangé |
| — | `components/ds/explain.tsx:199` | Méthode | conforme | conforme, inchangé |
| — | `components/ds/explain.tsx:204` | Détail dans la page Méthode | conforme | conforme, inchangé |
| — | `components/ds/page.tsx:165` | Source : | conforme | conforme, inchangé |
| — | `components/ds/page.tsx:169` | Incertitude : | conforme | conforme, inchangé |
| — | `components/ds/tags.tsx:31` | En hausse | conforme | conforme, inchangé |
| — | `components/ds/tags.tsx:34` | En baisse | conforme | conforme, inchangé |
| — | `components/ds/tags.tsx:48` | Illimitée | conforme | conforme, inchangé |
| — | `components/ds/tags.tsx:49` | Semi-limitée | conforme | conforme, inchangé |
| — | `components/ds/tags.tsx:50` | Limitée | conforme | conforme, inchangé |
| — | `components/hover-preview-context.tsx:23` | useHoverPreview must be used within a HoverPreviewProvider | message technique (erreur de développement), hors charte | conforme, inchangé |
| — | `components/nav.tsx:21` | Méta | conforme | conforme, inchangé |
| — | `components/nav.tsx:23` | Tier list | conforme | conforme, inchangé |
| — | `components/nav.tsx:25` | Évolution | conforme | conforme, inchangé |
| — | `components/nav.tsx:26` | Prédictions | conforme | conforme, inchangé |
| — | `components/nav.tsx:29` | Ban Center | conforme | conforme, inchangé |
| — | `components/nav.tsx:34` | Signaux boutique | conforme | conforme, inchangé |
| — | `components/nav.tsx:35` | Signaux précoces | conforme | conforme, inchangé |
| — | `components/nav.tsx:152` | YGO META | conforme | conforme, inchangé |
| — | `components/nav.tsx:193` | Menu | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:6` | Méta | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:8` | Tier list | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:9` | Évolution | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:10` | Prédictions | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:16` | Ban Radar | conforme | conforme, inchangé |
| T43 | `components/site-footer.tsx:17` | Impact des cartes | lien du pied : l’onglet s’appelle « Cartes à impact » | « Cartes à impact » |
| — | `components/site-footer.tsx:18` | Simulateur de ban | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:24` | Signaux boutique | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:25` | Signaux précoces | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:26` | Graphe de synergies | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:27` | Méthode | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:43` | YGO META | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:46` | Méta Yu-Gi-Oh! TCG et OCG, calculée sur les decklists de tournoi. | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:51` | Données au | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:55` | Mise à jour chaque lundi | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:79` | Sources : decklists de tournoi yugiohmeta.com · cartes et images YGOPRODeck · banlists Yugipedia · prix Cardmarket. | conforme | conforme, inchangé |
| — | `components/site-footer.tsx:83` | Site indépendant, sans lien avec Konami. Yu-Gi-Oh! est une marque de ses ayants droit. Scores et signaux : estimations statistiques, sans garantie. | conforme | conforme, inchangé |
| — | `components/smart-search.tsx:72` | Rechercher une carte… | conforme | conforme, inchangé |
| — | `components/smart-search.tsx:73` | Meta+K Control+K | raccourci clavier (attribut `aria-keyshortcuts`), pas un texte | conforme, inchangé |
| — | `components/smart-search.tsx:77` | ⌘K | conforme | conforme, inchangé |
| — | `components/ui/badge.tsx:35` | & VariantProps | code relevé par l’extracteur, pas un texte | conforme, inchangé |
| — | `components/ui/info-tooltip.tsx:37` | Définition : {…} | conforme | conforme, inchangé |
| — | `components/ui/info-tooltip.tsx:48` | i | conforme | conforme, inchangé |
| — | `lib/api.ts:39` | NEXT_PUBLIC_API_URL={…} est relative : côté serveur, définir API_URL (adresse absolue de l'API). | message technique (erreur levée côté serveur, journal), jamais affiché au lecteur : hors charte | conforme, inchangé |
| — | `lib/api.ts:49` | API error {…}: {…} | message technique (erreur levée côté serveur, journal), jamais affiché au lecteur : hors charte | conforme, inchangé |
| — | `lib/api.ts:59` | API error {…}: /archetypes/{…} | message technique (erreur levée côté serveur, journal), jamais affiché au lecteur : hors charte | conforme, inchangé |
| — | `lib/api.ts:67` | API error {…}: /decks/{…} | message technique (erreur levée côté serveur, journal), jamais affiché au lecteur : hors charte | conforme, inchangé |
| — | `lib/api.ts:104` | API error {…}: /simulate-ban | message technique (erreur levée côté serveur, journal), jamais affiché au lecteur : hors charte | conforme, inchangé |
| — | `lib/format.ts:73` | Top {…} | conforme | conforme, inchangé |
| — | `lib/og.tsx:24` | Token {…} introuvable dans globals.css | message technique (erreur de build), hors charte | conforme, inchangé |
| — | `lib/og.tsx:44` | Source : {…} | conforme | conforme, inchangé |
| — | `lib/og.tsx:102` | radial-gradient(circle at 88% 108%, {…}, transparent 58%) | valeur CSS relevée par l’extracteur, pas un texte | conforme, inchangé |
| — | `lib/site.ts:16` | YGO Meta | conforme | conforme, inchangé |
| — | `types/index.ts:3` | Modéré | conforme | conforme, inchangé |
| — | `types/index.ts:4` | Modéré | conforme | conforme, inchangé |
| — | `types/index.ts:4` | Élevé | conforme | conforme, inchangé |
