# TOK-138 — Vues de la semaine rafraîchies et archivées par date (jalon n°4, 2026-11-18)

Branche `claude/jalon-4-graphe-backtest-vues-e1f982`, session sur Opus 5.5. Suite des constats de TOK-93 (fraîcheur) et
TOK-129 (backtest des signaux précoces impossible sans vues datées). **Base de référence intacte** (md5 identique) :
le script a été lancé sur une copie (`data/copie_tok136.db`, ignorée par Git), avec un vrai appel à l'API YGOPRODeck
le 18/11. **Rien d'affiché ne change** tant que Thomas n'a pas rempli le formulaire : l'étape de la chaîne est branchée
mais verrouillée (`PENDING_FORM`, comme au TOK-136).

## En clair (pour Thomas)

1. `views_week` (« vues de la semaine » d'une carte sur YGOPRODeck) n'était plus jamais mise à jour pour les cartes
   déjà en base : toutes dataient du 13 juin. Les cartes nouvelles arrivaient, elles, avec les vues du jour. Le signal
   précoce comparait donc des vues de juin à des vues de novembre.
2. Un script relève maintenant les vues chaque semaine, ne change que cette colonne, et **garde chaque relevé avec sa
   date** dans une table nouvelle. Dans quelques mois, on pourra rejouer le signal précoce avec les vues connues à
   chaque date, sans voir le futur (ce qui bloquait TOK-129).
3. Effet mesuré sur une copie : 13 852 vues sur 14 084 changent. **Signal précoce** (page Boutique, « cartes à
   surveiller ») : 14 des 20 premières cartes restent (Spearman des rangs 0,90) ; le top 20 compte 3 cartes
   Unchained de plus et 4 cartes Dark Time Wizard de moins. **Signal boutique par archétype** (notebook 10, qui lit aussi les vues) : presque
   rien (Spearman 0,995, aucun libellé Fort / Modéré / Faible ne change).

## Commandes

```bash
python scripts/fetch_card_views.py --dry-run --db <base>   # appelle l'API, compte, n'écrit rien
python scripts/fetch_card_views.py --db <base>             # sauvegarde, archive le relevé, met à jour views_week
python scripts/fetch_card_views.py --from-json <fichier>   # relevé lu dans un fichier (tests, sans réseau)
```

Durée : ≈ 3 s (un appel, 14 084 cartes).

## Le script

`scripts/fetch_card_views.py` :
- **un appel** à `cardinfo.php?misc=yes&format=tcg` (fonction de `fetch_cards.py`, mêmes paramètres que
  `fetch_new_cards.py`), une seconde tentative après 30 s ; jamais d'appel dans les tests (`--from-json`, et la
  fonction réseau est remplacée par un échec dans `test_fetch_card_views.py`) ;
- **table nouvelle** `card_views_snapshots (snapshot_date, card_id, card_name, views_week, views, fetched_at)`, clé
  `(snapshot_date, card_id)` : une ligne par carte et par jour de relevé (UTC) ; relancer le même jour remplace ce
  jour. Toutes les cartes de l'API y entrent (même celles absentes de `cards`), avec le nom de l'API ce jour-là ;
