"""
Prépare une copie de `data/yugioh.db` à transmettre en privé (jamais par Git).

    python scripts/export_db_snapshot.py                      # → ~/Desktop/yugioh-AAAA-MM-JJ.db.gz
    python scripts/export_db_snapshot.py --dest ~/Downloads
    python scripts/export_db_snapshot.py --sans-auteurs       # pseudos des joueurs effacés

Produit deux fichiers, à envoyer ensemble :
- `yugioh-AAAA-MM-JJ.db.gz` : la base, compressée (~250 Mo → ~50 Mo) ;
- `yugioh-AAAA-MM-JJ.json`  : de quand elle date (dernier tournoi TCG / OCG, dernière
  banlist) et son empreinte SHA-256, pour vérifier qu'elle est arrivée intacte.

Pourquoi `VACUUM INTO` plutôt qu'une copie du fichier : un `cp` pendant que le job du
lundi ou le backend écrit peut produire une base corrompue. `VACUUM INTO` lit une vue
cohérente et écrit une base compactée. La base source est ouverte en lecture seule.

`--sans-auteurs` vide `tournament_decks.author` (≈ 15 000 pseudos de joueurs, donnée
personnelle). Aucune analyse ne la lit : seuls les scripts de fetch l'écrivent.
Mode d'emploi complet : docs/collaboration/transmission-base.md
"""

import argparse
import gzip
import hashlib
import json
import shutil
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DB = ROOT / "data" / "yugioh.db"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", type=Path, default=Path.home() / "Desktop", help="dossier de sortie (hors du dépôt)")
    parser.add_argument("--sans-auteurs", action="store_true", help="efface les pseudos des joueurs")
    args = parser.parse_args()

    if not SOURCE_DB.exists():
        raise SystemExit(f"Base absente : {SOURCE_DB}")
    dest = args.dest.expanduser().resolve()
    if dest == ROOT or ROOT in dest.parents:
        raise SystemExit("Le dossier de sortie doit être hors du dépôt (il est public).")
    dest.mkdir(parents=True, exist_ok=True)

    stem = f"yugioh-{date.today().isoformat()}"
    raw = dest / f"{stem}.db"
    raw.unlink(missing_ok=True)

    source = sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True)
    source.execute("VACUUM INTO ?", (str(raw),))
    facts = {
        "copie_du": date.today().isoformat(),
        "dernier_tournoi_tcg": source.execute(
            "SELECT MAX(created) FROM tournament_decks WHERE ocg = 0").fetchone()[0],
        "dernier_tournoi_ocg": source.execute(
            "SELECT MAX(created) FROM tournament_decks WHERE ocg = 1").fetchone()[0],
        "derniere_banlist": dict(source.execute(
            "SELECT format, MAX(effective_date) FROM banlist_history GROUP BY format").fetchall()),
        "decks": source.execute("SELECT COUNT(*) FROM tournament_decks").fetchone()[0],
    }
    source.close()

    if args.sans_auteurs:
        with sqlite3.connect(raw) as copy:
            copy.execute("UPDATE tournament_decks SET author = NULL")
        with sqlite3.connect(raw) as copy:
            copy.execute("VACUUM")  # sinon les pseudos restent lisibles dans les pages libérées
    facts["auteurs"] = "effacés" if args.sans_auteurs else "présents (donnée personnelle : ne pas republier)"

    packed = dest / f"{stem}.db.gz"
    with raw.open("rb") as src, gzip.open(packed, "wb", compresslevel=6) as out:
        shutil.copyfileobj(src, out, 1 << 20)
    raw.unlink()

    facts["fichier"] = packed.name
    facts["sha256"] = sha256(packed)
    facts["taille_mo"] = round(packed.stat().st_size / 1e6, 1)
    manifest = dest / f"{stem}.json"
    manifest.write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n")

    print(f"✓ {packed}  ({facts['taille_mo']} Mo)")
    print(f"✓ {manifest}")
    print(json.dumps(facts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
