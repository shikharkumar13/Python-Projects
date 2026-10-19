"""Tests for the Habit class and the streak maths.

Run them from the folder above this one with:  python -m pytest
"""

from datetime import date, timedelta

import pytest

from streaks.habits import Habit, StreaksError, find_habit, weekday_counts


def make_habit(*days: date, created: date = date(2026, 1, 1)) -> Habit:
    """A small helper, so each test can say just which days were done."""
    return Habit(name="read", created=created, done=set(days))


TODAY = date(2026, 10, 19)
YESTERDAY = TODAY - timedelta(days=1)


# ---------------------------------------------------------------------------
# Current streak
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "done_days, today, expected",
    [
        ([], TODAY, 0),                                            # never done
        ([TODAY], TODAY, 1),                                       # just today
        ([TODAY, YESTERDAY], TODAY, 2),                            # today and yesterday
        ([YESTERDAY], TODAY, 1),                                   # not done yet today: still alive
        ([YESTERDAY, YESTERDAY - timedelta(days=1)], TODAY, 2),
        ([TODAY - timedelta(days=2)], TODAY, 0),                   # missed yesterday: streak is over
        ([TODAY, TODAY - timedelta(days=2)], TODAY, 1),            # a gap of one day resets it
        ([date(2025, 12, 31), date(2026, 1, 1)], date(2026, 1, 1), 2),   # across New Year
    ],
)
def test_current_streak(done_days, today, expected):
    assert make_habit(*done_days).current_streak(today) == expected


def test_streak_across_a_month_boundary():
    habit = make_habit(date(2026, 9, 29), date(2026, 9, 30), date(2026, 10, 1))
    assert habit.current_streak(date(2026, 10, 1)) == 3


def test_streak_across_a_leap_day():
    # 2024 was a leap year, so 28 Feb, 29 Feb and 1 Mar are three days in a row.
    leap = make_habit(date(2024, 2, 28), date(2024, 2, 29), date(2024, 3, 1))
    assert leap.current_streak(date(2024, 3, 1)) == 3
    # 2025 wasn't, so 28 Feb and 1 Mar are already back to back.
    normal = make_habit(date(2025, 2, 28), date(2025, 3, 1))
    assert normal.current_streak(date(2025, 3, 1)) == 2


def test_habit_created_today():
    habit = Habit(name="read", created=TODAY)
    assert habit.current_streak(TODAY) == 0
    assert habit.longest_streak() == 0
    habit.mark_done(TODAY)
    assert habit.current_streak(TODAY) == 1


# ---------------------------------------------------------------------------
# Longest streak
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "done_days, expected",
    [
        ([], 0),
        ([date(2026, 3, 5)], 1),
        ([date(2026, 3, 5), date(2026, 3, 6), date(2026, 3, 7)], 3),
        # two runs: 3 days, then a gap, then 2 days. The longer one wins.
        ([date(2026, 3, 1), date(2026, 3, 2), date(2026, 3, 3), date(2026, 3, 9), date(2026, 3, 10)], 3),
        # the same days in a scrambled order: sets have no order anyway
        ([date(2026, 3, 10), date(2026, 3, 1), date(2026, 3, 9), date(2026, 3, 3), date(2026, 3, 2)], 3),
        ([date(2026, 2, 28), date(2026, 3, 1)], 2),           # 2026 isn't a leap year
    ],
)
def test_longest_streak(done_days, expected):
    assert make_habit(*done_days).longest_streak() == expected


# ---------------------------------------------------------------------------
# Everything else
# ---------------------------------------------------------------------------

def test_mark_done_only_counts_once():
    habit = make_habit()
    assert habit.mark_done(TODAY) is True
    assert habit.mark_done(TODAY) is False
    assert habit.done == {TODAY}


def test_each_habit_gets_its_own_set():
    first = Habit(name="read", created=TODAY)
    second = Habit(name="run", created=TODAY)
    first.mark_done(TODAY)
    assert second.done == set()


def test_to_dict_and_back_again():
    habit = make_habit(date(2026, 10, 2), date(2026, 10, 1), created=date(2026, 9, 30))
    data = habit.to_dict()
    assert data == {"name": "read", "created": "2026-09-30", "done": ["2026-10-01", "2026-10-02"]}
    assert Habit.from_dict(data) == habit


@pytest.mark.parametrize(
    "text, expected",
    [
        ("read 20 pages", "read 20 pages"),     # the full name
        ("read", "read 20 pages"),              # the start of the name
        ("READ", "read 20 pages"),              # capitals don't matter
        ("  drink ", "drink water"),            # spaces around it don't matter
        ("run", "run"),                         # an exact name beats "running club"
    ],
)
def test_find_habit(text, expected):
    habits = {name: Habit(name=name, created=TODAY) for name in ["read 20 pages", "drink water", "run", "running club"]}
    assert find_habit(habits, text).name == expected


@pytest.mark.parametrize("text", ["", "swim", "r"])
def test_find_habit_problems(text):
    # "" is empty, "swim" matches nothing, and "r" could be three different habits.
    habits = {name: Habit(name=name, created=TODAY) for name in ["read 20 pages", "run", "running club"]}
    with pytest.raises(StreaksError):
        find_habit(habits, text)


def test_completion_rate():
    habit = make_habit(date(2026, 10, 1), date(2026, 10, 2), created=date(2026, 10, 1))
    assert habit.completion_rate(date(2026, 10, 4)) == 0.5    # 2 of 4 days
    assert make_habit(created=TODAY).completion_rate(TODAY) == 0.0


def test_weekday_counts():
    # 19 and 26 October 2026 are both Mondays, and 20 October is a Tuesday.
    habits = {
        "read": make_habit(date(2026, 10, 19), date(2026, 10, 26)),
        "run": make_habit(date(2026, 10, 20)),
    }
    assert weekday_counts(habits) == {"Monday": 2, "Tuesday": 1}
