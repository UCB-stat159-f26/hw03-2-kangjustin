"""Pure functions that clean tennisabstract.com career JS files (no network)."""

import json
import re

import pandas as pd

from .errors import CareerDataError

DAYS_PER_YEAR = 365.25
# Positions of the fields we keep inside each raw match row of the JS file.
COLUMN_INDEX = {
    "date": 0, "tournament": 1, "surface": 2, "result": 4, "round": 8,
    "score": 9, "opponent": 11, "opponent_rank": 12, "opponent_age_raw": 16,
}
OUTPUT_COLUMNS = [
    "date", "tournament", "surface", "round", "score", "opponent",
    "opponent_rank", "result", "won", "player_age", "opponent_age", "age_diff",
]


def extract_match_rows(js_text):
    """Return the list of raw match rows found in the `*matchmx` arrays of a career JS file."""
    decoder = json.JSONDecoder()
    rows = []
    for found in re.finditer(r"var\s+\w*matchmx\s*=\s*", js_text):
        try:
            block, _ = decoder.raw_decode(js_text, found.end())
        except json.JSONDecodeError as err:
            raise CareerDataError(f"Could not parse the career file: {err}") from err
        rows.extend(block)
    if not rows:
        raise CareerDataError("No match data found in the career file.")
    return rows


def extract_birth_date(page_text):
    """Find `var dob = YYYYMMDD` in a tennisabstract player page; return a Timestamp or None."""
    found = re.search(r"var\s+dob\s*=\s*['\"]?(\d{8})", page_text)
    return pd.to_datetime(found.group(1), format="%Y%m%d") if found else None


def _age_in_years(start, end):
    return (end - start).days / DAYS_PER_YEAR


def parse_opponent_age(raw_value, match_date):
    """Opponent age: men's files give it directly, women's files give a YYYYMMDD birth date."""
    raw_value = str(raw_value).strip()
    if re.fullmatch(r"\d{8}", raw_value):
        return _age_in_years(pd.to_datetime(raw_value, format="%Y%m%d"), match_date)
    try:
        return float(raw_value)
    except ValueError:
        return float("nan")


def _pad(row, width):
    return list(row) + [""] * (width - len(row))


def _rows_to_frame(rows):
    width = max(COLUMN_INDEX.values()) + 1
    records = [{name: _pad(r, width)[i] for name, i in COLUMN_INDEX.items()} for r in rows]
    return pd.DataFrame(records)


def _add_ages(frame, birth_date):
    frame["player_age"] = frame["date"].apply(lambda d: _age_in_years(birth_date, d))
    frame["opponent_age"] = [
        parse_opponent_age(raw, d) for raw, d in zip(frame["opponent_age_raw"], frame["date"])
    ]
    frame["age_diff"] = frame["player_age"] - frame["opponent_age"]
    return frame


def clean_career_js(js_text, birth_date):
    """Turn the text of a career JS file plus the player's birth date into a tidy DataFrame."""
    birth_date = pd.Timestamp(birth_date)
    frame = _rows_to_frame(extract_match_rows(js_text))
    frame["date"] = pd.to_datetime(frame["date"], format="%Y%m%d")
    frame["opponent_rank"] = pd.to_numeric(frame["opponent_rank"], errors="coerce")
    frame["won"] = frame["result"].eq("W")
    frame = _add_ages(frame, birth_date)
    return frame[OUTPUT_COLUMNS].sort_values("date").reset_index(drop=True)
