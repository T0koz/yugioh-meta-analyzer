# TOK-136 — Recalcul de `card_graph_metrics` et `graph_communities` (jalon n°4, 2026-11-18)

Branche `claude/jalon-4-graphe-backtest-vues-e1f982`, session sur Opus 5.5. Suite du constat de TOK-120 (pont daté) et
du contrôle de fraîcheur TOK-93. **Base de référence intacte** (lue en `mode=ro`, md5 identique avant et après) : le
recalcul a été fait sur une copie (`data/copie_tok136.db`, ignorée par Git). **Rien d'affiché ne change** tant que
Thomas n'a pas rempli le formulaire : l'étape de la chaîne est branchée mais verrouillée (`PENDING_FORM`).

## En clair (pour Thomas)

1. Le graphe des cartes (page « Graphe », critère « pont » du Ban Radar, « fragmentation » du simulateur) était calculé
   une seule fois par le notebook 03, jamais refait : 663 cartes, alors que les co-occurrences d'aujourd'hui en donnent
   1 402. Un script le recalcule maintenant à l'identique du notebook (`scripts/build_graph_metrics.py`).
2. **Effet sur le Ban Radar : faible.** Le pont pèse 5 % du score. Sur les 20 banlists rejouées, les rangs médians
   bougent de 0 à 8 rangs ; le top 25 ne change pas (TCG 29 contre 16 aux staples, OCG 41 contre 18). Classement du
   jour : les 10 premiers et 50 premiers identiques (en ensemble), 24 des 25 premiers, 15 libellés de risque changent.
3. **Mais le verdict de l'onglet Historique disparaîtrait** : il compare des sommes figées, dont « rang médian
   meilleur que les staples sur 8 listes OCG sur 10 », qui passerait à 7 (la liste OCG du 2025-01-01 : rang médian
   80 → 86, staples 84). Le verdict qualitatif reste vrai mot pour mot (« en OCG, il fait mieux sur les deux
   mesures » : 7 sur 10), mais les chiffres de `SITE_FACTS.banTop25` sont à réécrire.
4. **Effet visible ailleurs : fort.** La page du graphe montre les 150 cartes les plus connectées : seules 48 restent
   (le reste vient d'archétypes absents de l'ancien graphe). Les communautés passent de 63 à 151 (32 de 2 cartes) ;
   le chiffre « 63 communautés » de l'accueil et de `/methode` est à changer.

## Commandes

```bash
python scripts/build_graph_metrics.py --dry-run --db <base>   # calcule et compare, n'écrit rien
python scripts/build_graph_metrics.py --db <base>             # sauvegarde des 2 tables, puis remplacement (1 transaction)
python scripts/diagnose_backtest_variantes.py --db <copie> --out <dossier> --label avant|apres
python scripts/diagnose_backtest_variantes.py --compare <dossier>/avant <dossier>/apres
```

Durées mesurées : recalcul 2 s ; mesure du backtest 16 s.

## Le script

`scripts/build_graph_metrics.py` reprend le notebook 03 (seuils Jaccard ≥ 0,3 et ≥ 5 decks en commun, mêmes colonnes,
même schéma, aucune colonne ajoutée), lit `card_cooccurrence` (notebook 02, déjà dans la chaîne) et écrit les deux
tables. Écarts déclarés dans sa docstring :

| Écart | Notebook 03 | Script | Pourquoi |
|---|---|---|---|
| Intermédiarité | 500 sources tirées au hasard, sans graine | **exacte** (comme `bridge_date.py`) | reproductible ; 2 s sur 1 402 nœuds |
| Communautés | `greedy_modularity_communities`, arêtes dans l'ordre de la requête | même algorithme, arêtes triées par nom | l'algorithme n'a pas de hasard (pas de graine à fixer) mais départage les égalités selon l'ordre : trier rend le résultat identique d'une exécution à l'autre (testé) |
| Carte de tête, archétypes à égalité | premier rencontré dans un ensemble Python | ordre alphabétique | ordre non garanti |
| Archétype d'une carte | `cards.name` brut | aussi sans `<`/`>` | « Maliss <P> March Hare » (cards) contre « Maliss P March Hare » (decks) : l'étiquette manquait |

Repris tel quel (hors périmètre, ce serait changer le critère) : `weight = jaccard` lu comme une **distance** par
networkx (un lien fort allonge le chemin), déjà signalé par TOK-120.

Écriture : sauvegarde des deux tables seules dans `data/backup_graphe_<base>_<AAAAMMJJ>.db` (≈ 90 ko, une par jour au
plus), puis `DROP` + `CREATE` + `INSERT` des deux tables dans une seule transaction.

