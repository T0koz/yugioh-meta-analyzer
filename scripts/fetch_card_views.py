"""
TOK-138 — rafraîchit `cards.views_week` et archive chaque relevé daté dans `card_views_snapshots`.

    python scripts/fetch_card_views.py                 # appelle l'API, archive le relevé, met à jour views_week
    python scripts/fetch_card_views.py --dry-run       # appelle l'API, compte, n'écrit rien
    python scripts/fetch_card_views.py --db <chemin>   # autre base (copie, worktree)
    python scripts/fetch_card_views.py --from-json <f> # relevé lu dans un fichier (même forme que l'API) : tests

Pourquoi : `views_week` (« vues de la semaine » sur YGOPRODeck) n'était écrite que par `init_db.py`, qui réécrit toute
la table `cards`. `fetch_new_cards.py` ajoute les cartes nouvelles sans toucher aux autres : au 18/11, les vues de
toutes les cartes connues dataient de l'instantané du 13/06 (`data/raw/cards.json`), et le signal précoce
(`build_early_signals.py`, critère « vues », 35 %) comparait des vues de juin à des cartes nouvelles relevées le jour
même. Les vues n'avaient pas de date en base : aucun backtest des vues n'était possible sans voir le futur (TOK-129).

Ce que fait le script, en **une seule transaction** (`BEGIN IMMEDIATE` … `COMMIT`, `ROLLBACK` sur erreur) :
1. archive le relevé du jour dans `card_views_snapshots` (table nouvelle, additive : une ligne par carte et par jour
   de relevé, `snapshot_date` en UTC ; relancer le même jour remplace les lignes de ce jour) ;
2. met à jour `cards.views_week` et **rien d'autre**, carte par carte, par `id`, seulement si le nom de l'API (sans
   `<`/`>` ni entité HTML) est le nom en base : une carte renommée garde sa valeur et est signalée (⚠) ;
3. **carte renumérotée** (YGOPRODeck change parfois l'`id` d'une carte : Odd-Eyes Pendulum Dragon, 16178681 →
   16178683, au 18/11) : quand un `id` de l'API est inconnu et qu'**une seule** carte de `cards` porte le même nom et
   manque à l'API, c'est elle qui reçoit les vues (signalé ⚠). Plusieurs candidates : rien, signalé.

Le plan (quelles lignes changer) est recalculé **dans** la transaction, sur `cards` lue après `BEGIN IMMEDIATE` : une
autre écriture ne peut pas passer entre la lecture et la mise à jour.

Gardes :
- réponse tronquée (moins de 90 % des cartes en base, comme `fetch_new_cards.py`) : rien n'est écrit, code 1 ;
- `viewsweek` absent pour plus de la moitié des cartes (format de l'API changé) : rien n'est écrit, code 1 ;
- une carte sans `viewsweek` garde sa valeur (jamais remplacée par NULL) et n'entre pas dans l'archive.

Sauvegarde : avant la première écriture du jour, `(id, views_week)` de `cards` dans
`data/backup_vues_<base>_<AAAAMMJJ>.db` (≈ 300 ko, fichier temporaire puis renommé). Sont gardées les 8 plus récentes
**et la toute première**, qui contient les vues d'avant le premier relevé (13/06 sur la référence). L'archive ne
contient que les relevés de ce script : les vues du 13/06 restent dans cette première sauvegarde et dans
`data/raw/cards.json`.

Réseau : un seul appel à l'API publique YGOPRODeck (`cardinfo.php?misc=yes&format=tcg`, comme `fetch_cards.py`),
une seconde tentative après 30 s en cas d'échec. Jamais d'appel dans les tests (`--from-json`).
"""
from __future__ import annotations

import argparse
import html
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Chemin en dur, comme fetch_new_cards.py : YGO_DB_PATH (variable du backend) ne doit pas détourner une écriture.
DB = ROOT / "data" / "yugioh.db"
MIN_API_RATIO = 0.9        # comme fetch_new_cards.py : en dessous, réponse jugée tronquée
MIN_VIEWS_SHARE = 0.5      # en dessous, `viewsweek` a disparu de la réponse : format changé
RETRY_DELAY_S = 30
KEEP_BACKUPS = 8

