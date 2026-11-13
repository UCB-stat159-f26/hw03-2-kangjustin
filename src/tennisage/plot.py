"""Public function 2: scatter plot of player age vs. age gap, colored by win/loss."""

import matplotlib.pyplot as plt

REQUIRED_COLUMNS = ("player_age", "age_diff", "won")
WIN_COLOR, LOSS_COLOR = "#2a78d6", "#eb6834"  # blue / orange: colorblind-safe pair
INK, MUTED = "#0b0b0b", "#52514e"


def _check_columns(matches):
    missing = [c for c in REQUIRED_COLUMNS if c not in matches.columns]
    if missing:
        raise ValueError(f"`matches` is missing columns {missing}; build it with get_career_matches().")


def _scatter_group(ax, group, color, label):
    ax.scatter(group["player_age"], group["age_diff"], s=22, color=color, alpha=0.7,
               edgecolors="white", linewidths=0.4, label=f"{label} ({len(group)})")


def _style_axes(ax):
    ax.axhline(0, color=MUTED, linewidth=1, zorder=0)
    ax.grid(color="#e4e3df", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("Player's age (years)", color=INK)
    ax.set_ylabel("Player's age minus opponent's age (years)\nolder than opponent  ↑   ↓  younger", color=INK)


def plot_age_gap(matches, ax=None, title=None):
    """Draw the age-gap scatter for a DataFrame from get_career_matches(); returns the Axes."""
    _check_columns(matches)
    data = matches.dropna(subset=["player_age", "age_diff"])
    ax = ax if ax is not None else plt.subplots(figsize=(10, 6))[1]
    _scatter_group(ax, data[data["won"]], WIN_COLOR, "Win")
    _scatter_group(ax, data[~data["won"]], LOSS_COLOR, "Loss")
    _style_axes(ax)
    name = matches.attrs.get("player", "Player")
    ax.set_title(title or f"{name}: every career match by age and age gap", loc="left", color=INK)
    ax.legend(frameon=False, loc="upper right")
    return ax
