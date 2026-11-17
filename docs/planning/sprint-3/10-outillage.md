# 10 — Outillage : moins de validations, fin de journée automatique

Modèle : Sonnet. Aucun code du site. Pas de push.

**1. Pré-autorisations** (`.claude/settings.json`, partagé, et non `settings.local.json`) : autoriser sans clic les
commandes sûres : lecture (`ls`, `cat`, `grep`, `find`, `rg`, `head`, `tail`, `wc`), `git status/diff/log/show/
branch/worktree list`, `python scripts/check.py`, `npx tsc --noEmit`, `npx eslint`, `npm run lint/build/lighthouse`,
`pytest`, `python scripts/build_serving_db.py --check`, Playwright du projet. Lis la doc des réglages de ta version
de Claude Code avant d'écrire (syntaxe des règles). Ne pré-autorise rien qui écrit en base ou supprime.

**2. Garde-fou par hook** : un hook `PreToolUse` qui refuse `git push`, `--force`, `--no-verify` et `rm -rf` hors
`.claude/worktrees/`, avec un message clair. Test : montre qu'une commande interdite est bloquée.

**3. Commande `/fin-de-journee`** (`.claude/commands/` ou skill du projet) : relit `git log` du jour, met à jour la
section concernée de `context.md` et `BACKLOG.md`, synchronise les statuts Linear (Done / In Progress) si le MCP
est connecté, et rend un résumé de 10 lignes. Elle propose les changements, ne commite pas.

**4. Règle d'or** dans `CLAUDE.md` : « une seule session de travail à la fois ; une deuxième seulement sur demande
explicite de Thomas ».

**Critères** : une session de test n'affiche plus de demande de validation pour les commandes listées ; le hook
bloque les commandes interdites ; `/fin-de-journee` produit un diff correct sur la journée ; `check.py` vert.
