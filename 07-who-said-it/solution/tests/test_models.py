"""Tests for Quote and Author, and the rules they check."""

from datetime import date

import pytest

from whosaidit.errors import ValidationError
from whosaidit.models import Author, Quote


def test_a_good_quote():
    quote = Quote("Be yourself.", "Oscar Wilde", "Oscar-Wilde", ("life",))
    assert quote.tags == ("life",)


@pytest.mark.parametrize(
    "text, author, slug, tags",
    [
        ("", "Oscar Wilde", "Oscar-Wilde", ()),
        ("   ", "Oscar Wilde", "Oscar-Wilde", ()),
        ("Be yourself.", "", "Oscar-Wilde", ()),
        ("Be yourself.", "Oscar Wilde", "", ()),
        ("Be yourself.", "Oscar Wilde", "Oscar-Wilde", ("life", " ")),
    ],
)
def test_a_bad_quote_is_refused(text, author, slug, tags):
    with pytest.raises(ValidationError):
        Quote(text, author, slug, tags)


def test_quotes_cannot_be_changed():
    quote = Quote("Be yourself.", "Oscar Wilde", "Oscar-Wilde")
    with pytest.raises(AttributeError):
        quote.text = "Be someone else."     # type: ignore[misc]


@pytest.mark.parametrize("slug, name", [("", "Albert Einstein"), ("Albert-Einstein", " ")])
def test_a_bad_author_is_refused(slug, name):
    with pytest.raises(ValidationError):
        Author(slug, name)


def test_round_trip_through_dicts():
    quote = Quote("Be yourself.", "Oscar Wilde", "Oscar-Wilde", ("life", "humor"))
    author = Author("Albert-Einstein", "Albert Einstein", date(1879, 3, 14), "Ulm, Germany")
    assert Quote.from_dict(quote.to_dict()) == quote
    assert Author.from_dict(author.to_dict()) == author
    assert author.to_dict()["born"] == "1879-03-14"
    assert Author.from_dict(Author("X", "X").to_dict()) == Author("X", "X")


@pytest.mark.parametrize(
    "data",
    [
        {"text": "Hi", "author": "Me"},                                       # no author_slug or tags
        {"text": "Hi", "author": "Me", "author_slug": "Me", "tags": None},
        {"text": "", "author": "Me", "author_slug": "Me", "tags": []},        # breaks the rules
    ],
)
def test_quote_from_a_bad_dict(data):
    with pytest.raises(ValidationError):
        Quote.from_dict(data)


def test_author_from_a_bad_date():
    with pytest.raises(ValidationError):
        Author.from_dict({"slug": "X", "name": "X", "born": "14 March 1879", "birthplace": None})
