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
# TODO 1: the pattern for the start of every message line.
# It should match lines like  12/03/2025, 21:45 - Riya: see you tomorrow!
# and also  1/3/25, 9:05 - ...  (one-digit days, months and hours, two-digit years).
# Use re.compile(r"""...""", re.VERBOSE) and these named groups:
#   (?P<day>...)  (?P<month>...)  (?P<year>...)  (?P<hour>...)  (?P<minute>...)
#   (?P<rest>.*)  for everything after the " - "
# Hints:
# - \d{1,2} is one or two digits. \d{4}|\d{2} is four digits, or two.
# - In VERBOSE mode, spaces in the pattern are ignored, so write a real
#   space as \s, and use # comments to explain each part.
# - Start with ^ and end with $, so it only matches whole lines.
# The EMOJI pattern in stats.py is a finished example of a VERBOSE pattern.
LINE_START = re.compile(r"(?!)")   # placeholder: this pattern never matches anything

# What comes after the dash, for a real message: "Riya: see you tomorrow!".
# [^:"]+? means "as few characters as possible that aren't a colon or a
# quote", so the name stops at the FIRST colon, and a message like
# "time: 9pm" keeps its own colon. Why no quotes? System lines put group
# names in quotes, and a group name can have a colon in it:
#   Riya changed the subject from "Trip: Goa" to "Goa"
# Real people's names don't have quotes in them, so that line can't match.
# TODO 2: the pattern that splits "Riya: see you tomorrow!" into a sender and a text.
# - Named groups: (?P<sender>...) and (?P<text>...)
# - The name is everything up to the FIRST colon, and can't contain a quote
#   (the comment above explains both). [^:"]+? does that.
# - A system line like "Riya added Arjun" has no ": " at all, so it
#   shouldn't match.
SENDER = re.compile(r"(?!)")   # placeholder: this pattern never matches anything


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
    # TODO 3
    # - Read the parts with match["day"], match["month"] and so on, and turn
    #   them into numbers with int().
    # - If DAY_FIRST is False, swap the day and the month.
    # - A two-digit year like 25 means 2025: add 2000 if it's under 100.
    # - Build the datetime inside a try. datetime() raises ValueError for an
    #   impossible date like 32/01/2025. Catch it and raise ChatFormatError,
    #   saying which line it was and mentioning DAY_FIRST.
    return datetime(2000, 1, 1)   # placeholder: replace this line


def read_messages(path: Path) -> Iterator[Message]:
    """Yield the messages in a chat export, one at a time.

    This is a generator, so it never holds the whole chat in memory. It reads
    one line, and hands over a message as soon as it knows the message is
    complete, which is when the NEXT message starts.
    """
    # TODO 5  (write the two tests in TODO 4 first!)
    # - Keep the message you're building in a variable, `current`, starting as None.
    # - Open the file with encoding="utf-8-sig", and loop with
    #   enumerate(file, start=1), so you know each line's number.
    # - For each line: strip the "\n" from the end, and remove any "\u200e" marks.
    # - If LINE_START doesn't match, the line belongs to the message above:
    #   add "\n" + line to current.text, if current isn't None. Then `continue`.
    # - If it does match, the message in `current` is complete: yield it, and
    #   set current back to None.
    # - Work out the time with parse_when(). Then try SENDER on start["rest"].
    #   No match means a system line, so skip it. Otherwise, make a new Message
    #   and keep it in `current`.
    # - AFTER the loop: if current isn't None, yield it. (Why? Your test from
    #   TODO 4 will tell you.)
    yield from ()   # placeholder: a generator that gives nothing


def latest_year(messages: Iterable[Message]) -> int | None:
    """The most recent year in the chat, or None if there are no messages."""
    # TODO 6
    # - One line: max() over a generator expression of each message's year.
    # - Give max() default=None, so an empty chat gives None instead of an error.
    return None   # placeholder: replace this line
