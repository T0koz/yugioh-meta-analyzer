# 0043 — Champs de date ajoutés à quatre réponses d'API pour les pieds « source + date »

- Date : 2026-11-16
- Statut : à valider par Thomas
- Décidé par : Lot 3, par défaut ; en attente de revue de Thomas
- Tickets : TOK-99

## Contexte
Le pied « source + date » exige des dates que l'API ne servait pas (prédictions, boutique, signaux précoces, decks par mois).

## Options
- Ne pas afficher de date
- Ajouter les champs

## Décision
Champs `decks_by_month`, `data_month`, `computed_at` ajoutés, lus dans des colonnes existantes ; rien de retiré, aucune écriture en base.

## Raison
Sans date servie, le critère est inatteignable ; un ajout de champ est réversible ; le test de fumée passe sur les deux bases.

## Conséquences
Le graphe de co-occurrences et le simulateur n'ont pas de date servie : leur pied écrit « date de calcul non enregistrée dans la base servie ».

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lot 3)
