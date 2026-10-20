"""Reading a WhatsApp chat export, one message at a time.

An exported chat looks like this:

    12/03/2025, 21:45 - Riya: see you tomorrow!
    12/03/2025, 21:46 - Arjun: Packing list:
    - sunscreen
    - chargers
    12/03/2025, 21:50 - Meera added Zoya

Each message starts with a date and time. A line without one (like the
packing list) is the rest of the message above it. Lines with no "Name:"
part are system messages, and we skip them.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# 12/03/2025 means 12 March in India and the UK, but 3 December in the US.
# WhatsApp uses whatever your phone uses. If your dates come out wrong, or
# you get an "impossible date" error, set this to False.
DAY_FIRST = True

# The start of every message line: "12/03/2025, 21:45 - ". With re.VERBOSE,
# spaces in the pattern are ignored and # starts a comment, so a pattern can
# be spread over several lines and explained as it goes.
LINE_START = re.compile(
    r"""
    ^
    (?P<day>\d{1,2}) / (?P<month>\d{1,2}) / (?P<year>\d{4}|\d{2})   # 12/03/2025 or 12/03/25
    ,\s
    (?P<hour>\d{1,2}) : (?P<minute>\d{2})                              # 21:45
    \s-\s                                                              # " - "
    (?P<rest>.*)                                                       # everything after that
    $
    """,
    re.VERBOSE,
)

# What comes after the dash, for a real message: "Riya: see you tomorrow!".
# [^:"]+? means "as few characters as possible that aren't a colon or a
# quote", so the name stops at the FIRST colon, and a message like
# "time: 9pm" keeps its own colon. Why no quotes? System lines put group
# names in quotes, and a group name can have a colon in it:
#   Riya changed the subject from "Trip: Goa" to "Goa"
# Real people's names don't have quotes in them, so that line can't match.
SENDER = re.compile(
    r"""
    ^
    (?P<sender>[^:"]+?)   # the name: no colons or quotes, up to the first colon
    :\s                   # ": "
    (?P<text>.*)          # the message itself
    $
    """,
    re.VERBOSE,
)


class ChatFormatError(Exception):
    """Raised when the chat file has something in it we can't make sense of."""


@dataclass
class Message:
    """One message: when it was sent, who sent it, and what it said."""

    when: datetime
    sender: str
    text: str


def parse_when(match: re.Match[str], line_number: int) -> datetime:
    """Turn the date and time parts of a LINE_START match into a datetime."""
    day, month = int(match["day"]), int(match["month"])
    if not DAY_FIRST:
        day, month = month, day
    year = int(match["year"])
    if year < 100:          # "25" means 2025
        year += 2000
    try:
        return datetime(year, month, day, int(match["hour"]), int(match["minute"]))
    except ValueError:
        raise ChatFormatError(
            f"Line {line_number} has an impossible date or time: {match.group()[:17]!r}. "
            "If your phone writes the month before the day, set DAY_FIRST = False in parser.py."
        )


def read_messages(path: Path) -> Iterator[Message]:
    """Yield the messages in a chat export, one at a time.

    This is a generator, so it never holds the whole chat in memory. It reads
    one line, and hands over a message as soon as it knows the message is
    complete, which is when the NEXT message starts.
    """
    current: Message | None = None

    # utf-8-sig copes with the invisible mark some tools put at the start of a file.
    with open(path, encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            # Some phones put invisible left-to-right marks (\u200e) in exports.
            line = line.rstrip("\n").replace("\u200e", "")
            start = LINE_START.match(line)

            if start is None:
                # No timestamp, so this line is the rest of the message above.
                # (If the line above was a system message, current is None,
                # and we skip this line too.)
                if current is not None:
                    current.text += "\n" + line
                continue

            # A new line with a timestamp means the previous message is complete.
            if current is not None:
                yield current
                current = None

            when = parse_when(start, line_number)
            sender = SENDER.match(start["rest"])
            if sender is None:
                continue        # a system line, like "Riya added Arjun"
            current = Message(when, sender["sender"], sender["text"])

    # The very last message has no "next message" to push it out, so it's
    # still waiting here. Forgetting this line loses the last message.
    if current is not None:
        yield current


def latest_year(messages: Iterable[Message]) -> int | None:
    """The most recent year in the chat, or None if there are no messages."""
    # A generator expression in the brackets: max() pulls one year at a time.
    return max((message.when.year for message in messages), default=None)
