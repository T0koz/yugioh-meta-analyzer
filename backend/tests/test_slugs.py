"""Identifiant d'URL des archétypes (TOK-101)."""

from app.slugs import resolve, slugify


def test_slug_keeps_only_url_safe_characters():
    assert slugify("Harpie/Amazoness") == "harpie-amazoness"
    assert slugify("D/D/D") == "d-d-d"
    assert slugify("@Ignister") == "ignister"
    assert slugify("Live☆Twin Spright") == "live-twin-spright"
    assert slugify("Gold Pride P.U.N.K.") == "gold-pride-p-u-n-k"
    assert slugify("Maliss <P> March Hare") == "maliss-p-march-hare"
    assert slugify("Évolution Météore") == "evolution-meteore"


def test_resolve_finds_the_name_or_nothing():
    names = ["Snake-Eye", "Harpie/Amazoness", "Branded"]
    assert resolve("harpie-amazoness", names) == "Harpie/Amazoness"
    assert resolve("snake-eye", names) == "Snake-Eye"
    assert resolve("inconnu", names) is None
    assert resolve("", names) is None
    assert resolve("---", names) is None


def test_resolve_ignores_case_so_every_spelling_gives_the_same_page():
    names = ["Snake-Eye", "Harpie/Amazoness", "Branded"]
    assert resolve("Branded", names) == "Branded"
    assert resolve("BRANDED", names) == "Branded"


def test_resolve_is_stable_on_collision():
    assert resolve("snake-eye", ["Snake-Eye", "Snake Eye"]) == "Snake-Eye"
