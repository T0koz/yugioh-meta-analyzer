"""Direction des prédictions calculée sur l'écart dessiné (audit de rigueur, A6, lot 20)."""

from app.labels import PRED_DIRECTION_MAP, PRED_GAP_THRESHOLD, direction_from_gap

W_MODEL = 0.3  # notebook 05 : prévision = niveau + 0,3 × variation prédite
NOTEBOOK_DELTA_THRESHOLD = 0.01  # notebook 05 : flèche ↑ / ↓ au-delà de |variation| > 0,01


def notebook_direction(delta: float) -> str:
    arrow = "↑" if delta > NOTEBOOK_DELTA_THRESHOLD else "↓" if delta < -NOTEBOOK_DELTA_THRESHOLD else "→"
    return PRED_DIRECTION_MAP[arrow]


def test_seuil_ramene_a_l_echelle_dessinee():
    assert abs(PRED_GAP_THRESHOLD - W_MODEL * NOTEBOOK_DELTA_THRESHOLD) < 1e-12


def test_meme_classement_que_le_notebook_hors_seuil_exact():
    # Valeurs de novembre 2026 (meta_predictions) : variation complète prédite, niveau observé.
    for current, delta in [(0.1523, 0.00033), (0.1108, -0.0251), (0.0634, 0.0216), (0.0685, -0.0094),
                           (0.0570, -0.0101), (0.0441, 0.0122), (0.0345, -0.0027)]:
        predicted = current + W_MODEL * delta
        assert direction_from_gap(current, predicted) == notebook_direction(delta)


def test_ecart_nul_ou_faible_stable():
    assert direction_from_gap(0.05, 0.05) == "Stable"
    assert direction_from_gap(0.05, 0.0529) == "Stable"
    assert direction_from_gap(0.05, 0.0531) == "Rising"
    assert direction_from_gap(0.05, 0.0469) == "Declining"
