import pytest

from tennisage.errors import PlayerNotFoundError
from tennisage.names import to_url_slug


@pytest.mark.parametrize(
    "typed",
    ["serena williams", "Serena Williams", "SerenaWilliams", "  SERENA   WILLIAMS ", "serena-williams"],
)
def test_name_variants_give_same_slug(typed):
    assert to_url_slug(typed) == "SerenaWilliams"


def test_apostrophes_are_dropped():
    assert to_url_slug("Ons Jabeur's") == "OnsJabeurs"


@pytest.mark.parametrize("bad", ["", "   ", "!!!", None, 42])
def test_empty_or_invalid_names_raise(bad):
    with pytest.raises(PlayerNotFoundError):
        to_url_slug(bad)
