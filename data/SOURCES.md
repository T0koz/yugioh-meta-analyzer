# Sources de données — Yu-Gi-Oh! Meta Analyzer

## 1. YGOPRODeck API v7
**URL :** `https://db.ygoprodeck.com/api/v7/cardinfo.php`
**Ce qu'on récolte :** Toutes les cartes TCG (13 797) avec leurs stats, archetype, banlist, prix, dates de sortie, popularité (views).
**Comment :** Appel HTTP simple avec `requests`. Un seul appel suffit pour tout récupérer.
**Script :** `scripts/fetch_cards.py` → `data/raw/cards.json` → `data/yugioh.db` (tables `cards`, `card_sets`, `card_prices`)
**Fréquence :** À relancer à chaque nouvelle banlist ou sortie de set.

---

## 2. YGOPRODeck — Banlist
**URL :** Inclus dans l'API v7 (`banlist_info` dans la réponse)
**Ce qu'on récolte :** Statut TCG/OCG/Goat de chaque carte (Banned, Limited, Semi-Limited).
**Comment :** Automatiquement récupéré avec les cartes (champ `ban_tcg`, `ban_ocg`, `ban_goat`).
**Stockage :** Colonnes `ban_tcg`, `ban_ocg`, `ban_goat` dans la table `cards`.

---

## 3. YGOPRODeck — Sets
**URL :** Inclus dans l'API v7 (`card_sets` dans la réponse)
**Ce qu'on récolte :** Dans quels boosters chaque carte est sortie, avec code, rareté et prix.
**Comment :** Automatiquement récupéré avec les cartes.
**Stockage :** Table `card_sets`.

---

## 4. yugiohmeta.com — Decklists de tournoi
**URL :** `https://www.yugiohmeta.com/api/v1/top-decks`
**Ce qu'on récolte :** Decklists complètes (main/extra/side) des joueurs ayant top-coupé des tournois TCG, avec archetype, placement, tournoi, lieu, date.
**Comment :** API JSON non documentée mais publique, découverte via interception réseau Playwright. Appels paginés avec `requests`.
**Script :** `scripts/fetch_tournament_decks.py` → `data/yugioh.db` (tables `tournament_decks`, `deck_cards`)
**Fréquence :** À relancer chaque semaine pour rester à jour sur la méta.

---

## 5. yugiohmeta.com — Tier List *(à venir)*
**URL :** `https://www.yugiohmeta.com/api/v1/tier-list` *(à confirmer)*
**Ce qu'on récoltera :** Classement des archetypes par tier (S, A, B, C) mis à jour quotidiennement.
**Comment :** Même approche que les decklists.
**Script :** `scripts/fetch_tier_list.py` *(à créer)*

---

## 6. YouTube / Transcripts *(Phase 4)*
**Sources :** Chaînes de tournoi Yu-Gi-Oh! (DuelLogs, Play TCG, etc.)
**Ce qu'on récoltera :** Séquences de combo extraites des commentaires de gameplay (ordre des cartes jouées).
**Comment :** Whisper (OpenAI) pour transcrire les vidéos, regex pour détecter les noms de cartes.
**Script :** `scripts/transcribe_combos.py` *(à créer en Phase 4)*

---

## Schéma global des données

```
YGOPRODeck API
    └── cards.json
        └── yugioh.db
            ├── cards          (13 797 lignes)
            ├── card_sets      (43 145 lignes)
            └── card_prices    (13 797 lignes)

yugiohmeta.com API
    └── yugioh.db
        ├── tournament_decks   (decklists de tournoi)
        └── deck_cards         (cartes par deck, zone main/extra/side)
```
