# 0056 — Mise en ligne : moteur en pause, corrections affichées du bloc A avant le premier déploiement

- Date : 2026-11-19
- Statut : acceptée
- Décidé par : Thomas (avec Claude, session d'orchestration du 19/11)
- Tickets : TOK-35, TOK-82, TOK-122, TOK-116, TOK-130, TOK-132, TOK-129, TOK-128, revue de code du 17/11

## Contexte
La release `v2026.11.18` est prête mais non poussée. Elle affiche des chiffres ou des libellés que des mesures des
jalons 1 à 3 ont montrés faux ou trompeurs (cartes suivies, « decklists légales », tableau des tendances de `/methode`,
légende de l'exemple Kewl Tune, onglet « Impact »). Le moteur de combos était la priorité n° 1 (décision 0053).

## Décision
- **Moteur de combos en pause** à partir du 19/11 ; priorité à la mise en ligne. L'horloge de la règle d'arrêt
  (J2 avant le 13/01/2027) n'est pas suspendue.
- **Bloc A de `docs/planning/2026-11-19/formulaires-a-trancher.md` validé tel que pré-coché** (« tout validé go ») :
  A1 chiffres de vitrine (commit `f485ca1`) ; A2 tableau des tendances retiré de `/methode`, marquage « limite » gardé,
  population précisée sous le r ≈ 0,53 de l'accueil, gain −4 % non affiché ; A3 légende Kewl Tune avec les effectifs
  servis, fenêtre fixe ; A4 fenêtre d'arrivée 75-202 j libellée en archétypes (27 sur 36, 12 sur 18 en 2026) ;
  A5 « Impact » → « Diffusion », simulateur décrit sans prévision avec les archétypes de deck qui jouent la carte,
  appliqué avant la relecture de la collaboratrice ; A6 page des signaux précoces gardée en attendant un backtest du
  classement d'archétypes ; A7 textes du lot 16 confirmés ; A8 lots C (témoin de base dans `deploy_prebuilt.py`) et
  D (durcissement de l'API) avant la mise en ligne, lots A, B, E après, rapport de revue fusionné.
- **Jalon n°8 = mise en ligne** (E4) : le bloc A est appliqué en un lot, puis la release `v2026.11.19` remplace
  `v2026.11.18`.

## Raison
Le site est public, même s'il n'est pas diffusé : la première version en ligne ne doit pas porter d'erreur déjà
mesurée. Les blocs B à E ne changent rien d'affiché avant le 31/12 et restent en attente.

## Conséquences
- `v2026.11.18` n'est pas poussée ; Thomas pousse `v2026.11.19`.
- Les blocs B (jalon 4, avant le 31/12), C, D et E restent à trancher.
