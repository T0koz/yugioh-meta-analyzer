# TOK-55 — Ban Predictor contre l'historique

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front. Sous-agent : `data-scientist-ygo`
(chiffres, lecture seule).

**But** : une page publique qui montre, banlist par banlist, ce que le Ban Radar prévoyait **avant** l'annonce et ce
que Konami a réellement fait. C'est la preuve de crédibilité du site.

**À faire**
1. Avec `data-scientist-ygo` : reprendre les résultats du backtest existant (`python scripts/build_ban_radar.py
   --backtest`, journal des prédictions `ban_risk_tcg`, mesures concluantes TCG mai 2026 et OCG juillet 2026).
   Les chiffres affichés sont ceux du backtest, sans fuite de données (seules les données disponibles avant
   chaque annonce). Ne jamais baisser `BACKTEST_MIN_DECKS`. Pas de changement de `WEIGHTS`.
2. Page `/ban/historique` (ou onglet du Ban Center) : frise des banlists ; pour chacune, top N prévu face aux
   cartes réellement touchées ; taux de réussite et base de comparaison (hasard, ou « staples les plus jouées »).
   **Réussites ET échecs** (ex. Ash Blossom en tête, jamais touchée). Source + date sous chaque vue. Ton sobre.
3. Si une donnée manque à l'API : nouvel endpoint, tables dans `SERVED_TABLES`, `build_serving_db.py --check`.

**Critères** : chiffres vérifiés par `data-scientist-ygo` et identiques au backtest ; échecs visibles ; base de
comparaison affichée ; LCP ≤ 2,0 s ; Accessibilité ≥ 95 ; `check.py` vert.
