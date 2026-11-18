"""
TOK-93 : contrôle de fraîcheur des tables servies (`SERVED_TABLES` de `scripts/build_serving_db.py`) et santé de
l'endpoint yugiohmeta `/top-decks`.

    python scripts/check_freshness.py                        # data/yugioh.db (sinon celle du dépôt principal)
    python scripts/check_freshness.py --db data/serving.db   # la base qui part en ligne ; dates de référence : yugioh.db
    python scripts/check_freshness.py --status               # n'exécute rien : derniers contrôles journalisés
    python scripts/check_freshness.py --sans-endpoint        # pas d'appel réseau
    python scripts/check_freshness.py --today 2026-11-16 --sans-journal   # rejeu à une date, sans rien écrire

Lecture seule sur les bases (`mode=ro`), bibliothèque standard seulement. Dernière étape de `scripts/refresh_decks.py`
(job du lundi), **après** la reconstruction de `serving.db`, qu'elle ne peut donc pas bloquer. Chaque contrôle ajoute
une ligne `{"step": "fraicheur_tables", …}` à `data/fetch_health.jsonl` (fichier ignoré par Git, celui du checkout
courant). Code de sortie 1 si une table est PÉRIMÉE ou si l'endpoint est en erreur, 0 sinon. « Non datée », « non lue »,
« ignorée » et « périmée connue » sont affichées sans faire échouer.

Pour chaque table, la date la plus fiable disponible :
1. une date de calcul (`computed_at`), comparée à la date du contrôle ;
2. une date des données (`as_of`, dernier deck d'un extrait, mois, dernier relevé de prix), comparée au dernier deck
   relevé du même format dans `tournament_decks` (ou à la date du contrôle pour les prix) ;
3. à défaut, un contrôle de cohérence avec une autre table (graphe ↔ co-occurrences, historique ↔ banlists,
   vues ↔ instantané du 13/06, table fille ↔ table mère) ;
4. sinon « non datée » : c'est dit, rien n'est conclu.
Une table servie vide, une colonne de date entièrement vide ou une requête en erreur (colonne renommée) : PÉRIMÉE,
jamais tolérée.

Seuils : réglages posés à la main le 2026-11-18 (TOK-93), non estimés, à valider par Thomas :
- `COMPUTED_MAX_DAYS` = 8 jours : le job tourne chaque lundi, un jour de marge (Mac endormi, rattrapage launchd) ;
- `DATA_LAG_MAX_DAYS` = 7 jours de retard sur le dernier deck : une table calculée après le relevé des decks a
  0 jour de retard ; 7 = une semaine de relevé manquée ;
- `MONTH_LAG_MAX` = 1 mois pour les tables mensuelles (le mois en cours peut ne pas encore avoir de ligne) ;
- `VIEWS_MAX_DAYS` = 8 jours pour les vues (« vues de la semaine » : sans sens au-delà d'une semaine).

`KNOWN_STALE` : défauts connus, tolérés jusqu'à une date d'expiration (motif → ticket, date, raison) ; affichés
« périmée connue », ils redeviennent PÉRIMÉS après la date. Réglage déclaré, à valider par Thomas.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_serving_db import SERVED_TABLES, tables_referenced_by_api  # noqa: E402

SNAPSHOT = ROOT / "data" / "raw" / "cards.json"
HEALTH = ROOT / "data" / "fetch_health.jsonl"
STEP = "fraicheur_tables"   # pas « freshness » : refresh_decks.py relit ses propres lignes "freshness"

COMPUTED_MAX_DAYS = 8
DATA_LAG_MAX_DAYS = 7
MONTH_LAG_MAX = 1
VIEWS_MAX_DAYS = 8
VIEWS_FROZEN_SHARE = 0.5   # au-delà de 50 % de vues identiques à l'instantané, les vues datent de l'instantané

# Défauts connus (motif « table:contrôle » → ticket, expiration, raison). Jamais pour une table absente ou vide.
KNOWN_STALE = {
    "card_graph_metrics:graphe": ("TOK-136", "2026-12-31", "graphe du notebook 03, hors refresh_all.py"),
    "graph_communities:graphe": ("TOK-136", "2026-12-31", "graphe du notebook 03, hors refresh_all.py"),
    "early_card_signals:vues": ("ticket à créer", "2026-12-31",
                                "views_week figée au 13/06 : fetch_new_cards.py ajoute sans rafraîchir"),
}

# Graphe du notebook 03, mêmes seuils que `scripts/bridge_date.py` (test d'alignement dans backend/tests).
EDGE_MIN_JACCARD = 0.3
EDGE_MIN_COOC = 5

# Endpoint des decklists (même adresse que `fetch_tournament_decks.py`, test d'alignement dans backend/tests).
ENDPOINT = "https://www.yugiohmeta.com/api/v1/top-decks"
ENDPOINT_PARAMS = "?limit=1&ocg%5B%24ne%5D=true"
ENDPOINT_TIMEOUT = 30

OK, STALE, KNOWN, UNDATED, UNREAD, SKIPPED = "ok", "PÉRIMÉE", "périmée connue", "non datée", "non lue", "ignorée"
ORDER = [STALE, KNOWN, UNDATED, SKIPPED, OK]   # du plus grave au moins grave (UNREAD est posé après coup)


@dataclass
class Result:
    table: str
    status: str
    detail: str


def parse_day(value) -> dt.date | None:
    if not value:
        return None
    m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?", str(value))
    if not m:
        return None
    return dt.date(int(m[1]), int(m[2]), int(m[3] or 1))


def months_between(a: dt.date, b: dt.date) -> int:
    """Nombre de mois calendaires de a à b (b postérieur)."""
    return (b.year - a.year) * 12 + b.month - a.month


def table_names(conn: sqlite3.Connection) -> set[str]:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def main_checkout() -> Path:
    """Racine du dépôt principal (≠ ROOT dans un worktree, qui n'a pas de base)."""
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             cwd=ROOT, capture_output=True, text=True, timeout=20)
        common = out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        common = ""
    return Path(common).parent if common else ROOT


