"""Saving the scraped quotes to quotes.json, and loading them again."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO

from whosaidit.errors import StorageError, ValidationError
from whosaidit.models import Author, Quote

logger = logging.getLogger(__name__)

# The folder that holds the whosaidit package. The data, the HTML cache
# and the log all go here, so starter/ and solution/ each keep their own.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "quotes.json"
CACHE_DIR = PROJECT_DIR / "html_cache"
LOG_FILE = PROJECT_DIR / "whosaidit.log"


@dataclass
class QuoteBook:
    """Everything the game needs: the quotes, their authors, and when they were scraped."""

    quotes: list[Quote]
    authors: dict[str, Author]      # slug -> Author
    scraped_at: datetime

    def author_of(self, quote: Quote) -> Author | None:
        """The quote's Author, or None if their page couldn't be scraped."""
        return self.authors.get(quote.author_slug)


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
        os.replace(temp, path)      # swaps the files in one step
    finally:
        # After a successful replace, the temp file is gone. If it's still
        # here, something went wrong, so tidy it up.
        if temp.exists():
            temp.unlink()


def save(path: Path, book: QuoteBook) -> None:
    """Write the whole book to a JSON file, atomically."""
    data = {
        "scraped_at": book.scraped_at.isoformat(),
        "quotes": [quote.to_dict() for quote in book.quotes],
        "authors": [author.to_dict() for author in book.authors.values()],
    }
    try:
        with atomic_write(path) as file:
            json.dump(data, file, indent=2, ensure_ascii=False)     # ensure_ascii=False keeps "André" readable
    except OSError as error:
        raise StorageError(f"Couldn't save {path.name}: {error.strerror}.") from error
    logger.info("Saved %d quotes to %s", len(book.quotes), path)


def load(path: Path) -> QuoteBook:
    """Read the book back from a JSON file. Raises StorageError if it's missing or damaged."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            data = json.load(file)
        quotes = [Quote.from_dict(item) for item in data["quotes"]]
        authors = [Author.from_dict(item) for item in data["authors"]]
        scraped_at = datetime.fromisoformat(data["scraped_at"])
    except FileNotFoundError:
        raise StorageError("There are no quotes yet. Get them first with: python -m whosaidit scrape")
    except (ValueError, KeyError, TypeError, ValidationError) as error:
        # ValueError covers bad JSON, bad dates, and UnicodeDecodeError.
        logger.exception("Couldn't read %s", path)
        raise StorageError(f"{path.name} is damaged. Make it again with: python -m whosaidit scrape") from error
    except OSError as error:
        raise StorageError(f"Couldn't read {path.name}: {error.strerror}.") from error
    if not quotes:
        raise StorageError(f"{path.name} has no quotes in it. Make it again with: python -m whosaidit scrape")
    return QuoteBook(quotes, {author.slug: author for author in authors}, scraped_at)
