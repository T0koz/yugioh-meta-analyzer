# Parts OCG mensuelles servies par l'API (TOK-116, Jalon 2, 2026-11-18)

Remplace les données figées du graphique « preuve » de l'accueil (`frontend/src/lib/proof-data.ts`, décision 0041,
relevé du 16/11/2026) par des données servies. Même graphique, mêmes textes.

## Ce qui change

| Couche | Changement |
|---|---|
| Base de service | `meta_scores_ocg` (notebook 04, 1 530 lignes, 2023-08 → 2026-11) ajoutée à `SERVED_TABLES` ; `serving.db` 11,8 → 11,9 Mo |
| API | `GET /archetypes/{slug}` sert `ocg_history` (même forme que `history` : mois, decks, total_decks, part ; 0 deck = mois sans l'archétype) et `ocg_history_computed_at` |
| Fraîcheur | règle `meta_scores_ocg` dans `check_freshness.py` (dernier mois contre dernier deck OCG, retard toléré 1 mois) |
| Front | `proof-data.ts` ne garde que l'exemple (archétype, slug servi, fenêtre août 2025 → novembre 2026) et `buildProof()` ; l'accueil appelle `api.archetype("kewl-tune")` ; `ProofChart` reçoit les données en propriété |
| Tests | `test_home_example_has_both_series` (les deux séries couvrent la fenêtre, date servie, effectifs cohérents) ; `kewl-tune` dans `EXPLICIT_GETS` et dans `ARCHETYPES` des tests visuels ; fixture `archetypes__kewl-tune.json` |

Aucun endpoint nouveau : la page d'archétype avait déjà l'historique TCG, l'OCG s'y ajoute (champ réutilisable par la
page d'archétype plus tard, non affiché aujourd'hui).

## Mesures

- **Valeurs dessinées identiques au relevé figé** : 16 mois × 2 formats, 0 écart à 0,1 point près (Kewl Tune, OCG
  0,8 → 2,1 %, TCG 0 → 0 %, pics 26,7 % en avril 2026 et 32,1 % en juillet 2026). Date affichée inchangée
  (« relevé du 16 novembre 2026 » : `ocg_archetype_scores.computed_at` = 2026-11-16).
- **Captures** : 51 sur 51 identiques aux références après réenregistrement des fixtures (accueil compris, 3 largeurs).
- Tests de l'API : 74 sur chaque base (base du worktree). Sur la `serving.db` actuelle de la référence, 1 échec attendu
  (`test_home_example_has_both_series`) tant qu'elle n'est pas reconstruite.

## Décisions prises par défaut

- **Date de calcul** : `meta_scores_ocg` n'a pas de colonne de date et la modifier n'est pas additif. L'API sert
  `MAX(computed_at)` d'`ocg_archetype_scores` (notebook 10, juste après le notebook 04 dans `refresh_all.py`). C'est une
  approximation : si le notebook 04 tourne seul, la date est celle du dernier notebook 10.
- **Fenêtre fixe** (août 2025 → novembre 2026) : les textes de l'accueil nomment ses mois. Une fenêtre glissante
  demanderait de réécrire ces textes (formulaire).
- **Sans données complètes, la section n'est pas rendue** (base de service antérieure, archétype absent, pic avant le
  quatrième mois) plutôt que dessinée à moitié ou retombée sur des chiffres figés.
- Noms de table en clair dans `archetypes.py` (« FROM meta_scores_ocg ») : `build_serving_db.py --check` et
  `check_freshness.py` repèrent les tables lues par l'API par expression régulière.

## Limites et suites

- La légende dit encore « Incertitude non dessinée : les effectifs mensuels n'ont pas été relevés avec cette série
  figée ». Les effectifs sont maintenant servis (`decks`, `total_decks`) : la phrase devient inexacte, mais le brief
  interdit de changer un texte. Formulaire Jalon 2, TOK-116.
- Les textes « pic en OCG en avril 2026 », « janvier 2026 », « juillet » sont écrits en dur : si un recalcul déplaçait
  un pic dans la fenêtre, le graphique et le texte divergeraient. Le test de fumée ne le voit pas (il ne lit pas le texte).

## À appliquer sur la base de référence (orchestrateur)

```bash
python scripts/build_serving_db.py          # ajoute meta_scores_ocg à data/serving.db
python scripts/check.py                     # le test de fumée sur serving.db doit repasser à 74
```

Aucune écriture dans `yugioh.db`. À relire par la collaboratrice : rien de statistique (données existantes servies telles quelles).
