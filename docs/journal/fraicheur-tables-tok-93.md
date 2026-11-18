# Contrôle de fraîcheur des tables servies (TOK-93, Jalon 1, 2026-11-18)

Branche `claude/j1-tok-129-93-signaux-fraicheur-d1344d`. Lecture seule sur les bases : rien d'écrit en base, rien
d'affiché ne change. Relu par `gardien-donnees` (ses corrections sont intégrées). Contexte du ticket : `meta_tier_list`
est restée figée 5 mois sans alerte.

## En clair (pour Thomas)

1. Chaque lundi, en dernière étape du job (`refresh_decks.py`), un contrôle vérifie que les 19 tables servies par l'API
   ont été recalculées récemment, et que l'API yugiohmeta `/top-decks` répond. Une table périmée ou l'API en erreur font
   échouer le job (code 1). Le résultat est écrit dans `data/fetch_health.jsonl` et lisible par `--status`.
2. Le contrôle tourne **après** la reconstruction de `serving.db` : il ne peut pas bloquer la mise à jour du site.
3. Au 18/11 : 12 tables à jour ; 3 périmées connues, tolérées jusqu'au 31/12 (graphe des cartes et ses communautés, 663
   cartes au lieu de 1 402, TOK-136 ; vues des signaux précoces figées au 13/06) ; 2 sans date (`card_cooccurrence`,
   `cards`) ; 2 lues par aucune page (`meta_tier_list`, figée au 17/06, et `archetype_trend`). L'API répond (HTTP 200).
4. Une tolérance a une date d'expiration : passé le 31/12, ces tables refont échouer le contrôle. Une table vide, absente
   ou illisible n'est jamais tolérée. Le formulaire propose de valider ce choix et les seuils.

## Commandes

```bash
python scripts/check_freshness.py                        # yugioh.db (celle du dépôt principal depuis un worktree) + endpoint
python scripts/check_freshness.py --db data/serving.db   # la base qui part en ligne ; dates de référence lues dans yugioh.db
python scripts/check_freshness.py --status               # derniers contrôles journalisés (code 1 si le dernier a échoué)
python scripts/refresh_decks.py --status                 # santé des fetchs + fraîcheur des decks + dernier contrôle des tables
python scripts/check_freshness.py --sans-endpoint --sans-journal --today 2026-12-01   # rejeu, sans réseau ni écriture
```

Branchements :
- **`scripts/refresh_decks.py`** (job launchd du lundi) : dernière étape, après `serving`, lancée même si une étape amont
  a échoué ; elle contrôle `data/serving.db` contre `data/yugioh.db` et teste l'endpoint. Son échec s'ajoute au code
  de sortie et la sortie est dans `~/Library/Logs/yugioh-refresh-decks.log`.
- **`scripts/deploy_prebuilt.py`**, étape « 2. Base de service » : refuse le déploiement si une table est périmée (sans
  appel réseau ni journal).
- **Pas dans `refresh_all.py`** : un code 1 y faisait sauter la reconstruction de `serving.db` dans `refresh_decks.py`
  (étape aval bloquée), et la cause se perdait dans le journal (relecture du gardien). **Pas dans
  `build_serving_db.py --check`** : `check.py` le lance à chaque modification de `backend/` ou `scripts/`, des pushes
  sans rapport auraient été bloqués.

Journal : une ligne `{"step": "fraicheur_tables", "ok", "db", "controle_du", "perimees", "perimees_connues",
"non_datees", "non_lues", "ignorees", "endpoint", "details", "at"}` par contrôle, dans le `data/fetch_health.jsonl` du
checkout courant (fichier ignoré par Git). Nom d'étape distinct de `"freshness"`, que `refresh_decks.py` relit pour
vérifier que le nombre de decks ne baisse pas.

Test : `backend/tests/test_check_freshness.py` (20 cas sur une base synthétique, sans `yugioh.db` ni réseau : l'endpoint
est remplacé par une fonction de test), lancé par `python scripts/check.py` avec le reste de `backend/tests`.

## Règles, table par table

