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
        if day in self.done:
            return False
        self.done.add(day)
        return True

    def current_streak(self, today: date) -> int:
        """How many days in a row the habit has been done, up to today.

        If today isn't done yet, the streak still counts up to yesterday.
        You have until midnight, so not having done it *yet* doesn't break it.
        """
        if today in self.done:
            day = today
        else:
            day = today - ONE_DAY

        streak = 0
        while day in self.done:
            streak += 1
            day -= ONE_DAY
        return streak

    def longest_streak(self) -> int:
        """The longest run of days in a row, ever."""
        longest = 0
        run = 0
        previous: date | None = None
        for day in sorted(self.done):
            if previous is not None and day - previous == ONE_DAY:
                run += 1
            else:
                run = 1
            longest = max(longest, run)
            previous = day
        return longest

    def completion_rate(self, today: date) -> float:
        """The share of days since the habit was created that it was done, from 0.0 to 1.0."""
        days = (today - self.created).days + 1      # +1 counts the created day itself
        if days <= 0:
            return 0.0
        return len(self.done) / days

    def to_dict(self) -> dict:
        """Turn the habit into plain values that json can save.

        json doesn't know about dates or sets, so dates become text like
        "2026-10-19", and the set becomes a sorted list.
        """
        return {
            "name": self.name,
            "created": self.created.isoformat(),
            "done": sorted(day.isoformat() for day in self.done),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Habit:
        """The opposite of to_dict(): build a Habit from saved values.

        A classmethod is called on the class itself, Habit.from_dict(...),
        because there's no Habit yet when you call it.
        """
        return cls(
            name=data["name"],
            created=date.fromisoformat(data["created"]),
            done={date.fromisoformat(text) for text in data["done"]},
        )


def find_habit(habits: dict[str, Habit], text: str) -> Habit:
    """Find a habit from the start of its name, so "read" finds "read 20 pages".

    An exact name always wins. Otherwise the text must match the start of
    exactly one habit. Capital letters don't matter.
    """
    text = text.strip().lower()
    if text == "":
        raise StreaksError("Which habit? Try something like: python -m streaks done read")

    for name, habit in habits.items():
        if name.lower() == text:
            return habit

    matches = [habit for name, habit in habits.items() if name.lower().startswith(text)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) == 0:
        raise StreaksError(f"There's no habit called '{text}'. See them all with: python -m streaks status")
    names = ", ".join(f"'{habit.name}'" for habit in matches)
    raise StreaksError(f"'{text}' could be {names}. Type a bit more of the name.")


def weekday_counts(habits: dict[str, Habit]) -> Counter[str]:
    """Count how many check-ins happened on each day of the week, across all habits."""
    counts: Counter[str] = Counter()
    for habit in habits.values():
        for day in habit.done:
            counts[WEEKDAY_NAMES[day.weekday()]] += 1
    return counts
