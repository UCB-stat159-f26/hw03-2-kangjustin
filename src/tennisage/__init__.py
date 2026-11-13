"""tennisage: career match data and age-gap plots from tennisabstract.com."""

from .data import get_career_matches
from .errors import CareerDataError, PlayerNotFoundError, TennisAgeError
from .plot import plot_age_gap

__version__ = "0.1.0"
__all__ = [
    "get_career_matches", "plot_age_gap",
    "PlayerNotFoundError", "CareerDataError", "TennisAgeError",
]
