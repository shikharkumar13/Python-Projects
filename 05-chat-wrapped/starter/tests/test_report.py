"""Tests for the report, and for running the whole thing from the command line."""

from datetime import datetime, timedelta

import pytest

from wrapped.cli import chat_title, main
from wrapped.parser import Message
from wrapped.report import build_report, describe_duration
from wrapped.stats import analyse


@pytest.mark.parametrize(
    "length, expected",
    [
        (timedelta(seconds=42), "42 s"),
        (timedelta(minutes=2, seconds=10), "2 min 10 s"),
        (timedelta(hours=1, minutes=5), "1 hour, 5 min"),
        (timedelta(hours=3), "3 hours, 0 min"),
        (timedelta(days=1, hours=1), "1 day, 1 hour"),
        (timedelta(days=11, hours=3, minutes=59), "11 days, 3 hours"),
    ],
)
def test_describe_duration(length, expected):
    assert describe_duration(length) == expected


def test_the_report_names_the_winners():
    base = datetime(2025, 3, 12, 21, 0)
    messages = [
        Message(base, "Riya", "yaar 😂"),
        Message(base + timedelta(minutes=1), "Riya", "yaar guys"),
        Message(base + timedelta(minutes=2), "Arjun", "bro"),
        Message(base.replace(hour=2), "Kabir", "can't sleep"),
    ]
    messages.sort(key=lambda message: message.when)
    report = build_report(analyse(messages), "Goa Gang", 2025)
    assert report.startswith("# Goa Gang: Wrapped 2025")
    assert "The Chatterbox: Riya" in report
    assert "Emoji of the Year: 😂" in report
    assert "The Night Owl: Kabir" in report
    assert "The Lightning Replier: nobody yet" in report       # too few replies to judge
    assert '**Riya**: "yaar" (2 times)' in report
    assert "1 messages" not in report and "1 times" not in report


def test_a_one_message_chat_still_makes_a_report():
    report = build_report(analyse([Message(datetime(2025, 5, 1, 12, 0), "Riya", "hello")]), "Tiny", 2025)
    assert "1 message**" in report and "The Night Owl: nobody" in report


@pytest.mark.parametrize(
    "filename, title",
    [("WhatsApp Chat with Goa Gang.txt", "Goa Gang"), ("sample_chat.txt", "Sample Chat"), ("_chat.txt", "Chat")],
)
def test_chat_title(filename, title, tmp_path):
    assert chat_title(tmp_path / filename) == title


# ---------------------------------------------------------------------------
# The command line
# ---------------------------------------------------------------------------

CHAT = (
    "30/12/2024, 21:45 - Riya: last one of the year\n"
    "02/01/2025, 10:00 - Riya: happy new year 😂\n"
    "02/01/2025, 10:01 - Arjun: bro same\n"
)


def test_main_writes_the_report_for_the_latest_year(tmp_path, capsys):
    path = tmp_path / "goa.txt"
    path.write_text(CHAT, encoding="utf-8")
    assert main([str(path)]) == 0
    saved = (tmp_path / "goa_wrapped_2025.md").read_text(encoding="utf-8")
    assert "Wrapped 2025" in saved and "2 messages" in saved
    assert "For last year, try" in capsys.readouterr().out    # 2025 only has 2 messages


def test_main_with_a_year(tmp_path):
    path = tmp_path / "goa.txt"
    path.write_text(CHAT, encoding="utf-8")
    assert main([str(path), "2024"]) == 0
    assert "1 message**" in (tmp_path / "goa_wrapped_2024.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "content, args, code, words",
    [
        (CHAT, ["2019"], 1, "no messages from 2019"),
        (CHAT, ["twenty"], 2, "should be a number"),
        (CHAT, ["²"], 2, "should be a number"),          # "²".isdigit() is True, but int("²") fails
        ("just some notes\nnot a chat\n", [], 1, "couldn't find any messages"),
        ("32/01/2025, 10:00 - Riya: hi\n", [], 1, "impossible date"),
        ("12/03/25, 9:45\u202fpm - Riya: hi\n", [], 1, "24-hour clock"),     # a 12-hour export
        (CHAT, ["2025", "please"], 2, "too many words"),
    ],
)
def test_main_problems(tmp_path, capsys, content, args, code, words):
    path = tmp_path / "chat.txt"
    path.write_text(content, encoding="utf-8")
    assert main([str(path), *args]) == code
    assert words in capsys.readouterr().out


def test_main_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "nope.txt")]) == 1
    assert "can't find" in capsys.readouterr().out


def test_main_not_utf8(tmp_path, capsys):
    path = tmp_path / "chat.txt"
    path.write_bytes("12/03/2025, 21:45 - Ren\xe9: salut\n".encode("cp1252"))
    assert main([str(path)]) == 1
    assert "UTF-8" in capsys.readouterr().out


def test_main_help(capsys):
    assert main([]) == 0
    assert "Usage" in capsys.readouterr().out


def test_main_zip_file(tmp_path, capsys):
    assert main([str(tmp_path / "WhatsApp Chat with Goa Gang.zip")]) == 1
    assert "Unzip it first" in capsys.readouterr().out


def test_main_cannot_save_but_still_shows_the_report(tmp_path, capsys, monkeypatch):
    path = tmp_path / "goa.txt"
    path.write_text(CHAT, encoding="utf-8")

    # monkeypatch makes writing any file fail, just for this test.
    def refuse(self, *args, **kwargs):
        raise PermissionError("read-only folder")
    monkeypatch.setattr(type(path), "write_text", refuse)
    assert main([str(path), "2025"]) == 1
    out = capsys.readouterr().out
    assert "Wrapped 2025" in out and "couldn't save" in out
