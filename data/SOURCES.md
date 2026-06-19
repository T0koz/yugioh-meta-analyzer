# Sources de données — Yu-Gi-Oh! Meta Analyzer

## 1. YGOPRODeck API v7
**URL :** `https://db.ygoprodeck.com/api/v7/cardinfo.php`
**Ce qu'on récolte :** 13 797 cartes TCG avec stats, archetype, banlist, prix, images, dates de sortie, popularité (views/views_week).
**Script :** `scripts/fetch_cards.py` → `data/raw/cards.json` → `scripts/init_db.py` → tables `cards`, `card_sets`, `card_prices`
**Prix quotidiens :** `scripts/snapshot_prices.py` (cron 9h, 1 appel bulk) → `card_price_history`
**Images :** `https://images.ygoprodeck.com/images/cards/{id}.jpg` — stockées dans `cards.image_url`
**Archetypes officiels :** `/archetypes.php` → `archetypes_official` (640 archetypes)
**Fréquence :** Relancer à chaque nouvelle banlist ou sortie de set.

---

## 2. yugiohmeta.com — Decklists de tournoi
**URL :** `https://www.yugiohmeta.com/api/v1/top-decks`
**Ce qu'on récolte :** Decklists complètes (main/extra/side) des top-coupés depuis 2024-01-01.
- TCG : `ocg[$ne]=true` → 9 330 decklists (`scripts/fetch_tournament_decks.py`)
- OCG : `ocg=true` → 10 558 decklists (`scripts/fetch_ocg_decks.py`)
- Total : **19 888 decklists**, **852 405 entrées deck_cards**
**Tables :** `tournament_decks`, `deck_cards`
**Fréquence :** Hebdomadaire pour rester à jour sur la méta.

---

## 3. yugiohmeta.com — Tier List
**URL :** `https://www.yugiohmeta.com/api/v1/tier-list`
**Ce qu'on récolte :** Classement T1/T2/T3/field par archetype.
**Table :** `meta_tier_list` (47 archetypes, scrapé dans `10_boutique_alert_score.ipynb`)

---

## 4. Yugipedia — Banlist historique
**URL :** `https://yugipedia.com/wiki/...`
**Ce qu'on récolte :** Toutes les banlists TCG depuis 2002, avec dates effective/fin et statuts carte par carte.
**Table :** `banlist_history` (11 890 entrées), scrapé dans `09_banlist_history.ipynb`
**Features dérivées :** `banlist_features` (3 660 lignes archetype × mois × statuts)

---

## 5. YouTube — Transcripts combos
**Source :** Chaînes combo guide Yu-Gi-Oh! (via `youtube_transcript_api`)
**Ce qu'on récolte :** Séquences de cartes jouées dans les combo guides vidéo.
**Traitement :** Blacklist 64 termes, ASR corrections (Cool Tune → Kewl Tune), graphe orienté A→B→C
**Tables :** `combo_mentions` (598), `combo_edges` (155), `combo_edges_global` (117)
**Notebook :** `08_nlp_combos.ipynb`

---

## Schéma global des données

```
YGOPRODeck API
    ├── cards.json (fetch_cards.py)
    │   └── yugioh.db
    │       ├── cards              (13 797 — avec images)
    │       ├── card_sets          (43 145)
    │       └── card_prices        (13 797)
    └── snapshot_prices.py (cron 9h)
        └── card_price_history     (27 620+, croît chaque jour)

yugiohmeta.com
    ├── fetch_tournament_decks.py (TCG)
    ├── fetch_ocg_decks.py (OCG)
    │   └── tournament_decks       (19 888)
    │       └── deck_cards         (852 405)
    └── tier-list (notebook 10)
        └── meta_tier_list         (47)

Yugipedia (scraping)
    └── banlist_history            (11 890)
        └── banlist_features       (3 660 — features ML)

YouTube (youtube_transcript_api)
    └── combo_mentions / combo_edges / combo_edges_global
```