Date la plus fiable disponible, dans cet ordre : date de calcul (`computed_at`) comparée à la date du contrôle ; date
des données (`as_of`, dernier deck d'un extrait, mois, dernier relevé de prix) comparée au dernier deck relevé ;
contrôle de cohérence avec une autre table ; sinon « non datée » (dit, rien n'est conclu). Avant toute règle : table
absente, vide, colonne de date entièrement vide ou requête en erreur → PÉRIMÉE, jamais tolérée.

| Table | Source de la date | Résultat au 18/11 |
|---|---|---|
| `archetype_card_profile` | `computed_at` ; `window_end` contre le mois du dernier deck TCG | ok |
| `archetype_recent_decks` | liste la plus récente contre le dernier deck TCG | ok (0 j) |
| `archetype_recent_deck_cards` | fille de la précédente (même script) : son statut, et 0 ligne orpheline exigée | ok |
| `archetype_trend` | aucune colonne de date (notebook 04) | non lue (aucun routeur) |
| `ban_backtest_lists` | dernière banlist en vigueur de chaque format couverte (ligne retenue ou écartée) ; `computed_at` non retenu : `build_ban_history.py` n'est pas dans la chaîne et ne change qu'avec une nouvelle liste | ok |
| `ban_backtest_cards` | fille de `ban_backtest_lists` sur (format, date) : une liste écartée n'y a jamais de cartes | ok |
| `ban_radar`, `card_impact` | `as_of` contre le dernier deck TCG | ok (0 j) |
| `boutique_buy_signals`, `ocg_archetype_scores` | `computed_at` | ok |
| `boutique_price_history` | `computed_at` et dernier relevé de prix | ok |
| `card_cooccurrence` | aucune colonne de date (notebook 02) | non datée |
| `card_graph_metrics` | aucune date ; ses nœuds doivent être ceux du graphe de `card_cooccurrence` (Jaccard ≥ 0,3, ≥ 5 decks, seuils du notebook 03 et de `bridge_date.py`) | **périmée connue** : 663 contre 1 402 (TOK-136) |
| `graph_communities` | aucune date ; cartes réparties = nœuds du même graphe | **périmée connue** : 663 contre 1 402 (TOK-136) |
| `cards` | aucune date d'ajout ; servie pour les noms et les images | non datée |
| `early_card_signals` | `computed_at` ; `as_of` contre le dernier deck TCG ; **vues** : `cards.views_week` comparée à l'instantané `data/raw/cards.json` (daté par son commit, 13/06), car c'est cette table qui sert les vues | **périmée connue** : vues de 158 j |
| `meta_predictions` | `computed_at` ; `data_month` contre le mois du dernier deck | ok |
| `meta_scores` | dernier mois contre le mois du dernier deck | ok |
| `meta_tier_list` | `scraped_at` | non lue : 154 j, aucun routeur ne la lit depuis TOK-97 |

Une table qu'aucun routeur ne lit (même expression que la garde de `build_serving_db.py`) est « non lue », quel que soit
son statut : signalée, sans faire échouer. Sur `serving.db`, qui n'a ni `tournament_decks` ni `banlist_history`, les
dates de référence viennent de `yugioh.db` (option `--reference`, trouvée seule à défaut) ; sans référence, les
comparaisons sont « ignorées » et le résumé le dit.

## Endpoint `/top-decks`

Un GET par contrôle (`?limit=1&ocg[$ne]=true`, même adresse que `fetch_tournament_decks.py`, alignement testé). Réussite
= HTTP 200 et une liste de decks non vide. Un échec réseau, un code HTTP d'erreur ou une réponse qui n'est plus une liste
sont rapportés tels quels dans la sortie et le journal, et font échouer le contrôle. Jamais d'appel dans les tests ni
dans `deploy_prebuilt.py`. Au 18/11 : HTTP 200, 1 deck, 0,9 s.

## Plan B si `/top-decks` disparaît

Risque suivi par TOK-76 (API non officielle, sans contrat).
- **Ce qui reste** : `tournament_decks` (23 948 decks, du 2023-05-05 au 2026-11-14) et `deck_cards` (1 026 945 lignes)
  restent en base. Les fetchs ne suppriment jamais un deck (`INSERT OR REPLACE` ; seules les cartes d'un deck renvoyé
  sont purgées avant réinsertion) et `refresh_decks.py` signale toute baisse du nombre de decks. Toutes les tables
  dérivées se recalculent encore depuis ces decks : le site reste juste, figé à la date du dernier deck, et chaque
  graphique le dit déjà par son `DataFooter`.
- **Ce que voit le contrôle** : la première semaine, l'endpoint en erreur (code 1) ; ensuite, les tables datées par le
  dernier deck (`ban_radar`, `card_impact`, `early_card_signals`, `archetype_recent_decks`) restent alignées sur le
  dernier deck (0 j de retard) ; c'est la fraîcheur des decks de `refresh_decks.py` (> 7 j) qui alerte.
- **À faire alors** :
  1. ne rien purger ; sauvegarder la base (`scripts/export_db_snapshot.py`) ;
  2. vérifier sur le site public que la page des top decks a disparu aussi, et pas seulement l'API (changement de
     paramètres ou d'adresse : corriger `BASE_URL`) ;
  3. évaluer une source de remplacement qui donne, par deck, la liste complète par zone, la date du tournoi, le
     classement et l'archétype (candidates à vérifier : pages de tournois de YGOPRODeck, couverture officielle Konami ;
     non testées ici) ;
  4. l'ingérer dans les mêmes tables par un nouveau script, avec une colonne `source` ajoutée (changement de schéma
     additif, avis de `gardien-donnees`), et vérifier la continuité (archétypes nommés pareil, part des decks par mois
     sans saut) avant de mélanger les deux sources ;
  5. en attendant, écrire sur le site la date du dernier deck relevé (déjà dans les pieds de graphique).

