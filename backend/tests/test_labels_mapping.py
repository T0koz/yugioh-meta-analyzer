"""Correspondances de libellés (`app/labels.py`) : tier, tendance, direction (TOK-135, sans base)."""

from app.labels import (
    PRED_DIRECTION_MAP,
    TIER_MAP,
    TREND_LABEL_MAP,
    map_pred_direction,
    map_tier,
    map_trend_label,
)


def test_known_tiers_keep_their_name_and_field_is_rogue():
    for tier in ("T0", "T1", "T2", "T3", "Rogue"):
        assert map_tier(tier) == tier
    assert map_tier("field") == "Rogue"


def test_unknown_tier_falls_back_to_rogue():
    assert map_tier("T9") == "Rogue"
    assert map_tier("") == "Rogue"


def test_trend_labels_map_to_the_three_api_values():
    assert set(TREND_LABEL_MAP.values()) == {"Rising", "Stable", "Declining"}
    assert map_trend_label("⬆️ émergence") == "Rising"
    assert map_trend_label("⬇️ chute forte") == "Declining"


def test_missing_or_unknown_trend_is_stable():
    assert map_trend_label(None) == "Stable"
    assert map_trend_label("inconnu") == "Stable"


def test_prediction_arrows_map_to_the_three_api_values():
    assert set(PRED_DIRECTION_MAP.values()) == {"Rising", "Stable", "Declining"}
    assert map_pred_direction("↑") == "Rising"
    assert map_pred_direction("↓") == "Declining"
    assert map_pred_direction(None) == "Stable"
    assert map_pred_direction("?") == "Stable"


def test_every_mapped_tier_is_a_value_the_schema_accepts():
    # Tier = Literal["T0", "T1", "T2", "T3", "Rogue"] dans app/schemas.py.
    assert set(TIER_MAP.values()) <= {"T0", "T1", "T2", "T3", "Rogue"}
