"""Reading the command line, and putting the pieces together."""

from __future__ import annotations

from pathlib import Path

from wrapped.parser import ChatFormatError, latest_year, read_messages
from wrapped.report import build_report
from wrapped.stats import analyse

FEW_MESSAGES = 100     # fewer than this in the latest year, and we suggest the year before

USAGE = """Usage: python -m wrapped <chat file> [year]

  python -m wrapped sample_chat.txt          the latest year in the chat
  python -m wrapped sample_chat.txt 2024     a year of your choice

The report is printed, and saved next to the chat as a .md file."""


def chat_title(path: Path) -> str:
    """A title from the file name. WhatsApp names its exports like
    "WhatsApp Chat with Goa Gang.txt", so that becomes "Goa Gang"."""
    name = path.stem
    prefix = "WhatsApp Chat with "
    if name.startswith(prefix):
        return name[len(prefix):]
    # .strip() because iPhones call the file "_chat.txt", which would
    # otherwise give " Chat", with a space in front.
    return name.replace("_", " ").strip().title()


def main(argv: list[str]) -> int:
    """Make the report. Returns the exit code: 0 for OK, 1 for a problem, 2 for a typo."""
    if len(argv) == 0 or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0

    if len(argv) > 2:
        print(f"That's too many words after python -m wrapped: {' '.join(argv)}")
        print()
        print(USAGE)
        return 2

    path = Path(argv[0])
    if path.suffix.lower() == ".zip":
        # WhatsApp often shares an export as a .zip file.
        print(f"{path.name} is a .zip file. Unzip it first, then use the .txt file inside it.")
        return 1
    year = None
    chose_year = False          # did we pick the year ourselves?
    if len(argv) > 1:
        if not argv[1].isdigit():
            print(f"The year should be a number, like 2025, not {argv[1]!r}.")
            return 2
        year = int(argv[1])

    try:
        if year is None:
            # A first, quick pass through the file just to find the latest year.
            # A generator can't be rewound, but we can simply make a new one.
            year = latest_year(read_messages(path))
            if year is None:
                print(f"I couldn't find any messages in {path.name}.")
                print("This reads Android exports with a 24-hour clock, where every message starts like:")
                print("  12/03/2025, 21:45 - Riya: see you tomorrow!")
                return 1
            chose_year = True

        # The second pass. The generator expression keeps one year's messages,
        # still one at a time, and analyse() counts them as they arrive.
        stats = analyse(message for message in read_messages(path) if message.when.year == year)
    except FileNotFoundError:
        print(f"I can't find {path}. Check the name, and which folder you're in.")
        return 1
    except OSError as error:
        # For example, the name of a folder instead of a file.
        print(f"I couldn't open {path}. ({error})")
        return 1
    except UnicodeDecodeError:
        print(f"{path.name} isn't saved as UTF-8 text, so I can't read it. Is it really a chat export?")
        return 1
    except ChatFormatError as error:
        print(error)
        return 1

    if stats.total == 0:
        print(f"There are no messages from {year} in {path.name}.")
        return 1

    report = build_report(stats, chat_title(path), year)
    print(report)
    output = path.with_name(f"{path.stem}_wrapped_{year}.md")
    try:
        output.write_text(report, encoding="utf-8")
    except OSError as error:
        # The report is already on the screen, so nothing is lost.
        print(f"I couldn't save the report as {output.name}. ({error})")
        return 1
    print(f"Saved the report as {output.name}")
    if chose_year and stats.total < FEW_MESSAGES:
        # A chat exported in early January has only a few days of the new year.
        print(f"Only {stats.total} messages in {year}. For last year, try: python -m wrapped {argv[0]} {year - 1}")
    return 0
