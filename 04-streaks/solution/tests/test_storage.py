"""Tests for saving and loading.

`tmp_path` is a pytest fixture: a brand new empty folder for each test, so
these tests never touch your real habits.json.
"""

from datetime import date

import pytest

from streaks.habits import Habit, StreaksError
from streaks.storage import atomic_write, load_habits, save_habits


def test_save_then_load_gives_back_the_same_habits(tmp_path):
    path = tmp_path / "habits.json"
    habits = {
        "read": Habit(name="read", created=date(2026, 10, 1), done={date(2026, 10, 1), date(2026, 10, 2)}),
        "run": Habit(name="run", created=date(2026, 10, 5)),
    }
    save_habits(habits, path)
    assert load_habits(path) == habits


def test_no_file_yet_means_no_habits(tmp_path):
    assert load_habits(tmp_path / "habits.json") == {}


@pytest.mark.parametrize("content", ["{not json", '{"habits": [{"name": "read"}]}', '{"habits": [{"name": "read", "created": "2026-13-45", "done": []}]}'])
def test_a_damaged_file_is_reported_and_left_alone(tmp_path, content):
    path = tmp_path / "habits.json"
    path.write_text(content)
    with pytest.raises(StreaksError):
        load_habits(path)
    assert path.read_text() == content


def test_atomic_write_replaces_the_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("old")
    with atomic_write(path) as file:
        file.write("new")
    assert path.read_text() == "new"
    assert list(tmp_path.iterdir()) == [path]      # no .tmp file left behind


def test_atomic_write_keeps_the_old_file_if_something_goes_wrong(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("old")
    with pytest.raises(RuntimeError):
        with atomic_write(path) as file:
            file.write("half of the new")
            raise RuntimeError("the power went off")
    assert path.read_text() == "old"
    assert list(tmp_path.iterdir()) == [path]      # and the .tmp file was tidied up
