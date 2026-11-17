# 0016 — Moteur de combos : jalons J1 à J3 et règle d'arrêt à 8 semaines

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (réunion du 2026-11-16)
- Tickets : TOK-84

## Contexte
L'exhaustivité des données peut grossir sans jamais répondre à une question (« piège de l'exhaustivité » noté parmi les risques).

## Options
- Non consignées dans la source.

## Décision
J1 : 100 % des cartes du pilote formalisées avec un taux d'erreur chiffré ; J2 : le moteur retrouve seul les 5 à 10 combos des guides publics ; J3 : il trouve au moins un combo absent des guides, vérifié ensuite. Règle d'arrêt : J2 non atteint en 8 semaines, ou J3 sans résultat → réévaluer l'approche.

## Raison
J3 est le seul jalon qui montre que l'exhaustivité apporte quelque chose.

## Conséquences
Un test avec un ami (un samedi) complète : échec si l'ami ne voit aucune situation où l'outil l'aiderait.

## Sources
- `docs/moteur-combos/decisions-2026-11-16.md` (§ 5, 9)
