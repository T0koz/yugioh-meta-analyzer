"""
Construit `data/serving.db` : la base réduite que l'API sert en production.

    python scripts/build_serving_db.py
    python scripts/build_serving_db.py --check   # vérifie sans écrire

`yugioh.db` pèse ~170 Mo mais l'API n'en lit que 12 tables : tout ce qu'elle
sert est précalculé par les notebooks et les scripts. `deck_cards` et ses index
représentent à eux seuls 74% du volume et ne sont jamais interrogés en ligne.
La base de service tombe à ~9 Mo, ce qui la rend transportable avec le
déploiement — pas de volume persistant à provisionner ni à sauvegarder.

Le backend lit `YGO_DB_PATH` si la variable est définie, sinon `data/yugioh.db`.
En production : YGO_DB_PATH=/app/data/serving.db
"""

import argparse
import os
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DB = ROOT / "data" / "yugioh.db"
SERVING_DB = ROOT / "data" / "serving.db"
ROUTERS_DIR = ROOT / "backend" / "app" / "routers"

# Tables interrogées par l'API. La garde ci-dessous échoue si un routeur en
# référence une qui manque ici — sans quoi un nouvel endpoint passerait en
# production avec une table absente et ne casserait qu'à la première requête.
SERVED_TABLES = [
    "archetype_trend",
    "ban_radar",
    "boutique_buy_signals",
    "card_cooccurrence",
    "card_graph_metrics",
    "card_impact",
    "cards",
    "early_card_signals",
    "graph_communities",
    "meta_predictions",
    "meta_scores",
    "meta_tier_list",
]

TABLE_REFERENCE = re.compile(r"\b(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*)", re.IGNORECASE)


def tables_referenced_by_api() -> set[str]:
    """Noms de tables apparaissant après FROM/JOIN dans les routeurs."""
    referenced: set[str] = set()
    for path in ROUTERS_DIR.glob("*.py"):
        referenced |= set(TABLE_REFERENCE.findall(path.read_text()))
    return referenced


def check_coverage(conn: sqlite3.Connection) -> list[str]:
    """Signale les tables citées par l'API mais absentes de SERVED_TABLES."""
    existing = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    # On ne retient que les références qui correspondent à de vraies tables :
    # la regex attrape aussi des alias et des sous-requêtes.
    referenced = tables_referenced_by_api() & existing
    return sorted(referenced - set(SERVED_TABLES))


def build(source: sqlite3.Connection, destination: Path) -> None:
    destination.unlink(missing_ok=True)
    source.execute("ATTACH DATABASE ? AS serving", (str(destination),))

    for table in SERVED_TABLES:
        schema = source.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if schema is None:
            raise SystemExit(f"Table absente de {SOURCE_DB.name} : {table}")

        # Le DDL nomme la table sans préfixe de base ; on le requalifie pour
        # créer dans `serving` plutôt que dans `main`.
        ddl = re.sub(
            rf'CREATE TABLE\s+"?{re.escape(table)}"?',
            f'CREATE TABLE serving."{table}"',
            schema[0],
            count=1,
            flags=re.IGNORECASE,
        )
        source.execute(ddl)
        source.execute(f'INSERT INTO serving."{table}" SELECT * FROM main."{table}"')

        # Index explicites de la table (les auto-index de contrainte ont
        # sql IS NULL et sont recréés d'office par le DDL de la table).
        for (index_sql,) in source.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL",
            (table,),
        ):
            source.execute(
                re.sub(
                    r"CREATE\s+(UNIQUE\s+)?INDEX\s+",
                    lambda m: f"CREATE {m.group(1) or ''}INDEX serving.",
                    index_sql,
                    count=1,
                    flags=re.IGNORECASE,
                )
            )

    source.commit()
    source.execute("DETACH DATABASE serving")

    # VACUUM sur la base fille : sans ça elle hérite de pages à moitié vides.
    with sqlite3.connect(destination) as vacuumed:
        vacuumed.execute("VACUUM")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Vérifie la couverture sans écrire")
    args = parser.parse_args()

    conn = sqlite3.connect(SOURCE_DB)

    missing = check_coverage(conn)
    if missing:
        raise SystemExit(
            "Ces tables sont interrogées par un routeur mais absentes de "
            f"SERVED_TABLES : {', '.join(missing)}\n"
            "Ajoute-les à la liste, sinon l'endpoint cassera en production."
        )
    print(f"✓ Couverture OK — {len(SERVED_TABLES)} tables servies, aucune référence orpheline")

    if args.check:
        return

    build(conn, SERVING_DB)

    source_mb = os.path.getsize(SOURCE_DB) / 1e6
    serving_mb = os.path.getsize(SERVING_DB) / 1e6
    print(f"✓ {SERVING_DB.relative_to(ROOT)} — {serving_mb:.1f} Mo "
          f"(contre {source_mb:.1f} Mo, ÷{source_mb / serving_mb:.0f})")


if __name__ == "__main__":
    main()
