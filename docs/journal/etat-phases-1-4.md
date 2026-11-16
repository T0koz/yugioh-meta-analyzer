## État du projet — Phases 1 à 4 : ✅ TOUTES TERMINÉES

### Ce qui existe en DB (yugioh.db)
| Table | Lignes | Source |
|-------|--------|--------|
| cards | 13 797 | YGOPRODeck API |
| tournament_decks | 19 888 | yugiohmeta.com (TCG + OCG) |
| deck_cards | 852 405 | yugiohmeta.com |
| meta_scores | 462 | notebook 04 |
| meta_tier_list | 47 | notebook (tier list yugiohmeta) |
| text_synergies | 55 072 | notebook 07 (NLP sur desc) |
| card_mechanic_tags | 13 797 | notebook 07 |
| early_card_signals | 467 | notebook 11 (views_week signal) |
| banlist_history | 11 890 | notebook 09 |
| banlist_features | 3 660 | notebook 09 |
| archetypes_official | 640 | notebook 10 (endpoint /archetypes.php) |
| archetype_mapping | 122 | notebook 10 |
| card_price_history | 41 395 | notebook (snapshot quotidien) |
| card_cooccurrence | 5 489 | notebook 02 |
| card_cooccurrence_90d | 8 797 | notebook 02 (fenêtre 90j) |
| card_cooccurrence_extra | 5 583 | notebook 02 (extra deck) |
| card_cooccurrence_elite | 4 796 | notebook 02 (YCS/Nationals) |
| card_cooccurrence_quarterly | 9 851 | notebook 02 (trimestriel) |
| card_cooccurrence_side | 739 | notebook 02 |
| card_graph_metrics | 663 | notebook 03 (betweenness) |
| graph_communities | 63 | notebook 03 |
| deck_style_clusters | 3 601 | notebook 12 (K-Means k=4) |
| meta_predictions | 45 | notebook 05 (AR(1)) |
| boutique_alerts | 69 | notebook 10 |
| boutique_card_alerts | 167 | notebook 10 |
| boutique_buy_signals | 137 | notebook 10 |
| combo_edges_global | 117 | notebook 08 (NLP combos) |
| meta_scores_regional | 678 | notebook (OCG vs TCG) |

### Notebooks existants
- `01_exploration.ipynb` — exploration cartes
- `02_cooccurrence.ipynb` — co-occurrence pondérée (toutes variantes)
- `03_graph.ipynb` — graphe NetworkX + Pyvis + betweenness
- `04_meta_score.ipynb` — score méta + trends
- `05_meta_prediction.ipynb` — modèle AR(1) par archetype
- `06_card_ban_impact.ipynb` — bridge score + impact ban
- `07_nlp_text_synergies.ipynb` — NLP sur texte des effets (desc)
- `08_nlp_combos.ipynb` — NLP combos YouTube (blacklist appliquée ✅)
- `09_banlist_history.ipynb` — historique banlist complet
- `09_ocg_tcg_correlation.ipynb` — corrélation OCG→TCG (r=0.771, lag 4 mois)
- `10_archetypes_official.ipynb` — matching archetypes officiels Konami
- `10_boutique_alert_score.ipynb` — score alerte boutiques (Kewl Tune 100/100)
- `11_early_card_signal.ipynb` — signal précoce views_week
- `12_deck_clustering.ipynb` — clustering style de jeu K-Means

### Signal boutiques ✅
- **Corrélation OCG→TCG : r=0.771, p<0.0001, lag 4 mois**
- Formule : `alert_score = meta_score_ocg × log(1 + avg_views_week_cartes_core)`
- Filtres : staples >20% decks TCG exclues + cartes bannies TCG exclues
- **Kewl Tune : score 100/100** — Fydraulis Harmonia (19 844 views/week) signal d'achat fort
- Entrée TCG estimée : octobre 2026

### NLP Combos (notebook 08) — état actuel
- Blacklist appliquée : 49 termes exclus (NEXT, Fine, Return, Prohibition, Contact, Surface, Storm...)
- Problème identifié : transcription YouTube déforme les noms OCG/japonais (ex: "Kewl Tune" → "Cool Tune")
- Fonctionne bien sur archetypes aux noms anglais classiques (Branded, Snake-Eye...)
- **P4-X en cours** : test sur vidéo Branded 101 (`DSYkfk5u_uA`) — pas encore lancé
