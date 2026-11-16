# Compte rendu — file front du 2026-11-16 (soir)

Branche d'intégration : `claude/front-nuit-17-11` (depuis `main` local `cb2e9fb`). Rien fusionné dans `main`, rien poussé.
Décisions prises par défaut : [`decisions-prises.md`](decisions-prises.md).

| Lot | Ticket | Modèle réel | Résultat | Critères | `check.py` après fusion | Reste |
|---|---|---|---|---|---|---|
| 01 | Seuil boutique (suite TOK-113) | Sonnet 5.5 (demandé : `claude-sonnet-5-5`) | ✅ Fusionné (`69de94c`) | Plus de libellé relatif : `signal_label` (Fort / Modéré / Faible / null) = rang de l'archétype parmi les 89 archétypes OCG (Fort ≤ rang 8, Modéré ≤ rang 22), `archetype_rank`, `label_rule` ; au 16/11 : 3 Fort, 9 Modéré, 0 Faible sur 12 signaux. Méthode : `docs/journal/seuils-signal-boutique.md`. Seuils = quantiles ronds, **non validables** aujourd'hui (première échéance mars 2027). Tuile d'accueil : à lire au lot 02. | ✓ vert, aucune étape ignorée (29 tests sur `yugioh.db` et `serving.db`) | `serving.db` reconstruite par l'orchestrateur (sauvegarde `data/backup_serving_avant_lot01_20261116.db`) ; `buy_label` retiré de l'API (colonne gardée en base) |
