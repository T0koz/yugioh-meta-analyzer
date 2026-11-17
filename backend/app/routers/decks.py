"""Decks (TOK-114) : index des archétypes et fiche de composition.

Tout est précalculé par scripts/build_archetype_profiles.py (parts et médianes, listes
récentes). Ici : les étiquettes (app/deck_profile.py), le tier (mêmes règles que la
tier list, même fenêtre) et les images.
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db
from app.deck_profile import BASE_MIN_SHARE, FLEX_MIN_SHARE, MIN_PROFILE_DECKS, ROLE_BASE, has_profile, role_for
from app.routers.meta import compute_tier_list, get_archetype_image
from app.schemas import (
    DeckCardStat,
    DeckIndexEntry,
    DeckIndexResponse,
    DeckListCard,
    DeckListZone,
    DeckProfileRule,
    DeckResponse,
    DeckZoneProfile,
    RecentDeck,
    TierWindow,
)
from app.slugs import resolve, slugify

router = APIRouter(prefix="/decks", tags=["decks"])

ZONES = ("main", "extra", "side")
PREVIEW_CARDS = 4
RULE = DeckProfileRule(base_min_share=BASE_MIN_SHARE, flex_min_share=FLEX_MIN_SHARE, min_decks=MIN_PROFILE_DECKS)


def load_archetypes(db: sqlite3.Connection) -> list[sqlite3.Row]:
    """Archétypes qui ont au moins une liste dans la fenêtre, du plus joué au moins joué."""
    try:
        return db.execute(
            """
            SELECT archetype, MAX(n_decks) AS n_decks, MAX(n_decks_window) AS n_window,
                   MIN(window_start) AS window_start, MAX(window_end) AS window_end,
                   MAX(computed_at) AS computed_at
            FROM archetype_card_profile
            GROUP BY archetype
            ORDER BY n_decks DESC, archetype
            """
        ).fetchall()
    except sqlite3.OperationalError:  # base construite avant scripts/build_archetype_profiles.py
        return []


def card_images(db: sqlite3.Connection, names: set[str]) -> dict[str, str]:
    """Image par nom de carte. `cards.name` porte <P>/<C>/<Q>, pas les listes : même
    expression que l'index idx_cards_name_clean (TOK-83). Une carte récente absente de
    `cards` n'a pas d'image : le front affiche son repli."""
    if not names:
        return {}
    ordered = sorted(names)
    marks = ",".join("?" for _ in ordered)
    rows = db.execute(
        f"""
        SELECT REPLACE(REPLACE(name, '<', ''), '>', '') AS clean, image_url_small
        FROM cards
        WHERE REPLACE(REPLACE(name, '<', ''), '>', '') IN ({marks}) AND image_url_small IS NOT NULL
        """,
        ordered,
    ).fetchall()
    return {row["clean"]: row["image_url_small"] for row in rows}


def card_stat(row: sqlite3.Row, images: dict[str, str]) -> DeckCardStat:
    return DeckCardStat(
        card_name=row["card_name"],
        n_lists=row["n_lists"],
        share=row["share"],
        median_copies=row["median_copies"],
        role=role_for(row["share"]),
        image_url=images.get(row["card_name"]),
    )


@router.get("", response_model=DeckIndexResponse)
def get_decks(db: sqlite3.Connection = Depends(get_db)) -> DeckIndexResponse:
    archetypes = load_archetypes(db)
    if not archetypes:
        return DeckIndexResponse(data=[], rule=RULE)

    # Cartes de base du main des archétypes à profil. `spread` = nombre d'archétypes de la
    # fenêtre qui jouent la carte au main : à part égale, l'aperçu montre d'abord les cartes
    # propres à l'archétype plutôt qu'une staple présente partout.
    base_rows = db.execute(
        """
        WITH spread AS (
            SELECT card_name, COUNT(*) AS n FROM archetype_card_profile WHERE zone = 'main' GROUP BY card_name
        )
        SELECT p.archetype, p.card_name, p.n_lists, p.share, p.median_copies
        FROM archetype_card_profile p JOIN spread s ON s.card_name = p.card_name
        WHERE p.zone = 'main' AND p.share >= ? AND p.n_decks >= ?
        ORDER BY p.archetype, s.n, p.share DESC, p.card_name
        """,
        (BASE_MIN_SHARE, MIN_PROFILE_DECKS),
    ).fetchall()
    base: dict[str, list[sqlite3.Row]] = {}
    for row in base_rows:
        base.setdefault(row["archetype"], []).append(row)
    images = card_images(db, {r["card_name"] for rows in base.values() for r in rows[:PREVIEW_CARDS]})

    tiers = {entry.archetype: entry for entry in compute_tier_list(db)[0]}
    data = []
    for row in archetypes:
        name = row["archetype"]
        tier_entry = tiers.get(name)
        cards = base.get(name, [])
        data.append(
            DeckIndexEntry(
                archetype=name,
                slug=slugify(name),
                tier=tier_entry.tier if tier_entry else "Rogue",
                decks=row["n_decks"],
                share=row["n_decks"] / row["n_window"],
                has_profile=has_profile(row["n_decks"]),
                image_url=tier_entry.image_url if tier_entry else get_archetype_image(db, name),
                base_cards=len(cards),
                base_copies=sum(c["median_copies"] for c in cards),
                preview=[card_stat(c, images) for c in cards[:PREVIEW_CARDS]],
            )
        )
    first = archetypes[0]
    return DeckIndexResponse(
        data=data,
        window=TierWindow(start=first["window_start"], end=first["window_end"], n_decks=first["n_window"]),
        rule=RULE,
        computed_at=first["computed_at"],
    )


def load_recent_decks(db: sqlite3.Connection, archetype: str, rank: dict[tuple[str, str], int]) -> list[RecentDeck]:
    decks = db.execute(
        """
        SELECT deck_id, author, tournament_type, placement, created
        FROM archetype_recent_decks WHERE archetype = ? ORDER BY position
        """,
        (archetype,),
    ).fetchall()
    rows = db.execute(
        """
        SELECT c.deck_id, c.zone, c.card_name, c.amount
        FROM archetype_recent_deck_cards c
        JOIN archetype_recent_decks d ON d.deck_id = c.deck_id
        WHERE d.archetype = ?
        """,
        (archetype,),
    ).fetchall()
    images = card_images(db, {row["card_name"] for row in rows})
    content: dict[tuple[str, str], list[sqlite3.Row]] = {}
    for row in rows:
        content.setdefault((row["deck_id"], row["zone"]), []).append(row)

    result = []
    for deck in decks:
        zones = []
        for zone in ZONES:
            # Même ordre que le tableau de composition (cartes les plus partagées d'abord).
            cards = sorted(
                content.get((deck["deck_id"], zone), []),
                key=lambda r: (rank.get((zone, r["card_name"]), len(rank)), r["card_name"]),
            )
            zones.append(
                DeckListZone(
                    zone=zone,
                    n_cards=sum(r["amount"] for r in cards),
                    cards=[
                        DeckListCard(card_name=r["card_name"], amount=r["amount"], image_url=images.get(r["card_name"]))
                        for r in cards
                    ],
                )
            )
        result.append(
            RecentDeck(
                deck_id=deck["deck_id"],
                author=deck["author"],
                tournament_type=deck["tournament_type"],
                placement=deck["placement"],
                date=deck["created"][:10],
                zones=zones,
            )
        )
    return result


@router.get("/{slug}", response_model=DeckResponse)
def get_deck(slug: str, db: sqlite3.Connection = Depends(get_db)) -> DeckResponse:
    archetypes = load_archetypes(db)
    archetype = resolve(slug, [row["archetype"] for row in archetypes])
    if archetype is None:
        raise HTTPException(status_code=404, detail=f"Aucune liste récente pour : {slug}")
    summary = next(row for row in archetypes if row["archetype"] == archetype)

    rows = db.execute(
        """
        SELECT zone, card_name, n_lists, share, median_copies
        FROM archetype_card_profile WHERE archetype = ?
        ORDER BY share DESC, median_copies DESC, card_name
        """,
        (archetype,),
    ).fetchall()
    rank = {(row["zone"], row["card_name"]): i for i, row in enumerate(rows)}

    zones: list[DeckZoneProfile] = []
    profiled = has_profile(summary["n_decks"])
    if profiled:
        images = card_images(db, {row["card_name"] for row in rows})
        zones = [
            DeckZoneProfile(zone=zone, cards=[card_stat(row, images) for row in rows if row["zone"] == zone])
            for zone in ZONES
        ]

    tier_entry = next((e for e in compute_tier_list(db, with_images=False)[0] if e.archetype == archetype), None)
    image = get_archetype_image(db, archetype)
    if image is None and zones:
        # Archétype à nom composé ou absent de `cards` : sa carte de base la plus propre… à défaut la première.
        image = next((c.image_url for c in zones[0].cards if c.role == ROLE_BASE and c.image_url), None)

    return DeckResponse(
        archetype=archetype,
        slug=slugify(archetype),
        image_url=image,
        tier=tier_entry.tier if tier_entry else None,
        decks=summary["n_decks"],
        share=summary["n_decks"] / summary["n_window"],
        has_profile=profiled,
        window=TierWindow(start=summary["window_start"], end=summary["window_end"], n_decks=summary["n_window"]),
        rule=RULE,
        computed_at=summary["computed_at"],
        zones=zones,
        recent_decks=load_recent_decks(db, archetype, rank),
    )
