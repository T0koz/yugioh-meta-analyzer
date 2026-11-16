# Moteur de combos Yu-Gi-Oh! — décisions de la réunion du 16 novembre 2026

> **Participants.** Thomas (décide). Orchestrateur : Claude. Voix : John (produit), Winston
> (architecture), Amelia (développement), Noether (data science), Mary (marché), Sally (UX).
> Les voix sont des personnages joués par un modèle de langage, sans accès aux outils : leurs
> affirmations ne sont pas vérifiées, sauf mention contraire. Seul le spike sur les simulateurs
> (§ 6) repose sur des sources consultées.

## 1. L'idée en une phrase

Un système qui calcule, à partir des **textes officiels des cartes** et des **règles officielles**,
les combos possibles de Yu-Gi-Oh!, avec leurs conditions, et qui permet de les interroger.

## 2. Pourquoi

- **Cible B2C d'abord.** Un joueur voit vite l'impact de changer une carte dans son deck, et
  l'impact d'un ban. Aujourd'hui, il consulte des tier lists et passe des heures sur Discord à en
  débattre.
- Le cœur est la **visibilité globale sur les combos**. Le ban n'est qu'une partie du projet.
- **B2B** : gain faible pour le seul Yu-Gi-Oh. À terme, couvrir d'autres TCG pour qu'il devienne
  significatif.
- Premier usage attendu : **naviguer entre les combos**, avant « et si je retire cette carte ? ».

## 3. Principe directeur

**Data-first.** La conception n'est pas guidée par ce que l'utilisateur final demandera : on vise
l'exhaustivité de la donnée récupérée et de son traitement dès le départ. L'interface vient après.

## 4. Décisions

| Sujet | Décision |
|---|---|
| Combo | Suite de cartes, avec ou sans ordre, composée de micro-combos (ABCD contient AB, BC, CD). Enregistré dans son ordre réel, interrogeable « A puis directement B » ou « A et B ensemble ». Un macro-combo sur plusieurs tours est fait de micro-combos. |
| Relations entre deux cartes | Quatre familles, qui peuvent coexister : déplacer la carte, servir de matériel ou de coût, conditionner, interagir avec le jeu adverse. |
| Conditions | Rattachées aux étapes (une ou plusieurs), elles ne font **pas** partie du combo. |
| Hasard | Affiché comme une condition. Les probabilités viennent plus tard. |
| Moteur | **Le nôtre**, avec les règles officielles **strictes dès le départ** (chaînes, timing, rulings). |
| Formalisation des effets | Un LLM propose, le moteur teste, l'oracle compare, un échantillon est relu. |
| Ce qui est affiché | Seulement ce qui est démontré. Un combo qui contient une carte non vérifiée reste visible, **étiqueté « non vérifié »**, séparé des combos démontrés. |
| Jugement | Le système **recense sans juger** : il décrit le plateau final, « optimal » se déduit ensuite. |
| « Exhaustif » | 100 % des cartes **classées avec un statut** (formalisée, vérifiée, non formalisable) et un **taux de couverture publié**. Pas la promesse que tout est exécutable. |
| Erreur tolérée | Borne haute inférieure à 5 % à 95 % de confiance, soit environ 60 cas indépendants par strate de cartes à risque. |
| Mode | Le mode « absolu » (les cartes à chercher sont supposées disponibles) est la base technique. Le mode **decklist** porte la valeur pour le joueur. |
| Point de départ | **Tour d'ouverture** d'abord, avec un modèle d'état générique pour les tours suivants. |
| Définitions | **État** = la photo du jeu (main, terrain, cimetière, bannies, deck, effets « une fois par tour » consommés). **Action** = invoquer, activer, choisir une cible. **Équivalence** = deux chemins qui mènent à la même photo donnent le même état. **Arrêt** = plus d'action légale, ou profondeur maximale, boucles coupées. |
| Adversaire | Hors du premier pilote. La place d'un point d'interruption est réservée dans le modèle. |
| Livrable | Base de données + API de requêtes. Plus tard, une interface qui supporte de nombreux combos, avec filtres, prévisualisation et autocomplétion (pas de page minimale). |
| Format | Règles du jeu papier, cartes TCG. |
| Pilote | **Branded** + les cartes jouées avec lui dans les decks de tournoi. Jeu de test : un deck Branded réel. |
| Oracle de test | **Project Ignis (EDOPro)**, avec repli sur Fluorohydride si le branchement coince. Voir § 6. |
| Calendrier | Pas de date. Chaque étape est prévue et **chronométrée**, pour calibrer les estimations futures. |
| Place dans le projet | En parallèle du produit actuel. Le nettoyage du backlog reste prioritaire. |

## 5. Jalons et règle d'arrêt

