# tennisage

Retrieve a tennis player's career matches from [tennisabstract.com](https://www.tennisabstract.com)
and draw an NYT-style scatter plot: **player's age** (x) vs. **player's age minus opponent's age** (y),
colored by win / loss.

## Install

```bash
pip install git+https://github.com/UCB-stat159-f26/hw03-2-kangjustin.git
```

## Usage

```python
import matplotlib.pyplot as plt
from tennisage import get_career_matches, plot_age_gap

serena = get_career_matches("serena williams")   # also "Serena Williams" or "SerenaWilliams"
plot_age_gap(serena)
plt.show()

rafa = get_career_matches("Rafael Nadal")
plot_age_gap(rafa)

get_career_matches("GastonSanchez")   # raises PlayerNotFoundError with a helpful message
```

### Public functions

| Function | Input | Output |
|---|---|---|
| `get_career_matches(player_name, birth_date=None)` | player name in any capitalisation / spacing | `pandas.DataFrame`, one row per match |
| `plot_age_gap(matches, ax=None, title=None)` | DataFrame from `get_career_matches` | matplotlib `Axes` with the scatter plot |

`get_career_matches` returns the columns `date, tournament, surface, round, score, opponent,
opponent_rank, result, won, player_age, opponent_age, age_diff`, where
`age_diff = player_age - opponent_age` (positive means the player was older).

`birth_date` (`"YYYY-MM-DD"`) is optional. It is normally read from the player's page on
tennisabstract.com; pass it explicitly if that lookup fails or to skip one web request.

## How it works

1. `names.to_url_slug` normalises the typed name (`"serena williams"` → `SerenaWilliams`).
2. `fetch` downloads `/jsmatches/<Slug>Career.js` (and the player's birth date from their player page).
   A missing file raises `PlayerNotFoundError`.
3. `parse.clean_career_js` pulls the match rows out of the JS and computes ages. Women's files store the
   opponent's **date of birth** (age is derived from it); men's files store the opponent's **age** directly.
4. `plot.plot_age_gap` draws the scatter.

## Tests

```bash
pip install -e ".[test]"
pytest
```

Tests never touch the live site: parsing is tested on mock female/male career files in
`tests/fixtures/`, and the network layer is tested with fake responses.

## Reflections

_TODO (write in your own words before submitting). Things this assignment surfaced:_

- Separating pure cleaning functions (`parse.py`) from the one module that touches the network (`fetch.py`)
  is what made offline tests possible.
- Female and male career files differ (opponent birth date vs. opponent age), and neither file contains
  the player's own birth date, so it has to come from somewhere else.
- Small commits and a 20-line function limit pushed me toward many tiny, individually testable helpers.
