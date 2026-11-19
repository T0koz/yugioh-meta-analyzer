# Questions résiduelles : ce que l'oracle ne peut pas trancher (TOK-141, jalon n°5)

> **18/11/2026**, session du jalon n°5. Lot **préparé, non envoyé** (décision 0055 : il ne part vers un joueur que si
> Thomas le décide ; sans réponse, les cartes concernées restent `formalisee`, jamais `verifiee`). Sources :
> `reponses-oracle.md` (§ 1, § 7), `points-de-regle-a-valider.md`, `situations-pour-oracle.md` (N01 à N13), et les
> séquences des 10 combos (`sequences-pour-oracle.md`, sortie de `scripts/combos_j2.py`).

## 1. Ce qui a été recensé, et pourquoi il reste si peu

L'oracle Project Ignis rejoue une situation et dit ce que son cœur permet. Il **ne tranche pas** dans trois cas :

| Cas | Pourquoi l'oracle ne suffit pas | Points recensés |
|---|---|---|
| **Texte de sa base ≠ texte TCG** | Sa base (BabelCDB) porte parfois le texte OCG, marqué « non officiel » ; son script suit ce texte | R23 (`Incredible Ecclesia`), `Mirrorjade` 2ᵉ effet, `Predaplant Dragostapelia` 2ᵉ effet (§ 7.4 de `reponses-oracle.md`) |
| **Comportement venu d'un script ou d'un réglage**, que le texte TCG ne confirme pas | Le script est écrit par la communauté ; le réglage du duel est supposé (`DUEL_TCG_SEGOC_NONPUBLIC`) | R22 (réglage), N01 (`Luluwalilith`), N04 (Attribut déjà porté), R34 (coût ou effet) |
| **Pas de situation jouable** | L'effet n'est jamais proposé par le cœur dans les états posés | N12 (`Albion the Sanctifire Dragon`, Cimetière) |

