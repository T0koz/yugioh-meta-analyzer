"""
TOK-136 — recalcule `card_graph_metrics` et `graph_communities` depuis `card_cooccurrence` (notebook 03 en script).

    python scripts/build_graph_metrics.py                 # écrit les deux tables (après sauvegarde des deux tables)
    python scripts/build_graph_metrics.py --dry-run       # calcule et compare à l'existant, n'écrit rien
    python scripts/build_graph_metrics.py --db <chemin>   # autre base (copie, worktree)

Pourquoi : les deux tables n'étaient produites que par le notebook 03, hors de `refresh_all.py`. Au 18/11 elles
avaient 663 nœuds, alors que le graphe de `card_cooccurrence` (recalculée chaque lundi par le notebook 02) en a 1 402
(constat TOK-120, contrôle de fraîcheur TOK-93). Elles alimentent le critère « pont » du Ban Radar
(`build_ban_radar.py`), la « fragmentation » du simulateur (`POST /simulate-ban`), les nœuds de la page du graphe
(`GET /graph/synergies`) et le numéro de communauté du simulateur.

Fidèle au notebook 03 (mêmes seuils, mêmes colonnes, même schéma), avec ces écarts déclarés :
- intermédiarité **exacte** (le notebook tirait 500 sources au hasard, sans graine : non reproductible), comme
  `scripts/bridge_date.py` (TOK-120) ;
- arêtes insérées dans un ordre fixé (tri par nom) : `greedy_modularity_communities` (Clauset-Newman-Moore) n'a pas de
  hasard, mais départage les égalités de modularité selon l'ordre des nœuds ; trier rend le résultat identique d'une
  exécution à l'autre. Aucun paramètre aléatoire, donc pas de graine à fixer ;
- carte de tête d'une communauté : à degré pondéré égal, la première par ordre alphabétique (le notebook prenait la
  première rencontrée dans un ensemble Python, ordre non garanti) ; archétypes à égalité de compte : ordre alphabétique ;
- étiquette d'archétype : `cards.name` est aussi lu sans `<`/`>` (« Maliss <P> March Hare » → « Maliss P March
  Hare », le nom des decks) ; le notebook ne trouvait pas l'archétype de ces cartes.

Repris tel quel, bien que discutable (hors périmètre, ce serait changer le critère) : `weight = jaccard` est lu par
networkx comme une **distance** pour l'intermédiarité et la proximité (un lien fort allonge le chemin).

Écriture : sauvegarde des deux tables existantes dans `data/backup_graphe_<base>_<AAAAMMJJ>.db` (≈ 90 ko, écrite
dans un fichier temporaire puis renommée ; les 8 plus récentes sont gardées), puis remplacement des deux tables dans
**une seule transaction** explicite (`BEGIN IMMEDIATE` … `COMMIT`, `ROLLBACK` sur erreur) : en mode par défaut,
sqlite3 valide un `DROP`/`CREATE` hors de la transaction ouverte par `with conn` (relecture `gardien-donnees`). Le schéma ne change
pas (aucune colonne ajoutée : la base de service et les routeurs lisent ces colonnes-là).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import networkx as nx
import pandas as pd
from networkx.algorithms.community import greedy_modularity_communities

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"

EDGE_MIN_JACCARD = 0.3   # notebook 03, comme bridge_date.py et check_freshness.py
EDGE_MIN_COOC = 5

METRICS_DDL = """
    CREATE TABLE card_graph_metrics (
        card_name         TEXT PRIMARY KEY,
        betweenness       REAL,
        degree_centrality REAL,
        closeness         REAL,
        degree_weighted   REAL
    )"""
COMMUNITIES_DDL = """
    CREATE TABLE graph_communities (
        community_id    INTEGER PRIMARY KEY,
        n_cards         INTEGER,
        lead_card       TEXT,
        archetype_label TEXT,
        top_archetypes  TEXT,
        lead_degree     REAL
    )"""


def load_edges(conn: sqlite3.Connection) -> pd.DataFrame:
    edges = pd.read_sql_query(
        "SELECT card_a, card_b, jaccard, cooc_count FROM card_cooccurrence WHERE jaccard >= ? AND cooc_count >= ?",
        conn, params=(EDGE_MIN_JACCARD, EDGE_MIN_COOC),
    )
    return edges.sort_values(["card_a", "card_b"]).reset_index(drop=True)


def build_graph(edges: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    for a, b, j, c in edges.itertuples(index=False, name=None):
        G.add_edge(a, b, weight=float(j), count=int(c))
    return G


def compute_metrics(G: nx.Graph) -> pd.DataFrame:
    bc = nx.betweenness_centrality(G, weight="weight", normalized=True)   # exacte
    dc = nx.degree_centrality(G)
    cc = nx.closeness_centrality(G, distance="weight")
    nodes = sorted(G.nodes())
    m = pd.DataFrame({
        "card_name": nodes,
        "betweenness": [round(bc[n], 6) for n in nodes],
        "degree_centrality": [round(dc[n], 6) for n in nodes],
        "closeness": [round(cc.get(n, 0), 6) for n in nodes],
        "degree_weighted": [round(G.degree(n, weight="weight"), 4) for n in nodes],
    })
    return m.sort_values(["betweenness", "card_name"], ascending=[False, True]).reset_index(drop=True)


def compute_communities(G: nx.Graph, arch_map: dict[str, str]) -> tuple[pd.DataFrame, dict[str, int]]:
    comms = greedy_modularity_communities(G, weight="weight")
    comms = sorted((sorted(c) for c in comms), key=lambda c: (-len(c), c[0]))
    rows, membership = [], {}
    for i, comm in enumerate(comms):
        sub = G.subgraph(comm)
        deg = dict(sub.degree(weight="weight"))
        lead = min(comm, key=lambda n: (-deg[n], n))
        arches = [arch_map[c] for c in comm if arch_map.get(c)]
        top = [a for a, _ in sorted(Counter(arches).items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
        rows.append({"community_id": i, "n_cards": len(comm), "lead_card": lead,
                     "archetype_label": arch_map.get(lead, lead), "top_archetypes": ", ".join(top),
                     "lead_degree": round(deg[lead], 3)})
        membership.update({c: i for c in comm})
    return pd.DataFrame(rows), membership


def archetype_map(conn: sqlite3.Connection) -> dict[str, str]:
    """Comme le notebook 03 : `cards.name` → `cards.archetype`. Clé brute ET clé sans `<`/`>` (noms de deck_cards)."""
    out: dict[str, str] = {}
    for name, arch in conn.execute("SELECT name, archetype FROM cards WHERE archetype IS NOT NULL"):
        out.setdefault(name, arch)
        out.setdefault(name.replace("<", "").replace(">", ""), arch)
    return out


KEEP_BACKUPS = 8


def backup_tables(db: Path) -> Path:
    dest = db.with_name(f"backup_graphe_{db.stem}_{datetime.now().strftime('%Y%m%d')}.db")
    if dest.exists():
        return dest
    tmp = dest.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    src = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=60)
    dst = sqlite3.connect(tmp)
    for table in ("card_graph_metrics", "graph_communities"):
        if not src.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
            continue
        (ddl,) = src.execute("SELECT sql FROM sqlite_master WHERE name=?", (table,)).fetchone()
        rows = src.execute(f"SELECT * FROM {table}").fetchall()
        dst.execute(ddl)
        if rows:
            dst.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(rows[0]))})", rows)
    dst.commit()
    dst.close()
    src.close()
    tmp.replace(dest)   # une sauvegarde interrompue ne laisse qu'un .tmp, jamais un fichier réutilisé tel quel
    for old in sorted(db.parent.glob(f"backup_graphe_{db.stem}_*.db"))[:-KEEP_BACKUPS]:
        old.unlink()
    return dest


def write(db: Path, metrics: pd.DataFrame, comms: pd.DataFrame) -> None:
    # isolation_level=None : sqlite3 n'ouvre plus de transaction implicite ; celle-ci couvre DROP, CREATE et INSERT des
    # deux tables, qui changent ensemble ou pas du tout.
    conn = sqlite3.connect(db, timeout=60, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute("DROP TABLE IF EXISTS card_graph_metrics")
            conn.execute(METRICS_DDL)
            conn.executemany("INSERT INTO card_graph_metrics VALUES (?,?,?,?,?)",
                             metrics.itertuples(index=False, name=None))
            conn.execute("DROP TABLE IF EXISTS graph_communities")
            conn.execute(COMMUNITIES_DDL)
            conn.executemany("INSERT INTO graph_communities VALUES (?,?,?,?,?,?)",
                             comms.itertuples(index=False, name=None))
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()


def previous_counts(conn: sqlite3.Connection) -> tuple[int | None, int | None, int | None]:
    def one(sql):
        try:
            return conn.execute(sql).fetchone()[0]
        except sqlite3.Error:
            return None
    return (one("SELECT COUNT(*) FROM card_graph_metrics"), one("SELECT COUNT(*) FROM graph_communities"),
            one("SELECT SUM(n_cards) FROM graph_communities"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--dry-run", action="store_true", help="calcule et compare, n'écrit rien")
    ap.add_argument("--no-backup", action="store_true")
    a = ap.parse_args()
    if not a.db.exists():
        print(f"Base absente : {a.db}", file=sys.stderr)
        return 2

    ro = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    if not ro.execute("SELECT 1 FROM sqlite_master WHERE name='card_cooccurrence'").fetchone():
        print("card_cooccurrence absente : lancer le notebook 02 d'abord", file=sys.stderr)
        return 1
    edges = load_edges(ro)
    arch = archetype_map(ro)
    before = previous_counts(ro)
    ro.close()
    if edges.empty:
        print("Aucune arête au-dessus des seuils : rien écrit (card_cooccurrence vide ?)", file=sys.stderr)
        return 1

    G = build_graph(edges)
    metrics = compute_metrics(G)
    comms, _ = compute_communities(G, arch)
    if not comms.n_cards.sum() == len(metrics) == G.number_of_nodes():
        print("Incohérence : communautés et nœuds ne couvrent pas les mêmes cartes ; rien écrit.", file=sys.stderr)
        return 1

    print(f"Graphe : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes, "
          f"{nx.number_connected_components(G)} composantes, {len(comms)} communautés")
    print(f"Avant  : {before[0]} nœuds dans card_graph_metrics, {before[1]} communautés ({before[2]} cartes réparties)")
    print("Top 5 intermédiarité : " + ", ".join(f"{r.card_name} ({r.betweenness:.4f})"
                                               for r in metrics.head(5).itertuples()))
    if a.dry_run:
        print("--dry-run : rien écrit.")
        return 0
    if not a.no_backup:
        print(f"Sauvegarde des deux tables : {backup_tables(a.db)}")
    write(a.db, metrics, comms)
    print(f"Écrit : card_graph_metrics ({len(metrics)}), graph_communities ({len(comms)}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
