TIER_MAP = {
    "T0": "T0",
    "T1": "T1",
    "T2": "T2",
    "T3": "T3",
    "Rogue": "Rogue",
    "field": "Rogue",
}

TREND_LABEL_MAP = {
    "➡️ stable": "Stable",
    "↗️ montée": "Rising",
    "⬆️ émergence": "Rising",
    "↘️ déclin": "Declining",
    "⬇️ chute forte": "Declining",
}

PRED_DIRECTION_MAP = {
    "↑": "Rising",
    "→": "Stable",
    "↓": "Declining",
}


def map_tier(tier: str) -> str:
    return TIER_MAP.get(tier, "Rogue")


def map_trend_label(label: str | None) -> str:
    return TREND_LABEL_MAP.get(label or "", "Stable")


def map_pred_direction(direction: str | None) -> str:
    return PRED_DIRECTION_MAP.get(direction or "", "Stable")
