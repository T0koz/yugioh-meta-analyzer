"""Page d'archétype (TOK-101) : tout ce que la base de service sait d'un archétype.

Aucun calcul nouveau : la position vient de la tier list (mêmes règles), l'historique
de `meta_scores` (TCG) et `meta_scores_ocg` (OCG, TOK-116), les cartes de `ban_radar`,
le signal boutique de `/boutique/signals`.
"""

import re
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db
from app.routers.boutique import latest_computed_at, load_boutique_signals
from app.routers.meta import compute_tier_list, get_archetype_image
from app.schemas import (
    ArchetypeBoutique,
    ArchetypeKeyCard,
    ArchetypeKeyCards,
    ArchetypeMonth,
    ArchetypeOcg,
    ArchetypeResponse,
    ArchetypeTcg,
    TierWindow,
)
from app.slugs import resolve, slugify

router = APIRouter(prefix="/archetypes", tags=["archetypes"])

KEY_CARDS_LIMIT = 12


def known_archetypes(db: sqlite3.Connection) -> list[str]:
    """Archétypes qui ont une page : vus en tournoi TCG, ou porteurs d'un signal boutique.

    Triés du plus joué au moins joué : si deux noms donnaient un jour le même slug,
    l'adresse irait au plus joué, de façon stable.
    """
    return [
        row["archetype"]
        for row in db.execute(
            """
            SELECT archetype, SUM(deck_count) AS decks FROM meta_scores GROUP BY archetype
            UNION ALL
            SELECT DISTINCT archetype, 0 AS decks FROM boutique_buy_signals
            WHERE archetype NOT IN (SELECT archetype FROM meta_scores)
            ORDER BY decks DESC, archetype
            """
        )
    ]


def load_tcg(db: sqlite3.Connection, archetype: str) -> tuple[TierWindow | None, ArchetypeTcg | None]:
    entries, rows = compute_tier_list(db, with_images=False)
    if not rows:
        return None, None
    window = TierWindow(start=rows[0]["window_start"], end=rows[0]["window_end"], n_decks=rows[0]["n_cur"])
    for rank, (entry, row) in enumerate(zip(entries, rows), start=1):
        if entry.archetype != archetype:
            continue
        n_prev = row["n_prev"]
        return window, ArchetypeTcg(
            tier=entry.tier,
            trend=entry.trend,
            rank=rank,
            n_archetypes=len(entries),
            share=entry.share,
            decks=entry.decks,
            meta_score=entry.meta_score,
            share_prev=row["decks_prev"] / n_prev if n_prev else None,
            decks_prev=row["decks_prev"],
            n_decks_prev=n_prev,
        )
    return window, None


def _history_sql(table: str) -> str:
    return f"""
        WITH months AS (SELECT month, MAX(total_decks) AS total FROM {table} GROUP BY month)
        SELECT m.month, m.total, COALESCE(s.deck_count, 0) AS decks
        FROM months m
        LEFT JOIN {table} s ON s.month = m.month AND s.archetype = :a
        WHERE m.month >= (SELECT MIN(month) FROM {table} WHERE archetype = :a)
        ORDER BY m.month
        """


# Noms de table écrits en clair : `build_serving_db.py --check` et `check_freshness.py` repèrent les tables
# lues par l'API en cherchant « FROM <table> » dans les routeurs. Même schéma, écrites par le notebook 04.
# SQL: FROM meta_scores / FROM meta_scores_ocg
HISTORY_SQL = {"meta_scores": _history_sql("meta_scores"), "meta_scores_ocg": _history_sql("meta_scores_ocg")}


def load_history(db: sqlite3.Connection, archetype: str, table: str = "meta_scores") -> list[ArchetypeMonth]:
    # Un mois sans ligne pour l'archétype est un mois à 0 deck, pas un mois manquant :
    # on part de tous les mois de la base à partir de sa première apparition.
    rows = db.execute(HISTORY_SQL[table], {"a": archetype}).fetchall()
    return [
        ArchetypeMonth(
            month=row["month"],
            decks=row["decks"],
            total_decks=row["total"],
            share=row["decks"] / row["total"] if row["total"] else 0.0,
        )
        for row in rows
    ]


def load_ocg_history(db: sqlite3.Connection, archetype: str) -> tuple[list[ArchetypeMonth], str | None]:
    """Part mensuelle en OCG (TOK-116) et date de calcul de la chaîne OCG.

    `meta_scores_ocg` n'a pas de colonne de date : on sert `computed_at` de `ocg_archetype_scores`,
    écrite par le notebook 10, qui tourne juste après le notebook 04 dans `refresh_all.py`.
    """
    try:
        history = load_history(db, archetype, table="meta_scores_ocg")
        computed_at = db.execute("SELECT MAX(computed_at) FROM ocg_archetype_scores").fetchone()[0]
    except sqlite3.OperationalError:  # base de service construite avant l'ajout de la table
        return [], None
    return history, computed_at


