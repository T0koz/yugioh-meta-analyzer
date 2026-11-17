"""
Vérifications avant de pousser — une seule commande pour tout le monde.

    python scripts/check.py              # ce qui a changé depuis origin/main (commits + fichiers modifiés)
    python scripts/check.py --all        # tout, même si rien n'a changé
    python scripts/check.py --ci         # mode GitHub Actions : sans base de données, sur tout le dépôt
    python scripts/check.py --pre-push   # appelé par .githooks/pre-push (lit les refs sur stdin)
    python scripts/check.py --visuel     # ajoute les tests visuels du front (≈ 45 s, voir docs/tests-visuels.md)

Pourquoi ce script : le dépôt est public et deux personnes poussent directement sur
`main`, sans revue. Les garde-fous existaient déjà, mais éparpillés (CLAUDE.md, context.md) :
ici, ils sont lancés d'un coup, et seulement ceux qui concernent ce qui a changé.

| Vérification                       | Quand                                      | Bloquante |
|------------------------------------|--------------------------------------------|-----------|
| Fichiers interdits, secrets        | toujours                                   | oui       |
| WEIGHTS alignés script / API       | toujours                                   | oui       |
| tsc + eslint                       | frontend/ modifié                          | oui       |
| build_serving_db.py --check        | backend/ ou scripts/ modifié (base requise)| oui       |
| Test de fumée, yugioh.db + serving | backend/ ou scripts/ modifié (base requise)| oui       |
| Backtest du Ban Radar              | scoring modifié (base requise)             | non : à lire, pas de seuil défini |
| Tests visuels du front             | seulement avec --visuel (≈ 45 s, réseau)   | oui       |
| Mots interdits dans les textes     | frontend/src/ modifié, ou --all            | non (lot 16 : bloquant une fois les textes appliqués) |
| Moteur de combos (pytest)          | moteur_combos/ ou tests du moteur modifiés | oui       |

Bibliothèque standard uniquement : le script tourne sans venv (GitHub Actions, hook).
Les étapes qui demandent une base ou `node_modules` absents sont **ignorées et signalées**,
jamais réussies en silence.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"
YUGIOH_DB = ROOT / "data" / "yugioh.db"
SERVING_DB = ROOT / "data" / "serving.db"

BAN_RADAR_FILES = {"scripts/build_ban_radar.py", "backend/app/routers/ban_radar.py"}

# Fichiers qui ne doivent jamais être suivis par Git (dépôt public).
FORBIDDEN_FILES = [
    (re.compile(r"(^|/)\.env(\..+)?$"), "fichier d'identifiants (.env)"),
    (re.compile(r"\.(db|sqlite3?|db-journal|db-wal)$"), "base de données"),
    (re.compile(r"(^|/)HANDOFF\.md$"), "notes personnelles de Thomas"),
    (re.compile(r"\.(pem|key|p12)$"), "clé privée"),
    # data/raw/cards.json est suivi depuis le premier commit, avant l'entrée .gitignore :
    # données publiques YGOPRODeck, sans risque, donc pas listé ici.
]
ALLOWED_FILES = {".env.example"}

# Motifs d'identifiants. Volontairement prudents : un faux positif coûte une ligne
# d'explication, un vrai positif sur un dépôt public coûte une rotation de clé.
SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "clé privée"),
    (re.compile(r"\b(postgres(ql)?|mysql|mongodb(\+srv)?)://[^\s:/@]+:[^\s@]+@"), "URL de base avec mot de passe"),
    (re.compile(r"\blibsql://\S+authToken=\S+"), "URL Turso avec jeton"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "clé AWS"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "jeton GitHub"),
    (re.compile(r"\bsk-(ant-|proj-)?[A-Za-z0-9_-]{20,}\b"), "clé d'API (OpenAI / Anthropic)"),
    (re.compile(r"\blin_api_[A-Za-z0-9]{20,}\b"), "clé d'API Linear"),
    (re.compile(r"""(?i)\b\w*(api[_-]?key|secret|password|passwd|auth[_-]?token)\w*\s*[:=]\s*['"][^'"\s]{12,}['"]"""),
     "identifiant écrit en dur"),
]
# Ce fichier contient les motifs eux-mêmes.
SECRET_SCAN_EXCLUDE = {"scripts/check.py"}


# ── Affichage ──────────────────────────────────────────────────────────────────

class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.skipped: list[str] = []

    def step(self, title: str) -> None:
        print(f"\n▶ {title}")

    def ok(self, msg: str) -> None:
        print(f"  ✓ {msg}")

    def fail(self, title: str, detail: str = "") -> None:
        self.failures.append(title)
        print(f"  ✗ {title}")
        if detail:
            for line in detail.rstrip().splitlines()[-40:]:
                print(f"    {line}")

    def skip(self, title: str, why: str) -> None:
        self.skipped.append(f"{title} ({why})")
        print(f"  ⚠ ignoré : {why}")


def run(cmd: list[str], cwd: Path = ROOT, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        env={**os.environ, **(env or {})},
    )


def git(*args: str) -> str:
    result = run(["git", *args])
    return result.stdout if result.returncode == 0 else ""


def main_checkout() -> Path:
    """Racine du dépôt principal. Égale à ROOT, sauf dans un worktree Git
    (les sessions Claude Code en ouvrent souvent) : la base et le venv n'existent
    alors que dans le dépôt principal."""
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    return Path(common).parent if common else ROOT


def python_bin() -> str:
    """Le venv du projet (ou celui du dépôt principal), sinon l'interpréteur courant."""
    for root in (ROOT, main_checkout()):
        venv = root / ".venv" / "bin" / "python"
        if venv.exists():
            return str(venv)
    return sys.executable


