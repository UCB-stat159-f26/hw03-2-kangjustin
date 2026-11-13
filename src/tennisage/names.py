"""Turn user-typed player names into tennisabstract.com URL slugs."""

import re

from .errors import PlayerNotFoundError


def _capitalize_part(part):
    """'williams' -> 'Williams'; 'WILLIAMS' -> 'Williams'; 'McEnroe' unchanged."""
    if part.isupper():
        part = part.lower()
    return part[:1].upper() + part[1:]


def to_url_slug(player_name):
    """Convert 'serena williams', 'Serena Williams' or 'SerenaWilliams' to 'SerenaWilliams'."""
    if not isinstance(player_name, str):
        raise PlayerNotFoundError(f"Player name must be a string, got {player_name!r}.")
    parts = re.split(r"[\s_\-.]+", player_name.strip())
    parts = [re.sub(r"[^A-Za-z0-9]", "", p) for p in parts]
    slug = "".join(_capitalize_part(p) for p in parts if p)
    if not slug:
        raise PlayerNotFoundError("Player name is empty; try e.g. 'Serena Williams'.")
    return slug
