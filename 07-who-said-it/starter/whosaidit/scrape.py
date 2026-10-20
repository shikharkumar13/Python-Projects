"""Fetching quotes.toscrape.com, politely.

- robots.txt is checked before the first real request.
- Every request sends a User-Agent that says who's asking, and has a timeout.
- There's a pause between requests, so the site is never hammered.
- Every page is saved in html_cache/. The site is scraped once, and after
  that everything works offline, with no requests at all.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests

from whosaidit.errors import NotAllowed, ValidationError, WhoSaidItError
from whosaidit.models import Author, Quote
from whosaidit.parse import next_page_url, parse_author, parse_quotes
from whosaidit.storage import CACHE_DIR, atomic_write

BASE_URL = "https://quotes.toscrape.com/"
USER_AGENT = "whosaidit/1.0 (a Python course practice project)"
TIMEOUT = 10        # seconds to wait for an answer before giving up
DELAY = 1.0         # seconds to wait between requests

logger = logging.getLogger(__name__)


def cache_name(url: str) -> str:
    """The file name a page is saved under: ".../page/2/" gives "page-2.html".

    The front page ("/") gives "index.html". Anything that isn't a letter,
    a digit or a dot becomes "-". A name with no dot in it gets ".html".
    """
    path = urlparse(url).path.strip("/")
    name = "".join(char if char.isalnum() or char == "." else "-" for char in path) or "index"
    return name if "." in name else name + ".html"


def author_slug(url: str) -> str:
    """ ".../author/Albert-Einstein" gives "Albert-Einstein"."""
    return urlparse(url).path.rstrip("/").split("/")[-1]


class Scraper:
    """Fetches pages politely, and remembers them. Use it in a `with` block:

        with Scraper() as scraper:
            html = scraper.get("https://quotes.toscrape.com/")

    Tests pass in their own cache folder, and a fake session that never
    touches the internet.
    """

    def __init__(self, cache_dir: Path = CACHE_DIR, session: requests.Session | None = None, delay: float = DELAY) -> None:
        self.cache_dir = cache_dir
        self.session = session if session is not None else requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.delay = delay
        self.robots: RobotFileParser | None = None      # read the first time we need it
        self.requests_made = 0
        self.from_cache = 0

    def __enter__(self) -> Scraper:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.session.close()

    def download(self, url: str, missing_ok: bool = False) -> str:
        """One polite request. With missing_ok, a 404 gives "" instead of an error."""
        # TODO 9: one polite request.
        # - If self.requests_made is more than 0, time.sleep(self.delay) first.
        # - Add 1 to self.requests_made, and log the URL with logger.info.
        # - response = self.session.get(url, timeout=TIMEOUT)
        # - If the status is 401 or 403 and the URL ends with "/robots.txt", raise
        #   NotAllowed: a robots.txt we can't read means "keep out".
        # - If missing_ok and the status is 404, return "".
        # - response.raise_for_status()
        # - If "charset" isn't in response.headers.get("Content-Type", "").lower(),
        #   set response.encoding = "utf-8".
        # - Return response.text.
        raise WhoSaidItError("Downloading a page is TODO 9.")   # placeholder: replace this line

    def allowed(self, url: str) -> bool:
        """Does the site's robots.txt let us fetch this URL? It's read once, the first time this is asked."""
        # TODO 10
        # - If self.robots is None, it hasn't been read yet: self.robots = self._read_robots().
        #   Then, if self.robots.crawl_delay(USER_AGENT) isn't None, make self.delay
        #   the bigger of the two (turn the crawl delay into a float first).
        # - Return self.robots.can_fetch(USER_AGENT, url).
        raise WhoSaidItError("Checking robots.txt is TODO 10.")   # placeholder: replace this line

    def _read_robots(self) -> RobotFileParser:
        """Fetch and read robots.txt. A site without one (a 404) allows everything."""
        url = urljoin(BASE_URL, "/robots.txt")
        text = self._read_cache(url)
        if text is None:
            text = self.download(url, missing_ok=True)
            self._save(url, text)
        robots = RobotFileParser(url)
        robots.parse(text.splitlines())     # parse([]), for an empty file, allows everything
        return robots

    def get(self, url: str) -> str:
        """A page's HTML: from the cache if it's there, otherwise downloaded (if robots.txt allows it) and saved."""
        # TODO 11
        # - cached = self._read_cache(url). If it isn't None, return it. (No request,
        #   so no need to check robots.txt, or to pause.)
        # - If not self.allowed(url), raise NotAllowed with a message naming the URL.
        # - html = self.download(url), then self._save(url, html), and return html.
        raise WhoSaidItError("Getting a page is TODO 11.")   # placeholder: replace this line

    def _read_cache(self, url: str) -> str | None:
        path = self.cache_dir / cache_name(url)
        if not path.exists():
            return None
        self.from_cache += 1
        return path.read_text(encoding="utf-8")

    def _save(self, url: str, html: str) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with atomic_write(self.cache_dir / cache_name(url)) as file:
            file.write(html)

    def quote_pages(self, start: str = BASE_URL) -> Iterator[tuple[str, str]]:
        """Every page of quotes as (url, html), following "Next →" until there isn't one.

        A generator: it fetches the next page only when the loop asks for it.
        It never follows a link to a different site, or to a page it has
        already seen, which would go round in circles forever.
        """
        # TODO 12: a generator that follows "Next →".
        # - url (type hint: str | None) starts as `start`, and seen starts as an empty set.
        # - while url is not None:
        #   - if url is in seen, log a warning and return. (In a generator, return
        #     just means "no more".)
        #   - if urlparse(url).netloc isn't the same as urlparse(start).netloc, it's
        #     another site: log a warning and return.
        #   - add url to seen, html = self.get(url), and yield (url, html).
        #   - url = next_page_url(html, url)
        yield from ()   # placeholder: a generator that gives nothing


def scrape_all(scraper: Scraper) -> tuple[list[Quote], dict[str, Author]]:
    """Every quote on the site, then every author's page. Bad items are skipped, and logged."""
    # TODO 13
    # - quotes = [], and author_urls = {}: slug -> the URL of their page.
    # - For each (url, html) in scraper.quote_pages(), and each `data` in
    #   parse_quotes(html, url):
    #   - slug = author_slug(data["author_url"])
    #   - Make a Quote(data["text"], data["author"], slug, tuple(data["tags"])),
    #     in a try. On ValidationError, log a warning and `continue`.
    #   - Append it, and author_urls.setdefault(slug, data["author_url"]).
    #     (setdefault only stores it the first time, so each page is fetched once.)
    # - Then authors = {}. For each slug and url in author_urls.items():
    #   - html = scraper.get(url), in a try. On requests.HTTPError, log and continue.
    #   - found = parse_author(html, url). If it's None, continue.
    #   - authors[slug] = Author(slug, found["name"], found["born"], found["birthplace"]),
    #     in a try. On ValidationError, log and continue.
    # - Return quotes, authors.
    return [], {}   # placeholder: replace this line
