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


# Audit de rigueur, A6 (lot 20) : la flèche de /predictions est calculée sur l'écart DESSINÉ
# (prévu − observé), et non sur la variation complète prédite par le Ridge (`pred_delta`), dont
# l'haltère ne montre que 30 % (W_MODEL du notebook 05). Le seuil reprend celui du notebook
# (|pred_delta| > 0,01) ramené à l'échelle dessinée : 0,3 × 0,01 = 0,003 (0,3 point de score ×100).
# Réglage à la main, hérité du notebook ; il classe les archétypes comme avant, mais il est lisible.
PRED_GAP_THRESHOLD = 0.003


def direction_from_gap(current: float, predicted: float) -> str:
    gap = predicted - current
    if gap > PRED_GAP_THRESHOLD:
        return "Rising"
    if gap < -PRED_GAP_THRESHOLD:
        return "Declining"
    return "Stable"
