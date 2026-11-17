# Journal de décisions

Une note par décision structurante (architecture, données, design, process). Le but : savoir dans six mois
**pourquoi** les choses sont comme elles sont.

## Règles
- Fichier `NNNN-titre-court.md` (numéro sur 4 chiffres, suivant le dernier), en français.
- Une décision remplacée n'est pas effacée : on passe son statut à « remplacée par NNNN » et on crée la nouvelle.
- Les décisions prises par défaut pendant une file de nuit restent dans `docs/planning/<date>/decisions-prises.md`
  jusqu'à la revue de Thomas ; celles qu'il valide sont recopiées ici.
- Ajouter une ligne à l'index ci-dessous à chaque nouvelle note.

## Modèle de note
```
# NNNN — Titre

- Date : AAAA-MM-JJ
- Statut : acceptée | remplacée par NNNN | abandonnée
- Décidé par : Thomas (avec Claude / session …)
- Tickets : TOK-…

## Contexte
Le problème, en 2 à 4 phrases.

## Options
- A : …
- B : …

## Décision
L'option retenue, en une phrase.

## Raison
Pourquoi, et ce qu'on accepte de perdre.

## Conséquences
Ce que ça change, ce qu'il faudra revoir et quand.
```

## Index
| # | Date | Décision | Statut |
|---|---|---|---|
| 0001 | 2026-11-16 | [Direction visuelle de la refonte : « Braise vivante »](0001-direction-visuelle-de-la-refonte-braise-vivante.md) | acceptée |
| 0002 | 2026-11-16 | [Préalables bloquants avant la refonte : TOK-83 et erreur 500 de /early-signals](0002-prealables-bloquants-avant-la-refonte-tok-83-et-erreur.md) | acceptée |
| 0003 | 2026-11-16 | [Crédibilité des chiffres traitée avant la nouvelle page d'accueil](0003-credibilite-des-chiffres-traitee-avant-la-nouvelle-page.md) | acceptée |
| 0004 | 2026-11-16 | [Ban Radar : vue par défaut « Pièces d'archétype »](0004-ban-radar-vue-par-defaut-pieces-d-archetype.md) | acceptée |
| 0005 | 2026-11-16 | [Animation : CSS d'abord, puis Motion, GSAP seulement si nécessaire](0005-animation-css-d-abord-puis-motion-gsap-seulement-si-nec.md) | acceptée |
| 0006 | 2026-11-16 | [Couleurs de données : un bleu pour l'OCG et six teintes catégorielles](0006-couleurs-de-donnees-un-bleu-pour-l-ocg-et-six-teintes-c.md) | acceptée |
| 0007 | 2026-11-16 | [Images de cartes hébergées par nous, en trois tailles](0007-images-de-cartes-hebergees-par-nous-en-trois-tailles.md) | acceptée |
| 0008 | 2026-11-16 | [Graphiques : SVG maison avec D3, remplacement de recharts et vis-network](0008-graphiques-svg-maison-avec-d3-remplacement-de-recharts.md) | acceptée |
| 0009 | 2026-11-16 | [Option 3D (Three.js) tardive et limitée au graphe de synergies](0009-option-3d-three-js-tardive-et-limitee-au-graphe-de-syne.md) | acceptée |
| 0010 | 2026-11-16 | [Transitions de page : embellissement, le site marche sans](0010-transitions-de-page-embellissement-le-site-marche-sans.md) | acceptée |
| 0011 | 2026-11-16 | [Calendrier : la refonte passe avant le reste du backlog](0011-calendrier-la-refonte-passe-avant-le-reste-du-backlog.md) | acceptée |
| 0012 | 2026-11-16 | [Première étape de la refonte : formaliser avant de lancer](0012-premiere-etape-de-la-refonte-formaliser-avant-de-lancer.md) | acceptée |
| 0013 | 2026-11-16 | [Moteur de combos : principes, périmètre et pilote Branded](0013-moteur-de-combos-principes-perimetre-et-pilote-branded.md) | acceptée |
| 0014 | 2026-11-16 | [Moteur de combos : n'afficher que ce qui est démontré, « exhaustif » = couverture publiée](0014-moteur-de-combos-n-afficher-que-ce-qui-est-demontre-exh.md) | acceptée |
| 0015 | 2026-11-16 | [Moteur de combos : oracle Project Ignis, local seulement, sans contact avec le LLM](0015-moteur-de-combos-oracle-project-ignis-local-seulement-s.md) | acceptée |
| 0016 | 2026-11-16 | [Moteur de combos : jalons J1 à J3 et règle d'arrêt à 8 semaines](0016-moteur-de-combos-jalons-j1-a-j3-et-regle-d-arret-a-8-se.md) | acceptée |
| 0017 | 2026-11-16 | [Moteur de combos (D1) : deck source du jeu de tests](0017-moteur-de-combos-d1-deck-source-du-jeu-de-tests.md) | acceptée |
| 0018 | 2026-11-16 | [Moteur de combos (D2) : deux niveaux, le pas et la transition](0018-moteur-de-combos-d2-deux-niveaux-le-pas-et-la-transitio.md) | acceptée |
| 0019 | 2026-11-16 | [Moteur de combos (D3) : position des monstres sur le terrain](0019-moteur-de-combos-d3-position-des-monstres-sur-le-terrai.md) | acceptée |
| 0020 | 2026-11-16 | [Moteur de combos (D4) : actions légales mais sans intérêt](0020-moteur-de-combos-d4-actions-legales-mais-sans-interet.md) | acceptée |
| 0021 | 2026-11-16 | [Moteur de combos (D5) : propagation du « non couvert »](0021-moteur-de-combos-d5-propagation-du-non-couvert.md) | acceptée |
| 0022 | 2026-11-16 | [Moteur de combos (D6) : statuts de formalisation des cartes](0022-moteur-de-combos-d6-statuts-de-formalisation-des-cartes.md) | acceptée |
| 0023 | 2026-11-16 | [Moteur de combos (D7) : format du jeu de tests Branded](0023-moteur-de-combos-d7-format-du-jeu-de-tests-branded.md) | acceptée |
| 0024 | 2026-11-16 | [Moteur de combos (D8) : cartes manquantes chargées et table `cards` tenue à jour](0024-moteur-de-combos-d8-cartes-manquantes-chargees-et-table.md) | acceptée |
| 0025 | 2026-11-16 | [Moteur de combos (D9) : commit des documents du moteur](0025-moteur-de-combos-d9-commit-des-documents-du-moteur.md) | acceptée |
| 0026 | 2026-11-16 | [Collaboration : accès direct à main sans revue, dépôt public, garde-fous par outillage](0026-collaboration-acces-direct-a-main-sans-revue-depot-publ.md) | acceptée |
| 0027 | 2026-11-16 | [Base : une copie de référence partagée, pas de base hébergée (option A)](0027-base-une-copie-de-reference-partagee-pas-de-base-heberg.md) | acceptée |
| 0028 | 2026-11-16 | [Transmission de la base à la collaboratrice : Drive nominatif, sans pseudos](0028-transmission-de-la-base-a-la-collaboratrice-drive-nomin.md) | acceptée |
| 0029 | 2026-11-16 | [Stack inchangée pour travailler à deux, avec une liste de frictions à traiter](0029-stack-inchangee-pour-travailler-a-deux-avec-une-liste-d.md) | acceptée |
| 0030 | 2026-11-16 | [Un seul auteur pour le journal des prédictions et une seule base de référence](0030-un-seul-auteur-pour-le-journal-des-predictions-et-une-s.md) | acceptée |
| 0031 | 2026-11-16 | [Graphe de synergies en attente, remplacé par la page Decks (TOK-102 → TOK-114)](0031-graphe-de-synergies-en-attente-remplace-par-la-page-dec.md) | acceptée |
| 0032 | 2026-11-16 | [Déploiement : Vercel gratuit seul, un projet pour le site et l'API (option A, projet yugi-gang)](0032-deploiement-vercel-gratuit-seul-un-projet-pour-le-site.md) | acceptée |
| 0033 | 2026-11-16 | [Front : toujours le modèle le plus puissant disponible](0033-front-toujours-le-modele-le-plus-puissant-disponible.md) | acceptée |
| 0034 | 2026-11-16 | [Ton des textes du site : sobre, statistique, l'explication passe par le graphique](0034-ton-des-textes-du-site-sobre-statistique-l-explication.md) | acceptée |
| 0035 | 2026-11-16 | [Organisation : une seule session de travail à la fois, file continue de nuit](0035-organisation-une-seule-session-de-travail-a-la-fois-fil.md) | acceptée |
| 0036 | 2026-11-16 | [Skills BMad en invocation sur demande, sauf quatorze](0036-skills-bmad-en-invocation-sur-demande-sauf-quatorze.md) | acceptée |
| 0037 | 2026-11-16 | [Contexte chargé à chaque session allégé : journaux déplacés dans docs/journal/](0037-contexte-charge-a-chaque-session-allege-journaux-deplac.md) | acceptée |
| 0038 | 2026-11-16 | [Animation de hero locale, hors Git](0038-animation-de-hero-locale-hors-git.md) | acceptée |
| 0039 | 2026-11-16 | [Libellé de signal boutique par rang de percentile de l'archétype](0039-libelle-de-signal-boutique-par-rang-de-percentile-de-l.md) | acceptée |
| 0040 | 2026-11-16 | [buy_label supprimé de la réponse API, colonne conservée en base](0040-buy-label-supprime-de-la-reponse-api-colonne-conservee.md) | acceptée |
| 0041 | 2026-11-16 | [Données de Kewl Tune figées dans le front pour l'exemple de l'accueil](0041-donnees-de-kewl-tune-figees-dans-le-front-pour-l-exempl.md) | acceptée |
| 0042 | 2026-11-16 | [loading.tsx déplacé de la racine de app/ vers app/ban/](0042-loading-tsx-deplace-de-la-racine-de-app-vers-app-ban.md) | acceptée |
| 0043 | 2026-11-16 | [Champs de date ajoutés à quatre réponses d'API pour les pieds « source + date »](0043-champs-de-date-ajoutes-a-quatre-reponses-d-api-pour-les.md) | acceptée |
| 0044 | 2026-11-16 | [URL d'archétype : /archetype/{slug}, slug calculé et servi par l'API](0044-url-d-archetype-archetype-slug-slug-calcule-et-servi-pa.md) | acceptée |
| 0045 | 2026-11-16 | [GET /archetypes/{slug} : nouvel endpoint sans calcul statistique nouveau](0045-get-archetypes-slug-nouvel-endpoint-sans-calcul-statist.md) | acceptée |
| 0046 | 2026-11-16 | [Résolution d'archétype insensible à la casse (cache de pages corrompu sur macOS)](0046-resolution-d-archetype-insensible-a-la-casse-cache-de-p.md) | acceptée |
| 0047 | 2026-11-16 | [Tests visuels avec Playwright Python plutôt que @playwright/test](0047-tests-visuels-avec-playwright-python-plutot-que-playwri.md) | acceptée |
| 0048 | 2026-11-16 | [Tests visuels sur une fausse API rejouant des réponses JSON commitées](0048-tests-visuels-sur-une-fausse-api-rejouant-des-reponses.md) | acceptée |
| 0049 | 2026-11-16 | [Lot 1 et orchestrateur : décisions mineures de la file du soir](0049-lot-1-et-orchestrateur-decisions-mineures-de-la-file-du.md) | acceptée |
| 0050 | 2026-11-16 | [Lots 2 et 3 : choix de contenu, de palette et de forme des graphiques](0050-lots-2-et-3-choix-de-contenu-de-palette-et-de-forme-des.md) | acceptée |
| 0051 | 2026-11-16 | [Lots 4 et 5 : périmètre des pages, du SEO et des captures](0051-lots-4-et-5-perimetre-des-pages-du-seo-et-des-captures.md) | acceptée |
| 0052 | 2026-11-17 | [Ban Radar : l'omniprésence prédit une partie des bans, le score sert à la tête de liste](0052-ban-radar-l-omniprésence-predit-une-partie-des-bans.md) | acceptée |
| 0053 | 2026-11-18 | [Reprise du moteur de combos : ordre des lots, parallélisme et horloge](0053-reprise-du-moteur-de-combos-ordre-parallelisme-et-horloge.md) | acceptée |