WORKTREE_DB_HINT = ("dans un worktree, la base est dans le dépôt principal → "
                    "ln -s {main}/data/yugioh.db data/yugioh.db")


def db_missing_reason(db: Path) -> str:
    main_db = main_checkout() / "data" / db.name
    if main_checkout() != ROOT and main_db.exists():
        return WORKTREE_DB_HINT.format(main=main_checkout()).replace("yugioh.db", db.name)
    return f"data/{db.name} absente (voir docs/collaboration/transmission-base.md)"


# ── Ce qui a changé ────────────────────────────────────────────────────────────

ZERO_SHA = "0" * 40


def changed_files_pre_push(stdin: str) -> tuple[set[str], list[str]]:
    """Fichiers et plages de commits poussés, d'après les lignes que Git passe au hook."""
    files: set[str] = set()
    ranges: list[str] = []
    for line in stdin.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        _local_ref, local_sha, _remote_ref, remote_sha = parts
        if local_sha == ZERO_SHA:  # suppression de branche distante : rien à vérifier
            continue
        if remote_sha == ZERO_SHA:  # nouvelle branche : comparer à origin/main
            base = git("merge-base", local_sha, "origin/main").strip() or f"{local_sha}~1"
        else:
            base = remote_sha
        ranges.append(f"{base}..{local_sha}")
        files |= set(git("diff", "--name-only", base, local_sha).split())
    return files, ranges


def changed_files_local() -> tuple[set[str], list[str]]:
    """Commits pas encore sur origin/main + modifications non commitées + fichiers nouveaux."""
    base = git("merge-base", "HEAD", "origin/main").strip()
    if not base:
        print("  (origin/main introuvable : je vérifie tout)")
        return set(git("ls-files").split()), []
    files = set(git("diff", "--name-only", base).split())
    files |= set(git("ls-files", "--others", "--exclude-standard").split())
    return files, [base]


# ── Vérifications ──────────────────────────────────────────────────────────────

