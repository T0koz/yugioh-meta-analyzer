# Backtest des signaux précoces contre « vues seules » (TOK-129, B2, Jalon 1, 2026-11-18)

Branche `claude/j1-tok-129-93-signaux-fraicheur-d1344d`. Diagnostic seulement : aucune base écrite, rien d'affiché ne
change, `early_card_signals` et ses poids intacts. Dépend de TOK-122 (lot 20 : `scripts/build_early_signals.py`, rejoué
ici à des dates passées). Relu par `data-scientist-ygo` (méthode, fuites, dépendance, chiffres) ; ses corrections sont
intégrées au script.

## En clair (pour Thomas)

1. On a rejoué la page « signaux précoces » le 1er de chaque mois de juillet 2024 à juillet 2026 (25 dates), avec les
   seules données connues à chaque date, et compté combien des 20 premières cartes sont ensuite entrées en méta TCG
   (au moins 3 % des decks dans les 4 mois).
2. **Le critère du ticket est rempli sur le papier** : 54 % des 20 premières cartes du score entrent en méta, contre 38 %
   pour le classement par vues seules et 8 % au hasard ; écart +15 points, intervalle [+7 ; +25].
3. **Mais l'écart ne résiste pas à un comptage honnête.** Les 25 dates se ramènent à environ 8 épisodes (un archétype
   fort en OCG qui arrive en TCG : Ryzeal/Maliss, Dracotail/Yummy, Kewl Tune/Elfnote…). Le score gagne parce qu'il met
   dans son top 20 beaucoup de cartes du même archétype qui arrive. Compté par archétype, l'écart avec les vues est nul
   (+3 points, intervalle [−6 ; +12]). Sans l'épisode Dracotail/Yummy, il tombe à +7 points.
4. **Le seul signal solide est la force OCG de l'archétype**, sans les vues : elle désigne l'archétype qui arrive. 66 %
   des archétypes de son top 20 ont au moins une carte qui entre en méta, contre 39 % pour les vues (+27 points,
   intervalle par épisodes [+11 ; +43], 7 épisodes sur 8).
5. **La proximité de texte fait baisser le score** (−11 points quand on l'ajoute à la force OCG). Les vues n'apportent
   aucun gain démontré : celles dont on dispose datent toutes du 13/06/2026, elles viennent donc du futur pour les dates
   passées (fuite qui les avantage).
6. À la seule date sans fuite (13/06/2026, vues du même jour), il n'y a rien à mesurer : 7 cartes sur 288 sont entrées en
   méta, aucune méthode ne dépasse 2 réussites sur 20.
7. **Recommandation : revoir la page**, ni la garder telle quelle ni la masquer. Afficher les archétypes classés par la
   force OCG (et leurs cartes, sans rang), après un backtest propre à ce classement. Formulaire en fin de
   `docs/planning/2026-11-18/decisions-prises.md`.

## Commande

```bash
python scripts/backtest_early_signals.py                 # ≈ 35 s, lecture seule, graine 20261118
python scripts/backtest_early_signals.py --verifier      # contrôle de reproduction du calcul servi
python scripts/backtest_early_signals.py --json sortie.json
```

Dans un worktree : `--db <dépôt principal>/data/yugioh.db`. Les vues datées viennent de `data/raw/cards.json`, suivi par
Git depuis le commit `cc9b27d` du 13/06/2026.

## Définitions figées avant la première exécution

Écrites dans la docstring du script avant tout calcul de résultat.

- **Classement rejoué** : celui de `build_early_signals.py` (lot 20), reconstruit à la date t : fenêtres de sortie
  TCG 168 j / OCG 380 j, carte sortie au plus tard à t, banlist TCG en vigueur à t (Forbidden et Limited exclues),
  cartes déjà en méta exclues (≥ 3 % des decks TCG légaux des 90 j avant t), archétypes méta tirés des mois entièrement
  écoulés, force OCG recalculée à t (notebook 10, decks OCG légaux des 3 mois avant t). Poids inchangés.
- **Entrer en méta** : la carte est jouée (toutes zones) dans au moins 3 % des decks TCG légaux de ]t ; t + 120 j].
  C'est le seuil « déjà en méta » du lot 20 (seuil T3 de la tier list) : une carte signalée « avant la méta » réussit si
  elle franchit ce seuil dans les 4 mois. Sensibilité fixée d'avance : 1 %.
