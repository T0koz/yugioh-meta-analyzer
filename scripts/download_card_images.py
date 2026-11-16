"""Télécharge une fois les images de cartes et en tire trois tailles (TOK-92, décision 7).

    python scripts/download_card_images.py --limit 50     # essai
    python scripts/download_card_images.py                # tout ce qui manque (reprenable)
    python scripts/download_card_images.py --retry-missing  # retente les 404 déjà notés

Sources (domaine d'images déjà utilisé par le projet, jamais par le navigateur de l'internaute) :
    images/cards/{id}.jpg          carte entière
    images/cards_cropped/{id}.jpg  illustration seule (carrée)

Sorties (dossier ignoré par Git, `CARD_IMAGES_DIR`, défaut `<dépôt principal>/data/card-images`) :
    card-lg/{id}.webp   carte entière, 421 px de large (hero, carte vedette)
    card-sm/{id}.webp   carte entière, 168 px de large (vignettes de carte)
    art/{id}.webp       illustration carrée, 256 px (pastilles, lignes de liste)
    _missing.json       ids absents de la source (404) : non retentés sans --retry-missing
    _failures.jsonl     journal des échecs (réseau, fichier qui n'est pas une image)

Un second lancement ne télécharge rien : un id est sauté quand ses trois fichiers existent.
Les fichiers reçus sont des données : ils ne sont décodés que par Pillow, après contrôle du type et de la taille.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://images.ygoprodeck.com/images"
UA = "card-image-sync/1.0"
MAX_RPS = 15            # plafond du brief : 20 requêtes par seconde
MAX_BYTES = 3_000_000   # une image de carte pèse < 300 ko ; au-delà, ce n'est pas une carte
MAX_PIXELS = 4_000_000
TIMEOUT = 20

SIZES = {  # dossier -> (source, largeur max, hauteur max)
    "card-lg": ("cards", 421, 614),
    "card-sm": ("cards", 168, 246),
    "art": ("cards_cropped", 256, 256),
}


def main_checkout() -> Path:
    """Le dépôt principal : les images doivent survivre à la suppression d'un worktree."""
    try:
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        return Path(common).parent
    except Exception:
        return ROOT


def default_db() -> Path:
    for base in (ROOT, main_checkout()):
        p = base / "data" / "yugioh.db"
        if p.exists():
            return p
    return ROOT / "data" / "yugioh.db"


class Limiter:
    def __init__(self, rps: float):
        self.gap = 1.0 / rps
        self.lock = threading.Lock()
        self.next = 0.0

    def wait(self):
        with self.lock:
            now = time.monotonic()
            t = max(now, self.next)
            self.next = t + self.gap
        if t > now:
            time.sleep(t - now)


def fetch(session: requests.Session, limiter: Limiter, url: str) -> bytes | None:
    """Octets de l'image, None si 404. Lève après 3 essais."""
    last = None
    for attempt in range(3):
        limiter.wait()
        try:
            r = session.get(url, timeout=TIMEOUT, stream=True)
            if r.status_code == 404:
                return None
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(5 * (attempt + 1))
                last = RuntimeError(f"HTTP {r.status_code}")
                continue
            r.raise_for_status()
            if "image" not in r.headers.get("Content-Type", ""):
                raise RuntimeError(f"type inattendu : {r.headers.get('Content-Type')}")
            data = r.raw.read(MAX_BYTES + 1, decode_content=True)
            if len(data) > MAX_BYTES:
                raise RuntimeError("fichier trop gros")
            return data
        except Exception as exc:  # réseau, délai : on retente avec pause
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(str(last))


def decode(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    if img.format not in ("JPEG", "PNG", "WEBP"):
        raise RuntimeError(f"format inattendu : {img.format}")
    if img.width * img.height > MAX_PIXELS:
        raise RuntimeError("dimensions inattendues")
    img.load()
    return img.convert("RGB")


def save(img: Image.Image, path: Path, w: int, h: int, quality: int):
    out = img.copy()
    out.thumbnail((w, h), Image.LANCZOS)  # ne grossit jamais
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    out.save(tmp, "WEBP", quality=quality, method=6)
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", type=Path, default=default_db())
    ap.add_argument("--dest", type=Path, default=Path(os.environ.get("CARD_IMAGES_DIR") or main_checkout() / "data" / "card-images"))
    ap.add_argument("--limit", type=int, default=0, help="n'en traite que n (essai)")
    ap.add_argument("--retry-missing", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    ids = [r[0] for r in con.execute("SELECT id FROM cards ORDER BY id")]
    con.close()

    dest: Path = a.dest
    dest.mkdir(parents=True, exist_ok=True)
    miss_path = dest / "_missing.json"
    missing: dict[str, list[str]] = json.loads(miss_path.read_text()) if miss_path.exists() else {}

    def done(i: int) -> bool:
        return all((dest / d / f"{i}.webp").exists() for d in SIZES)

    todo = [i for i in ids if not done(i) and (a.retry_missing or str(i) not in missing)]
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(ids)} cartes, {len(todo)} à télécharger, destination {dest}", flush=True)
    if not todo:
        print("Rien à faire.")
        return 0

    limiter = Limiter(MAX_RPS)
    stats = {"ok": 0, "missing": 0, "fail": 0, "requests": 0}
    lock = threading.Lock()
    local = threading.local()
    fail_log = (dest / "_failures.jsonl").open("a", encoding="utf-8")
    t0 = time.time()

    def work(i: int):
        s = getattr(local, "s", None)
        if s is None:
            s = local.s = requests.Session()
            s.headers["User-Agent"] = UA
        try:
            src: dict[str, Image.Image | None] = {}
            for kind in {v[0] for v in SIZES.values()}:
                with lock:
                    stats["requests"] += 1
                data = fetch(s, limiter, f"{BASE}/{kind}/{i}.jpg")
                src[kind] = decode(data) if data is not None else None
            absent = [k for k, v in src.items() if v is None]
            if absent:
                with lock:
                    missing[str(i)] = absent
                    stats["missing"] += 1
            for d, (kind, w, h) in SIZES.items():
                if src[kind] is not None:
                    save(src[kind], dest / d / f"{i}.webp", w, h, 82 if d != "art" else 80)
            with lock:
                stats["ok"] += 1
        except Exception as exc:
            with lock:
                stats["fail"] += 1
                fail_log.write(json.dumps({"id": i, "error": str(exc)[:200]}) + "\n")
                fail_log.flush()
        with lock:
            n = stats["ok"] + stats["fail"]
            if n % 500 == 0:
                print(f"  {n}/{len(todo)}  échecs {stats['fail']}  {time.time() - t0:.0f} s", flush=True)
                miss_path.write_text(json.dumps(missing))

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, todo))
    miss_path.write_text(json.dumps(missing))
    fail_log.close()
    dur = time.time() - t0
    print(f"Terminé en {dur:.0f} s : {stats['ok']} traitées, {stats['missing']} avec une variante absente (404), "
          f"{stats['fail']} échecs, {stats['requests']} requêtes ({stats['requests'] / max(dur, 1):.1f}/s)")
    return 1 if stats["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
