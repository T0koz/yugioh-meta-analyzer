# 01 — Seuil absolu Fort / Modéré / Faible (suite de TOK-113)

Modèle : économique (Sonnet). Sous-agent autorisé : `data-scientist-ygo`.

**Problème** : les libellés Fort / Modéré / Faible des signaux boutique sont relatifs au premier du lot (il y a
toujours un « Fort »). Au 16/11 : Raise Moon 100, Trirealm Rift 56,6, Harpie/Amazoness 44,0 (12 signaux : 3 / 5 / 4).
L'accueil (TOK-106) affichera une tuile boutique : il lui faut un libellé honnête.

**À faire**
1. Lis `docs/journal/signal-boutique-v3.md`, le notebook 10 et `scripts/` associés (lecture seule d'abord).
2. Avec `data-scientist-ygo` : proposer des seuils **absolus** sur le score, justifiés par les données (distribution
   des scores sur l'historique, et ce que le journal de prédictions permet de dire). Si les données ne permettent
   pas de justifier de seuils, dis-le : le repli est d'afficher le score avec sa fenêtre et l'avertissement, sans libellé.
3. Appliquer dans l'API (`/boutique/signals`) et la page boutique, avec le texte « seuils provisoires, non validés
   hors échantillon ». Tests backend. Pas de changement de scoring ni de `WEIGHTS`.
4. Consigner la méthode et les seuils dans `docs/journal/seuils-signal-boutique.md`.

**Critères** : plus aucun libellé relatif ; seuils et justification écrits ; `check.py` vert ; page boutique et
tuile de l'accueil lisent le nouveau champ.