SNAPSHOT_DDL = """
    CREATE TABLE IF NOT EXISTS card_views_snapshots (
        snapshot_date TEXT    NOT NULL,   -- jour du relevé (UTC), AAAA-MM-JJ
        card_id       INTEGER NOT NULL,   -- cards.id (identifiant YGOPRODeck)
        card_name     TEXT    NOT NULL,   -- nom renvoyé par l'API ce jour-là
        views_week    INTEGER NOT NULL,   -- misc_info.viewsweek
        views         INTEGER,            -- misc_info.views (cumul), gardé pour un usage futur
        fetched_at    TEXT    NOT NULL,   -- instant du relevé (UTC, ISO 8601)
        PRIMARY KEY (snapshot_date, card_id)
    )"""


def clean(name: str) -> str:
    """Même normalisation que fetch_new_cards.clean et l'index idx_cards_name_clean, entités HTML décodées."""
    return html.unescape(name).replace("<", "").replace(">", "")


def fetch_api() -> list[dict]:
    from fetch_cards import fetch_all_cards
    try:
        return fetch_all_cards()
    except Exception as exc:   # une seconde tentative, puis on laisse l'erreur remonter
        print(f"  ⚠ premier appel en échec ({exc}) ; nouvel essai dans {RETRY_DELAY_S} s", file=sys.stderr)
        time.sleep(RETRY_DELAY_S)
        return fetch_all_cards()


def views_of(card: dict) -> tuple[int | None, int | None]:
    misc = (card.get("misc_info") or [{}])[0]
    vw, v = misc.get("viewsweek"), misc.get("views")
    return (int(vw) if vw is not None else None, int(v) if v is not None else None)


def plan(api: list[dict], base: dict[int, tuple[str, int | None]]) -> dict:
    """Compare le relevé à `cards` ; ne lit ni n'écrit la base."""
    snapshot, updates, renamed, unknown, no_views, unchanged = [], [], [], 0, 0, 0
    renumbered, ambiguous = [], []
    api_ids = {c["id"] for c in api}
    # Cartes de `cards` absentes de l'API, par nom nettoyé : candidates d'une renumérotation.
    orphans: dict[str, list[int]] = {}
    for i, (n, _) in base.items():
        if i not in api_ids:
            orphans.setdefault(clean(n), []).append(i)
    for c in api:
        vw, v = views_of(c)
        if vw is None:
            no_views += 1
            continue
        snapshot.append((int(c["id"]), html.unescape(c["name"]), vw, v))
        if c["id"] not in base:
            cands = orphans.get(clean(c["name"]), [])
            if len(cands) == 1:
                old_id = cands[0]
                renumbered.append((old_id, int(c["id"]), c["name"]))
                if base[old_id][1] != vw:
                    updates.append((vw, old_id))
            elif cands:
                ambiguous.append((int(c["id"]), c["name"], cands))
            else:
                unknown += 1
            continue
        name, old = base[c["id"]]
        if clean(name) != clean(c["name"]):
            renamed.append((c["id"], name, c["name"]))
            continue
        if old != vw:
            updates.append((vw, int(c["id"])))
        else:
            unchanged += 1
    return {"snapshot": snapshot, "updates": updates, "renamed": renamed, "unknown": unknown,
            "renumbered": renumbered, "ambiguous": ambiguous, "no_views": no_views, "unchanged": unchanged,
            "missing": sum(1 for i in base if i not in api_ids) - len(renumbered)}


def read_base(conn: sqlite3.Connection) -> dict[int, tuple[str, int | None]]:
    return {i: (n, v) for i, n, v in conn.execute("SELECT id, name, views_week FROM cards")}


