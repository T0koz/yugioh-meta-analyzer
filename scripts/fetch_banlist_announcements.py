"""
TOK-121 — Dates d'annonce des banlists (TCG et OCG) : table `banlist_announcements`.

    python scripts/fetch_banlist_announcements.py                  # écrit la table (après sauvegarde)
    python scripts/fetch_banlist_announcements.py --dry-run        # affiche, n'écrit rien
    python scripts/fetch_banlist_announcements.py --db <chemin>    # autre base (copie, worktree)
    python scripts/fetch_banlist_announcements.py --no-backup      # sans copie de sauvegarde

Pourquoi : `banlist_history` ne connaît que la date d'**entrée en vigueur**. Le backtest du Ban Radar classe « la
veille » de cette date : les decks joués entre l'annonce et l'entrée en vigueur sont dans la fenêtre (diagnostic
TOK-115, question 4). Ce script collecte la date d'annonce pour mesurer ce biais (`diagnose_ban_radar.py
--as-of announcement`). **Il ne modifie ni `banlist_history` ni le calcul du backtest.**

Source : Yugipedia (page de chaque liste), qui cite les sources primaires (comptes officiels de Konami, vidéos des
YCS, YGOrganization, Beyond the Duel). Le texte d'introduction de la page est lu, la phrase et la référence sont
conservées dans la table (`evidence`, `cited_url`). Le site officiel de Konami ne publie pas de date d'annonce
exploitable pour les listes passées : il n'est cité que lorsque Yugipedia renvoie vers lui (comptes officiels).

Deux notions, qu'il faut séparer (constat du lot 21) : **annoncer qu'une liste va sortir** (Konami OCG publie la
date de la prochaine liste une dizaine de jours avant son contenu ; Konami TCG a annoncé le 10 juillet 2024 la date de
la liste de septembre, publiée le 31 août) et **rendre public le contenu** (les cartes touchées). Seule la seconde
change ce que les joueurs peuvent anticiper : c'est elle que le backtest doit couper. Yugipedia écrit « first
announced on » pour l'une ou l'autre selon la page (les listes OCG de 2026 portent la date de la première).

Champs, du plus sûr au plus faible. **Aucune date n'est devinée** : un champ sans preuve reste vide.

- `announced_date` : ce que la page Yugipedia dit (« first announced on March 24, 2024 »). `announced_precision` =
  `jour`, `jour_deduit` (« on the day prior », confirmé par la date d'une référence citée) ou `debut_evenement`
  (« on the weekend of October 16 », jour exact non précisé). `announced_kind` = `liste` (le contenu) ou
  `date_seule` (une source citée, titrée « Announcement », « Date For… » ou « To Be Revealed », porte cette même
  date : c'est la date de sortie annoncée, pas les cartes).
- `full_list_date` : la page dit quand la liste complète a été publiée, si elle diffère.
- `first_source_date` : date de la plus ancienne source citée qui **reprend le contenu** de la liste (titre sans
  « Announcement », sans mois d'une autre liste). **Borne haute** : le contenu était public ce jour-là ou avant.
- `content_date` : le jour où les cartes touchées sont devenues publiques, quand la page le permet : la date de
  `announced_date` si `announced_kind = liste`, sinon `full_list_date`, sinon `first_source_date` (`content_basis` le
  dit). Vide quand aucune phrase de la page ne donne d'annonce : la borne haute reste dans `first_source_date`.
- `missing_reason` : si `content_date` est vide, pourquoi.

La table est reconstruite à chaque exécution (Yugipedia fait foi, les pages sont amendées) dans une transaction
unique ; une erreur réseau sur une page garde la ligne précédente de cette liste (jamais de ligne perdue en silence).
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "yugioh.db"
API = "https://yugipedia.com/api.php"
PAGE_URL = "https://yugipedia.com/wiki/"
HEADERS = {"User-Agent": "yugioh-meta-analyzer (personal research project)"}
REQUEST_PAUSE_SEC = 0.5
MAX_ATTEMPTS = 6
# Une source citée plus de ~4 mois avant l'entrée en vigueur n'est pas une source sur cette liste.
MAX_LEAD_DAYS = 120

SCHEMA = """
CREATE TABLE IF NOT EXISTS banlist_announcements (
    format              TEXT NOT NULL,   -- TCG | OCG
    list_name           TEXT NOT NULL,   -- nom de la page Yugipedia, comme banlist_history.list_name
    effective_date      TEXT NOT NULL,   -- entrée en vigueur (jointure avec banlist_history.effective_date)
    announced_date      TEXT,            -- première annonce publique, si la page la donne
    announced_precision TEXT,            -- jour | jour_deduit | debut_evenement
    announced_kind      TEXT,            -- liste | date_seule
    full_list_date      TEXT,            -- liste complète publique, si différente
    first_source_date   TEXT,            -- plus ancienne source citée qui reprend la liste : borne haute
    content_date        TEXT,            -- jour où les cartes touchées sont devenues publiques
    content_basis       TEXT,            -- annonce_yugipedia | liste_complete | article_de_la_liste
    source              TEXT NOT NULL,   -- yugipedia
    source_url          TEXT NOT NULL,   -- page Yugipedia lue
    cited_source        TEXT,            -- konami | ygorganization | beyondtheduel | autre
    cited_url           TEXT,            -- source datée du jour retenu (content_date, sinon first_source_date)
    evidence            TEXT,            -- phrase relevée sur la page
    missing_reason      TEXT,            -- si content_date est vide
    fetched_at          TEXT NOT NULL,
    PRIMARY KEY (format, list_name)
);
CREATE INDEX IF NOT EXISTS idx_banlist_ann_eff ON banlist_announcements(format, effective_date);
"""

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_RE = rf"(?P<m>{MONTHS})\s+(?P<d>\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(?P<y>\d{{4}}))?"
REF_RE = re.compile(r"<ref\b([^>/]*)(?:/>|>(.*?)</ref>)", re.S)
CITE_FIELD = re.compile(r"\|\s*([\w-]+)\s*=\s*(.*?)(?=\s*\|\s*[\w-]+\s*=|\}\}|$)", re.S)


def parse_date(month: str, day: str, year: str | None) -> date | None:
    if not year:
        return None
    try:
        return datetime.strptime(f"{month} {int(day)} {year}", "%B %d %Y").date()
    except ValueError:
        return None


def parse_ref(body: str) -> dict:
    """Champs d'un `{{cite web | ... }}` : url, title, date (date de publication, pas d'archivage)."""
    fields = {k.strip().lower(): v.strip() for k, v in CITE_FIELD.findall(body or "")}
    out = {"url": fields.get("url"), "title": fields.get("title", ""), "date": None}
    m = re.fullmatch(DATE_RE, fields.get("date", "").strip())
    if m:
        out["date"] = parse_date(m["m"], m["d"], m["y"])
    return out


def cited_kind(url: str | None) -> str | None:
    if not url:
        return None
    u = url.lower()
    if "yugioh-card.com" in u or "yu-gi-oh.jp" in u or "x.com/yugioh_tcg" in u or "x.com/yugiohcardeu" in u or "twitter.com/yugioh" in u:
        return "konami"
    if "youtube.com" in u:
        return "konami"  # chaîne officielle « Yu-Gi-Oh! TRADING CARD GAME » (déclarée dans `publisher`)
    if "ygorganization.com" in u:
        return "ygorganization"
    if "beyondtheduel.com" in u:
        return "beyondtheduel"
    return "autre"


def split_head(wikitext: str) -> str:
    """Texte avant le modèle `{{Limitation list`, sans la liste de cartes."""
    i = wikitext.find("{{Limitation list")
    return wikitext[: i if i > 0 else 3000]


def extract(fmt: str, list_name: str, effective: date, head: str) -> dict:
    """Lit l'introduction d'une page. Renvoie les champs de la table (sans `fetched_at`).

    Chaque référence est remplacée par un repère `§i§` : le texte devient lisible (les points des adresses
    ne coupent plus les phrases) et on sait quelle référence suit quelle phrase.
    """
    refs: list[dict] = []

    def mark(m: re.Match) -> str:
        refs.append(parse_ref(m.group(2) or ""))
        return f"§{len(refs) - 1}§"

    flat = REF_RE.sub(mark, head)
    flat = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", flat)
    flat = re.sub(r"'{2,}", "", flat)

    def clean(txt: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"§\d+§", "", txt)).strip()

    def ref_following(pos: int) -> dict | None:
        m = re.compile(r"§(\d+)§").search(flat, pos)
        return refs[int(m.group(1))] if m else None

    row = {"format": fmt, "list_name": list_name, "effective_date": effective.isoformat(),
           "announced_date": None, "announced_precision": None, "announced_kind": None,
           "full_list_date": None, "first_source_date": None, "content_date": None, "content_basis": None,
           "source": "yugipedia",
           "source_url": PAGE_URL + quote(list_name.replace(" ", "_"), safe="_(),!:"),
           "cited_source": None, "cited_url": None, "evidence": None, "missing_reason": None}

    def recent(day: date | None) -> bool:
        return bool(day) and day <= effective and effective - day <= timedelta(days=MAX_LEAD_DAYS)

    def same_day_ref(month: str, d: str) -> dict | None:
        c = [r for r in refs if r["date"] and r["date"].strftime("%B") == month and r["date"].day == int(d)]
        return c[0] if c else None

    sentences = [m for m in re.finditer(r"[^.]*?(?:announced|revealed)[^.]*\.", flat)]
    found = None   # (jour, phrase, référence, précision)

    # 1) « announced on <date> » : jour explicite. Sans année dans la phrase, l'année vient d'une référence
    #    qui porte le même jour (jamais supposée).
    for sm in sentences:
        m = re.search(rf"announced\s+on\s+{DATE_RE}", sm.group(0))
        if not m:
            continue
        day = parse_date(m["m"], m["d"], m["y"])
        ref = ref_following(sm.start() + m.end())
        if day is None:
            ref = same_day_ref(m["m"], m["d"]) or ref
            day = ref["date"] if ref and ref["date"] and ref["date"].strftime("%B") == m["m"] else None
        if recent(day):
            found = (day, clean(sm.group(0)), ref, "jour")
            break
    # 2) « on the day prior » : relatif à l'entrée en vigueur, accepté seulement si une référence citée porte
    #    exactement ce jour.
    if found is None:
        for sm in sentences:
            if re.search(r"announced[^.]*on the day prior", sm.group(0)):
                day = effective - timedelta(days=1)
                conf = [r for r in refs if r["date"] == day]
                conf.sort(key=lambda r: cited_kind(r["url"]) != "konami")
                if conf:
                    found = (day, clean(sm.group(0)), conf[0], "jour_deduit")
                    break
    # 3) « on the weekend of <date> » : début d'un événement, jour exact non précisé.
    if found is None:
        for sm in sentences:
            m = re.search(rf"announced[^.]*weekend of\s+{DATE_RE}", sm.group(0))
            if m and recent(parse_date(m["m"], m["d"], m["y"])):
                found = (parse_date(m["m"], m["d"], m["y"]), clean(sm.group(0)),
                         ref_following(sm.start() + m.end()), "debut_evenement")
                break
    if found:
        day, evidence, ref, precision = found
        row.update(announced_date=day.isoformat(), announced_precision=precision, evidence=evidence[:400])
        if ref and ref["url"]:
            row.update(cited_url=ref["url"], cited_source=cited_kind(ref["url"]))

    # Liste complète publiée plus tard que la première annonce.
    m = re.search(rf"(?:finally|fully|completely)\s+released\s+on\s+{DATE_RE}", flat)
    if m:
        day = parse_date(m["m"], m["d"], m["y"])
        if day is None:
            r = same_day_ref(m["m"], m["d"])
            day = r["date"] if r else None
        if recent(day) and day.isoformat() != row["announced_date"]:
            row["full_list_date"] = day.isoformat()
    elif row["announced_date"]:
        final = [r for r in refs if r["date"] and re.search(r"\bFINAL\b", r["title"]) and recent(r["date"])]
        if final and final[0]["date"].isoformat() != row["announced_date"]:
            row["full_list_date"] = final[0]["date"].isoformat()

    # Sources qui reprennent le contenu de la liste. On écarte les articles qui n'annoncent qu'une date
    # (« Announcement », « Date For… », « To Be Revealed ») et ceux d'une autre liste (mois et année du titre à
    # plus d'un mois de l'entrée en vigueur : Yugipedia cite parfois la liste voisine).
    def date_only(title: str) -> bool:
        return bool(re.search(r"Announcement|Date For|Date Confirm|To Be Revealed|Preview|Teaser", title or "", re.I))

    def other_list(title: str) -> bool:
        m = re.search(rf"({MONTHS})\s+(?:\d{{1,2}}(?:st|nd|rd|th)?,?\s+)?(\d{{4}})", title or "")
        if not m:
            return False
        t = datetime.strptime(f"{m.group(1)} 1 {m.group(2)}", "%B %d %Y").date()
        return abs((t.year - effective.year) * 12 + t.month - effective.month) > 1

    def is_list_source(r: dict) -> bool:
        listy = re.search(r"Forbidden|Limit|F&L|F\s*&amp;\s*L|リミットレギュレーション", r["title"] or "", re.I)
        return bool(recent(r["date"]) and listy and not date_only(r["title"]) and not other_list(r["title"])
                    and cited_kind(r["url"]) in ("konami", "ygorganization", "beyondtheduel"))

    pool = [r for r in refs if is_list_source(r)]
    if pool:
        first = min(pool, key=lambda r: r["date"])
        row["first_source_date"] = first["date"].isoformat()

    # Nature de la date d'annonce : une source « date seule » du même jour (± 1) la dit annonce de date.
    if row["announced_date"]:
        ann = date.fromisoformat(row["announced_date"])
        only = [r for r in refs if r["date"] and date_only(r["title"]) and abs((r["date"] - ann).days) <= 1]
        row["announced_kind"] = "date_seule" if only else "liste"
        if row["announced_kind"] == "liste":
            row.update(content_date=row["announced_date"], content_basis="annonce_yugipedia")
        elif row["full_list_date"]:
            row.update(content_date=row["full_list_date"], content_basis="liste_complete")
        elif row["first_source_date"]:
            row.update(content_date=row["first_source_date"], content_basis="article_de_la_liste")

    # `cited_url` : la source qui porte la date retenue (contenu, sinon borne haute), jamais une autre référence
    # de la page. Aucune référence datée de ce jour : vide (la phrase de Yugipedia, dans `evidence`, fait foi).
    target = row["content_date"] or row["first_source_date"]
    row["cited_url"] = row["cited_source"] = None
    if target:
        td = date.fromisoformat(target)
        match = [r for r in refs if r["date"] == td and r["url"] and not date_only(r["title"])
                 and not other_list(r["title"])]
        match.sort(key=lambda r: cited_kind(r["url"]) != "konami")
        if match:
            row.update(cited_url=match[0]["url"], cited_source=cited_kind(match[0]["url"]))

    if row["content_date"] is None:
        if row["announced_date"]:
            row["missing_reason"] = ("La date citée par Yugipedia n'annonce que la date de sortie de la liste, "
                                     "et aucune source citée ne donne le jour de publication des cartes.")
        elif row["first_source_date"]:
            row["missing_reason"] = (
                "La page Yugipedia ne dit pas quand la liste a été annoncée ; seule la source citée "
                f"({row['cited_source'] or 'source'}, publiée le {row['first_source_date']}) reprend la liste : "
                "borne haute du jour de publication, pas la date.")
        else:
            row["missing_reason"] = ("La page Yugipedia ne donne ni date d'annonce ni source datée qui reprenne "
                                     "la liste (listes anciennes, avant les sources en ligne de Konami).")
    return row


# --------------------------------------------------------------------------- réseau et base

def fetch_wikitext(title: str) -> str:
    last_error = "?"
    for attempt in range(MAX_ATTEMPTS):
        try:
            r = requests.get(API, params={"action": "parse", "page": title, "prop": "wikitext", "format": "json"},
                             headers=HEADERS, timeout=30)
            r.raise_for_status()
            text = r.json().get("parse", {}).get("wikitext", {}).get("*", "")
            if text:
                return text
            last_error = "page vide"
        except Exception as exc:  # réponse vide ou non JSON observée sur Yugipedia : on réessaie
            last_error = str(exc)[:120]
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(last_error)


def lists_to_cover(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    rows = conn.execute(
        "SELECT DISTINCT format, list_name, effective_date FROM banlist_history "
        "WHERE effective_date IS NOT NULL ORDER BY format, effective_date"
    ).fetchall()
    return [tuple(r) for r in rows]


def backup(db: Path) -> Path:
    dest = db.with_name(f"backup_avant_lot21_{db.stem}_{datetime.now().strftime('%Y%m%d')}.db")
    if dest.exists():
        return dest
    src = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    dst = sqlite3.connect(dest)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--dry-run", action="store_true", help="Affiche le résumé, n'écrit rien")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()
    if not args.db.exists():
        raise SystemExit(f"Base absente : {args.db}")

    ro = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True, timeout=60)
    lists = lists_to_cover(ro)
    previous = {}
    if ro.execute("SELECT 1 FROM sqlite_master WHERE name='banlist_announcements'").fetchone():
        ro.row_factory = sqlite3.Row
        previous = {(r["format"], r["list_name"]): dict(r) for r in ro.execute("SELECT * FROM banlist_announcements")}
    ro.close()
    if not lists:
        raise SystemExit("banlist_history vide : lancer fetch_banlist_history.py d'abord")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows, failed = [], []
    for fmt, name, eff in lists:
        try:
            row = extract(fmt, name, date.fromisoformat(eff), split_head(fetch_wikitext(name)))
            row["fetched_at"] = now
        except Exception as exc:
            failed.append(f"{fmt} {name}: {exc}")
            old = previous.get((fmt, name))
            if old:
                row = old   # on garde la ligne précédente plutôt que de la perdre
            else:
                continue
        rows.append(row)
        time.sleep(REQUEST_PAUSE_SEC)

    n = len(rows)
    with_ann = [r for r in rows if r["announced_date"]]
    print(f"{n} listes lues ({len(failed)} en échec) ; date d'annonce pour {len(with_ann)}, "
          f"borne haute seule pour {sum(1 for r in rows if not r['announced_date'] and r['first_source_date'])}, "
          f"rien pour {sum(1 for r in rows if not r['announced_date'] and not r['first_source_date'])}")
    for f in failed:
        print("  ⚠", f)
    for r in rows:
        if r["effective_date"] >= "2024-01-01":
            lead = ""
            if r["announced_date"]:
                lead = f"{(date.fromisoformat(r['effective_date']) - date.fromisoformat(r['announced_date'])).days} j avant"
            print(f"  {r['format']} {r['effective_date']}  annoncée {r['announced_date'] or '—':10} "
                  f"({r['announced_kind'] or '—':10}) contenu {r['content_date'] or '—':10} {lead:11} "
                  f"borne {r['first_source_date'] or '—'}")

    if args.dry_run:
        return 1 if failed and not rows else 0
    if not rows:
        raise SystemExit("Aucune ligne collectée : table inchangée")

    # Sauvegarde à la première création seulement : ensuite le script ne remplace que sa propre table (déjà
    # reconstructible depuis Yugipedia) ; dans `refresh_all.py` (chaque lundi), une copie datée de 270 Mo par
    # semaine s'empilerait.
    if not args.no_backup and not previous:
        print(f"Sauvegarde : {backup(args.db)}")
    conn = sqlite3.connect(args.db, timeout=60)
    try:
        conn.executescript(SCHEMA)   # CREATE ... IF NOT EXISTS (commit implicite, hors de la transaction ci-dessous)
        with conn:  # transaction unique : tout ou rien
            conn.execute("DELETE FROM banlist_announcements")
            cols = ["format", "list_name", "effective_date", "announced_date", "announced_precision",
                    "announced_kind", "full_list_date", "first_source_date", "content_date", "content_basis", "source", "source_url", "cited_source", "cited_url",
                    "evidence", "missing_reason", "fetched_at"]
            conn.executemany(
                f"INSERT INTO banlist_announcements ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                [tuple(r[c] for c in cols) for r in rows])
    finally:
        conn.close()
    print(f"✓ banlist_announcements : {len(rows)} lignes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
