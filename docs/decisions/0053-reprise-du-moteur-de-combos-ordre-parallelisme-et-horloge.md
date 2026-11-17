# 0053 — Reprise du moteur de combos : ordre des lots, parallélisme et horloge de la règle d'arrêt

- Date : 2026-11-18
- Statut : acceptée
- Décidé par : Thomas (avec Claude, session d'orchestration du 17-18/11)
- Tickets : TOK-84, TOK-86, TOK-90

## Contexte
La préparation du moteur est finie (définitions, 72 tests, relecture des 34 points de règle le 17/11). Les lots front
16 et 20 étaient prêts aussi, et la refonte front était jusqu'ici prioritaire. Thomas veut reprendre le moteur.
La règle d'arrêt du 16/11 (J2 non atteint en 8 semaines → réévaluer) n'avait pas de date de départ.

## Options
- Ordre : fondations (lot 18) d'abord, ou oracle (lot 17) d'abord, ou lots front 16 et 20 d'abord.
- Oracle : en parallèle du lot 18 (deuxième session), ou après.
- Branche : branche d'intégration dédiée, ou fusion directe dans `main`.
- Horloge : départ au lancement du lot 18, ou à la tranche 0.

## Décision
Lot 18 d'abord, lot 17 en parallèle dans une session séparée, branche d'intégration `claude/moteur-18-11` créée depuis
`main` et fusionnée à la revue suivante, horloge de la règle d'arrêt partie le 18/11 : **échéance J2 le 13/01/2027**.

## Raison
L'installation de l'oracle est le point le plus incertain (échec le 17/11) : la lancer tôt, pendant les fondations,
dit vite si elle tient. Les deux lots touchent des fichiers différents et doivent de toute façon rester isolés (aucun
agent du moteur ne lit le code de l'oracle). L'horloge part au premier lot de code pour mesurer tout le développement.
On accepte de repousser les lots front 16 et 20, et deux sessions en même temps (règle du 17/11 : jamais plus de deux,
sur demande explicite de Thomas).

## Conséquences
- `docs/planning/file.md` : ordre 18 et 17 (en parallèle), puis tranche 0, puis 16 et 20.
- Le 13/01/2027, faire le point sur J2 ; si les combos manqués passent par `Lubellion`, soupçonner la liste (D1)
  avant le moteur.
