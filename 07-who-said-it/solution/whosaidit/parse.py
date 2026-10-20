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
QUOTE_MARKS = re.compile(r'^[“"]+|[”"]+$')
SPACES = re.compile(r"\s+")         # any run of spaces, tabs or newlines


def text_of(element: Tag, selector: str) -> str | None:
    """The text inside the first match for a CSS selector, stripped. None if there's no match, or it's empty."""
    found = element.select_one(selector)
    if found is None:
        return None
    text = found.get_text().strip()
    return text or None


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
    text = QUOTE_MARKS.sub("", text.strip())
    return SPACES.sub(" ", text).strip()


def parse_quotes(html: str, page_url: str) -> Iterator[dict[str, Any]]:
    """Every quote on a page, as a dictionary. A quote with a missing piece is skipped, and logged."""
    soup = BeautifulSoup(html, "html.parser")
    for number, box in enumerate(soup.select("div.quote"), start=1):
        text = text_of(box, "span.text")
        author = text_of(box, "small.author")
        link = attr_of(box, "a[href*='/author/']", "href")
        if text is None or author is None or link is None:
            missing = [name for name, value in [("text", text), ("author", author), ("author link", link)] if value is None]
            logger.warning("Skipped quote %d on %s: it has no %s", number, page_url, " or ".join(missing))
            continue
        yield {
            "text": clean_quote(text),
            "author": author,
            "author_url": urljoin(page_url, link),      # "/author/Albert-Einstein" becomes a full URL
            "tags": [tag.get_text().strip() for tag in box.select("a.tag") if tag.get_text().strip()],
        }


def next_page_url(html: str, page_url: str) -> str | None:
    """The full URL of the "Next →" link, or None on the last page."""
    soup = BeautifulSoup(html, "html.parser")
    link = attr_of(soup, "li.next > a", "href")
    if link is None:
        return None
    return urljoin(page_url, link)


def parse_born_date(text: str) -> date | None:
    """ "March 14, 1879" becomes date(1879, 3, 14). Anything else gives None, and is logged."""
    try:
        return datetime.strptime(text.strip(), "%B %d, %Y").date()
    except ValueError:
        logger.warning("Couldn't read the birth date %r", text)
        return None


def parse_author(html: str, page_url: str) -> dict[str, Any] | None:
    """An author's name, birth date and birthplace, from their page. None if the page has no name."""
    soup = BeautifulSoup(html, "html.parser")
    name = text_of(soup, "h3.author-title")
    if name is None:
        logger.warning("Skipped the author page %s: it has no name", page_url)
        return None
    born = text_of(soup, "span.author-born-date")
    place = text_of(soup, "span.author-born-location")
    return {
        "name": SPACES.sub(" ", name),
        "born": parse_born_date(born) if born else None,
        "birthplace": place.removeprefix("in ").strip() if place else None,    # "in Ulm, Germany"
    }