def default_db(name: str) -> Path:
    for root in (ROOT, main_checkout()):
        if (root / "data" / name).exists():
            return root / "data" / name
    return ROOT / "data" / name


class Context:
    """`conn` : base contrôlée. `ref` : base qui donne les dates de référence (dernier deck, banlists) ;
    par défaut la même. La base de service n'a ni `tournament_decks` ni `banlist_history` : on la contrôle
    contre `yugioh.db`."""

    def __init__(self, conn: sqlite3.Connection, today: dt.date, snapshot: Path | None = None,
                 ref: sqlite3.Connection | None = None, known: dict | None = None):
        self.conn, self.today, self.snapshot = conn, today, snapshot
        self.known = KNOWN_STALE if known is None else known
        self.tables = table_names(conn)
        self.ref = ref or conn
        self.ref_tables = table_names(self.ref)
        self.last_deck: dict[str, dt.date | None] = {}
        if "tournament_decks" in self.ref_tables:
            for fmt, ocg in (("TCG", 0), ("OCG", 1)):
                self.last_deck[fmt] = parse_day(self.ref.execute(
                    f"SELECT MAX(created) FROM tournament_decks WHERE ocg = {ocg}").fetchone()[0])
            days = [d for d in self.last_deck.values() if d]
            self.last_deck["ALL"] = max(days) if days else None

    def one(self, sql: str, params: tuple = ()):
        row = self.conn.execute(sql, params).fetchone()
        return row[0] if row else None

    def res(self, table: str, motif: str, status: str, detail: str) -> Result:
        """Résultat d'un contrôle ; un motif connu et non expiré passe de PÉRIMÉE à « périmée connue »."""
        key = f"{table}:{motif}"
        if status == STALE and key in self.known:
            ticket, until, why = self.known[key]
            if self.today <= dt.date.fromisoformat(until):
                return Result(table, KNOWN, f"{detail} [connue : {ticket}, tolérée jusqu'au {until} ; {why}]")
            detail += f" [tolérance {ticket} expirée le {until}]"
        return Result(table, status, detail)


