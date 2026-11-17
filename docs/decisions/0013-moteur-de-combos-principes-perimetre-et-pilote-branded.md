# 0013 — Moteur de combos : principes, périmètre et pilote Branded

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (réunion du 2026-11-16, voix simulées par un modèle de langage)
- Tickets : TOK-84, TOK-85

## Contexte
Thomas veut un système qui calcule les combos possibles à partir des textes officiels des cartes et des règles. Il ne joue pas à Yu-Gi-Oh : les choix de règles ne peuvent pas venir de lui.

## Options
- Non consignées en tant qu'options dans la source (tableau de décisions uniquement).

## Décision
Projet distinct du produit d'analyse, mené en parallèle ; principe « data-first » ; moteur à nous avec règles strictes ; tour d'ouverture d'abord ; pilote Branded avec un deck de tournoi réel ; livrable = base de données + API ; adversaire, probabilités, OCG et hypothèse du ban hors périmètre.

## Raison
Cible B2C d'abord (voir l'impact d'un changement de carte ou d'un ban). Le B2B est jugé faible pour le seul Yu-Gi-Oh. L'hypothèse du ban est « mise de côté, pas abandonnée » : environ 11 cartes touchées par liste, deux listes exploitables (avis de la voix data science, non vérifié).

## Conséquences
Le moteur ne passe pas avant la refonte front (décision 11, TOK-94). Le calendrier n'a pas de date : chaque étape est chronométrée (TOK-88). Les voix de la réunion sont jouées par un modèle : leurs affirmations ne sont pas vérifiées, sauf le spike sur les simulateurs.

## Sources
- `docs/moteur-combos/decisions-2026-11-16.md` (§ 1 à 4, 7, 9)
