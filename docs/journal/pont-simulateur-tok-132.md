# TOK-132 — Score de pont et simulateur de ban confrontés aux banlists (B3, lot 26, 2026-11-18)

Branche `claude/j1-tok-120-132-ban-radar-pont-d32da4` (Jalon 1), session sur Opus 5.5. Ticket B3 de l'audit de rigueur
(`audit-rigueur-statistique.md`, § 9 et § 10). **Lecture seule** de la base de référence. **Rien d'affiché ne change** :
ni `card_impact`, ni `/simulate-ban`, ni les textes ; la proposition de renommage est au formulaire.
Dépend de TOK-120 (pont daté, `scripts/bridge_date.py`) et de TOK-122 (A4 : textes du simulateur déjà conformes au calcul).

Reproduire (≈ 4 min, graine 132) :

```
python scripts/diagnose_pont_simulateur.py --db <dépôt principal>/data/yugioh.db --out <dossier>
```

---

## La réponse en quatre phrases

1. **Un ban fait bien baisser la part de méta de ses archétypes porteurs** : −3,1 points de plus que des cartes non
   touchées de même popularité dans la même liste [−4,7 ; −1,5], sur 158 cartes touchées et 17 listes, et −5,5
   [−7,6 ; −2,8] quand on écarte les contrôles qui partagent un porteur avec une carte touchée. La mesure voit donc
   l'effet d'un ban : on peut s'en servir pour juger les deux outils.
2. **Le score de pont ne mesure pas un « impact »** : à part des decks égale, plus il est élevé, **moins** les porteurs de
   la carte perdent (coefficient +6,5 points par écart type [+4,5 ; +8,6]). Il ajoute bien de l'information à la part des
   decks hors échantillon (erreur quadratique −15 [−22 ; −8], 10 listes sur 12), mais dans le sens contraire de ce que dit
   l'onglet : une carte jouée par beaucoup d'archétypes est **diffuse**, et son ban se répartit sur des decks qui la
   remplacent.
3. **La « fragmentation » du simulateur** (intermédiarité datée) va dans le bon sens à part des decks égale (−1,9
   [−2,6 ; −1,0]) mais **n'améliore pas la prévision** hors échantillon (−1,6 [−5,9 ; +2,4], 7 listes sur 12).
4. **Les « archétypes voisins » du simulateur ne font pas mieux qu'une liste naïve** : seuls 229 noms sur 728 (31 %)
   existent comme archétype de deck (203 avec au moins 5 decks), parce que le simulateur lit `cards.archetype`
   (nomenclature YGOPRODeck) ; et les archétypes mesurables perdent en moyenne 25 % de leur part, contre 33 % pour les
   archétypes qui jouent le plus la carte (écart +0,08 [0,00 ; +0,19]).

**Recommandation** (formulaire) : renommer « Impact » en « Diffusion » et déclarer la formule ; décrire le simulateur comme
une description de la position de la carte dans le graphe, sans prévision, et remplacer ses « archétypes voisins » par
les archétypes de deck qui jouent la carte.

---

## Démarche (pour Thomas)

### Ce qu'affirment les deux outils

- **Onglet « Impact »** (`card_impact.bridge_score = n_archetypes × log(1 + decks)`) : « retirer une carte jouée par
  beaucoup d'archétypes fragmente plusieurs decks à la fois ».
- **Simulateur** (`POST /simulate-ban`) : une « fragmentation » (intermédiarité de la carte dans le graphe des
  co-occurrences, rapportée au maximum) et une liste d'« archétypes voisins » (archétypes des 30 cartes qui lui sont le
  plus associées, plus son archétype porteur, par ordre alphabétique, 10 au plus).

### La mesure

