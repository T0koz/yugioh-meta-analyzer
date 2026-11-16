"""
TOK-114 — Profils de composition par archétype, pour les pages /decks.

    python scripts/build_archetype_profiles.py --dry-run   # affiche, n'écrit rien
    python scripts/build_archetype_profiles.py             # écrit les trois tables

Pour chaque archétype et chaque zone (main, extra, side) : part des listes qui
contiennent la carte, et nombre d'exemplaires habituel (médiane parmi les listes
qui la jouent). Généralise `archetype_extra_profile` (notebook 02, extra deck
seulement, tout l'historique) aux trois zones et à une fenêtre récente.

Population — la même que la tier list, pour que les deux pages parlent des mêmes
decks : TCG (`ocg = 0`), légaux à la date du tournoi (`deck_legality.legal = 1`,
ce qui écarte aussi le format Genesys, non évaluable), archétype / placement /
date renseignés (filtres du notebook 04). Fenêtre : mois de tournoi les plus
récents cumulés jusqu'à `MIN_WINDOW_DECKS` decks (règle de backend/app/tiering.py,
importée et non recopiée).

Tables écrites (créées par ce script, et lui seul ; aucune autre n'est touchée) :
- `archetype_card_profile`      une ligne par (archétype, zone, carte)
- `archetype_recent_decks`      les RECENT_DECKS listes les plus récentes par archétype
- `archetype_recent_deck_cards` le contenu de ces listes
`deck_cards` (74 % du volume de yugioh.db) n'entre pas dans la base de service :
les deux dernières tables en sont l'extrait précalculé, quelques milliers de lignes.

Ce script ne pose AUCUN seuil (« de base », « d'appoint », effectif minimal d'une
fiche) : il compte. Les seuils vivent à un seul endroit, backend/app/deck_profile.py.

Idempotent : les trois tables sont vidées puis réécrites dans une seule
transaction. Le calcul se fait avant, en lecture ; l'écriture dure une fraction
de seconde (la base est lue en même temps par le backend).
"""

import argparse
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"

sys.path.insert(0, str(ROOT / "backend"))
from app.tiering import MIN_WINDOW_DECKS  # noqa: E402  (règle de fenêtre partagée)

# Listes récentes servies par fiche (brief : 3 à 5).
RECENT_DECKS = 5
ZONES = ("main", "extra", "side")

# Population de la tier list (notebook 04, cellule de chargement).
POPULATION = """
    FROM tournament_decks t
    JOIN deck_legality l ON l.deck_id = t.id AND l.legal = 1
    WHERE t.ocg = 0
      AND t.archetype IS NOT NULL
      AND t.placement IS NOT NULL
      AND t.created IS NOT NULL
"""

SCHEMA = """
CREATE TABLE IF NOT EXISTS archetype_card_profile (
    archetype      TEXT NOT NULL,
    zone           TEXT NOT NULL,      -- main | extra | side
    card_name      TEXT NOT NULL,
    n_lists        INTEGER NOT NULL,   -- listes de l'archétype qui contiennent la carte dans cette zone
    n_decks        INTEGER NOT NULL,   -- listes de l'archétype dans la fenêtre
    share          REAL NOT NULL,      -- n_lists / n_decks
    median_copies  REAL NOT NULL,      -- médiane des exemplaires, parmi les n_lists
    window_start   TEXT NOT NULL,      -- premier mois de la fenêtre (AAAA-MM)
    window_end     TEXT NOT NULL,
    n_decks_window INTEGER NOT NULL,   -- decks de la fenêtre, tous archétypes
    computed_at    TEXT NOT NULL,
    PRIMARY KEY (archetype, zone, card_name)
) WITHOUT ROWID;  -- la clé est la table : pas d'index en double (base de service ÷ 2 sur ces tables)
CREATE TABLE IF NOT EXISTS archetype_recent_decks (
    deck_id         TEXT PRIMARY KEY,
    archetype       TEXT NOT NULL,
    position        INTEGER NOT NULL,  -- 1 = la plus récente
    author          TEXT,
    tournament_type TEXT,
    placement       REAL NOT NULL,
    created         TEXT NOT NULL      -- date du tournoi
);
CREATE INDEX IF NOT EXISTS idx_archetype_recent_decks_archetype
    ON archetype_recent_decks (archetype, position);
CREATE TABLE IF NOT EXISTS archetype_recent_deck_cards (
    deck_id   TEXT NOT NULL,
    zone      TEXT NOT NULL,
    card_name TEXT NOT NULL,
    amount    INTEGER NOT NULL,
    PRIMARY KEY (deck_id, zone, card_name)
) WITHOUT ROWID;
"""
OWN_TABLES = ("archetype_card_profile", "archetype_recent_decks", "archetype_recent_deck_cards")


