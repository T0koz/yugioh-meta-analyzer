import sqlite3
from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.schemas import (
    BanHistoryCard,
    BanHistoryList,
    BanHistoryResponse,
    BanRadarCriteria,
    BanRadarEntry,
    BanRadarResponse,
)
from app.db import get_db

router = APIRouter(tags=["ban-radar"])

BAN_RADAR_LIMIT_DEFAULT = 50

# Doit rester aligné sur WEIGHTS dans scripts/build_ban_radar.py : la table
# ban_radar stocke les critères bruts (0-1), la pondération est réappliquée ici
# pour renvoyer au front la contribution de chaque critère en points de score.
WEIGHTS = {
    "ubiquity": 0.30,
    "carrier": 0.25,
    "copies": 0.20,
    "restriction": 0.10,
    "momentum": 0.10,
    "bridge": 0.05,
}


@router.get("/ban-radar", response_model=BanRadarResponse)
def get_ban_radar(
    limit: int = Query(BAN_RADAR_LIMIT_DEFAULT, le=200),
    min_score: float = Query(0, ge=0, le=100),
    status: str | None = Query(None, description="Filtre sur le statut TCG actuel"),
    kind: Literal["generic", "archetype"] | None = Query(
        None,
        description="generic = staples sans deck d'attache, archetype = pièces de moteur",
    ),
    db: sqlite3.Connection = Depends(get_db),
) -> BanRadarResponse:
    meta = db.execute("SELECT as_of, n_decks_window FROM ban_radar LIMIT 1").fetchone()
    if meta is None:
        return BanRadarResponse(data=[], as_of="", n_decks_window=0, weights=WEIGHTS)

    rows = db.execute(
        """
        SELECT r.*, c.image_url_small
        FROM ban_radar r
        -- cards.name porte parfois la notation <C>/<P>/<Q> (ex: "Maliss <P>
        -- March Hare") que ban_radar.card_name, dérivé de deck_cards, n'a
        -- jamais — sans le strip, la jointure échoue et l'image manque.
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +r.card_name -- le « + » désactive l'affinité TEXT : sans lui SQLite n'utilise pas idx_cards_name_clean (TOK-83)
        WHERE r.ban_risk_score >= :min_score
          AND (:status IS NULL OR r.current_status = :status)
          -- top_archetype est nul pour les staples sans deck d'attache
          -- (concentration < 50%), renseigné pour les pièces de moteur.
          AND (:kind IS NULL
               OR (:kind = 'generic' AND r.top_archetype IS NULL)
               OR (:kind = 'archetype' AND r.top_archetype IS NOT NULL))
        ORDER BY r.ban_risk_score DESC
        LIMIT :limit
        """,
        {"min_score": min_score, "status": status, "kind": kind, "limit": limit},
    ).fetchall()

    # Le score final est rééchelonné sur le max du dataset : les contributions
    # brutes x poids sont remises à la même échelle pour qu'elles se somment
    # bien au score affiché.
    data = []
    for row in rows:
        weighted = {key: row[key] * weight for key, weight in WEIGHTS.items()}
        total = sum(weighted.values())
        scale = row["ban_risk_score"] / total if total else 0.0
        data.append(
            BanRadarEntry(
                card_name=row["card_name"],
                ban_risk_score=row["ban_risk_score"],
                risk_label=row["risk_label"],
                current_status=row["current_status"],
                deck_share=row["deck_share"],
                decks=row["decks"],
                n_archetypes=row["n_archetypes"],
                mean_copies=row["mean_copies"],
                top_archetype=row["top_archetype"],
                image_url=row["image_url_small"],
                criteria=BanRadarCriteria(
                    **{key: round(value * scale, 2) for key, value in weighted.items()}
                ),
            )
        )

    return BanRadarResponse(
        data=data,
        as_of=meta["as_of"],
        n_decks_window=meta["n_decks_window"],
        weights=WEIGHTS,
    )


def _table_exists(db: sqlite3.Connection, name: str) -> bool:
    return db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)
    ).fetchone() is not None


@router.get("/ban-radar/history", response_model=BanHistoryResponse)
def get_ban_radar_history(db: sqlite3.Connection = Depends(get_db)) -> BanHistoryResponse:
    """Backtest du Ban Radar liste par liste (TOK-55), écrit par scripts/build_ban_history.py.

    Listes retenues et écartées, TCG et OCG. Les listes écartées antérieures aux
    premiers decks collectés (fenêtre vide) ne sont pas renvoyées : elles ne disent
    rien du score, seulement de la période couverte par les données.
    """
    # Table absente tant que build_ban_history.py n'a pas tourné sur la base :
    # réponse vide plutôt qu'une erreur 500.
    if not (_table_exists(db, "ban_backtest_lists") and _table_exists(db, "ban_backtest_cards")):
        return BanHistoryResponse(lists=[], computed_at="", top_n=0, min_decks=0, min_hits=0)

    list_rows = db.execute(
        """
        SELECT * FROM ban_backtest_lists
        WHERE n_decks > 0
        ORDER BY effective_date DESC, format DESC
        """
    ).fetchall()
    if not list_rows:
        return BanHistoryResponse(lists=[], computed_at="", top_n=0, min_decks=0, min_hits=0)

    card_rows = db.execute(
        """
        SELECT b.*, c.image_url_small
        FROM ban_backtest_cards b
        LEFT JOIN cards c ON REPLACE(REPLACE(c.name, '<', ''), '>', '') = +b.card_name -- « + » : voir get_ban_radar (TOK-83)
        -- Top prévu d'abord, dans l'ordre du classement ; puis les cartes touchées
        -- plus bas, par rang ; celles hors univers (rang nul) en dernier.
        ORDER BY b.rank IS NULL, b.rank, b.card_name
        """
    ).fetchall()

    cards_by_list: dict[tuple[str, str], list[BanHistoryCard]] = {}
    seen: set[tuple[str, str, str]] = set()
    for row in card_rows:
        key = (row["format"], row["effective_date"], row["card_name"])
        # cards.name n'est pas unique (renumérotations YGOPRODeck) : une carte ne
        # doit pas apparaître deux fois si la jointure double.
        if key in seen:
            continue
        seen.add(key)
        cards_by_list.setdefault(key[:2], []).append(
            BanHistoryCard(
                card_name=row["card_name"],
                rank=row["rank"],
                ban_risk_score=row["ban_risk_score"],
                baseline_rank=row["baseline_rank"],
                hit=bool(row["hit"]),
                in_top=bool(row["in_top"]),
                generic=bool(row["generic"]),
                top_archetype=row["top_archetype"],
                status_before=row["status_before"],
                status_after=row["status_after"],
                image_url=row["image_url_small"],
            )
        )

    fields = BanHistoryList.model_fields.keys() - {"retained", "cards"}
    lists = [
        BanHistoryList(
            **{f: row[f] for f in fields},
            retained=bool(row["retained"]),
            cards=cards_by_list.get((row["format"], row["effective_date"]), []),
        )
        for row in list_rows
    ]
    first = list_rows[0]
    return BanHistoryResponse(
        lists=lists,
        computed_at=first["computed_at"],
        top_n=max((row["top_n"] or 0) for row in list_rows),
        min_decks=first["min_decks"],
        min_hits=first["min_hits"],
    )
