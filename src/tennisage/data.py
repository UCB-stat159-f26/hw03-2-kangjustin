"""Public function 1: get a player's career matches as a clean DataFrame."""

import re

import pandas as pd

from .fetch import fetch_birth_date, fetch_career_js
from .names import to_url_slug
from .parse import clean_career_js


def _display_name(slug):
    """'SerenaWilliams' -> 'Serena Williams'."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", slug)


def get_career_matches(player_name, birth_date=None):
    """Return one row per career match for `player_name` (e.g. 'serena williams').

    Columns: date, tournament, surface, round, score, opponent, opponent_rank,
    result ('W'/'L'), won (bool), player_age, opponent_age, age_diff (player - opponent).
    `birth_date` ('YYYY-MM-DD') is optional; if omitted it is read from tennisabstract.com.
    Raises PlayerNotFoundError for unknown players.
    """
    slug = to_url_slug(player_name)
    js_text = fetch_career_js(slug)
    birth_date = pd.Timestamp(birth_date) if birth_date else fetch_birth_date(slug)
    matches = clean_career_js(js_text, birth_date)
    matches.attrs["player"] = _display_name(slug)
    return matches
