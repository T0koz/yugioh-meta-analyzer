# Moteur de combos — jeu de tests Branded écrit à la main (TOK-87)

> **Statut : version 2, non validée.** Écrit le 16 novembre 2026, avant tout code de moteur.
> La version 2 intègre les textes de quatre cartes chargées en base le même jour (décision D8).
> **Chaque situation est « à valider par un juge humain (TOK-89) »** : son auteur (Claude) n'est pas
> un juge, Thomas ne joue pas, et aucun simulateur n'a été consulté (condition d'indépendance).
> Un test non validé peut être faux : il sert à poser les questions, pas encore à trancher.

Fichiers :

- [`tests-branded.yaml`](tests-branded.yaml) : les 72 situations, lisibles par un programme ;
- [`deck-branded-source.json`](deck-branded-source.json) : la decklist extraite de la base
  (`scripts/combos_extract_deck.py`, lecture seule) ;
- [`points-de-regle-a-valider.md`](points-de-regle-a-valider.md) : les 34 points de règle à soumettre au juge.

---

## 1. Le deck source

| | |
|---|---|
| Identifiant | `6af240d29e8b7a3a8eb28d8d` (table `tournament_decks`) |
| Joueur | Džavid Berberović |
| Tournoi | Yu-Gi-Oh! WCQ Regional, **8 novembre 2026** |
| Placement | **3,5** dans la base, c'est-à-dire demi-finaliste (top 4) |
| Format | TCG, **légal** selon `deck_legality` (liste « October 2026 Lists (TCG) », 0 infraction) |
| Distance au changement de liste | 20 jours (hors de la fenêtre ambiguë de 14 jours) |
| Taille | 40 cartes Main Deck, 15 Extra Deck, 15 Side Deck |

### Pourquoi celui-ci

Critères, dans l'ordre : légal à la date du tournoi sous la **liste en vigueur aujourd'hui**, hors
fenêtre ambiguë, le plus récent, le mieux placé, 40 cartes exactement.

- Seuls **9 decks Branded TCG légaux** existent sous la liste d'octobre 2026. Parmi eux, 4 datent du
  8 novembre ; les deux mieux placés (3,5) sont celui-ci et un deck de 41 cartes.
- **40 cartes** : moins d'états à explorer, et aucune carte « technique » isolée.
- **Représentatif** : 18 de ses cartes sont jouées par 9 decks sur 9, et 27 par au moins 7 sur 9.
- Écarté : le deck classé 2e le 24 octobre (41 cartes, à 5 jours du changement de liste, donc dans la
  fenêtre où la légalité est incertaine). Écartés aussi les vainqueurs de septembre, joués sous une
  liste qui n'est plus en vigueur.

**Limite du choix** : un seul deck. Trois cartes fréquentes chez les autres n'y sont pas
(`Lubellion the Searing Dragon` 7/9, `Despian Quaeritis` 5/9, `Albion the Shrouded Dragon` 4/9).
Le jalon J1 (« 100 % des cartes du pilote ») devra les ajouter.

### Contenu

**Main Deck (40)** : Aluber the Jester of Despia ×3 · Ash Blossom & Joyous Spring ×3 · Blazing
Cartesia, the Virtuous ×2 · Branded Fusion ×1 · Branded Opening ×1 · Branded in High Spirits ×1 ·
Cocatorium the Heavy Metal Avian ×1 · Dogmatika Ecclesia, the Virtuous ×1 · Droll & Lock Bird ×1 ·
Fallen of Albaz ×1 · Fallen of the White Dragon ×2 · Ghost Ogre & Snow Rabbit ×3 · Gold Sarcophagus ×1
· Guiding Quem, the Virtuous ×1 · Incredible Ecclesia, the Virtuous ×2 · Mulcharmy Fuwalos ×3 · Nadir
Servant ×3 · Springans Kitt ×1 · Super Polymerization ×3 · The Fallen & The Virtuous ×3 · The
Golden Swordsoul ×1 · Tri-Brigade Mercourier ×1 · Tri-Brigade Springans Kitt ×1.

**Extra Deck (15)** : Albion the Sanctifire Dragon · Despian Luluwalilith · Ecclesia and the Dark
Dragon · Garura, Wings of Resonant Life · Granguignol the Dusk Dragon · Hyperinvoked Aeon ·
Mirrorjade the Iceblade Dragon · Mixousia the Confounder · Predaplant Dragostapelia · Rindbrumm
the Striking Dragon · Sprind the Irondash Dragon · The Dragon that Devours the Dogma ×2 · The Three
Champions of Swordsoul · Titaniklad the Ash Dragon.

### Quatre cartes manquaient dans la base (corrigé le 16 novembre 2026)

À la première extraction, quatre cartes du deck (6 exemplaires sur 55) n'avaient pas de texte :

