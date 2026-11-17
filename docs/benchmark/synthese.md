# Benchmark fonctionnel des sites de méta de jeux de cartes

Vérifié le 2026-11-16 par lecture de pages publiques (aucun compte, aucun formulaire). 20 sites, 39 fonctionnalités, 780 cases : **155 oui, 18 partiel, 36 non, 571 non vérifié (73 %)**. Détail dans `benchmark.xlsx` / `benchmark.csv`, définitions dans `fonctionnalites.md`.

## Limite principale
Dix pages ont répondu 403 et quelques autres 404 ou sont restées vides (HSReplay, Moxfield, AetherHub, InkDecks, Marvel Snap Zone, 17Lands, Trainer Hill…). Les cases de ces sites reposent sur des extraits de recherche ou restent « non vérifié ». Les chiffres ci-dessous comptent des preuves vues, pas des absences prouvées : « non vérifié » ne veut pas dire « non ». Sites annoncés au brief mais écartés faute de page lisible : HSGuru (403 sur la seule page tentée).

## Minimum attendu (présent sur au moins la moitié des sites vérifiables)
Résultats de tournois (11 sites), constructeur de decks (11), part de méta en pourcentage (10), filtres période/format (9), base de decklists (9), recherche avancée de cartes (9), articles et guides (9), compte utilisateur (8). Une tier list ou un classement existe sur 11 sites, mais seuls 5 la présentent avec paliers (6 la donnent sans palier : points, nombre de decks).

## Fonctionnalités rares (1 à 4 sites)
Matchups entre archétypes (3 sites : Limitless Pocket, Trainer Hill, HSReplay), prix de cartes (3), prix d'un deck (3), alertes de prix (2 : YGOPRODeck, MTGGoldfish), mouvements de prix (1 : MTGGoldfish, page « movers » non ouverte, vue par le lien du menu), évolution de la part dans le temps (1 : EDHREC, avec une courbe sur 8 semaines), simulateur de boosters (1), historique des changements de cartes (2), API publique (2 : YGOPRODeck, PokeData), application compagnon ou tracker (4), collection personnelle (5), forum ou commentaires (2).

## Fonctionnalités où le projet est seul (dans les pages vues)
- Signal précoce (archétype joué en OCG avant sa sortie en TCG) : aucun des 7 sites dont la navigation complète a été lue n'en montre ; 13 sites restent « non vérifié ».
- Prédiction de bans (Ban Radar, score de risque 0-100).
- Suivi public de fiabilité : backtest publié (dix listes TCG, dix OCG) et journal de prédictions daté.
- Simulateur de ban.
Ces quatre cases sont « non » sur les 7 sites à navigation lue et « non vérifié » ailleurs : l'affirmation « seul » vaut pour l'échantillon ouvert, pas pour l'ensemble du marché. Le graphe de synergies a un équivalent partiel (EDHREC : liste de combos).

## Où le projet est en retrait
9 oui et 8 partiel sur 39. Absent : constructeur de decks, import/export, decklists complètes, pages de tournois, matchups, historique de prix, alertes, collection, comptes, articles, API publique, interface multilingue (français seul). Prix : seulement le prix Cardmarket dans le signal boutique. Ce sont des fonctionnalités de service ; la différence du projet est sur les prédictions, pas sur la couverture.

## Enseignements
1. Aucun site ouvert ne publie de mesure de fiabilité de ses propres prédictions : l'écart se situe là (backtest, journal daté).
2. Les sites Yu-Gi-Oh voisins sont des classements de parts de decks, sans matchups ni évolution visibles ; YGOPRODeck est le plus riche (prix, alertes, collection, API, Premium 4,99 €/mois).
3. Les matchups existent surtout hors Yu-Gi-Oh (Limitless Pocket, HSReplay, Trainer Hill) : une page de matchups entre archétypes serait une piste, la base de decks permettant des confrontations seulement si les résultats de tour sont stockés (non vérifié ici).
4. Le modèle économique dominant est un palier léger : retrait de publicité via Patreon (Limitless, EDHREC) ou abonnement à 5-6 $ par mois (MTGGoldfish, YGOPRODeck).
5. Les prix et l'historique de prix sont le terrain de MTGGoldfish et YGOPRODeck ; le projet n'a pas de courbe de prix (TOK-103 au backlog).

## Cases « non vérifié » à revoir
Priorité à rouvrir à la main (navigateur, hors pare-feu anti-robot) : HSReplay (tier list, matchups, Premium, prix), Moxfield (Pro, prix, historique), InkDecks (tier list, parts), Marvel Snap Zone et Snap.fan (win rate, tracker), AetherHub, 17Lands (colonnes, filtres), Trainer Hill (page non rendue), PokeData (méta), EGMAN (pas de page méta ouverte). Pour les sites Yu-Gi-Oh : page « Ban List » de yugiohmeta.com (lien vu, URL testée 404), prix et statistiques de cartes de yugiohmeta.com, contenu des pages d'archétype, historique des listes de bans sur les trois sites. Les 7 sites à navigation lue ont encore 9 à 17 cases « non vérifié » chacun, surtout des pages de détail non ouvertes.

## Sources
Les pages ouvertes (avec leur état) sont listées dans l'onglet « Sources » de `benchmark.xlsx` ; pages principales :
- https://www.yugiohmeta.com, https://www.yugiohmeta.com/tier-list
- https://www.masterduelmeta.com, /tier-list, /top-cards
- https://ygoprodeck.com, /premium/, /card-database/, /api-guide/
- https://limitlesstcg.com, /decks, /decks/284 ; https://pocket.limitlesstcg.com ; https://play.limitlesstcg.com/decks?game=POCKET ; https://onepiece.limitlesstcg.com, /decks
- https://www.mtggoldfish.com, /metagame/standard, /premium ; https://www.mtgtop8.com, /format?f=ST
- https://edhrec.com ; https://www.pokedata.ovh ; https://egmanevents.com ; https://dreamborn.ink ; https://snap.fan
- Extraits de recherche (sources secondaires) : hsreplay.net, Moxfield (wiki public), inkdecks.com, 17Lands (articles tiers), aetherhub.com (2019-2020), Trainer Hill (projet metadex), marvelsnapzone.com.
- Colonne « Yugioh Meta Analyzer » : `context.md` et `frontend/src/app/` de ce dépôt.
