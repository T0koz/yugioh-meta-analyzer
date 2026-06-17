"""
Snapshot quotidien des prix Cardmarket/TCGPlayer pour les cartes boutique.
Lance depuis run.sh ou en cron : python scripts/snapshot_prices.py
"""

import sqlite3, requests, datetime, time, os
from urllib.parse import quote

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'yugioh.db')
TODAY   = datetime.date.today().isoformat()

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

    # Cartes boutique + leur id
    cards = con.execute("""
        SELECT DISTINCT c.id, c.name
        FROM boutique_card_alerts bca
        JOIN cards c ON c.name = bca.card_name
        ORDER BY c.name
    """).fetchall()

    print(f"[snapshot_prices] {len(cards)} cartes à pricer ({TODAY})")

    rows    = []
    errors  = 0
    headers = {'User-Agent': 'Mozilla/5.0'}

    for cid, cname in cards:
        try:
            url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={quote(cname)}"
            r   = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                errors += 1
                continue
            data   = r.json().get("data", [{}])[0]
            prices = data.get("card_prices", [{}])[0] if data.get("card_prices") else {}
            cm  = float(prices.get("cardmarket_price", 0) or 0)
            tcp = float(prices.get("tcgplayer_price",  0) or 0)
            rows.append((cid, cname, TODAY, cm, tcp))
            time.sleep(0.15)
        except Exception as e:
            errors += 1

    con.executemany(
        "INSERT OR IGNORE INTO card_price_history VALUES (?,?,?,?,?)", rows
    )
    con.commit()
    print(f"[snapshot_prices] {len(rows)} prix sauvegardés ({errors} erreurs)")
    con.close()

if __name__ == "__main__":
    run()