# ── Contrôles élémentaires ─────────────────────────────────────────────────────

def computed(ctx: Context, table: str, max_days: int = COMPUTED_MAX_DAYS) -> Result:
    return day_age(ctx, table, f'SELECT MAX(computed_at) FROM "{table}"', "calculée", max_days, "calcul")


def day_age(ctx: Context, table: str, sql: str, label: str, max_days: int = COMPUTED_MAX_DAYS,
            motif: str = "date") -> Result:
    """Date lue par `sql`, comparée à la date du contrôle. Colonne vide : PÉRIMÉE (le producteur ne la remplit plus)."""
    d = parse_day(ctx.one(sql))
    if d is None:
        return ctx.res(table, motif, STALE, f"{label} : colonne de date vide")
    age = (ctx.today - d).days
    return ctx.res(table, motif, OK if age <= max_days else STALE, f"{label} le {d} ({age} j, seuil {max_days} j)")


def data_lag(ctx: Context, table: str, sql: str, fmt: str = "ALL", label: str = "données") -> Result:
    d = parse_day(ctx.one(sql))
    ref = ctx.last_deck.get(fmt)
    if d is None:
        return ctx.res(table, "donnees", STALE, f"{label} : colonne de date vide")
    if ref is None:
        return Result(table, SKIPPED, f"{label} au {d} ; pas de tournament_decks pour comparer")
    lag = (ref - d).days
    return ctx.res(table, "donnees", OK if lag <= DATA_LAG_MAX_DAYS else STALE,
                   f"{label} au {d}, dernier deck {fmt} le {ref} ({lag} j de retard, seuil {DATA_LAG_MAX_DAYS} j)")


def month_lag(ctx: Context, table: str, sql: str, fmt: str = "TCG", label: str = "mois") -> Result:
    d = parse_day(ctx.one(sql))
    ref = ctx.last_deck.get(fmt)
    if d is None:
        return ctx.res(table, "mois", STALE, f"{label} : colonne de date vide")
    if ref is None:
        return Result(table, SKIPPED, f"{label} {d:%Y-%m} ; pas de tournament_decks pour comparer")
    lag = months_between(d, ref)
    return ctx.res(table, "mois", OK if lag <= MONTH_LAG_MAX else STALE,
                   f"{label} {d:%Y-%m}, dernier deck {fmt} {ref:%Y-%m} ({lag} mois de retard, seuil {MONTH_LAG_MAX})")


def worst(table: str, *results: Result) -> Result:
    st = min((r.status for r in results), key=ORDER.index)
    return Result(table, st, " ; ".join(r.detail for r in results))


def graph_nodes(ctx: Context) -> set[str] | None:
    if "card_cooccurrence" not in ctx.tables:
        return None
    rows = ctx.conn.execute(
        "SELECT card_a, card_b FROM card_cooccurrence WHERE jaccard >= ? AND cooc_count >= ?",
        (EDGE_MIN_JACCARD, EDGE_MIN_COOC))
    return {c for pair in rows for c in pair}


def rule_graph_metrics(ctx: Context, table: str) -> Result:
    nodes = graph_nodes(ctx)
    have = {r[0] for r in ctx.conn.execute(f'SELECT card_name FROM "{table}"')}
    if nodes is None:
        return Result(table, UNDATED, f"non datée ; {len(have)} nœuds, card_cooccurrence absente pour comparer")
    return ctx.res(table, "graphe", OK if have == nodes else STALE,
                   f"non datée ; {len(have)} nœuds contre {len(nodes)} dans le graphe de card_cooccurrence "
                   f"(jaccard ≥ {EDGE_MIN_JACCARD}, ≥ {EDGE_MIN_COOC} decks), {len(nodes & have)} en commun "
                   "(notebook 03, hors refresh_all.py)")


