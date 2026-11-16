# Tâches de fond (quand la file est vide ou en attente de Thomas)

Ne démarre que si tous les lots de `file.md` sont terminés ou bloqués en attente de validation (lots 15 et 16).
Modèle : Sonnet. Au plus **3 tâches par nuit**, une session neuve par tâche, dans l'ordre ci-dessous, en reprenant
où la nuit précédente s'est arrêtée (noter dans `etat.md`, section « Tâches de fond »).

## Règles
- Branche à part `claude/fond-<AAAA-MM-JJ>`, créée depuis `claude/front-nuit-17-11` (ou `main` si elle a été
  fusionnée). **Un commit par tâche.** Ni `main`, ni push, ni fusion dans la branche d'intégration.
- Interdit : toucher au scoring (`WEIGHTS`, backtest), écrire en base, changer le design, les textes du site ou une
  décision. Rien d'irréversible.
- Arrêt dès que la limite d'usage approche, **sans** reprise programmée pour ces tâches.
- Compte rendu dans `docs/planning/fond/<date>.md` : ce qui a été fait, ce qui est proposé à Thomas.

## Tâches
1. **Revue du code fusionné** (skills `bmad-code-review`, `bmad-review-edge-case-hunter`) sur les commits de la
   branche d'intégration depuis la dernière revue : rapport des bugs, fragilités et cas limites, classés par
   gravité, avec fichier:ligne. **Aucune correction** : Thomas choisit le matin ce qui devient un lot.
2. **Vérification des données** (lecture seule, `file:…?mode=ro`) : fraîcheur (`fetch_health.jsonl`, dates max
   des decks), tables vides ou anormalement petites, cartes sans image, écarts entre `yugioh.db` et `serving.db`
   (`build_serving_db.py --check`), valeurs aberrantes évidentes. **Rapport seul.**
3. **Documentation désynchronisée** : comparer la doc au code réel et corriger la doc seulement
   (`docs/api-contracts.md`, `docs/data-models.md`, `docs/architecture.md`, `README.md`, `docs/ONBOARDING.md`).
   Une ligne par écart corrigé dans le compte rendu. Ne pas toucher au code.
4. **Tests** : ajouter des tests aux routes de l'API et aux fonctions sans test (`backend/tests`), sans modifier le
   code testé. Si un test révèle un bug, le marquer `xfail` avec une note et le signaler au compte rendu.

`python scripts/check.py` doit passer après chaque tâche qui modifie un fichier.
