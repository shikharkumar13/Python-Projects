"""Tests for reading a chat export.

Each test writes a tiny chat into a temporary file (tmp_path) and reads it back.
"""

import types
from datetime import datetime

import pytest

from wrapped import parser
from wrapped.parser import LINE_START, SENDER, ChatFormatError, Message, latest_year, read_messages


def chat(tmp_path, text: str):
    """Write `text` to a chat file and return the messages read from it."""
    path = tmp_path / "chat.txt"
    path.write_text(text, encoding="utf-8")
    return list(read_messages(path))


# ---------------------------------------------------------------------------
# The two patterns on their own
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "line, expected",
    [
        ("12/03/2025, 21:45 - Riya: hi", {"day": "12", "month": "03", "year": "2025", "hour": "21", "minute": "45", "rest": "Riya: hi"}),
        ("1/3/25, 9:05 - Riya: hi", {"day": "1", "month": "3", "year": "25", "hour": "9", "minute": "05", "rest": "Riya: hi"}),
        ("12/03/2025, 21:45 - Riya added Arjun", {"day": "12", "month": "03", "year": "2025", "hour": "21", "minute": "45", "rest": "Riya added Arjun"}),
    ],
)
def test_line_start_matches(line, expected):
    match = LINE_START.match(line)
    assert match is not None
    assert match.groupdict() == expected


@pytest.mark.parametrize(
    "line",
    [
        "- sunscreen",                        # the second line of a message
        "see you at 12/03/2025, 21:45",       # a date, but not at the start
        "12/03/2025 21:45 - Riya: hi",        # the comma is missing
        "",
    ],
)
def test_line_start_does_not_match(line):
    assert LINE_START.match(line) is None


@pytest.mark.parametrize(
    "rest, sender, text",
    [
        ("Riya: see you tomorrow!", "Riya", "see you tomorrow!"),
        ("Riya: time: 9pm", "Riya", "time: 9pm"),                # the name stops at the FIRST colon
        ("+91 98765 43210: who is this?", "+91 98765 43210", "who is this?"),
    ],
)
def test_sender(rest, sender, text):
    match = SENDER.match(rest)
    assert (match["sender"], match["text"]) == (sender, text)


@pytest.mark.parametrize(
    "rest",
    [
        "Riya added Arjun",
        'Riya created group "Goa Gang"',
        "Messages and calls are end-to-end encrypted.",
        'Riya changed the subject from "Trip: Goa" to "Goa"',     # a colon, but inside quotes
    ],
)
def test_system_lines_have_no_sender(rest):
    assert SENDER.match(rest) is None


# ---------------------------------------------------------------------------
# Reading whole chats
# ---------------------------------------------------------------------------

def test_reading_simple_messages(tmp_path):
    messages = chat(tmp_path, "12/03/2025, 21:45 - Riya: see you tomorrow!\n12/03/2025, 21:47 - Arjun: bye\n")
    assert messages == [
        Message(datetime(2025, 3, 12, 21, 45), "Riya", "see you tomorrow!"),
        Message(datetime(2025, 3, 12, 21, 47), "Arjun", "bye"),
    ]


def test_the_last_message_is_not_lost(tmp_path):
    # The classic bug: the last message is still waiting when the file ends.
    messages = chat(tmp_path, "12/03/2025, 21:45 - Riya: first\n12/03/2025, 21:46 - Riya: last\n")
    assert messages[-1].text == "last"


def test_a_line_without_a_timestamp_belongs_to_the_message_above(tmp_path):
    messages = chat(tmp_path, "12/03/2025, 21:45 - Arjun: Packing list:\n- sunscreen\n- chargers\n12/03/2025, 21:50 - Riya: ok\n")
    assert len(messages) == 2
    assert messages[0].text == "Packing list:\n- sunscreen\n- chargers"


def test_system_lines_are_skipped(tmp_path):
    text = (
        "12/03/2025, 21:40 - Messages and calls are end-to-end encrypted. Tap to learn more.\n"
        '12/03/2025, 21:41 - Riya created group "Goa Gang"\n'
        "12/03/2025, 21:41 - Riya added Arjun\n"
        "12/03/2025, 21:45 - Riya: hello!\n"
        "12/03/2025, 21:46 - Arjun left\n"
    )
    assert [m.text for m in chat(tmp_path, text)] == ["hello!"]


def test_a_line_after_a_system_line_is_skipped_too(tmp_path):
    text = "12/03/2025, 21:45 - Riya: hello\n12/03/2025, 21:46 - Riya changed the group description\nsecond line of it\n"
    messages = chat(tmp_path, text)
    assert [m.text for m in messages] == ["hello"]


def test_two_digit_years(tmp_path):
    assert chat(tmp_path, "12/03/25, 21:45 - Riya: hi\n")[0].when == datetime(2025, 3, 12, 21, 45)


def test_month_first_dates(tmp_path, monkeypatch):
    # monkeypatch changes DAY_FIRST just for this one test.
    monkeypatch.setattr(parser, "DAY_FIRST", False)
    assert chat(tmp_path, "03/12/2025, 21:45 - Riya: hi\n")[0].when == datetime(2025, 3, 12, 21, 45)


def test_an_impossible_date_names_its_line(tmp_path):
    with pytest.raises(ChatFormatError, match="Line 2"):
        chat(tmp_path, "12/03/2025, 21:45 - Riya: hi\n03/13/2025, 21:45 - Riya: hi\n")


def test_invisible_marks_are_ignored(tmp_path):
    # A byte order mark at the start of the file, and a left-to-right mark.
    path = tmp_path / "chat.txt"
    path.write_text("\ufeff12/03/2025, 21:45 - \u200eRiya: hi\n", encoding="utf-8")
    assert list(read_messages(path)) == [Message(datetime(2025, 3, 12, 21, 45), "Riya", "hi")]


def test_an_empty_file_has_no_messages(tmp_path):
    assert chat(tmp_path, "") == []


def test_read_messages_is_a_generator(tmp_path):
    path = tmp_path / "chat.txt"
    path.write_text("12/03/2025, 21:45 - Riya: hi\n", encoding="utf-8")
    assert isinstance(read_messages(path), types.GeneratorType)


def test_latest_year(tmp_path):
    messages = chat(tmp_path, "30/12/2024, 21:45 - Riya: hi\n02/01/2025, 10:00 - Riya: happy new year\n")
    assert latest_year(messages) == 2025
    assert latest_year([]) is None
