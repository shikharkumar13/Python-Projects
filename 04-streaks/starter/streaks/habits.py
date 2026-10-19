"""The Habit dataclass, and all the date maths for streaks.

Nothing in this file reads the clock. Every function that needs "today" is
given it as an argument. That's what lets the tests pretend it's any day
they like: a leap day, New Year's Day, or the day a habit was created.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta

ONE_DAY = timedelta(days=1)
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class StreaksError(Exception):
    """A problem to tell the user about, like a habit that doesn't exist."""


@dataclass
class Habit:
    """One habit you want to keep up, like "read 20 pages".

    @dataclass writes __init__, __repr__ and __eq__ for us, from the
    fields listed below.
    """

    name: str
    created: date
    # A set, because a day is either done or not: doing it twice changes
    # nothing. It can't be `= set()`: dataclasses refuse a mutable default,
    # because every Habit would end up sharing the same set. default_factory
    # makes a brand new set for each Habit.
    done: set[date] = field(default_factory=set)

    def mark_done(self, day: date) -> bool:
        """Record the habit as done on `day`.

        Returns True if that's new, or False if it was already done.
        """
        # TODO 2
        # - If `day` is already in self.done, return False.
        # - Otherwise .add() it to self.done and return True.
        return False   # placeholder: replace this line

    def current_streak(self, today: date) -> int:
        """How many days in a row the habit has been done, up to today.

        If today isn't done yet, the streak still counts up to yesterday.
        You have until midnight, so not having done it *yet* doesn't break it.
        """
        # TODO 3
        # - Decide where to start counting: today if today is in self.done,
        #   otherwise yesterday (today - ONE_DAY).
        # - Count backwards: while that day is in self.done, add 1 to the streak
        #   and step back one day with `day -= ONE_DAY`.
        # - Return the streak.
        return 0   # placeholder: replace this line

    def longest_streak(self) -> int:
        """The longest run of days in a row, ever."""
        # TODO 4
        # - Loop over sorted(self.done), remembering the previous day.
        # - If this day is exactly ONE_DAY after the previous one, the run goes on:
        #   add 1. Otherwise a new run starts at 1.
        # - Keep track of the biggest run you've seen, and return it.
        #   (No days at all means 0.)
        return 0   # placeholder: replace this line

    def completion_rate(self, today: date) -> float:
        """The share of days since the habit was created that it was done, from 0.0 to 1.0."""
        # TODO 17
        # - The number of days since it was created, counting the created day too:
        #     (today - self.created).days + 1
        # - If that's 0 or less, return 0.0. Otherwise return len(self.done) / days.
        return 0.0   # placeholder: replace this line

    def to_dict(self) -> dict:
        """Turn the habit into plain values that json can save.

        json doesn't know about dates or sets, so dates become text like
        "2026-10-19", and the set becomes a sorted list.
        """
        # TODO 5
        # - Return a dictionary with three keys: "name", "created" and "done".
        # - Dates become text with .isoformat(), e.g. "2026-10-19".
        # - "done" is a list of those texts, sorted, so the file is easy to read.
        return {}   # placeholder: replace this line

    @classmethod
    def from_dict(cls, data: dict) -> Habit:
        """The opposite of to_dict(): build a Habit from saved values.

        A classmethod is called on the class itself, Habit.from_dict(...),
        because there's no Habit yet when you call it.
        """
        # TODO 6
        # - The opposite of to_dict(). date.fromisoformat("2026-10-19") turns the
        #   text back into a date.
        # - Build the habit with cls(name=..., created=..., done=...). `cls` here
        #   means Habit. "done" needs to be a set of dates again.
        raise StreaksError("Reading saved habits is TODO 6.")   # placeholder


def find_habit(habits: dict[str, Habit], text: str) -> Habit:
    """Find a habit from the start of its name, so "read" finds "read 20 pages".

    An exact name always wins. Otherwise the text must match the start of
    exactly one habit. Capital letters don't matter.
    """
    # TODO 7
    # - Clean up `text` with .strip().lower(). If it's empty, raise StreaksError
    #   with a hint.
    # - If any habit's name (lowercased) is exactly `text`, return that habit.
    # - Otherwise make a list of the habits whose lowercased name .startswith(text).
    #     - Exactly one: return it.
    #     - None: raise StreaksError, saying there's no habit called that.
    #     - More than one: raise StreaksError, listing them and asking for more
    #       of the name.
    raise StreaksError("Finding a habit by name is TODO 7.")   # placeholder


def weekday_counts(habits: dict[str, Habit]) -> Counter[str]:
    """Count how many check-ins happened on each day of the week, across all habits."""
    # TODO 18
    # - Make an empty Counter().
    # - For every day in every habit's .done, add 1 to the count for that
    #   day's name: WEEKDAY_NAMES[day.weekday()]
    # - Return the Counter.
    return Counter()   # placeholder: replace this line
