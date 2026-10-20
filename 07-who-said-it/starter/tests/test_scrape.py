"""Tests for the scraper: robots.txt, the cache, the pauses, and following "Next →". No internet."""

from itertools import islice

import pytest
import requests

from fakes import SITE, FakeResponse, FakeSite, author_page, quote_page, saved_page
from whosaidit.errors import NotAllowed
from whosaidit.scrape import TIMEOUT, USER_AGENT, Scraper, author_slug, cache_name, scrape_all

EINSTEIN = ("Imagination is everything.", "Albert Einstein", "Albert-Einstein", ["imagination"])
AUSTEN = ("There is no charm equal to tenderness of heart.", "Jane Austen", "Jane-Austen", ["charm"])


def two_page_site(robots=""):
    """A tiny site: two pages of quotes, and both authors' pages."""
    return FakeSite({
        SITE + "/": quote_page([EINSTEIN], next_href="/page/2/"),
        SITE + "/page/2/": quote_page([AUSTEN, EINSTEIN]),
        SITE + "/author/Albert-Einstein": author_page("Albert Einstein"),
        SITE + "/author/Jane-Austen": author_page("Jane Austen", "December 16, 1775", "in Steventon Rectory, Hampshire, The United Kingdom"),
    }, robots=robots)


@pytest.mark.parametrize(
    "url, name",
    [
        (SITE + "/", "index.html"),
        (SITE + "/page/2/", "page-2.html"),
        (SITE + "/author/Albert-Einstein", "author-Albert-Einstein.html"),
        (SITE + "/robots.txt", "robots.txt"),
        (SITE + "/author/J.K.-Rowling", "author-J.K.-Rowling.html"),     # a dot in the name
        (SITE + "/tag/love/?page=2", "tag-love--page-2.html"),           # the query is part of the name...
        (SITE + "/tag/love/page/2/", "tag-love-page-2.html"),            # ...so it can't clash with this
        (SITE + "/..", "...html"),                                       # never the folder above
    ],
)
def test_cache_name(url, name):
    assert cache_name(url) == name


def test_author_slug():
    assert author_slug(SITE + "/author/J-K-Rowling") == "J-K-Rowling"
    assert author_slug(SITE + "/author/J-K-Rowling/") == "J-K-Rowling"


# ---------------------------------------------------------------------------
# Being polite
# ---------------------------------------------------------------------------

def test_robots_txt_is_checked_first(tmp_path):
    site = two_page_site()
    Scraper(tmp_path, site).get(SITE + "/")
    assert site.requests == [SITE + "/robots.txt", SITE + "/"]


def test_a_page_robots_txt_forbids(tmp_path):
    site = two_page_site(robots="User-agent: *\nDisallow: /page/\n")
    scraper = Scraper(tmp_path, site)
    scraper.get(SITE + "/")                         # allowed
    with pytest.raises(NotAllowed):
        scraper.get(SITE + "/page/2/")
    assert SITE + "/page/2/" not in site.requests   # never even asked for


def test_no_robots_txt_means_everything_is_allowed(tmp_path):
    site = two_page_site()
    del site.pages[SITE + "/robots.txt"]            # a 404, like the real site
    assert "Imagination" in Scraper(tmp_path, site).get(SITE + "/")


def test_a_private_robots_txt_means_keep_out(tmp_path):
    class Forbidden(FakeSite):
        def get(self, url, timeout=None):
            return FakeResponse(403, "Forbidden")
    with pytest.raises(NotAllowed):
        Scraper(tmp_path, Forbidden()).get(SITE + "/")


def test_every_request_has_a_user_agent_and_a_timeout(tmp_path):
    site = two_page_site()
    Scraper(tmp_path, site).get(SITE + "/")
    assert site.headers["User-Agent"] == USER_AGENT
    assert site.timeouts == [TIMEOUT, TIMEOUT]


