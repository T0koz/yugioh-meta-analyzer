"""
Snapshot quotidien des prix Cardmarket/TCGPlayer pour toutes les cartes.
Fetch bulk en 1 seul appel API (toutes les cartes à la fois).
Lance depuis run.sh ou en cron : python scripts/snapshot_prices.py
"""

import sqlite3, requests, datetime, time, os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'yugioh.db')
TODAY   = datetime.date.today().isoformat()
API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def run():
    con = sqlite3.connect(DB_PATH)

    con.execute("""
        CREATE TABLE IF NOT EXISTS card_price_history (
            card_id       INTEGER,
            card_name     TEXT,
            snapshot_date TEXT,
            cardmarket_price  REAL,
            tcgplayer_price   REAL,
            PRIMARY KEY (card_id, snapshot_date)
        )
    """)

    n_today = con.execute(
        "SELECT COUNT(*) FROM card_price_history WHERE snapshot_date = ?", (TODAY,)
    ).fetchone()[0]
    if n_today > 0:
        print(f"[snapshot_prices] Snapshot du {TODAY} déjà présent ({n_today} cartes) — skip.")
        con.close()
        return

    print(f"[snapshot_prices] Fetch bulk toutes les cartes ({TODAY})…")
    t0 = time.time()
    try:
        r = requests.get(API_URL, params={"misc": "yes", "format": "tcg"}, headers=HEADERS, timeout=60)
        r.raise_for_status()
        cards = r.json().get("data", [])
    except Exception as e:
        print(f"[snapshot_prices] Erreur API: {e}")
        con.close()
        return

    rows = []
    for card in cards:
        prices = card.get("card_prices", [{}])[0] if card.get("card_prices") else {}
        cm  = _safe_float(prices.get("cardmarket_price"))
        tcp = _safe_float(prices.get("tcgplayer_price"))
        if cm is not None or tcp is not None:
            rows.append((card["id"], card["name"], TODAY, cm, tcp))

    con.executemany(
        "INSERT OR IGNORE INTO card_price_history VALUES (?,?,?,?,?)", rows
    )
    con.commit()
    con.close()
    print(f"[snapshot_prices] {len(rows)} prix sauvegardés en {time.time()-t0:.1f}s")


def _safe_float(val):
    try:
        f = float(val)
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    run()