| Carte | Cause | Correction |
|---|---|---|
| `The Fallen & The Virtuous` (×3) | présente dans `cards`, mais sous le nom `The Fallen &amp; The Virtuous` (entité HTML) : la jointure par nom échouait | nom corrigé en base |
| `Hyperinvoked Aeon`, `Mixousia the Confounder`, `The Three Champions of Swordsoul` | sorties le 2 juillet 2026, jamais chargées (`cards.json` datait de juin) | insérées avec 285 autres cartes nouvelles |

`scripts/fetch_cards.py` a été relancé, puis **seules les cartes absentes ont été insérées** (288
lignes, `cards` passe de 13 797 à 14 085). Les cartes déjà en base n'ont pas été réécrites, pour ne
pas changer `views_week` ni les statuts de banlist hors de la chaîne du lundi.

Ce que les textes ont changé dans les tests (14 situations retouchées) :

- `The Fallen & The Virtuous` est « always treated as a "Branded" and "Dogmatika" card » : `Aluber`
  et `Springans Kitt` peuvent la chercher (T01, T49), `Dogmatika Ecclesia` aussi (T50), et `Guiding
  Quem` peut l'envoyer au Cimetière (T23). **T02 était faux en v1** : avec trois exemplaires dans le
  Deck, `Aluber` avait bien une carte à chercher. Le test a été réécrit.
- `The Three Champions of Swordsoul` cite « Fallen of Albaz » : elle peut payer le coût de `Fallen of
  the White Dragon` (T29).
- Les trois cartes de l'Extra Deck sont de Niveau 8 ou 10, LUMIÈRE ou TÉNÈBRES : `Granguignol` peut
  les envoyer au Cimetière (T53).

**Anomalie de la source** : le texte de `The Three Champions of Swordsoul` se termine par « You can
only use each effect of "The Three Brave Swordsouls" once per turn » : le nom ne correspond pas à
celui de la carte. C'est une incohérence de la source (cause non vérifiée), à faire trancher
lors de la formalisation, et un argument pour garder l'empreinte du texte (`text_sha256`).

---

## 2. Format d'une situation

```yaml
- id: T18
  mecanique: recherche_sous_condition_de_valeur   # une mécanique par test
  perimetre: pilote                               # ou hors_pilote (adversaire, tours suivants)
  depart: {main: [NADIR, ASH, ASH, OGRE, DROLL]}  # zones non vides seulement
  action: "Activer NADIR en envoyant TITAN…"
  attendu:
    verdict: legal                                # legal | illegal | non_couvert
    choix: [ALBAZ, WHITE, DECCLESIA, QUEM]        # liste EXACTE des options légales
    exclus: [CARTESIA, IECCLESIA, GSWORD, ALUBER] # pièges qui ne doivent pas y figurer
    etat: "…"                                     # ce que l'état d'arrivée doit contenir
  source: "Textes de NADIR, QUEM, WHITE."
  regles: [R03, R11, R12]                         # points de règle à faire valider
  confiance: moyenne                              # celle de l'auteur, pas une validation
```

Conventions :

- **État de départ par défaut** : tour 1, nous commençons, Phase Principale 1, pas de pioche, terrain
  adverse vide, Extra Deck complet, deck = les 40 cartes moins celles placées ailleurs, mémoire du
  tour vide. Seul ce qui s'en écarte est écrit.
- **Deux sortes de départ** : une main de 5 cartes (situation d’ouverture, 26 cas), ou un état en
  cours de tour décrit directement (46 cas). Ces derniers isolent une mécanique sans dépendre d'une
  longue séquence ; certains ne sont pas atteignables depuis une ouverture, ce qui n'enlève rien à la
  question de légalité qu'ils posent.
- **Alias** : les noms complets des cartes sont dans la section `cartes` du fichier.
- `choix` est une liste **exacte** : le moteur doit rendre ces options, toutes, et aucune autre
  (sauf cartes signalées dans `incomplet`). C'est ce qui rend le test exigeant.
- Le champ `etat` est en texte libre dans cette version. Il sera traduit en forme canonique
  (definitions-et-schema.md § 2.3) quand le schéma sera validé.

---

## 3. Répartition

72 situations : **35 légales, 36 illégales, 1 « non couvert »** (plus T67, exploration marquée
incomplète). 70 dans le périmètre du pilote, 2 hors pilote (places réservées). Confiance de
l'auteur : 24 haute, 45 moyenne, 3 basse.

