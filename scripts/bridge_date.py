"""
TOK-120 (B5 de l'audit de rigueur) — critère « pont » du Ban Radar recalculé à une date donnée, sans fuite.

Module de lecture seule, importé par `diagnose_ban_radar_rangs.py` (TOK-120) et `diagnose_pont_simulateur.py`
(TOK-132). N'écrit rien en base. Ne change ni `build_ban_radar.py` ni ce que sert l'API : le critère `bridge` du
score servi lit toujours `card_graph_metrics` (graphe calculé une fois sur toutes les données, d'où la fuite).

Reconstruction fidèle de la chaîne actuelle, à une différence près, la date :

- notebook 02 (`card_cooccurrence`) : decks légaux (`deck_legality.legal = 1`), tous formats confondus, zone main ;
  score d'une carte dans un deck = min(exemplaires, 3) / 3 × poids du deck ; poids du deck = poids de place
  (1 / place, 0,3 si inconnue) × récence exp(−jours / 365), ramené à une moyenne de 1 ; cartes présentes dans au
  moins 10 decks ; Jaccard pondéré ; paires gardées au-dessus de 0,1 (le notebook les filtre ainsi avant d'écrire) ;
- notebook 03 (`card_graph_metrics`) : graphe des paires Jaccard ≥ 0,3 et au moins 5 decks en commun, centralité
  d'intermédiarité (`betweenness`) avec `weight = jaccard`, normalisée ;
- `build_ban_radar.build` : `bridge = betweenness / max(betweenness)`, borné à [0, 1], 0 hors graphe.

Ce qui change : seuls les decks **mis en ligne** au plus tard à la date de coupure entrent (`uploaded ≤ as_of`, plus
strict que `created`, puisque la mise en ligne suit le tournoi de 5 jours en moyenne), et la récence se mesure depuis
la date de coupure, pas depuis le dernier deck de la base.

Deux écarts assumés avec le notebook 03, déclarés :
- intermédiarité **exacte** (le notebook tire 500 sources au hasard sans graine, ce qui n'est pas reproductible) ;
- `weight = jaccard` est repris tel quel, bien que networkx le lise comme une **distance** (un lien fort allonge le
  chemin). C'est le calcul qui alimente le score servi ; le corriger serait un autre critère, pas une datation.
"""

from __future__ import annotations

import sqlite3

import networkx as nx
import numpy as np
import pandas as pd
from scipy import sparse

MIN_CARD_DECKS = 10          # notebook 02 : cartes présentes dans au moins 10 decks
PAIR_MIN_JACCARD = 0.1       # notebook 02 : paires écrites dans card_cooccurrence
EDGE_MIN_JACCARD = 0.3       # notebook 03 : arêtes du graphe
EDGE_MIN_COOC = 5            # notebook 03
DECAY_DAYS = 365             # notebook 02 : demi-vie de la récence


def _placement_weight(p: pd.Series) -> pd.Series:
    w = 1.0 / p.where(p > 0)
    return w.clip(upper=1.0).fillna(0.3)


class DatedGraph:
    """Charge une fois les lignes main des decks légaux, puis calcule le graphe à n'importe quelle date."""

    def __init__(self, conn: sqlite3.Connection):
        self.rows = pd.read_sql_query(
            """
            SELECT dc.deck_id, dc.card_name, dc.amount, td.placement, substr(td.uploaded, 1, 10) AS uploaded
            FROM deck_cards dc
            JOIN tournament_decks td ON td.id = dc.deck_id
            WHERE dc.zone = 'main' AND td.uploaded IS NOT NULL
              AND td.id IN (SELECT deck_id FROM deck_legality WHERE legal = 1)
            """,
            conn,
        )
        self._cache: dict[str, dict] = {}

    def at(self, as_of: str) -> dict:
        """{'n_decks', 'n_nodes', 'n_edges', 'betweenness' (Series), 'pairs' (DataFrame des paires)} à `as_of`."""
        if as_of in self._cache:
            return self._cache[as_of]
        r = self.rows[self.rows.uploaded <= as_of]
        decks = r.drop_duplicates("deck_id").set_index("deck_id")
        days = (pd.Timestamp(as_of) - pd.to_datetime(decks.uploaded)).dt.days.clip(lower=0)
        w = _placement_weight(decks.placement) * np.exp(-days / DECAY_DAYS)
        w = w / w.mean()

        presence = r.groupby("card_name").deck_id.nunique()
        cards = presence[presence >= MIN_CARD_DECKS].index
        r = r[r.card_name.isin(cards)]
        deck_idx = pd.Index(decks.index)
        card_idx = pd.Index(sorted(cards))
        i = deck_idx.get_indexer(r.deck_id)
        j = card_idx.get_indexer(r.card_name)
        score = (r.amount.clip(upper=3).to_numpy() / 3.0) * w.reindex(r.deck_id).to_numpy()
        W = sparse.csr_matrix((score, (i, j)), shape=(len(deck_idx), len(card_idx)))
        B = sparse.csr_matrix((np.ones(len(r)), (i, j)), shape=W.shape)

        cooc = (W.T @ W).toarray()
        diag = np.diag(cooc)
        union = diag[:, None] + diag[None, :] - cooc
        with np.errstate(divide="ignore", invalid="ignore"):
            jac = np.where(union > 0, cooc / union, 0.0)
        np.fill_diagonal(jac, 0.0)
        count = (B.T @ B).toarray().astype(int)

        a, b = np.nonzero(np.triu(jac, k=1) > PAIR_MIN_JACCARD)
        pairs = pd.DataFrame({"card_a": card_idx[a], "card_b": card_idx[b],
                              "jaccard": np.round(jac[a, b], 4), "cooc_count": count[a, b]})

        edges = pairs[(pairs.jaccard >= EDGE_MIN_JACCARD) & (pairs.cooc_count >= EDGE_MIN_COOC)]
        G = nx.Graph()
        G.add_weighted_edges_from(edges[["card_a", "card_b", "jaccard"]].itertuples(index=False, name=None))
        bc = nx.betweenness_centrality(G, weight="weight", normalized=True) if len(G) else {}
        out = {"n_decks": len(deck_idx), "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges(),
               "betweenness": pd.Series(bc, dtype=float), "pairs": pairs}
        self._cache[as_of] = out
        return out

    def bridge(self, as_of: str, cards: pd.Index) -> pd.Series:
        """Critère `bridge` daté, comme `build_ban_radar.build` : betweenness / max, borné, 0 hors graphe."""
        bc = self.at(as_of)["betweenness"]
        top = bc.max() if len(bc) and bc.max() > 0 else 1.0
        return (bc.reindex(cards).fillna(0) / top).clip(0, 1)

    def neighbors(self, as_of: str, card: str, limit: int) -> list[str]:
        """Voisins de plus fort Jaccard, comme `/simulate-ban` (30 voisins lus dans `card_cooccurrence`)."""
        p = self.at(as_of)["pairs"]
        sub = p[(p.card_a == card) | (p.card_b == card)].sort_values("jaccard", ascending=False).head(limit)
        return [b if a == card else a for a, b in zip(sub.card_a, sub.card_b)]