**Écartés du lot** (l'oracle a déjà répondu, ou peut répondre au jalon n°6) : R08 et R27 (b) (un avis humain + l'oracle,
confiance forte : accord) ; N09 généralisé à `Luluwalilith` 1 et `Aeon` 1 (testable par l'oracle) ; R09 moitié positive
(T52, testable, pas encore rejouée) ; R10 moitié « When » (aucun effet « When … » joué au tour 1 dans le pilote) ; la
limite « une fois par tour » de `The Three Champions of Swordsoul` (défaut du texte de notre base, testable par
l'oracle). Les 26 autres points R et les 9 points N confirmés ne sont pas repris.

## 2. Classement par impact

« Effets » : effets du pilote dont la formalisation dépend de la réponse. « Combos » : combos parmi les 10 du lot J2
plein dont une séquence trouvée par le moteur passe par l'un de ces effets (compté sur les séquences exportées).

| Rang | Question | Point | Effets touchés | Combos touchés (sur 10) | Pourquoi l'oracle ne tranche pas |
|---|---|---|---|---|---|
| 1 | Q1 | R23 | `Incredible Ecclesia` 3 | **5** : G2, G7, G8, G9, G10 (la carte revient en main en Phase de Fin ; cible de G9) | texte OCG dans sa base |
| 2 | Q2 | R22 (réglage) | tous les effets déclenchés facultatifs simultanés ; dans les séquences : `The Golden Swordsoul` 2 + `Guiding Quem` 1, `Guiding Quem` 2 + `The Three Champions of Swordsoul` 1 | **1** : G7 (2 transitions) ; et T45, T62 du jeu de tests | dépend d'un réglage du duel supposé |
| 3 | Q3 | N01 | `Despian Luluwalilith` 1 | 0 (aucune séquence ne fait sa Synchro) ; change la liste des combos possibles | comportement de script (confiance moyenne) |
| 4 | Q5 | R34 | `The Fallen & The Virtuous` 1 | 4 : G1, G4, G6, G8 (aucun effet au tour 1 sans annulation adverse) | comportement de script |
| 5 | Q4 | N04 | `Hyperinvoked Aeon` 2, `Mixousia` 1 et 3 | 0 (effets écartés par le filtre déclaré « pas de changement d'Attribut ») | restriction de script, contraire au texte TCG |
| 6 | Q6 | texte | `Mirrorjade` 2 | 0 (suppose une carte adverse) | texte OCG dans sa base |
| 7 | Q7 | N12 | `Albion the Sanctifire Dragon` 3 | 0 (suppose des monstres adverses) | aucune situation jouable |

Sept questions sur dix permises : deux seulement (Q1, Q2) touchent un combo du tour 1. Si Thomas n'en envoie qu'une
partie, envoyer **Q1 et Q2**.

## 3. Les questions (≈ 15 minutes de lecture)

Pour un joueur de tournoi, sans connaissance du moteur. Une réponse courte suffit (« oui », « non », « je ne sais
pas ») ; une source (ruling, texte imprimé, page de règles) vaut mieux qu'un souvenir.

**Q1 — `Incredible Ecclesia, the Virtuous`, retour en main en Phase de Fin** (R23, T37, J07)
Son effet du Cimetière la ramène en main pendant la Phase de Fin, si un monstre Fusion est allé au Cimetière ce
tour. Le texte TCG imprimé n'écrit pas « You can » ; la version OCG l'écrit.
→ En TCG, le joueur **doit**-il reprendre la carte (effet obligatoire), ou peut-il **choisir** de la laisser au
Cimetière ? `[ ] obligatoire  [ ] facultatif  [ ] je ne sais pas` — source :

**Q2 — Deux de mes effets facultatifs se déclenchent en même temps** (R22, T45, T62)
Exemple : `Cocatorium the Heavy Metal Avian` bannit `Tri-Brigade Mercourier` du Deck en coût ; `Mercourier` (banni) et
`The Golden Swordsoul` (au Cimetière) peuvent tous deux s'activer après la chaîne.
→ En TCG aujourd'hui, est-ce que je **choisis librement l'ordre** dans la nouvelle chaîne, et puis-je **n'en activer
qu'un** ? `[ ] ordre libre, un seul possible  [ ] ordre libre, tous ceux que je veux  [ ] ordre imposé (lequel ?)`

**Q3 — `Despian Luluwalilith` et sa propre Invocation** (N01, J30)
Son effet s'active quand une carte quitte l'Extra Deck.
→ S'active-t-il quand **elle-même** quitte l'Extra Deck pour être Invoquée par Synchro ? `[ ] oui  [ ] non`

**Q4 — Déclarer l'Attribut que le monstre a déjà** (N04, J17 à J19)
`Hyperinvoked Aeon` (les autres monstres prennent l'Attribut déclaré) et `Mixousia the Confounder` (un monstre ciblé,
ou elle-même au Cimetière, prend l'Attribut déclaré).
→ Peut-on déclarer un Attribut que le monstre visé porte déjà (ex. TÉNÈBRES pour `Aluber`) ? `[ ] oui  [ ] non`

**Q5 — `The Fallen & The Virtuous` : l'envoi depuis l'Extra Deck est-il un coût ?** (R34)
Son premier effet envoie un monstre de l'Extra Deck au Cimetière, puis cible une carte face recto et la détruit.
→ L'envoi est-il **payé à l'activation** (perdu même si l'activation est annulée, par ex. par `Solemn Judgment`) ?
`[ ] oui, c'est un coût  [ ] non, il a lieu à la résolution`

**Q6 — `Mirrorjade the Iceblade Dragon`, 2ᵉ effet** (texte OCG ≠ TCG, hors tour 1)
Le texte TCG le déclenche quand elle quitte le terrain **à cause d'une carte adverse** ; la version OCG, quand
**l'adversaire la fait quitter** le terrain.
→ Y a-t-il un cas de jeu où les deux formulations donnent un résultat différent ? `[ ] non  [ ] oui (lequel ?)`

**Q7 — `Albion the Sanctifire Dragon`, effet du Cimetière** (N12, non testable par l'oracle, hors tour 1)
L'effet concerne les monstres des zones Monstre **centrales**.
→ S'agit-il de la zone centrale **de chaque joueur** (une chez moi, une chez l'adversaire) ? `[ ] oui  [ ] non (alors ?)`

Commentaire libre :

## 4. Ce que change chaque réponse

- **Q1** : « obligatoire » (texte TCG) → rien ne change ; « facultatif » → la Phase de Fin peut se terminer sans
  reprendre `Incredible Ecclesia`, une option de plus dans chaque combo qui passe par elle (T37 et J07 à revoir).
- **Q2** : « ordre libre » → rien ne change (réglage par défaut, R22 codé ainsi) ; « ordre imposé » → règle à rendre
  configurable dans le moteur, toutes les séquences avec deux déclencheurs simultanés à rejouer.
- **Q3** : « non » → rien ne change (N01 adopté au lot C3) ; « oui » → l'Invocation Synchro de `Luluwalilith` déclenche
  son propre effet (+500 ATK, annulation possible).
- **Q4, Q5, Q6, Q7** : sans effet sur les combos du tour 1 ; elles fixent une liste de choix (Q4), une nature de coût qui
  ne compte que si l'activation est annulée (Q5), ou des effets qui supposent l'adversaire (Q6, Q7).

## 5. Ajout du jalon n°7 (TOK-144, 18/11) : ce que l'échantillon J1 n'a pas tranché

Rien n'est envoyé (décision 0055). Une seule question nouvelle ; les trois désaccords de l'échantillon (E32, E49, E68)
ont reçu une réponse de l'oracle et ont été corrigés côté moteur (`j1-rapport.md` § 9).

| Rang | Question | Point | Effets touchés | Combos touchés (sur 10) | Pourquoi l'oracle ne tranche pas |
|---|---|---|---|---|---|
| 8 | Q8 | E18 | `Dogmatika Ecclesia` 2 (« un monstre Invoqué Spécialement depuis l'Extra Deck est sur le terrain ») | 0 (au tour 1, l'adversaire n'a pas de monstre) | le lanceur ne sait pas donner à un monstre adverse un historique d'invocation |

**Q8 — `Dogmatika Ecclesia, the Virtuous`, condition de son Invocation depuis la main** (E18)
Elle peut s'Invoquer Spécialement depuis la main si un monstre Invoqué Spécialement depuis l'Extra Deck est sur le
terrain. → Un monstre de ce genre **chez l'adversaire** suffit-il ? `[ ] oui  [ ] non` — source :

Ce que change la réponse : « oui » → rien (le moteur lit déjà les deux terrains) ; « non » → la condition se limite à
notre terrain. Sans effet sur un combo du tour 1. Sans réponse, `Dogmatika Ecclesia` reste `verifiee` (la règle du
§ 8 de `j1-rapport.md` ne la bloque pas : ses deux effets du pilote ont des situations en accord) ; ce point est le
seul de la carte que l'oracle n'a pas pu jouer.

Différence de modèle J2-a (retour d'`Ecclesia and the Dark Dragon` en Phase de Fin) : **pas une question pour un
joueur**, l'oracle a répondu ; c'est une correction à faire côté moteur (`j2-rapport.md` § 9.3).
