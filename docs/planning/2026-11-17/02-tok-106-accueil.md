# 02 — TOK-106 : nouvelle page d'accueil d'après le prototype

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front.

**Lis** : `docs/audit-front/3-proposition.md` (§ 10 « Mois 1 », § 11), `decisions-2026-11-16.md`,
`lighthouse-2026-11-16.md`, `docs/audit-front/prototype/index.html`, `docs/journal/refonte-front-braise-vivante.md`.

**Objectif** : accueil avec hero, preuve au défilement, outils, méthode, pied de page. **Suivre le prototype
fidèlement** ; les textes en français sont rédigés par toi et listés dans le compte rendu pour relecture.

**Critères** : hauteur ≥ 4 écrans ; LCP mobile ≤ 2,0 s (devtools) ; JavaScript transféré ≤ 220 ko ; Lighthouse
Performance ≥ 90 et Accessibilité ≥ 95 ; pied de données (source + date) sous chaque visualisation ; fonctionne
sans JavaScript et avec mouvement réduit ; capture avant/après à 3 largeurs.

**Pièges** : tuile boutique lit `tcg_window_*` (plus `tcg_entry_estimated`) et le nouveau libellé du ticket 01 ;
22 cartes du radar n'ont pas d'image (repli de `CardArt`) ; ne relance pas `fetch_cards.py`.
