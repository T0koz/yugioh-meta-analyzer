# 0030 — Un seul auteur pour le journal des prédictions et une seule base de référence

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (règle écrite dans `CLAUDE.md`), proposition de l'avis stack TOK-111
- Tickets : TOK-107, TOK-111

## Contexte
`data/prediction_log.jsonl` est la preuve datée des prédictions : deux journaux locaux qui ajoutent des lignes produiraient conflits et doublons.

## Options
- Plusieurs personnes commitent le journal
- Un seul auteur : le job du lundi, sur la base de référence

## Décision
Seul Thomas commite `prediction_log.jsonl` ; la collaboratrice ne lance pas `log_predictions.py` sur sa copie.

## Raison
Le commit (et le push) date la prédiction par un tiers ; la valeur du journal est sa preuve.

## Conséquences
Règle présente dans `CLAUDE.md` et `docs/ONBOARDING.md` § 8.

## Sources
- `docs/collaboration/avis-stack.md` (problème 6)
- `CLAUDE.md`