def rule_communities(ctx: Context, table: str) -> Result:
    nodes = graph_nodes(ctx)
    n = ctx.one(f'SELECT SUM(n_cards) FROM "{table}"') or 0
    if nodes is None:
        return Result(table, UNDATED, f"non datée ; {n} cartes réparties, card_cooccurrence absente pour comparer")
    return ctx.res(table, "graphe", OK if n == len(nodes) else STALE,
                   f"non datée ; {n} cartes réparties en communautés contre {len(nodes)} nœuds dans le graphe "
                   "de card_cooccurrence (notebook 03, hors refresh_all.py)")


def snapshot_date() -> dt.date | None:
    """Date de l'instantané `data/raw/cards.json` : date du dernier commit qui l'a modifié (le fichier est suivi)."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", "data/raw/cards.json"],
                             cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return parse_day(out)


def views_age(ctx: Context, table: str) -> Result:
    """Âge de `views_week`. Aucune date en base : on compare les vues de `cards` à l'instantané suivi par Git.
    Les vues servies sont celles d'`early_card_signals` (copiées depuis `cards` par build_early_signals.py)."""
    if "cards" not in ctx.tables:
        return Result(table, SKIPPED, "vues : table cards absente pour comparer")
    if ctx.snapshot is None or not ctx.snapshot.exists():
        return Result(table, UNDATED, "vues non datées (instantané data/raw/cards.json absent)")
    snap_day = snapshot_date()
    if snap_day is None:
        return Result(table, SKIPPED, "vues : date de l'instantané data/raw/cards.json introuvable (git)")
    snap = {c["id"]: (c.get("misc_info") or [{}])[0].get("viewsweek") for c in json.loads(ctx.snapshot.read_text())}
    rows = ctx.conn.execute("SELECT id, views_week FROM cards").fetchall()
    known = [(i, v) for i, v in rows if i in snap]
    if not known:
        return Result(table, UNDATED, "vues : aucune carte de l'instantané dans cards, vues non datées")
    same = sum(1 for i, v in known if snap[i] == v)
    share = same / len(known)
    if share < VIEWS_FROZEN_SHARE:
        return Result(table, UNDATED, f"vues différentes de l'instantané du {snap_day} pour {1 - share:.0%} des "
                                      "cartes : rafraîchies depuis, mais non datées")
    age = (ctx.today - snap_day).days
    return ctx.res(table, "vues", OK if age <= VIEWS_MAX_DAYS else STALE,
                   f"vues (cards.views_week) identiques à l'instantané du {snap_day} pour {same} cartes sur "
                   f"{len(known)} ({share:.0%}) : {age} j (seuil {VIEWS_MAX_DAYS} j)")


def rule_cards(ctx: Context, table: str) -> Result:
    added = len(ctx.conn.execute(f'SELECT id FROM "{table}"').fetchall())
    return Result(table, UNDATED, f"{added} cartes, aucune date d'ajout ; servie pour les noms et les images "
                                  "(views_week est contrôlée avec early_card_signals, qui la sert)")


def rule_ban_history(ctx: Context, table: str) -> Result:
    """Historique du Ban Radar : il doit couvrir la dernière banlist entrée en vigueur de chaque format (ligne
    retenue ou écartée avec `skip_reason`). `computed_at` n'est pas un critère : `build_ban_history.py` n'est pas dans
    refresh_all.py et ne change qu'avec une nouvelle liste."""
    if "banlist_history" not in ctx.ref_tables:
        return Result(table, SKIPPED, "pas de banlist_history pour comparer")
    parts, stale = [], False
    for fmt in ("TCG", "OCG"):
        latest = parse_day(ctx.ref.execute(
            "SELECT MAX(effective_date) FROM banlist_history WHERE format = ? AND effective_date <= ?",
            (fmt, ctx.today.isoformat())).fetchone()[0])
        covered = parse_day(ctx.one(f'SELECT MAX(effective_date) FROM "{table}" WHERE format = ?', (fmt,)))
        if latest and (covered is None or covered < latest):
            stale = True
            parts.append(f"{fmt} : dernière liste du {latest} absente (dernière couverte : {covered})")
        else:
            parts.append(f"{fmt} : couvre la liste du {latest}")
    return ctx.res(table, "banlists", STALE if stale else OK,
                   " ; ".join(parts) + (" (relancer build_ban_history.py)" if stale else ""))


