# Fondations du moteur de combos (indépendantes des règles de jeu)

Modèle : Opus (code de fond, pas de front). **Ne lis jamais le code de Project Ignis** ni le dossier de l'oracle ;
tu peux lire `docs/moteur-combos/reponses-oracle.md` (données). Pas de logique de règles (timing, chaînes, une fois
par tour) : c'est la tranche 0 (TOK-90), qui attend le juge.

**Préalable bloquant** : les décisions D1 à D7 de `docs/moteur-combos/decisions-a-prendre-tok-85-87.md` doivent être
**validées par Thomas** (noté dans ce fichier ou dans `docs/decisions/`). Sinon : arrête-toi et signale-le dans
`etat.md`. Ne valide rien toi-même.

**À faire**
1. Schéma de données de TOK-85 (`definitions-et-schema.md`) en code et en tables, dans une base **à part**
   (`data/combos.db`, ignorée par git), jamais dans `yugioh.db`.
2. Chargement d'un deck (depuis `deck-branded-source.json`) et construction de l'état de départ d'une situation.
3. Harnais de tests qui lit `tests-branded.yaml`, exécute ce qui est exécutable sans règles, et marque chaque test
   « dépend d'un point non validé » (lien vers le point de règle) tant que le juge n'a pas répondu.
4. Tests unitaires (`pytest`) des structures et du chargement.

**Critères** : `check.py` vert ; harnais lancé par une commande unique ; chaque test classé (exécuté / dépend de
Rxx) ; aucune règle de jeu codée ; temps noté dans `chronometrage.md`.
