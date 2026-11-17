# Règles communes des lots de méthode (sprint 4)

- Sous-agent `data-scientist-ygo` obligatoire. Source des attendus : `docs/journal/audit-rigueur-statistique.md`
  (tableau des tickets B1-B5) et `docs/journal/ban-radar-tcg-diagnostic.md`.
- Méthode : estimation sur les données, **validation temporelle** (origine glissante, jamais de mélange entre dates),
  comparaison à une méthode naïve, intervalles d'incertitude, graine fixée, script reproductible dans `scripts/`.
- **Aucun changement de ce que le site affiche sans validation de Thomas** : le lot livre l'analyse, le code prêt
  (sur sa branche, fusionné dans l'intégration mais derrière un réglage ou dans une table à part), un journal dans
  `docs/journal/` et un formulaire pré-coché dans `decisions-prises.md`. `WEIGHTS` jamais modifié sans formulaire.
- Écriture en base : table nouvelle seulement, après sauvegarde, transaction unique. `BACKTEST_MIN_DECKS` jamais baissé.
- La relecture par la collaboratrice viendra **après** (décision de Thomas du 18/11) : noter dans chaque journal ce
  qu'elle devra relire.
