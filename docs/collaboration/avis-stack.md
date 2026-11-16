# Avis sur la stack pour travailler à deux (TOK-111)

> Note, **aucun changement de stack**. Rédigée le 2026-11-16 à partir de l'état du dépôt.
> Réponse courte : **la stack tient**. Ce qui gêne à deux, ce ne sont pas les technologies,
> c'est l'outillage autour (installation, tests, jobs liés au Mac de Thomas, notebooks).

## Ce qui tient, à garder

| Brique | Pourquoi elle convient à deux |
|---|---|
| **Python 3.13 + pandas / scikit-learn** | La langue commune d'une data scientist. Rien à changer. |
| **SQLite** | Un fichier, zéro serveur, zéro coût, zéro identifiant. Le pipeline est mono-écrivain (le job du lundi) : la force de Postgres (écritures concurrentes) n'est pas utile aujourd'hui. Voir [`base-hebergee.md`](base-hebergee.md). |
| **FastAPI en lecture seule sur `serving.db`** | Petit, lisible, sans état. Le test de fumée couvre tous les endpoints en 1 s. |
| **Next.js 16 + TypeScript strict** | `tsc` attrape beaucoup d'erreurs sans test. Le front et la data sont des zones séparées : peu de risque de se marcher dessus. |
| **Tables précalculées** | L'API ne calcule rien : une erreur de modèle ne fait pas tomber le site, elle donne un mauvais chiffre (que le test de fumée ne voit pas, mais c'est un problème de validation, pas de stack). |
| **Linear + `BACKLOG.md` + `context.md`** | Mémoire écrite, lisible par un humain et par un agent : précieux à deux. |

## Ce qui gêne à deux, par ordre d'impact

Effort : S = moins d'une demi-journée, M = un à deux jours, L = une semaine ou plus.

| # | Problème | Pourquoi ça gêne à deux | Proposition | Effort |
|---|---|---|---|---|
| 1 | **Presque aucun test automatisé**, et accès direct à `main` sans revue | Une erreur poussée est en ligne et publique immédiatement ; personne ne relit | **Fait dans ce chantier** : `scripts/check.py` (une commande), hook pre-push optionnel, CI GitHub gratuite. **Ensuite** : tests de non-régression sur les chiffres clés (ex. le backtest du Ban Radar ne doit pas perdre plus de N rangs médians), seuil à fixer par la data scientist | S (fait) puis M |
| 2 | **Installation en plusieurs étapes**, sans fichier de dépendances à la racine | Elle passera sa première demi-journée à deviner les paquets (le README et l'ONBOARDING donnent deux listes différentes) ; versions non figées = résultats non reproductibles | Un `requirements.txt` racine (ou `pyproject.toml` + `uv`) avec versions figées, et une commande d'installation unique (`make setup` ou `scripts/setup.sh`) | S |
| 3 | **Jobs liés au Mac de Thomas** (launchd : prix quotidiens, decks du lundi), chemins absolus `/Users/thomascozian/…` dans les `.plist`, `.claude/launch.json` et `docs/development-guide.md` | Si le Mac est éteint, le snapshot des prix est **perdu** (non rattrapable) ; elle ne peut ni relancer ni surveiller le job | Court terme : rendre les chemins relatifs dans `launch.json`. Moyen terme : faire tourner les deux jobs ailleurs. **Option gratuite : GitHub Actions planifié** — *mais* il faut alors stocker la base hors du dépôt public (bucket privé, cf. option B de `base-hebergee.md`) et y accéder avec un secret GitHub. À traiter avec TOK-35 | S puis M |
| 4 | **14 notebooks qui produisent des tables** | Un `.ipynb` est du JSON : deux personnes qui le modifient = conflit illisible. Les sorties sont commitées dans 6 notebooks (diffs bruyants). Les erreurs de logique y sont difficiles à relire | Règle simple : **les calculs qui écrivent en base vivent dans `scripts/`**, les notebooks servent à explorer et à expliquer. Continuer l'extraction commencée par TOK-69 (`build_banlist_features.py`, `build_buy_signals.py` existent déjà). En attendant : vider les sorties avant de commiter (`nbstripout`, gratuit) | M (progressif) |
| 5 | **`context.md` et `BACKLOG.md` modifiés par tout le monde** | Ce sont les fichiers les plus édités : conflits garantis si deux personnes ajoutent une section en même temps | `git pull --rebase` avant de commencer et avant de pousser ; chacun écrit dans **sa** section ; à terme, découper `context.md` (35 Ko) par thème | S |
| 6 | **Journal des prédictions (`prediction_log.jsonl`) commité par deux personnes** | Deux journaux locaux qui ajoutent des lignes → conflits et doublons ; or c'est la **preuve** datée du produit | Un seul auteur : le job du lundi, sur la base de référence (règle écrite dans `CLAUDE.md` et `ONBOARDING.md`) | S (fait) |
| 7 | **`data/raw/cards.json` (32 Mo) suivi par Git** malgré `.gitignore` (commité au tout premier commit, avant la règle) | Chaque clone télécharge 32 Mo et son historique ; pas de risque de confidentialité (données publiques YGOPRODeck) | `git rm --cached data/raw/cards.json` (garde le fichier local, l'historique reste lourd). Décision de Thomas, sans urgence | S |
| 8 | **Ses outils** (agents IA ou non) inconnus | Les consignes vivent dans `CLAUDE.md`, lu seulement par Claude Code | Garder la règle « tout ce qui compte est aussi dans `ONBOARDING.md` » ; si elle utilise un autre agent (Cursor, Copilot…), un `AGENTS.md` racine qui renvoie à `CLAUDE.md` suffit | S |

## Ce qu'il ne faut **pas** changer maintenant

- **Pas de migration vers Postgres** : coût élevé, aucun gain pour un pipeline mono-écrivain
  (cf. `base-hebergee.md`).
- **Pas d'orchestrateur** (Airflow, Dagster, Prefect) : `refresh_all.py` enchaîne déjà les étapes ;
  un orchestrateur ajoute un serveur à maintenir pour un job hebdomadaire.
- **Pas de passage aux pull requests obligatoires** : c'est un choix de Thomas (accès direct). La CI
  et le hook rattrapent l'essentiel sans ralentir. À reconsidérer si une erreur passe en production.
- **Pas de DVC / Git LFS** pour la base : le dépôt est public, la base ne doit pas y être, même en LFS.

## Ordre conseillé

1. (fait) `scripts/check.py`, hook, CI, `.env` ignoré.
2. Fichier de dépendances racine + installation en une commande — **avant** son premier jour.
3. Chemins relatifs dans `.claude/launch.json`.
4. `nbstripout` sur les notebooks.
5. Avec TOK-35 : décider où tournent les jobs et où vit la base de référence.
6. Avec elle : tests de non-régression des chiffres clés.