def window_months(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    """Mois les plus récents cumulés jusqu'à MIN_WINDOW_DECKS (même règle que TIER_LIST_SQL)."""
    months = conn.execute(
        f"SELECT substr(t.created, 1, 7) AS month, COUNT(*) {POPULATION} GROUP BY month ORDER BY month DESC"
    ).fetchall()
    kept, total = [], 0
    for month, n in months:
        if total >= MIN_WINDOW_DECKS:
            break
        kept.append((month, n))
        total += n
    return kept


def compute(conn: sqlite3.Connection) -> dict:
    months = window_months(conn)
    if not months:
        raise SystemExit("Aucun deck TCG légal en base : rien à calculer.")
    names = [m for m, _ in months]
    marks = ",".join("?" for _ in names)

    decks = conn.execute(
        f"""
        SELECT t.id, t.archetype, t.author, t.tournament_type, t.placement, t.created
        {POPULATION} AND substr(t.created, 1, 7) IN ({marks})
        """,
        names,
    ).fetchall()
    archetype_of = {d[0]: d[1] for d in decks}
    n_decks: dict[str, int] = defaultdict(int)
    for d in decks:
        n_decks[d[1]] += 1

    # Une seule lecture de deck_cards, limitée aux decks de la fenêtre (index idx_deck_cards_deck).
    conn.execute("CREATE TEMP TABLE _tok114_window (id TEXT PRIMARY KEY)")
    conn.executemany("INSERT INTO _tok114_window VALUES (?)", [(d[0],) for d in decks])
    cards = conn.execute(
        """
        SELECT dc.deck_id, dc.zone, dc.card_name, SUM(dc.amount)
        FROM _tok114_window w JOIN deck_cards dc ON dc.deck_id = w.id
        WHERE dc.zone IN ('main', 'extra', 'side') AND dc.amount > 0
        GROUP BY dc.deck_id, dc.zone, dc.card_name
        """
    ).fetchall()
    conn.execute("DROP TABLE _tok114_window")

    copies: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    content: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for deck_id, zone, card, amount in cards:
        copies[(archetype_of[deck_id], zone, card)].append(amount)
        content[deck_id].append((zone, card, amount))

    start, end, total = min(names), max(names), len(decks)
    today = date.today().isoformat()
    profile = [
        (a, zone, card, len(v), n_decks[a], len(v) / n_decks[a], float(statistics.median(v)), start, end, total, today)
        for (a, zone, card), v in copies.items()
    ]
    profile.sort(key=lambda r: (r[0], ZONES.index(r[1]), -r[3], r[2]))

    # Listes récentes : date du tournoi décroissante, puis meilleur résultat, puis identifiant (ordre stable).
    by_archetype: dict[str, list] = defaultdict(list)
    for d in decks:
        if content.get(d[0]):  # une liste sans carte en base n'a rien à montrer
            by_archetype[d[1]].append(d)
    recent, recent_cards = [], []
    for a, rows in by_archetype.items():
        rows.sort(key=lambda d: d[0])
        rows.sort(key=lambda d: d[4])
        rows.sort(key=lambda d: d[5], reverse=True)
        for position, (deck_id, _, author, ttype, placement, created) in enumerate(rows[:RECENT_DECKS], start=1):
            recent.append((deck_id, a, position, author, ttype, placement, created))
            recent_cards.extend((deck_id, zone, card, amount) for zone, card, amount in content[deck_id])

    return {
        "months": months, "n_decks": dict(n_decks), "total": total,
        "profile": profile, "recent": recent, "recent_cards": recent_cards,
    }


def report(result: dict) -> None:
    months = ", ".join(f"{m} ({n})" for m, n in sorted(result["months"]))
    print(f"Fenêtre : {months} — {result['total']} decks TCG légaux, {len(result['n_decks'])} archétypes")
    print(f"archetype_card_profile      : {len(result['profile'])} lignes")
    print(f"archetype_recent_decks      : {len(result['recent'])} lignes")
    print(f"archetype_recent_deck_cards : {len(result['recent_cards'])} lignes")
    top = sorted(result["n_decks"].items(), key=lambda kv: -kv[1])[:5]
    for archetype, n in top:
        core = [r for r in result["profile"] if r[0] == archetype and r[1] == "main"][:4]
        cards = " ; ".join(f"{r[2]} {r[5]:.0%} ×{r[6]:g}" for r in core)
        print(f"  {archetype} ({n} listes) — {cards}")


def write(conn: sqlite3.Connection, result: dict) -> None:
    conn.executescript(SCHEMA)  # CREATE … IF NOT EXISTS : sans effet si les tables existent
    with conn:  # une seule transaction : tout ou rien
        for table in OWN_TABLES:
            conn.execute(f"DELETE FROM {table}")
        conn.executemany("INSERT INTO archetype_card_profile VALUES (?,?,?,?,?,?,?,?,?,?,?)", result["profile"])
        conn.executemany("INSERT INTO archetype_recent_decks VALUES (?,?,?,?,?,?,?)", result["recent"])
        conn.executemany("INSERT INTO archetype_recent_deck_cards VALUES (?,?,?,?)", result["recent_cards"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Calcule et affiche sans écrire")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Base à lire et à écrire (défaut : data/yugioh.db)")
    args = parser.parse_args()

    # sqlite3.connect créerait un fichier vide si la base manquait.
    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")

    reader = sqlite3.connect(f"file:{args.db.resolve()}?mode=ro", uri=True, timeout=60)
    try:
        result = compute(reader)
    finally:
        reader.close()
    report(result)

    if args.dry_run:
        print("\n--dry-run : rien n'a été écrit.")
        return

    # timeout=60 : le backend ou un notebook peut tenir la base (« database is locked »).
    writer = sqlite3.connect(args.db, timeout=60)
    try:
        write(writer, result)
    finally:
        writer.close()
    print(f"\nTables écrites dans {args.db.name} : {', '.join(OWN_TABLES)}")


if __name__ == "__main__":
    main()
