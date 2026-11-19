"""TOK-148 : `scripts/deploy_prebuilt.py` vérifie que l'API locale lit la base de service (valeurs témoins).

Base synthétique et API remplacée par une fonction de test : ni réseau, ni `serving.db`, ni commande Vercel.
"""

import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import deploy_prebuilt as dp  # noqa: E402


@pytest.fixture
def serving(tmp_path: Path) -> Path:
    path = tmp_path / "data" / "serving.db"
    path.parent.mkdir()
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE ban_radar (card_name TEXT, as_of TEXT, n_decks_window INTEGER);
        INSERT INTO ban_radar VALUES ('A', '2026-11-14', 1883), ('B', '2026-11-14', 1883);
        CREATE TABLE boutique_buy_signals (card_name TEXT, computed_at TEXT);
        INSERT INTO boutique_buy_signals VALUES ('A', '2026-11-09'), ('B', '2026-11-16');
        """
    )
    con.commit()
    con.close()
    return path


def api(**overrides):
    """Fausse API : sert les valeurs de la base synthétique, sauf celles remplacées."""
    answers = {
        "/meta/tier-list": {"data": [{"archetype": "X"}]},
        "/ban-radar?limit=1": {"data": [], "as_of": "2026-11-14", "n_decks_window": 1883},
        "/boutique/signals": {"data": [], "computed_at": "2026-11-16"},
    }
    for route, fields in overrides.items():
        answers[route] = {**answers[route], **fields}

    def fetch(url: str):
        route = url.removeprefix("http://api/v1")
        if route not in answers:
            raise OSError(f"route inattendue {route}")
        return answers[route]

    return fetch


def test_same_witnesses_pass(serving):
    assert dp.witness_mismatches("http://api/v1", serving, api()) == []


@pytest.mark.parametrize(
    "overrides",
    [
        {"/ban-radar?limit=1": {"as_of": "2026-11-07"}},            # API sur une base plus ancienne
        {"/ban-radar?limit=1": {"n_decks_window": 1700}},
        {"/boutique/signals": {"computed_at": None}},              # base sans la colonne datée
    ],
)
def test_a_different_witness_is_reported(serving, overrides):
    problems = dp.witness_mismatches("http://api/v1", serving, api(**overrides))
    assert len(problems) == 1 and "serving.db" in problems[0]


def test_check_api_fails_on_mismatch_and_execute_is_refused(serving, monkeypatch, capsys):
    monkeypatch.setattr(dp, "data_dir", lambda: serving.parent)
    c = dp.Checks()
    dp.check_api(c, "http://api/v1", api(**{"/boutique/signals": {"computed_at": "2026-11-02"}}))
    assert len(c.failed) == 1 and "ne lit pas data/serving.db" in c.failed[0]

    # --execute n'est accepté que si toutes les vérifications passent : l'écart témoin bloque.
    monkeypatch.setattr(dp, "check_config", lambda c: None)
    monkeypatch.setattr(dp, "check_database", lambda c, copy: None)
    monkeypatch.setattr(dp, "check_api", lambda c, url: c.fail("écart témoin"))
    ran = []
    monkeypatch.setattr(dp.subprocess, "run", lambda *a, **k: ran.append(a))
    monkeypatch.setattr(sys, "argv", ["deploy_prebuilt.py", "--execute", "preview"])
    assert dp.main() == 1
    assert ran == [] and "--execute refusé" in capsys.readouterr().out


def test_check_api_passes_when_witnesses_match(serving, monkeypatch):
    monkeypatch.setattr(dp, "data_dir", lambda: serving.parent)
    c = dp.Checks()
    dp.check_api(c, "http://api/v1", api())
    assert c.failed == []


def test_unreachable_api_fails(serving, monkeypatch):
    monkeypatch.setattr(dp, "data_dir", lambda: serving.parent)

    def down(url):
        raise ConnectionRefusedError

    c = dp.Checks()
    dp.check_api(c, "http://api/v1", down)
    assert len(c.failed) == 1 and "injoignable" in c.failed[0]
