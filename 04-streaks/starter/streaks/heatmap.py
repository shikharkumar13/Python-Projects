"""A GitHub-style heatmap of the last few weeks, drawn with characters."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from itertools import groupby

from streaks.habits import Habit

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
LEGEND = "· none   ░ some   ▓ at least half   █ all done"


def shade(done: int, total: int) -> str:
    """Pick the character for one day: how many of the `total` habits were done."""
    # TODO 14
    # - No habits at all, or none done: "·"
    # - All of them done: "█"
    # - At least half done (done * 2 >= total): "▓"
    # - Otherwise: "░"
    return "·"   # placeholder: replace this line


def week_start(day: date) -> date:
    """The Monday of the week that `day` is in."""
    return day - timedelta(days=day.weekday())


def heatmap(habits: list[Habit], today: date, weeks: int = 12) -> str:
    """Draw the last `weeks` weeks: one row per weekday, one column per week."""
    # TODO 15
    # - The first Monday to show is week_start(today) - timedelta(weeks=weeks - 1).
    # - Make a list of every day from that Monday up to today.
    # - Count how many habits were done on each day with a Counter.
    # - Make rows = defaultdict(list). For each day, append its shade() to
    #   rows[day.weekday()]. (Monday is 0 and Sunday is 6.)
    # - Build the lines: month_header(...) first, then one line per weekday,
    #   like "Mon  " + " ".join(rows[0]), then LEGEND. Join them with "\n".
    return "(The heatmap is TODO 15.)"   # placeholder: replace this line


def month_header(first_monday: date, weeks: int) -> str:
    """A line of month names, each one above the first week that starts in it.

    groupby() groups items that are next to each other and share the same
    key. The Mondays are in order, so all the weeks of one month sit
    together, and each group is one month.
    """
    # TODO 16
    # - Make the list of Mondays: first_monday + timedelta(weeks=i) for each i.
    # - Start the header with 5 spaces, to line up with the "Mon  " labels.
    # - groupby(mondays, key=lambda monday: monday.strftime("%b")) gives you
    #   each month name, with the group of Mondays in it.
    # - Each week is 2 characters wide, so a month takes 2 * len(list(group)).
    #   If that's at least 4, add the name padded with .ljust(width).
    #   Otherwise add that many spaces.
    # - Return the header with .rstrip().
    return ""   # placeholder: replace this line
