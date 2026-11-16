# 03 — TOK-103 : boutique regroupée par archétype, courbes de prix

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front. Sous-agent autorisé : `data-scientist-ygo` (lecture seule).

**À faire** : page boutique regroupée par archétype (signal v3, fenêtre d'arrivée en TCG, libellé du seuil du
sprint 1), courbe de prix par carte en SVG maison (palette de TOK-99). L'historique est irrégulier avant
novembre 2026 : **montrer les trous, ne pas lisser ni interpoler**. Pied de données sur chaque courbe.

**Critères** : un trou de données est visible comme tel sur la courbe ; source + date partout ; LCP ≤ 2,0 s ;
Accessibilité ≥ 95 ; `check.py` vert. Le test avec 3 gérants de boutique est fait par Thomas, hors de cette session :
prépare seulement un court scénario de test dans `docs/`.
