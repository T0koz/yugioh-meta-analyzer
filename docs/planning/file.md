# File d'attente continue — Yugioh Meta Analyzer

Prompt de reprise (identique à chaque fenêtre) : « Lis docs/planning/file.md et reprends la file. »

## Règles
- **Parallélisme (règle de Thomas, 17/11)** : un lot à la fois. Exception unique : si la session en cours est
  bloquée par une attente longue et passive (téléchargement, build ou calcul long, attente d'une validation de
  Thomas), tu peux lancer **une** deuxième session sur un lot qui ne touche pas les mêmes fichiers. **Jamais plus
  de deux sessions.** Dès que l'attente se termine, tu ne relances rien en parallèle. Note le motif dans `etat.md`.
- Tu es l'orchestrateur : tu coordonnes, tu ne codes pas. Une seule session de travail à la fois (sauf l'exception ci-dessus), une session neuve
  par lot, chacune avec le brief indiqué + `docs/planning/2026-11-17/regles.md`.
- Lis d'abord `docs/planning/etat.md` : reprends au premier lot non terminé. Mets `etat.md` à jour **après chaque
  étape** (lot démarré, lot fini, arrêt), et fais commiter souvent sur la branche d'intégration : un arrêt brutal
  ne doit perdre que l'étape en cours.
- Branche d'intégration : `claude/front-nuit-17-11` jusqu'au lot 19 (fusionnée dans `main` le 17/11). **Depuis le 18/11 :
  `claude/moteur-18-11`** (créée depuis `main`, fusionnée à la revue suivante). Ni `main`, ni push.
- **Ordre décidé par Thomas le 18/11** (`docs/decisions/0053-*.md`) : lot 18 et lot 17 **en parallèle** (deux sessions,
  accord explicite), puis la tranche 0 du moteur (TOK-90, brief à écrire), puis les lots 16 et 20.
- Modèle : front = le plus puissant disponible (Fable, sinon Opus) ; données, doc, recherche = Sonnet si tu peux le
  choisir. Note le modèle réellement utilisé dans `etat.md`.
- Limite d'usage : tu ne peux pas lire le pourcentage. Dès qu'un message de limite apparaît ou approche, termine
  l'étape en cours proprement, mets `etat.md` à jour et arrête-toi. La fenêtre suivante reprendra.
- **Reprise automatique (test du 16/11)** : quand la limite apparaît ou approche, avant de t'arrêter, programme ta
  propre reprise avec l'outil de reprise programmée de Claude Code (wakeup / tâche planifiée de la session), environ
  10 minutes après la réinitialisation annoncée par le message de limite (à défaut : 5 h plus tard). Le message
  de reprise : « Lis docs/planning/file.md et reprends la file. ». Note dans `etat.md` l'heure programmée et
  l'outil utilisé. Si aucun outil de ce type n'existe, écris-le dans `etat.md`.
- **Journal de décisions** : toute décision structurante prise pendant un lot (architecture, données, design,
  process) va dans `decisions-prises.md` du jour ; après validation de Thomas, elle rejoint `docs/decisions/`.
- Arrêts aussi si : `check.py` échoue deux fois sur la même cause, ou décision irréversible / hors brief
  (formulaire à cocher dans `etat.md`).

## Lots, dans l'ordre
| # | Lot | Brief | Modèle |
|---|---|---|---|
| 1 | Seuil Fort / Modéré / Faible | `2026-11-17/01-seuil-boutique.md` | Sonnet |
| 2 | TOK-106 accueil | `2026-11-17/02-tok-106-accueil.md` | Fable |
| 3 | TOK-99 dataviz D3 + palette | `2026-11-17/03-tok-99-dataviz.md` | Fable |
| 4 | TOK-101 page d'archétype + transitions | `2026-11-17/04-tok-101-archetype.md` | Fable |
| 5 | TOK-100 SEO + tests visuels | `2026-11-17/05-tok-100-seo-tests-visuels.md` | Fable |
| 6 | Benchmark fonctionnel | `benchmark/brief.md` | Sonnet |
| 7 | Rattrapage du journal de décisions (`docs/decisions/`) | `sprint-2/00-journal-decisions.md` | Sonnet |
| 8 | Composants d'interaction « smooth » (boutons, pills, onglets) | `sprint-2/00-boutons.md` | Fable |
| 9 | TOK-114 Decks (index + fiches) | `sprint-2/01-decks.md` | Fable |
| 10 | TOK-92 images + `cards` dans la chaîne | `sprint-2/02-images-cartes.md` | Sonnet |
| 11 | TOK-103 boutique par archétype | `sprint-2/03-boutique-archetype.md` | Fable |
| 12 | TOK-55 Ban Predictor contre l'historique | `sprint-3/ban-predictor-historique.md` | Fable |
| 13 | Outillage : pré-autorisations + `/fin-de-journee` | `sprint-3/10-outillage.md` | Sonnet |
| 14 | TOK-35 préparation du déploiement | `sprint-3/11-deploiement.md` | Sonnet |
| 15a | TOK-115 diagnostic Ban Radar TCG (avant l'étape 2 du lot 15) | `sprint-3/tok-115-ban-radar-tcg.md` | Opus |
| 15 | Charte ton et explication + système d'explication graphique (arrêt pour validation de la charte) | `sprint-3/12-explication-graphique.md` | Fable |
| 16 | Réécriture des textes du site (arrêt pour validation du tableau) | `sprint-3/13-reecriture-textes.md` | Fable |
| 17 | TOK-86 banc d'oracle Project Ignis (agent séparé) | `combos/tok-86-banc-oracle.md` | Sonnet |
| 18 | Fondations du moteur de combos (arrêt si D1-D7 non validées par Thomas) | `combos/fondations-moteur.md` | Opus |
| 19 | Audit de rigueur statistique de tous les scores (rapport seul) | `sprint-3/audit-rigueur-statistique.md` | Opus |
| 20 | Correctifs de l'audit A1 à A8 (A1-A4 d'abord) | `sprint-3/audit-A1-A8.md` | Opus |

Les tests visuels du lot 5 sont à mettre à jour après les lots 9, 11 et 12 (nouvelles pages).

## Quand la file est vide ou en attente de Thomas
Passe aux tâches de fond : `docs/planning/taches-de-fond.md` (Sonnet, 3 par nuit, branche à part, rapports seuls pour la revue et les données).
