"""Custom exceptions so users get meaningful error messages."""


class TennisAgeError(Exception):
    """Base class for all tennisage errors."""


class PlayerNotFoundError(TennisAgeError, ValueError):
    """Raised when tennisabstract.com has no career file for the given name."""


class CareerDataError(TennisAgeError, ValueError):
    """Raised when a career file (or player page) cannot be parsed."""
