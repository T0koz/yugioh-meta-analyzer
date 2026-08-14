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
from collections import Counter
from functools import reduce
from math import gcd
from pathlib import Path

DB_FILE    = Path("data/yugioh.db")
BASE_URL   = "https://www.yugiohmeta.com/api/v1/top-decks"
SINCE_DATE = "2024-01-01"
BATCH_SIZE = 100
SLEEP_SEC  = 0.5

# Tailles légales d'une zone, utilisées pour repérer une decklist API dupliquée.
ZONE_LIMITS = {"main": 60, "extra": 15, "side": 15}

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
        # Tri sur _id, unique, et non sur uploaded : des dizaines de decks
        # partagent le même timestamp d'upload, et le serveur les re-trie entre
        # deux requêtes. Avec skip/limit, les enregistrements des frontières de
        # page glissaient — 48 decks n'étaient jamais ramenés et 54 revenaient
        # en double à chaque run.
        "sort[_id]": 1,
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

def zone_amounts(entries: list, zone: str, deck_id: str) -> dict[str, int]:
    """Quantités par carte pour une zone, listes dupliquées repliées.

    Deux anomalies de l'API deviennent indistinguables une fois sommées :
    une carte éclatée en deux entrées (amount 1 puis 2 = 3 exemplaires joués,
    à sommer) et la decklist entière renvoyée en double (à replier, sinon un
    main de 40 en pèse 80 et chaque carte grimpe à 6 exemplaires).

    On ne replie que si la zone dépasse sa taille légale ET que chaque couple
    (carte, amount) s'y répète le même nombre de fois — signature d'une liste
    recopiée telle quelle. Une carte réellement éclatée laisse ce PGCD à 1.
    """
    pairs = []
    for entry in entries:
        card_name = entry.get("card", {}).get("name") or entry.get("name")
        if card_name:
            pairs.append((card_name, entry.get("amount", 1)))
    if not pairs:
        return {}

    repeats = Counter(pairs)
    limit = ZONE_LIMITS[zone]
    factor = reduce(gcd, repeats.values())
    if sum(amount * n for (_, amount), n in repeats.items()) <= limit:
        factor = 1

    amounts: dict[str, int] = {}
    for (card_name, amount), n in repeats.items():
        amounts[card_name] = amounts.get(card_name, 0) + amount * (n // factor)

    total = sum(amounts.values())
    if total > limit:
        print(f"\n  ⚠ {deck_id} : {zone} à {total} cartes (max {limit}) — decklist API douteuse")
    return amounts


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
            amounts = zone_amounts(d.get(zone, []), zone, d["_id"])
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
