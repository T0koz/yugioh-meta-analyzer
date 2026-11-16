# Moteur de combos — décisions à prendre (TOK-85, TOK-87)

> Formulaires à copier-coller. Ma recommandation est pré-cochée. Aucune de ces décisions ne demande
> de connaître les règles du jeu : celles qui en demandent sont dans `points-de-regle-a-valider.md`.

## D1 — Deck source du jeu de tests

Régional WCQ du 8 novembre 2026, top 4, 40 cartes, légal sous la liste d'octobre, à 20 jours du
changement de liste. Détail : `jeu-de-tests-branded.md` § 1.

```
D1 — Deck source
[x] Deck 6af240d2… (Džavid Berberović, régional du 08/11/2026, top 4, 40 cartes)
[ ] Deck 6addeee9… (2e le 24/10/2026, 41 cartes, mais à 5 jours du changement de liste)
[ ] Un vainqueur de septembre 2026 (1er, mais liste qui n'est plus en vigueur)
[ ] Plusieurs decks dès maintenant (plus de cartes à formaliser avant le premier résultat)
Commentaire libre :
```

## D2 — Deux niveaux : le « pas » et la « transition »

Le pas est une décision élémentaire (choisir une cible). La transition va d'un état stable au
suivant (une action complète avec sa chaîne). Le combo se lit en transitions ; la comparaison avec
l'oracle se fait en pas. Stocker les deux coûte plus de lignes, mais sans les pas on ne peut pas dire
**où** le moteur et l'oracle divergent.

```
D2 — Granularité
[x] Deux niveaux : pas (moteur, oracle) et transitions (combos)
[ ] Transitions seulement (plus simple, désaccords avec l'oracle plus durs à localiser)
[ ] Pas seulement (combos illisibles : 5 à 10 lignes par carte jouée)
Commentaire libre :
```

## D3 — Position des monstres sur le terrain

Deux cartes du deck lisent la position (`Sprind` : colonne ; `Albion the Sanctifire Dragon` : zones
centrales). Énumérer les 5 zones à chaque invocation multiplie les états pour presque rien.

```
D3 — Zones
[x] L'état porte toujours la zone ; le moteur place par défaut (première zone libre) et n'énumère
    les placements que si une carte du deck lit la position. Hypothèse à faire confirmer par le juge.
[ ] Énumérer toutes les zones, toujours (exact sans hypothèse, beaucoup plus d'états)
[ ] Ignorer les zones dans le pilote (les effets de Sprind et d'Albion deviennent « non couverts »)
Commentaire libre :
```

## D4 — Actions légales mais sans intérêt

Annuler son propre effet avec `Ash Blossom`, défausser `Mulcharmy Fuwalos` à son propre tour : c'est
légal, et « le système recense sans juger ». Mais chaque carte de ce type double le nombre de lignes.

```
D4 — Actions sans intérêt
[x] Le moteur les déclare légales ; l'exploration peut les écarter par des filtres DÉCLARÉS,
    enregistrés avec le résultat (cb_run.filters_json). L'exhaustivité s'entend « à filtres près ».
[ ] Tout explorer, toujours (fidèle à la lettre des décisions, explosion du nombre de lignes)
[ ] Les interdire dans le moteur (plus simple, mais le moteur ne dit plus la règle)
Commentaire libre :
```

## D5 — Propagation du « non couvert »

Que rendre quand une carte sans texte (4 dans ce deck) ou non formalisée est en jeu ?
Détail : `definitions-et-schema.md` § 3.4.

```
D5 — Non couvert
[x] Trois niveaux : action sur la carte → « non couvert » ; carte qui pourrait agir → la branche
    s'arrête, exploration marquée incomplète ; zone qui la contient → liste « peut-être incomplète »
[ ] Strict : dès qu'une carte non couverte est dans le deck, aucun résultat (rien d'affichable
    tant que le deck n'est pas couvert à 100 %)
[ ] Souple : ignorer la carte, sans marquage (contraire à « n'afficher que ce qui est démontré »)
Commentaire libre :
```

## D6 — Statuts de formalisation

Le ticket en cite quatre, les décisions du 16/11 trois. Je propose la réunion des deux.

```
D6 — Statuts
[x] Cinq : non_traitee, brouillon, formalisee, verifiee, non_formalisable
[ ] Trois, comme dans les décisions : formalisee, verifiee, non_formalisable
[ ] Quatre, comme dans le ticket : non_traitee, brouillon, verifiee, non_formalisable
Commentaire libre :
```

## D7 — Format du jeu de tests

```
D7 — Format
[x] YAML écrit à la main (tests-branded.yaml), état d'arrivée en texte libre pour l'instant,
    à formaliser quand le schéma (D2, D3) est validé
[ ] Formaliser l'état d'arrivée tout de suite (risque de tout réécrire si D2 ou D3 change)
[ ] Tests en Python (pytest) directement (lie le jeu de tests à un moteur qui n'existe pas)
Commentaire libre :
```

## D8 — Les quatre cartes sans texte : ✅ fait le 16 novembre 2026

Décision de Thomas : relancer `fetch_cards.py`. Fait : 288 cartes nouvelles insérées, un nom corrigé
(`The Fallen &amp; The Virtuous`). Détail dans `jeu-de-tests-branded.md` § 1. Reste une décision :

```
D8 bis — Garder `cards` à jour
[x] Ajouter au job du lundi une étape « cartes nouvelles seulement » (insertion sans réécriture),
    et corriger init_db.py qui duplique card_sets à chaque relance
[ ] Rafraîchir toute la table chaque lundi (met aussi à jour views_week et les statuts de banlist ;
    à décider avec le data scientist, car le signal précoce lit views_week)
[ ] Rester manuel
Commentaire libre :
```

## D9 — Commit

```
D9 — Commit sur la branche claude/combos-preparation-987ed6 (pas de push)
[x] Un seul commit : « docs(TOK-85, TOK-87): définitions, schéma et jeu de tests Branded du moteur de combos »
[ ] Deux commits (TOK-85 puis TOK-87)
[ ] Ne pas committer maintenant
Commentaire libre :
```
