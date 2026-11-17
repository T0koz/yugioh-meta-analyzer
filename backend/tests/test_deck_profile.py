from app.deck_profile import MIN_PROFILE_DECKS, has_profile, role_for


def test_role_thresholds_are_inclusive_at_the_lower_bound():
    assert role_for(1.0) == "base"
    assert role_for(0.80) == "base"
    assert role_for(0.799) == "appoint"
    assert role_for(0.20) == "appoint"
    assert role_for(0.199) is None


def test_seven_lists_out_of_eight_is_base():
    # À l'effectif minimal, « de base » tolère une seule liste sans la carte.
    assert role_for(7 / 8) == "base"
    assert role_for(6 / 8) == "appoint"


def test_profile_needs_the_minimum_number_of_lists():
    assert not has_profile(MIN_PROFILE_DECKS - 1)
    assert has_profile(MIN_PROFILE_DECKS)
