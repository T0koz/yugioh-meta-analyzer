# Réponses du premier relecteur (TOK-89) — 17 novembre 2026

> Source : réponses au Google Form « Relecture des règles Yu-Gi-Oh! — Branded » (export CSV, 1 répondant,
> 18/11 00 h 17 heure de La Réunion) et transcription de l'entretien mené par Thomas le même soir, où les
> questions ont été parcourues ensemble. La transcription n'est pas versée au dépôt (conversation privée) ;
> ce qui en est tiré est résumé ici. Le relecteur reste anonyme (pseudo laissé vide).

## Qui a répondu

- **Joueur de tournoi régulier, pas arbitre.** Le formulaire porte « Arbitre (juge certifié) », mais il dit
  pendant l'entretien ne pas avoir la certification. On le compte comme joueur de tournoi (niveau 2 du dossier).
- Il ne joue pas Branded : il connaît les règles générales, pas les lignes de combo du deck.
- Il a lu chaque « lecture supposée » avant de répondre : ses accords sont exposés à un **biais d'ancrage**
  (tendance à confirmer ce qu'on lit). Un « d'accord » vaut donc moins qu'une réponse donnée à l'aveugle.

## Résultat en un coup d'œil

| | Nombre |
|---|---|
| Questions fermées | 34 |
| D'accord | 32 |
| Faux | 1 (R22, sur la seconde moitié de la lecture) |
| Ça dépend | 1 (R34 : (a) et (c) justes ; (b), où la lecture disait « je ne sais pas », tranché) |
| Je ne sais pas | 0 |

**Taux d'erreur mesuré** : 1 lecture contestée sur 34, soit 3 % ; intervalle de Wilson à 95 % : 0,5 % à 14,9 %.
Si R22 se révèle un malentendu (voir plus bas) : 0 sur 34, intervalle 0 % à 10,2 %. C'est la première mesure du
taux d'erreur du projet ; elle repose sur un seul relecteur non arbitre, des questions écrites par le modèle
lui-même et un risque d'ancrage : **à lire comme une borne optimiste**, pas comme une validation.

Les questions ouvertes ont fait apparaître **une hypothèse fausse** (question 3, sur les colonnes) et deux
nuances (questions 1 et 4) : elles pèsent plus que le score ci-dessus, parce qu'elles touchent la décision D3.

## Verdict par point

| N° | Réponse | Ce qu'il a ajouté (formulaire et entretien) |
|---|---|---|
| R01 | d'accord | On ne peut pas activer un effet qu'on ne peut pas résoudre (chercher une carte absente du Deck). Si un effet a plusieurs étapes et qu'une bloque, on résout « au maximum ». En tournoi, une activation impossible faite par erreur est une faute de jeu (avertissement) : l'adversaire ne sait pas que le Deck était vide et peut gaspiller une annulation. Pour le moteur : activation illégale, lecture confirmée. |
| R07 | d'accord | « Avant » et « après » la carte : la formulation suffit. |
| R08 | d'accord | Question jugée mal posée (« oui aux deux » pour ce qui semblait une seule question), mais lecture juste. |
| R09 | d'accord | Un monstre envoyé de l'Extra Deck au Cimetière n'a pas été « correctement invoqué » et ne peut pas en être ressuscité. Règle qu'il rappelle souvent en tournoi. |
| R10 | d'accord | Question de niveau « diplôme d'arbitre » selon lui. |
| R14 | d'accord | — |
| R17 | d'accord | Un deux-points ou un point-virgule après « Discard 1 card » en ferait un coût. Conséquence : une carte « si elle est défaussée par un effet de carte » se déclenche si la défausse est un effet (cas de `Branded Opening`), pas si c'est un coût. |
| R22 | **faux** | « Le joueur choisit l'ordre » : juste. « Il peut aussi n'en activer qu'un » : jugé faux (« il peut activer les deux »). **Probable malentendu** : la lecture dit qu'il *peut* n'en activer qu'un, pas qu'il *ne peut* en activer qu'un. Sa propre réponse à R23 (sans « You can », l'effet est obligatoire) implique qu'avec « You can » il est facultatif, donc qu'on peut n'en activer qu'un : **tenu pour résolu par cohérence**, sans confirmation explicite (relecteur plus disponible). Il ajoute que l'ordre de la chaîne sert à jouer autour d'`Ash Blossom` : un effet qui ne répond qu'« à l'activation » ne peut viser que le dernier maillon, donc mettre l'effet de recherche en maillon 1 et l'autre en maillon 2 le protège. |
| R23 | d'accord | Le deux-points signifie que l'effet est **déclaré** (activé, il ouvre une chaîne) même sans « You can » ; sans deux-points, on prendrait simplement la carte. Effet obligatoire et activé. |
| R27 | d'accord | Le regroupement de `Mercourier` et `The Golden Swordsoul` dans la même question l'a gêné : `Mercourier` se déclenche quand **lui** est banni, `Golden Swordsoul` quand **un autre** monstre est banni, alors qu'il est sur le terrain ou au Cimetière (texte vérifié en base). `Cocatorium` a été joué à un exemplaire dans des listes Branded d'un format où l'on bannissait beaucoup. |
| R34 | ça dépend | (a) et (c) : justes. (b) : **la cible se choisit à l'activation** ; tout ce qui précède le point-virgule (coût, ciblage) se fait à l'activation. |
| R30 | d'accord | Légal, mais rarement utile (`Fuwalos` à son tour peut servir ; s'annuler avec son propre `Ash`, presque jamais). |
| R03 | d'accord | Ajout : la limite de 3 exemplaires par nom vaut **pour les deux cartes ensemble** (`Fallen of Albaz` et `Fallen of the White Dragon` « ont le même nom ») : d'où 1 + 2 dans la liste. À intégrer à tout contrôle de validité d'un deck. |
| R04 | d'accord | — |
| R05 | d'accord | — |
| R11 | d'accord | « 100 % raison ». Ajout : des cartes désignent aussi une famille par type et attribut (« Magicien LUMIÈRE dont l'ATK égale la DEF »), indépendamment du nom. |
| R32 | d'accord | — |
| R06 | d'accord | Question qu'il ne saurait pas trancher : `Fallen of Albaz` et `Fallen of the White Dragon` utilisés **ensemble** comme matériels quand le texte exige des noms différents. Selon lui, un ruling officiel existe sans doute en ligne. |
| R20 | d'accord | — |
| R24 | d'accord | Surpris que la première partie soit posée. |
| R25 | d'accord | — |
| R26 | d'accord | `Despian Luluwalilith` (Synchro 12) est dans la liste pour être envoyée au Cimetière depuis l'Extra Deck, ou invoquée plus tard dans la partie, sans le verrou (partie longue, miroir) : rarement sur le terrain au tour 1. |
| R12 | d'accord | — |
| R13 | d'accord | — |
| R21 | d'accord | — |
| R29 | d'accord | Après explication : « tour 5 du duel » = son 3e tour à lui. La formulation l'a d'abord dérouté ; écrire « 3e tour du joueur (tour 5 du duel) ». |
| R02 | d'accord | « Mal formulé, mais juste. » |
| R15 | d'accord | Le deux-points fait bien la différence. |
| R16 | d'accord | — |
| R18 | d'accord | — |
| R19 | d'accord | — |
| R28 | d'accord | « On pourrait même dire *il doit*. » |
| R31 | d'accord | La règle « pas de pioche au tour 1 » n'a pas toujours existé. |
| R33 | d'accord | — |

