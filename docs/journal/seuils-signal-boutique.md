# Libellé absolu des signaux boutique (suite de TOK-113, 2026-11-17)

## Problème
`buy_label` (Fort ≥ 80 / Modéré ≥ 50 / Faible) était doublement relatif : `alert_score` est divisé par le maximum des
3 archétypes retenus (notebook 10), puis `buy_score_100` par le maximum des 12 cartes. Il y avait toujours un « Fort ».

## Ce que disent les données (analyse `data-scientist-ygo`, lecture seule)
- **Aucun seuil sur le score n'est validable.** Le journal de prédictions n'a qu'une série v3 live (2026-11-16, 3 archétypes,
  12 cartes), fenêtres de sortie de 2027-03 à 2027-05 : rien n'est évaluable. Les lignes v1/v2 ont une cible fixe sans valeur
  et le lot v1 de juin (seul évalué) est contaminé par des archétypes déjà en TCG (ρ = +0,52, même piège que le modèle naïf du
  notebook 05) : ne pas le citer. **Aucune série ne relie un niveau de score à une arrivée en TCG ou à un mouvement de prix.**
- **Un seuil en points dérive.** Le maximum brut de `meta_score_ocg × log1p(vues)` est passé de 1,84 (juin, Kewl Tune) à 2,58
  (novembre, Elfnote) ; le P90 du brut a bougé de +25 %. Le classement, lui, est assez stable (Spearman 0,74 sur 49 archétypes
  communs juin/novembre), et la médiane est stable (0,27 → 0,27).
- **Grandeur absolue retenue** : `ocg_archetype_scores.ocg_score`, même formule que `alert_score` mais normalisée sur les
  **89 archétypes OCG** (pas sur un lot de 3), et surtout son **rang** dans cette population.

## Règle retenue
Libellé porté par l'**archétype** (force du signal) ; le prix reste une colonne à part.

| Libellé | Règle | Rangs (89 archétypes) |
|---|---|---|
| Fort | rang / population ≤ 10 % | 1 à 8 |
| Modéré | ≤ 25 % | 9 à 22 |
| Faible | le reste | 23 à 89 |

Calculé **à la volée** dans l'API (`backend/app/signal_label.py`), sans recalcul en base ni changement de scoring ni de `WEIGHTS`.
Mesuré : les rangs (Raise Moon 3/89, Trirealm Rift 12/89, Harpie/Amazoness 18/89), les quantiles de `ocg_score`
(P50 10,6 ; P75 18,3 ; P90 34,9 ; max 100), l'absence de coupure naturelle sur les 20 premiers. **Arbitraire** : les coupes
10 % et 25 % (quantiles ronds, pas des optimums) et la population de référence.

Sensibilité à la population : restreinte aux archétypes ≥ 5 decks (n = 36, 53 sur 89 en ont moins, médiane 3), seul
Raise Moon resterait Fort et les deux autres passeraient Faible. Aucune donnée ne tranche ce dénominateur. Autre limite :
`ocg_score` est relatif à Elfnote (déjà en TCG, 2× le suivant) ; sans lui, Raise Moon passerait de 51,5 à 92,5. Le rang n'en souffre pas.

**Résultat au 2026-11-16** : Fort 3 (Raise Moon : Pot of Desires, Foolish Burial Goods, Sacred Sword of Seven Stars),
Modéré 9 (Trirealm Rift, Harpie/Amazoness), Faible 0. Avant : 3 / 5 / 4. Fydraulis Harmonia (41,70 €) passe de Faible à
Modéré : le prix n'entre plus dans le libellé.

Mention affichée : « seuils provisoires, non validés hors échantillon ». Première vérification possible : mars 2027 (échéance des
premières fenêtres v3), sur 3 archétypes, donc de l'anecdote. Un vrai seuil demande plus de séries datées.

Repli sans libellé (score + fenêtre) : appliqué automatiquement si `ocg_archetype_scores` manque dans la base servie ou ne
contient pas l'archétype (`signal_label = null`).

## Contrat de l'API — `GET /api/v1/boutique/signals` (pour la tuile boutique de l'accueil, TOK-106)
Champs ajoutés par signal (`data[]`) :
- **`signal_label`** : `"Fort" | "Modéré" | "Faible" | null` (null = indisponible, afficher le score sans libellé).
- **`archetype_rank`** : entier ≥ 1 (1 = archétype OCG le plus fort) ou null.
Champ ajouté à la racine :
- **`label_rule`** : `{ population, strong_max_rank, moderate_max_rank, provisional, note }` ou null. `note` contient le texte
  « Seuils provisoires, non validés hors échantillon … » à afficher près du libellé. `provisional` vaut toujours `true` pour l'instant.
Champ **supprimé** : `buy_label` (relatif). `buy_score` reste (0-100, le premier vaut toujours 100) : **c'est l'ordre
d'affichage, pas une force**. L'accueil ne doit pas le présenter comme un score absolu.
Types front : `BoutiqueSignal.signal_label`, `archetype_rank`, `SignalLabelRule` dans `frontend/src/types/index.ts`.

## Pièges
- `ocg_archetype_scores` est **ajoutée à `SERVED_TABLES`** : tant que `serving.db` n'est pas reconstruite
  (`python scripts/build_serving_db.py`, fait par le job du lundi), l'API sert les signaux **sans libellé** (repli ci-dessus).
  La base de service existante du dépôt principal n'a pas été touchée par cette branche.
- La colonne `buy_label` existe toujours dans `boutique_buy_signals` (calculée par `build_buy_signals.py`, scoring inchangé) mais
  **n'est plus lue par l'API** ; elle reste relative. `app.py` (Streamlit, historique) l'affiche encore : ne pas la citer comme force.
- Le rang est calculé parmi **tous** les archétypes OCG, y compris ceux déjà en TCG ; un archétype « retenu » n'est donc pas
  forcément dans le top 10 %.
- Tests : `backend/tests/test_signal_label.py` (règle pure, endpoint sur base mémoire, repli sans table).
- Captures : `docs/journal/captures-seuils/boutique-avant.png` / `boutique-apres.png`.
