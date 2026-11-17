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
5. **Confrontation avec une tier list d'experts** (lecture seule, rapport seul, sous-agent `data-scientist-ygo`) :
   source = vidéo Tsugi YGO « Les Meilleurs Deck pour le YCS Paris » (live du 2026-09-15, chapitres seulement :
   Sky Striker, Elfnotes, PP Artmage, PP Pure, RDA, Blitz, Dracotail, Predaplant, Invoked, Sacred Beast, Clown,
   Malice, Yummy, Train/Machina, Blue-Eyes, Killer Tune, Lunalight, Fairy Tail, Spellcaster Pile, Rollad,
   Angelity, Primite, Mitsu, Doom Z, HERO, Branded).
   a. **Angelechy** : passé de ~2,5 % (hybride avec Elfnote, sept. 2026) à 17,1 % des decks TCG en oct. 2026.
      Notre signal précoce, nos prédictions méta ou le journal `prediction_log.jsonl` l'avaient-ils repéré avant
      octobre ? À quelle date, avec quel score ? Sinon, pourquoi (données OCG, seuils, nom d'archétype) ?
   b. **YCS Paris** : le tournoi est-il dans `tournament_decks` ? Si oui, comparer son top (archétypes) à la liste
      de la vidéo et à notre tier list du moment. Signaler les archétypes de la vidéo absents de nos données ou
      classés sous un autre nom (variantes PP, hybrides).
