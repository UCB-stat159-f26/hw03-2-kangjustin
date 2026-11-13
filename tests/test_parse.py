from pathlib import Path

import pandas as pd
import pytest

from tennisage.errors import CareerDataError
from tennisage.parse import (
    OUTPUT_COLUMNS, clean_career_js, extract_birth_date, extract_match_rows, parse_opponent_age,
)

FIXTURES = Path(__file__).parent / "fixtures"
SERENA_DOB = "1981-09-26"
NADAL_DOB = "1986-06-03"


@pytest.fixture
def female_js():
    return (FIXTURES / "FemalePlayerCareer.js").read_text()


@pytest.fixture
def male_js():
    return (FIXTURES / "MalePlayerCareer.js").read_text()


def test_extract_match_rows_counts(female_js, male_js):
    assert len(extract_match_rows(female_js)) == 3
    assert len(extract_match_rows(male_js)) == 3


def test_extract_match_rows_reads_several_arrays():
    js = 'var matchmx = [["20200101"]]; var morematchmx = [["20190101"]];'
    assert len(extract_match_rows(js)) == 2


@pytest.mark.parametrize("bad", ["", "<html>Not found</html>", "var matchmx = [[oops"])
def test_extract_match_rows_bad_input_raises(bad):
    with pytest.raises(CareerDataError):
        extract_match_rows(bad)


def test_female_opponent_age_is_derived_from_birth_date():
    age = parse_opponent_age("19770119", pd.Timestamp("1995-10-30"))
    assert age == pytest.approx(18.78, abs=0.01)


def test_male_opponent_age_is_used_as_is():
    assert parse_opponent_age("22.264202601", pd.Timestamp("2001-09-10")) == pytest.approx(22.2642)


def test_missing_opponent_age_is_nan():
    assert pd.isna(parse_opponent_age("", pd.Timestamp("2001-09-10")))


def test_female_frame_shape_and_values(female_js):
    frame = clean_career_js(female_js, SERENA_DOB)
    assert list(frame.columns) == OUTPUT_COLUMNS
    first = frame.iloc[0]
    assert first["opponent"] == "Anne Miller" and not first["won"]
    assert first["player_age"] == pytest.approx(14.10, abs=0.01)
    assert first["age_diff"] == pytest.approx(14.10 - 18.78, abs=0.02)


def test_male_frame_uses_given_opponent_age(male_js):
    frame = clean_career_js(male_js, NADAL_DOB)
    first = frame.iloc[0]
    assert first["opponent_age"] == pytest.approx(22.2642, abs=1e-3)
    assert first["player_age"] == pytest.approx(15.27, abs=0.01)
    assert frame["won"].tolist() == [False, False, True]


def test_frame_is_sorted_and_typed(male_js):
    frame = clean_career_js(male_js, NADAL_DOB)
    assert frame["date"].is_monotonic_increasing
    assert pd.api.types.is_datetime64_any_dtype(frame["date"])
    assert frame["opponent_rank"].tolist() == [731, 161, 751]


def test_extract_birth_date():
    assert extract_birth_date("var fullname = 'x'; var dob = 19810926; var ht = 175;") == pd.Timestamp(SERENA_DOB)
    assert extract_birth_date("<html>no dob here</html>") is None
