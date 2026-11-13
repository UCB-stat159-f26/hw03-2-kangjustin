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

**Commit history.** In the previous homework I didn't keep a real commit history, so
my work went in as a few big uploads. This time I committed one coherent step at a
time: setup, exceptions, name handling, fixtures, parser, network layer, public
function, plot, README. Writing the commit message forced me to say what each step
did, and running the tests before each commit meant every commit worked on its own.
It also made it easy to see how the package was built up, and I could undo a step
with `git reset --soft HEAD~1` without losing my files.

**Keeping network code separate from cleaning code.** The assignment said not to hit
live servers in tests. I only understood why once I split the package into a
`fetch.py` module (the only code that touches the web) and a `parse.py` module of
pure functions. The pure functions can be tested on the mock female and male career
files, and the network layer can be tested with fake responses. That kept the tests
fast and independent of the website being up.

**Messy real-world data.** Female and male career files store different things for
the opponent: a date of birth for women (so I had to derive the age) and the age
itself for men. Neither file contains the player's own birth date, so it has to come
from the player's page on tennisabstract.com. The mock files didn't reveal that
problem, which showed me that a test passing on a few rows is not the same as the
code working on a real career. When I ran it on Serena Williams I got 1,038 matches
with ages for all of them, which was a relief.

**Small functions.** The limit of 20 lines per function pushed me to write many small
helpers, each with a single job. They were easier to name, to test and to reason
about than one long function would have been.

**Git and Python workflow lessons.** My tests first failed with "No module named
tennisage" because I ran `pytest` from outside my virtual environment. Running
`python -m pytest` made sure the right Python was used. I also learned that a repo
created from a template can already have a starter commit, so my commits sit on top
of it, and that environment variables like `$SRC` only last for one terminal session.