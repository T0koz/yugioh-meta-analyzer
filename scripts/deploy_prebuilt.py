"""
Déploiement « voie 2 » (TOK-35, docs/deploiement.md §7-8) : construire le site sur la machine de
Thomas, puis envoyer le résultat à Vercel.

    python scripts/deploy_prebuilt.py                     # vérifie, prépare la base, AFFICHE les commandes
    python scripts/deploy_prebuilt.py --execute preview   # les lance : prévisualisation
    python scripts/deploy_prebuilt.py --execute prod      # les lance : production

**Par défaut, aucune commande Vercel n'est lancée.** Le script :
  1. vérifie `vercel.json`, la CLI Vercel (version seulement) et le lien du projet à la racine ;
  2. vérifie la base de service `data/serving.db` : présente, toutes les tables servies,
     plus récente que `data/yugioh.db` (sinon : `python scripts/build_serving_db.py`) ;
  3. la copie dans `backend/data/serving.db` (embarquée dans la fonction de l'API), après avoir
     vérifié que Git ignore ce chemin (dépôt public) ;
  4. vérifie que l'API locale répond (le build du site l'interroge : pages pré-générées) ;
  5. affiche les commandes `vercel pull`, `vercel build`, `vercel deploy --prebuilt`.

`--execute` n'est accepté que si toutes les vérifications passent. Seul Thomas le passe.

Pourquoi un build local : sur Vercel, la liaison BACKEND_URL ne se résout pas pendant le build
(doc Services, *Bindings*) ; le site ne pourrait pas interroger l'API pour pré-générer ses pages.
En local, `API_URL` pointe sur l'API lancée sur la base de service. Les données du site sont alors
figées au build, ce qui convient à une mise à jour hebdomadaire.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API = "http://localhost:8000/api/v1"
MIN_CLI = (48, 1, 8)  # FastAPI sur Vercel (doc *FastAPI on Vercel*)
EMBEDDED_DB = ROOT / "backend" / "data" / "serving.db"


class Checks:
    def __init__(self) -> None:
        self.failed: list[str] = []

    def ok(self, msg: str) -> None:
        print(f"  ✓ {msg}")

    def warn(self, msg: str) -> None:
        print(f"  ⚠ {msg}")

    def fail(self, msg: str, hint: str = "") -> None:
        self.failed.append(msg)
        print(f"  ✗ {msg}")
        if hint:
            print(f"      → {hint}")


def main_checkout() -> Path:
    """Dépôt principal (différent de ROOT dans un worktree, où `data/` n'existe pas)."""
    out = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=ROOT, capture_output=True, text=True,
    )
    return Path(out.stdout.strip()).parent if out.returncode == 0 and out.stdout.strip() else ROOT


def data_dir() -> Path:
    for root in (ROOT, main_checkout()):
        if (root / "data" / "serving.db").exists():
            return root / "data"
    return ROOT / "data"


