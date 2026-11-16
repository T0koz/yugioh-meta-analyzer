### ⚖️ Légalité des decks à la date du tournoi (2026-11-01)

**Problème :** `tournament_decks.illegal` (drapeau de l'API yugiohmeta) est évalué contre une banlist
**postérieure** au tournoi. Avant le 2 février 2026 (TCG) et avril 2026 (OCG), 90 à 100 % des decks
sont jugés illégaux ; le filtre `illegal = 0` des notebooks 02, 03, 04, 09, 10, 12 et de
`build_ban_radar.py` jette donc l'essentiel de l'historique (4 757 decks « légaux » sur 21 206), et en
priorité les decks qui jouaient des cartes touchées ensuite (biais de survivant). C'est ce qui rend
`meta_scores` si maigre (moins de 40 decks par mois avant 2026).

**Correctif (étape 1, faite) :** `scripts/compute_deck_legality.py` reconstruit la table `deck_legality`
(banlist en vigueur à la date `created` du tournoi, infractions comptées main + extra + side). Résultat :
20 220 decks légaux (TCG 9 282, OCG 10 938), 598 illégaux, 388 non évaluables (format Genesys, légalité
par points). Accord avec l'API de 99,6 % depuis juin 2026, période où la liste est stable.

- `illegal` n'est **pas** modifié : tant qu'on ne rebranche pas les notebooks, rien ne change.
- `days_to_boundary` : distance au changement de liste le plus proche. Autour d'un changement
  (≈ 14 jours) la date réelle d'entrée en vigueur est ambiguë (accord 84-92 % en fév.-mai 2026).
- **À vérifier :** `Stake Your Soul!` et `Vanquish Soul Razen` (Semi-Limited dans la liste de
  février 2026) concentrent les désaccords avec l'API : banlist scrapée ou API en cause ?
- **À vérifier :** l'API juge « légaux » des decks Genesys (≈ 11 % du TCG depuis février) : le
  méta TCG actuel en est probablement pollué.
- **Étape 2 (non faite) :** rebrancher les consommateurs sur `deck_legality` (`legal = 1`, et
  `days_to_boundary > 14` si on veut éviter les fenêtres ambiguës), recalculer `meta_scores`, les
  prédictions, les signaux boutique, puis relancer `build_ban_radar.py --backtest` (obligatoire,
  c'est un changement de données du scoring). Les chiffres de vitrine (r = 0,771…) changeront.