| Bloc | Situations | Mécaniques |
|---|---|---|
| A. Règles de base du tour | T01 à T06 | Invocation Normale, « une fois par tour » par nom, activation sans résolution possible, premier tour |
| B. Branded Fusion | T07 à T15 | Fusion depuis le Deck, matériels exacts, verrou rétroactif ou non, une activation par tour, déclencheur au Cimetière |
| C. Fin de tour, Nadir Servant, Guiding Quem | T16 à T24 | Phase de Fin, verrou et sa portée, hasard (pioche), monstre de l'Extra Deck non invoqué, prédicat « mentionne » |
| D. Invocations Spéciales depuis la main | T25 à T33 | conditions de présence et de comparaison, coûts, prédicats de nom, nom temporaire, déclencheur pendant un coût |
| E. Coût ou effet, Magies Jeu-Rapide | T34 à T50 | ponctuation « ; », carte posée, chaîne interdite, effet obligatoire, Synchro, ordre du deck, déclencheurs simultanés |
| F. Matériels de Fusion | T51 à T58 | niveau, nombre de matériels, « ne peut pas servir de matériel », mémoire d'invocation |
| G. Chaînes | T59 à T64 | enchaîner, vitesses, effet sur son propre terrain, effet différé |
| H. Cartes ajoutées en v2, « non couvert » | T65 à T68 | cible obligatoire, matériels d'`Hyperinvoked Aeon`, carte non formalisée, exploration incomplète |
| I. Recenser sans juger | T69 à T70 | actions légales sans intérêt |
| J. Hors pilote | T71 à T72 | matériel adverse, interruption adverse |

### Paires à lire ensemble

Plusieurs tests vont par deux : le même plateau, une différence, un verdict opposé. Ce sont eux qui
montrent que le moteur a compris la règle et pas seulement un cas.

| Paire | Ce qui change | Ce que ça teste |
|---|---|---|
| T12 / T13 | `Branded Fusion` ou `Branded Opening` après une Synchro | verrou « du tour entier » contre verrou « après résolution » |
| T22 / T52 | monstre Fusion envoyé ou invoqué puis envoyé | drapeau « correctement invoqué » |
| T31 / T36 | Synchro de Niveau 12 ou 8 sous le verrou de `Fallen of the White Dragon` | verrou avec exception |
| T34 / T38 | défausse de `Branded Opening` ou de `Super Polymerization` | effet ou coût (même verdict, raisons différentes) |
| T47 / T48 | `Titaniklad` ou `Granguignol` au Cimetière | « mentionne Albaz **comme matériel** » |
| T54 / T55 | 2 ou 3 matériels pour `The Dragon that Devours the Dogma` | une ligne de matériel par monstre |
| T57 / T58 | `Aluber` invoqué normalement ou `Cartesia` invoquée spécialement | mémoire d'invocation |
| T05 / T71 | `Fallen of Albaz` sans ou avec monstre adverse | terrain adverse (hors pilote) |

---

## 4. Ce que ce jeu de tests ne couvre pas

- **Aucun combo complet de bout en bout.** Les tests portent sur des étapes (1 à 3 actions). Je n'ai
  pas écrit « la » ligne Branded de référence : je ne joue pas, et une ligne inventée par moi ne
  prouverait rien. Les 5 à 10 combos des guides publics (jalon J2) restent à collecter, et c'est la
  tranche 0 (TOK-90) qui en écrira un premier.
- **Les quatre cartes ajoutées en v2 sont peu testées** : `The Fallen & The Virtuous` (T01, T23, T49,
  T50, T65), `Hyperinvoked Aeon` (T66), `The Three Champions of Swordsoul` (T29), `Mixousia the
  Confounder` (aucun test propre : son effet de Fusion ne s'active qu'au tour adverse).
- **Le cas « texte absent de la source »** n'a plus d'exemple réel dans ce deck. Il reste à tester
  avec un nom de carte fictif.
- **L'état d'arrivée n'est pas formalisé** (texte libre), en attendant la validation du schéma.
- **Les zones** (colonnes de `Sprind`, zones centrales d'`Albion the Sanctifire Dragon`) : aucun
  test, en attendant la décision D3.
- **« When … you can »** (un effet facultatif qui « rate son moment ») : aucune carte du deck n'y est
  exposée pendant notre propre tour 1. À couvrir avec l'adversaire.
- **Le Side Deck** (15 cartes) : hors périmètre, sauf `Lava Golem` utilisée comme carte non formalisée (T68).
- **La borne d'erreur** des décisions (« environ 60 cas indépendants par strate ») : 72 cas ne font
  pas 60 cas *par strate*, et ces cas ne sont pas indépendants (un même point de règle en porte
  plusieurs). Ce jeu sert à construire et à déboguer, pas à chiffrer un taux d'erreur.

## 5. Comment le faire valider

1. Le juge lit `points-de-regle-a-valider.md` : 34 questions fermées, chacune avec ma lecture.
   C'est plus court que 72 tests, et une réponse corrige tous les tests qui en dépendent.
2. Pour chaque point : « d'accord », « faux, parce que… », ou « ça dépend de… ».
3. Je corrige le YAML et je passe `confiance` à `validee` avec le nom du juge et la date.
4. Les tests restants sans point de règle (verdicts tirés directement du texte) sont relus par échantillon.
