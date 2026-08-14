"""
fetch_ocg_decks.py
Récupère les decklists OCG depuis yugiohmeta.com et les ajoute dans yugioh.db.
Les decks OCG auront ocg=1 dans tournament_decks.

Usage :
    python3 scripts/fetch_ocg_decks.py
"""

import requests
import sqlite3
import time
from pathlib import Path

DB_FILE    = Path("data/yugioh.db")
BASE_URL   = "https://www.yugiohmeta.com/api/v1/top-decks"
SINCE_DATE = "2024-01-01"
BATCH_SIZE = 100
SLEEP_SEC  = 0.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Referer": "https://www.yugiohmeta.com/",
}

def fetch_batch(offset: int, limit: int) -> list:
    params = {
        "ocg": "true",                  # OCG uniquement
        "uploaded[$gte]": SINCE_DATE,
        "limit": limit,
        "skip": offset,
        "sort[uploaded]": -1,
    }
    r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_all_decks() -> list:
    all_decks = []
    offset = 0
    print(f"Téléchargement des decklists OCG depuis {SINCE_DATE}...")
    while True:
        batch = fetch_batch(offset, BATCH_SIZE)
        if not batch:
            break
        all_decks.extend(batch)
        print(f"  {len(all_decks)} decks récupérés...", end="\r")
        if len(batch) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
        time.sleep(SLEEP_SEC)
    print(f"\n  ✓ {len(all_decks)} decklists OCG au total")
    return all_decks

def insert_decks(decks: list) -> None:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    inserted = 0

    for d in decks:
        def extract_name(field):
            if field is None: return None
            if isinstance(field, dict):
                val = field.get("name")
                return str(val) if val is not None else None
            return str(field)

        try:
            cur.execute("""
                INSERT OR REPLACE INTO tournament_decks VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                d["_id"],
                # author est tantôt une chaîne, tantôt un objet {_id, name} :
                # sans extract_name, sqlite3 refuse le dict et le deck est perdu.
                extract_name(d.get("author")),
                extract_name(d.get("deckType")),
                extract_name(d.get("tournamentType")),
                extract_name(d.get("tournamentLocation")),
                d.get("tournamentPlacement"),
                d.get("created"),
                d.get("uploaded"),
                1 if d.get("ocg") else 0,
                1 if d.get("illegal") else 0,
                1 if d.get("incomplete") else 0,
            ))
        except Exception as e:
            print(f"\n  ⚠ Erreur sur deck {d['_id']} : {e}")
            continue

        # Purge avant réinsertion : tournament_decks est en INSERT OR REPLACE
        # (idempotent) mais deck_cards n'a pas de clé unique, donc sans ce DELETE
        # chaque relance du script re-empile les cartes des decks déjà en base.
        cur.execute("DELETE FROM deck_cards WHERE deck_id = ?", (d["_id"],))

        for zone in ("main", "extra", "side"):
            # L'API éclate parfois une même carte en deux entrées dans la même
            # zone (ex: amount 1 puis 2 = 3 exemplaires joués). On agrège avant
            # d'insérer pour garder une ligne par (deck, carte, zone).
            amounts: dict[str, int] = {}
            for entry in d.get(zone, []):
                card_name = entry.get("card", {}).get("name") or entry.get("name")
                if card_name:
                    amounts[card_name] = amounts.get(card_name, 0) + entry.get("amount", 1)

            cur.executemany(
                "INSERT INTO deck_cards (deck_id, card_name, amount, zone) VALUES (?,?,?,?)",
                [(d["_id"], name, amount, zone) for name, amount in amounts.items()],
            )
        inserted += 1

    con.commit()
    con.close()
    print(f"  ✓ {inserted} decks OCG insérés dans {DB_FILE}")

def verify() -> None:
    con = sqlite3.connect(DB_FILE)
    print("\n── Vérification ──")
    print("  Decks OCG total :", con.execute("SELECT COUNT(*) FROM tournament_decks WHERE ocg=1").fetchone()[0])
    print("  Decks TCG total :", con.execute("SELECT COUNT(*) FROM tournament_decks WHERE ocg=0").fetchone()[0])
    print("\n  Top 10 archetypes OCG :")
    rows = con.execute("""
        SELECT archetype, COUNT(*) as nb
        FROM tournament_decks
        WHERE ocg=1 AND archetype IS NOT NULL
        GROUP BY archetype ORDER BY nb DESC LIMIT 10
    """).fetchall()
    for arch, nb in rows:
        print(f"    {nb:4d}x  {arch}")
    con.close()

if __name__ == "__main__":
    decks = fetch_all_decks()
    insert_decks(decks)
    verify()