def load_key_cards(db: sqlite3.Connection, archetype: str) -> ArchetypeKeyCards | None:
    # `top_archetype` = deck d'attache : renseigné par build_ban_radar.py quand au
    # moins la moitié des decks qui jouent la carte sont de cet archétype.
    rows = db.execute(
        """
        SELECT r.card_name, r.decks, r.deck_share, r.mean_copies, r.current_status,
               r.as_of, r.n_decks_window, c.image_url_small
        FROM ban_radar r
        -- Jointure indexée (TOK-83) : le `+` coupe l'affinité TEXT, sinon l'index est ignoré.
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +r.card_name
        WHERE r.top_archetype = ?
        GROUP BY r.card_name
        ORDER BY r.decks DESC, r.card_name
        LIMIT ?
        """,
        (archetype, KEY_CARDS_LIMIT),
    ).fetchall()
    if not rows:
        return None
    return ArchetypeKeyCards(
        data=[
            ArchetypeKeyCard(
                card_name=row["card_name"],
                decks=row["decks"],
                deck_share=row["deck_share"],
                mean_copies=row["mean_copies"],
                current_status=row["current_status"],
                image_url=row["image_url_small"],
            )
            for row in rows
        ],
        as_of=rows[0]["as_of"],
        n_decks_window=rows[0]["n_decks_window"],
    )


def load_ocg(db: sqlite3.Connection, archetype: str) -> ArchetypeOcg | None:
    try:
        row = db.execute(
            "SELECT share_ocg, n_ocg_decks, computed_at FROM ocg_archetype_scores WHERE archetype = ?",
            (archetype,),
        ).fetchone()
    except sqlite3.OperationalError:  # base de service construite avant l'ajout de la table
        return None
    if row is None:
        return None
    return ArchetypeOcg(share=row["share_ocg"], decks=row["n_ocg_decks"], computed_at=row["computed_at"])


def load_boutique(db: sqlite3.Connection, archetype: str) -> ArchetypeBoutique | None:
    signals, rule = load_boutique_signals(db, archetype)
    if not signals:
        return None
    first = signals[0]
    return ArchetypeBoutique(
        signal_label=first.signal_label,
        archetype_rank=first.archetype_rank,
        label_rule=rule,
        tcg_window_start=first.tcg_window_start,
        tcg_window_end=first.tcg_window_end,
        computed_at=latest_computed_at(db, "boutique_buy_signals"),
        signals=signals,
    )


@router.get("/{slug}", response_model=ArchetypeResponse)
def get_archetype(slug: str, db: sqlite3.Connection = Depends(get_db)) -> ArchetypeResponse:
    archetype = resolve(slug, known_archetypes(db))
    if archetype is None:
        raise HTTPException(status_code=404, detail=f"Archétype inconnu : {slug}")

    key_cards = load_key_cards(db, archetype)
    boutique = load_boutique(db, archetype)
    # Vignette : carte la plus consultée de l'archétype ; à défaut (nom composé, archétype
    # pas encore dans `cards`), la carte clé la plus jouée, puis la première du signal boutique.
    image = get_archetype_image(db, archetype)
    if image is None and key_cards:
        image = next((c.image_url for c in key_cards.data if c.image_url), None)
    if image is None and boutique:
        # D'abord une carte dont le nom reprend un mot de l'archétype (« Amazoness War
        # Chief » pour « Harpie/Amazoness ») : la première du lot est souvent une staple.
        words = [w for w in re.split(r"[^a-z0-9]+", archetype.lower()) if len(w) > 2]
        with_image = [s for s in boutique.signals if s.image_url]
        own = [s for s in with_image if any(w in s.card_name.lower() for w in words)]
        image = next((s.image_url for s in own + with_image), None)

    tcg_window, tcg = load_tcg(db, archetype)
    ocg_history, ocg_history_computed_at = load_ocg_history(db, archetype)
    return ArchetypeResponse(
        archetype=archetype,
        slug=slugify(archetype),
        image_url=image,
        tcg_window=tcg_window,
        tcg=tcg,
        history=load_history(db, archetype),
        ocg_history=ocg_history,
        ocg_history_computed_at=ocg_history_computed_at,
        key_cards=key_cards,
        ocg=load_ocg(db, archetype),
        boutique=boutique,
    )
