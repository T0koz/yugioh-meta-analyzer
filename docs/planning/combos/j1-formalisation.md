# Combos — J1 : formaliser toutes les cartes du pilote Branded

Modèle : Opus. Après TOK-90. Même interdit Project Ignis que la tranche 0.

**But (jalon J1)** : 100 % des cartes du deck pilote (`deck-branded-source.json`, 37 cartes distinctes) formalisées
dans le schéma, statut par carte (`non_traitee`, `brouillon`, `formalisee`, `verifiee`, `non_formalisable`, décision
D6). Méthode décidée : un LLM propose la formalisation depuis le texte officiel, le moteur la teste sur
`tests-branded.yaml`, l'oracle compare quand il est disponible, un échantillon est relu (liste pour Thomas / le juge).

**Critères** : toutes les cartes ont un statut ; **taux d'erreur chiffré** sur un échantillon vérifié (méthode et
taille écrites) ; les tests du jeu Branded passent ou sont expliqués ; désaccords avec l'oracle listés ; temps noté.
