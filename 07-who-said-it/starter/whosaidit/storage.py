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
    # TODO 7: a context manager made with @contextmanager.
    # - temp = path.with_name(path.name + ".tmp")
    # - In a try:
    #   - open temp for writing (with encoding="utf-8") in a `with`, and
    #     `yield file` inside it. Whatever the caller writes goes into temp.
    #   - after the with: os.replace(temp, path) swaps the files in one step.
    # - In the finally: if temp still exists, something went wrong, so delete it
    #   with temp.unlink().
    with open(path, "w", encoding="utf-8") as file:   # placeholder: not atomic yet
        yield file


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
    # TODO 8
    # - In a try: open the file with encoding="utf-8-sig" and json.load() it.
    #   Then make the quotes with Quote.from_dict() for each item in data["quotes"],
    #   the authors with Author.from_dict() for each item in data["authors"], and
    #   scraped_at with datetime.fromisoformat(data["scraped_at"]).
    # - except FileNotFoundError: raise StorageError saying to run scrape first.
    # - except (ValueError, KeyError, TypeError, ValidationError): the file is
    #   damaged. Log it with logger.exception(...), and raise StorageError
    #   saying so. Add `from error` to keep the original error attached.
    # - except OSError: raise StorageError with error.strerror.
    # - After the try: if there are no quotes at all, raise StorageError too.
    # - Return QuoteBook(quotes, {author.slug: author for author in authors}, scraped_at).
    # save(), above, writes the file this reads.
    raise StorageError("Loading quotes.json is TODO 8.")   # placeholder: replace this line