- **J1** : 100 % des cartes du pilote Branded formalisées, avec un taux d'erreur chiffré sur un
  échantillon vérifié.
- **J2** : le moteur retrouve seul les 5 à 10 combos décrits par les guides publics.
- **J3** : il trouve au moins un combo qu'aucun guide ne cite, vérifié ensuite. C'est le seul jalon
  qui montre que l'exhaustivité apporte quelque chose.
- **Test avec un ami (un samedi)** : échec si l'ami ne voit aucune situation où l'outil l'aiderait.
- **Règle d'arrêt** : si J2 n'est pas atteint en 8 semaines, ou si J3 ne donne rien, on réévalue
  l'approche.

## 6. L'oracle de test (résultat du spike)

Un **oracle** est une source de vérité externe à laquelle on compare les réponses de notre moteur.
On lui donne la même situation et on compare : un désaccord signale une erreur, qu'on tranche avec
les règles officielles.

Ce que le spike a vérifié (sources : dépôts GitHub `ProjectIgnis/CardScripts`,
`edo9300/ygopro-core`, `Fluorohydride/ygopro-core`, `Fluorohydride/ygopro-scripts`) :

- Les **23 cartes Branded** et les **56 cartes** avec leur soutien ont un script. Environ
  **325 cartes TCG de 2026 sur 329** sont scriptées.
- Le moteur est une bibliothèque C qu'on peut appeler sans interface.
- Les scripts Ignis sont mis à jour en continu (plus de 100 changements le mois précédent).
- **Licence AGPL-3.0** pour le moteur et les scripts Ignis (revérifiée dans les fichiers `COPYING`).

**Trois conditions d'usage**

1. **Local seulement** : jamais intégré ni exposé dans le produit (l'AGPL imposerait de publier
   notre code). Les textes et images des cartes appartiennent à Konami : risque distinct, sans
   conclusion juridique.
2. **Indépendance** : les scripts de l'oracle ne sont **jamais** fournis au LLM qui formalise nos
   effets, ni à l'agent qui code notre moteur. Limite non exclue : le LLM a pu voir ces scripts
   publics pendant son entraînement.
3. **Effort** : environ 3 à 6 jours pour un banc de comparaison (estimation, pas une mesure).

## 7. Hors périmètre pour l'instant

- Probabilités d'ouvrir une main.
- Effets du jeu adverse (on ne traite que le premier tour).
- Délai de prise en charge des nouvelles cartes.
- OCG, Master Duel et autres formats.
- **Hypothèse du ban** (la place d'une carte dans les combos prédit-elle son ban ?). Selon Noether,
  elle n'est pas testable aujourd'hui : environ 11 cartes touchées par liste, deux listes
  exploitables, et des textes de cartes actuels, pas ceux de l'époque. Mise de côté, pas abandonnée.

## 8. Questions ouvertes

1. **Qui juge les résultats**, puisque Thomas ne joue pas ? L'ami testeur joue-t-il ?
2. **Budget** : combien d'heures par semaine ?
3. Le moteur Ignis liste-t-il bien **toutes** les actions légales à chaque étape ?
4. Le banc d'oracle tourne-t-il sur **Mac avec Python 3.13** ?
5. Les scripts suivent-ils les rulings **TCG** ou **OCG** quand les deux diffèrent ?
6. **Boucles**, **textes de cartes à une date passée** (errata), **source des textes OCG**.
7. L'hypothèse de Winston, « une transition ne dépend que des cartes qu'elle nomme », qui rendrait
   « retirer X » peu coûteux, tient-elle face aux effets en chaîne ?

## 9. Risques identifiés

- **Charge** : plusieurs centaines d'heures pour formaliser toutes les cartes (estimation
  d'Amelia, à mesurer sur un lot de 100).
- **Erreurs corrélées** si le LLM vérifie ce qu'il a lui-même produit : d'où l'oracle indépendant.
- **Explosion combinatoire** : « tous les combos » doit être borné (main fixe, profondeur).
- **Piège de l'exhaustivité** : les données grossissent sans qu'aucune question n'en change la
  réponse. Les jalons J2 et J3 servent à le détecter.
- **Pas de juge humain** identifié.

## 10. Prochaines étapes proposées (à valider par Thomas)

1. Écrire les **définitions formelles** et le **schéma de données** : cartes, états, transitions,
   relations, conditions, statuts de formalisation.
2. Construire le **banc d'oracle Ignis** en local et lever les inconnues 3 à 5.
3. Écrire le **jeu de tests Branded à la main**, à partir d'un deck de tournoi réel, avant le moteur.
4. **Tranche 0** : un combo Branded de 2 à 3 étapes, un test « attendu » et trois tests négatifs,
   et une carte non encodée qui renvoie « non couvert » au lieu d'un résultat silencieux.
5. **Chronométrer** chaque étape.