def test_it_pauses_between_requests(tmp_path, sleeps):
    scraper = Scraper(tmp_path, two_page_site(), delay=1.5)
    scraper.get(SITE + "/")
    scraper.get(SITE + "/page/2/")
    # robots.txt, then a pause, the front page, a pause, then page 2.
    assert sleeps == [1.5, 1.5]


def test_robots_txt_can_ask_for_a_longer_pause(tmp_path, sleeps):
    scraper = Scraper(tmp_path, two_page_site(robots="User-agent: *\nCrawl-delay: 5\n"), delay=1)
    scraper.get(SITE + "/")
    assert sleeps == [5.0]


def test_the_second_time_costs_no_requests(tmp_path, sleeps):
    with Scraper(tmp_path, two_page_site()) as scraper:
        first = scraper.get(SITE + "/")
    later = Scraper(tmp_path, FakeSite())           # an empty site: any request would be a 404
    assert later.get(SITE + "/") == first
    assert later.session.requests == []
    assert (later.requests_made, later.from_cache) == (0, 1)


def test_pages_on_other_sites_are_refused(tmp_path):
    site = FakeSite()
    with pytest.raises(NotAllowed, match="isn't on quotes.toscrape.com"):
        Scraper(tmp_path, site).get("https://elsewhere.example/author/X")
    assert site.requests == []          # robots.txt only speaks for its own site


def test_a_cache_file_that_cannot_be_read_is_fetched_again(tmp_path, caplog):
    (tmp_path / "index.html").mkdir()                                  # a folder where the file should be
    (tmp_path / "page-2.html").write_bytes("caf\xe9".encode("cp1252"))  # not UTF-8
    scraper = Scraper(tmp_path, two_page_site())
    assert "Imagination" in scraper.get(SITE + "/")
    assert "charm" in scraper.get(SITE + "/page/2/")
    assert "so fetching it again" in caplog.text


def test_a_cache_that_cannot_be_saved_still_works(tmp_path, caplog):
    blocked = tmp_path / "html_cache"
    blocked.write_text("a file, where the cache folder should be", encoding="utf-8")
    assert "Imagination" in Scraper(blocked, two_page_site()).get(SITE + "/")
    assert "Couldn't save index.html" in caplog.text


def test_with_closes_the_session(tmp_path):
    with Scraper(tmp_path, FakeSite()) as scraper:
        pass
    assert scraper.session.closed


def test_a_missing_charset_is_read_as_utf8(tmp_path):
    class NoCharset(FakeSite):
        def get(self, url, timeout=None):
            self.response = FakeResponse(200, "", content_type="text/html")
            return self.response
    site = NoCharset()
    Scraper(tmp_path, site).download(SITE + "/")
    assert site.response.encoding == "utf-8"


# ---------------------------------------------------------------------------
# download() and allowed() on their own
# ---------------------------------------------------------------------------

def test_download_pauses_between_requests(tmp_path, sleeps):
    site = two_page_site()
    scraper = Scraper(tmp_path, site, delay=2)
    assert "Imagination" in scraper.download(SITE + "/")
    scraper.download(SITE + "/page/2/")
    assert sleeps == [2]                            # no pause before the very first request
    assert site.timeouts == [TIMEOUT, TIMEOUT]
    assert scraper.requests_made == 2


def test_download_a_missing_page(tmp_path):
    scraper = Scraper(tmp_path, FakeSite())
    assert scraper.download(SITE + "/robots.txt", missing_ok=True) == ""
    with pytest.raises(requests.HTTPError):
        scraper.download(SITE + "/page/99/")


def test_allowed_reads_robots_txt_once(tmp_path):
    site = two_page_site(robots="User-agent: *\nDisallow: /page/\n")
    scraper = Scraper(tmp_path, site)
    assert scraper.allowed(SITE + "/")
    assert not scraper.allowed(SITE + "/page/2/")
    assert site.requests == [SITE + "/robots.txt"]  # read once, and remembered


def test_allowed_with_no_robots_txt(tmp_path):
    assert Scraper(tmp_path, FakeSite()).allowed(SITE + "/page/2/")     # a 404 allows everything


