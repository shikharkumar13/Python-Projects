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
    if total == 0 or done == 0:
        return "·"
    if done >= total:
        return "█"
    if done * 2 >= total:
        return "▓"
    return "░"


def week_start(day: date) -> date:
    """The Monday of the week that `day` is in."""
    return day - timedelta(days=day.weekday())


def heatmap(habits: list[Habit], today: date, weeks: int = 12) -> str:
    """Draw the last `weeks` weeks: one row per weekday, one column per week."""
    first_monday = week_start(today) - timedelta(weeks=weeks - 1)
    days = [first_monday + timedelta(days=i) for i in range((today - first_monday).days + 1)]

    # How many habits were done on each day. A Counter is a dictionary that
    # starts every key at 0, so counts[day] works even for empty days.
    counts: Counter[date] = Counter()
    for habit in habits:
        for day in habit.done:
            counts[day] += 1

    # One row per weekday. defaultdict(list) makes an empty list the first
    # time we touch a row, so there's no "is this row there yet?" check.
    rows: defaultdict[int, list[str]] = defaultdict(list)
    for day in days:
        rows[day.weekday()].append(shade(counts[day], len(habits)))

    lines = [month_header(first_monday, weeks)]
    for weekday in range(7):
        lines.append(f"{DAY_LABELS[weekday]}  " + " ".join(rows[weekday]))
    lines.append(LEGEND)
    return "\n".join(lines)


def month_header(first_monday: date, weeks: int) -> str:
    """A line of month names, each one above the first week that starts in it.

    groupby() groups items that are next to each other and share the same
    key. The Mondays are in order, so all the weeks of one month sit
    together, and each group is one month.
    """
    mondays = [first_monday + timedelta(weeks=i) for i in range(weeks)]
    header = "     "      # lines up with the "Mon  " labels
    for month, group in groupby(mondays, key=lambda monday: monday.strftime("%b")):
        width = 2 * len(list(group))     # each week column is 2 characters wide
        if width >= 4:
            header += month.ljust(width)
        else:
            header += " " * width         # too narrow for a name, so leave it blank
    return header.rstrip()
