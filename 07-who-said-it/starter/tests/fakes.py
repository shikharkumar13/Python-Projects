"""A pretend website, so the tests never touch the internet."""

from pathlib import Path

import requests

# Real pages from quotes.toscrape.com, saved for the tests to read, and two
# made-up broken ones (broken_page.html and broken_author.html).
FIXTURES = Path(__file__).parent / "fixtures"

SITE = "https://quotes.toscrape.com"


def saved_page(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeResponse:
    """Pretends to be a requests.Response."""

    def __init__(self, status_code=200, text="", content_type="text/html; charset=utf-8"):
        self.status_code = status_code
        self.text = text
        self.headers = {"Content-Type": content_type}
        self.encoding = None

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)


class FakeSite:
    """Pretends to be a requests.Session talking to a website.

    `pages` maps each URL to its HTML. Any other URL is a 404. Every request
    is remembered in .requests, so a test can check what was asked for.
    """

    def __init__(self, pages=None, robots=None):
        self.pages = dict(pages or {})
        if robots is not None:
            self.pages[SITE + "/robots.txt"] = robots
        self.requests = []
        self.timeouts = []
        self.headers = {}
        self.closed = False

    def get(self, url, timeout=None):
        self.requests.append(url)
        self.timeouts.append(timeout)
        if url in self.pages:
            return FakeResponse(200, self.pages[url])
        return FakeResponse(404, "Not found")

    def close(self):
        self.closed = True


def quote_page(quotes, next_href=None):
    """Make a page of quotes that looks like the real site's. `quotes` is a list of (text, author, slug, tags)."""
    boxes = []
    for text, author, slug, tags in quotes:
        tag_links = "".join(f'<a class="tag" href="/tag/{tag}/page/1/">{tag}</a>' for tag in tags)
        boxes.append(
            f'<div class="quote"><span class="text">“{text}”</span>'
            f'<span>by <small class="author">{author}</small> <a href="/author/{slug}">(about)</a></span>'
            f'<div class="tags">Tags: {tag_links}</div></div>'
        )
    pager = f'<li class="next"><a href="{next_href}">Next <span>→</span></a></li>' if next_href else ""
    return f"<html><body>{''.join(boxes)}<nav><ul class='pager'>{pager}</ul></nav></body></html>"


def author_page(name, born="March 14, 1879", place="in Ulm, Germany"):
    """Make an author's page that looks like the real site's."""
    return (
        f'<html><body><div class="author-details"><h3 class="author-title">{name}</h3>'
        f'<p><strong>Born:</strong> <span class="author-born-date">{born}</span> '
        f'<span class="author-born-location">{place}</span></p></div></body></html>'
    )
