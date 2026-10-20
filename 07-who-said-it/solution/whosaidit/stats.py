"""Counting things in the scraped quotes, with collections.Counter."""

from __future__ import annotations

from collections import Counter

from whosaidit.models import Author, Quote


def most_quoted(quotes: list[Quote], how_many: int = 5) -> list[tuple[str, int]]:
    """The authors with the most quotes, as (name, count), most first."""
    return Counter(quote.author for quote in quotes).most_common(how_many)


def top_tags(quotes: list[Quote], how_many: int = 10) -> list[tuple[str, int]]:
    """The most used tags, as (tag, count), most first."""
    return Counter(tag for quote in quotes for tag in quote.tags).most_common(how_many)


def quotes_per_decade(quotes: list[Quote], authors: dict[str, Author]) -> dict[int, int]:
    """How many quotes come from authors born in each decade: {1870: 12, 1880: 3, ...}, oldest first.

    Quotes whose author has no birth date are left out.
    """
    decades: Counter[int] = Counter()
    for quote in quotes:
        author = authors.get(quote.author_slug)
        if author is not None and author.born is not None:
            decades[author.born.year // 10 * 10] += 1      # 1879 // 10 * 10 is 1870
    return dict(sorted(decades.items()))