## Seuils (réglages posés à la main, déclarés)

| Réglage | Valeur | Raison |
|---|---|---|
| `COMPUTED_MAX_DAYS` | 8 jours | job hebdomadaire du lundi, un jour de marge (Mac endormi, rattrapage launchd) |
| `DATA_LAG_MAX_DAYS` | 7 jours de retard sur le dernier deck | une table calculée après le relevé a 0 jour ; 7 = une semaine de relevé manquée |
| `MONTH_LAG_MAX` | 1 mois | le mois en cours peut ne pas avoir encore de ligne (`meta_predictions` porte sur le dernier mois complet) |
| `VIEWS_MAX_DAYS` | 8 jours | « vues de la semaine » : sans sens au-delà d'une semaine |
| `KNOWN_STALE` | 3 motifs jusqu'au 2026-12-31 | défauts connus : sans tolérance, le job échouerait chaque lundi et une 4e table périmée passerait inaperçue |

Aucun n'est estimé sur les données : ce sont des conventions de surveillance, pas des scores.

## Pièges

- **Un code 1 dans `refresh_all.py` fait sauter la reconstruction de `serving.db`** (`derived` n'est pas dans
  `NON_BLOCKING` de `refresh_decks.py`). Tout contrôle qui peut échouer va après `serving`.
- **La cohérence entre deux tables ne prouve pas leur fraîcheur** : le graphe passerait si `card_cooccurrence` était
  elle-même périmée ; elle prouve seulement qu'elles viennent du même calcul.
- **`views_week` n'a pas de date en base** : la règle compare les vues à l'instantané suivi par Git (date du commit, `git`
  requis dans le PATH de launchd, sinon « ignorée »). Une fois les vues rafraîchies, la règle dira « non datée » tant
  qu'aucune date de relevé n'est enregistrée.
- **Une table fille hérite du statut de sa mère** (`archetype_recent_deck_cards`, `ban_backtest_cards`) ; `ban_backtest_cards`
  ne doit pas être comparée aux banlists : une liste écartée par le backtest n'y a jamais de cartes.

## Suites

- TOK-136 : recalculer `card_graph_metrics` et `graph_communities` (notebook 03) et l'ajouter à la chaîne.
- Ticket à créer : rafraîchir `cards.views_week` sans `init_db.py` (qui réécrit toute la table), avec la date du relevé
  (aussi utile à TOK-129 : archiver les vues chaque lundi).
- Retirer `meta_tier_list` et `archetype_trend` de `SERVED_TABLES` (lues par aucun routeur) : à décider.
- Dater `card_cooccurrence` et `archetype_trend` (colonne `computed_at` dans les notebooks 02 et 04).
- `refresh_all.py` s'arrête au premier échec : une panne réseau de `card_images` ou `banlist_announcements` (en fin de
  chaîne) le fait sortir en erreur et fait sauter `serving` dans `refresh_decks.py` (défaut antérieur à ce ticket).
