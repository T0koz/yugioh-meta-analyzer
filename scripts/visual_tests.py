"""
Tests visuels du front (TOK-100) — une seule commande.

    python scripts/visual_tests.py                   # construit le site, capture, compare aux références
    python scripts/visual_tests.py --update          # régénère les images de référence (changement voulu)
    python scripts/visual_tests.py --only tier-list  # limite aux captures dont le nom contient ce texte
    python scripts/visual_tests.py --refresh-fixtures [--api http://localhost:8000/api/v1]
                                                     # réenregistre les réponses d'API figées, puis --update

Ce que fait la suite : 15 pages × 3 largeurs (375, 768, 1440 px), page entière, comparées pixel à pixel
aux images de `frontend/tests/visual/reference/`. En cas d'écart, l'image obtenue et l'image de
différence (pixels changés en rouge) sont écrites dans `frontend/tests/visual/output/` (hors Git).

Pourquoi les captures sont reproductibles :
- **Données figées.** Le site est construit contre une fausse API qui rejoue les réponses JSON de
  `frontend/tests/visual/fixtures/` : ni base ni backend, et le recalcul du lundi ne change rien.
  Le build va dans `frontend/.next-visual` (variable NEXT_DIST_DIR), sans toucher à `.next`.
- **Mouvement arrêté.** `prefers-reduced-motion: reduce` (le site s'y plie : pas de braises, pas de
  récit au défilement, pas d'apparition différée), plus animations et transitions CSS neutralisées.
- **Images de cartes remplacées** par un aplat : elles viennent de YGOPRODeck (réseau externe, TOK-92).
- **Graphe de synergies masqué** : sa mise en page (vis-network) part d'un tirage aléatoire.
- **Polices chargées** avant la capture (`document.fonts.ready`), fuseau et langue fixés.

Seuil (docs/tests-visuels.md) : un pixel compte comme changé si un canal s'écarte de plus de
PIXEL_TOLERANCE ; une capture échoue au-delà de MAX_DIFF_RATIO de pixels changés, ou si sa taille change.

Dépendances : le venv du projet (playwright, pillow, numpy), Chromium de Playwright
(`.venv/bin/playwright install chromium`) et `frontend/node_modules`. S'il en manque une, le script
sort en code 3 (« ignoré », pas « échoué ») : c'est ce que lit `scripts/check.py --visuel`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
VISUAL = FRONTEND / "tests" / "visual"
FIXTURES = VISUAL / "fixtures"
REFERENCE = VISUAL / "reference"
OUTPUT = VISUAL / "output"
DIST_DIR = ".next-visual"
API_PREFIX = "/api/v1"

WIDTHS = [375, 768, 1440]
VIEWPORT_HEIGHT = 900
# Archétypes dont la réponse est figée : un de la tier list, un qui n'existe que par son signal
# boutique. Les autres pages d'archétype répondent 404 pendant ce build (elles ne sont pas capturées).
ARCHETYPES = ["branded", "raise-moon"]
# Fiches de deck figées (TOK-114) : une avec profil (≥ 8 listes), une sous l'effectif minimal (listes seules).
DECKS = ["branded", "chaos-ritual"]
PAGES = [
    ("accueil", "/"),
    ("tier-list", "/tier-list"),
    ("evolution", "/evolution"),
    ("predictions", "/predictions"),
    ("boutique", "/boutique"),
    ("early-signals", "/early-signals"),
    ("graph", "/graph"),
    ("ban-radar", "/ban"),
    ("ban-historique", "/ban?tab=historique"),
    ("ban-impact", "/ban?tab=impact"),
    ("ban-simulateur", "/ban?tab=simulateur"),
    ("archetype-tcg", f"/archetype/{ARCHETYPES[0]}"),
    ("archetype-boutique", f"/archetype/{ARCHETYPES[1]}"),
    ("decks", "/decks"),
    ("deck-fiche", f"/decks/{DECKS[0]}"),
    ("deck-listes", f"/decks/{DECKS[1]}"),
]
# Zones masquées (aplat) : contenu qui ne peut pas être rendu deux fois à l'identique.
MASKS = {"graph": ["canvas"]}

# Bruit mesuré le 2026-11-16 : 0 pixel d'écart sur 36 captures, sur trois passages (docs/tests-visuels.md).
PIXEL_TOLERANCE = 16      # écart par canal (sur 255) en dessous duquel un pixel est tenu pour identique
MAX_DIFF_RATIO = 0.0001   # 0,01 % des pixels : une page de 1440 × 3000 tolère 432 pixels changés

EXIT_FAILED, EXIT_SKIPPED = 1, 3

FREEZE_CSS = """
*, *::before, *::after {
  animation: none !important;
  transition: none !important;
  caret-color: transparent !important;
  scroll-behavior: auto !important;
}
::-webkit-scrollbar { display: none; }
"""


def skip(reason: str) -> "NoReturn":  # noqa: F821
    print(f"⚠ Tests visuels ignorés : {reason}")
    sys.exit(EXIT_SKIPPED)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ── Fausse API : rejoue (ou enregistre) les réponses figées ────────────────────

def fixture_name(path: str) -> str:
    """« /api/v1/ban-radar?limit=3&kind=archetype » → « ban-radar__kind-archetype_limit-3.json »."""
    parts = urlsplit(path)
    name = parts.path.removeprefix(API_PREFIX).strip("/").replace("/", "__")
    query = "_".join(f"{k}-{v}" for k, v in sorted(parse_qsl(parts.query)))
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", f"{name}__{query}" if query else name).lower() + ".json"


def make_handler(record_from: str | None):
    class Handler(BaseHTTPRequestHandler):
        missing: set[str] = set()

        def log_message(self, *args) -> None:  # silence
            pass

        def _send(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if "/archetypes/" in path and path.rsplit("/", 1)[-1].lower() not in ARCHETYPES:
                return self._send(404, b'{"detail":"hors du jeu de donnees fige"}')
            if "/decks/" in path and path.rsplit("/", 1)[-1].lower() not in DECKS:
                return self._send(404, b'{"detail":"hors du jeu de donnees fige"}')
            file = FIXTURES / fixture_name(self.path)
            if record_from:
                url = record_from.rstrip("/") + self.path.removeprefix(API_PREFIX)
                try:
                    with urllib.request.urlopen(url, timeout=30) as res:
                        data = json.load(res)
                except urllib.error.HTTPError as err:
                    return self._send(err.code, b'{"detail":"erreur de l API"}')
                file.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
            if not file.exists():
                Handler.missing.add(self.path)
                return self._send(404, b'{"detail":"reponse non figee"}')
            self._send(200, file.read_bytes())

    return Handler


def start_mock_api(record_from: str | None) -> tuple[ThreadingHTTPServer, type]:
    handler = make_handler(record_from)
    # Le build de Next interroge l'API depuis une dizaine de processus à la fois : la file
    # d'attente par défaut (5 connexions) en refuse une partie (ECONNRESET).
    ThreadingHTTPServer.request_queue_size = 256
    server = ThreadingHTTPServer(("127.0.0.1", free_port()), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, handler


# ── Site : build de production dédié, puis serveur ─────────────────────────────

def build_and_start(api_url: str) -> tuple[subprocess.Popen, str]:
    env = {
        **os.environ,
        "NEXT_PUBLIC_API_URL": api_url,
        "NEXT_PUBLIC_SITE_URL": "http://localhost:3000",
        "NEXT_DIST_DIR": DIST_DIR,
        "NEXT_TELEMETRY_DISABLED": "1",
    }
    # Le cache de fetch de Next survivrait à un changement de données figées. Le reste du dossier
    # est gardé : il accélère le build suivant.
    shutil.rmtree(FRONTEND / DIST_DIR / "cache" / "fetch-cache", ignore_errors=True)
    print("▶ Build de production contre les données figées…", flush=True)
    # next/font télécharge les polices chez Google à chaque build : une coupure réseau passagère
    # le fait échouer (observé une fois sur cinq le 2026-11-16), d'où trois essais. Si le réseau
    # reste coupé, la suite est « ignorée » : ce n'est pas un écart visuel.
    for attempt in (1, 2, 3):
        build = subprocess.run(["npm", "run", "build"], cwd=FRONTEND, env=env, capture_output=True, text=True)
        if build.returncode == 0:
            break
        output = build.stdout + build.stderr
        if "internal/font/google" not in output:
            print(output[-3000:])
            print("✗ Le build a échoué.")
            sys.exit(EXIT_FAILED)
        if attempt == 3:
            skip("polices Google injoignables pendant le build (réseau) : relancer plus tard")
        print(f"  (polices Google injoignables, essai {attempt + 1} sur 3)", flush=True)
        time.sleep(5)
    port = free_port()
    server = subprocess.Popen(
        ["npx", "next", "start", "-p", str(port)], cwd=FRONTEND, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            urllib.request.urlopen(base + "/robots.txt", timeout=2)
            return server, base
        except OSError:
            time.sleep(0.3)
    server.terminate()
    print("✗ Le serveur Next n'a pas démarré.")
    sys.exit(EXIT_FAILED)


# ── Captures ───────────────────────────────────────────────────────────────────

def placeholder_png() -> bytes:
    """Aplat qui remplace toute image de carte (couleur du token --ink-4, lue dans globals.css)."""
    import io
    from PIL import Image
    css = (FRONTEND / "src" / "app" / "globals.css").read_text()
    color = re.search(r"--ink-4:\s*(#[0-9a-fA-F]{6})", css).group(1)
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color).save(buffer, "PNG")
    return buffer.getvalue()


def capture_all(base: str, targets: list[tuple[str, str]]) -> dict[str, bytes]:
    from playwright.sync_api import Error, sync_playwright

    image = placeholder_png()
    shots: dict[str, bytes] = {}
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Error as err:
            skip(f"Chromium de Playwright absent → .venv/bin/playwright install chromium ({str(err).splitlines()[0]})")
        for width in WIDTHS:
            context = browser.new_context(
                viewport={"width": width, "height": VIEWPORT_HEIGHT},
                device_scale_factor=1,
                reduced_motion="reduce",
                color_scheme="dark",
                locale="fr-FR",
                timezone_id="Europe/Paris",
            )
            # Aucune requête ne sort de la machine : images de cartes → aplat, le reste est coupé.
            def route(r):
                url = r.request.url
                try:
                    if "/_next/image" in url or (not url.startswith(base) and r.request.resource_type == "image"):
                        r.fulfill(status=200, content_type="image/png", body=image)
                    elif url.startswith(base) or url.startswith("data:"):
                        r.continue_()
                    else:
                        r.abort()
                except Error:
                    pass  # requête annulée par un changement de page : rien à servir
            context.route("**/*", route)
            page = context.new_page()
            for name, path in targets:
                page.goto(base + path, wait_until="networkidle")
                page.add_style_tag(content=FREEZE_CSS)
                page.evaluate("document.fonts.ready")
                # Un aller-retour jusqu'en bas déclenche tout ce qui attend d'entrer dans l'écran.
                page.evaluate(
                    """async () => {
                        for (let y = 0; y < document.body.scrollHeight; y += 600) {
                            window.scrollTo(0, y);
                            await new Promise((r) => requestAnimationFrame(r));
                        }
                        window.scrollTo(0, 0);
                        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
                    }"""
                )
                page.wait_for_load_state("networkidle")
                shots[f"{name}-{width}"] = page.screenshot(
                    full_page=True,
                    animations="disabled",
                    caret="hide",
                    mask=[page.locator(sel) for sel in MASKS.get(name, [])],
                    mask_color="#000000",
                )
            context.close()
        browser.close()
    return shots


def compare(name: str, actual_png: bytes) -> tuple[bool, str]:
    """(réussi, message). Écrit l'image obtenue et la différence en cas d'écart."""
    import io
    import numpy as np
    from PIL import Image

    reference_path = REFERENCE / f"{name}.webp"
    if not reference_path.exists():
        return False, "pas d'image de référence (lancer avec --update)"
    actual = Image.open(io.BytesIO(actual_png)).convert("RGB")
    reference = Image.open(reference_path).convert("RGB")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if actual.size != reference.size:
        actual.save(OUTPUT / f"{name}-obtenu.png")
        return False, f"taille {actual.size[0]}×{actual.size[1]}, référence {reference.size[0]}×{reference.size[1]}"
    a, r = np.asarray(actual, dtype=np.int16), np.asarray(reference, dtype=np.int16)
    changed = np.abs(a - r).max(axis=2) > PIXEL_TOLERANCE
    ratio = float(changed.mean())
    if ratio <= MAX_DIFF_RATIO:
        return True, f"{int(changed.sum())} px"
    actual.save(OUTPUT / f"{name}-obtenu.png")
    # Différence : la capture assombrie, les pixels changés en rouge vif.
    diff = (a * 0.35).astype(np.uint8)
    diff[changed] = (255, 0, 60)
    Image.fromarray(diff).save(OUTPUT / f"{name}-diff.png")
    return False, f"{int(changed.sum())} px changés ({ratio:.3%}, seuil {MAX_DIFF_RATIO:.2%})"


def write_reference(name: str, png: bytes) -> None:
    import io
    from PIL import Image
    REFERENCE.mkdir(parents=True, exist_ok=True)
    # WebP sans perte : mêmes pixels qu'un PNG, pour 3,5 Mo au lieu de 12,4 Mo (mesuré sur 36 captures).
    Image.open(io.BytesIO(png)).convert("RGB").save(REFERENCE / f"{name}.webp", lossless=True, method=4)


# ── Point d'entrée ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--update", action="store_true", help="régénérer les images de référence")
    parser.add_argument("--only", help="ne traiter que les captures dont le nom contient ce texte")
    parser.add_argument("--refresh-fixtures", action="store_true",
                        help="réenregistrer les réponses d'API figées depuis une API réelle (implique --update)")
    parser.add_argument("--api", default="http://localhost:8000/api/v1", help="API réelle lue par --refresh-fixtures")
    args = parser.parse_args()

    try:
        import numpy  # noqa: F401
        import PIL  # noqa: F401
        import playwright  # noqa: F401
    except ImportError as err:
        skip(f"module Python manquant ({err.name}) → lancer avec le venv du projet : .venv/bin/python scripts/visual_tests.py")
    if not (FRONTEND / "node_modules").exists():
        skip("frontend/node_modules absent → cd frontend && npm install")

    started = time.monotonic()
    if args.refresh_fixtures:
        if args.only:
            parser.error("--refresh-fixtures réenregistre tout : incompatible avec --only")
        shutil.rmtree(FIXTURES, ignore_errors=True)
    elif not FIXTURES.exists():
        print("✗ Données figées absentes : frontend/tests/visual/fixtures/ (--refresh-fixtures pour les créer).")
        return EXIT_FAILED
    FIXTURES.mkdir(parents=True, exist_ok=True)
    update = args.update or args.refresh_fixtures

    targets = [(name, path) for name, path in PAGES if not args.only or args.only in name]
    if not targets:
        parser.error(f"aucune page ne correspond à « {args.only} »")

    mock, handler = start_mock_api(args.api if args.refresh_fixtures else None)
    api_url = f"http://127.0.0.1:{mock.server_address[1]}{API_PREFIX}"
    server, base = build_and_start(api_url)
    try:
        print(f"▶ {len(targets)} pages × {len(WIDTHS)} largeurs ({', '.join(map(str, WIDTHS))} px)…", flush=True)
        shots = capture_all(base, targets)
    finally:
        server.terminate()
        server.wait(timeout=10)
        mock.shutdown()

    if handler.missing:
        print("✗ Requêtes sans réponse figée (lancer --refresh-fixtures) :")
        for path in sorted(handler.missing):
            print(f"    {path}")
        return EXIT_FAILED

    if update:
        if not args.only:  # une référence dont la page a disparu ne doit pas rester
            shutil.rmtree(REFERENCE, ignore_errors=True)
        for name, png in shots.items():
            write_reference(name, png)
        total = sum(f.stat().st_size for f in REFERENCE.glob("*.webp"))
        print(f"✓ {len(shots)} images de référence écrites ({total / 1e6:.1f} Mo au total dans {REFERENCE.relative_to(ROOT)}).")
        print("  À relire puis à commiter avec le changement qui les justifie.")
        return 0

    shutil.rmtree(OUTPUT, ignore_errors=True)
    failures = []
    for name, png in shots.items():
        ok, message = compare(name, png)
        print(f"  {'✓' if ok else '✗'} {name} : {message}")
        if not ok:
            failures.append(name)
    duration = time.monotonic() - started
    if failures:
        print(f"\n✗ {len(failures)} capture(s) sur {len(shots)} diffèrent de la référence ({duration:.0f} s).")
        print(f"  Images obtenues et différences : {OUTPUT.relative_to(ROOT)}/")
        print("  Changement voulu ? Relire les différences, puis : python scripts/visual_tests.py --update")
        return EXIT_FAILED
    print(f"\n✓ {len(shots)} captures identiques aux références ({duration:.0f} s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