## Questions ouvertes

1. **Une fois par tour consommé dès l'activation ?** Oui. Mais selon la formulation, une **autre copie** de la carte
   peut rester utilisable. Le moteur doit distinguer au moins « You can only activate 1 [nom] per turn » (par nom),
   « You can only use this effect of [nom] once per turn » (par effet et par nom) et « Once per turn » (par copie).
2. **Ordre du Cimetière.** Il compte, mais pour que l'arbitre puisse retracer la partie ; aucune carte connue de lui
   ne lit cet ordre. Le moteur peut traiter le Cimetière comme un ensemble ; garder l'historique des actions suffit
   à retracer.
3. **Colonnes « n'importe où » ?** **Non, c'est faux.** Il faut jouer autour des cartes adverses qui parlent de
   colonnes ; les monstres Lien pointent des zones précises ; la **Zone Monstre Extra** est très importante.
   → **L'hypothèse de D3 est infirmée** (voir conséquences).
4. **Fusion en Zone Extra ou Principale, au choix ?** Oui quand le monstre est invoqué depuis l'Extra Deck.
   **Non s'il est réinvoqué depuis le Cimetière** : il ne peut pas aller en Zone Monstre Extra. Le placement en Zone
   Extra peut compter pour les colonnes.

**Ligne d'ouverture** : pas de réponse (« ce n'est pas un joueur Branded »). Début esquissé pendant l'entretien :
Invocation Normale d'`Aluber`, effet, ajout de `Branded Fusion` ; il s'est arrêté là. Il juge Branded « pas vraiment
un deck combo ».