**Chaîne** : étape `graph_metrics` de `scripts/refresh_all.py`, après `02_cooccurrence` (dont elle lit les paires) et
avant `ban_radar` (qui lit l'intermédiarité) et `build_serving_db` (page du graphe, simulateur). Elle est dans
`PENDING_FORM` : `refresh_all.py` l'affiche et ne la lance pas (« non lancé : en attente du formulaire TOK-136 »).
Raison : le job du lundi (launchd) tourne depuis le dépôt principal, qui suit la branche d'intégration
`claude/moteur-18-11` ; sans verrou, fusionner cette branche recalculerait la référence le lundi suivant, sans
formulaire. Accepter = retirer `graph_metrics` de `PENDING_FORM` et les deux tolérances de `check_freshness.py` dans
le même commit.

**Contrôle de fraîcheur** : la tolérance des deux tables (`KNOWN_STALE`, jusqu'au 31/12) est **gardée**. La retirer
ferait échouer le contrôle du lundi tant que la référence n'est pas recalculée. Sur la copie recalculée, le contrôle
dit « ok » pour les deux tables (1 402 nœuds contre 1 402).

Tests : `backend/tests/test_build_graph_metrics.py` (base synthétique : seuils, pont, communautés reproductibles, nom
sans chevrons, écriture et sauvegarde, `--dry-run` sans écriture) ; seuils alignés avec `check_freshness.py`
(`test_constants_match_their_sources`).

## Mesures (copie de la base de référence du 18/11, dernier deck du 14/11)

### Le graphe

| | Avant (table servie) | Après (recalcul) |
|---|---|---|
| Nœuds | 663 | 1 402 |
| Arêtes | — | 5 322 (143 composantes) |
| Communautés | 63 (2 à 43 cartes, médiane 10) | 151 (2 à 41 cartes, médiane 9 ; 32 de 2 cartes) |
| Intermédiarité maximale | 0,0058 | 0,0014 (Tri-Brigade Mercourier) |
| Cartes avec intermédiarité > 0 | 302 | 587 |
| Cartes de l'univers du Ban Radar (966) avec pont > 0 | 176 | 237 (28 ≥ 0,1 dans les deux cas) |
| Page du graphe : 150 nœuds les plus connectés communs | — | 48 sur 150 |
| Archétypes porteurs de `card_impact` (46) qui trouvent une communauté (simulateur) | 23 | 29 |

### Backtest (20 listes, veille de l'entrée en vigueur, `backtest_lists` inchangé)

Rang médian des cartes touchées, avant → après ; listes dont un chiffre bouge :

| Liste | Avant | Après | Top 25 avant → après | Staples (inchangé) |
|---|---|---|---|---|
| TCG 2024-09-02 | 76 | 68 | 3 → 3 | 83 / 2 |
| TCG 2025-04-07 | 18 | 20 | 10 → 10 | 39 / 4 |
| TCG 2025-09-15 | 58 | 57 | 3 → 3 | 98 / 1 |
| TCG 2025-10-27 | 350 | 352 | 0 → 0 | 224 / 0 |
| TCG 2026-05-18 (référence) | **84** / 889 | **86** / 889 | 1 → 2 | 58 / 1 |
| TCG 2026-09-21 | 206 | 208 | 2 → 2 | 99 / 0 |
| TCG 2026-10-19 | 308 | 307 | 6 → 5 | 128 / 4 |
| OCG 2024-04-01 | 22 | 21 | 4 → 4 | 43 / 2 |
| OCG 2024-07-01 | 19 | 20 | 4 → 4 | 62 / 2 |
| OCG 2025-01-01 | 80 | **86** | 3 → 3 | **84** / 0 |
| OCG 2025-10-01 | 30 | 29 | 4 → 4 | 52 / 1 |
| OCG 2026-01-01 | 26 | 25 | 7 → 7 | 49 / 5 |
| OCG 2026-07-01 (référence) | **19** / 1 236 | **19** / 1 236 | 6 → 6 | 54 / 3 |

Sommes par format (celles de `SITE_FACTS.banTop25`) :

| | TCG avant | TCG après | OCG avant | OCG après |
|---|---|---|---|---|
| Top 25 radar / staples | 29 / 16 | 29 / 16 | 41 / 18 | 41 / 18 |
| Listes où le radar place plus de cartes au top 25 / moins | 6 / 1 | **7** / 1 | 9 / 1 | 9 / 1 |
| Listes où le rang médian bat les staples | 3 | 3 | 8 | **7** |
| Test du signe, top 25 | p = 0,125 | p = 0,070 | p = 0,021 | p = 0,021 |
| Test du signe, rang médian | p = 0,34 | p = 0,34 | p = 0,11 | p = 0,34 |
| Rang médian moyen, % de l'univers (staples) | 15,9 % (10,6 %) | 15,9 % (10,6 %) | 4,6 % (6,2 %) | 4,7 % (6,2 %) |

Lecture : écarts dans le bruit d'un critère pesant 5 %. Ce qui change à l'écran, c'est le verdict figé : `verdictMatches`
(`frontend/src/lib/ban-verdict.ts`) compare `medianBetter` (8 en OCG) aux listes servies ; après recalcul de la
référence et de `ban_backtest_lists`, il vaut 7 et le verdict est masqué jusqu'à réécriture de `SITE_FACTS.banTop25`
(`medianBetter` OCG 8 → 7, `better` TCG 6 → 7). La phrase du verdict reste exacte avec ces nouveaux chiffres. La seule
conclusion « démontrée » (top 25 OCG, p = 0,021) est inchangée.

### Classement `ban_radar` du jour (TCG, 14/11)

966 cartes notées avant et après ; Spearman 0,998 ; déplacement médian 2 rangs, maximal 255 ; 10 premiers identiques
en ensemble (Mulcharmy Fuwalos passe 1er devant Ash Blossom, dont le pont tombe de 0,32 à 0,05) ; 24 des 25 premiers,
50 des 50 premiers ; libellé de risque changé pour 15 cartes. Le score étant rééchelonné sur le maximum, la plupart des
scores du haut gagnent 1 à 2 points.

## Fuites de données

| Variable | Connue à quelle date | Risque |
|---|---|---|
| `card_graph_metrics.betweenness` dans le backtest | calculée sur toutes les données (avant : une version antérieure des co-occurrences ; après : celles du 16/11) | **Préexistant et inchangé en nature** : le critère pont du backtest lit une table globale (fuite connue, TOK-120). Le recalcul y met un graphe plus récent, donc plus éloigné des listes de 2024. Le pont daté (TOK-120) a montré que dater ce critère ne change rien de mesurable (±0,1 point de rang médian) ; poids estimé négatif. |
| Classement servi `ban_radar` | coupure = dernier deck | aucun : le graphe du jour pour le classement du jour. |

## À relire par la collaboratrice

1. L'algorithme des communautés : `greedy_modularity_communities` sur 1 402 nœuds donne 32 communautés de 2 cartes ;
   faut-il un seuil de taille pour l'affichage ou un autre algorithme (Louvain avec graine) ? Hors périmètre ici.
2. `weight = jaccard` comme distance dans l'intermédiarité et la proximité (repris du notebook).
3. Les sommes du verdict : le basculement 8 → 7 tient à une liste (OCG 2025-01-01, 86 contre 84) : un verdict fondé sur
   des comptes de listes est fragile à quelques rangs près.

## Relectures des sous-agents

**`data-scientist-ygo`** (lecture seule) : chiffres retrouvés en relançant `--compare` (84 → 86, 19 → 19, top 25
inchangés, OCG 2025-01-01 80 → 86, Spearman 0,998) ; calcul déterministe, une exécution suffit. La fuite du critère
pont ne disparaît pas, elle **s'étend** (237 cartes de l'univers avec un pont non nul au lieu de 176), effet borné par
la mesure (≤ 8 rangs, poids effectif ≈ 2 %) : ligne ajoutée au formulaire. **Recommandation : recalculer la référence
maintenant** et réécrire `SITE_FACTS.banTop25` (OCG `medianBetter` 8 → 7) plutôt que garder une table périmée pour
qu'un texte reste vrai ; le pont reste à retirer au prochain changement de poids (poids estimé négatif, fuite non
datable, il mesure la diffusion, TOK-132), pas maintenant (changement de scoring). Non vérifié par lui : les autres
lecteurs (`card_impact` ne lit pas le graphe ; fragmentation du simulateur, mesurée ci-dessus seulement par la
couverture des communautés).

**`gardien-donnees`** (lecture seule) : schéma identique à la référence, aucune table orpheline pour
`build_serving_db.py` (référence et copie), test de fumée de l'API sur la copie vert (29, dont `/graph/synergies` et
`/simulate-ban`). **Défaut bloquant trouvé et corrigé** : l'écriture n'était pas atomique (sqlite3 en mode par défaut
valide `DROP`/`CREATE` hors de la transaction de `with conn` ; une erreur d'insertion laissait `card_graph_metrics`
vide). Corrigé par `isolation_level=None` + `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK`, avec un test qui fait échouer
l'écriture. Autres corrections appliquées : test que l'étape verrouillée a sa tolérance (`PENDING_FORM` ↔
`KNOWN_STALE`), sauvegarde écrite dans un `.tmp` puis renommée, 8 sauvegardes gardées, `assert` remplacé par un
contrôle explicite. Tolérance de fraîcheur : à garder (avis concordant).
