# 0038 — Animation de hero locale, hors Git

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (piste visuelle du 2026-11-16, « à étudier, rien d'imposé ») ; gardée comme piste par Thomas le 2026-11-17
- Tickets : TOK-106, lot 15

## Contexte
Thomas souhaite un hero animé dont le contenu vidéo lui appartient.

## Options
- Non consignées dans les sources.

## Décision
Emplacement `frontend/public/local-hero/` ignoré par Git (`hero.webm`, `hero.mp4`, `hero.jpg`) ; boucle lente sous un voile ; image fixe si mouvement réduit ; repli original (courbes OCG / TCG) si le fichier est absent.

## Raison
Le contenu fourni par Thomas ne va jamais dans Git ni en ligne.

## Conséquences
Statut : piste inscrite dans le brief du lot 15, « rien d'imposé » ; la source ne dit pas qu'elle est tranchée, d'où l'ambiguïté. Autres pistes du même brief : composition en couches (solidroad.com), clears.ai.

Revue du 2026-11-17 : Thomas garde la piste telle quelle. L'emplacement reste réservé ; le hero affiche les courbes OCG / TCG tant qu'il ne fournit pas la vidéo (formulaire de la charte : « repli en courbes d'abord »). Aucun ticket ouvert.

## Sources
- `docs/planning/sprint-3/12-explication-graphique.md` (Pistes visuelles de Thomas)
