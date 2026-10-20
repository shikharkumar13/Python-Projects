"""The three commands: scrape, play and stats."""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from pathlib import Path

import requests

from whosaidit import game
from whosaidit.errors import UsageError, WhoSaidItError
from whosaidit.scrape import Scraper, scrape_all
from whosaidit.stats import most_quoted, quotes_per_decade, top_tags
from whosaidit.storage import CACHE_DIR, DATA_FILE, QuoteBook, load, save

logger = logging.getLogger(__name__)

USAGE = """Usage: python -m whosaidit <command>

  scrape        get every quote and author from quotes.toscrape.com
  play          the game: who said it? (add a number, like play 7, to replay the same order)
  stats         the most quoted authors, the most used tags, and quotes by decade

Pages are saved in html_cache/, so the site is only ever scraped once."""


def bar(count: int, biggest: int, width: int = 30) -> str:
    """A bar of # characters, scaled so the biggest count is `width` long."""
    return "#" * max(1, round(count / biggest * width))


def scrape_command(data_file: Path, cache_dir: Path, session: requests.Session | None) -> None:
    with Scraper(cache_dir, session) as scraper:
        quotes, authors = scrape_all(scraper)
    if not quotes:
        raise WhoSaidItError("No quotes found. Has the site changed? Look in whosaidit.log for why.")
    save(data_file, QuoteBook(quotes, authors, datetime.now(timezone.utc)))
    print(f"Saved {len(quotes)} quotes by {len(authors)} authors to {data_file.name}.")
    print(f"Requests to the site: {scraper.requests_made}. Pages from html_cache/: {scraper.from_cache}.")
    missing = len({quote.author_slug for quote in quotes} - set(authors))
    if missing:
        print(f"{missing} authors' pages couldn't be read, so their hints will be vaguer. See whosaidit.log.")
    print("Now play with: python -m whosaidit play")


def play_command(data_file: Path, args: list[str], ask: game.Ask) -> None:
    if len(args) > 1:
        raise UsageError("Just one number after play, like: python -m whosaidit play 7")
    if args and not args[0].isdecimal():
        raise UsageError(f"The number after play should be a whole number, like 7, not {args[0]!r}.")
    book = load(data_file)
    rng = random.Random(int(args[0])) if args else random.Random()
    print(f"Who said it? {len(book.quotes)} quotes. You get {game.GUESSES} guesses for each one,")
    print("and a hint after every wrong guess. Type quit to stop.")
    game.play(book, rng, ask)


def stats_command(data_file: Path) -> None:
    book = load(data_file)
    scraped = book.scraped_at.astimezone()      # in your own time zone
    print(f"{len(book.quotes)} quotes by {len(book.authors)} authors, scraped on "
          f"{scraped.day} {scraped:%B %Y at %H:%M}.")

    print()
    print("Most quoted authors")
    authors = most_quoted(book.quotes)
    for name, count in authors:
        print(f"  {name:<22}{count:>4}  {bar(count, authors[0][1])}")

    print()
    print("Most used tags")
    tags = top_tags(book.quotes)
    for tag, count in tags:
        print(f"  {tag:<22}{count:>4}  {bar(count, tags[0][1])}")

    print()
    print("Quotes by the decade the author was born")
    decades = quotes_per_decade(book.quotes, book.authors)
    biggest = max(decades.values(), default=1)
    for decade, count in decades.items():
        print(f"  {decade}s{count:>21}  {bar(count, biggest)}")
    unknown = len(book.quotes) - sum(decades.values())
    if not decades:
        print("  (No birth dates to count.)")
    elif unknown:
        print(f"  (and {unknown} quotes by authors with no birth date)")


def main(
    argv: list[str],
    data_file: Path = DATA_FILE,
    cache_dir: Path = CACHE_DIR,
    session: requests.Session | None = None,
    ask: game.Ask = input,
) -> int:
    """Run one command. Returns the exit code: 0 for OK, 1 for a problem, 2 for a typo.

    Tests pass in a temporary data file and cache, a fake session that never
    touches the internet, and an `ask` that types the player's answers.
    """
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    command, args = argv[0], argv[1:]
    try:
        if command == "scrape" and not args:
            scrape_command(data_file, cache_dir, session)
        elif command == "play":
            play_command(data_file, args, ask)
        elif command == "stats" and not args:
            stats_command(data_file)
        elif command in ("scrape", "stats"):
            raise UsageError(f"{command} doesn't take anything after it. Try: python -m whosaidit {command}")
        else:
            print(f"There's no command called {command!r}.")
            print()
            print(USAGE)
            return 2
    except UsageError as error:
        print(error)
        return 2
    except WhoSaidItError as error:
        print(error)
        return 1
    except requests.ConnectionError:
        print("Couldn't connect to quotes.toscrape.com. Are you online? Pages already in html_cache/ "
              "don't need the internet, and running scrape again carries on where it stopped.")
        return 1
    except requests.RequestException as error:
        logger.exception("Request failed")
        print(f"Something went wrong talking to the site: {error}")
        return 1
    return 0
