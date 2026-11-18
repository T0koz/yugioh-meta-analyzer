"""
Rafraîchissement hebdomadaire des decklists (TOK-70) + journal de santé des fetchs (TOK-76).

    python scripts/refresh_decks.py            # TCG, OCG, légalité, puis contrôle de fraîcheur
    python scripts/refresh_decks.py --status   # n'exécute rien : affiche les 10 derniers runs + fraîcheur

Enchaîne `fetch_new_cards.py` (cartes nouvelles, non bloquante), `fetch_tournament_decks.py`, `fetch_ocg_decks.py`, `fetch_banlist_history.py`, `compute_deck_legality.py`,
`refresh_all.py` (tables dérivées), `build_serving_db.py` (base de service) puis `check_freshness.py` (TOK-93 :
fraîcheur des tables servies et santé de l'endpoint yugiohmeta, toujours lancé, même après un échec amont)
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
    # Cartes sorties depuis le dernier chargement (texte, image, caractéristiques). Ajout seul, sans
    # réécrire les cartes existantes. Non bloquante : une panne de YGOPRODeck ne doit pas empêcher
    # le recalcul des scores, qui ne dépend que des decks.
    ("new_cards", "scripts/fetch_new_cards.py"),
    ("fetch_tcg", "scripts/fetch_tournament_decks.py"),
    ("fetch_ocg", "scripts/fetch_ocg_decks.py"),
    # La banlist doit être à jour AVANT la légalité : sinon les decks postérieurs à une nouvelle liste
    # sont jugés contre l'ancienne, donc illégaux, donc exclus de tous les scores.
    ("banlist", "scripts/fetch_banlist_history.py"),
    ("legality", "scripts/compute_deck_legality.py"),
]
# Étapes aval : recalcul de toutes les tables dérivées puis base de service. Sautées si une étape
# amont a échoué (on ne recalcule pas, et on ne journalise pas de prédiction « live », sur des decks périmés).
DOWNSTREAM = [
    ("derived", "scripts/refresh_all.py"),
    ("serving", "scripts/build_serving_db.py"),
]
NON_BLOCKING = {"new_cards"}  # en échec : journalisée, code de sortie non nul, mais l'aval tourne
# TOK-93 : dernier contrôle, après la base de service (qu'il ne peut donc pas bloquer), lancé même si l'amont a
# échoué. Il contrôle la base qui part en ligne, avec les dates de référence de yugioh.db, et teste /top-decks.
# Il journalise lui-même sa ligne {"step": "fraicheur_tables", …} : pas de seconde ligne ici.
TABLES_FRESHNESS = ["scripts/check_freshness.py", "--db", "data/serving.db", "--reference", "data/yugioh.db"]


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
    # TOK-93 : derniers contrôles de fraîcheur des tables servies et de l'endpoint.
    tables = subprocess.run([sys.executable, "scripts/check_freshness.py", "--status"], cwd=ROOT,
                            capture_output=True, text=True)
    print(tables.stdout.rstrip())
    return 1 if (stale or tables.returncode == 1) else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        return status()

    failed = blocking = 0
    for name, script in STEPS + DOWNSTREAM:
        if name in dict(DOWNSTREAM) and blocking:
            log({"step": name, "ok": False, "skipped": "étape amont en échec"})
            print(f"[{name}] sautée (étape amont en échec)")
            continue
        t0 = time.time()
        p = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        ok = p.returncode == 0
        failed += not ok
        blocking += (not ok) and name not in NON_BLOCKING
        # Les fetchs avalent les erreurs par deck (« ⚠ Erreur sur deck », « decklist API douteuse ») et
        # continuent : on les compte, sinon un champ d'API qui change de forme passe inaperçu.
        warns = [l.strip() for l in p.stdout.replace("\r", "\n").splitlines() if "⚠" in l]
        log({"step": name, "ok": ok, "returncode": p.returncode, "seconds": round(time.time() - t0),
             "n_warnings": len(warns), "warnings_sample": warns[:5],
             "stderr_tail": p.stderr[-600:] if not ok else ""})
        print(f"[{name}] {'ok' if ok else 'ÉCHEC'} ({round(time.time() - t0)} s, {len(warns)} avertissements)")
        if not ok:
            print(p.stderr[-600:], file=sys.stderr)

    f = freshness()
    stale = [k for k, v in f.items() if v["age_days"] is None or v["age_days"] > FRESHNESS_MAX_DAYS]
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=60)
    counts = {"n_decks_tcg": con.execute("SELECT COUNT(*) FROM tournament_decks WHERE ocg=0").fetchone()[0],
              "n_decks_ocg": con.execute("SELECT COUNT(*) FROM tournament_decks WHERE ocg=1").fetchone()[0]}
    con.close()
    prev = [json.loads(l) for l in HEALTH.read_text().splitlines() if '"freshness"' in l] if HEALTH.exists() else []
    shrunk = bool(prev) and any(counts[k] < prev[-1].get(k, 0) for k in counts)  # le nombre de decks ne doit jamais baisser
    if shrunk:
        print("⚠ le nombre de decks a BAISSÉ depuis le dernier run : API tronquée ou purge ?", file=sys.stderr)
    log({"step": "freshness", "ok": not stale and not shrunk, **counts, **{k: v for k, v in f.items()}})
    stale = stale or (["nombre_de_decks_en_baisse"] if shrunk else [])
    if stale:
        print(f"⚠ decks périmés (> {FRESHNESS_MAX_DAYS} j) : {', '.join(stale)}", file=sys.stderr)

    t0 = time.time()
    p = subprocess.run([sys.executable, *TABLES_FRESHNESS], cwd=ROOT, capture_output=True, text=True)
    print(p.stdout.rstrip())
    print(f"[tables_freshness] {'ok' if p.returncode == 0 else 'ÉCHEC'} ({round(time.time() - t0)} s)")
    if p.returncode:
        print(p.stderr[-600:], file=sys.stderr)
        failed += 1
    return 1 if (failed or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
