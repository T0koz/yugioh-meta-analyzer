---
description: Fin de journée — relit les commits du jour, propose la mise à jour de context.md et BACKLOG.md, vérifie Linear, résume en 10 lignes. Ne commite pas.
allowed-tools: Bash(git log:*), Bash(git status:*), Bash(git diff:*), Bash(git show:*), Bash(git branch --list:*), Read, Grep, Glob, Edit
---

Tu fais le point de fin de journée. **Tu proposes, tu ne commites pas, tu ne pousses pas.** Réponds en français.
Argument facultatif : `$ARGUMENTS` = une date `AAAA-MM-JJ` (sinon : aujourd'hui) ou un nom de branche à relire.

## 1. Relire la journée
- `git log --since="<date> 00:00" --until="<date> 23:59" --format='%h %s' --no-merges` (puis sans `--no-merges`
  pour repérer les fusions) sur la branche courante ; avec un nom de branche en argument, lis celle-là.
- `git status --short` : liste ce qui reste non commité (à signaler, pas à régler).
- Regroupe les commits par ticket (`TOK-xxx`, `lot NN`) à partir des préfixes et des messages.

## 2. Proposer les changements de mémoire du projet
- **Règle « une session = une section »** : n'édite que la section du ticket concerné dans `context.md` et
  `BACKLOG.md` ; n'en ajoute une nouvelle que si le ticket n'en a pas encore. Ne touche pas aux sections des
  autres tickets, ni à `docs/planning/etat.md`, `file.md`, `compte-rendu.md`, `regles.md`.
- Dans `BACKLOG.md` : statut du ticket (🔜 → 🟡 livré sur branche non fusionnée → ✅ après fusion), avec
  la mesure ou le résultat qui le justifie, tirés des messages de commit et des journaux `docs/journal/`.
- Dans `context.md` : pièges nouveaux et résultats mesurés, pas de récit ; le détail va dans `docs/journal/`.
- Ne copie aucun chiffre que tu n'as pas lu dans un commit ou un fichier du dépôt. Pas de date inventée.
- **Par défaut, n'édite aucun fichier** : écris le diff proposé dans des blocs ```diff (chemin, lignes
  avant/après). N'applique (Edit) que si la personne l'a demandé dans cet appel (`appliquer`) ; même alors,
  laisse tout non commité.

## 3. Linear (tickets TOK)
- Si un outil Linear (`mcp__*__save_issue`, `list_issues`…) est disponible : propose, ticket par ticket,
  `Done` (fusionné) ou `In Progress` (livré sur branche, non fusionné) ; **ne change rien sans accord**.
- Sinon, dis-le en une ligne (« Linear non connecté : statuts à synchroniser à la main ») et continue sans.

## 4. Résumé de 10 lignes au plus
1. Commits du jour (nombre, tickets touchés)  2. Ce qui est fusionné / seulement sur branche
3. Mesures clés  4. Pièges ajoutés  5. Fichiers de mémoire modifiés (proposés)  6. Linear (état ou « non connecté »)
7. Non commité restant  8. Décisions prises par défaut  9. À valider par la personne  10. Prochaine étape.
Une ligne par point, factuel, sans formule publicitaire.
