# Refonte front — décisions du 16 novembre 2026

Suite de l'audit (`rapport.md`, `1-audit.md`, `2-benchmark.md`, `3-proposition.md`). Thomas a répondu
explicitement aux points 11 et 12 ; pour les points 1 à 10, il n'a rien coché d'autre, donc les
recommandations pré-cochées de l'agent sont retenues (à corriger s'il le souhaite).

| # | Sujet | Décision |
|---|---|---|
| 1 | Direction visuelle | **B — « Braise vivante »** : Ember conservé, la carte devient l'objet-signature, langage de mouvement et récit au défilement. |
| 2 | Préalables bloquants | Fusionner le correctif TOK-83 dans `main` et corriger l'erreur 500 de `/early-signals` **tout de suite**. |
| 3 | Crédibilité des chiffres | À traiter **avant** la nouvelle page d'accueil, avec l'agent `data-scientist-ygo` (Elfnote « mars 2027 » déjà à 20 % en TCG, Ash Blossom à 100/100, tier list datée du 17 juin, écart OCG → TCG de 3 ou 4 mois). |
| 4 | Ban Radar | Vue par défaut « Pièces d'archétype », staples génériques en second onglet. |
| 5 | Animation | CSS d'abord, puis Motion ; GSAP seulement si le récit au défilement l'exige. |
| 6 | Couleurs de données | Un bleu pour l'OCG et une palette de 6 teintes pour le radar et le graphe. |
| 7 | Images de cartes | Hébergées par nous, en trois tailles pré-générées. |
| 8 | Graphiques | Remplacer recharts et vis-network : SVG maison avec D3 pour les graphiques, Sigma.js ou PixiJS pour le graphe. |
| 9 | 3D (Three.js) | Option tardive, uniquement pour le graphe de synergies, après le mois 3. |
| 10 | Transitions de page | Oui, comme embellissement (drapeau expérimental de Next 16) ; le site doit marcher sans. |
| 11 | Calendrier | **Tout de suite, en priorité sur le reste du backlog.** |
| 12 | Première étape | **Rien n'est lancé** : on formalise d'abord (document de décisions + tickets Linear). |

## Ce que change la décision 11

La refonte front passe devant le reste du backlog, y compris le moteur de combos (TOK-84), qui
avait été placé « en parallèle ». La décision 3 impose quand même de fiabiliser les chiffres avant
la nouvelle page d'accueil : un site plus beau qui affiche des chiffres faux perdrait sa crédibilité.

## Suivi

Ticket parent dans Linear : voir `BACKLOG.md`, section « Refonte front ». Feuille de route et
critères de réussite : `3-proposition.md`, § 10.
