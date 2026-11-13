from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from tennisage.parse import clean_career_js
from tennisage.plot import plot_age_gap

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def matches():
    frame = clean_career_js((FIXTURES / "MalePlayerCareer.js").read_text(), "1986-06-03")
    frame.attrs["player"] = "Rafael Nadal"
    return frame


def test_plot_returns_axes_with_both_groups(matches):
    ax = plot_age_gap(matches)
    assert len(ax.collections) == 2
    assert [len(c.get_offsets()) for c in ax.collections] == [1, 2]
    plt.close("all")


def test_plot_labels_and_title(matches):
    ax = plot_age_gap(matches)
    assert "Rafael Nadal" in ax.get_title(loc="left")
    assert "age" in ax.get_xlabel().lower()
    plt.close("all")


def test_plot_ignores_rows_without_ages(matches):
    matches.loc[0, "age_diff"] = float("nan")
    ax = plot_age_gap(matches)
    assert sum(len(c.get_offsets()) for c in ax.collections) == 2
    plt.close("all")


def test_plot_rejects_wrong_dataframe():
    with pytest.raises(ValueError, match="get_career_matches"):
        plot_age_gap(pd.DataFrame({"x": [1]}))
