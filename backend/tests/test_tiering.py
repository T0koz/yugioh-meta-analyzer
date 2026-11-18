"""Règles de la tier list maison (TOK-91) : seuils et test de tendance."""

from app.tiering import benjamini_hochberg, meta_score_for, tier_for, trend_for, trend_pvalue, trends_corrected


def test_tiers_follow_share_thresholds():
    assert tier_for(0.45, 180) == "T0"
    assert tier_for(0.207, 82) == "T1"
    assert tier_for(0.08, 32) == "T2"
    assert tier_for(0.04, 16) == "T3"
    assert tier_for(0.028, 11) == "Rogue"


def test_too_few_decks_is_rogue_whatever_the_share():
    assert tier_for(0.20, 4) == "Rogue"


def test_trend_needs_a_significant_change():
    # Elfnote, 2026-11-16 : 82/396 contre 76/519 (z ≈ +2,4)
    assert trend_for(82, 396, 76, 519) == "Rising"
    # Dark Magician Chaos Ritual : 19/396 contre 55/519 (z ≈ -3,2)
    assert trend_for(19, 396, 55, 519) == "Declining"
    # Branded : 16/396 contre 24/519, dans le bruit
    assert trend_for(16, 396, 24, 519) == "Stable"


def test_trend_is_stable_on_tiny_counts():
    # 5 decks contre 0 donnerait z = +2,6 : trop peu pour conclure.
    assert trend_for(5, 396, 0, 519) == "Stable"
    assert trend_for(10, 396, 0, 0) == "Stable"


def test_meta_score_is_one_for_a_deck_that_is_everything_and_best_placed():
    assert meta_score_for(1.0, 2.0, 0.5) == 1.0
    assert meta_score_for(0.2, 0.0, 0.5) == 0.0


def test_benjamini_hochberg_ignore_les_tests_non_appliques():
    # m = 3 tests : seuils 0,0167 / 0,0333 / 0,05.
    assert benjamini_hochberg([0.01, None, 0.04, 0.03]) == [True, False, True, True]
    assert benjamini_hochberg([0.02, 0.04, 0.5]) == [False, False, False]
    assert benjamini_hochberg([None, None]) == [False, False]


def test_pvalue_coherente_avec_le_seuil_de_trend_for():
    p = trend_pvalue(82, 396, 76, 519)  # Elfnote, z ≈ +2,4
    assert p is not None and p < 0.05
    assert trend_pvalue(5, 396, 0, 519) is None


def test_tendance_corrigee_retire_un_signal_isole_parmi_beaucoup_de_tests():
    # Un seul écart à p ≈ 0,03 parmi 20 archétypes stables : significatif seul, pas après correction.
    counts = [(30, 30)] * 19 + [(25, 18)]
    assert trend_for(25, 396, 18, 519) == "Rising"
    assert trends_corrected(counts, 396, 519)[-1] == "Stable"
    # Deux écarts nets restent.
    assert trends_corrected([(82, 76), (19, 55), (16, 24)], 396, 519) == ["Rising", "Declining", "Stable"]
