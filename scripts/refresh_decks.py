"""
Rafraîchissement hebdomadaire des decklists (TOK-70) + journal de santé des fetchs (TOK-76).

    python scripts/refresh_decks.py            # TCG, OCG, légalité, puis contrôle de fraîcheur
    python scripts/refresh_decks.py --status   # n'exécute rien : affiche les 10 derniers runs + fraîcheur

Enchaîne `fetch_tournament_decks.py`, `fetch_ocg_decks.py`, `compute_deck_legality.py`
en sous-processus, **en séquence** (un seul écrivain sur `yugioh.db`). Chaque étape est
journalisée dans `data/fetch_health.jsonl` (fichier, pas table : il reste lisible quand la
base est verrouillée et il survit à une reconstruction de la base) : code de retour, durée,
fin de la sortie d'erreur. Une étape en échec n'empêche pas les suivantes de s'exécuter,
mais le code de sortie final est non nul et une alerte « fraîcheur » est écrite si
`MAX(created)` dépasse FRESHNESS_MAX_DAYS.

Surveillance, rien d'externe : pas de mail ni de webhook. Le job launchd écrit sur
`~/Library/Logs/yugioh-refresh-decks.log` ; `--status` résume l'état.
"""
import argparse
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "yugioh.db"
HEALTH = ROOT / "data" / "fetch_health.jsonl"
FRESHNESS_MAX_DAYS = 7   # au-delà, les decks sont considérés périmés
STEPS = [
    ("fetch_tcg", "scripts/fetch_tournament_decks.py"),
    ("fetch_ocg", "scripts/fetch_ocg_decks.py"),
    ("legality", "scripts/compute_deck_legality.py"),
]


def log(entry: dict) -> None:
    entry["at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with HEALTH.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def freshness() -> dict:
    """Âge du dernier deck TCG et OCG (jours), lu en lecture seule."""
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=60)
    out = {}
    for fmt, ocg in (("TCG", 0), ("OCG", 1)):
        (mx,) = con.execute("SELECT MAX(created) FROM tournament_decks WHERE ocg=?", (ocg,)).fetchone()
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(mx.replace("Z", "+00:00"))).days if mx else None
        out[fmt] = {"max_created": mx, "age_days": age}
    con.close()
    return out


def status() -> int:
    if HEALTH.exists():
        for line in HEALTH.read_text().splitlines()[-10:]:
            print(line)
    f = freshness()
    print("Fraîcheur :", json.dumps(f))
    stale = [k for k, v in f.items() if v["age_days"] is None or v["age_days"] > FRESHNESS_MAX_DAYS]
    if stale:
        print(f"⚠ périmé (> {FRESHNESS_MAX_DAYS} j) : {', '.join(stale)}")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        return status()

    failed = 0
    for name, script in STEPS:
        t0 = time.time()
        p = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        ok = p.returncode == 0
        failed += not ok
        log({"step": name, "ok": ok, "returncode": p.returncode,
             "seconds": round(time.time() - t0), "stderr_tail": p.stderr[-600:] if not ok else ""})
        print(f"[{name}] {'ok' if ok else 'ÉCHEC'} ({round(time.time() - t0)} s)")
        if not ok:
            print(p.stderr[-600:], file=sys.stderr)

    f = freshness()
    stale = [k for k, v in f.items() if v["age_days"] is None or v["age_days"] > FRESHNESS_MAX_DAYS]
    log({"step": "freshness", "ok": not stale, **{k: v for k, v in f.items()}})
    if stale:
        print(f"⚠ decks périmés (> {FRESHNESS_MAX_DAYS} j) : {', '.join(stale)}", file=sys.stderr)
    return 1 if (failed or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
