"""Tests for the commands, run through main() just like the real program.

main() lets us choose the data file and the date, so these tests use a
temporary file and pretend it's whatever day they like.
"""

from datetime import date, timedelta

from streaks.cli import COMMANDS, main
from streaks.storage import load_habits

TODAY = date(2026, 10, 19)


def test_every_command_is_registered():
    assert set(COMMANDS) == {"add", "done", "remove", "status", "stats"}


def test_add_then_done_then_status(tmp_path, capsys):
    data = tmp_path / "habits.json"
    assert main(["add", "read 20 pages"], data, TODAY) == 0
    assert main(["done", "read"], data, TODAY) == 0
    assert "Your streak is 1 day." in capsys.readouterr().out

    assert main(["done", "read"], data, TODAY + timedelta(days=1)) == 0
    assert "Your streak is 2 days." in capsys.readouterr().out

    assert main(["status"], data, TODAY + timedelta(days=1)) == 0
    out = capsys.readouterr().out
    assert "read 20 pages" in out and "✓" in out and "Mon  " in out


def test_add_works_without_quotes(tmp_path):
    data = tmp_path / "habits.json"
    main(["add", "drink", "water"], data, TODAY)
    assert list(load_habits(data)) == ["drink water"]


def test_done_twice_in_one_day(tmp_path, capsys):
    data = tmp_path / "habits.json"
    main(["add", "read"], data, TODAY)
    main(["done", "read"], data, TODAY)
    main(["done", "read"], data, TODAY)
    assert "already done" in capsys.readouterr().out
    assert load_habits(data)["read"].done == {TODAY}


def test_problems_give_exit_code_1_and_change_nothing(tmp_path, capsys):
    data = tmp_path / "habits.json"
    main(["add", "read"], data, TODAY)
    before = data.read_text()
    assert main(["add", "READ"], data, TODAY) == 1          # already tracking it
    assert main(["done", "swim"], data, TODAY) == 1         # no such habit
    assert main(["done"], data, TODAY) == 1                 # which habit?
    assert data.read_text() == before


def test_unknown_command_gives_exit_code_2(tmp_path, capsys):
    assert main(["dance"], tmp_path / "habits.json", TODAY) == 2
    assert "I don't know the command 'dance'" in capsys.readouterr().out


def test_help_lists_every_command(tmp_path, capsys):
    assert main([], tmp_path / "habits.json", TODAY) == 0
    out = capsys.readouterr().out
    for name in COMMANDS:
        assert f"  {name}" in out


def test_remove(tmp_path):
    data = tmp_path / "habits.json"
    main(["add", "read"], data, TODAY)
    main(["add", "run"], data, TODAY)
    assert main(["remove", "read"], data, TODAY) == 0
    assert list(load_habits(data)) == ["run"]


def test_stats(tmp_path, capsys):
    data = tmp_path / "habits.json"
    main(["add", "read"], data, TODAY)
    main(["done", "read"], data, TODAY)
    capsys.readouterr()
    assert main(["stats"], data, TODAY + timedelta(days=1)) == 0
    out = capsys.readouterr().out
    assert "Monday" in out and "50%" in out
