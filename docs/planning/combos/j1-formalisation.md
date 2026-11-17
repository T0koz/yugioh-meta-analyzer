# Combos — J1 : formaliser toutes les cartes du pilote Branded

Modèle : Opus. Après TOK-90. Même interdit Project Ignis que la tranche 0.

**But (jalon J1)** : 100 % des cartes du deck pilote (`deck-branded-source.json`, 37 cartes distinctes) formalisées
dans le schéma, statut par carte (`non_traitee`, `brouillon`, `formalisee`, `verifiee`, `non_formalisable`, décision
D6). Méthode décidée : un LLM propose la formalisation depuis le texte officiel, le moteur la teste sur
`tests-branded.yaml`, l'oracle compare quand il est disponible, un échantillon est relu (liste pour Thomas / le juge).

**Critères** : toutes les cartes ont un statut ; **taux d'erreur chiffré** sur un échantillon vérifié (méthode et
taille écrites) ; les tests du jeu Branded passent ou sont expliqués ; désaccords avec l'oracle listés ; temps noté.

## Contexte au lancement (orchestrateur, 18/11)
- **C1 fusionné** dans `claude/moteur-18-11` : `moteur_combos/regles.py`, `cartes.py`, `catalogue.py`, `scenarios.py` ;
  5 cartes formalisées (`Aluber`, `Branded Fusion`, `Fallen of Albaz`, `Rindbrumm`, `Tri-Brigade Springans Kitt`),
  10 situations exécutées, 77 tests `pytest`, `check.py --all` vert. Reste **32 cartes** (37 distinctes en Main et Extra ;
  le Side est hors pilote).
- Décisions par défaut de C1 et du lot 18 (`docs/planning/2026-11-18/decisions-prises.md`) : non encore validées par
  Thomas ; appuie-toi dessus (« non couvert » effet par effet, `HORS_PERIMETRE` pour les effets qui supposent
  l'adversaire, ordre des déclencheurs simultanés `non_couvert`). Si J1 exige de coder l'ordre des déclencheurs
  simultanés (R22), fais-le et déclare-le.
- **Oracle** : tu ne lis que `docs/moteur-combos/reponses-oracle.md` (jamais son code ni `~/code/oracle-ignis/`). Pour
  comparer une formalisation nouvelle à l'oracle, il faut le faire jouer par un agent séparé : **liste** dans ton
  rapport les situations à lui soumettre (`docs/moteur-combos/situations-pour-oracle.md`), l'orchestrateur lancera ce
  lot à part. Le taux d'erreur de J1 repose sur : tests du jeu Branded, réponses existantes de l'oracle, et un
  échantillon tiré au hasard (graine fixée) que tu prépares pour relecture humaine.
- R23 / T37 : texte TCG de notre base = effet obligatoire ; l'oracle (texte OCG) dit facultatif. Le texte TCG fait foi.
- Lot long : commite souvent sur ta branche (un arrêt brutal ne doit perdre que l'étape en cours) ; note l'avancement
  carte par carte dans ton rapport. Ne pousse pas, ne fusionne pas ; ne lance ni session ni sous-agent, sauf
  `gardien-donnees` si tu modifies le schéma de `combos.db`, et `data-scientist-ygo` pour la méthode du taux d'erreur.