**Liste du deck** : il relève l'absence de `Lubellion the Searing Dragon`, qu'il juge « ultra importante » (vérifié :
absente de cette liste, jouée par 102 des 123 listes Branded TCG de juin à novembre 2026). Il estime aussi que le
régional d'où vient la liste avait peu de joueurs ; la base ne stocke ni le lieu ni l'effectif du tournoi, ce point
n'est pas vérifiable ici. → D1 réexaminée, maintenue par Thomas le 18/11.

## Conséquences pour les tests et les décisions

| Objet | Changement |
|---|---|
| `tests-branded.yaml` | Aucun verdict modifié. T45 : objection R22 levée par cohérence (choix inchangés) ; T37 et T65 annotés (effet déclaré, cible à l'activation). |
| `points-de-regle-a-valider.md` | Colonne « Relecture 1 » ajoutée : 32 confirmés par un joueur de tournoi, R22 contesté, R34 complété. |
| **D3 (zones)** | **Hypothèse infirmée.** Le placement « première zone libre » ne suffit pas : la Zone Monstre Extra et les colonnes comptent, y compris par les cartes de l'adversaire. Révisée par Thomas le 18/11 : « entre-deux » (Zone Extra / principale essayées à chaque sortie de l'Extra Deck, case exacte toujours gardée). |
| **D1 (deck)** | Liste sans `Lubellion`, carte jouée dans 83 % des listes. **Maintenue par Thomas le 18/11** (un seul deck), risque sur le jalon J2 noté. |
| D4 (actions sans intérêt) | Confirmée sur le fond (« légal mais ça ne sert à rien ») ; le relecteur insiste sur les **boucles** possibles avec Branded (jouer 25 minutes sans rien construire). Les filtres déclarés et une détection des boucles deviennent nécessaires, pas optionnels. |
| Arrêt de l'exploration | Le relecteur recommande de donner une **cible** au moteur (le plateau final visé) plutôt que d'énumérer tous les plateaux. À verser dans les critères d'arrêt (TOK-85). |

## Ce qui reste à faire confirmer

Le relecteur n'est plus disponible (entretien terminé le 17/11). Tous les renvois « voir le transcript » du formulaire
(R03, R34, questions 2 à 4) sont intégrés ci-dessus.
- **R22** : tenu pour résolu par cohérence avec R23 (voir le tableau), pas confirmé explicitement.
- **R08, R27 (b), R34** étaient à « confiance basse » : le dossier prévoyait deux avis, ils n'en ont qu'un. À soumettre
  au prochain relecteur s'il y en a un ; sinon, l'oracle (TOK-86) les tranchera.
- La question des deux `Albaz` comme matériels « de noms différents » (soulevée par lui) : chercher le ruling
  officiel TCG.


## Pistes hors règles relevées pendant l'entretien (hypothèses, non vérifiées)

À traiter avec le data scientist, selon le principe de rigueur du projet (estimer, valider dans le temps, comparer
à une méthode naïve) :

- **Comportement de Konami sur les banlists** : éviter de bannir les cartes d'un archétype dont des produits vont
  sortir ; bannir ce qui affaiblirait un archétype bientôt soutenu ; libérer ce qui le renforce ; affaiblir le
  deck dominant avant une extension pour laisser une chance aux nouvelles stratégies ; bannir rarement les
  « floodgates ». Hypothèse testable avec un calendrier des sorties de produits. Il cite aussi une **banlist
  d'urgence récente d'environ 35 cartes, « jamais vue »** : à rapprocher des deux listes TCG récentes où le Ban
  Radar est mauvais (2026-09-21 et 2026-10-19).
- **Lecture du graphique OCG → TCG de l'accueil** : en voyant les courbes superposées, il a d'abord cru à une erreur,
  avant que Thomas lui explique le décalage de 3 mois. Indice que l'annotation du décalage n'est pas assez visible
  (accueil, TOK-106).
- **Catégories de fonction des cartes** : pièce de combo, pièce de plateau final, *hand trap*, *floodgate*,
  *board breaker*. Piste de classification.
- **Format de tournoi** : main deck de 40 à 60 cartes, Extra Deck de 15, side deck de 15 en BO3 (le deck garde sa
  taille après échange). Au premier match on vise un plateau polyvalent ; aux suivants, un plateau adapté à
  l'adversaire.
- **Analyse des matchs filmés** : la main des joueurs n'est pas visible, ce qui limite la reconstitution des combos
  à partir de vidéos.
- **Règles OCG et TCG** : les rulings diffèrent entre les deux formats ; la référence pour le moteur est le livret
  officiel et les rulings **TCG**.
- **Sources de decklists** : il conseille les résultats de tournois de YGOPRODeck (le projet tire ses decks de
  yugiohmeta.com ; YGOPRODeck sert aux données de cartes). À regarder lors d'un futur choix de source.
