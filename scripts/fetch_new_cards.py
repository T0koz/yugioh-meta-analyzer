"""Ajoute à `cards` les cartes sorties depuis le dernier chargement (décision D8 bis, TOK-84).

    python scripts/fetch_new_cards.py            # insère les cartes absentes
    python scripts/fetch_new_cards.py --dry-run  # compte sans écrire

Pourquoi un script à part de `fetch_cards.py` + `init_db.py` :
- `init_db.py` réécrit TOUTES les cartes (`INSERT OR REPLACE`) : il écrase `views_week` et les
  statuts de banlist, que lisent le signal précoce (notebook 11) et le Ban Radar. Ce rafraîchissement
  complet reste une décision à part ; ici on n'ajoute que ce qui manque.
- sans cette étape, une carte sortie après le dernier chargement n'a ni texte, ni image, ni
  caractéristiques : les jointures `deck_cards` ↔ `cards` la perdent sans bruit (3 cartes jouées par
  tous les decks Branded manquaient ainsi le 2026-11-16).

Ce que fait le script, en une seule transaction :
1. insère les cartes dont l'`id` est absent de `cards`, avec leurs éditions et leurs prix ;
2. corrige les noms qui portent une entité HTML (`&amp;` → `&`) : l'API en a renvoyé par le passé,
   et un tel nom ne se joint à aucun nom issu de `deck_cards`.
Il ne modifie aucune autre colonne d'une carte déjà présente, et ne supprime jamais rien.

Garde : si l'API renvoie nettement moins de cartes que la base n'en contient, c'est une réponse
tronquée ; le script s'arrête sans écrire (code de sortie 1).
"""
from __future__ import annotations

import argparse
import html
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_cards import fetch_all_cards  # noqa: E402
from init_db import insert_card, insert_prices, insert_sets  # noqa: E402

# Chemin en dur, comme refresh_decks.py : YGO_DB_PATH est la variable du backend (elle peut pointer
# vers serving.db) et ne doit pas détourner une écriture.
DB = ROOT / "data" / "yugioh.db"
MIN_API_RATIO = 0.9  # en dessous de 90 % du nombre de cartes en base, la réponse est jugée tronquée


def clean(name: str) -> str:
    """Même normalisation que l'index idx_cards_name_clean et les jointures des routeurs."""
    return name.replace("<", "").replace(">", "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="compte sans écrire")
    ap.add_argument("--db", type=Path, default=DB, help="autre base (tests sur une copie)")
    args = ap.parse_args()
    db = args.db

    cards = fetch_all_cards()
    con = sqlite3.connect(f"file:{db}?mode=ro" if args.dry_run else db, uri=args.dry_run, timeout=60)
    cur = con.cursor()
    known = {row[0] for row in cur.execute("SELECT id FROM cards")}

    if len(cards) < MIN_API_RATIO * len(known):
        print(f"ERREUR : l'API renvoie {len(cards)} cartes pour {len(known)} en base : réponse tronquée, rien n'est écrit.",
              file=sys.stderr)
        con.close()
        return 1

    # Garde de nom : YGOPRODeck renumérote parfois une carte (id différent, même nom). L'index sur le
    # nom n'est pas unique : sans ce contrôle, la carte serait dupliquée sans erreur et toutes les
    # jointures par nom doubleraient ses lignes. On n'insère donc jamais un nom déjà présent.
    names = {clean(name) for (name,) in cur.execute("SELECT name FROM cards")}
    new, skipped = [], []
    for c in cards:
        if c["id"] in known:
            continue
        c["name"] = html.unescape(c["name"])
        if clean(c["name"]) in names:
            skipped.append(c["name"])
        else:
            new.append(c)
            names.add(clean(c["name"]))
    escaped = []
    for cid, name in cur.execute("SELECT id, name FROM cards").fetchall():
        fixed = html.unescape(name)
        if fixed == name:
            continue
        if clean(fixed) in names:
            skipped.append(fixed)
        else:
            escaped.append((fixed, cid))
            names.add(clean(fixed))
    print(f"  {len(known)} cartes en base, {len(new)} nouvelles, {len(escaped)} noms à corriger (entités HTML)")
    for name in skipped:
        print(f"  ⚠ nom déjà présent sous un autre id, carte ignorée : {name}")
    for c in new[:10]:
        print(f"    + {c['name']}")
    if len(new) > 10:
        print(f"    … et {len(new) - 10} autres")

    if args.dry_run:
        print("  (dry-run : rien n'est écrit)")
        con.close()
        return 0

    try:
        cur.execute("BEGIN IMMEDIATE")
        for c in new:
            insert_card(cur, c)
            insert_sets(cur, c["id"], c.get("card_sets", []))
            insert_prices(cur, c["id"], c.get("card_prices", []))
        cur.executemany("UPDATE cards SET name = ? WHERE id = ?", escaped)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        total = cur.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        con.close()
    print(f"  ✓ {len(new)} cartes insérées, {len(escaped)} noms corrigés ; `cards` compte {total} lignes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