- **Mesure** : precision@20, égalités départagées en espérance.
- **Bases naïves** : « vues seules » (`views_week`) et hasard (taux de base) ; pour information, « déjà un peu joué »
  (part des 90 j avant t, sous 3 %) et force OCG seule.
- **Origines** : 25 dates glissantes (le 1er du mois, 2024-07 à 2026-07 ; t + 120 j reste avant le dernier deck du
  14/11) ; une origine propre, le 13/06/2026.
- **Critère (brief B2)** : écart moyen score − vues > 0 et intervalle bootstrap par date à 95 % qui exclut 0.

Ajouté **après** la première exécution, déclaré : variantes sans vues, formule servie sans texte, comptages par archétype,
bootstrap par épisodes (découpage en 8 épisodes posé après lecture des résultats), autocorrélation et effectif efficace.

**Contrôle de reproduction** (`--verifier`) : à la date du dernier deck (2026-11-14), avec les vues de la base, le
classement reconstruit redonne les 263 cartes de `early_card_signals`, les mêmes 20 premières (deux voisines inversées)
et les mêmes 50 premières ; écart maximal de score 0,0002, dû à l'arrondi à 4 décimales du script servi. La force OCG
recalculée redonne `ocg_archetype_scores` (89 archétypes, écart 0,00 point sur 100, Spearman 0,9999).

## Résultats

### Origines glissantes (25 dates, seuil 3 %)

N = 287 à 430 cartes notées par date, 6 à 54 entrées en méta (734 couples carte-date en tout).

| Méthode | P@20 moyenne |
|---|---|
| Score rejoué (vues 0,35 + texte 0,35 + force OCG 0,30) | 0,536 |
| Vues seules | 0,382 |
| Hasard (taux de base) | 0,080 |
| « Déjà un peu joué » (part des 90 j avant t) | 0,286 |
| Force OCG (avec les vues des cartes clés, comme servie) | 0,586 |
| Force OCG sans vues | 0,583 |
| Score sans vues (texte + force OCG sans vues) | 0,477 |
| Formule servie au lot 20, texte nul (vues + force OCG) | 0,624 |
| Vues + force OCG sans vues | 0,619 |

Écarts (IC à 95 % : bootstrap par dates ; bootstrap par épisodes ; épisodes devant / derrière) :

| Écart | Comptage | Moyenne | IC dates | IC épisodes | Épisodes |
|---|---|---|---|---|---|
| Score − vues | cartes | **+0,154** | [+0,066 ; +0,252] | [+0,017 ; +0,325] | 5 / 2 |
| Score − vues | par archétype | +0,026 | [−0,033 ; +0,087] | [−0,063 ; +0,119] | 4 / 4 |
| Score − vues | au plus 3 réussites par archétype | −0,032 | [−0,094 ; +0,034] | [−0,123 ; +0,054] | 4 / 4 |
| Force OCG sans vues − vues | cartes | +0,201 | [+0,087 ; +0,316] | [+0,023 ; +0,374] | 6 / 1 |
| Force OCG sans vues − vues | archétypes touchés | **+0,272** | [+0,166 ; +0,380] | [+0,114 ; +0,430] | 7 / 1 |
| Score − force OCG sans vues | cartes | −0,047 | [−0,116 ; +0,016] | [−0,143 ; +0,029] | 2 / 6 |
| Score sans vues − force OCG sans vues (effet du texte) | cartes | **−0,106** | [−0,181 ; −0,038] | [−0,212 ; −0,018] | 2 / 6 |
| Score − (vues + force OCG sans vues) (effet du texte) | cartes | −0,083 | [−0,145 ; −0,022] | [−0,179 ; −0,010] | 2 / 6 |
| Vues + force OCG sans vues − force OCG sans vues | cartes | +0,036 | [+0,001 ; +0,072] | [+0,004 ; +0,070] | 5 / 2 |

- **Dépendance** : autocorrélation de l'écart score − vues +0,59 à un mois ; effectif efficace ≈ 6,5 dates sur 25.
  Le bootstrap par épisodes est la version honnête ; avec 8 grappes, il reste optimiste.
- **Critère B2 : rempli** en comptant les cartes (IC par dates [+0,066 ; +0,252], par épisodes [+0,017 ; +0,325]).
  **Non robuste** : nul en comptant les archétypes, porté à environ 60 % par l'épisode Dracotail/Yummy (sans lui : +0,069).
