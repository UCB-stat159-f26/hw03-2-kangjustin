"""Thin network layer for tennisabstract.com (the only module that touches the web)."""

import requests

from .errors import CareerDataError, PlayerNotFoundError
from .parse import extract_birth_date

BASE_URL = "https://www.tennisabstract.com"
PLAYER_PAGES = ("cgi-bin/wplayer.cgi", "cgi-bin/player.cgi")  # women's, men's
HEADERS = {"User-Agent": "tennisage (student project; python-requests)"}
TIMEOUT_SECONDS = 20


def _get(url, **params):
    try:
        return requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as err:
        raise CareerDataError(f"Could not reach tennisabstract.com ({err}).") from err


def fetch_career_js(slug):
    """Download the text of /jsmatches/<Slug>Career.js; raise PlayerNotFoundError if absent."""
    response = _get(f"{BASE_URL}/jsmatches/{slug}Career.js")
    if response.status_code == 404 or "matchmx" not in response.text:
        raise PlayerNotFoundError(
            f"No career data found for '{slug}' on tennisabstract.com. "
            "Check the spelling, e.g. 'Serena Williams' or 'Rafael Nadal'."
        )
    response.raise_for_status()
    return response.text


def fetch_birth_date(slug):
    """Look up the player's own birth date on their tennisabstract.com player page."""
    for page in PLAYER_PAGES:
        response = _get(f"{BASE_URL}/{page}", p=slug)
        birth_date = extract_birth_date(response.text) if response.ok else None
        if birth_date is not None:
            return birth_date
    raise CareerDataError(
        f"Could not find the birth date of '{slug}'. Pass it yourself with birth_date='YYYY-MM-DD'."
    )
