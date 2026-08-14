"""
fetch_tournament_decks.py
Récupère les decklists de tournoi TCG depuis l'API yugiohmeta.com
et les stocke dans data/yugioh.db (tables : tournament_decks, deck_cards).

Usage :
    python3 scripts/fetch_tournament_decks.py

Options modifiables ci-dessous :
    SINCE_DATE  : ne récupérer que les decks uploadés après cette date
    OCG         : False = TCG uniquement
"""

import requests
import sqlite3
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
DB_FILE    = Path("data/yugioh.db")
BASE_URL   = "https://www.yugiohmeta.com/api/v1/top-decks"
SINCE_DATE = "2024-01-01"   # On prend 2024-2026 pour avoir une bonne base méta
BATCH_SIZE = 100             # Nombre de decks par requête
SLEEP_SEC  = 0.5             # Pause entre les requêtes (respecter le serveur)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Referer": "https://www.yugiohmeta.com/",
}

# ── Schéma SQLite ─────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS tournament_decks (
    id                  TEXT PRIMARY KEY,
    author              TEXT,
    archetype           TEXT,
    tournament_type     TEXT,
    tournament_location TEXT,
    placement           REAL,
    created             TEXT,
    uploaded            TEXT,
    ocg                 INTEGER,
    illegal             INTEGER,
    incomplete          INTEGER
);

CREATE TABLE IF NOT EXISTS deck_cards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id     TEXT NOT NULL REFERENCES tournament_decks(id),
    card_name   TEXT NOT NULL,
    amount      INTEGER,
    zone        TEXT    -- 'main', 'extra', 'side'
);

CREATE INDEX IF NOT EXISTS idx_deck_cards_name ON deck_cards(card_name);
CREATE INDEX IF NOT EXISTS idx_deck_cards_deck ON deck_cards(deck_id);
"""

# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_batch(offset: int, limit: int) -> list:
    params = {
        "ocg[$ne]": "true",
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

    print(f"Téléchargement des decklists depuis {SINCE_DATE}...")
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

    print(f"\n  ✓ {len(all_decks)} decklists au total")
    return all_decks

# ── Stockage SQLite ───────────────────────────────────────────────────────────
def insert_decks(decks: list) -> None:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    inserted = 0
    for d in decks:
        # Deck principal
        def extract_name(field):
            if field is None:
                return None
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
            print(f"    deckType       = {repr(d.get('deckType'))}")
            print(f"    tournamentType = {repr(d.get('tournamentType'))}")
            continue

        # Cartes (main / extra / side)
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
    print(f"  ✓ {inserted} decks insérés dans {DB_FILE}")


# ── Vérification rapide ───────────────────────────────────────────────────────
def verify() -> None:
    con = sqlite3.connect(DB_FILE)
    print("\n── Vérification ──")
    print("  Decks total      :", con.execute("SELECT COUNT(*) FROM tournament_decks").fetchone()[0])
    print("  Cartes total     :", con.execute("SELECT COUNT(*) FROM deck_cards").fetchone()[0])
    print("\n  Top 10 archetypes les plus joués :")
    rows = con.execute("""
        SELECT archetype, COUNT(*) as nb
        FROM tournament_decks
        WHERE archetype IS NOT NULL
        GROUP BY archetype
        ORDER BY nb DESC
        LIMIT 10
    """).fetchall()
    for archetype, nb in rows:
        print(f"    {nb:4d}x  {archetype}")
    con.close()


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    decks = fetch_all_decks()
    insert_decks(decks)
    verify()
