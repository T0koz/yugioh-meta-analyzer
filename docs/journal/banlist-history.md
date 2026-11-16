### `banlist_history` — scraping scripté, TCG + OCG

`scripts/fetch_banlist_history.py` remplace le notebook 09 pour cette table
(le notebook reste la source de `banlist_features`). Il reconstruit la table
intégralement à chaque exécution : Yugipedia est la source de vérité et amende
les listes passées rétroactivement.

Deux changements par rapport au notebook :
- **Les listes OCG sont scrapées** (catégorie `OCG Forbidden & Limited Lists`,
  87 listes). C'est ce qui a débloqué le second point de backtest du Ban Radar.
  La catégorie contient aussi des sous-catégories régionales (coréen, chinois
  simplifié…) qu'il faut filtrer — ce ne sont pas des listes.
- **Une colonne `format`** ('TCG' / 'OCG'). Le filtre historique
  `list_name LIKE '%TCG%'` laissait de côté 33 listes TCG antérieures à 2021 que
  Yugipedia nomme sans suffixe (« September 2020 Lists »). Ne plus filtrer sur
  le nom de la page.

État au 2026-08-14 : 23 995 lignes, TCG jusqu'au 2026-05-18, OCG jusqu'au
2026-07-01.

**Sur la banlist TCG en vigueur :** YGOPRODeck (`?banlist=tcg`) renvoie 5 cartes
de moins que la liste du 18 mai — Ext Ryzeal, Maliss P Dormouse, Maliss P White
Rabbit, Maliss Q White Binder et Number 89: Diablosis the Mind Hacker, toutes
assouplies. Mais **Yugipedia n'a aucune liste TCG après le 18 mai**. C'est donc
plus probablement une dérive de la donnée YGOPRODeck qu'une nouvelle banlist.
Dans les deux cas : aucune nouvelle restriction TCG, donc aucun point de
backtest supplémentaire de ce côté.
