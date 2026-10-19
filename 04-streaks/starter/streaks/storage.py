"""Loading and saving habits, without ever losing your data."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

from streaks.habits import Habit, StreaksError

logger = logging.getLogger(__name__)

# The data and the log live in the folder just above the package, so
# starter/ and solution/ each keep their own.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "habits.json"
LOG_FILE = PROJECT_DIR / "streaks.log"


@contextmanager
def atomic_write(path: Path) -> Iterator[TextIO]:
    """Open a file for writing, so that a crash can never leave it half-written.

    Everything is written to a temporary file first. Only when the whole
    `with` block has finished does the temporary file replace the real one.
    If anything goes wrong halfway, the old file is still there, untouched.
    """
    # TODO 8
    # - The temporary file goes next to the real one:
    #     temp = path.with_name(path.name + ".tmp")
    # - Inside a try:
    #     - open `temp` for writing and `yield` the file. Whatever the caller
    #       writes in their `with` block happens at that yield.
    #     - after the inner `with` closes the file, os.replace(temp, path)
    # - In a finally: if temp still exists, something went wrong, so delete it
    #   with temp.unlink().
    # The placeholder below works, but it's NOT safe: it writes straight into the
    # real file, so a crash halfway leaves it broken. The test in
    # tests/test_storage.py proves it.
    with open(path, "w", encoding="utf-8") as file:   # placeholder: not safe yet!
        yield file


def load_habits(path: Path) -> dict[str, Habit]:
    """Read all the habits from a file. No file yet just means no habits yet."""
    # TODO 9
    # - If the file doesn't exist yet, return {}.
    # - Inside a try, open it (encoding="utf-8-sig"), json.load() it, and turn
    #   each item in data["habits"] into a Habit with Habit.from_dict().
    # - except (ValueError, KeyError, TypeError): log the error, then raise
    #   StreaksError saying the file is damaged and nothing was changed.
    # - Return a dictionary of name -> Habit.
    return {}   # placeholder: replace this line


def save_habits(habits: dict[str, Habit], path: Path) -> None:
    """Write all the habits to a file, safely."""
    # TODO 10
    # - Make data = {"habits": [...]}, with habit.to_dict() for every habit.
    # - Write it with:  with atomic_write(path) as file:
    #                       json.dump(data, file, indent=2)
    # - Log that you saved, with logger.info(...).
    print("(Saving is TODO 10, so nothing was saved.)")   # placeholder
