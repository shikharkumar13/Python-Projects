"""Tests for the stats."""

from datetime import date

from whosaidit.models import Author, Quote
from whosaidit.stats import most_quoted, quotes_per_decade, top_tags

QUOTES = [
    Quote("One.", "Albert Einstein", "Albert-Einstein", ("life", "science")),
    Quote("Two.", "Albert Einstein", "Albert-Einstein", ("life",)),
    Quote("Three.", "Jane Austen", "Jane-Austen", ("love", "life")),
    Quote("Four.", "Mystery Writer", "Mystery-Writer", ("love",)),
]
AUTHORS = {
    "Albert-Einstein": Author("Albert-Einstein", "Albert Einstein", date(1879, 3, 14)),
    "Jane-Austen": Author("Jane-Austen", "Jane Austen", date(1775, 12, 16)),
    "Mystery-Writer": Author("Mystery-Writer", "Mystery Writer"),        # no birth date
}


def test_most_quoted():
    assert most_quoted(QUOTES) == [("Albert Einstein", 2), ("Jane Austen", 1), ("Mystery Writer", 1)]
    assert most_quoted(QUOTES, 1) == [("Albert Einstein", 2)]


def test_top_tags():
    assert top_tags(QUOTES) == [("life", 3), ("love", 2), ("science", 1)]


def test_quotes_per_decade():
    # 1879 is in the 1870s, and 1775 in the 1770s. The mystery writer is left out.
    assert quotes_per_decade(QUOTES, AUTHORS) == {1770: 1, 1870: 2}
    assert list(quotes_per_decade(QUOTES, AUTHORS)) == [1770, 1870]    # oldest first


def test_quotes_per_decade_with_a_missing_author():
    assert quotes_per_decade(QUOTES, {}) == {}
