# TOK-115 — Ban Radar TCG : pourquoi il ne bat pas la méthode « cartes les plus jouées »

Modèle : Opus. Agent `data-scientist-ygo`. Lecture seule de la base, aucun changement de `WEIGHTS` sans formulaire
validé par Thomas. Ticket Linear TOK-115 (constat et attendus détaillés). Livrable : diagnostic dans
`docs/journal/ban-radar-tcg-diagnostic.md` + formulaire de décision dans `decisions-prises.md`. À faire **avant**
l'étape 2 du lot 15 (le verdict de la page historique en dépend).

## Approche data science demandée par Thomas (17/11)
Estimer les poids à partir des données au lieu de les fixer à la main, puis comparer au modèle actuel.
1. **Jeu de données** : une ligne par (banlist, carte jouée dans la fenêtre des 6 mois précédents) ; variables = les
   6 critères calculés avec les seules données disponibles la veille (pas de fuite : statut de restriction et decks
   antérieurs à la date) ; cible = carte touchée (1) ou non (0). Réutiliser `build_ban_radar.backtest_lists`.
2. **Modèle** : régression logistique (coefficients lisibles = poids), avec `class_weight="balanced"` (peu de cartes
   touchées). Option de comparaison : un modèle à arbres, seulement s'il apporte un gain net.
3. **Validation temporelle** : entraîner sur les listes anciennes, tester sur la suivante, en avançant dans le temps
   (jamais de mélange aléatoire entre dates). TCG et OCG séparés, puis ensemble avec une variable de format.
4. **Mesures** : celles de la page historique (rang médian, cartes touchées dans le top 25) face au hasard, aux
   « cartes les plus jouées » et aux poids actuels ; plus AUC et précision moyenne. Intervalles d'incertitude :
   20 listes, c'est peu.
5. **Vérifier la leçon d'août** (« l'omniprésence seule ne prédit rien ») sur les 20 listes.
6. **Décision** : nouveaux poids adoptés seulement s'ils battent les poids actuels ET les staples sur les listes
   tenues à l'écart. Formulaire pour Thomas ; `WEIGHTS` changés dans le script et l'API ensemble, `--backtest` relancé,
   `BACKTEST_MIN_DECKS` jamais baissé. Expliquer la démarche pas à pas (Thomas suit le bootcamp Le Wagon).