def check_forbidden_files(report: Report, files: set[str]) -> None:
    report.step("Fichiers interdits dans Git (dépôt public)")
    # Seuls les fichiers que Git suivra comptent : un .env ignoré ne sera jamais poussé.
    tracked_or_new = set(git("ls-files").split()) | set(git("ls-files", "--others", "--exclude-standard").split())
    candidates = {f for f in files if f in tracked_or_new and (ROOT / f).exists()}
    bad = [
        f"{f} : {why}"
        for f in sorted(candidates)
        for pattern, why in FORBIDDEN_FILES
        if pattern.search(f) and Path(f).name not in ALLOWED_FILES
    ]
    if bad:
        report.fail("Fichiers à ne jamais pousser", "\n".join(bad)
                    + "\n→ git rm --cached <fichier>, puis l'ajouter à .gitignore")
    else:
        report.ok(f"{len(candidates)} fichier(s) examiné(s)")


def added_lines(ranges: list[str], include_worktree: bool) -> list[tuple[str, str]]:
    """(fichier, ligne ajoutée) pour chaque plage, plus le non-commité si demandé."""
    diffs = [git("diff", "--unified=0", "--no-color", r) for r in ranges]
    if include_worktree:
        diffs.append(git("diff", "--unified=0", "--no-color", "HEAD"))
    out: list[tuple[str, str]] = []
    current = ""
    for diff in diffs:
        for line in diff.splitlines():
            if line.startswith("+++ "):
                current = line[6:] if line.startswith("+++ b/") else ""
            elif line.startswith("+") and not line.startswith("+++") and current:
                out.append((current, line[1:]))
    return out


def scan_text(path: str, text: str) -> list[str]:
    if path in SECRET_SCAN_EXCLUDE:
        return []
    return [
        f"{path} : {why} → {line.strip()[:80]}"
        for line in text.splitlines()
        for pattern, why in SECRET_PATTERNS
        if pattern.search(line)
    ]


def check_secrets(report: Report, files: set[str], ranges: list[str], mode: str) -> None:
    report.step("Identifiants dans le code (clés, mots de passe, URL de base)")
    hits: list[str] = []
    if mode == "ci":
        # Tout le dépôt : la CI ne sait pas ce qui a déjà été vérifié.
        for path in git("ls-files").split():
            p = ROOT / path
            if p.suffix in {".png", ".jpg", ".ico", ".woff", ".woff2", ".ipynb"} or not p.is_file():
                continue
            try:
                hits += scan_text(path, p.read_text(errors="ignore"))
            except OSError:
                continue
    else:
        for path, line in added_lines(ranges, include_worktree=(mode == "local")):
            hits += scan_text(path, line)
        # Fichiers nouveaux non suivis : pas dans le diff.
        if mode == "local":
            for path in git("ls-files", "--others", "--exclude-standard").split():
                p = ROOT / path
                if p.is_file() and p.stat().st_size < 2_000_000:
                    hits += scan_text(path, p.read_text(errors="ignore"))
    if hits:
        report.fail("Identifiant possible", "\n".join(sorted(set(hits)))
                    + "\n→ le mettre dans .env (ignoré par Git) et le lire avec os.environ."
                    + "\n  S'il a déjà été poussé : le révoquer, l'effacer du code ne suffit pas.")
    else:
        report.ok("aucun motif d'identifiant trouvé")


def read_weights(path: Path) -> dict | None:
    """Lit le dict littéral WEIGHTS sans exécuter le module (pas de pandas requis)."""
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "WEIGHTS" for t in node.targets):
            return ast.literal_eval(node.value)
    return None


def check_weights(report: Report) -> None:
    report.step("WEIGHTS du Ban Radar identiques dans le script et dans l'API")
    script = read_weights(ROOT / "scripts" / "build_ban_radar.py")
    api = read_weights(ROOT / "backend" / "app" / "routers" / "ban_radar.py")
    if script is None or api is None:
        report.fail("WEIGHTS introuvable", "le dict littéral WEIGHTS a disparu d'un des deux fichiers")
    elif script != api:
        diff = "\n".join(f"{k} : script {script.get(k)} / API {api.get(k)}"
                         for k in sorted(set(script) | set(api)) if script.get(k) != api.get(k))
        report.fail("WEIGHTS désalignés", diff)
    else:
        report.ok(f"{len(script)} critères, somme {sum(script.values()):.2f}")