def rule_child(parent: str, cols: tuple[str, ...]):
    """Table sans date remplie par le même script qu'une table datée : elle prend le statut de sa mère, après un
    contrôle de cohérence (chaque ligne renvoie à une ligne de la mère, sur `cols`)."""
    def rule(ctx: Context, table: str) -> Result:
        on = " AND ".join(f'p."{c}" = c."{c}"' for c in cols)
        orphans = ctx.one(f'SELECT COUNT(*) FROM "{table}" c WHERE NOT EXISTS (SELECT 1 FROM "{parent}" p WHERE {on})')
        if orphans:
            return Result(table, STALE, f"{orphans} lignes sans correspondance dans {parent} : tables désynchronisées")
        mother = run_rule(ctx, parent)
        return Result(table, mother.status, f"non datée, remplie avec {parent} (même script), 0 ligne orpheline ; "
                                            f"statut de {parent} : {mother.detail}")
    return rule


RULES = {
    "archetype_card_profile": lambda c, t: worst(t, computed(c, t),
                                                 month_lag(c, t, f'SELECT MAX(window_end) FROM "{t}"', label="fenêtre jusqu'à")),
    "archetype_recent_decks": lambda c, t: data_lag(c, t, f'SELECT MAX(created) FROM "{t}"', "TCG", "liste la plus récente"),
    "archetype_recent_deck_cards": rule_child("archetype_recent_decks", ("deck_id",)),
    "archetype_trend": lambda c, t: Result(t, UNDATED, "aucune colonne de date (notebook 04, dans refresh_all.py)"),
    "ban_backtest_lists": rule_ban_history,
    # Fille : seules les listes retenues y ont des cartes ; une liste écartée n'y apparaît jamais.
    "ban_backtest_cards": rule_child("ban_backtest_lists", ("format", "effective_date")),
    "ban_radar": lambda c, t: data_lag(c, t, f'SELECT MAX(as_of) FROM "{t}"', "TCG", "as_of"),
    "boutique_buy_signals": computed,
    "boutique_price_history": lambda c, t: worst(t, computed(c, t), day_age(
        c, t, f'SELECT MAX(snapshot_date) FROM "{t}"', "dernier relevé de prix", motif="releve")),
    "card_cooccurrence": lambda c, t: Result(t, UNDATED, "aucune colonne de date (notebook 02, dans refresh_all.py)"),
    "card_graph_metrics": rule_graph_metrics,
    "card_impact": lambda c, t: data_lag(c, t, f'SELECT MAX(as_of) FROM "{t}"', "TCG", "as_of"),
    "cards": rule_cards,
    "early_card_signals": lambda c, t: worst(t, computed(c, t), data_lag(c, t, f'SELECT MAX(as_of) FROM "{t}"', "TCG", "as_of"),
                                             views_age(c, t)),
    "graph_communities": rule_communities,
    "meta_predictions": lambda c, t: worst(t, computed(c, t),
                                           month_lag(c, t, f'SELECT MAX(data_month) FROM "{t}"', label="mois des données")),
    "meta_scores": lambda c, t: month_lag(c, t, f'SELECT MAX(month) FROM "{t}"', label="dernier mois"),
    # TOK-116 : parts OCG mensuelles (notebook 04), comparées au dernier deck OCG.
    "meta_scores_ocg": lambda c, t: month_lag(c, t, f'SELECT MAX(month) FROM "{t}"', fmt="OCG", label="dernier mois"),
    "meta_tier_list": lambda c, t: day_age(c, t, f'SELECT MAX(scraped_at) FROM "{t}"', "relevée"),
    "ocg_archetype_scores": computed,
}


