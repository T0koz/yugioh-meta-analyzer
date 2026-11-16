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