def check_frontend(report: Report, files: set[str]) -> None:
    report.step("Front : types (tsc) et lint (eslint)")
    if not (FRONTEND / "node_modules").exists():
        report.skip("front", "frontend/node_modules absent → cd frontend && npm install")
        return
    tsc = run(["npx", "tsc", "--noEmit"], cwd=FRONTEND)
    if tsc.returncode:
        report.fail("tsc", tsc.stdout + tsc.stderr)
    else:
        report.ok("tsc --noEmit")
    stats = run(["node", "scripts/test-stats.mjs"], cwd=FRONTEND)
    if stats.returncode:
        report.fail("test des calculs du front (intervalle de Wilson)", stats.stdout + stats.stderr)
    else:
        report.ok(stats.stdout.strip().splitlines()[-1].lstrip("✓ "))
    targets = sorted(
        f.removeprefix("frontend/") for f in files
        if f.startswith("frontend/src/") and f.endswith((".ts", ".tsx")) and (ROOT / f).exists()
    ) or ["src"]
    lint = run(["npx", "eslint", *targets], cwd=FRONTEND)
    if lint.returncode:
        report.fail("eslint", lint.stdout + lint.stderr)
    else:
        report.ok(f"eslint ({'tout src/' if targets == ['src'] else f'{len(targets)} fichier(s)'})")


