# Moteur de combos — dossier pour le juge (TOK-89)

> Ce document se suffit à lui-même : il peut être envoyé tel quel à la personne qui accepte de relire.
> Le questionnaire ci-dessous est généré depuis `points-de-regle-a-valider.md` (34 questions).

## Pour Thomas : comment trouver et utiliser un juge

**Qui convient.** Par ordre de préférence :

1. un **arbitre** (juge certifié Konami) : il tranche tout, y compris les questions marquées « confiance basse » ;
2. un **joueur de tournoi régulier** (régionaux, YCS) : il tranche la plupart des questions et sait dire « là, je ne suis pas sûr » ;
3. un joueur occasionnel ou de Master Duel : utile pour une première passe, **pas suffisant seul**
   (Master Duel applique les règles automatiquement, on y apprend peu les cas limites).

Un joueur de Branded est un plus, pas une condition : les questions portent sur les règles générales.

**Où chercher.** L'ami testeur prévu un samedi, s'il joue en tournoi. Sinon : la boutique de jeux la
plus proche (les arbitres de tournois locaux s'y trouvent), ou un serveur Discord de joueurs
francophones. Je ne peux contacter personne à votre place : les deux messages ci-dessous sont prêts à copier.

**Ce que ça lui coûte.** 34 questions fermées, avec ma réponse déjà écrite. Estimation non mesurée :
une à deux heures. Les 12 premières sont celles où je doute le plus : si le temps manque, celles-là suffisent
pour débloquer la suite.

**Ce que je fais des réponses.** Vous me collez ses réponses (texte, photo, message vocal retranscrit,
peu importe la forme). Je corrige les tests concernés, je note son nom ou pseudo et la date sur chaque
point, et je vous dis combien de mes lectures étaient fausses : c'est la première mesure réelle du
taux d'erreur du projet.

**Deux juges valent mieux qu'un** pour les questions à confiance basse (R08, R27, R34) : si deux
joueurs se contredisent, la question part chez un arbitre.

### Message pour un ami

```
Salut ! Je monte un projet autour de Yu-Gi-Oh : un programme qui calcule les combos possibles d'un
deck à partir des textes des cartes. Je ne joue pas, donc j'ai besoin de quelqu'un qui connaît les
règles pour vérifier 34 points précis (sur un deck Branded). Chaque point est une question fermée
avec la réponse que le programme suppose : tu dis « d'accord », « faux » ou « ça dépend ».
Ça prend une à deux heures, à ton rythme. Tu serais partant ? Je t'envoie le document.
```

### Message pour une boutique, un arbitre ou un serveur Discord

```
Bonjour, je développe un outil d'analyse de combos Yu-Gi-Oh (projet personnel, non commercial pour
l'instant). Je cherche un arbitre ou un joueur de tournoi pour valider 34 points de règle sur un
deck Branded : des questions fermées, chacune avec la lecture que j'en fais, à confirmer ou corriger.
Une à deux heures de relecture. Je peux citer la personne dans le projet si elle le souhaite.
Quelqu'un serait-il intéressé, ou pourrait-il m'orienter ?
```

---

## Pour le juge

Merci de prendre ce temps.

**Le contexte en trois lignes.** Un programme doit décider si une action est légale à partir du texte
officiel des cartes (anglais, TCG) et des règles du jeu papier. Avant de l'écrire, on a rédigé des
tests à la main. Ils reposent sur les 34 lectures ci-dessous, faites par une IA : **certaines sont
sûrement fausses**, et c'est ce qu'on vous demande de repérer.

**Comment répondre.** Pour chaque question : cochez une case, et ajoutez une ligne si ce n'est pas
« d'accord ». « Je ne sais pas » est une réponse utile. Si vous connaissez un ruling officiel ou une
source, citez-la. Le deck est un Branded de régional (novembre 2026, liste TCG d'octobre 2026) ;
toutes les situations sont au **tour 1 du joueur qui commence**, sauf mention contraire.

## Partie 1 — les 12 questions prioritaires

Ce sont celles où la lecture est la moins sûre.

### R01

**Question.** Peut-on activer un effet qui ne pourra rien faire à la résolution (aucune carte à chercher dans le Deck, aucune Fusion possible, aucune carte à défausser) ?

**Lecture supposée.** Non. L'activation est illégale. Doute : le Deck est une zone privée, et la règle exacte pour « chercher alors qu'il n'y a rien » peut différer.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R07

**Question.** `Branded Fusion` : « you cannot Special Summon from the Extra Deck, except Fusion Monsters, **the turn you activate this card** ». Si j'ai déjà fait une Invocation Synchro ce tour, puis-je l'activer ? Et `Branded Opening` (« for the rest of this turn **after this card resolves** ») ?

**Lecture supposée.** `Branded Fusion` : non (la restriction vaut pour tout le tour, passé compris). `Branded Opening` : oui.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R08

**Question.** Si l'effet d'une carte « You can only activate 1 per turn » est annulé (par `Ash Blossom`), la limite est-elle consommée et le verrou s'applique-t-il ?

**Lecture supposée.** Oui aux deux : l'effet est annulé, pas l'activation. Si c'est l'**activation** qui est annulée, la carte ne compte pas comme activée.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R09

**Question.** Un monstre Fusion envoyé au Cimetière directement depuis l'Extra Deck (par `Nadir Servant`) peut-il être ciblé par `Guiding Quem` pour être Invoqué Spécialement ?

**Lecture supposée.** Non : il n'a jamais été correctement invoqué. Le même monstre, invoqué par Fusion puis envoyé au Cimetière, peut revenir.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R10

**Question.** Un effet « If … : You can » dont la condition se réalise **pendant** la résolution d'un autre effet, ou pendant le paiement d'un coût, peut-il être activé ensuite ?

**Lecture supposée.** Oui, dans une nouvelle chaîne, après la chaîne en cours. Seuls les effets « When … you can » ratent leur moment.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R14

**Question.** Un effet dont le seul résultat possible est interdit par un verrou (Fusion depuis l'Extra Deck sous `Nadir Servant`) peut-il être activé ?

**Lecture supposée.** Non.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R17

**Question.** `Branded Opening` : « Discard 1 card, then take… » sans point-virgule. La défausse est-elle un coût ? Et faut-il une carte à défausser pour activer ? Même question pour « Reveal… and send… » de `Branded in High Spirits`.

**Lecture supposée.** Ce sont des effets, pas des coûts (ils se font à la résolution). Il faut quand même pouvoir les faire pour activer.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R22

**Question.** Deux effets facultatifs du même joueur se déclenchent en même temps (`Granguignol` invoqué par Fusion, `Tri-Brigade Springans Kitt` envoyée au Cimetière). Qui choisit l'ordre dans la chaîne ?

**Lecture supposée.** Le joueur, librement. Il peut aussi n'en activer qu'un.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R23

**Question.** `Incredible Ecclesia` : « During the End Phase, if a Fusion Monster(s) was sent to your GY this turn: Add this card from the GY to your hand » (sans « You can »). Obligatoire ? Et dans quel ordre résout-on plusieurs effets de Phase de Fin ?

**Lecture supposée.** Obligatoire. Le joueur du tour active ses effets de Phase de Fin un par un, dans l'ordre qu'il veut, chacun dans sa chaîne.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R27

**Question.** `Cocatorium` bannit `Tri-Brigade Mercourier` du Deck (coût) et prend son nom. (a) Compte-t-il comme monstre « Tri-Brigade » pour `Tri-Brigade Springans Kitt` ? (b) Le bannissement en coût depuis le Deck est-il « face visible », et déclenche-t-il `Mercourier` et `The Golden Swordsoul` ?

**Lecture supposée.** (a) oui ; (b) oui aux deux.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R34

**Question.** `The Fallen & The Virtuous` : « Send 1 monster… from your Extra Deck to the GY, **then target** 1 face-up card on the field; destroy it ». (a) La carte peut-elle se cibler elle-même ? (b) La cible se choisit-elle à l'activation ou à la résolution ? (c) Sans aucune carte face visible sur le terrain, peut-on l'activer ?

**Lecture supposée.** (a) non ; (b) je ne sais pas : la formulation « then target » est inhabituelle ; (c) non.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R30

**Question.** Est-il légal d'activer `Mulcharmy Fuwalos` pendant son propre tour, ou d'enchaîner son propre `Ash Blossom` à son propre effet ?

**Lecture supposée.** Oui : rien dans les textes ne l'interdit.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

## Partie 2 — les 22 autres

### R03

**Question.** `Fallen of the White Dragon` (« always treated as "Fallen of Albaz" ») compte-t-il comme « Fallen of Albaz » partout : matériel pris dans le Deck par `Branded Fusion`, carte cherchée par `Nadir Servant`, condition de `Blazing Cartesia` ?

**Lecture supposée.** Oui, dans toutes les zones.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R04

**Question.** « A card / monster that mentions "Fallen of Albaz" » : est-ce toute carte dont le texte contient ce nom entre guillemets ? `Ecclesia and the Dark Dragon` et `The Three Champions of Swordsoul` (Synchro) comptent-ils ? Les Magies comptent-elles quand le texte dit « card » ?

**Lecture supposée.** Oui aux trois.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R05

**Question.** « A Fusion Monster that mentions "Fallen of Albaz" **as material** » : faut-il que le nom soit dans la ligne de matériels ?

**Lecture supposée.** Oui. `Granguignol` (matériels : `Blazing Cartesia` + 1 LIGHT ou DARK) ne compte pas ; `Titaniklad`, `Rindbrumm`, `Mirrorjade`, `Albion the Sanctifire Dragon`, `Sprind`, `The Dragon that Devours the Dogma` comptent.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R11

**Question.** Appartenance à un archétype : par le nom ou par « always treated as ». `Guiding Quem` est-il « Dogmatika » et « Despia » ? `Fallen of Albaz` est-il « Dogmatika » ? `Incredible Ecclesia` et `Dogmatika Ecclesia` sont-ils des monstres « Ecclesia » ?

**Lecture supposée.** `Quem` : les deux. `Fallen of Albaz` : **non**. Les deux Ecclesia : oui. `Blazing Cartesia` : ni « Dogmatika » ni « Ecclesia ». `The Fallen & The Virtuous` (« always treated as a "Branded" and "Dogmatika" card ») : cherchable par `Aluber` et par `Dogmatika Ecclesia`.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R32

**Question.** `Springans Kitt` : « If you have a Fusion Monster that mentions "Fallen of Albaz" as material on your field or in your GY ». Un monstre Fusion envoyé au Cimetière sans avoir été invoqué suffit-il ?

**Lecture supposée.** Oui : la condition ne demande que sa présence.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R06

**Question.** `Branded Fusion` (« using 2 monsters ») peut-il invoquer `The Dragon that Devours the Dogma` (3 matériels) ?

**Lecture supposée.** Non.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R20

**Question.** `Garura` : « 2 monsters with the same Type and Attribute, but different names ». `Blazing Cartesia` + `Guiding Quem` conviennent-ils ?

**Lecture supposée.** Oui (LIGHT Spellcaster tous les deux).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R24

**Question.** Un monstre peut-il remplir deux lignes de matériel d'une même Fusion ? `Albion the Sanctifire Dragon` peut-il servir de matériel ?

**Lecture supposée.** Non et non (« Cannot be used as Fusion Material »).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R25

**Question.** `Sprind` : « 1 Effect Monster Special Summoned this turn ». Un monstre Invoqué Normalement ce tour convient-il ?

**Lecture supposée.** Non.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R26

**Question.** Synchro : `Ecclesia and the Dark Dragon` (« 1 Tuner + 1+ non-Tuners », Niveau 8) avec deux Syntoniseurs de Niveau 4 ? Verrou de `Fallen of the White Dragon` (« except Level 8 Fusion or Synchro Monsters ») : `Despian Luluwalilith` (Niveau 12) est-elle interdite ?

**Lecture supposée.** Deux Syntoniseurs : illégal. `Luluwalilith` : interdite sous ce verrou.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R12

**Question.** `Nadir Servant` : « ATK less than or equal to that sent monster in the GY ». On compare à l'ATK imprimée du monstre envoyé ?

**Lecture supposée.** Oui (au Cimetière, pas de modification).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R13

**Question.** Un verrou « cannot Special Summon from the Extra Deck » empêche-t-il d'invoquer depuis le Deck ou le Cimetière ?

**Lecture supposée.** Non.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R21

**Question.** `Branded in High Spirits` : « Level 8 Fusion Monster … with the same Type that has 2500 ATK or DEF ». `The Dragon that Devours the Dogma` (3000/2500) convient-il par sa DEF ? Et la limite « 1 effect per turn » interdit-elle de reprendre la carte en Phase de Fin après l'avoir activée ?

**Lecture supposée.** Oui et oui.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R29

**Question.** `Gold Sarcophagus` activée à notre tour 1 : « your second Standby Phase after this card's activation » est-elle celle de notre tour 5 ?

**Lecture supposée.** Oui (tour 3 = première, tour 5 = seconde).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R02

**Question.** Toute recherche dans le Deck est-elle suivie d'un mélange ? Une carte posée au-dessous du Deck (`Springans Kitt`) y reste-t-elle jusqu'au mélange suivant ?

**Lecture supposée.** Oui et oui.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R15

**Question.** `Incredible Ecclesia` (« you can Special Summon this card (from your hand) ») : invocation sans chaîne. `Blazing Cartesia` (« If you control … : You can Special Summon this card from your hand ») : effet activé, avec chaîne. Exact ?

**Lecture supposée.** Oui (la présence de « : » fait la différence).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R16

**Question.** « If your opponent controls more monsters than you do » avec 0 contre 0 ?

**Lecture supposée.** Faux : pas d'invocation.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R18

**Question.** Une Magie Jeu-Rapide peut-elle être activée depuis la main pendant son propre tour, en réponse à son propre effet ? Et le tour où elle a été posée face cachée ?

**Lecture supposée.** Depuis la main : oui. Posée ce tour : non.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R19

**Question.** `Super Polymerization` : puis-je enchaîner ma propre carte à son activation ?

**Lecture supposée.** Non (« Neither player »).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R28

**Question.** `Mirrorjade` : « banish 1 monster on the field ». Peut-elle bannir un monstre de son propre contrôleur ? L'effet cible-t-il ?

**Lecture supposée.** Oui ; il ne cible pas (pas de « target »).

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R31

**Question.** Le joueur qui commence ne pioche pas et n'a pas de Phase de Combat au tour 1 ?

**Lecture supposée.** Oui.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

### R33

**Question.** `Tri-Brigade Springans Kitt` (« Special Summon 1 of the following monsters from your GY ») : l'effet cible-t-il ? Faut-il un monstre éligible au Cimetière pour l'activer ?

**Lecture supposée.** Il ne cible pas ; il faut au moins un monstre éligible à l'activation.

```
[ ] d'accord   [ ] faux   [ ] ça dépend   [ ] je ne sais pas
Commentaire ou source :
```

## Partie 3 — quatre questions ouvertes

Elles ne portent pas sur une carte, mais sur la façon de représenter le jeu.

1. Un effet « une fois par tour » est-il consommé dès l'**activation**, même si l'effet est ensuite annulé ?
2. L'**ordre des cartes dans le Cimetière** compte-t-il pour une carte jouée en TCG aujourd'hui ?
3. La **colonne** où se trouve un monstre ne compte-t-elle que pour les cartes qui en parlent
   (`Sprind the Irondash Dragon`, `Albion the Sanctifire Dragon`) ? Peut-on placer tous les autres
   monstres « n'importe où » sans jamais perdre un combo ?
4. Un monstre Fusion peut-il toujours être placé, au choix, en Zone Monstre Extra ou en Zone Monstre Principale ?

```
1.
2.
3.
4.
```

## Et ensuite

Si vous avez encore un peu de temps : quelle est, selon vous, la ligne d'ouverture la plus courante de
ce deck (4 à 8 cartes jouées, dans l'ordre) ? Le programme devra la retrouver seul.

```
Ligne d'ouverture :
```
