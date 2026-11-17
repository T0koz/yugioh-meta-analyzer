# Enseignements du benchmark — matière pour un futur brainstorming

Source : `benchmark.xlsx` (20 sites, 39 fonctionnalités, relevé du 2026-11-16). **Limite** : 73 % des cases sont
« non vérifié » (sites bloquant la lecture automatique). Les conclusions décrivent les sites lisibles, pas tout le
marché ; « seul » veut dire « seul parmi les pages ouvertes ».

## 1. Le positionnement en une phrase
Les concurrents décrivent la méta **telle qu'elle est** ; Yugioh Meta Analyzer est le seul, dans l'échantillon, à
dire **ce qu'elle va devenir et à publier s'il s'est trompé**.

## 2. Trois cercles

| Cercle | Fonctionnalités | Présence chez les autres | Chez nous |
|---|---|---|---|
| **Notre avantage** | Signal précoce OCG → TCG, prédiction de bans, suivi public de fiabilité, simulateur de ban | 0 site confirmé | oui |
| **Rare, et on l'a déjà** | Évolution de la part dans le temps (1 site), historique des banlists (0 confirmé), graphe de combos (1) | quasi absent | oui ou partiel |
| **Minimum attendu, absent chez nous** | Résultats de tournois (11), constructeur de decks (11), part de méta (10, on l'a), base de decklists (9), articles (9), compte (8) | courant | non ou partiel |

## 3. Conclusions

1. **La fiabilité publique est la marque.** Personne ne mesure ses propres prédictions. En faire le cœur visible
   du site : page Ban Predictor contre l'historique (TOK-55, en file), page « nos prédictions et leur bilan »
   depuis le journal daté, bilan affiché à chaque banlist.
2. **On sous-exploite deux raretés qu'on possède déjà.** L'évolution de la méta dans le temps (`/evolution`) et
   l'historique des banlists (`banlist_history`, 10 listes TCG et OCG) n'existent presque nulle part. Les relier :
   une frise « méta + bans + nos prédictions » serait un objet unique.
3. **Le minimum attendu se gagne avec les données qu'on a.** Résultats de tournois, decklists complètes, cartes
   les plus jouées, filtres : tout est déjà dans `tournament_decks` et `deck_cards`. La page Decks (TOK-114) en
   couvre une partie ; une page « tournois » serait peu coûteuse.
4. **Ne pas courir après le « service ».** Constructeur de decks, collection, forum, comptes, articles : terrain
   saturé (YGOPRODeck, MTGGoldfish), coûteux, sans lien avec notre avantage. À ne faire que s'il sert une prédiction.
5. **Les prix sont occupés, mais pas « prix + demande prévue ».** MTGGoldfish et YGOPRODeck ont prix, historique,
   alertes. Notre angle unique : le prix d'une carte **et** sa demande prévue (signal boutique). C'est la boutique
   par archétype (TOK-103) avec courbes, et plus tard une alerte « carte sous-cotée avant son arrivée en TCG ».
6. **Les matchups sont rares en Yu-Gi-Oh.** Ils existent ailleurs (Limitless Pocket, HSReplay, Trainer Hill).
   Possible chez nous seulement si les résultats manche par manche sont disponibles : à vérifier avant d'y penser.
7. **La langue limite l'audience.** Interface en français seul ; la scène TCG est largement anglophone.
   Une version anglaise multiplierait l'audience potentielle sans toucher au produit.
8. **Le modèle économique du secteur est léger** : retrait de pub par Patreon (Limitless, EDHREC) ou abonnement
   à 5-6 $ par mois (MTGGoldfish, YGOPRODeck), plus des liens d'affiliation (4 sites). Cohérent avec le referral
   boutique et une API de prédictions (phase C), que 2 sites seulement proposent en API publique.

## 4. Questions pour le brainstorming
- Le site est-il un **outil de prédiction** (resserré, unique) ou une **référence méta complète** (large, concurrencé) ?
- Quelle forme donner à la fiabilité publique pour qu'elle se voie dès l'accueil, sans ton publicitaire ?
- Faut-il une version anglaise, et quand (avant ou après la mise en ligne) ?
- Une page tournois et des decklists complètes : minimum à fournir, ou porte d'entrée vers nos prédictions ?
- Prix : jusqu'où aller (courbes, alertes) sans devenir un clone de MTGGoldfish ?
- Matchups : vaut-il la peine de vérifier les données manche par manche ?
- Monétisation : affiliation boutique, abonnement léger, API de prédictions — laquelle d'abord, et pour qui ?

## 5. À compléter avant de trancher
Rouvrir à la main (navigateur) les sites bloqués : HSReplay, Moxfield, 17Lands, InkDecks, Marvel Snap Zone,
Trainer Hill, et les pages « Ban List » et prix de yugiohmeta.com. Les cases de notre avantage (cercle 1) sont
« non vérifié » sur 13 sites : la conclusion 1 doit être confirmée avant d'être affichée publiquement.

- **Ajout demandé par Thomas (18/11)** : regarder **Duelingbook** (duelingbook.com), simulateur de duels Yu-Gi-Oh! en ligne : fonctionnalités, public, ce qu'il propose autour des decks et de la méta, et s'il peut servir au projet (tests de combos à la main, communauté).
