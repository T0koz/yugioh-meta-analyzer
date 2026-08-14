"""
Reconstruit `banlist_history` depuis Yugipedia — listes TCG **et** OCG.

    python scripts/fetch_banlist_history.py
    python scripts/fetch_banlist_history.py --dry-run

Reprend le scraping du notebook 09 (TOK-8) en y ajoutant deux choses :

- **Les listes OCG.** Le Ban Radar n'avait qu'un seul point de backtest TCG
  exploitable. Les listes OCG sont trimestrielles et la base couvre bien les
  decks OCG depuis février 2026, ce qui ouvre des points de mesure
  supplémentaires (voir `build_ban_radar.py --backtest`).
- **Une colonne `format`.** Le filtre `list_name LIKE '%TCG%'` utilisé jusqu'ici
  laissait de côté 33 listes TCG antérieures à 2021, que Yugipedia nomme sans
  suffixe (« September 2020 Lists »). Le format vient maintenant de la catégorie
  d'origine, plus du nom de la page.

La table est reconstruite intégralement à chaque exécution : Yugipedia est la
source de vérité, et les listes passées sont amendées rétroactivement.
"""

import argparse
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

DB = Path(__file__).resolve().parents[1] / "data" / "yugioh.db"
API = "https://yugipedia.com/api.php"
HEADERS = {"User-Agent": "yugioh-meta-analyzer (contact: thomascozianpro@gmail.com)"}

CATEGORIES = {
    "TCG": "Category:TCG Advanced Format Forbidden & Limited Lists",
    "OCG": "Category:OCG Forbidden & Limited Lists",
}

STATUS_KEYS = [("forbidden", "Forbidden"), ("limited", "Limited"), ("semi_limited", "Semi-Limited")]
DATE_FORMATS = ("%B %d, %Y", "%Y-%m-%d", "%d %B %Y")
REQUEST_PAUSE_SEC = 0.4
MAX_ATTEMPTS = 3


def parse_date(raw: str) -> str | None:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_banlist_wikitext(title: str, fmt: str, text: str) -> list[dict]:
    rows = []
    start = re.search(r"\|\s*start_date\s*=\s*(.+)", text)
    end = re.search(r"\|\s*end_date\s*=\s*(.+)", text)
    effective_date = parse_date(start.group(1)) if start else None
    end_date = parse_date(end.group(1)) if end else None

    for status_key, status_label in STATUS_KEYS:
        pattern = (
            r"\|\s*" + status_key + r"\s*=\s*(.*?)(?=\|\s*(?:forbidden|limited|semi_limited|unlimited"
            r"|notes|prev|next|start_date|end_date|medium|format)\s*=|\}\})"
        )
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if not match:
            continue
        for line in match.group(1).split("\n"):
            card = re.sub(r"//.*$", "", line)
            card = re.sub(r"\[\[|\]\]", "", card).strip()
            if not card or card[0] in "|*{":
                continue
            rows.append(
                {
                    "list_name": title,
                    "format": fmt,
                    "effective_date": effective_date,
                    "end_date": end_date,
                    "card_name": card,
                    "status": status_label,
                }
            )
    return rows


def list_pages(category: str) -> list[str]:
    response = requests.get(
        API,
        params={
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": "500",
            "format": "json",
        },
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    members = response.json()["query"]["categorymembers"]
    # La catégorie OCG contient aussi des sous-catégories régionales
    # (coréen, chinois simplifié…) qui ne sont pas des listes.
    return [m["title"] for m in members if not m["title"].startswith("Category:")]


def fetch_wikitext(title: str) -> str:
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(
                API,
                params={"action": "parse", "page": title, "prop": "wikitext", "format": "json"},
                headers=HEADERS,
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("parse", {}).get("wikitext", {}).get("*", "")
        except Exception:
            if attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(2)
    return ""


def scrape() -> pd.DataFrame:
    rows: list[dict] = []
    errors: list[str] = []

    for fmt, category in CATEGORIES.items():
        titles = list_pages(category)
        print(f"{fmt} : {len(titles)} listes")
        for index, title in enumerate(titles, start=1):
            try:
                rows.extend(parse_banlist_wikitext(title, fmt, fetch_wikitext(title)))
            except Exception as exc:
                errors.append(f"{title}: {exc}")
            time.sleep(REQUEST_PAUSE_SEC)
            if index % 20 == 0:
                print(f"  [{index}/{len(titles)}] {len(rows)} entrées...")

    if errors:
        print(f"\n⚠ {len(errors)} pages en échec : {errors[:5]}")
    return pd.DataFrame(rows)


def save(df: pd.DataFrame) -> None:
    con = sqlite3.connect(DB)
    con.executescript(
        """
        DROP TABLE IF EXISTS banlist_history;
        CREATE TABLE banlist_history (
            list_name      TEXT,
            format         TEXT,
            effective_date TEXT,
            end_date       TEXT,
            card_name      TEXT,
            status         TEXT
        );
        """
    )
    df.to_sql("banlist_history", con, if_exists="append", index=False)
    con.executescript(
        """
        CREATE INDEX idx_banlist_card ON banlist_history(card_name);
        CREATE INDEX idx_banlist_date ON banlist_history(effective_date);
        CREATE INDEX idx_banlist_format ON banlist_history(format, effective_date);
        """
    )
    con.commit()
    con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Affiche le résumé sans écrire")
    args = parser.parse_args()

    df = scrape()
    if df.empty:
        raise SystemExit("Aucune entrée récupérée — scraping en échec")

    print(f"\n{len(df):,} entrées, {df.card_name.nunique():,} cartes uniques")
    print(df.groupby("format").agg(
        listes=("list_name", "nunique"),
        entrees=("card_name", "size"),
        depuis=("effective_date", "min"),
        jusqu_a=("effective_date", "max"),
    ).to_string())

    if args.dry_run:
        return

    save(df)
    print(f"\n✓ banlist_history reconstruite ({len(df):,} lignes)")


if __name__ == "__main__":
    main()