def run_rule(ctx: Context, table: str) -> Result:
    """Une table absente, vide ou dont la requête échoue est PÉRIMÉE (jamais tolérée)."""
    if table not in ctx.tables:
        return Result(table, STALE, "table absente de la base")
    try:
        if not ctx.one(f'SELECT COUNT(*) FROM "{table}"'):
            return Result(table, STALE, "table vide")
        rule = RULES.get(table)
        return rule(ctx, table) if rule else Result(table, UNDATED, "aucune règle de fraîcheur (à ajouter dans RULES)")
    except sqlite3.Error as exc:
        return Result(table, STALE, f"contrôle impossible ({exc.__class__.__name__} : {exc}) : schéma changé ?")


def check(conn: sqlite3.Connection, today: dt.date, snapshot: Path | None = None, tables: list[str] | None = None,
          ref: sqlite3.Connection | None = None, known: dict | None = None) -> tuple[list[Result], Context]:
    ctx = Context(conn, today, snapshot, ref, known)
    read_by_api = tables_referenced_by_api()
    out = []
    for table in tables or SERVED_TABLES:
        res = run_rule(ctx, table)
        if table not in read_by_api and res.status != OK and table in ctx.tables:
            res = Result(table, UNREAD, f"{res.status} : {res.detail} ; servie mais lue par aucun routeur, sans effet "
                                        "sur le site")
        out.append(res)
    return out, ctx


# ── Endpoint externe ───────────────────────────────────────────────────────────

