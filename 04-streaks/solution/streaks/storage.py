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
    temp = path.with_name(path.name + ".tmp")
    try:
        with open(temp, "w", encoding="utf-8") as file:
            yield file
        # os.replace swaps the files in one step. There's never a moment
        # when habits.json is missing or only half there.
        os.replace(temp, path)
    finally:
        # After a successful replace, the temp file is gone. If it's still
        # here, something went wrong, so tidy it up. Because this is in a
        # `finally`, it runs even when an exception is on its way out.
        if temp.exists():
            temp.unlink()


def load_habits(path: Path) -> dict[str, Habit]:
    """Read all the habits from a file. No file yet just means no habits yet."""
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        habits = [Habit.from_dict(item) for item in data["habits"]]
    except (ValueError, KeyError, TypeError) as error:
        # ValueError covers broken JSON and bad dates like "2026-13-45".
        # KeyError and TypeError mean the file has the wrong shape.
        logger.error("Couldn't read %s: %s", path, error)
        raise StreaksError(
            f"{path.name} is damaged, so I haven't changed anything. "
            f"Fix it or move it somewhere else, then try again. ({error})"
        )
    return {habit.name: habit for habit in habits}


def save_habits(habits: dict[str, Habit], path: Path) -> None:
    """Write all the habits to a file, safely."""
    data = {"habits": [habit.to_dict() for habit in habits.values()]}
    with atomic_write(path) as file:
        json.dump(data, file, indent=2)
    logger.info("Saved %d habit(s) to %s", len(habits), path.name)
