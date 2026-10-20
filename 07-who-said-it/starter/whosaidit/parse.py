"""Turning the site's HTML into plain dictionaries.

Nothing here touches the internet. Each function gets some HTML (from the
cache, or from a test) and gives back what it found. Every field goes
through text_of() or attr_of(), so a missing piece gives None instead of a
crash, and the item is skipped and logged.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# The site wraps every quote in curly quotes: “Like this.” This pattern
# matches quote marks at the very start (^) or the very end ($) of the
# text, curly or straight, so they can be removed. Quote marks in the
# middle are left alone.
# TODO 2 (part 1): a pattern for quote marks at the START or the END of the text.
# - ^ means "the start", and $ means "the end".
# - [“"]+ means "one or more curly opening quotes or straight quotes". At the
#   end, it's the closing curly quote instead: [”"]+
# - Put the two halves together with | ("or"):  start marks | end marks
# - Use a raw string with single quotes outside, because the pattern has a " in it:
#   re.compile(r'...')
QUOTE_MARKS = re.compile(r"(?!)")   # placeholder: this pattern never matches anything
SPACES = re.compile(r"\s+")         # any run of spaces, tabs or newlines


def text_of(element: Tag, selector: str) -> str | None:
    """The text inside the first match for a CSS selector, stripped. None if there's no match, or it's empty."""
    # TODO 1: the safe helper every field goes through.
    # - found = element.select_one(selector). It gives the first match, or None.
    # - If found is None, return None.
    # - Otherwise take found.get_text().strip(). If that's empty, return None
    #   too (`return text or None` does both).
    # attr_of(), just below, is a finished example of the same idea.
    return None   # placeholder: replace this line


def attr_of(element: Tag, selector: str, attribute: str) -> str | None:
    """An attribute (like href) of the first match for a CSS selector. None if there's no match, or no attribute."""
    found = element.select_one(selector)
    if found is None:
        return None
    value = found.get(attribute)
    if not isinstance(value, str) or not value.strip():     # missing, or a list (like class="a b")
        return None
    return value.strip()


def clean_quote(text: str) -> str:
    """Take the quote marks off the ends, and squash runs of spaces and newlines into one space."""
    # TODO 2 (part 2)
    # - Strip the text, then QUOTE_MARKS.sub("", text) removes the marks at the ends.
    # - SPACES.sub(" ", text) squashes each run of spaces and newlines into one space.
    # - Strip it once more, and return it.
    return text   # placeholder: replace this line


def parse_quotes(html: str, page_url: str) -> Iterator[dict[str, Any]]:
    """Every quote on a page, as a dictionary. A quote with a missing piece is skipped, and logged."""
    # TODO 3: a generator.
    # - soup = BeautifulSoup(html, "html.parser")
    # - Loop over soup.select("div.quote"), with enumerate(..., start=1) so you
    #   know each quote's number.
    # - For each box, use text_of() for "span.text" and "small.author", and
    #   attr_of() for the link: selector "a[href*='/author/']", attribute "href".
    # - If any of the three is None, log a warning that says which page, which
    #   quote number, and what's missing, then `continue`.
    # - Otherwise yield a dictionary with:
    #     "text": clean_quote(text), "author": author,
    #     "author_url": urljoin(page_url, link), and
    #     "tags": the stripped text of each element in box.select("a.tag")
    #             (leave out any that are empty).
    yield from ()   # placeholder: a generator that gives nothing


def next_page_url(html: str, page_url: str) -> str | None:
    """The full URL of the "Next →" link, or None on the last page."""
    soup = BeautifulSoup(html, "html.parser")
    link = attr_of(soup, "li.next > a", "href")
    if link is None:
        return None
    return urljoin(page_url, link)


def parse_born_date(text: str) -> date | None:
    """ "March 14, 1879" becomes date(1879, 3, 14). Anything else gives None, and is logged."""
    # TODO 4
    # - datetime.strptime(text.strip(), "%B %d, %Y") reads "March 14, 1879".
    #   %B is a month's full name, %d the day, and %Y a four-digit year.
    # - .date() turns the datetime into a date.
    # - strptime raises ValueError for anything else: catch it, log a warning
    #   with the text, and return None.
    return None   # placeholder: replace this line


def parse_author(html: str, page_url: str) -> dict[str, Any] | None:
    """An author's name, birth date and birthplace, from their page. None if the page has no name."""
    # TODO 5
    # - soup = BeautifulSoup(html, "html.parser")
    # - name = text_of(soup, "h3.author-title"). If it's None, log a warning and
    #   return None.
    # - born = text_of(soup, "span.author-born-date"), and
    #   place = text_of(soup, "span.author-born-location").
    # - Return a dictionary:
    #     "name": the name, with SPACES.sub(" ", ...) to tidy it,
    #     "born": parse_born_date(born), or None if born is None,
    #     "birthplace": place without the "in " at the start (place.removeprefix("in ")),
    #                   stripped, or None if place is None.
    return None   # placeholder: replace this line
