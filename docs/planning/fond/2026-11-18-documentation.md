# Documentation désynchronisée — 2026-11-18 (TOK-134, jalon n°3)

Documentation seulement, aucun code modifié. Comparaison avec le code de `c8727a4` (jalon n°2 fini) et la base de
référence lue en lecture seule (effectifs du 2026-11-18). Réponses de l'API relevées avec `TestClient` sur `serving.db`.
Le sous-agent `gardien-donnees` n'a pas pu être lancé (refus de l'outil d'autorisation) : comparaison faite directement.

## Écarts corrigés

### `docs/api-contracts.md`
- 8 endpoints documentés (état d'août) contre 16 dans les routeurs : ajout de `/archetypes/{slug}`, `/decks`,
  `/decks/{slug}`, `/boutique/prices`, `/ban-radar/history`, `/card-impact` ; tableau méthode / chemin / paramètres /
  tables lues / ticket.
- `/meta/tier-list` décrite comme lisant `meta_tier_list` : elle est calculée à la volée sur `meta_scores`
  (`tiering.py`) ; champs `slug`, `decks`, `window_*`, `n_decks`, `tier_thresholds`, `tier_min_decks` ajoutés.
- `/meta/evolution` : paramètres `archetypes`, `from_month`, `to_month` inexistants retirés ; `decks`, `images`,
  `decks_by_month` ajoutés.
- `/meta/predictions` : `model` « Ridge + Naïf blend (ρ≈+0.65) » → « 70 % naïf + 30 % Ridge » ; champs `data_month`,
  `computed_at`, `direction_threshold`, `interval_*` ajoutés.
- `/boutique/signals` : paramètres `min_score`, `label` inexistants retirés ; `buy_label` et `tcg_entry_estimated`
  (plus servis) remplacés par `signal_label`, `archetype_rank`, `label_rule`, `tcg_window_*`, `archetype_slug`.
- `/early-signals` : `as_of`, `computed_at`, `cards_scored`, `text_signal_cards` ajoutés.
- `/graph/synergies` : paramètre `archetype` inexistant retiré ; défauts `limit` 150 (≤ 500) et `min_jaccard` 0,15
  (au lieu de 200 et 0,1) ; forme des nœuds et arêtes (`group`, `size`, `source`, `target`, `weight`).
- `/cards/search` : `q` à partir de 1 caractère (et non 2).
- `/cards/{name}` : la réponse est la ligne brute de `cards`, sans `price_history`.
- `/simulate-ban` : `image_url` ajouté ; approximation et absence de validation dites (TOK-132).
- `/ban-radar` : `deck_share` en pourcentage signalé ; exemple daté du 2026-11-14 (1 883 decks).
- URL de production « non décidée » → Vercel Services préparé, rien de déployé (TOK-35) ; images servies par le front
  (TOK-92) ; slugs calculés par l'API.
- APIs consommées : `cardinfo.php` aussi utilisé par `fetch_new_cards.py` ; images YGOPRODeck par
  `download_card_images.py` ; `tier-list` de yugiohmeta plus appelé par le code ; santé de `top-decks` contrôlée par
  `check_freshness.py`.
- Loaders Streamlit : `load_tier_list` ne correspond plus à `/meta/tier-list`.

### `docs/data-models.md`
- En-tête : « 12 tables lues par l'API », ~9 Mo → 20 tables de `SERVED_TABLES`, ~12 Mo ; 49 tables dans `yugioh.db`.
- Effectifs mis à jour pour 19 tables (ex. `tournament_decks` 21 198 → 23 948, `deck_cards` 906 159 → 1 026 945,
  `card_impact` 35 → 966, `boutique_buy_signals` 137 → 12) et pour les 6 tables de co-occurrence.
- `banlist_features` : colonnes `months_on_banlist`, `bl_n_limited` inexistantes → `ban_severity_t1`, `was_hit_recent`.
- `meta_scores` : `placement_score_norm` n'est pas une colonne (calcul intermédiaire) ; TCG seul depuis TOK-80.
- `meta_predictions` : `computed_at` ajouté ; direction « Falling » → « Declining ».
- `card_impact` : schéma de l'ancien notebook 06 → schéma de `build_card_impact.py` (8 colonnes, univers du Ban Radar).
- `text_synergies` : `shared_keywords`, `arch_a`, `arch_b` ajoutés ; hors chaîne.
- `combo_edges` : `archetype` et `computed_at` existent dans les deux tables.
- `early_card_signals` : 6 colonnes ajoutées (`early_score_100`, `as_of`…) ; produite par `build_early_signals.py`.
- `boutique_alerts` : `alert_score_raw`, `tcg_compat_ratio`, `tcg_entry_estimated` disparus ; 5 colonnes v3 ajoutées.
- `boutique_card_alerts` : `ban_tcg` disparu, `unreleased` ajouté.
- `boutique_buy_signals` : `tcg_entry_estimated` → `tcg_window_start` / `tcg_window_end` ; `ban_tcg` vient de
  `banlist_history`.
- 19 tables non documentées : 12 décrites dans un groupe 9 (`deck_legality`, `banlist_announcements`,
  `meta_scores_ocg`, `ocg_archetype_scores`, `boutique_price_history`, `archetype_card_profile`,
  `archetype_recent_decks` / `_deck_cards`, `ban_backtest_lists` / `_cards`, `prediction_log`,
  `prediction_validation`) ; les 6 tables de co-occurrence étaient dans le tableau du groupe 4 ; `combo_edges_global`
  était décrite avec `combo_edges`.

### `docs/architecture.md`
- Stack front : Next.js 15 + recharts → Next.js 16 + React 19, SVG avec D3, design system, images hébergées,
  `apiBaseUrl()` ; déploiement « à trancher » → Vercel Services préparé.
- Pages : 8 routes d'août (`/ban-radar`, `/ban-simulator` n'existent plus) → 11 routes réelles dont `/ban?tab=…`,
  `/archetype/{slug}`, `/decks`, `/methode`.