- **Les vues** : le gain de +0,036 qu'elles ajoutent à la force OCG est une borne haute, puisque les vues viennent du
  futur. Mesure de la fuite (relecture) : aux dates de 2024-07 à 2025-06, les cartes entrées en méta et encore jouées au
  printemps 2026 ont une médiane de ≈ 2 875 vues, celles qui ne sont plus jouées ≈ 1 166, les autres ≈ 282 ; AUC des vues
  0,87 en moyenne sur les dates glissantes contre 0,75 à 0,81 aux dates sans fuite.
- Seuil de sensibilité 1 % : même sens (score − vues +0,126, IC dates [+0,032 ; +0,222]).

### Origine propre (13/06/2026, vues du même jour)

N = 288, K = 7 entrées en méta (hasard 0,024), 1 109 decks après. Score 2 réussites sur 20 (0,10, les deux de l'archétype
Artmage), vues 1 sur 20 (0,05, l'une des deux du score). Écart +0,05, intervalle indicatif [−0,10 ; +0,15] (bootstrap sur
les cartes, avec doublons et égalités). Au seuil de 1 %, l'ordre s'inverse : vues 0,40, score 0,15. **Pas exploitable
comme test** : aux trois dates les plus récentes (2026-06-01, 06-13, 07-01 ; 7 à 11 entrées), aucune méthode ne dépasse
0,25. Sans arrivée d'un archétype OCG fort, il n'y a rien à prédire au niveau des cartes.

### Liste archivée du 17/06/2026 (journal `prediction_log`, `early_card`, provenance `backfill`)

Copie archivée le 01/11 du classement d'avant le lot 20, pas une preuve datée. P@20 0,85, comme les vues seules (0,85),
mais 18 des 20 cartes étaient déjà en méta le 17/06 ; parmi les 2 autres, 1 est entrée en méta (0,05).

## Fuites et biais (relecture `data-scientist-ygo`)

| Source | Verdict |
|---|---|
| Vues du 13/06/2026 | Fuite forte, déclarée ; avantage les méthodes à proportion de leur poids de vues (vues seules 100 %, score ≈ 34 %) |
| Cartes OCG anciennes admises par une date TCG future | Négligeable (0 à 16 cartes par date ; moyennes +0,01 sans elles) |
| `created` au lieu de `uploaded` | Négligeable (force OCG sans vues 0,583 → 0,585) |
| `meta_scores`, `deck_legality`, `text_synergies` (texte seul) | Pas de fuite |
| Noms d'archétypes OCG hybrides (« Vanquish Soul K9 ») non appariés | Biais **contre** la force OCG (11 à 31 % des decks du top 10 OCG), pas une fuite |

Poids effectifs moyens du score rejoué (poids × écart type) : vues 34 %, texte 32 %, force OCG 33 %. Le calcul servi au
lot 20 a un texte nul (`text_synergies` hors chaîne) : il vaut en pratique vues + force OCG (0,624 ici). **Ce qui est servi
n'est donc pas exactement ce qui est testé** : si `text_synergies` est recalculée, le texte revient et coûte ≈ 0,1.

## Constats en passant

- `build_early_signals.py` garde des cartes **pas encore sorties** à la date de référence (3 cartes OCG annoncées pour le
  16/02/2027 dans la table actuelle) ; le backtest les exclut (`strict=True`).
- La fenêtre des archétypes méta du script servi compare `month` (« AAAA-MM ») à « AAAA-MM-01 » : le premier mois de la
  fenêtre est toujours écarté. Reproduit tel quel.

## Ce que la collaboratrice devra relire

- La définition « entrer en méta » (3 % sur 120 jours) et le choix de la precision@20 en cartes plutôt qu'en archétypes.
- Le découpage en 8 épisodes, posé après lecture des résultats, et le bootstrap par grappes avec 8 grappes.
- Le chiffrage de la fuite des vues (médianes, AUC) et la lecture « vues : aucun gain démontré ».

## Suites proposées (au formulaire)

1. Mettre le poids du texte à 0 (changement de scoring déclaré).
2. Classement d'archétypes par la force OCG, avec son propre backtest figé d'avance (unité archétype × date, part TCG
   de l'archétype sur 120 j, bases : part OCG seule et archétypes déjà annoncés en TCG, bootstrap par épisodes).
3. Archiver `views_week` chaque lundi : un vrai test des vues deviendra possible dans 6 à 12 mois.
4. La force OCG est presque le rang déjà affiché sur `/boutique` (ρ 0,94 avec la part OCG, audit) : fusionner ou renvoyer.
5. Apparier les noms d'archétypes hybrides (changement décidé après lecture : à valider sur des dates tenues à l'écart).