def probe_endpoint(url: str = ENDPOINT + ENDPOINT_PARAMS, timeout: int = ENDPOINT_TIMEOUT) -> dict:
    """Un appel GET (un seul deck demandé). Un échec réseau est rapporté tel quel, jamais masqué."""
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; controle-fraicheur)",
                                               "Accept": "application/json"})
    out = {"url": url.split("?")[0]}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            out["http_status"] = resp.status
        data = json.loads(body)
        n = len(data) if isinstance(data, list) else None
        out["ok"] = resp.status == 200 and bool(n)
        out["detail"] = f"HTTP {resp.status}, {n} deck(s) renvoyé(s)" if n is not None else \
            f"HTTP {resp.status}, réponse qui n'est pas une liste de decks (format changé ?)"
    except urllib.error.HTTPError as exc:
        out.update(ok=False, http_status=exc.code, detail=f"HTTP {exc.code} {exc.reason}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        out.update(ok=False, http_status=None, detail=f"échec réseau : {getattr(exc, 'reason', exc)}")
    except ValueError as exc:
        out.update(ok=False, detail=f"réponse illisible (JSON) : {exc}")
    out["seconds"] = round(time.time() - t0, 1)
    return out


# ── Journal ────────────────────────────────────────────────────────────────────

def journal_entry(results: list[Result], db: str, today: dt.date, endpoint: dict | None) -> dict:
    by = lambda st: [r.table for r in results if r.status == st]  # noqa: E731
    stale = by(STALE)
    return {"step": STEP, "ok": not stale and (endpoint is None or endpoint["ok"]), "db": Path(db).name,
            "controle_du": today.isoformat(), "perimees": stale, "perimees_connues": by(KNOWN),
            "non_datees": by(UNDATED), "non_lues": by(UNREAD), "ignorees": by(SKIPPED),
            "endpoint": endpoint, "details": {r.table: r.detail for r in results if r.status != OK},
            "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}


def append_journal(entry: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def status(path: Path, n: int = 10) -> int:
    """Derniers contrôles journalisés, lisibles. Code 1 si le dernier est en échec, 2 si aucun."""
    entries = []
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("step") == STEP:
                entries.append(e)
    if not entries:
        print(f"Aucun contrôle de fraîcheur des tables dans {path}")
        return 2
    print(f"{len(entries[-n:])} derniers contrôles de fraîcheur des tables ({path.name}) :")
    for e in entries[-n:]:
        ep = e.get("endpoint") or {}
        ep_txt = "endpoint non testé" if not ep else f"endpoint {'ok' if ep.get('ok') else 'EN ERREUR'} ({ep.get('detail')})"
        print(f"  {e['at']}  {e['db']:<11} {'ok' if e['ok'] else 'ÉCHEC'}  "
              f"périmées {e['perimees'] or '—'} ; connues {e['perimees_connues'] or '—'} ; {ep_txt}")
    last = entries[-1]
    for table in last["perimees"]:
        print(f"  ✗ {table} : {last['details'].get(table, '')}")
    return 0 if last["ok"] else 1


# ── Programme ──────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", help="Base contrôlée (défaut : data/yugioh.db du checkout, sinon du dépôt principal)")
    ap.add_argument("--today", help="Date du contrôle (AAAA-MM-JJ), défaut : aujourd'hui")
    ap.add_argument("--reference", help="Base des dates de référence (dernier deck, banlists). Défaut : la base "
                                        "contrôlée si elle a tournament_decks, sinon yugioh.db")
    ap.add_argument("--journal", default=str(HEALTH), help="Journal JSONL (défaut : data/fetch_health.jsonl du checkout)")
    ap.add_argument("--sans-journal", action="store_true", help="N'écrit rien dans le journal")
    ap.add_argument("--sans-endpoint", action="store_true", help="Pas d'appel à yugiohmeta /top-decks")
    ap.add_argument("--status", action="store_true", help="Affiche les derniers contrôles journalisés, n'exécute rien")
    a = ap.parse_args()
    if a.status:
        return status(Path(a.journal))

    db = a.db or str(default_db("yugioh.db"))
    if not Path(db).exists():
        print(f"Base absente : {db}")
        return 2
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    ro = lambda p: sqlite3.connect(f"file:{os.path.abspath(p)}?mode=ro", uri=True, timeout=60)  # noqa: E731
    conn = ro(db)
    ref_path = a.reference
    if ref_path is None and "tournament_decks" not in table_names(conn):
        candidate = default_db("yugioh.db")
        ref_path = str(candidate) if candidate.exists() else None
    results, ctx = check(conn, today, snapshot=SNAPSHOT, ref=ro(ref_path) if ref_path else None)
    endpoint = None if a.sans_endpoint else probe_endpoint()

    decks = ", ".join(f"{k} {v}" for k, v in ctx.last_deck.items() if k != "ALL") or "aucun (aucune référence trouvée)"
    print(f"Fraîcheur des {len(results)} tables servies — {Path(db).name}, contrôle du {today}, dernier deck : {decks}"
          + (f" (référence : {Path(ref_path).name})" if ref_path else ""))
    mark = {OK: "✓", STALE: "✗", KNOWN: "~", UNDATED: "?", UNREAD: "·", SKIPPED: "⚠"}
    for st in (OK, UNREAD, SKIPPED, UNDATED, KNOWN, STALE):  # les périmées en dernier : visibles en fin de journal
        for r in results:
            if r.status == st:
                print(f"  {mark[st]} {r.table:28s} {r.status:14s} {r.detail}")
    for st, label in ((SKIPPED, "Ignorées (référence manquante)"), (UNDATED, "Non datées (rien n'est conclu)"),
                      (UNREAD, "Non lues par l'API"), (KNOWN, "Périmées connues, tolérées")):
        tabs = [r.table for r in results if r.status == st]
        if tabs:
            print(f"⚠ {label} ({len(tabs)}) : {', '.join(tabs)}")
    if endpoint is not None:
        print(f"{'✓' if endpoint['ok'] else '✗'} Endpoint {endpoint['url']} : {endpoint['detail']} ({endpoint['seconds']} s)")

    entry = journal_entry(results, db, today, endpoint)
    if not a.sans_journal:
        append_journal(entry, Path(a.journal))
    if entry["perimees"]:
        print(f"✗ PÉRIMÉES ({len(entry['perimees'])}) : {', '.join(entry['perimees'])}")
    if not entry["ok"]:
        return 1
    print("✓ Aucune table servie périmée au-delà de son seuil" + ("" if endpoint is None else ", endpoint joignable") + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
