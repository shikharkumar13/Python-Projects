"""Tests for the heatmap."""

from datetime import date

import pytest

from streaks.habits import Habit
from streaks.heatmap import heatmap, month_header, shade, week_start


@pytest.mark.parametrize(
    "done, total, expected",
    [
        (0, 3, "·"),
        (1, 3, "░"),
        (2, 3, "▓"),
        (3, 3, "█"),
        (1, 2, "▓"),     # exactly half counts as "at least half"
        (1, 1, "█"),
        (0, 0, "·"),     # no habits at all
    ],
)
def test_shade(done, total, expected):
    assert shade(done, total) == expected


@pytest.mark.parametrize(
    "day, monday",
    [
        (date(2026, 10, 19), date(2026, 10, 19)),   # a Monday is its own week start
        (date(2026, 10, 25), date(2026, 10, 19)),   # Sunday
        (date(2026, 10, 1), date(2026, 9, 28)),     # a week that starts in the month before
    ],
)
def test_week_start(day, monday):
    assert week_start(day) == monday


def test_heatmap_shape():
    today = date(2026, 10, 21)       # a Wednesday
    habit = Habit(name="read", created=date(2026, 1, 1), done={today, date(2026, 10, 19)})
    lines = heatmap([habit], today, weeks=12).splitlines()

    assert len(lines) == 9           # month header, 7 weekdays, legend
    monday, tuesday, wednesday, thursday = lines[1], lines[2], lines[3], lines[4]
    assert monday.startswith("Mon  ")
    assert monday.count(" ") >= 11
    assert monday.endswith("█")       # 19 October was done
    assert tuesday.endswith("·")      # 20 October wasn't
    assert wednesday.endswith("█")    # today was done
    # Thursday hasn't happened yet this week, so its row is one week shorter.
    assert len(thursday) == len(wednesday) - 2


def test_month_header():
    # 12 Mondays from 3 August 2026 run to 19 October: Aug (5), Sep (4), Oct (3).
    header = month_header(date(2026, 8, 3), 12)
    assert header == "     Aug       Sep     Oct"
