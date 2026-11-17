# 0024 — Moteur de combos (D8) : cartes manquantes chargées et table `cards` tenue à jour

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude, par délégation de Thomas (« tu peux pas prendre ces décisions tout seul ? »)
- Tickets : TOK-84, TOK-85, TOK-87

## Contexte
Quatre cartes du deck n'avaient pas de texte dans la base. Thomas a décidé de relancer `fetch_cards.py` (D8, fait le 2026-11-16 : 287 cartes insérées, un nom corrigé). Restait à décider comment garder `cards` à jour (D8 bis).

## Options
- A : étape « cartes nouvelles seulement » dans le job du lundi, et correction de `init_db.py` (qui dupliquait `card_sets`)
- B : rafraîchir toute la table chaque lundi (met aussi à jour `views_week` et les statuts de banlist ; à décider avec le data scientist car le signal précoce lit `views_week`)
- C : rester manuel

## Décision
D8 : relancer `fetch_cards.py` (décision de Thomas). D8 bis : option A (`scripts/fetch_new_cards.py`, première étape non bloquante de `refresh_decks.py`).

## Raison
B changerait les valeurs lues par le signal précoce : à arbitrer avec le data scientist.

## Conséquences
Ambiguïté signalée dans `BACKLOG.md` : `views_week` des cartes existantes n'est jamais rafraîchi, donc le signal précoce compare des instantanés de dates différentes. Actif au prochain lundi une fois la branche fusionnée dans `main`.

## Sources
- `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` (décision D8)
