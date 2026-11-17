# 0052 — Ban Radar : l'omniprésence prédit une partie des bans, le score sert à la tête de liste

- Date : 2026-11-17
- Statut : acceptée
- Décidé par : Thomas (réponse à l'orchestrateur, 17/11, après le lot 12)
- Tickets : TOK-55, TOK-53

## Contexte
`context.md` portait le piège « l'omniprésence seule ne prédit rien », tiré de la v1 du Ban Radar (rang médian 302/681,
au niveau du hasard), calculée sur des données biaisées par le drapeau `illegal`. Le backtest rangé liste par liste du
lot 12 (`docs/journal/ban-historique-tok-55.md`, chiffres vérifiés par `data-scientist-ygo`) compare le score à une base
« staples les plus jouées » (même univers classé par la seule part des decks), sur 10 listes TCG et 10 listes OCG.

## Options
- Garder le piège tel quel.
- Le réviser d'après les données légales.

## Décision
Piège révisé : la popularité seule classe mieux l'ensemble des cartes touchées en TCG (rang médian meilleur que le score
sur 7 listes sur 10), mais le score reste devant en OCG (8 sur 10) et en tête de classement (top 25 de la veille touché
29 fois sur 250 contre 16 en TCG, 41 contre 18 en OCG).

## Raison
Le piège contredisait les données actuelles et aurait orienté à tort une future retouche du scoring.

## Conséquences
- Toute retouche du scoring se compare aux deux bases (hasard et staples), pas au hasard seul.
- Le second piège (« le critère décisif est le nombre moyen d'exemplaires ») repose aussi sur des chiffres de la v1 :
  à recalculer au prochain changement de scoring.
- Aucun `WEIGHTS` modifié par cette décision.
