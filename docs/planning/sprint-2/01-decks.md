# 01 — TOK-114 : Decks, index des archétypes et fiche de composition

Modèle : le plus puissant disponible (données + front). Sous-agents autorisés : `gardien-donnees` (table,
`SERVED_TABLES`), `data-scientist-ygo` (seuils), en lecture seule sauf la table créée par ce ticket.

**Pourquoi** : le graphe de synergies ne montre que des cartes jouées ensemble ; une liste de deck le dit mieux.

**À faire**
1. Script `scripts/build_archetype_profiles.py` (pas de notebook) : pour chaque archétype et chaque zone
   (main, extra, side), part des listes contenant la carte et nombre d'exemplaires habituel (médiane), sur les
   decks légaux à la date du tournoi, fenêtre récente (même logique de fenêtre que la tier list,
   `backend/app/tiering.py`). Modèle : `archetype_extra_profile` (notebook 02). Ajouter le script à
   `scripts/refresh_all.py`. Sauvegarde de la base avant la première écriture.
2. Seuils « de base » / « d'appoint » avec `data-scientist-ygo`, justifiés sur la distribution ; défaut si rien
   ne se justifie : base ≥ 80 % des listes, appoint 20 à 80 %. Les documenter dans `docs/journal/`.
3. API : `GET /decks` (index) et `GET /decks/{archetype}` (fiche, avec 3 à 5 listes récentes et leur résultat).
   Tables ajoutées à `SERVED_TABLES`, `python scripts/build_serving_db.py --check`. `deck_cards` brute n'entre pas
   dans la base de service : servir un extrait précalculé des listes récentes.
4. Pages `/decks` et `/decks/[archetype]` : `CardArt`, tableaux par zone, source + date sous chaque tableau,
   `metadata`. Lien depuis la tier list et depuis la page d'archétype de TOK-101 si elle existe.

**Critères** : `check.py` vert ; test de fumée de l'API couvre les deux routes ; LCP ≤ 2,0 s (devtools) ;
Lighthouse Accessibilité ≥ 95 ; la dépendance d'un archétype à une carte se lit sans calcul (« 95 % des listes ») ;
captures à 3 largeurs.