def test_allowed_uses_the_crawl_delay(tmp_path):
    scraper = Scraper(tmp_path, two_page_site(robots="User-agent: *\nCrawl-delay: 5\n"), delay=1)
    scraper.allowed(SITE + "/")
    assert scraper.delay == 5


def test_a_missing_page_is_an_error(tmp_path):
    with pytest.raises(requests.HTTPError):
        Scraper(tmp_path, two_page_site()).get(SITE + "/page/99/")


# ---------------------------------------------------------------------------
# Following "Next →"
# ---------------------------------------------------------------------------

def test_quote_pages_follows_next(tmp_path):
    pages = list(Scraper(tmp_path, two_page_site()).quote_pages())
    assert [url for url, _ in pages] == [SITE + "/", SITE + "/page/2/"]


def test_quote_pages_is_lazy(tmp_path):
    site = two_page_site()
    pages = Scraper(tmp_path, site).quote_pages()
    next(pages)
    assert SITE + "/page/2/" not in site.requests       # not fetched until it's asked for


def test_quote_pages_stops_going_round_in_circles(tmp_path, caplog):
    site = FakeSite({SITE + "/": quote_page([EINSTEIN], next_href="/page/2/"),
                     SITE + "/page/2/": quote_page([AUSTEN], next_href="/")}, robots="")
    # islice stops after 10 at most, so a scraper without the check fails here instead of looping for ever.
    assert len(list(islice(Scraper(tmp_path, site).quote_pages(), 10))) == 2
    assert "again, so stopping" in caplog.text


def test_quote_pages_stays_on_the_site(tmp_path, caplog):
    site = FakeSite({SITE + "/": quote_page([EINSTEIN], next_href="https://elsewhere.example/page/2/")}, robots="")
    assert len(list(Scraper(tmp_path, site).quote_pages())) == 1
    assert "another site" in caplog.text
    assert not any("elsewhere" in url for url in site.requests)


# ---------------------------------------------------------------------------
# Everything together
# ---------------------------------------------------------------------------

def test_scrape_all(tmp_path):
    quotes, authors = scrape_all(Scraper(tmp_path, two_page_site()))
    assert [quote.author for quote in quotes] == ["Albert Einstein", "Jane Austen", "Albert Einstein"]
    assert list(authors) == ["Albert-Einstein", "Jane-Austen"]       # each author's page fetched once
    assert authors["Jane-Austen"].birthplace == "Steventon Rectory, Hampshire, The United Kingdom"


def test_scrape_all_skips_what_it_cannot_use(tmp_path, caplog):
    site = FakeSite({SITE + "/": saved_page("broken_page.html"),
                     SITE + "/author/Albert-Einstein": author_page("Albert Einstein"),
                     SITE + "/author/Mark-Twain": "<html><body>Oops</body></html>"}, robots="")
    quotes, authors = scrape_all(Scraper(tmp_path, site))
    # The "“”" quote parses, but has no text left, so Quote refuses it.
    assert [quote.text for quote in quotes] == ["A quote with everything.", "A quote with no tags, split over two lines."]
    assert "has no text" in caplog.text
    assert list(authors) == ["Albert-Einstein"]                     # Jane Austen's page is a 404
    assert "Skipped the author Jane-Austen: 404" in caplog.text


def test_scrape_all_skips_authors_on_other_sites(tmp_path, caplog):
    page = quote_page([EINSTEIN]).replace('href="/author/Albert-Einstein"', 'href="https://elsewhere.example/author/X"')
    site = FakeSite({SITE + "/": page}, robots="")
    quotes, authors = scrape_all(Scraper(tmp_path, site))
    assert len(quotes) == 1 and authors == {}
    assert not any("elsewhere" in url for url in site.requests)
    assert "Skipped the author X" in caplog.text


def test_scrape_all_on_the_real_last_page(tmp_path):
    site = FakeSite({SITE + "/": saved_page("page-10.html")}, robots="")
    quotes, authors = scrape_all(Scraper(tmp_path, site))
    assert len(quotes) == 10 and authors == {}                       # the author pages are all 404s here
