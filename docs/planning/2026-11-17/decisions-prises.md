# Décisions prises par défaut — file front du 2026-11-16 (soir)

Une ligne par décision imprévue : ticket, question, choix, raison.

| Ticket | Question | Choix | Raison |
|---|---|---|---|
| Orchestrateur | Le brief demande `main` = `origin/main` avant de créer la branche d'intégration ; `main` local a 4 commits d'avance (les briefs `docs(planning)` non poussés), 0 de retard. | Branche `claude/front-nuit-17-11` créée depuis `main` **local** (`cb2e9fb`), sans pousser. | Les briefs n'existent que dans ces 4 commits ; `main` n'est pas en retard sur `origin/main`, donc rien à récupérer. Réversible (la branche peut être rebasée). |
| Orchestrateur | Où fusionner les lots : la branche d'intégration doit être extraite quelque part. | Le dépôt principal est basculé sur `claude/front-nuit-17-11` (il n'est plus sur `main`). | C'est le seul checkout qui a `data/*.db` et `node_modules`, donc le seul où `scripts/check.py` tourne en entier. Retour : `git checkout main`. |
| Orchestrateur | `regles.md` (§ lots lancés à la main) dit que la session fusionne elle-même et supprime son worktree ; l'orchestrateur dit que c'est lui. | L'orchestrateur fusionne, lance `check.py`, écrit le compte rendu et nettoie ; les sessions s'arrêtent après leur dernier commit. | Un seul acteur écrit sur la branche d'intégration : pas de fusion concurrente. |
| Lot 01 (TOK-113) | Les données ne justifient aucun seuil en points ; faut-il le repli sans libellé ? | Libellé par **rang de percentile** de l'archétype parmi les archétypes OCG (Fort ≤ 10 %, Modéré ≤ 25 %), calculé à la volée, mention « provisoire, non validé ». Repli sans libellé automatique si la table de référence manque. | Recommandation du data scientist : un rang est stable dans le temps, un seuil en points dérive ; réversible (aucun recalcul, aucune écriture en base). |
| Lot 01 (TOK-113) | La base de service existante n'a pas `ocg_archetype_scores`, et je n'ai pas le droit d'écrire en base. | Table ajoutée à `SERVED_TABLES` ; l'API dégrade en `signal_label = null` tant que `serving.db` n'est pas reconstruite. | Règle de la nuit : pas d'écriture dans la base de référence. |
| Lot 01 (TOK-113) | `buy_label` : supprimé de l'API ou conservé ? | Supprimé de la réponse API (remplacé par `signal_label`), colonne laissée en base. | « Plus aucun libellé relatif » ; la colonne en base évite de toucher au scoring. |