- **`cards.views_week` seule** est mise à jour, par `id`, et seulement si le nom de l'API (sans `<`/`>`, entités HTML
  décodées) est le nom en base (**garde de nom**). Le 18/11, deux cartes sont restées de côté : `Aroma Strategy`
  (« Aroma Strategy (Skill Card) » dans l'API) et `Void Liberation` (« Void Unleashing »). Une carte sans `viewsweek`
  garde sa valeur (jamais `NULL`) ;
- **carte renumérotée** : quand un `id` de l'API est inconnu et qu'une seule carte de `cards` porte le même nom et
  manque à l'API, elle reçoit les vues (signalé ⚠) ; plusieurs candidates : rien. Cas réel du 18/11 : Odd-Eyes Pendulum
  Dragon (16178681 → 16178683), qui aurait gardé à jamais ses vues de juin (732 contre 273) ;
- le plan (quelles lignes changer) est recalculé **dans** la transaction, sur `cards` lue après `BEGIN IMMEDIATE` ;
- **gardes** : réponse tronquée (< 90 % des cartes en base) ou `viewsweek` absent pour plus de la moitié des cartes
  → rien n'est écrit, code 1 ;
- **sauvegarde** `(id, views_week)` dans `data/backup_vues_<base>_<AAAAMMJJ>.db` (≈ 300 ko, fichier temporaire puis
  renommé) : les 8 plus récentes et **la toute première**, qui garde les vues du 13/06 ;
- **une transaction** (`isolation_level=None`, `BEGIN IMMEDIATE` … `COMMIT`, `ROLLBACK` sur erreur), leçon du TOK-136.

**Chaîne** : étape `card_views` de `scripts/refresh_all.py`, juste après `fetch_new_cards` et avant `early_signals`
(qui lit `cards.views_week`) et le notebook 10. Raisons du choix de `refresh_all.py` plutôt que `refresh_decks.py` :
même API et même mode de panne que `fetch_new_cards`, déjà dans `refresh_all.py` en tête de chaîne (une API
indisponible arrête déjà la chaîne à cet endroit : pas de nouvelle cause d'échec) ; et c'est là que vit le verrou
`PENDING_FORM`. L'étape y est verrouillée (« non lancé : en attente du formulaire TOK-138 »). Elle est aussi **non
bloquante** (`NON_BLOCKING` de `refresh_all.py`, ajouté ici) : un échec est écrit en « ⚠ » (relevé par
`refresh_decks.py` comme avertissement) et la chaîne continue avec les vues précédentes ; une panne de l'API ne doit
pas empêcher la mise à jour du site pour 35 % d'une seule table. `fetch_new_cards` reste bloquante dans
`refresh_all.py` (alors que `refresh_decks.py` la déclare non bloquante) : défaut antérieur, hors périmètre, signalé.

**Contrôle de fraîcheur** (`check_freshness.py`) : les vues sont désormais datées par le dernier relevé de
`card_views_snapshots` (lu dans la base de référence) quand **les vues servies** (`early_card_signals.views_week`, par
nom) en viennent (≥ 50 % de valeurs égales), sinon par l'instantané Git comme avant. Dater la table servie, et non
`cards`, évite un « ok » à tort si `build_early_signals.py` échoue après le relevé. Sur la copie relevée :
« vues (early_card_signals.views_week) égales au relevé du 2026-11-18 pour 262 cartes sur 262 : 0 j ». La tolérance `early_card_signals:vues` (jusqu'au 31/12) est **gardée** et rattachée à TOK-138 : la
référence n'est pas relevée tant que l'étape est verrouillée, la retirer ferait échouer le contrôle du lundi.

Tests : `backend/tests/test_fetch_card_views.py` (mise à jour de la seule colonne, garde de nom, nom à entité HTML,
archive, relance du même jour, `--dry-run`, réponse tronquée ou sans vues, jamais de `NULL`, échec d'écriture
annulé, datation par la fraîcheur) ; `test_pending_form_steps_are_skipped_and_tolerated` couvre la nouvelle étape.

## Mesures (copie de la base de référence du 18/11, relevé de l'API du 18/11)

| | Valeur |
|---|---|
| Cartes de l'API / en base | 14 084 / 14 084 (1 de l'API absente de `cards`, 1 de `cards` absente de l'API) |
| Cartes avec des vues | 14 084 |
| `views_week` changées / déjà égales / gardées par la garde de nom | 13 853 / 229 / 2 (dont 1 carte renumérotée rattrapée par le nom) |

### Signal précoce (`early_card_signals`, 263 cartes, recalculé par `build_early_signals.py` sur la copie)

Le recalcul avec les vues de juin redonne exactement la table servie (hors `computed_at`) : la comparaison isole bien
l'effet des vues.

| | Vues de juin | Vues du 18/11 |
|---|---|---|
| Vues médianes des 263 cartes | 1 407 | 462 |
| Spearman des vues | 0,855 | |
| Spearman des rangs du score | 0,902 | |
| Cartes communes dans le top 10 / 20 / 50 | 6 / 14 / 45 | |
| Archétypes du top 20 | Witchcrafter 7, Dark Time Wizard 5, Unchained 4 | Witchcrafter 7, Unchained 7, Dark Time Wizard 1 |

Les vues des cartes de juin ont baissé (l'engouement de leur sortie est passé), celles des cartes Unchained ont monté.
Le score est rééchelonné sur le maximum : les scores du top 20 gagnent 0 (le premier reste à 100) à 17 points.

### Signal boutique (notebook 10, exécuté sur deux copies : vues de juin, vues du 18/11)

Le notebook 10 multiplie la force OCG d'un archétype par le log des vues moyennes de ses cartes clés.

| | Résultat |
|---|---|
| `ocg_archetype_scores` (89 archétypes) : Spearman des rangs | 0,995 |
| Libellés Fort / Modéré / Faible (rang ≤ 10 % / ≤ 25 %) changés | 0 |
| `boutique_alerts` (3 archétypes) | mêmes archétypes ; scores 56,2 → 51,3 (Trirealm Rift), 44,7 → 46,7 (Harpie/Amazoness) |
| `boutique_card_alerts` (42 cartes) : Spearman | 0,997 ; top 5 par archétype identique |

## Fuites de données

| Variable | Connue à quelle date | Risque |
|---|---|---|
| `cards.views_week` (servie) | date du dernier relevé | aucun pour le classement du jour ; c'était l'écart de dates (juin contre novembre) qui faussait la comparaison entre cartes |
| `card_views_snapshots` | `snapshot_date` | la table rend possible un backtest des vues **à partir du premier relevé** ; avant, il n'existe que l'instantané du 13/06 (`data/raw/cards.json`, daté par son commit) |
| Backtest TOK-129 | — | toujours impossible pour les dates passées ; possible dans quelques mois si l'étape tourne chaque semaine |

## À relire par la collaboratrice

1. « Vues de la semaine » : fenêtre exacte et heure de calcul côté YGOPRODeck inconnues (pas de documentation) ; le
   relevé du lundi matin et le dernier deck du week-end ne coïncident qu'à quelques jours près.
2. Faut-il réinjecter l'instantané du 13/06 (`data/raw/cards.json`) dans l'archive, avec sa date de commit, pour avoir
   un premier point ancien ? Proposé au formulaire, non fait.
3. Le critère « vues » du signal précoce (35 %) n'a pas battu les vues seules par archétype au TOK-129 : rafraîchir les
   vues corrige une incohérence de dates, pas la valeur du critère.

## Relecture `gardien-donnees`

Lecture seule, sans réseau : tests de `backend/tests` verts sur les deux bases (142 + 1 `xfail`), aucune table orpheline
pour `build_serving_db.py`, aucun routeur ne lit `card_views_snapshots` (à garder hors `SERVED_TABLES`), aucun nom en
double dans `cards`. Écriture jugée sûre et additive. Corrections demandées, **toutes appliquées** : (1) étape non
bloquante (`NON_BLOCKING`) ; (2) rattrapage par le nom des cartes renumérotées (cas Odd-Eyes Pendulum Dragon trouvé
par lui) ; (3) lecture de `cards` dans la transaction ; (4) première sauvegarde (vues de juin) toujours gardée ;
(5) fraîcheur datée sur la table servie. Tolérance de fraîcheur : à garder tant que l'étape est verrouillée, à retirer
au même commit que le déverrouillage.

Mesures refaites après corrections : le relevé à blanc sur la copie aux vues de juin donne 13 853 mises à jour (la
carte renumérotée en plus) ; les mesures d'effet ci-dessus (signal précoce, boutique) ont été faites avant le
rattrapage et portent sur 13 852 cartes : une carte de plus (Odd-Eyes Pendulum Dragon, absente des 263 cartes du signal
précoce) ne les change pas.
