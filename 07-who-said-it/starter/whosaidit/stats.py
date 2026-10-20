"""Counting things in the scraped quotes, with collections.Counter."""

from __future__ import annotations

from collections import Counter

from whosaidit.models import Author, Quote


def most_quoted(quotes: list[Quote], how_many: int = 5) -> list[tuple[str, int]]:
    """The authors with the most quotes, as (name, count), most first."""
    return Counter(quote.author for quote in quotes).most_common(how_many)


def top_tags(quotes: list[Quote], how_many: int = 10) -> list[tuple[str, int]]:
    """The most used tags, as (tag, count), most first."""
    # TODO 18 (part 1)
    # - Like most_quoted() above, but count every tag of every quote. A
    #   generator expression with two `for`s does it:
    #   (tag for quote in quotes for tag in quote.tags)
    return []   # placeholder: replace this line


def quotes_per_decade(quotes: list[Quote], authors: dict[str, Author]) -> dict[int, int]:
    """How many quotes come from authors born in each decade: {1870: 12, 1880: 3, ...}, oldest first.

    Quotes whose author has no birth date are left out.
    """
    # TODO 18 (part 2)
    # - decades: Counter[int] = Counter()
    # - For each quote, find its author with authors.get(quote.author_slug).
    #   If there's an author with a birth date, add 1 to
    #   decades[author.born.year // 10 * 10]. (1879 // 10 * 10 is 1870.)
    # - Return dict(sorted(decades.items())), so the oldest decade comes first.
    return {}   # placeholder: replace this line
