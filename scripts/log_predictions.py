"""
Journal des prédictions — archive datée et append-only de ce que le projet annonce.

Pourquoi : meta_predictions, boutique_alerts, boutique_buy_signals et ban_radar sont
recalculées et ÉCRASÉES à chaque exécution. Sans historique, on ne peut jamais prouver
« annoncé le X, réalisé le Y » : on ne peut que rejouer le passé (backtest). Ce script
copie l'état courant de ces tables dans `prediction_log`, sans jamais modifier une ligne
déjà écrite.

Deux supports, volontairement redondants :
  - table `prediction_log` (data/yugioh.db) : interrogeable en SQL. Des triggers
    interdisent UPDATE et DELETE. La base n'est pas versionnée (data/*.db) et se
    régénère pour une partie de ses tables, donc elle ne suffit pas comme preuve.
  - `data/prediction_log.jsonl` : une ligne JSON par prédiction, versionné par git.
    Le commit (puis le push) date la prédiction par un tiers. Si la table est vide
    au lancement, elle est reconstruite depuis ce fichier.

À lancer après chaque recalcul d'une des sources (notebook 05, notebook 10,
build_ban_radar.py), puis à committer :
    python scripts/log_predictions.py            # archive les nouvelles prédictions
    python scripts/log_predictions.py --dry-run  # montre ce qui serait ajouté
    python scripts/log_predictions.py --status   # résumé du journal

Idempotent : une prédiction déjà journalisée (même kind, sujet, date de calcul et
version du modèle) est ignorée.

`provenance` : 'live' si la prédiction est journalisée au plus 1 jour après son calcul,
'backfill' sinon. Une ligne 'backfill' prouve ce que le modèle disait à `made_at`
seulement si on fait confiance à la date de calcul de la source ; seule une ligne
'live', commitée, est une preuve indépendante.
"""

import argparse
import ast
import datetime
import hashlib
import json
import os
import sqlite3
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(ROOT, "data", "yugioh.db")
JSONL_PATH = os.path.join(ROOT, "data", "prediction_log.jsonl")
BAN_SCRIPT = os.path.join(ROOT, "scripts", "build_ban_radar.py")

# À incrémenter quand le modèle correspondant change (notebook 05, notebook 10).
META_MODEL = "blend-ridge-ar1-naive-v1"
BOUTIQUE_MODEL = "alert-views-v1"
EARLY_MODEL = "early-views-text-ocg-v1"

