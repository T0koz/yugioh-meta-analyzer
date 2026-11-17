# 0039 — Libellé de signal boutique par rang de percentile de l'archétype

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lot 1, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-113

## Contexte
Les données ne justifient aucun seuil en points pour Fort / Modéré / Faible.

## Options
- Seuil absolu en points
- Rang de percentile parmi les archétypes OCG
- Repli sans libellé

## Décision
Rang de percentile (Fort ≤ 10 %, Modéré ≤ 25 %), calculé à la volée, avec la mention « provisoire, non validé » ; repli sans libellé si la table de référence manque.

## Raison
Recommandation du data scientist : un rang est stable dans le temps, un seuil en points dérive ; réversible (aucun recalcul, aucune écriture).

## Conséquences
Servi par `GET /boutique/signals` (`signal_label`, `archetype_rank`, `label_rule`). Seuils non validés hors échantillon (une seule série datée, rien d'échu avant mars 2027).

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 1)
- `docs/journal/seuils-signal-boutique.md`
