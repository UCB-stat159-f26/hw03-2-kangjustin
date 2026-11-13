import pandas as pd
import pytest

from tennisage import fetch
from tennisage.errors import CareerDataError, PlayerNotFoundError


class FakeResponse:
    def __init__(self, text="", status_code=200):
        self.text, self.status_code = text, status_code
        self.ok = status_code < 400

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(f"HTTP {self.status_code}")


def patch_get(monkeypatch, responder):
    monkeypatch.setattr(fetch.requests, "get", lambda url, **kw: responder(url, kw.get("params")))


def test_career_js_returned_when_present(monkeypatch):
    patch_get(monkeypatch, lambda url, params: FakeResponse("var morematchmx = [[]];"))
    assert "matchmx" in fetch.fetch_career_js("SerenaWilliams")


@pytest.mark.parametrize("response", [FakeResponse("nope", 404), FakeResponse("<html>hi</html>", 200)])
def test_unknown_player_gives_meaningful_error(monkeypatch, response):
    patch_get(monkeypatch, lambda url, params: response)
    with pytest.raises(PlayerNotFoundError, match="GastonSanchez"):
        fetch.fetch_career_js("GastonSanchez")


def test_birth_date_tries_both_player_pages(monkeypatch):
    def responder(url, params):
        return FakeResponse("var dob = 19860603;") if url.endswith("/player.cgi") else FakeResponse("", 404)

    patch_get(monkeypatch, responder)
    assert fetch.fetch_birth_date("RafaelNadal") == pd.Timestamp("1986-06-03")


def test_missing_birth_date_raises(monkeypatch):
    patch_get(monkeypatch, lambda url, params: FakeResponse("<html></html>"))
    with pytest.raises(CareerDataError, match="birth_date"):
        fetch.fetch_birth_date("Nobody")
