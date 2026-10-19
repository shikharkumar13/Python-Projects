"""The commands you can type, and the code that runs them.

Each command is a function marked with @command. That one line is all it
takes to add a new command: main() finds it in the COMMANDS dictionary.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date
from pathlib import Path

from streaks.habits import Habit, StreaksError, find_habit, weekday_counts
from streaks.heatmap import heatmap
from streaks.storage import DATA_FILE, load_habits, save_habits

logger = logging.getLogger(__name__)

# Every command takes the habits, the extra words typed after the command,
# and today's date. It returns True if it changed anything, so main() knows
# whether to save.
CommandFunc = Callable[[dict[str, Habit], list[str], date], bool]

COMMANDS: dict[str, CommandFunc] = {}


def command(func: CommandFunc) -> CommandFunc:
    """A decorator that registers a function as a command, under its own name.

    Writing @command above `def add(...)` is the same as writing
    add = command(add) after it. So this runs once for each command, when
    Python first reads this file.
    """
    name = func.__name__
    if name in COMMANDS:
        raise ValueError(f"There are two commands called '{name}'.")
    COMMANDS[name] = func
    return func    # hand the function back unchanged, so it still works normally


def plural(count: int, word: str) -> str:
    """plural(1, "day") is "1 day", and plural(3, "day") is "3 days"."""
    if count == 1:
        return f"{count} {word}"
    return f"{count} {word}s"


# ---------------------------------------------------------------------------
# The commands. The first line of each docstring is shown in the help.
# ---------------------------------------------------------------------------

@command
def add(habits: dict[str, Habit], args: list[str], today: date) -> bool:
    """add "read 20 pages"   start tracking a new habit"""
    # " ".join() means it still works if you forget the quotes.
    name = " ".join(args).strip()
    if name == "":
        raise StreaksError('What habit? Try something like: python -m streaks add "read 20 pages"')
    for existing in habits:
        if existing.lower() == name.lower():
            raise StreaksError(f"You're already tracking '{existing}'.")

    habits[name] = Habit(name=name, created=today)
    logger.info("Added habit %r", name)
    print(f"Added '{name}'. When you've done it, type: python -m streaks done {name.split()[0]}")
    return True


@command
def done(habits: dict[str, Habit], args: list[str], today: date) -> bool:
    """done read             mark a habit as done today"""
    habit = find_habit(habits, " ".join(args))
    if not habit.mark_done(today):
        print(f"You've already done '{habit.name}' today. Nice!")
        return False

    logger.info("Marked %r done on %s", habit.name, today)
    streak = habit.current_streak(today)
    print(f"Done: {habit.name}. Your streak is {plural(streak, 'day')}.")
    return True


@command
def remove(habits: dict[str, Habit], args: list[str], today: date) -> bool:
    """remove read           stop tracking a habit, and forget its history"""
    habit = find_habit(habits, " ".join(args))
    del habits[habit.name]
    logger.info("Removed habit %r", habit.name)
    print(f"Removed '{habit.name}'.")
    return True


@command
def status(habits: dict[str, Habit], args: list[str], today: date) -> bool:
    """status                your streaks, and a heatmap of the last 12 weeks"""
    if len(habits) == 0:
        print('No habits yet. Add one with: python -m streaks add "read 20 pages"')
        return False

    width = max(len(name) for name in habits) + 2
    print(f"Your habits on {today:%A} {today.day} {today:%B %Y}")
    print()
    print(f"{'Habit':<{width}}Today   Streak     Best")
    for habit in habits.values():
        if today in habit.done:
            mark = "✓"
            note = ""
        else:
            mark = "·"
            note = ""
            if habit.current_streak(today) > 0:
                note = "   do it today to keep your streak going!"
        current = plural(habit.current_streak(today), "day")
        best = plural(habit.longest_streak(), "day")
        print(f"{habit.name:<{width}}  {mark}   {current:>8} {best:>8}{note}")

    print()
    print("The last 12 weeks:")
    print(heatmap(list(habits.values()), today))
    return False


@command
def stats(habits: dict[str, Habit], args: list[str], today: date) -> bool:
    """stats                 your best day of the week, and how often you keep each habit"""
    counts = weekday_counts(habits)
    if len(counts) == 0:
        print("No check-ins yet. Come back after a few days of: python -m streaks done ...")
        return False

    best_day, best_count = counts.most_common(1)[0]
    print(f"Your best day: {best_day}, with {plural(best_count, 'check-in')}.")
    print()
    for habit in habits.values():
        rate = habit.completion_rate(today)
        print(f"{habit.name}: done {rate:.0%} of the days since you started it")
    return False


# ---------------------------------------------------------------------------
# Running a command
# ---------------------------------------------------------------------------

def usage() -> str:
    """The help text, built from the first line of each command's docstring."""
    lines = ["Usage: python -m streaks <command>", "", "Commands:"]
    for func in COMMANDS.values():
        first_line = (func.__doc__ or "").strip().splitlines()[0]
        lines.append(f"  {first_line}")
    return "\n".join(lines)


def main(argv: list[str], data_file: Path = DATA_FILE, today: date | None = None) -> int:
    """Run one command. Returns the exit code: 0 for OK, 1 for a problem, 2 for a typo.

    `data_file` and `today` can be swapped out, which is how the tests run
    commands without touching your real habits or waiting for tomorrow.
    """
    if today is None:
        today = date.today()

    if len(argv) == 0 or argv[0] in ("help", "-h", "--help"):
        print(usage())
        return 0

    name, args = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"I don't know the command '{name}'.")
        print()
        print(usage())
        return 2

    logger.info("Running %r with %r", name, args)
    try:
        habits = load_habits(data_file)
        changed = COMMANDS[name](habits, args, today)
        if changed:
            save_habits(habits, data_file)
    except StreaksError as error:
        logger.warning("%s", error)
        print(error)
        return 1
    return 0