def check_backend(report: Report) -> None:
    report.step("Base de service : tables lues par l'API (build_serving_db.py --check)")
    if not YUGIOH_DB.exists():
        report.skip("SERVED_TABLES", db_missing_reason(YUGIOH_DB))
    else:
        res = run([python_bin(), "scripts/build_serving_db.py", "--check"])
        if res.returncode:
            report.fail("SERVED_TABLES", res.stdout + res.stderr)
        else:
            report.ok(res.stdout.strip().splitlines()[-1].lstrip("✓ "))

    report.step("Test de fumée de l'API (tous les endpoints répondent 200)")
    for local_db in (YUGIOH_DB, SERVING_DB):
        # Le test lit YGO_DB_PATH : depuis un worktree, il peut viser la base du dépôt principal.
        db = local_db if local_db.exists() else main_checkout() / "data" / local_db.name
        if not db.exists():
            report.skip(f"fumée {local_db.name}", db_missing_reason(local_db))
            continue
        res = run([python_bin(), "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                  cwd=BACKEND, env={"YGO_DB_PATH": str(db)})
        output = res.stdout + res.stderr
        if res.returncode and ("No module named" in output):
            module = re.search(r"No module named '?([\w.]+)", output)
            report.skip(f"fumée {db.name}", f"module Python manquant ({module.group(1) if module else '?'}) → "
                        ".venv/bin/pip install -r backend/requirements-dev.txt")
        elif res.returncode:
            report.fail(f"test de fumée sur {db.name}", output)
        else:
            report.ok(f"{db.name} : {res.stdout.strip().splitlines()[-1]}")


def check_backtest(report: Report) -> None:
    report.step("Backtest du Ban Radar (scoring modifié) — à LIRE, pas de seuil automatique")
    if not YUGIOH_DB.exists():
        report.skip("backtest", db_missing_reason(YUGIOH_DB) + " — backtest OBLIGATOIRE avant de pousser")
        return
    res = run([python_bin(), "scripts/build_ban_radar.py", "--backtest"])
    if res.returncode:
        report.fail("backtest", res.stdout + res.stderr)
        return
    # Une ligne par liste : « TCG 2026-05-18  rang médian 84/889 (aléatoire ≈ 444) | top-10% … »
    fmt, date = "", ""
    for line in res.stdout.splitlines():
        if line.strip() in {"TCG", "OCG"}:
            fmt = line.strip()
        elif m := re.match(r"--- Liste du (\S+)", line):
            date = m.group(1)
        elif "rang médian" in line:
            print(f"    {fmt} {date}  {line.strip().removeprefix('-> ')}")
    report.ok("backtest exécuté : compare les rangs médians à ceux de context.md avant de pousser")


def check_garde_fou(report: Report) -> None:
    report.step("Garde-fou des commandes (hook .claude/hooks/garde_fou.py)")
    try:
        json.loads((ROOT / ".claude" / "settings.json").read_text())
    except FileNotFoundError:
        report.skip("garde-fou", ".claude/settings.json absent")
        return
    except ValueError as exc:
        report.fail("settings.json", f".claude/settings.json invalide : {exc}")
        return
    res = run([sys.executable, ".claude/hooks/test_garde_fou.py"])
    if res.returncode:
        report.fail("garde-fou", res.stdout + res.stderr)
    else:
        report.ok(res.stdout.strip())


def check_copy(report: Report) -> None:
    """Charte « ton et explication » : appels à l'action, promesses, superlatifs, ponctuation,
    formules (scripts/check_copy.py). Non bloquant tant que le lot 16 n'est pas appliqué :
    passer `--strict` et `report.fail` ensuite."""
    report.step("Textes du site : mots et tournures interdits par la charte (non bloquant)")
    res = run([sys.executable, "scripts/check_copy.py"])
    lines = res.stdout.strip().splitlines()
    summary = lines[-1] if lines else "aucune sortie"
    if res.returncode:
        report.fail("check_copy.py", res.stdout + res.stderr)
    elif len(lines) > 1:
        print(f"  ⚠ avertissement (non bloquant) : {summary}")
        for line in lines[:-1][:40]:
            print(f"    {line.strip()}")
        print("    → propositions dans docs/textes-avant-apres.md (lot 16)")
    else:
        report.ok(summary)


COMBOS_FILES = ("moteur_combos/", "scripts/combos_", "docs/moteur-combos/tests-branded.yaml",
                "docs/moteur-combos/deck-branded-source.json", "docs/moteur-combos/points-de-regle-a-valider.md")


def check_combos(report: Report) -> None:
    """Moteur de combos (lot 18) : structures, schéma combos.db, chargement du deck, 72 départs, classement.
    Les tests qui lisent les textes des cartes demandent yugioh.db (lecture seule) : ignorés sans elle."""
    report.step("Moteur de combos : tests pytest (moteur_combos/tests)")
    db = YUGIOH_DB if YUGIOH_DB.exists() else main_checkout() / "data" / YUGIOH_DB.name
    res = run([python_bin(), "-m", "pytest", "moteur_combos/tests", "-q", "-p", "no:cacheprovider", "-rs"],
              env={"YGO_DB_PATH": str(db)})
    output = res.stdout + res.stderr
    if res.returncode and "No module named" in output:
        module = re.search(r"No module named '?([\w.]+)", output)
        report.skip("moteur de combos", f"module Python manquant ({module.group(1) if module else '?'}) → "
                    ".venv/bin/pip install pytest pyyaml")
    elif res.returncode:
        report.fail("tests du moteur de combos", output)
    else:
        resume = [line for line in res.stdout.strip().splitlines() if " passed" in line]
        report.ok(resume[-1].strip("= ") if resume else "pytest vert")
        if "skipped" in res.stdout:
            print(f"  ⚠ tests ignorés (base de référence absente : {db})")


def check_visual(report: Report) -> None:
    """Sur demande seulement : ≈ 45 s, et le build télécharge les polices (réseau requis)."""
    report.step("Tests visuels du front (45 captures comparées aux références)")
    res = run([python_bin(), "scripts/visual_tests.py"])
    last = (res.stdout.strip().splitlines() or [""])[-1]
    if res.returncode == 0:
        report.ok(last.lstrip("✓ "))
    elif res.returncode == 3:  # dépendance absente (navigateur, venv, node_modules, réseau)
        report.skip("tests visuels", last.removeprefix("⚠ Tests visuels ignorés : "))
    else:
        report.fail("tests visuels", res.stdout + res.stderr)


# ── Rappels non bloquants ──────────────────────────────────────────────────────

def reminders(files: set[str], visual_done: bool = False) -> None:
    notes = []
    if not visual_done and any(f.startswith("frontend/src/") for f in files):
        notes.append("Tu as touché l'interface : `python scripts/check.py --visuel` compare 45 captures aux "
                     "références (≈ 45 s). Changement voulu → `python scripts/visual_tests.py --update`.")
    if any(f.startswith(("notebooks/", "scripts/build_", "scripts/refresh_all")) for f in files):
        notes.append("Tu as touché un calcul : si une table a été recalculée, lancer "
                     "`python scripts/log_predictions.py` (Thomas seul commite data/prediction_log.jsonl).")
    code = [f for f in files if f.startswith(("backend/", "frontend/src/", "scripts/", "notebooks/"))]
    if code and not ({"context.md", "BACKLOG.md"} & files):
        notes.append("Fonctionnalité terminée ? Mettre à jour context.md (pièges, résultats) et BACKLOG.md.")
    if notes:
        print("\nℹ Rappels (non bloquants)")
        for n in notes:
            print(f"  • {n}")


# ── Point d'entrée ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="tout vérifier, même sans changement")
    group.add_argument("--ci", action="store_true", help="mode GitHub Actions (sans base, tout le dépôt)")
    group.add_argument("--pre-push", action="store_true", help="appelé par le hook pre-push")
    parser.add_argument("--visuel", action="store_true",
                        help="lancer aussi les tests visuels du front (≈ 45 s, scripts/visual_tests.py)")
    args = parser.parse_args()

    if args.pre_push:
        mode = "pre-push"
        files, ranges = changed_files_pre_push(sys.stdin.read())
        if not files:
            return 0
    elif args.ci:
        mode, files, ranges = "ci", set(git("ls-files").split()), []
    else:
        mode = "local"
        files, ranges = changed_files_local()
        if args.all:
            files |= set(git("ls-files").split())

    print(f"Vérifications ({mode}) — {len(files)} fichier(s) concerné(s)")
    report = Report()

    check_forbidden_files(report, files)
    check_secrets(report, files, ranges, mode)
    check_weights(report)

    touches = lambda *prefixes: any(f.startswith(prefixes) for f in files)  # noqa: E731
    if mode != "ci" and touches("frontend/"):
        check_frontend(report, files)
    if mode != "ci" and touches("backend/", "scripts/"):
        check_backend(report)
    if mode != "ci" and (args.all or BAN_RADAR_FILES & files):
        check_backtest(report)
    if mode != "ci" and (args.all or touches(*COMBOS_FILES)):
        check_combos(report)
    if args.all or touches("frontend/src/", "scripts/check_copy.py"):
        check_copy(report)  # 0,3 s, bibliothèque standard : tourne aussi en CI
    check_garde_fou(report)  # 0,2 s : toujours lancé
    if args.visuel and mode != "ci":
        check_visual(report)
    if mode != "ci":
        reminders(files, visual_done=args.visuel)

    print()
    if report.skipped:
        print("⚠ Ignoré (à lancer à la main si c'est concerné) :")
        for s in report.skipped:
            print(f"  • {s}")
    if report.failures:
        print(f"✗ {len(report.failures)} vérification(s) en échec : {', '.join(report.failures)}")
        if mode == "pre-push":
            print("  Push annulé. Corriger, ou, en connaissance de cause : git push --no-verify")
        return 1
    print("✓ Tout est bon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
