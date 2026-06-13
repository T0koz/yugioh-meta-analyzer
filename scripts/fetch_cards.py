"""
fetch_cards.py
Fetches all TCG cards from YGOPRODeck API (v7) and saves to data/raw/cards.json.

Usage (depuis la racine du projet) :
    python scripts/fetch_cards.py
"""

import requests
import json
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "cards.json"

PARAMS = {
    "misc": "yes",   # ajoute tcg_date, ocg_date, views, formats, has_effect...
    "format": "tcg", # cartes TCG uniquement (exclut Rush Duel, Speed Duel)
}

# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_all_cards() -> list:
    print("Connexion à l'API YGOPRODeck...")
    response = requests.get(BASE_URL, params=PARAMS, timeout=30)
    response.raise_for_status()

    cards = response.json().get("data", [])
    print(f"  ✓ {len(cards)} cartes récupérées")
    return cards

# ── Save ──────────────────────────────────────────────────────────────────────
def save_cards(cards: list) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"  ✓ Sauvegardé dans {OUTPUT_FILE} ({size_kb:.0f} KB)")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start = time.time()
    cards = fetch_all_cards()
    save_cards(cards)
    print(f"\nTerminé en {time.time() - start:.1f}s")