def served_tables() -> list[str]:
    spec = importlib.util.spec_from_file_location("build_serving_db", ROOT / "scripts" / "build_serving_db.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # le module ne fait rien à l'import (main() sous __name__)
    return list(module.SERVED_TABLES)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cli_version() -> tuple[int, ...] | None:
    if not shutil.which("vercel"):
        return None
    out = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
    for token in (out.stdout + out.stderr).split():
        parts = token.split(".")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            return tuple(int(p) for p in parts)
    return None


def check_config(c: Checks) -> None:
    print("1. Configuration Vercel")
    if (ROOT / "vercel.json").exists() and "services" in json.loads((ROOT / "vercel.json").read_text()):
        c.ok("vercel.json (mode Services) à la racine")
    else:
        c.fail("vercel.json absent ou sans « services »")
    version = cli_version()
    if version is None:
        c.fail("CLI Vercel introuvable", "npm i -g vercel (ou brew install vercel-cli)")
    elif version < MIN_CLI:
        c.fail(f"CLI Vercel {'.'.join(map(str, version))} < 48.1.8", "mettre la CLI à jour")
    else:
        c.ok(f"CLI Vercel {'.'.join(map(str, version))}")
    # Le lien doit partir de la racine (vercel.json y est), pas de frontend/ (§2 du guide).
    if (ROOT / ".vercel" / "project.json").exists():
        c.ok("projet relié depuis la racine (.vercel/project.json)")
    else:
        c.fail("projet non relié depuis la racine",
               "cd <dépôt> && vercel link --project yugi-gang --scope gang-5d00 (guide §2)")
    ignored = subprocess.run(["git", "check-ignore", "-q", ".vercel/project.json"], cwd=ROOT).returncode == 0
    if ignored:
        c.ok(".vercel/ ignoré par Git (vercel pull y écrit des variables)")
    else:
        c.fail(".vercel/ n'est PAS ignoré par Git", "ajouter .vercel/ à .gitignore avant tout vercel pull")


def check_database(c: Checks, copy: bool) -> None:
    print("2. Base de service")
    data = data_dir()
    serving, source = data / "serving.db", data / "yugioh.db"
    if not serving.exists():
        c.fail(f"{serving} absente", "python scripts/build_serving_db.py")
        return
    stamp = datetime.fromtimestamp(serving.stat().st_mtime)
    c.ok(f"{serving} ({serving.stat().st_size / 1e6:.1f} Mo, construite le {stamp:%Y-%m-%d %H:%M})")
    conn = sqlite3.connect(f"file:{serving}?mode=ro", uri=True)
    present = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    missing = sorted(set(served_tables()) - present)
    if missing:
        c.fail(f"tables servies absentes de serving.db : {', '.join(missing)}", "python scripts/build_serving_db.py")
    else:
        c.ok("toutes les tables de SERVED_TABLES sont présentes")
    if source.exists() and source.stat().st_mtime > serving.stat().st_mtime:
        c.fail("serving.db est plus ancienne que yugioh.db (recalcul non reporté)",
               "python scripts/build_serving_db.py")
    elif source.exists():
        c.ok("serving.db plus récente que yugioh.db")
    else:
        c.warn("yugioh.db introuvable : fraîcheur non vérifiée")
    age = (datetime.now() - stamp).days
    if age > 8:
        c.warn(f"serving.db a {age} jours : le job du lundi a-t-il tourné ?")

    print("3. Copie embarquée dans l'API")
    rel = EMBEDDED_DB.relative_to(ROOT)
    if subprocess.run(["git", "check-ignore", "-q", str(rel)], cwd=ROOT).returncode != 0:
        c.fail(f"{rel} n'est pas ignoré par Git : copie refusée (dépôt public)")
        return
    c.ok(f"{rel} ignoré par Git")
    if EMBEDDED_DB.exists() and sha256(EMBEDDED_DB) == sha256(serving):
        c.ok(f"{rel} identique à la base de service")
    elif copy:
        EMBEDDED_DB.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(serving, EMBEDDED_DB)
        c.ok(f"{rel} copiée depuis {serving}")
    else:
        c.fail(f"{rel} absente ou différente", f"mkdir -p backend/data && cp {serving} {rel}")


def check_api(c: Checks, api_url: str) -> None:
    print("4. API locale (interrogée par le build du site)")
    probe = f"{api_url}/meta/tier-list"
    try:
        with urllib.request.urlopen(probe, timeout=10) as res:
            body = json.loads(res.read())
        c.ok(f"{probe} → 200")
        if isinstance(body, dict) and not any(body.values()):
            c.warn("réponse vide : l'API lit-elle la bonne base ?")
    except Exception as err:  # noqa: BLE001 — tout échec réseau se traite pareil
        c.fail(f"{probe} injoignable ({err.__class__.__name__})",
               f"cd backend && YGO_DB_PATH={data_dir() / 'serving.db'} ../.venv/bin/uvicorn app.main:app --port 8000")
    c.warn("l'API doit lire data/serving.db (YGO_DB_PATH), la base qui part en ligne : sinon le site "
           "construit et l'API déployée ne montrent pas les mêmes données")


def commands(target: str, api_url: str) -> list[list[str]]:
    env = "production" if target == "prod" else "preview"
    prod = ["--prod"] if target == "prod" else []
    # --prebuilt : les variables système (VERCEL_ENV…) manquent au build (doc `vercel deploy`).
    # VERCEL_ENV est donc passée à la main : lib/site.ts en tire noindex des aperçus.
    return [
        ["vercel", "pull", "--yes", f"--environment={env}"],
        ["env", f"API_URL={api_url}", f"VERCEL_ENV={env}", "vercel", "build", *prod],
        ["vercel", "deploy", "--prebuilt", "--archive=tgz", *prod],
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", choices=["preview", "prod"],
                        help="lance réellement les commandes Vercel (Thomas seulement)")
    parser.add_argument("--api-url", default=os.environ.get("API_URL", DEFAULT_API),
                        help=f"API locale lue par le build (défaut : API_URL, sinon {DEFAULT_API})")
    parser.add_argument("--no-copy", action="store_true",
                        help="ne copie pas la base dans backend/data/ (vérifie seulement)")
    args = parser.parse_args()
    api_url = args.api_url.rstrip("/")

    print(f"Déploiement voie 2 — {ROOT}\n")
    c = Checks()
    check_config(c)
    check_database(c, copy=not args.no_copy)
    check_api(c, api_url)

    print("\n5. Commandes (depuis la racine du dépôt)")
    for target, label in (("preview", "Prévisualisation (toujours d'abord)"), ("prod", "Production")):
        print(f"\n  # {label}")
        for cmd in commands(target, api_url):
            print("  " + shlex.join(cmd))

    if c.failed:
        print(f"\n✗ {len(c.failed)} vérification(s) en échec : corriger avant de déployer.")
    else:
        print("\n✓ Prérequis réunis.")

    if not args.execute:
        print("\nAucune commande Vercel lancée (mode par défaut). "
              "Pour les lancer : python scripts/deploy_prebuilt.py --execute preview")
        return 1 if c.failed else 0
    if c.failed:
        print("--execute refusé : des vérifications échouent.")
        return 1
    print(f"\n▶ Exécution ({args.execute})")
    for cmd in commands(args.execute, api_url):
        print("$ " + shlex.join(cmd), flush=True)
        if subprocess.run(cmd, cwd=ROOT).returncode != 0:
            print("✗ Commande en échec : arrêt.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
