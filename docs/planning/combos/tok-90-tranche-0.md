# Combos — TOK-90 : tranche 0, un combo Branded de bout en bout

Modèle : Opus. Après le lot 18 (fondations). **Ne lis jamais le code de Project Ignis** ni `~/code/oracle-ignis/` ;
seules ses réponses (`docs/moteur-combos/reponses-oracle.md`) sont lisibles. Règles officielles strictes ; lectures
de règles = `points-de-regle-a-valider.md` (relecture 1 du juge : 32 d'accord, 1 faux R22, 1 ça dépend) et
`reponses-juge-2026-11-17.md`.

**But (décisions du 16/11, § 10.4)** : un combo Branded de 2 à 3 étapes résolu par le moteur, avec un test « attendu »
et trois tests négatifs (hors timing, effet déjà utilisé, matériel manquant), et une carte non encodée qui renvoie
« non couvert » au lieu d'un résultat silencieux. Les règles nécessaires seulement : invocation, activation, coût,
« une fois par tour » dans ses trois formes, chaîne simple. Harnais du lot 18 : ces tests passent de « dépend de Rxx »
à « exécuté ».

**Critères** : les 4 tests de la tranche passent ; « non couvert » renvoyé pour une carte non encodée ; aucune règle
codée au-delà du besoin ; `check.py` vert ; temps noté dans `docs/moteur-combos/chronometrage.md` (TOK-88).

## Contexte au lancement (orchestrateur, 18/11)
- **Lot 18 fusionné** dans `claude/moteur-18-11` : `moteur_combos/`, harnais `python scripts/combos_harnais.py`
  (72 situations : 54 « règles confirmées », 6 « un seul avis », 12 « sans point relu »), 50 tests `pytest`, étape
  dédiée dans `check.py`. Ses 12 décisions par défaut (`docs/planning/2026-11-18/decisions-prises.md`) attendent
  Thomas : appuie-toi dessus, elles sont réversibles, et note toute décision nouvelle au même endroit.
- **Lot 17 fusionné** : l'oracle a répondu aux 34 points (`docs/moteur-combos/reponses-oracle.md`, lisible ; son code et
  `~/code/oracle-ignis/` restent interdits). Il **confirme R08, R27 (b) et R34** (deux avis concordants désormais) et
  **contredit R23** : pour lui l'effet de Phase de Fin d'`Incredible Ecclesia` est facultatif, mais son texte est la
  version OCG (« You can »), alors que le texte TCG de notre base n'a pas « You can ». Règle du projet : le texte TCG fait
  foi ; T37 reste au verdict actuel, marqué « contredit par l'oracle (texte OCG) ». Ne choisis pas la tranche 0 sur T37.
- Le harnais peut ajouter une classe « confirmé par le relecteur et l'oracle » ; si tu le fais, déclare-le.
- Dans un worktree : textes des cartes en lecture seule dans
  `file:/Users/thomascozian/code/yugioh-meta-analyzer/data/yugioh.db?mode=ro`.
- Ne pousse pas, ne fusionne pas ; ne lance ni session ni sous-agent (sauf `gardien-donnees` si tu changes le schéma).