KEY = ("kind", "subject", "made_at", "model_version")
COLUMNS = (
    "kind", "subject", "made_at", "logged_at", "provenance", "target_date",
    "predicted_value", "baseline_value", "predicted_label", "model_version", "payload",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS prediction_log (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    kind             TEXT NOT NULL,   -- meta_forecast | boutique_signal | boutique_buy | early_card | ban_risk_<format>
    subject          TEXT NOT NULL,   -- archétype, ou "archétype | carte", ou carte
    made_at          TEXT NOT NULL,   -- date de calcul de la prédiction (source)
    logged_at        TEXT NOT NULL,   -- horodatage de l'archivage
    provenance       TEXT NOT NULL,   -- live | backfill
    target_date      TEXT,            -- mois visé (YYYY-MM) ; NULL = « prochaine banlist »
    predicted_value  REAL,            -- valeur annoncée (meta score, score d'alerte, risque 0-100)
    baseline_value   REAL,            -- valeur « sans changement » au moment de l'annonce
    predicted_label  TEXT,            -- direction / libellé annoncé
    model_version    TEXT NOT NULL,
    payload          TEXT NOT NULL,   -- JSON : tout le reste de la ligne source
    UNIQUE (kind, subject, made_at, model_version)
);
CREATE TRIGGER IF NOT EXISTS prediction_log_no_update
    BEFORE UPDATE ON prediction_log
    BEGIN SELECT RAISE(ABORT, 'prediction_log est append-only'); END;
CREATE TRIGGER IF NOT EXISTS prediction_log_no_delete
    BEFORE DELETE ON prediction_log
    BEGIN SELECT RAISE(ABORT, 'prediction_log est append-only'); END;
"""


def has_table(con, name):
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def next_month(ym):
    """'2026-05' -> '2026-06'."""
    y, m = int(ym[:4]), int(ym[5:7])
    y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{y:04d}-{m:02d}"


def month_from_english(label):
    """'October 2026' -> '2026-10' ; None si le libellé n'est pas parsable."""
    try:
        return datetime.datetime.strptime(label.strip(), "%B %Y").strftime("%Y-%m")
    except (ValueError, AttributeError):
        return None


def ban_model_version():
    """Empreinte des poids du Ban Radar, lus dans le script sans l'exécuter."""
    try:
        tree = ast.parse(open(BAN_SCRIPT, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "WEIGHTS" for t in node.targets
            ):
                weights = ast.literal_eval(node.value)
                digest = hashlib.sha1(json.dumps(weights, sort_keys=True).encode()).hexdigest()
                return f"ban-radar-{digest[:8]}"
    except (OSError, ValueError, SyntaxError):
        pass
    return "ban-radar-unknown"


def rows_of(con, sql):
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute(sql)]


def collect(con):
    """Lit l'état courant des tables sources. Retourne (entrées, tables_absentes)."""
    entries, missing = [], []

    if has_table(con, "meta_predictions"):
        for r in rows_of(con, "SELECT * FROM meta_predictions"):
            entries.append(dict(
                kind="meta_forecast", subject=r["archetype"], made_at=r["computed_at"],
                target_date=next_month(r["data_month"]),
                predicted_value=r["pred_meta_score"], baseline_value=r["meta_score_current"],
                predicted_label=r["pred_direction"], model_version=META_MODEL,
                payload={"data_month": r["data_month"], "pred_delta": r["pred_delta"]},
            ))
    else:
        missing.append("meta_predictions")

    if has_table(con, "boutique_alerts"):
        for r in rows_of(con, "SELECT * FROM boutique_alerts"):
            entries.append(dict(
                kind="boutique_signal", subject=r["archetype"], made_at=r["computed_at"],
                target_date=month_from_english(r["tcg_entry_estimated"]),
                predicted_value=r["alert_score"], baseline_value=None, predicted_label=None,
                model_version=BOUTIQUE_MODEL,
                payload={k: r[k] for k in r if k not in ("archetype", "computed_at", "alert_score")},
            ))
    else:
        missing.append("boutique_alerts")

    if has_table(con, "boutique_buy_signals"):
        for r in rows_of(con, "SELECT * FROM boutique_buy_signals"):
            entries.append(dict(
                kind="boutique_buy", subject=f"{r['archetype']} | {r['card_name']}",
                made_at=r["computed_at"], target_date=month_from_english(r["tcg_entry_estimated"]),
                predicted_value=r["buy_score_100"], baseline_value=r["cm_price"],
                predicted_label=r["buy_label"], model_version=BOUTIQUE_MODEL,
                payload={k: r[k] for k in r
                         if k not in ("archetype", "card_name", "computed_at", "buy_score_100", "cm_price", "buy_label")},
            ))
    else:
        missing.append("boutique_buy_signals")

    if has_table(con, "early_card_signals"):
        # views_week est un instantané écrasé à chaque recalcul : le journaliser est la seule
        # façon de constituer l'historique nécessaire pour backtester un jour alert_score.
        for r in rows_of(con, "SELECT * FROM early_card_signals"):
            entries.append(dict(
                kind="early_card", subject=r["card_name"], made_at=r["computed_at"],
                target_date=None, predicted_value=r["early_score_100"],
                baseline_value=r["views_week"], predicted_label=r["archetype"],
                model_version=EARLY_MODEL,
                payload={k: r[k] for k in r
                         if k not in ("card_name", "computed_at", "early_score_100", "views_week", "archetype")},
            ))
    else:
        missing.append("early_card_signals")

    if has_table(con, "ban_radar"):
        version = ban_model_version()
        for r in rows_of(con, "SELECT * FROM ban_radar"):
            entries.append(dict(
                kind=f"ban_risk_{str(r['format']).lower()}", subject=r["card_name"],
                made_at=r["as_of"], target_date=None,
                predicted_value=r["ban_risk_score"], baseline_value=None,
                predicted_label=r["risk_label"], model_version=version,
                payload={k: r[k] for k in r
                         if k not in ("card_name", "as_of", "ban_risk_score", "risk_label", "format")},
            ))
    else:
        missing.append("ban_radar")

    return entries, missing


def provenance(made_at, today):
    try:
        gap = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(made_at[:10])).days
    except (ValueError, TypeError):
        return "backfill"
    return "live" if gap <= 1 else "backfill"


def existing_keys(con):
    return {tuple(r) for r in con.execute(f"SELECT {', '.join(KEY)} FROM prediction_log")}


def restore_from_jsonl(con):
    """Table vide + fichier présent : on reconstruit la table depuis le fichier versionné."""
    if not os.path.exists(JSONL_PATH):
        return 0
    n = 0
    with open(JSONL_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            cur = con.execute(
                f"INSERT OR IGNORE INTO prediction_log ({', '.join(COLUMNS)}) "
                f"VALUES ({', '.join('?' * len(COLUMNS))})",
                [row[c] if c != "payload" else json.dumps(row[c], ensure_ascii=False, sort_keys=True)
                 for c in COLUMNS],
            )
            n += cur.rowcount
    con.commit()
    return n


def log_new(con, dry_run):
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    entries, missing = collect(con)
    for m in missing:
        print(f"[log_predictions] table source absente : {m} (ignorée)")

    done = existing_keys(con)
    new = []
    for e in entries:
        if not e["made_at"]:
            print(f"[log_predictions] date de calcul manquante pour {e['kind']} / {e['subject']} — ignorée")
            continue
        if tuple(e[k] for k in KEY) in done:
            continue
        e["logged_at"], e["provenance"] = now, provenance(e["made_at"], today)
        new.append(e)

    by_kind = {}
    for e in new:
        k = (e["kind"], e["made_at"], e["provenance"])
        by_kind[k] = by_kind.get(k, 0) + 1
    for (kind, made_at, prov), n in sorted(by_kind.items()):
        print(f"[log_predictions] {'+' if not dry_run else '(à ajouter)'} {n:>5}  {kind:<20} calculé le {made_at}  [{prov}]")
    if not new:
        print("[log_predictions] rien de nouveau : le journal est à jour.")
        return 0
    if dry_run:
        print(f"[log_predictions] dry-run : {len(new)} prédictions seraient ajoutées, rien n'est écrit.")
        return len(new)

    try:
        with open(JSONL_PATH, "a", encoding="utf-8") as f:
            for e in new:
                con.execute(
                    f"INSERT INTO prediction_log ({', '.join(COLUMNS)}) VALUES ({', '.join('?' * len(COLUMNS))})",
                    [e[c] if c != "payload" else json.dumps(e[c], ensure_ascii=False, sort_keys=True)
                     for c in COLUMNS],
                )
                f.write(json.dumps({c: e[c] for c in COLUMNS}, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        con.commit()
    except Exception:
        con.rollback()
        raise
    print(f"[log_predictions] {len(new)} prédictions archivées (table + {os.path.relpath(JSONL_PATH, ROOT)}).")
    print("[log_predictions] pense à committer data/prediction_log.jsonl : le commit date la preuve.")
    return len(new)


def status(con):
    rows = con.execute(
        "SELECT kind, made_at, provenance, COUNT(*), MIN(target_date), MAX(target_date) "
        "FROM prediction_log GROUP BY 1, 2, 3 ORDER BY 2, 1"
    ).fetchall()
    if not rows:
        print("[log_predictions] journal vide.")
        return
    print(f"{'kind':<20} {'calculé le':<12} {'provenance':<10} {'n':>5}  cible")
    for kind, made_at, prov, n, t0, t1 in rows:
        cible = t0 if t0 == t1 else f"{t0} → {t1}"
        sans_cible = "prochaine banlist" if kind.startswith("ban_risk") else "—"
        print(f"{kind:<20} {made_at:<12} {prov:<10} {n:>5}  {cible or sans_cible}")
    total = con.execute("SELECT COUNT(*) FROM prediction_log").fetchone()[0]
    print(f"total : {total} prédictions")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="affiche sans écrire")
    ap.add_argument("--status", action="store_true", help="résumé du journal")
    args = ap.parse_args()

    if not os.path.exists(DB_PATH):
        sys.exit(f"[log_predictions] base introuvable : {DB_PATH}")
    # timeout long : le backend FastAPI ou un notebook peut garder la base ouverte en lecture
    con = sqlite3.connect(DB_PATH, timeout=60)
    try:
        if args.dry_run and not has_table(con, "prediction_log"):
            # dry-run avant toute écriture : la table n'existe pas encore, on ne la crée pas
            collected, missing = collect(con)
            print(f"[log_predictions] dry-run (table pas encore créée) : {len(collected)} prédictions à archiver.")
            kinds = {}
            for e in collected:
                kinds[(e["kind"], e["made_at"])] = kinds.get((e["kind"], e["made_at"]), 0) + 1
            for (kind, made_at), n in sorted(kinds.items()):
                print(f"  {n:>5}  {kind:<20} calculé le {made_at}")
            for m in missing:
                print(f"  table source absente : {m}")
            return
        con.executescript(SCHEMA)
        if con.execute("SELECT COUNT(*) FROM prediction_log").fetchone()[0] == 0:
            n = restore_from_jsonl(con)
            if n:
                print(f"[log_predictions] table reconstruite depuis le fichier versionné : {n} lignes.")
        if args.status:
            status(con)
        else:
            log_new(con, args.dry_run)
    finally:
        con.close()


if __name__ == "__main__":
    main()
