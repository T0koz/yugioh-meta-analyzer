# Moteur de combos — définitions formelles et schéma de données (TOK-85)

> **Statut : choix techniques arbitrés le 16 novembre 2026 (D1 à D8 bis), points de règle non validés.**
> Part des définitions du § 4 de [`decisions-2026-11-16.md`](decisions-2026-11-16.md) et les précise.
> **Sources utilisées** : textes des cartes de la table `cards` (YGOPRODeck), règles officielles de
> Konami citées de mémoire (livret de règles, non relu en ligne pendant cette session), decklists de
> la base. **Aucun script de simulateur n'a été consulté** (condition d'indépendance, § 6 des décisions).
> **Limite** : je ne suis pas un juge. Tout point de règle marqué ⚖ est à soumettre à un juge humain
> (TOK-89). La liste complète est dans [`points-de-regle-a-valider.md`](points-de-regle-a-valider.md).

Les exemples viennent du deck source du jeu de tests (voir
[`jeu-de-tests-branded.md`](jeu-de-tests-branded.md)), et les numéros `T..` renvoient à ses situations.

---

## 1. Vocabulaire minimal (pour lire la suite sans jouer)

| Terme | Sens |
|---|---|
| Zones | Main, Deck, Extra Deck (monstres Fusion, Synchro…), terrain (5 zones Monstre principales, 2 zones Monstre Extra, 5 zones Magie/Piège, 1 zone Terrain), Cimetière (« GY »), cartes bannies. |
| Invocation Normale | Poser un monstre de sa main : **une seule par tour**. |
| Invocation Spéciale | Toute autre façon de mettre un monstre sur le terrain. Pas de limite, sauf texte contraire. |
| Invocation Fusion | Invocation Spéciale d'un monstre de l'Extra Deck en envoyant au Cimetière les « matériels » listés sur lui. |
| Activation / résolution | Un effet est d'abord **activé** (on l'annonce, on paie son coût, on choisit ses cibles), puis **résolu** (il s'applique). Entre les deux, on peut lui répondre. |
| Chaîne | Pile d'effets activés en réponse les uns aux autres. Elle se résout en ordre inverse (le dernier activé s'applique en premier). |
| Vitesse | 1 : effets lents (ne répondent à rien). 2 : effets rapides (répondent). 3 : pièges de contre. |
| Coût / effet | Dans un texte, ce qui précède « ; » est le coût (payé à l'activation, jamais remboursé). Ce qui suit est l'effet. Ce qui précède « : » est la condition d'activation. |
| « Une fois par tour » | Deux formes : *par nom* (« You can only use this effect of "X" once per turn » : vaut pour toutes les copies) et *par exemplaire* (« Once per turn » : vaut pour cette carte-là tant qu'elle reste sur le terrain). |
| Verrou | Restriction qui dure tout le tour (« you cannot Special Summon from the Extra Deck, except Fusion Monsters »). |

---

## 2. Les quatre définitions

### 2.1 État

**Définition.** L'état est la photo complète du jeu à un instant donné. Il doit être **suffisant** :
deux états identiques ont exactement les mêmes actions légales et les mêmes suites possibles, quel
que soit le chemin qui y a mené. Tout ce que le passé peut encore changer à l'avenir doit donc être
écrit **dans** la photo. C'est la propriété de Markov, et c'est elle qui rend l'équivalence (§ 2.3) valide.

La photo du § 4 des décisions (main, terrain, cimetière, bannies, deck, « une fois par tour »
consommés) est nécessaire mais **pas suffisante**. Les textes Branded obligent à y ajouter une
« mémoire du tour » et des attributs par exemplaire de carte. L'état a quatre blocs.

**A. Cadre**

- numéro du tour, joueur dont c'est le tour, phase (Pioche, Standby, Principale 1, Combat, Principale 2, Fin) ;
- points de vie des deux joueurs ;
- Invocation Normale du tour déjà utilisée (oui/non) ;
- pile de chaîne (vide dans un état stable, voir § 2.2) et effets déclenchés en attente ;
- **fenêtre d'interruption adverse** : champ réservé, toujours « aucune réponse » dans le pilote (§ 2.5).

**B. Zones, pour chaque joueur**

| Zone | Forme | Remarque |
|---|---|---|
| Main | multi-ensemble | L'ordre n'a pas de sens en jeu. |
| Deck | multi-ensemble **+ segments ordonnés connus** (dessus, dessous) | Après une recherche, le deck est mélangé : l'ordre disparaît. Mais `Springans Kitt` pose une carte **au-dessous** du deck : cette position est connue jusqu'au prochain mélange. |
| Extra Deck | multi-ensemble | |
| Zones Monstre | 5 principales + 2 Extra, **indexées** | La position compte pour `Sprind the Irondash Dragon` (colonne) et `Albion the Sanctifire Dragon` (zones centrales). Voir décision D3. |
| Zones Magie/Piège, Terrain | indexées | |
| Cimetière | multi-ensemble | ⚖ Aucune carte du pilote ne lit l'ordre du Cimetière ; à revoir si une carte le fait. |
| Bannies | multi-ensemble, face visible ou cachée | |

**C. Attributs de chaque exemplaire de carte** (une « instance », pas un nom)

- position (Attaque, Défense, face cachée), compteurs ;
- **comment et quand elle est arrivée** : posée ce tour ou non, par Invocation Normale, Spéciale, Fusion, Synchro ; venue de l'Extra Deck ou non ;
- **« correctement invoquée »** (oui/non) : un monstre de l'Extra Deck envoyé au Cimetière sans avoir été invoqué ne peut pas en être rappelé. Ce drapeau suit la carte au Cimetière et chez les bannies ;
- **« envoyée au Cimetière ce tour »** (plusieurs effets de Phase de Fin le lisent : `Titaniklad`, `Sprind`, `The Dragon that Devours the Dogma`, `Despian Luluwalilith`) ;
- modifications temporaires avec leur échéance : nom, Type, Attribut, Niveau, ATK (`Cocatorium` prend le nom d'un autre monstre « jusqu'à la Phase de Fin »), effets annulés ;
- carte posée face cachée ce tour (une Magie Jeu-Rapide posée ne s'active pas le tour même) ;
- restrictions portées par l'exemplaire (`Mirrorjade` : « ne peut pas utiliser cet effet au tour suivant »).

**D. Mémoire du tour** (ce que le passé interdit ou permet encore)

| Élément | Exemple Branded qui l'impose |
|---|---|
| « Une fois par tour » par nom, déjà consommés | `Aluber` : un seul des deux effets, une fois (T04). |
| Cartes dont le nom a déjà été activé ce tour | « You can only activate 1 "Branded Fusion" per turn » (T14), `Nadir Servant` (T21). |
| Verrous actifs | `Nadir Servant` : plus aucune Invocation Spéciale depuis l'Extra Deck (T20). |
| **Historique d'invocations depuis l'Extra Deck** | `Branded Fusion` : « the turn you activate this card » interdit de l'activer si une Synchro a **déjà** été invoquée ce tour (T12). Le passé rend l'action illégale après coup. |
| Événements du tour | « if a Fusion Monster(s) was sent to your GY this turn » (`Blazing Cartesia`, `Incredible Ecclesia`, `Branded in High Spirits`). |
| Effets différés | `Gold Sarcophagus` : « during your second Standby Phase after activation » ; `Ecclesia and the Dark Dragon` revient à la Phase de Fin. Ils traversent les tours. |
| Effets « appliqués ce tour » | `Mulcharmy Fuwalos`. |

**Ce que l'état ne contient pas** : le chemin suivi (il est dans les transitions), le jugement sur
la qualité du plateau, et les informations cachées de l'adversaire (réservées, § 2.5).

**Tests de la définition sur des exemples Branded**

1. *Même contenu de Cimetière, états différents.* `Titaniklad the Ash Dragon` est au Cimetière.
   Chemin 1 : `Nadir Servant` l'y a envoyé depuis l'Extra Deck. Chemin 2 : il a été invoqué par
   Fusion puis utilisé comme matériel. Les cartes visibles sont les mêmes, mais seul le chemin 2
   permet à `Tri-Brigade Springans Kitt` de le rappeler. Sans le drapeau « correctement invoquée »,
   la définition du § 4 confondrait les deux (T22, T52).
2. *Même plateau, verrou différent.* Deux mains mènent à `Albaz` + `Blazing Cartesia` sur le
   terrain ; dans l'une, `Nadir Servant` a été joué. L'effet de Fusion de `Cartesia` n'est légal que
   dans l'autre (T20). La mémoire du tour fait la différence.
3. *Nom temporaire.* `Cocatorium` bannit `Tri-Brigade Mercourier` du deck et **devient**
   « Tri-Brigade Mercourier » : `Tri-Brigade Springans Kitt` (« si vous contrôlez un monstre
   Tri-Brigade ») peut alors être invoqué (T32). L'état doit porter le nom courant, pas seulement
   le nom imprimé.

### 2.2 Action

**Définition.** Une action est une **décision élémentaire** d'un joueur, prise dans un état, parmi
la liste des décisions légales à cet instant. Le moteur ne fait que deux choses : lister les
décisions légales d'un état, et appliquer celle qui est choisie.

Le § 4 cite « invoquer, activer, choisir une cible ». Liste complète des décisions :

| Famille | Décisions |
|---|---|
| Déclarer | Invocation Normale, Pose, Invocation Spéciale inhérente (sans chaîne), **activation** d'une carte ou d'un effet, changement de position, déclaration d'attaque, changement de phase, fin de tour. |
| Compléter une activation | payer le **coût** (quelle carte défausser, envoyer, bannir), choisir les **cibles**. |
| Répondre | enchaîner un effet (ou passer). |
| Compléter une résolution | choisir les matériels, la carte cherchée, la zone d'arrivée, l'option (« ajouter à la main **ou** invoquer »), appliquer ou non un « then you can ». |
| Ordonner | l'ordre de plusieurs effets déclenchés en même temps. |
| Subir le hasard | pioche : ce n'est pas une décision du joueur, c'est une **branche aléatoire** (une par carte possible), étiquetée comme condition (§ 2.4). |

**Deux niveaux** (décision D2) :

- le **pas** : une décision élémentaire. C'est le niveau du moteur et de la comparaison avec l'oracle ;
- la **transition** : tout ce qui se passe entre deux **états stables**. Un état stable est un état
  où la chaîne est vide, où aucun effet déclenché n'attend et où le joueur du tour a la main. Une
  transition regroupe donc une action déclarée, ses coûts, ses cibles, la chaîne qu'elle ouvre, les
  effets déclenchés qui en découlent et tous les choix faits en route. C'est le niveau du combo.

**Ce qu'une action consomme** (question du ticket) : l'Invocation Normale du tour ; un « une fois
par tour » (consommé **à l'activation**, même si l'effet est ensuite annulé ⚖) ; les cartes du coût ;
une zone libre ; et parfois une liberté future (un verrou). Tout cela s'écrit dans l'état d'arrivée.

**Légalité d'une activation.** Une activation est légale si, au moment de l'annoncer : la
condition (avant « : ») est vraie, le coût (avant « ; ») est payable, des cibles valides existent, la
vitesse convient, aucune limite « une fois par tour » ni aucun verrou ne l'interdit, **et l'effet peut
se résoudre au moins en partie** ⚖ (on ne peut pas activer `Aluber` s'il ne reste aucune Magie/Piège
« Branded » dans le deck, T02).

**Tests sur des exemples Branded**

1. `Aluber the Jester of Despia` en Invocation Normale, puis recherche de `Branded Fusion` : une
   transition, trois pas (déclarer l'invocation, activer l'effet déclenché, choisir la carte) (T01).
2. `Branded Opening` (« Discard 1 card, then take… ») : **pas de « ; »**, la défausse fait partie de
   l'effet et non du coût. Avec `Super Polymerization` (« Discard 1 card; … ») c'est un coût. La
   définition distingue donc « payer » (pas d'activation) et « appliquer » (pas de résolution) (T34, T38).
3. `Blazing Cartesia` fusionne `Granguignol` en utilisant `Tri-Brigade Springans Kitt` comme
   matériel : deux effets se déclenchent en même temps (`Granguignol` « si invoqué par Fusion »,
   `Kitt` « si envoyé au Cimetière »). Le joueur choisit l'ordre : c'est un pas « ordonner », et les
   deux ordres sont deux transitions distinctes (T45).

### 2.3 Équivalence

**Définition.** Deux états sont équivalents si leur **forme canonique** est identique. La forme
canonique est l'écriture normalisée de l'état :

1. les exemplaires d'une même carte sont **interchangeables** quand tous leurs attributs (bloc C)
   sont égaux : on ne distingue pas le 1er `Aluber` du 2e ;
2. les multi-ensembles sont triés (par identifiant de carte puis par attributs) ;
3. les zones indexées gardent leur index (voir D3 pour une simplification possible) ;
4. le deck s'écrit « multi-ensemble + segments connus » ;
5. la mémoire du tour est écrite en entier, triée.

L'identifiant d'un état est l'empreinte (SHA-256) de cette forme. Deux chemins qui arrivent à la
même empreinte arrivent au même nœud : le résultat de l'exploration est un **graphe**, pas un arbre.

Trois précisions que le § 4 ne donnait pas :

- **L'équivalence porte sur l'état complet, pas sur le plateau visible.** « Même photo » veut dire
  même bloc A, B, C et D. Deux plateaux identiques avec des verrous différents ne sont pas équivalents.
- **Elle ne dit rien du chemin.** Deux combos différents peuvent finir au même état : ce sont deux
  combos (deux chemins), un seul plateau final.
- **Une seconde équivalence, plus large, sert à l'affichage** : le « plateau final » (terrain, main,
  Cimetière, bannies en fin de tour, sans la mémoire du tour écoulé). Elle sert à regrouper les
  résultats pour un humain, jamais à élaguer l'exploration.

**Tests sur des exemples Branded**

1. *Deux ordres, un état.* Main : `Aluber`, `Nadir Servant`. Ordre 1 : `Nadir` (envoie `Titaniklad`,
   ajoute `Fallen of Albaz`) puis Invocation Normale d'`Aluber` (cherche `Branded Fusion`). Ordre 2 :
   l'inverse. Mêmes zones, mêmes « une fois par tour », même verrou : **un seul état**, deux chemins.
2. *Copies interchangeables.* Défausser le 1er ou le 2e `Mulcharmy Fuwalos` donne le même état.
3. *Faux jumeaux.* Exemple 1 du § 2.1 (`Titaniklad` au Cimetière, invoqué ou non) : **deux états**.

### 2.4 Arrêt

Le § 4 dit : « plus d'action légale, ou profondeur maximale, boucles coupées ». Trois précisions.

**a. Fin de ligne.** Au tour d'ouverture, « passer à la Phase de Fin » est toujours légal : il n'y a
donc jamais « plus aucune action légale » au sens strict. Je distingue :

- **fin forcée** : état stable où la seule action légale restante est de passer ;
- **fin volontaire** : le joueur passe alors qu'il lui reste des actions. Tout état stable de Phase
  Principale peut donc conduire à un plateau final.

Dans les deux cas, le **plateau final** est l'état à la fin de la Phase de Fin, **après** : les
effets obligatoires de Phase de Fin (`Incredible Ecclesia` : « Add this card », sans « You can »,
T37), les effets facultatifs choisis, les retours différés (`Ecclesia and the Dark Dragon`) et la
limite de 6 cartes en main. Un état où un effet obligatoire attend n'est jamais final.

**b. Profondeur maximale.** Paramètre de l'exploration, compté en transitions. Un état atteint à la
profondeur maximale et qui a encore des actions est marqué **tronqué** : ce n'est pas un plateau
final, et l'exploration est déclarée **incomplète**. Ce statut est publié avec le résultat (cohérent
avec « n'afficher que ce qui est démontré »).

**c. Boucles.** L'exploration étant un graphe d'états, revenir sur un état déjà vu ne relance rien :
l'arête est enregistrée (marquée « retour ») et le nœud n'est pas ré-exploré. Un combo est un chemin
**sans répétition d'état**. Une boucle qui change l'état à chaque tour (elle gagne des points de vie,
des compteurs…) n'est pas détectée par l'égalité d'états : c'est la profondeur maximale qui la coupe,
et le résultat est alors « tronqué ». Cela tranche la partie « boucles » de la question ouverte n° 6.

**Motifs d'arrêt enregistrés** : `fin_forcee`, `fin_volontaire`, `tronque_profondeur`,
`retour_etat_connu`, `non_couvert` (une carte non formalisée intervient, § 3.4), `hors_perimetre`
(Phase de Combat, tour adverse : réservés).

**Tests sur des exemples Branded**

1. Main : `Ash Blossom` ×2, `Ghost Ogre` ×2, `Droll & Lock Bird`. Aucune de ces cartes ne peut agir
   seule au tour 1 (elles répondent à l'adversaire), sauf l'Invocation Normale. Fins forcées après une
   Invocation Normale ; fin volontaire possible dès le départ.
2. `Nadir Servant` envoie `Titaniklad` : le plateau « fin de Phase Principale » n'est pas final,
   l'effet de Phase de Fin de `Titaniklad` (ajouter ou invoquer `Albaz` ou un monstre « Dogmatika »)
   ouvre encore plusieurs branches (T18).
3. `Garura, Wings of Resonant Life` envoyé au Cimetière : « piochez 1 carte ». La suite dépend du
   hasard : une branche par carte piochable, chacune portant la condition « pioche = X » (T19).

### 2.5 Places réservées (hors pilote)

- **Point d'interruption adverse.** Chaque pas de type « activation » ou « invocation » ouvre une
  **fenêtre de réponse**. Le modèle l'enregistre toujours, avec la réponse `aucune` dans le pilote.
  Plus tard, la même fenêtre portera une réponse adverse (`Ash Blossom`, `Droll & Lock Bird`…) et
  produira des branches. Le schéma a la table et la colonne ; le pilote ne les remplit pas.
- **Tours suivants.** L'état porte déjà le numéro de tour, le joueur actif, la phase, les effets
  différés et les restrictions « au tour suivant ». Les deux joueurs ont la même structure de zones.
  Rien n'est spécifique au tour 1 dans la forme de l'état ; seule l'exploration s'y limite.
- **Information cachée.** La main et le deck adverses sont dans l'état, avec un drapeau « connu /
  inconnu » par zone. Le pilote les laisse « inconnu ».

---

## 3. Schéma de données

Proposition en SQLite, comme le reste du projet. Préfixe `cb_` (combos) pour ne rien mêler aux
tables de méta. **Rien n'est créé** : c'est un schéma sur papier, à implémenter en tranche 0 (TOK-90).

### 3.1 Vue d'ensemble

```
cb_card ──< cb_effect            texte découpé en effets, avec statut de formalisation
   │
   └──< cb_step_card >── cb_step ──> cb_transition ──> cb_state (départ, arrivée)
                              │            │
                              │            ├──< cb_transition_condition >── cb_condition
                              │            └──< cb_relation            (dérivée)
                              └──< cb_window                             (interruption réservée)

cb_run ──< cb_transition         une exploration : deck, main de départ, paramètres
cb_run ──< cb_combo ──< cb_combo_step >── cb_transition
```

### 3.2 Tables

```sql
-- Cartes : pointe vers cards.id, fige le texte utilisé (errata, question ouverte n° 6).
CREATE TABLE cb_card (
    card_id        INTEGER PRIMARY KEY,          -- = cards.id (YGOPRODeck)
    name           TEXT NOT NULL,                -- nom imprimé
    text_sha256    TEXT,                         -- empreinte du texte formalisé
    text_fetched   TEXT,                         -- date de lecture du texte
    text_source    TEXT NOT NULL DEFAULT 'ygoprodeck',
    status         TEXT NOT NULL CHECK (status IN
        ('non_traitee','brouillon','formalisee','verifiee','non_formalisable')),
    status_reason  TEXT,                         -- ex. « texte absent de la source »
    verified_by    TEXT,                         -- 'oracle', 'juge', 'oracle+juge'
    updated_at     TEXT NOT NULL
);

-- Appartenance à un archétype : calculée depuis le NOM et les clauses « always treated as »,
-- jamais depuis cards.archetype (voir § 3.5).
CREATE TABLE cb_card_name_tag (
    card_id   INTEGER NOT NULL REFERENCES cb_card(card_id),
    tag       TEXT NOT NULL,                     -- 'Dogmatika', 'Despia', 'Fallen of Albaz'…
    origin    TEXT NOT NULL CHECK (origin IN ('nom','traite_comme')),
    PRIMARY KEY (card_id, tag)
);

-- Un effet = un morceau du texte, avec sa forme formelle.
CREATE TABLE cb_effect (
    effect_id      INTEGER PRIMARY KEY,
    card_id        INTEGER NOT NULL REFERENCES cb_card(card_id),
    position       INTEGER NOT NULL,             -- 1er, 2e… effet du texte
    kind           TEXT NOT NULL CHECK (kind IN
        ('invocation_inherente','declenche','ignition','rapide','continu',
         'activation_carte','condition_invocation','restriction')),
    speed          INTEGER,                      -- 1, 2, 3 ; NULL si pas d'activation
    optional       INTEGER NOT NULL,             -- 1 « You can », 0 obligatoire
    timing         TEXT CHECK (timing IN ('if','when') OR timing IS NULL),
    limit_scope    TEXT CHECK (limit_scope IN
        ('aucune','par_nom_effet','par_nom_carte','par_exemplaire','activation_par_nom')),
    text_span      TEXT NOT NULL,                -- extrait exact du texte officiel
    formal_json    TEXT,                         -- condition, coût, cibles, résolution, verrous
    status         TEXT NOT NULL,                -- mêmes valeurs que cb_card.status
    UNIQUE (card_id, position)
);

-- Une exploration : ce qu'on a demandé au moteur.
CREATE TABLE cb_run (
    run_id         INTEGER PRIMARY KEY,
    mode           TEXT NOT NULL CHECK (mode IN ('absolu','decklist')),
    deck_ref       TEXT,                         -- tournament_decks.id en mode decklist
    start_state    TEXT NOT NULL REFERENCES cb_state(state_id),
    max_depth      INTEGER NOT NULL,
    filters_json   TEXT NOT NULL,                -- filtres d'exploration déclarés (décision D4)
    rules_version  TEXT NOT NULL,                -- version du livret + banlist
    engine_version TEXT NOT NULL,
    complete       INTEGER NOT NULL,             -- 0 si au moins un état tronqué ou non couvert
    started_at     TEXT NOT NULL
);

-- États : identifiés par l'empreinte de leur forme canonique (§ 2.3).
CREATE TABLE cb_state (
    state_id       TEXT PRIMARY KEY,             -- SHA-256 de canonical_json
    canonical_json TEXT NOT NULL,                -- blocs A, B, C, D
    turn           INTEGER NOT NULL,
    active_player  INTEGER NOT NULL,             -- 0 = nous, 1 = adversaire
    phase          TEXT NOT NULL,
    is_stable      INTEGER NOT NULL,
    board_id       TEXT                          -- empreinte du « plateau final » (affichage)
);

-- Transitions : d'un état stable à un état stable.
CREATE TABLE cb_transition (
    transition_id  INTEGER PRIMARY KEY,
    run_id         INTEGER NOT NULL REFERENCES cb_run(run_id),
    from_state     TEXT NOT NULL REFERENCES cb_state(state_id),
    to_state       TEXT NOT NULL REFERENCES cb_state(state_id),
    action_type    TEXT NOT NULL,                -- 'invocation_normale','activation','phase'…
    actor_card_id  INTEGER REFERENCES cb_card(card_id),   -- la carte « jouée »
    actor_effect   INTEGER REFERENCES cb_effect(effect_id),
    is_random      INTEGER NOT NULL DEFAULT 0,   -- branche de hasard (pioche)
    stop_reason    TEXT,                         -- § 2.4, NULL si la ligne continue
    verified       INTEGER NOT NULL              -- 0 si une carte impliquée n'est pas 'verifiee'
);
CREATE INDEX idx_cb_transition_from ON cb_transition (run_id, from_state);
CREATE INDEX idx_cb_transition_actor ON cb_transition (actor_card_id);

-- Pas : les décisions élémentaires à l'intérieur d'une transition (niveau oracle).
CREATE TABLE cb_step (
    step_id        INTEGER PRIMARY KEY,
    transition_id  INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    position       INTEGER NOT NULL,
    step_type      TEXT NOT NULL,                -- 'declarer','cout','cible','enchainer',
                                                 -- 'resoudre','choisir','ordonner','hasard'
    chain_link     INTEGER,                      -- maillon de chaîne, NULL hors chaîne
    effect_id      INTEGER REFERENCES cb_effect(effect_id),
    UNIQUE (transition_id, position)
);

-- Toutes les cartes qu'un pas nomme, avec leur rôle. C'est la table des requêtes.
CREATE TABLE cb_step_card (
    step_id    INTEGER NOT NULL REFERENCES cb_step(step_id),
    card_id    INTEGER NOT NULL REFERENCES cb_card(card_id),
    role       TEXT NOT NULL CHECK (role IN
        ('acteur','cout','materiel','cible','choisie','deplacee','revelee','condition')),
    from_zone  TEXT,
    to_zone    TEXT,
    PRIMARY KEY (step_id, card_id, role)
);
CREATE INDEX idx_cb_step_card_card ON cb_step_card (card_id);

-- Fenêtres d'interruption adverse : réservées, vides de réponses dans le pilote.
CREATE TABLE cb_window (
    window_id   INTEGER PRIMARY KEY,
    step_id     INTEGER NOT NULL REFERENCES cb_step(step_id),
    window_type TEXT NOT NULL,                   -- 'reponse_activation','reponse_invocation'
    response    TEXT NOT NULL DEFAULT 'aucune'   -- plus tard : carte adverse enchaînée
);

-- Conditions : rattachées aux étapes, hors du combo (décision du § 4).
CREATE TABLE cb_condition (
    condition_id INTEGER PRIMARY KEY,
    kind         TEXT NOT NULL CHECK (kind IN
        ('etat','hasard','adverse','verrou_absent','limite_disponible','zone_libre','hypothese')),
    expression   TEXT NOT NULL,                  -- forme lisible et formelle
    UNIQUE (kind, expression)
);
CREATE TABLE cb_transition_condition (
    transition_id INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    condition_id  INTEGER NOT NULL REFERENCES cb_condition(condition_id),
    PRIMARY KEY (transition_id, condition_id)
);

-- Relations entre deux cartes : les quatre familles, dérivées des pas.
CREATE TABLE cb_relation (
    relation_id   INTEGER PRIMARY KEY,
    transition_id INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    source_card   INTEGER NOT NULL REFERENCES cb_card(card_id),   -- celle qui agit
    target_card   INTEGER NOT NULL REFERENCES cb_card(card_id),   -- celle qui subit
    family        TEXT NOT NULL CHECK (family IN
        ('deplace','materiel_ou_cout','conditionne','interagit_adverse')),
    detail        TEXT                            -- 'deck→main', 'materiel de fusion', …
);
CREATE INDEX idx_cb_relation_pair ON cb_relation (source_card, target_card, family);

-- Combos : un chemin, enregistré dans son ordre réel.
CREATE TABLE cb_combo (
    combo_id     INTEGER PRIMARY KEY,
    run_id       INTEGER NOT NULL REFERENCES cb_run(run_id),
    final_state  TEXT NOT NULL REFERENCES cb_state(state_id),
    length       INTEGER NOT NULL,
    label        TEXT NOT NULL CHECK (label IN ('demontre','non_verifie')),
    stop_reason  TEXT NOT NULL
);
CREATE TABLE cb_combo_step (
    combo_id      INTEGER NOT NULL REFERENCES cb_combo(combo_id),
    position      INTEGER NOT NULL,
    transition_id INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    actor_card_id INTEGER REFERENCES cb_card(card_id),   -- recopié pour les requêtes
    PRIMARY KEY (combo_id, position)
);
CREATE INDEX idx_cb_combo_step_actor ON cb_combo_step (actor_card_id, combo_id, position);
```

### 3.3 Les quatre familles de relations, sur des cas Branded

Une relation relie la carte qui agit à une autre carte nommée dans la même transition. Les familles
peuvent coexister sur une même paire.

| Famille | Règle de dérivation depuis `cb_step_card` | Exemple |
|---|---|---|
| `deplace` | l'acteur fait changer de zone une autre carte par son **effet** | `Aluber` → `Branded Fusion` (deck → main) |
| `materiel_ou_cout` | l'autre carte a le rôle `materiel` ou `cout` | `Branded Fusion` → `Fallen of Albaz` (matériel) ; `Fallen of the White Dragon` → `Titaniklad` (coût) |
| `conditionne` | l'autre carte a le rôle `condition` : sa présence rend l'action légale | `Blazing Cartesia` ← `Fallen of Albaz` (« si vous contrôlez Albaz ») ; `Springans Kitt` ← `Titaniklad` au Cimetière |
| `interagit_adverse` | la carte visée appartient à l'adversaire, ou l'effet répond à une action adverse | `Super Polymerization` → monstre adverse ; `Ash Blossom` (hors pilote, réservée) |

Une même transition produit souvent plusieurs relations : `Fallen of the White Dragon` paie son
coût avec `Titaniklad` (`materiel_ou_cout`), ce qui fait quitter l'Extra Deck à une carte et déclenche
`Guiding Quem` (`conditionne`, dans la transition suivante).

### 3.4 Statuts de formalisation et « non couvert »

Le ticket cite quatre statuts (non traité, brouillon, vérifié, non formalisable), les décisions
trois (formalisée, vérifiée, non formalisable). Je propose les **cinq**, dans l'ordre du cycle de vie
(décision D6) :

| Statut | Sens | Le moteur l'exécute ? |
|---|---|---|
| `non_traitee` | personne n'a regardé la carte, ou son texte manque dans la source | non → « non couvert » |
| `brouillon` | un LLM a proposé une forme, non testée | non → « non couvert » |
| `formalisee` | la forme passe les tests du moteur | oui, résultats étiquetés **« non vérifié »** |
| `verifiee` | accord avec l'oracle, ou relue par un juge | oui, résultats **« démontrés »** |
| `non_formalisable` | le texte ne s'exprime pas dans le modèle (raison écrite) | non → « non couvert » |

« Exhaustif » (§ 4) = toute carte a l'un de ces statuts ; le taux de couverture publié est la part
de `formalisee` + `verifiee`, et le taux démontré la part de `verifiee`.

**Propagation du « non couvert »** (décision D5). Trois situations, trois réponses :

1. on demande une action **sur** une carte non couverte → réponse `non_couvert`, jamais un résultat ;
2. une exploration rencontre un état où une carte non couverte **pourrait agir** (elle est en main,
   sur le terrain, au Cimetière) → la branche s'arrête avec le motif `non_couvert`, l'exploration est
   `complete = 0` ;
3. une énumération porte sur une zone qui **contient** une carte non couverte (ex. « un monstre
   Fusion de l'Extra Deck qui mentionne Albaz » alors que des cartes de l'Extra Deck ne sont pas
   formalisées) → les résultats trouvés sont donnés, étiquetés « liste peut-être incomplète : N cartes non
   couvertes dans la zone ».

### 3.5 Piège de données trouvé : `cards.archetype` ne dit pas la règle

En jeu, une carte « Dogmatika » est une carte dont le **nom contient** « Dogmatika », ou dont le
texte dit « always treated as ». Or la colonne `cards.archetype` (YGOPRODeck) est un classement
éditorial, à une seule valeur :

| Carte | `cards.archetype` | Réalité du texte |
|---|---|---|
| `Fallen of Albaz` | Dogmatika | Son nom ne contient pas « Dogmatika » : ce n'est **pas** une carte Dogmatika. |
| `Guiding Quem, the Virtuous` | Despia | « always treated as a "Dogmatika" and "Despia" card » : **les deux**. |
| `Tri-Brigade Springans Kitt` | Springans | « Tri-Brigade » **et** « Springans ». |
| `Incredible Ecclesia, the Virtuous` | (vide) | C'est un monstre « Ecclesia » (son nom le contient). |
| `Fallen of the White Dragon` | (vide) | « always treated as "Fallen of Albaz" ». |

D'où la table `cb_card_name_tag`, calculée depuis le nom et les clauses « treated as ». Utiliser
`cards.archetype` ferait, par exemple, chercher `Fallen of Albaz` par `Dogmatika Ecclesia` (illégal).
De même, « une carte qui mentionne Fallen of Albaz » se calcule en cherchant le nom entre guillemets
dans le texte, pas par archétype (T23).

### 3.6 Les deux requêtes demandées par le ticket

**« Tous les combos qui passent par la carte X »** (X joue un rôle quelconque : jouée, matériel,
cherchée, condition) :

```sql
SELECT DISTINCT cs.combo_id
FROM cb_combo_step cs
JOIN cb_step s        ON s.transition_id = cs.transition_id
JOIN cb_step_card sc  ON sc.step_id = s.step_id
WHERE sc.card_id = :x;
-- variante « X est la carte jouée » : WHERE cs.actor_card_id = :x (index direct)
```

**« A puis directement B »** (deux étapes consécutives du combo, A jouée puis B jouée) :

```sql
SELECT a.combo_id, a.position
FROM cb_combo_step a
JOIN cb_combo_step b ON b.combo_id = a.combo_id AND b.position = a.position + 1
WHERE a.actor_card_id = :a AND b.actor_card_id = :b;
```

**« A et B ensemble »** (sans ordre) : intersection de deux fois la première requête.
**« A va chercher B »** (lecture plus fine que la succession) : `cb_relation` avec
`source_card = :a AND target_card = :b AND family = 'deplace'`.

Un **micro-combo** est un segment contigu de `cb_combo_step`. Il n'est pas stocké à part : AB, BC et
CD se lisent dans ABCD par les positions. Un macro-combo sur plusieurs tours sera un chemin dont les
transitions traversent un changement de tour (colonne `turn` de l'état).

---

## 4. Questions ouvertes du § 8 : ce que ces définitions changent

| N° | Question | Position |
|---|---|---|
| 1 | Qui juge ? | **Reste ouverte.** Ce document produit la matière à juger : 34 points de règle listés dans `points-de-regle-a-valider.md`. |
| 2 | Budget | Reste ouverte. Le chronométrage de cette session donne un premier point de calibrage. |
| 3 | L'oracle liste-t-il toutes les actions légales ? | **Reste ouverte, et devient bloquante** : le niveau « pas » (§ 2.2) suppose qu'on puisse comparer une liste d'actions légales, pas seulement un résultat. Si l'oracle ne la donne pas, la comparaison se fera au niveau « transition » (états d'arrivée), moins fine. |
| 4, 5 | Banc sur Mac, rulings TCG/OCG | Non traitées (TOK-86). |
| 6 | Boucles | **Tranchée** (§ 2.4 c). |
| 6 | Textes à une date passée | **Préparée, pas tranchée** : `cb_card.text_sha256` et `text_fetched` détectent un errata ; la source de textes anciens reste à trouver. |
| 6 | Textes OCG | Hors périmètre, non traitée. |
| 7 | Hypothèse de Winston | **Fausse telle quelle, vraie sous une forme restreinte**, voir ci-dessous. |

### L'hypothèse de Winston (§ 8, point 7)

> « Une transition ne dépend que des cartes qu'elle nomme », ce qui rendrait « retirer X » peu coûteux.

**Telle quelle, elle est fausse.** La légalité d'une transition dépend aussi de choses qu'elle ne
nomme pas. Quatre contre-exemples tirés du deck :

1. **Verrous.** « `Blazing Cartesia` fusionne `Granguignol` » ne nomme pas `Nadir Servant`, et
   pourtant elle est illégale si `Nadir Servant` a été joué avant (T20).
2. **Conditions d'absence ou de comptage.** `Mulcharmy Fuwalos` : « si vous ne contrôlez aucune
   carte ». `Incredible Ecclesia` : « si l'adversaire contrôle plus de monstres que vous ». La
   transition dépend de cartes qui ne sont **pas** là.
3. **Effets déclenchés par d'autres cartes.** Toute transition qui fait sortir une carte de l'Extra
   Deck déclenche `Guiding Quem` s'il est sur le terrain. La transition `Nadir Servant` ne nomme pas
   `Quem`, mais son état d'arrivée en dépend (T22). Avec un effet **obligatoire**, c'est pire : la
   présence de la carte impose la suite.
4. **Chaînes.** `Super Polymerization` interdit toute réponse à son activation : la légalité d'un
   enchaînement dépend de la carte à laquelle on répond.

**Forme restreinte que je crois vraie** (raisonnement de ma part, **non démontré**, à tester) :

> En mode decklist, si X ne quitte jamais sa zone cachée (Deck ou Extra Deck) le long d'un chemin,
> alors ce chemin reste légal quand on retire X du deck. Et retirer X ne crée aucun chemin nouveau.
> Donc : *les combos du deck sans X = les combos du deck avec X dont aucun pas ne nomme X*.

Pourquoi : une carte qui dort dans le Deck n'a ni effet, ni condition, ni déclencheur. Les quatre
contre-exemples ci-dessus passent tous par une carte qui a **bougé** ou **agi**, donc qui est nommée
quelque part dans le chemin (pas forcément dans la transition concernée : c'est là que la formule de
Winston était trop forte). Le filtre porte sur le **chemin entier**, pas sur la transition.

**Trois exceptions connues**, où le filtre ne suffit pas :

- les effets qui lisent un **agrégat** de la zone cachée : pioche (`Garura`), nombre de cartes
  restantes, cartes du dessus du deck. Le chemin survit, mais sa condition de hasard change ;
- « retirer X » en pratique veut dire **remplacer X par Z** (un deck fait 40 cartes) : les combos
  qui passent par Z sont nouveaux et doivent être calculés ;
- un **ban** qui passe X de 3 à 1 exemplaire : les chemins qui utilisent 2 copies de X disparaissent,
  ce que le filtre « nomme X » ne voit pas (il faut compter les exemplaires distincts utilisés).

**Conséquence pour le schéma** : `cb_step_card` (toutes les cartes nommées, avec leur rôle) est la
table qui rend « retirer X » peu coûteux. **Test à écrire en tranche 0** : sur une main, calculer les
combos avec X, filtrer, puis recalculer sans X et comparer. Tant que ce test n'a pas tourné,
l'affirmation reste une hypothèse.

---

## 5. Décisions à prendre

Formulaires regroupés dans [`decisions-a-prendre-tok-85-87.md`](decisions-a-prendre-tok-85-87.md)
(D1 à D8).
