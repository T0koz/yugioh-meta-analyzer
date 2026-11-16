# TOK-77 — Pollution Genesys du méta TCG (2026-11-16)

Reproductible : `python scripts/analyze_genesys.py` (lecture seule). Sources : `tournament_decks`
(`tournament_type = 'Genesys Format'`) et `deck_legality`. Tout est VÉRIFIÉ.

## Mesures

- **Genesys = 915 decks, 7,9 % de tout le TCG, 0 en OCG** — mais très inégalement réparti dans le temps :
  4 à 11 % par mois jusqu'en juin 2026, puis **44 % (juillet), 36 % (août), 28 % (septembre), 39 % (octobre),
  27 % (novembre)**. L'hypothèse de départ (« ~11 % depuis février ») sous-estimait fortement la période récente.
- **L'ancien filtre `illegal = 0` de l'API laissait entrer presque uniquement du Genesys** : parmi les decks TCG
  jugés « légaux » par l'API, 100 % sont Genesys en mai, juillet et août 2026 (24, 67 et 87 decks), 96 % en septembre.
  Le « méta TCG » des anciens `meta_scores` de l'été était donc le méta Genesys.
- **Effet sur le classement** : en juillet 2026, la corrélation de rang (Spearman) des archétypes avec/sans Genesys
  tombe à **0,14** (2 archétypes communs sur le top 5) ; Blitzclique gagne **+14,9 points** de part ;
  de août à octobre : 0,61-0,73, et Blitzclique reste gonflé de 3,5 à 4,5 points.
  Avant juin 2026, le classement est stable (ρ de 0,60 à 0,91, top 5 inchangé sauf un cas).

## Ce qui est déjà corrigé et ce qui ne l'est pas

- Le pipeline actuel (`deck_legality.legal = 1`) **exclut déjà Genesys** (légalité NULL, non évaluable) : les
  `meta_scores` recalculés le 2026-11-16 ne sont pas pollués. Conséquence : le méta TCG « Advanced » repose sur
  peu de decks en été (131 decks légaux en juillet, 272 en août, 519 en septembre).
- Non corrigé (hors périmètre, décision produit) : le site n'affiche aucun méta **Genesys**, qui pèse pourtant
  un tiers des decks TCG récents ; et `meta_scores` mêle TCG et OCG (voir `docs/evaluation-prediction.md`).
- À l'inverse, `prediction_log` : le lot `backfill` du 2026-06-19 a été calculé avec le filtre pollué.
