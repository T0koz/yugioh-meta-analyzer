### 🤝 Collaboration (TOK-107, 2026-11-16)

Une collaboratrice data scientist pousse **directement sur `main`, sans revue**, sur un dépôt **public**.
Règles complètes : `docs/ONBOARDING.md` §8 (humains) et `CLAUDE.md` (agents).

- **`python scripts/check.py`** avant chaque push : choisit les vérifications selon les fichiers modifiés
  (fichiers interdits et identifiants, `WEIGHTS` script = API, tsc + eslint, `build_serving_db.py --check`,
  test de fumée sur les deux bases, backtest si le scoring bouge — affiché, sans seuil). Bibliothèque
  standard seule. Dans un worktree, il prend le venv et la base du dépôt principal pour le test de fumée,
  mais `--check` et le backtest demandent un lien `data/yugioh.db` (ils lisent un chemin fixe).
  `--ci` : mode sans base. Hook optionnel : `git config core.hooksPath .githooks`.
- **CI** `.github/workflows/verifications.yml` : gratuite (dépôt public), aucun secret ; ne bloque rien
  (pas de revue), prévient par e-mail.
- **Piège corrigé** : `build_serving_db.py --check` sur une base absente créait un fichier vide et
  répondait « Couverture OK » (aucune table → aucune orpheline). Il échoue désormais.
- **`.env` n'était pas dans `.gitignore`** : ajouté (`.env`, `.env.*`, sauf `.env.example`).
- **Base pour la collaboratrice** : `scripts/export_db_snapshot.py [--sans-auteurs]` → `~/Desktop/yugioh-DATE.db.gz`
  (~51 Mo, `VACUUM INTO` cohérent même pendant le job du lundi) + `.json` (date, SHA-256). Partage Drive
  nominatif. `tournament_decks.author` = ≈ 15 000 pseudos de joueurs (donnée personnelle), lu par aucune analyse.
- **Une seule base de référence** (Thomas, job du lundi) ; la copie de la collaboratrice est un bac à sable ;
  `prediction_log.jsonl` n'est commité que par Thomas.
- `data/raw/cards.json` (32 Mo) est suivi par Git depuis le premier commit malgré `.gitignore` (données
  publiques, sans risque ; `git rm --cached` à décider).
- **Installation** : `requirements.txt` racine, versions figées sur le venv de Thomas (résolution vérifiée avec `uv pip compile`).
  `backend/requirements.txt` reste la liste minimale du déploiement. `.claude/launch.json` retrouve le venv via
  `git rev-parse --git-common-dir` (marche depuis un worktree et sur un autre poste).
- La collaboratrice utilise **Claude Code** : `CLAUDE.md` s'applique à elle ; accès Linear à lui ouvrir.
- Notes : `docs/collaboration/base-hebergee.md` (pas de base hébergée tant que le pipeline a un seul écrivain :
  Turso gratuit : ~7 M des 10 M lignes écrites/mois partent dans le fetch complet du lundi, Postgres = 1-2 semaines de migration) et
  `docs/collaboration/avis-stack.md` (la stack tient ; ce qui gêne : installation, tests, jobs sur le Mac,
  notebooks qui écrivent en base).
