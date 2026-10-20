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

from whosaidit.errors import NotAllowed, ValidationError
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

    The front page ("/") gives "index.html". A query like "?page=2" is part
    of the name too, so different pages never share a file. Anything that
    isn't a letter, a digit or a dot becomes "-", and names that don't
    already end in ".html" or ".txt" get ".html" on the end.
    """
    parts = urlparse(url)
    path = parts.path.strip("/") + (f"--{parts.query}" if parts.query else "")    # "--" so it can't look like a path
    name = "".join(char if char.isalnum() or char == "." else "-" for char in path) or "index"
    return name if name.endswith((".html", ".txt")) else name + ".html"


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
        if self.requests_made > 0:
            time.sleep(self.delay)          # never two requests in a row without a pause
        self.requests_made += 1
        logger.info("GET %s", url)
        response = self.session.get(url, timeout=TIMEOUT)
        if response.status_code in (401, 403) and url.endswith("/robots.txt"):
            # A robots.txt we're not allowed to read means "keep out".
            raise NotAllowed(f"The site won't even show us its robots.txt ({response.status_code}), so we won't scrape it.")
        if missing_ok and response.status_code == 404:
            return ""
        response.raise_for_status()
        # Without a charset in the Content-Type header, requests guesses
        # ISO-8859-1, and curly quotes come out as "â€œ". This site is UTF-8.
        if "charset" not in response.headers.get("Content-Type", "").lower():
            response.encoding = "utf-8"
        return response.text

    def allowed(self, url: str) -> bool:
        """Does the site's robots.txt let us fetch this URL? It's read once, the first time this is asked."""
        if self.robots is None:
            self.robots = self._read_robots()
            # A site can ask for a longer pause in robots.txt, with "Crawl-delay: 5".
            crawl_delay = self.robots.crawl_delay(USER_AGENT)
            if crawl_delay is not None:
                self.delay = max(self.delay, float(crawl_delay))
        return self.robots.can_fetch(USER_AGENT, url)

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
        # robots.txt only speaks for its own site, so a link to anywhere else is refused.
        site = urlparse(BASE_URL).netloc
        if urlparse(url).netloc != site:
            raise NotAllowed(f"{url} isn't on {site}, so we won't fetch it.")
        cached = self._read_cache(url)
        if cached is not None:
            return cached
        if not self.allowed(url):
            raise NotAllowed(f"The site's robots.txt asks programs not to fetch {url}, so we won't.")
        html = self.download(url)
        self._save(url, html)
        return html

    def _read_cache(self, url: str) -> str | None:
        """The saved page, or None if it isn't saved, or can't be read (then it's downloaded again)."""
        path = self.cache_dir / cache_name(url)
        if not path.exists():
            return None
        try:
            html = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            logger.warning("Can't use %s (%s), so fetching it again", path.name, error)
            return None
        self.from_cache += 1
        return html

    def _save(self, url: str, html: str) -> None:
        """Save a page in the cache. If that fails, it's logged: the page just isn't cached."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with atomic_write(self.cache_dir / cache_name(url)) as file:
                file.write(html)
        except OSError as error:
            logger.warning("Couldn't save %s in %s: %s", cache_name(url), self.cache_dir.name, error)

    def quote_pages(self, start: str = BASE_URL) -> Iterator[tuple[str, str]]:
        """Every page of quotes as (url, html), following "Next →" until there isn't one.

        A generator: it fetches the next page only when the loop asks for it.
        It never follows a link to a different site, or to a page it has
        already seen, which would go round in circles forever.
        """
        url: str | None = start
        seen: set[str] = set()
        while url is not None:
            if url in seen:
                logger.warning("The next page is %s again, so stopping", url)
                return
            if urlparse(url).netloc != urlparse(start).netloc:
                logger.warning("Not following %s: it's on another site", url)
                return
            seen.add(url)
            html = self.get(url)
            yield url, html
            url = next_page_url(html, url)


def scrape_all(scraper: Scraper) -> tuple[list[Quote], dict[str, Author]]:
    """Every quote on the site, then every author's page. Bad items are skipped, and logged."""
    quotes: list[Quote] = []
    author_urls: dict[str, str] = {}        # slug -> URL of their page, in the order they appear
    for url, html in scraper.quote_pages():
        for data in parse_quotes(html, url):
            slug = author_slug(data["author_url"])
            try:
                quote = Quote(data["text"], data["author"], slug, tuple(data["tags"]))
            except ValidationError as error:
                logger.warning("Skipped a quote on %s: %s", url, error)
                continue
            quotes.append(quote)
            author_urls.setdefault(slug, data["author_url"])

    authors: dict[str, Author] = {}
    for slug, url in author_urls.items():
        try:
            html = scraper.get(url)
        except (requests.HTTPError, NotAllowed) as error:
            # A missing page, or one robots.txt asks us to leave alone. The
            # quotes are still fine, so carry on without this author's hints.
            logger.warning("Skipped the author %s: %s", slug, error)
            continue
        found = parse_author(html, url)
        if found is None:
            continue        # parse_author has already logged why
        try:
            authors[slug] = Author(slug, found["name"], found["born"], found["birthplace"])
        except ValidationError as error:
            logger.warning("Skipped the author %s: %s", slug, error)
    return quotes, authors