def backup(db: Path, day: str) -> Path:
    dest = db.with_name(f"backup_vues_{db.stem}_{day.replace('-', '')}.db")
    if dest.exists():
        return dest
    tmp = dest.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    src = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=60)
    dst = sqlite3.connect(tmp)
    dst.execute("CREATE TABLE cards_views (id INTEGER PRIMARY KEY, views_week INTEGER)")
    dst.executemany("INSERT INTO cards_views VALUES (?, ?)", src.execute("SELECT id, views_week FROM cards"))
    dst.commit()
    dst.close()
    src.close()
    tmp.replace(dest)
    found = sorted(db.parent.glob(f"backup_vues_{db.stem}_*.db"))
    for old in found[1:-KEEP_BACKUPS]:   # la première (vues d'avant tout relevé) est toujours gardée
        old.unlink()
    return dest


def write(db: Path, day: str, fetched_at: str, api: list[dict]) -> dict:
    """Écrit le relevé ; le plan est recalculé sur `cards` lue dans la transaction. Renvoie ce plan."""
    conn = sqlite3.connect(db, timeout=60, isolation_level=None)   # transaction explicite (voir TOK-136)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            p = plan(api, read_base(conn))
            conn.execute(SNAPSHOT_DDL)
            conn.execute("DELETE FROM card_views_snapshots WHERE snapshot_date = ?", (day,))
            conn.executemany(
                "INSERT INTO card_views_snapshots VALUES (?, ?, ?, ?, ?, ?)",
                [(day, cid, name, vw, v, fetched_at) for cid, name, vw, v in p["snapshot"]])
            conn.executemany("UPDATE cards SET views_week = ? WHERE id = ?", p["updates"])
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=Path, default=DB)
    ap.add_argument("--dry-run", action="store_true", help="compte sans écrire")
    ap.add_argument("--from-json", type=Path, help="relevé lu dans un fichier (liste de cartes au format de l'API)")
    ap.add_argument("--no-backup", action="store_true")
    a = ap.parse_args()
    if not a.db.exists():
        print(f"Base absente : {a.db}", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    day, fetched_at = now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%dT%H:%M:%SZ")
    api = json.loads(a.from_json.read_text()) if a.from_json else fetch_api()
    if isinstance(api, dict):
        api = api.get("data", [])

    ro = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    base = read_base(ro)
    ro.close()

    if len(api) < MIN_API_RATIO * len(base):
        print(f"ERREUR : l'API renvoie {len(api)} cartes pour {len(base)} en base : réponse tronquée, rien n'est écrit.",
              file=sys.stderr)
        return 1
    p = plan(api, base)
    if len(p["snapshot"]) < MIN_VIEWS_SHARE * len(api):
        print(f"ERREUR : viewsweek absent pour {p['no_views']} cartes sur {len(api)} : format de l'API changé ? "
              "Rien n'est écrit.", file=sys.stderr)
        return 1

    print(f"  relevé du {day} : {len(api)} cartes de l'API, {len(p['snapshot'])} avec des vues "
          f"({p['no_views']} sans) ; {len(base)} cartes en base")
    print(f"  views_week à mettre à jour : {len(p['updates'])} ; déjà égales : {p['unchanged']}")
    print(f"  cartes de l'API absentes de cards : {p['unknown']} (fetch_new_cards.py les ajoute) ; "
          f"cartes de cards absentes de l'API : {p['missing']} (valeur gardée)")
    for old_id, new_id, name in p["renumbered"]:
        print(f"  ⚠ « {name} » renumérotée par l'API ({old_id} → {new_id}) : vues reportées sur l'id {old_id} de cards")
    for new_id, name, cands in p["ambiguous"]:
        print(f"  ⚠ « {name} » (id {new_id}) : plusieurs cartes de cards du même nom absentes de l'API {cands} : rien")
    for cid, old, new in p["renamed"][:10]:
        print(f"  ⚠ id {cid} : nom en base « {old} », nom de l'API « {new} » : vues non mises à jour")
    if len(p["renamed"]) > 10:
        print(f"  ⚠ … et {len(p['renamed']) - 10} autres noms différents")

    if a.dry_run:
        print("  (dry-run : rien n'est écrit)")
        return 0
    if not a.no_backup:
        print(f"  sauvegarde (id, views_week) : {backup(a.db, day)}")
    p = write(a.db, day, fetched_at, api)
    print(f"  ✓ {len(p['snapshot'])} vues archivées dans card_views_snapshots ({day}), "
          f"{len(p['updates'])} views_week mises à jour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
