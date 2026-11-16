### 📒 Journal des prédictions (2026-11-01)

`scripts/log_predictions.py` archive l'état courant de `meta_predictions`, `boutique_alerts`,
`boutique_buy_signals`, `early_card_signals` et `ban_radar` dans la table `prediction_log`
(append-only : triggers SQLite contre UPDATE/DELETE) **et** dans `data/prediction_log.jsonl`
(versionné par git). Ces cinq tables sont écrasées à chaque recalcul : sans journal, on ne peut
pas prouver « annoncé le X, réalisé le Y ».

- **À lancer après chaque recalcul d'une source** (notebook 05, notebook 10, notebook 11,
  `build_ban_radar.py`), puis **committer `data/prediction_log.jsonl`** : le commit (et le push) date
  la prédiction par un tiers. `--dry-run` simule, `--status` résume.
- Idempotent (clé : kind, sujet, date de calcul, version du modèle). Si la table est vide, elle
  est reconstruite depuis le fichier jsonl.
- **`provenance`** : `live` si journalisé au plus 1 jour après le calcul, `backfill` sinon. Le premier
  lot (2 008 lignes, calculées entre juin et août 2026) est `backfill` : il ne prouve rien d'indépendant.
  Seules les lignes `live` commitées sont une preuve.
- Bump `META_MODEL` / `BOUTIQUE_MODEL` / `EARLY_MODEL` dans le script quand un modèle change ; la
  version du Ban Radar est l'empreinte de `WEIGHTS` lue dans `build_ban_radar.py`.
- Le script ouvre la base avec `timeout=60` : un processus qui garde `yugioh.db` ouverte (backend,
  notebook, agent) bloque l'écriture (`database is locked`).
- La table n'est pas dans `SERVED_TABLES` (aucun endpoint ne la lit encore) : l'ajouter le jour où
  la page TOK-55 « Ban Predictor vs History » la servira.
- Il n'existe pas encore de script de **validation** (comparer chaque prédiction à la réalité
  après `target_date`) : prochaine étape.
