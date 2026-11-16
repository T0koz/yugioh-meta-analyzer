# TOK-74 — Kewl Tune est-il entré dans le méta TCG comme annoncé ? (2026-11-16)

Reproductible : `python scripts/analyze_signal_outcome.py` (lecture seule).
Sources : `tournament_decks` + `deck_legality` (decks légaux à la date du tournoi),
`boutique_buy_signals` (sauvegarde `data/backup_avant_nettoyage_20261116.db`, signal du 2026-06-17),
`card_price_history` (colonne `cardmarket_price`). **Tout ce qui suit est VÉRIFIÉ** (commande lancée) sauf mention.

## Verdict : le signal est défavorable, et sa prémisse était fausse

> Le signal annonçait une « entrée TCG estimée : octobre 2026 ». Or Kewl Tune **jouait déjà
> 22-32 % des decks TCG légaux de mai à juillet 2026**, avant même le signal de juin. Il n'y a
> pas eu d'entrée en octobre : il y a eu un déclin, puis une quasi-disparition.

| Mois | TCG : decks légaux | TCG : % Kewl Tune | OCG : % Kewl Tune |
|---|---|---|---|
| 2026-05 | 405 | 22,5 | 17,6 |
| 2026-06 | 281 | 26,7 | 25,1 |
| 2026-07 | 131 | 32,1 | 11,6 |
| 2026-08 | 272 | 19,9 | 9,9 |
| 2026-09 | 519 | **8,9** | 6,8 |
| 2026-10 | 240 | **0,4** | 1,1 |
| 2026-11 (au 14) | 156 | **0,0** | 2,1 |

Le déclin suit la banlist : `Kewl Tune Rotary` passe **Forbidden en TCG le 2026-09-21** (liste
reconduite le 2026-10-19), et quatre cartes Kewl Tune sont Limited en OCG le 2026-10-01
(`banlist_history`). Le « décalage OCG → TCG de 4 mois » n'explique rien ici : l'archétype
était présent dans les deux formats en même temps, puis frappé par la banlist.

## Prix : les cartes du signal ont baissé, le marché non

Variation Cardmarket du 2026-06-19 au 2026-11-16, cartes à **≥ 1 € au départ** :

| Groupe | n cartes | Variation médiane |
|---|---|---|
| Marché (toutes cartes ≥ 1 €) | 1 244 | **−0,8 %** |
| Cartes du signal du 17 juin | 34 | **−34,8 %** (IC95 bootstrap de l'écart : −50 % à +1 %) |
| dont Kewl Tune (6 cartes) | 6 | −54,7 % (Fydraulis Harmonia −37 %, Kewl Tune Synchro −85 %) |

Par archétype (médiane) : Kewl Tune −55 %, DoomZ −67 %, Elfnote −53 %, Chaos Ritual −43 %,
mais Branded +36 %, Sky Striker +4 %, Radiant Typhoon +9 %, Maliss −5 %, Power Patron −1 %.
La médiane des médianes par archétype est de −8,6 % (10 archétypes) : **le résultat est tiré par
4 archétypes**, dont celui qui a été banni.

## Limites (à ne pas oublier avant de conclure)

- **Une seule date de signal** (2026-06-17) : aucune répétition, donc aucune notion de fiabilité.
- **34 cartes** (sur 109 distinctes) passent le filtre ≥ 1 € ; elles sont regroupées en 10
  archétypes, donc non indépendantes. L'IC de l'écart au marché frôle zéro (borne haute +1 %).
- Prix = snapshots Cardmarket ponctuels, pas des ventes ; un prix qui baisse n'est pas une perte
  pour une boutique qui aurait acheté tôt et revendu tôt (aucune donnée sur les ventes).
- Les 75 cartes à moins de 1 € ont une variation médiane de ~0 % (bruit des centimes).
- Le signal de juin a été produit sur des decks filtrés par le drapeau `illegal` biaisé de l'API
  (voir TOK-72) : on ne peut pas dire ce qu'il aurait donné sur les données corrigées.

## Conclusion honnête

Sur la seule observation disponible, **le signal d'achat « Kewl Tune » a été perdant**, pour une
raison que le modèle ne pouvait pas voir : une banlist. Ce n'est pas une réfutation statistique
(n = 1), mais ce n'est certainement pas une validation, et le chiffre « Kewl Tune 100/100 »
ne doit plus être présenté comme un succès. Voir TOK-73 pour la robustesse du signal OCG → TCG.
