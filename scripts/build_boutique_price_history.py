"""
Extrait l'historique de prix des cartes du signal boutique (TOK-103).

    python scripts/build_boutique_price_history.py
    python scripts/build_boutique_price_history.py --db /chemin/vers/yugioh.db
    python scripts/build_boutique_price_history.py --dry-run

`card_price_history` (relevés Cardmarket et TCGplayer via YGOPRODeck, écrits par
`scripts/snapshot_prices.py`) compte ~140 000 lignes : trop pour la base de
service. La page boutique n'a besoin que des cartes de `boutique_buy_signals`
(une douzaine). Ce script en recopie les relevés dans `boutique_price_history`,
reconstruite à chaque exécution, à lancer après `build_buy_signals.py`.

Aucun calcul : chaque ligne est un relevé tel qu'il a été pris. Pas de lissage,
pas d'interpolation, pas de relevé inventé pour combler une date manquante. Les
trous (périodes sans relevé) sont décidés par l'API (`backend/app/price_history.py`),
pas ici.

Un prix à 0 ou absent n'est pas un prix : la ligne est écartée (le relevé partiel
du 2026-06-17 en contient quelques-uns).

Jointure par nom nettoyé de `<P>`/`<C>`/`<Q>` (même convention que `cards`). Si
YGOPRODeck a renuméroté une carte (même nom, deux `card_id`), un seul relevé est
gardé par date : celui de l'identifiant le plus récent.
"""

import argparse
import datetime
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"

TABLE = "boutique_price_history"

SCHEMA = f"""
CREATE TABLE {TABLE} (
    card_name        TEXT NOT NULL,
    snapshot_date    TEXT NOT NULL,
    cardmarket_price REAL,
    tcgplayer_price  REAL,
    computed_at      TEXT NOT NULL,
    PRIMARY KEY (card_name, snapshot_date)
)
"""

SELECT_ROWS = """
WITH signal_cards AS (
    SELECT DISTINCT card_name FROM boutique_buy_signals
),
ranked AS (
    SELECT REPLACE(REPLACE(h.card_name, '<', ''), '>', '') AS card_name,
           h.snapshot_date,
           h.cardmarket_price,
           h.tcgplayer_price,
           ROW_NUMBER() OVER (
               PARTITION BY REPLACE(REPLACE(h.card_name, '<', ''), '>', ''), h.snapshot_date
               ORDER BY h.card_id DESC
           ) AS rn
    FROM card_price_history h
    WHERE REPLACE(REPLACE(h.card_name, '<', ''), '>', '') IN (SELECT card_name FROM signal_cards)
      AND h.cardmarket_price > 0
)
SELECT card_name, snapshot_date, cardmarket_price, tcgplayer_price
FROM ranked
WHERE rn = 1
ORDER BY card_name, snapshot_date
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Base source et cible (défaut : data/yugioh.db)")
    parser.add_argument("--dry-run", action="store_true", help="Affiche le résumé sans écrire")
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")

    con = sqlite3.connect(args.db, timeout=60)
    rows = con.execute(SELECT_ROWS).fetchall()
    signal_cards = {r[0] for r in con.execute("SELECT DISTINCT card_name FROM boutique_buy_signals")}
    covered = {r[0] for r in rows}
    dates = sorted({r[1] for r in rows})

    print(f"[boutique_prices] {len(rows)} relevés, {len(covered)}/{len(signal_cards)} cartes du signal, "
          f"{len(dates)} dates ({dates[0] if dates else '—'} → {dates[-1] if dates else '—'})")
    for name in sorted(signal_cards - covered):
        print(f"  ⚠ aucun relevé de prix pour {name}")

    if args.dry_run:
        con.close()
        return

    computed_at = datetime.date.today().isoformat()
    with con:
        con.execute(f"DROP TABLE IF EXISTS {TABLE}")
        con.execute(SCHEMA)
        con.executemany(
            f"INSERT INTO {TABLE} VALUES (?, ?, ?, ?, ?)",
            [(*r, computed_at) for r in rows],
        )
    con.close()
    print(f"[boutique_prices] ✓ {TABLE} écrite ({len(rows)} lignes)")


if __name__ == "__main__":
    main()
