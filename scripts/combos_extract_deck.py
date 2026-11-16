"""Extrait un deck de tournoi de la base, pour le jeu de tests du moteur de combos (TOK-87).

Lecture seule (`mode=ro`) : ce script n'écrit jamais dans `yugioh.db`.
Ce n'est PAS du code du moteur : il ne résout aucun effet, il recopie une decklist.

Le fichier produit ne contient pas le texte des cartes (il appartient à Konami et le
dépôt est public) : seulement son empreinte SHA-256, qui sert à détecter un errata
entre l'écriture d'un test et son exécution.

Usage :
    python scripts/combos_extract_deck.py                 # deck source du pilote Branded
    python scripts/combos_extract_deck.py --deck-id <id>  # un autre deck
    python scripts/combos_extract_deck.py --texts         # affiche aussi les textes (non écrits)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Dans un worktree, data/yugioh.db n'existe pas : YGO_DB_PATH pointe vers la base du dépôt principal.
DEFAULT_DB = Path(os.environ.get("YGO_DB_PATH", ROOT / "data" / "yugioh.db"))
DEFAULT_DECK = "6af240d29e8b7a3a8eb28d8d"  # Branded, régional WCQ du 2026-11-08, top 4
OUT = ROOT / "docs" / "moteur-combos" / "deck-branded-source.json"

# cards.name porte <P>/<C>/<Q>, pas deck_cards ; le « + » coupe l'affinité TEXT pour
# que SQLite utilise l'index d'expression idx_cards_name_clean (cf. TOK-83).
CARDS_SQL = """
SELECT d.zone, d.card_name, d.amount, c.id, c.type, c.attribute, c.race, c.level,
       c.atk, c.def, c.ban_tcg, c.desc
FROM deck_cards d
LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +d.card_name
WHERE d.deck_id = ?
ORDER BY CASE d.zone WHEN 'main' THEN 0 WHEN 'extra' THEN 1 ELSE 2 END, d.card_name
"""

DECK_SQL = """
SELECT t.id, t.author, t.archetype, t.tournament_type, t.placement, t.created, t.ocg,
       l.format, l.list_name, l.legal, l.n_violations, l.days_to_boundary
FROM tournament_decks t LEFT JOIN deck_legality l ON l.deck_id = t.id
WHERE t.id = ?
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--deck-id", default=DEFAULT_DECK)
    parser.add_argument("--texts", action="store_true", help="affiche les textes des cartes")
    parser.add_argument("--no-write", action="store_true", help="n'écrit pas le fichier JSON")
    args = parser.parse_args()

    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=60)
    con.row_factory = sqlite3.Row
    deck = con.execute(DECK_SQL, (args.deck_id,)).fetchone()
    if deck is None:
        raise SystemExit(f"Deck introuvable : {args.deck_id}")
    rows = con.execute(CARDS_SQL, (args.deck_id,)).fetchall()
    con.close()

    cards, totals, missing = [], {}, []
    for r in rows:
        totals[r["zone"]] = totals.get(r["zone"], 0) + r["amount"]
        known = r["id"] is not None
        if not known:
            missing.append(r["card_name"])
        cards.append(
            {
                "zone": r["zone"],
                "name": r["card_name"],
                "amount": r["amount"],
                "card_id": r["id"],
                "type": r["type"],
                "attribute": r["attribute"],
                "race": r["race"],
                "level": r["level"],
                "atk": r["atk"],
                "def": r["def"],
                "ban_tcg": r["ban_tcg"],
                "text_sha256": hashlib.sha256(r["desc"].encode()).hexdigest() if known and r["desc"] else None,
                "in_cards_table": known,
            }
        )
        if args.texts:
            print(f"### {r['card_name']} [{r['zone']} x{r['amount']}]\n{r['desc'] or '(texte absent)'}\n")

    out = {
        "deck": {k: deck[k] for k in deck.keys()},
        "totals": totals,
        "missing_from_cards_table": sorted(set(missing)),
        "cards": cards,
    }
    print(f"Deck {deck['id']} — {deck['archetype']} — {deck['author']} — {deck['created'][:10]}")
    print(f"Totaux : {totals} — légal : {deck['legal']} ({deck['list_name']})")
    print(f"Cartes absentes de `cards` : {out['missing_from_cards_table'] or 'aucune'}")
    if not args.no_write:
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Écrit : {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
