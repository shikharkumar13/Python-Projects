"""Tests for turning HTML into dictionaries, using real pages saved from the site."""

from datetime import date

import pytest
from bs4 import BeautifulSoup

from fakes import SITE, saved_page
from whosaidit.parse import attr_of, clean_quote, next_page_url, parse_author, parse_born_date, parse_quotes, text_of

BOX = BeautifulSoup('<div><p class="a">  hello  </p><p class="empty">   </p><a href="/x">link</a><a>no href</a></div>',
                    "html.parser")


def test_text_of():
    assert text_of(BOX, "p.a") == "hello"


@pytest.mark.parametrize("selector", ["p.missing", "p.empty"])
def test_text_of_gives_none_when_there_is_nothing(selector):
    assert text_of(BOX, selector) is None


def test_attr_of():
    assert attr_of(BOX, "a", "href") == "/x"
    assert attr_of(BOX, "a.missing", "href") is None
    assert attr_of(BOX, "a:not([href])", "href") is None


@pytest.mark.parametrize(
    "raw, clean",
    [
        ("“Simple.”", "Simple."),
        ('"Straight quotes."', "Straight quotes."),
        ("  “Spaces  and\n  newlines.”  ", "Spaces and newlines."),
        ("“She said “hi” to me.”", "She said “hi” to me."),     # quote marks in the middle stay
        ("No marks at all", "No marks at all"),
        ("“”", ""),
    ],
)
def test_clean_quote(raw, clean):
    assert clean_quote(raw) == clean


def test_parse_quotes_on_a_real_page():
    quotes = list(parse_quotes(saved_page("index.html"), SITE + "/"))
    assert len(quotes) == 10
    assert quotes[0] == {
        "text": "The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.",
        "author": "Albert Einstein",
        "author_url": SITE + "/author/Albert-Einstein",
        "tags": ["change", "deep-thoughts", "thinking", "world"],
    }


def test_parse_quotes_skips_and_logs_broken_quotes(caplog):
    quotes = list(parse_quotes(saved_page("broken_page.html"), SITE + "/page/3/"))
    # The quotes with no author, no text, or no author link are skipped.
    assert [quote["text"] for quote in quotes] == ["A quote with everything.", "A quote with no tags, split over two lines.", ""]
    assert quotes[0]["tags"] == ["life"]          # the empty tag is left out
    assert quotes[1]["tags"] == []
    assert "Skipped quote 2 on https://quotes.toscrape.com/page/3/: it has no author" in caplog.text
    assert "Skipped quote 3" in caplog.text and "no text" in caplog.text
    assert "Skipped quote 6" in caplog.text and "no author link" in caplog.text


def test_parse_quotes_is_a_generator():
    found = parse_quotes(saved_page("index.html"), SITE + "/")
    assert next(found)["author"] == "Albert Einstein"


def test_next_page_url():
    assert next_page_url(saved_page("index.html"), SITE + "/") == SITE + "/page/2/"


def test_the_last_page_has_no_next():
    assert next_page_url(saved_page("page-10.html"), SITE + "/page/10/") is None


def test_parse_author_on_a_real_page():
    assert parse_author(saved_page("author-Albert-Einstein.html"), SITE + "/author/Albert-Einstein") == {
        "name": "Albert Einstein",
        "born": date(1879, 3, 14),
        "birthplace": "Ulm, Germany",
    }


def test_the_author_page_spells_some_names_differently():
    # The quotes say "Alexandre Dumas fils", but his own page says "Dumas-fils".
    # That's why quotes are matched to authors by their link, not their name.
    assert parse_author(saved_page("author-Alexandre-Dumas-fils.html"), "")["name"] == "Alexandre Dumas-fils"


def test_parse_author_with_missing_pieces(caplog):
    found = parse_author(saved_page("broken_author.html"), SITE + "/author/Mystery-Writer")
    assert found == {"name": "Mystery Writer", "born": None, "birthplace": None}
    assert "Couldn't read the birth date 'sometime in the 1800s'" in caplog.text


def test_parse_author_with_no_name(caplog):
    assert parse_author("<html><body><p>Not an author page</p></body></html>", SITE + "/author/X") is None
    assert "it has no name" in caplog.text


@pytest.mark.parametrize(
    "text, born",
    [
        ("March 14, 1879", date(1879, 3, 14)),
        ("  July 31, 1965 ", date(1965, 7, 31)),
        ("February 30, 1900", None),        # there's no 30 February
        ("14 March 1879", None),
        ("", None),
    ],
)
def test_parse_born_date(text, born):
    assert parse_born_date(text) == born
