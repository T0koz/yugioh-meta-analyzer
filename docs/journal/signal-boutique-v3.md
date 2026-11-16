### 🛒 Signal boutique v3 (TOK-113, 2026-11-16)

Correctif **à la source** des deux défauts trouvés par TOK-97. Chaîne : notebook 10 → `boutique_alerts`,
`boutique_card_alerts`, `ocg_archetype_scores` → `build_buy_signals.py` → `boutique_buy_signals`.

- **Règle « pas encore en TCG » sur les cartes, pas sur le nom** : archétype retenu si ≥ 5 decks OCG légaux sur 3 mois
  et ≥ 3 cartes clés jamais sorties en TCG (ni vues dans un deck TCG, Genesys inclus, ni `cards.tcg_date` passée).
  La règle par nom (< 5 decks TCG sur 12 mois) gardait 55 archétypes sur 94, dont 40 avec moins de 3 cartes inédites :
  vieux archétypes TCG faibles (Labrynth, Runick), hybrides (Elfnote existe sous 6 noms en TCG). Toon et Witchcrafter,
  gardés par le filtre de l'API, sont joués en TCG depuis le 2026-11-14 sous d'autres noms.
- **Résultat au 2026-11-16** : 3 archétypes (Raise Moon 100, Trirealm Rift 56,6, Harpie/Amazoness 44,0), 42 cartes
  clés dont 30 inédites, **12 signaux d'achat : Fort 3, Modéré 5, Faible 4**. Seules les cartes déjà cotées ressortent.
- **`tcg_entry_estimated` n'existe plus** (c'était date du calcul + 4 mois). Remplacé par `tcg_window_start` /
  `tcg_window_end` : médiane du premier deck OCG des cartes inédites + 75 à 202 jours (P10-P90 du délai
  `cards.ocg_date` → `tcg_date` sur 1 897 cartes 2022-2025, médiane 103 jours). C'est un intervalle à 80 %, **non validé
  hors échantillon**. Une date par archétype n'est pas défendable (30 cas, 1 à 10 mois, 37 % jamais arrivés).
- **Staples** : decks TCG légaux, 12 mois, > 20 % des decks **et** ≥ 30 archétypes (24 cartes). À 6 mois, le seuil
  attrape les pièces de moteur des decks dominants (Fydraulis Harmonia, Medius the Pure). Même filtre côté OCG (10 cartes,
  dont Maxx "C") : la garde ≥ 30 archétypes y est indispensable, sinon 9 cartes Elfnote passent pour des staples.
- **Cartes interdites** : lues dans `banlist_history` (liste TCG en vigueur, 156) et plus dans `cards.ban_tcg` (116,
  figé au dernier `fetch_cards.py`). 4 cartes interdites étaient proposées à l'achat.
- **Date de référence = dernier deck chargé**, une seule borne OCG pour tout le notebook (plus de `date('now')`).
- **`ocg_archetype_scores`** (nouvelle table, 89 archétypes) : force OCG de **tous** les archétypes. Le notebook 11 la
  lit pour `signal_ocg` ; il lisait `boutique_alerts`, qui ne contient plus que 3 archétypes. Effet sur
  `early_card_signals` : Spearman 0,9996, top 50 identique.
- **Journal** : `BOUTIQUE_MODEL = unreleased-cards-v3`, `target_date` = mois de fin de fenêtre (NULL si la source n'a
  pas de fenêtre : on ne journalise jamais une échéance non calculée). `EARLY_MODEL` = v3. Les lignes boutique v1/v2
  restent (ajout seul) et `validate_predictions.py` les évalue **à part**, statut `évaluée_horizon_fixe`. Une ligne v3
  est jugée sur `arrived` : ≥ 5 decks TCG dont le nom contient l'archétype avant la fin de la fenêtre.
- `app.py` (Streamlit) affiche la fenêtre. `backend/app/routers/boutique.py` est repris tel quel de
  `claude/refonte-front-cbe8af` ; son filtre par nom, qui faisait double emploi, a été retiré sur cette branche.

Limites connues, à ne pas présenter comme résolues :
- **Fort / Modéré / Faible sont relatifs au premier du lot** (`alert_norm` et `buy_score_100` divisés par le maximum) :
  il y a toujours un « Fort ». Aujourd'hui ce sont des génériques à moins de 0,50 € jouées par Raise Moon.
- **`cards` date du 2026-06-13** : `views_week` (moitié de la formule) est figé, et `fetch_cards.py` n'interroge que
  `format=tcg`. Les cartes inédites n'ont donc pas de vues : la moyenne se fait sur les seules cartes connues.
- Une générique peut sortir sous deux archétypes (Pot of Desires). « Harpie/Amazoness » est un nom hybride : son
  arrivée en TCG sous un autre nom serait manquée par le validateur.
- La fenêtre est servie par `GET /boutique/signals` et affichée sur la page boutique et l'accueil (dans `main` depuis
  la fusion de la refonte front, 2026-11-16).
- La base réelle est en schéma v3 depuis le 2026-11-16 et la branche est fusionnée dans `main` le même jour. Une
  branche antérieure à cette fusion qui lit `tcg_entry_estimated` répond 500 sur `/boutique/signals`.
  Sauvegardes : `data/backup_avant_boutique_v3_20261116.db`, `data/backup_serving_avant_boutique_v3_20261116.db`.
