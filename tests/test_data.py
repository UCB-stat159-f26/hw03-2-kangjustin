from pathlib import Path

import pandas as pd
import pytest

from tennisage import data
from tennisage.errors import PlayerNotFoundError

FIXTURES = Path(__file__).parent / "fixtures"


def fake_career(text_file):
    return lambda slug: (FIXTURES / text_file).read_text()


def test_get_career_matches_for_female_player(monkeypatch):
    monkeypatch.setattr(data, "fetch_career_js", fake_career("FemalePlayerCareer.js"))
    monkeypatch.setattr(data, "fetch_birth_date", lambda slug: pd.Timestamp("1981-09-26"))
    matches = data.get_career_matches("serena williams")
    assert len(matches) == 3
    assert matches.attrs["player"] == "Serena Williams"


def test_explicit_birth_date_skips_player_page(monkeypatch):
    monkeypatch.setattr(data, "fetch_career_js", fake_career("MalePlayerCareer.js"))
    monkeypatch.setattr(data, "fetch_birth_date", lambda slug: pytest.fail("should not be called"))
    matches = data.get_career_matches("Rafael Nadal", birth_date="1986-06-03")
    assert matches["player_age"].iloc[0] == pytest.approx(15.27, abs=0.01)


def test_unknown_player_error_propagates(monkeypatch):
    def missing(slug):
        raise PlayerNotFoundError(f"No career data found for '{slug}'.")

    monkeypatch.setattr(data, "fetch_career_js", missing)
    with pytest.raises(PlayerNotFoundError, match="GastonSanchez"):
        data.get_career_matches("Gaston Sanchez")
