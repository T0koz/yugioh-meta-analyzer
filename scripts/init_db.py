"""
init_db.py
Lit data/raw/cards.json et crée la base SQLite data/yugioh.db.

Tables créées :
  - cards       : une ligne par carte (infos principales + banlist)
  - card_sets   : dans quels boosters chaque carte est sortie
  - card_prices : prix par carte (Cardmarket, TCGPlayer, etc.)

Usage (depuis la racine du projet) :
    python scripts/init_db.py
"""

import json
import sqlite3
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE = Path("data/raw/cards.json")
DB_FILE    = Path("data/yugioh.db")

# ── Schéma SQL ────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    type        TEXT,
    frame_type  TEXT,
    desc        TEXT,
    archetype   TEXT,
    atk         INTEGER,
    def         INTEGER,
    level       INTEGER,
    race        TEXT,
    attribute   TEXT,
    link_val    INTEGER,
    scale       INTEGER,
    ban_tcg     TEXT,
    ban_ocg     TEXT,
    ban_goat    TEXT,
    tcg_date    TEXT,
    ocg_date    TEXT,
    has_effect  INTEGER,
    views       INTEGER,
    views_week  INTEGER,
    md_rarity   TEXT
);

CREATE TABLE IF NOT EXISTS card_sets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id     INTEGER NOT NULL REFERENCES cards(id),
    set_name    TEXT,
    set_code    TEXT,
    set_rarity  TEXT,
    set_price   REAL
);

CREATE TABLE IF NOT EXISTS card_prices (
    card_id            INTEGER PRIMARY KEY REFERENCES cards(id),
    cardmarket_price   REAL,
    tcgplayer_price    REAL,
    ebay_price         REAL,
    amazon_price       REAL,
    coolstuffinc_price REAL
);
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_float(val):
    try:
        return float(val) if val not in (None, "", "0.00") else None
    except (ValueError, TypeError):
        return None

def insert_card(cur, card):
    banlist = card.get("banlist_info", {})
    misc_list = card.get("misc_info", [])
    misc = misc_list[0] if misc_list else {}

    cur.execute("""
        INSERT OR REPLACE INTO cards VALUES (
            :id, :name, :type, :frame_type, :desc, :archetype,
            :atk, :def, :level, :race, :attribute,
            :link_val, :scale,
            :ban_tcg, :ban_ocg, :ban_goat,
            :tcg_date, :ocg_date, :has_effect,
            :views, :views_week, :md_rarity
        )
    """, {
        "id":         card["id"],
        "name":       card["name"],
        "type":       card.get("type"),
        "frame_type": card.get("frameType"),
        "desc":       card.get("desc"),
        "archetype":  card.get("archetype"),
        "atk":        card.get("atk"),
        "def":        card.get("def"),
        "level":      card.get("level"),
        "race":       card.get("race"),
        "attribute":  card.get("attribute"),
        "link_val":   card.get("linkval"),
        "scale":      card.get("scale"),
        "ban_tcg":    banlist.get("ban_tcg"),
        "ban_ocg":    banlist.get("ban_ocg"),
        "ban_goat":   banlist.get("ban_goat"),
        "tcg_date":   misc.get("tcg_date"),
        "ocg_date":   misc.get("ocg_date"),
        "has_effect": misc.get("has_effect"),
        "views":      misc.get("views"),
        "views_week": misc.get("viewsweek"),
        "md_rarity":  misc.get("md_rarity"),
    })

def insert_sets(cur, card_id, sets):
    for s in sets:
        cur.execute(
            "INSERT INTO card_sets (card_id, set_name, set_code, set_rarity, set_price) VALUES (?,?,?,?,?)",
            (card_id, s.get("set_name"), s.get("set_code"), s.get("set_rarity"), safe_float(s.get("set_price")))
        )

def insert_prices(cur, card_id, prices):
    if not prices:
        return
    p = prices[0]
    cur.execute(
        "INSERT OR REPLACE INTO card_prices VALUES (?,?,?,?,?,?)",
        (
            card_id,
            safe_float(p.get("cardmarket_price")),
            safe_float(p.get("tcgplayer_price")),
            safe_float(p.get("ebay_price")),
            safe_float(p.get("amazon_price")),
            safe_float(p.get("coolstuffinc_price")),
        )
    )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not INPUT_FILE.exists():
        print(f"ERREUR : {INPUT_FILE} introuvable.")
        print("Lance d'abord : python scripts/fetch_cards.py")
        return

    print(f"Lecture de {INPUT_FILE}...")
    with open(INPUT_FILE, encoding="utf-8") as f:
        cards = json.load(f)
    print(f"  ✓ {len(cards)} cartes chargées")

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    print("Insertion dans SQLite...")
    for card in cards:
        insert_card(cur, card)
        insert_sets(cur, card["id"], card.get("card_sets", []))
        insert_prices(cur, card["id"], card.get("card_prices", []))

    con.commit()
    con.close()
    print(f"  ✓ Base créée : {DB_FILE}")

if __name__ == "__main__":
    main()