- Scripts d'ingestion : 10 → 24 lignes, avec la chaîne `refresh_decks.py` / `refresh_all.py` ; `card_impact` produite par
  `build_card_impact.py` (et non `setup_impact_tables.py`) ; scripts de diagnostic listés.
- Base de service : « 12 des 36 tables », ~9 Mo → 18 tables lues sur 49, 20 copiées, ~12 Mo ; règle de fraîcheur.
- Groupes de tables : `deck_legality`, `banlist_announcements`, `meta_scores_ocg`, `ban_backtest_*`, profils de decks,
  journal des prédictions, `boutique_price_history`, `ocg_archetype_scores` ajoutés.
- Décisions de schéma : `tcg_compat_ratio` (disparu) → statut de banlist lu dans `banlist_history`, filtre `legal = 1`.
- Notebooks : 02 n'écrit pas `deck_style_clusters` ; 04 lit `deck_legality` (pas `meta_tier_list`) et écrit
  `meta_scores_ocg` ; 05 = 70 / 30 (AR(1) écarté) ; 09_banlist et 11 remplacés par des scripts ; 10 écrit
  `ocg_archetype_scores` et non `boutique_buy_signals`, lit `tournament_decks` / `deck_cards` / `deck_legality` /
  `banlist_history` / `cards`.
- Algorithmes : ρ ≈ +0,65 et `tcg_compat_ratio` retirés ; périmètre du signal précoce aligné sur le lot 20.
- Section finale : endpoints `/api/predictions`… (préfixe faux, 7 sur 16) → renvoi à `api-contracts.md`.

### `README.md`
- Vision : « signal OCG→TCG validé (r = 0,771, lag = 4 mois) » → r ≈ 0,53 à 4 mois, IC 95 % [0,43 ; 0,59], plateau de
  2 à 6 mois, 0,771 non reproductible (TOK-73).
- Feuille de route : 19 888 decks → 23 948 ; modèle « Ridge + AR(1) + Naïf » → 70 / 30 ; phase 5 « 🔜 » → livrée sauf
  déploiement ; « Kewl Tune 100/100 » → libellé par rang.
- Stack : 36 tables → 49 ; serving 12 tables / 9 Mo → 20 / ~12 Mo ; cron quotidien des prix → job du lundi ; front.
- Structure : scripts de la chaîne, `moteur_combos/`, 8 → 12 pages.
- Reconstruction : `setup_impact_tables.py` et « notebooks 01 → 12 » → `refresh_decks.py` + étapes hors chaîne.
- Données clés : 13 797 → 14 084 cartes ; ρ ≈ +0,65 → écart de ρ +0,009 et MAE −4 % (TOK-73) ; graphe périmé (TOK-136) ;
  r = 0,771 → 0,53.

### `docs/ONBOARDING.md`
- Thèse « environ 4 mois » → plateau de 2 à 6 mois, r ≈ 0,53.
- Volumes : 13 797 → 14 084 cartes ; « depuis 2024, ~21 200 decks, ~850 000 lignes » → depuis mai 2023, 23 948 decks,
  1 026 945 lignes ; banlists ~24 000 → 24 696 lignes + 170 listes datées.
- Base : « une quarantaine de tables » → 49 ; serving 9-10 Mo / 12 tables → ~12 Mo / 20 tables.
- Légalité : 20 220 légaux sur ~21 200 → 22 422 / 611 / 915 sur 23 948 ; 388 non évaluables → 915.
- Reconstruction : liste manuelle avec `setup_impact_tables.py` et notebook 11 → `refresh_decks.py` + étapes hors chaîne.
- Vérifications de `check.py` : 5 lignes → 10 (Wilson, garde-fou, textes bloquants, moteur de combos, captures) ;
  contrôle de fraîcheur du job du lundi mentionné.

## Écarts relevés dans le code, non corrigés (hors périmètre : code)
- `scripts/check.py`, docstring : « Mots interdits … non bloquante » alors que l'étape lance `check_copy.py --strict`
  (bloquante depuis le lot 16) ; le garde-fou et le test de Wilson n'y figurent pas.
- `scripts/check.py:417` : « 45 captures » ; 51 références dans `frontend/tests/visual/reference/`.
- `scripts/build_serving_db.py`, docstring : « l'API n'en lit que 12 tables », ~9 Mo (20 tables, ~12 Mo).
- `scripts/build_serving_db.py --check` ouvre `data/yugioh.db` sans `mode=ro` (aucune écriture, mais `sqlite3.connect`
  en écriture sur la base de référence via un lien symbolique).