Pour chaque carte de chaque banlist du backtest :
- ses **archétypes porteurs** : les archétypes dont au moins la moitié des decks la jouent (fenêtre de 6 mois du Ban
  Radar, archétypes d'au moins 5 decks). Médiane : 2 porteurs par carte touchée ;
- la **variation** : part de méta cumulée de ces archétypes dans les 3 mois qui suivent l'entrée en vigueur, moins celle
  des 3 mois qui précèdent la coupure, en points (decks légaux du format).

Tous les prédicteurs sont calculés à la coupure, avec les seules données connues ce jour-là : part des decks, nombre
d'archétypes et nombre de decks viennent du classement de la veille (`backtest_lists`) ; la fragmentation et les voisins
viennent du graphe daté de TOK-120. Les listes dont les 3 mois suivants ne sont pas encore dans la base (TCG 2026-09-21
et 2026-10-19, OCG 2026-10-01) sont écartées : **17 listes, 164 cartes touchées classées, 158 avec au moins un porteur**.

### Les quatre questions, figées avant lecture

1. Le ban fait-il bouger la mesure ? (carte touchée contre cartes non touchées de la même liste et du même quintile de
   part des decks)
2. Corrélations de rang entre chaque prédicteur et la variation.
3. **Critère de gain** : prévoir la variation hors échantillon dans le temps (origine glissante ; une liste ne sert à
   l'entraînement que si ses 3 mois suivants sont écoulés avant la coupure de la liste testée ; 12 listes testées), avec
   la part des decks seule (méthode naïve) contre la part des decks + score de pont (ou + fragmentation). Gain si
   l'erreur baisse avec un intervalle bootstrap par liste à 90 % entièrement sous 0.
4. Simulateur : les archétypes voisins perdent-ils plus qu'une liste naïve de même taille (les archétypes qui jouent le
   plus la carte, en nombre de decks) ?

**Limite de cette règle, vue à la lecture** : le critère 3 ne fixait pas le **sens** attendu. L'affirmation « Impact »
en fixe un (à popularité égale, un score élevé ferait davantage baisser les porteurs). Le signe des coefficients a donc
été ajouté après coup (« Q3 bis » dans le script, déclaré comme tel) ; c'est lui qui tranche l'interprétation.

---

## Résultats

### Q1. Effet d'un ban sur ses porteurs

| | Cartes touchées | Listes | Variation des touchées | Contrôle (même liste, même quintile) | Effet [90 %] | Touchées en baisse |
|---|---|---|---|---|---|---|
| Ensemble | 158 | 17 | −6,8 pts | −3,7 pts | **−3,1** [−4,7 ; −1,5] | 78 % |
| OCG | 82 | 9 | −7,6 | −3,9 | −3,7 [−6,3 ; −1,5] | 82 % |
| TCG | 76 | 8 | −6,0 | −3,6 | −2,4 [−4,3 ; −0,2] | 74 % |

Le contrôle baisse aussi (−3,7 points) : les archétypes qui pèsent perdent du terrain en trois mois même sans ban
(retour vers la moyenne, nouvelles sorties). L'effet du ban est l'écart entre les deux.

**Contrôles contaminés** (relecture `data-scientist-ygo`) : 71 % des contrôles partagent un porteur avec une carte
touchée de la même liste, et subissent donc le ban eux aussi, ce qui tire l'effet vers 0. Sans eux : effet **−5,5**
[−7,6 ; −2,8] sur 91 cartes touchées et 14 listes (TCG −5,8 [−8,2 ; −2,3], OCG −4,9 [−9,0 ; −0,4]). L'effet réel est
probablement plus proche de cette valeur que de −3,1. Le data scientist trouve aussi −2,9 [−4,5 ; −1,4] avec un contrôle
apparié sur la part cumulée des porteurs avant le ban (retour vers la moyenne) : l'effet ne s'explique pas par la seule
taille des archétypes.

### Q2. Corrélations de rang avec la variation (cartes touchées ; négatif = dans le sens « impact »)

| Prédicteur | Variation (points) [90 %] | Variation relative (÷ part avant) [90 %] |
|---|---|---|
| Part des decks (naïve) | **−0,58** [−0,66 ; −0,50] | −0,03 [−0,15 ; +0,09] |
| Score de pont | −0,23 [−0,36 ; −0,10] | +0,12 [−0,03 ; +0,26] |
| Fragmentation | −0,24 [−0,35 ; −0,12] | −0,15 [−0,25 ; −0,07] |
| Nombre d'archétypes | −0,17 [−0,30 ; −0,04] | +0,15 [0,00 ; +0,30] |
| Score de pont − part des decks | +0,35 [+0,23 ; +0,47] | +0,14 [+0,02 ; +0,27] |
| Fragmentation − part des decks | +0,34 [+0,21 ; +0,48] | −0,13 [−0,27 ; +0,01] |

Seul, le score de pont est **moins** lié à la variation que la part des decks, et nettement (écart +0,35, intervalle
loin de 0). En variation relative, il change de signe.

### Q3. Prévision hors échantillon (origine glissante, 12 listes testées)

Erreur quadratique moyenne sur les cartes touchées des listes tenues à l'écart :

| Modèle | Erreur moyenne |
|---|---|
| Constante | 66,8 |
| Score de pont seul | 71,0 |
| Part des decks | 59,3 |
| Part des decks + fragmentation | 57,7 |
| Part des decks + score de pont | **44,4** |

| Comparaison | Écart [90 %] | Listes où le 1er fait mieux | Test du signe | Gain selon la règle |
|---|---|---|---|---|
| part + pont − part | −14,9 [−22,3 ; −7,7] | 10/12 | p = 0,04 | oui |
| part + fragmentation − part | −1,6 [−5,9 ; +2,4] | 7/12 | p = 0,77 | non |
| pont seul − part | +11,7 [+3,0 ; +18,9] | 2/12 | p = 0,04 | non |
| part − constante | −7,5 [−18,2 ; +4,6] | 9/12 | p = 0,15 | non |

### Q3 bis (ajouté après lecture). Le sens des coefficients

Régression de la variation sur la part des decks et un second critère, critères standardisés, variable de format,
toutes les cartes touchées, intervalle bootstrap par liste à 90 % (2 000 tirages).

| Modèle | Part des decks | Second critère | Sens attendu par « Impact » |
|---|---|---|---|
| part + score de pont | −9,0 [−10,9 ; −7,3] | **+6,5** [+4,5 ; +8,6] | négatif : **contraire** |
| part + fragmentation | −3,3 [−4,4 ; −2,3] | −1,9 [−2,6 ; −1,0] | négatif : conforme |
| part + nombre d'archétypes | −8,2 [−9,8 ; −6,6] | +5,7 [+4,1 ; +7,4] | négatif : contraire |

En variation relative : score de pont +0,28 [+0,16 ; +0,45] (contraire) ; fragmentation −0,08 [−0,13 ; −0,04]
(conforme, petit) ; hors échantillon, le score de pont baisse encore l'erreur (−0,027 [−0,048 ; −0,008], 9/12), la
fragmentation l'augmente (+0,030 [+0,003 ; +0,060]).

**Pourquoi le score de pont « aide » dans le mauvais sens.** Il est corrélé à 0,83 au nombre de porteurs. Une carte
jouée par beaucoup d'archétypes a beaucoup de porteurs, dont la part cumulée couvre une grande partie de la méta et ne
peut pas baisser beaucoup : les joueurs remplacent la carte et restent sur leur deck. Une pièce de moteur d'un seul deck
dominant, au contraire, fait chuter ce deck. Le score de pont mesure donc la **diffusion** d'une carte, et une carte
diffuse est celle dont le ban **déplace le moins** la méta de ses porteurs. C'est une propriété en partie mécanique de la
mesure (part cumulée de nombreux archétypes), mais elle suffit à contredire le libellé « Impact ».

### Q4. Le simulateur, archétypes voisins

- 158 cartes touchées, 728 noms d'archétypes listés par le simulateur, **229 (31 %) qui existent comme archétype de
  deck**, 203 (28 %) avec au moins 5 decks sur la fenêtre ; 22 cartes n'ont aucun nom mesurable. Le simulateur mélange
  deux nomenclatures : `cards.archetype` (YGOPRODeck, « Dogmatika ») et l'archétype des decks (yugiohmeta, « Branded »).
- Critère (corrigé après la relecture `data-scientist-ygo`) : **variation relative** de chaque archétype (variation ÷
  part avant), archétypes d'au moins 5 decks des deux côtés. La première version, en points, favorisait mécaniquement la
  liste naïve, faite des plus gros archétypes (un petit archétype ne peut pas perdre beaucoup de points).
- Sur les 136 cartes mesurables : les archétypes du simulateur perdent en moyenne **25 %** de leur part, ceux de la liste
  naïve de même taille **33 %** ; écart +0,08 [0,00 ; +0,19] : **le simulateur ne fait pas mieux que la liste naïve**
  (plutôt moins bien). En points : −5,2 contre −6,4 (écart +1,2 [+0,4 ; +2,3]) ; part des archétypes en baisse : 74 %
  contre 77 % (écart −0,02 [−0,05 ; +0,01]).
- Non testé : `community_id` (appariement par `LIKE` sur un nom d'archétype, fragile, signalé par l'audit) ; il ne
  prévoit rien de mesurable.

---

## Verdict selon la règle, et ce qu'il faut en retenir

| Outil | Règle figée (Q3 / Q4) | Sens (Q3 bis) | Conclusion |
|---|---|---|---|
| Score de pont (« Impact ») | gain | **contraire** | ne mesure pas un impact ; mesure la diffusion |
| Fragmentation (simulateur) | aucun gain | conforme, faible | pas de valeur prédictive démontrée |
| Archétypes voisins (simulateur) | aucun gain (pas mieux que la liste naïve, 28 à 31 % de noms mesurables) | — | à remplacer ou retirer |

Aucun des deux outils n'est validé comme prévision de l'effet d'un ban. La proposition de l'audit (« renommer en
diffusion si B3 échoue ») s'applique : le score de pont échoue sur le sens, le simulateur sur la règle.

---

## Relecture `data-scientist-ygo`

Méthode et chiffres relus ; effet de Q1 (−3,11) et coefficient de Q3 bis (+6,49) recalculés à l'identique ; aucune fuite
dans les fenêtres (« entrée en vigueur + 3 mois avant la coupure testée » correct). Deux corrections appliquées avant le
commit : Q4 en variation relative avec le même filtre des deux côtés, variante de Q1 sans contrôles contaminés. Réserves
retenues dans ce journal : somme nulle des parts de méta, « gain » de Q3 fragile en variation relative (9 listes sur
12, p = 0,15) et dû en partie à un effet suppresseur entre deux variables corrélées (la part des decks seule ne bat pas
la constante, 9 sur 12, p = 0,15). Recommandation : renommer « Impact » en « Diffusion ».

## Fuites de données

| Variable | Donnée | Connue à quelle date | Risque |
|---|---|---|---|
| Part des decks, nombre d'archétypes, decks, porteurs | classement de la veille (`backtest_lists`) | coupure | Préexistant : filtre sur `created` (voir TOK-120). |
| Fragmentation, voisins | graphe daté (`uploaded ≤ coupure`) | coupure | Aucun. |
| Variation | parts de méta 3 mois avant la coupure et 3 mois après l'entrée en vigueur | entrée en vigueur + 3 mois | C'est la cible. La coupure est la veille de l'entrée en vigueur : aucune journée n'échappe aux deux fenêtres. |
| Entraînement de l'origine glissante | listes dont la variation est connue avant la coupure testée | coupure | Aucun (une liste n'entre qu'à entrée en vigueur + 3 mois). |
| `cards.archetype` | table `cards` actuelle | aujourd'hui | Faible : la nomenclature YGOPRODeck d'une carte change rarement. |
| Choix d'analyse | 4 questions figées ; Q3 bis ajoutée après lecture | — | Déclaré. La règle de gain aurait dû fixer le signe ; c'est la leçon pour les prochains lots. |

---

## À relire par la collaboratrice

1. La définition des porteurs (coreness ≥ 0,5, archétypes d'au moins 5 decks, fenêtre de 6 mois) et de la variation
   (part cumulée, en points) ; la variante relative ; est-ce la bonne cible pour « impact » ? Une cible par liste
   (fragmentation de la méta, indice de Herfindahl) aurait-elle été plus juste ?
2. Le contrôle de Q1 (médiane des non-touchées de même liste et même quintile) et la variante sans contrôles contaminés
   (−5,5 ici, −4,8 dans le recalcul du data scientist, qui ne définit pas tout à fait le partage de porteurs de la même
   façon : à harmoniser).
3. L'origine glissante de Q3 (règle « entrée en vigueur + 3 mois avant la coupure ») et le bootstrap par liste (17 listes,
   cartes d'une même liste dépendantes, plusieurs cartes d'un même deck dans une liste).
4. Le fait que Q3 bis a été ajouté après lecture, et l'interprétation « diffusion » (part mécanique).
5. La liste naïve de Q4 (archétypes qui jouent le plus la carte, même taille que la liste mesurable du simulateur) et le
   critère relatif.
6. La réserve du data scientist : une part de méta est à somme nulle, elle ne peut pas voir un affaiblissement uniforme
   de nombreux archétypes. La conclusion est « l'impact concentré n'est pas confirmé, le score mesure la diffusion »,
   pas « aucun impact ».

## Sorties brutes

Tableaux recopiés de la sortie de `diagnose_pont_simulateur.py` (CSV : `cartes_touchees.csv`, `effet_du_ban.csv`,
`effet_du_ban_controles_propres.csv`, `correlations.csv`, `origine_glissante.csv`, `origine_glissante_relative.csv`, `gains.csv`, `coefficients.csv`,
`simulateur.csv`).
