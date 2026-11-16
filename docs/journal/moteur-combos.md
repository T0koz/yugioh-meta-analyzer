### 🧩 Moteur de combos (TOK-84, préparation du 2026-11-16)

Projet distinct, documents dans `docs/moteur-combos/` (définitions, schéma `cb_*`, 72 tests Branded
non validés, dossier du juge). Aucun code de moteur. Deux retombées sur le pipeline de données :
- **`scripts/fetch_new_cards.py`** : première étape (non bloquante) du job du lundi. Ajoute les cartes
  absentes de `cards` sans réécrire les existantes (`init_db.py` écraserait `views_week` et les statuts
  de banlist). Avant lui, une carte sortie après le dernier chargement n'avait ni texte ni image.
- **Garde de nom** : YGOPRODeck renumérote parfois une carte (même nom, autre `id`) et l'index sur
  `cards.name` n'est pas unique. Le script n'insère jamais un nom déjà présent (il l'affiche en ⚠).
  Toute autre insertion dans `cards` doit faire le même contrôle, sinon les jointures par nom doublent.
- **Noms à entité HTML** : `cards.name` a contenu `The Fallen &amp; The Virtuous`, que la jointure par
  nom ne trouvait pas. Le script corrige ces noms ; `cards.archetype` n'est pas fiable pour les règles
  du jeu (classement éditorial de YGOPRODeck).
