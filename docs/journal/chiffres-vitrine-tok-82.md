# Chiffres de vitrine et fenêtres du notebook 11 (TOK-82, jalon n°3, 2026-11-18)

Relevé de chaque chiffre de `frontend/src/lib/site-facts.ts`, remesuré sur la base de référence en lecture seule
(`file:…/data/yugioh.db?mode=ro`, dernier deck du 2026-11-14, aucune donnée nouvelle depuis les calculs du 16/11).
Rien d'affiché ne change avant le formulaire de Thomas (`docs/planning/2026-11-18/decisions-prises.md`, section
« Jalon 3 — TOK-82 ») ; la modification du front est dans un commit séparé, le dernier de la branche.

Le sous-agent `data-scientist-ygo` n'a pas pu être lancé (l'outil d'autorisation a refusé le lancement de sous-agents
dans cette session) : les chiffres statistiques ont été recalculés avec les scripts existants, sans relecture tierce.

## Méthode

- Comptages : requêtes SQL directes (`tournament_decks`, `deck_legality`, `cards`, `card_prices`, `graph_communities`).
- Signal OCG → TCG : `scripts/evaluate_prediction.py --part B` (lecture seule, graine 42, 2 000 permutations,
  bootstrap par archétype), relancé le 18/11.
- Backtest du Ban Radar : table `ban_backtest_lists` (servie, `build_ban_history.py` du 16/11) ; top 10 par type rejoué
  avec `build_ban_radar.backtest_lists` (même boucle que `--backtest`), sans écriture.
- Corrélation `ocg_score` / `share_ocg` : Spearman sur `ocg_archetype_scores` (89 archétypes, calcul du 16/11).

## Relevé

| Chiffre (`SITE_FACTS`) | Affiché | Mesuré le 18/11 | Source | Écart |
|---|---|---|---|---|
| `decklists` | 23 948 | 23 948 (2023-05-05 → 2026-11-14) | `tournament_decks` | aucun |
| `decklistsTcg` / `decklistsOcg` | 11 618 / 12 330 | 11 618 / 12 330 | `tournament_decks.ocg` | aucun |
| — légales parmi elles | « légales à la date du tournoi » (accueil, `/methode`) | **22 422** (TCG 10 369, OCG 12 053) ; 611 illégales (334 TCG, 277 OCG) ; 915 TCG Genesys non évaluables | `deck_legality` | **texte faux** : les 23 948 ne sont pas toutes légales |
| `cardsTracked` | 13 797 | **14 084** (13 982 avec un prix Cardmarket > 0) | `cards`, `card_prices` | **+287** (cartes ajoutées par `fetch_new_cards.py`) |
| `ocgTcgCorrelation` | 0,53 | 0,529 (lag 4, n = 652, OCG à partir de 2024) | `evaluate_prediction.py --part B` | aucun |
| `ocgTcgCorrelationCi` | [0,43 ; 0,59] | [0,427 ; 0,589] (bootstrap par archétype) | idem | aucun |
| `ocgTcgArchetypes` | 105 | 105 | idem | aucun |
| `ocgTcgLagRange` | « 2 à 6 mois » | r interne 0,60-0,61 aux lags 1-3, 0,53 à 4, 0,47 à 5, 0,45 à 6 ; IC des lags 2 à 6 qui se chevauchent ; meilleur lag au bootstrap : 3 (41 %), 1 (31 %), 2 (28 %), 4 (0 %) | idem | aucun ; « 4 mois » reste exclu |
| `ocgScoreShareRho` / `ocgScoreArchetypes` | 0,94 / 89 | 0,9396 / 89 | `ocg_archetype_scores` | aucun |
| `arrivalWindowCards`, `arrivalCoverage` | 1 897 ; 67 % (2024), 62 % (2025) | non recalculé ici | lot 20 (A2) ; formulaire TOK-130 point 1 | traité par le formulaire TOK-130 (jalon 2) |
| `graphCommunities` | 63 | 63 communautés sur 663 cartes | `graph_communities` | aucun sur la table servie ; mais le graphe est périmé (1 402 nœuds recalculés, TOK-136) et sa date de calcul est inconnue |
| `banBacktestLists`, `banTop10HitsGeneric`, `banTop10HitsArchetype` | 10 ; 6 ; 19 | 10 ; 6 ; 19 (Ash Blossom première des génériques sur les 10 listes) | `backtest_lists`, TCG retenues | aucun |
| `banTop25` TCG | 10 listes, 29 contre 16, mieux 6, moins bien 1, rang médian meilleur 3 | identique (2024-04-15 → 2026-10-19) | `ban_backtest_lists` | aucun |
| `banTop25` OCG | 10 listes, 41 contre 18, mieux 9, moins bien 1, rang médian meilleur 8 | identique (2024-04-01 → 2026-10-01) | idem | aucun ; `verdictMatches` reste vrai |
| `banBacktestDate`, `banBacktestTotalLists` | 2026-11-16 ; 20 | 2026-11-16 ; 20 | idem | aucun |

Deux écarts touchent ce que le site affiche : le nombre de cartes suivies (13 797 contre 14 084) et la mention
« légales à la date du tournoi » accolée aux 23 948 listes (accueil, section des sources ; `/methode`, glossaire des
données), alors que 1 526 de ces listes (6,4 %) sont illégales ou Genesys et sont écartées de tous les calculs. Le
commentaire de `site-facts.ts` (« Decklists légales + Genesys ») est faux aussi : 23 948 est le total relevé.

Le nombre de communautés est exact pour le graphe affiché, mais rien ne date ce graphe : la proposition le qualifie
(663 cartes, non recalculé au rafraîchissement du 16/11) au lieu d'inventer un chiffre récent.

## Notebook 11

Obsolète, déjà marqué comme tel : la première cellule dit « Remplacé le 2026-11-18 (lot 20, ticket A1) », la cellule
d'écriture est retirée (cellule 13), et aucune table servie n'en dépend (`early_card_signals` vient de
`scripts/build_early_signals.py`, dont la référence est le dernier deck TCG relevé, `TCG_DAYS` = 168 jours). Ses fenêtres
sont relatives à la date du jour depuis le premier passage de TOK-82 (`6c30c95`). Aucune correction : le formulaire
propose de le laisser tel quel ou de l'archiver.

## Vérifications

- `python scripts/check.py` : vert avant le commit du front (étapes front, SERVED_TABLES et backtest exécutées).
- Captures : voir le commit du front (dernier de la branche) et le compte rendu du jalon.
