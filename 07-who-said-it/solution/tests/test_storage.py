"""Tests for saving and loading quotes.json."""

import json
from datetime import date, datetime, timezone

import pytest

from whosaidit.errors import StorageError
from whosaidit.models import Author, Quote
from whosaidit.storage import QuoteBook, atomic_write, load, save

WHEN = datetime(2026, 10, 20, 9, 30, tzinfo=timezone.utc)


def make_book():
    quotes = [Quote("Imagination is everything.", "Albert Einstein", "Albert-Einstein", ("imagination",)),
              Quote("Be kind.", "André Gide", "Andre-Gide")]
    authors = {"Albert-Einstein": Author("Albert-Einstein", "Albert Einstein", date(1879, 3, 14), "Ulm, Germany")}
    return QuoteBook(quotes, authors, WHEN)


def test_save_then_load(tmp_path):
    path = tmp_path / "quotes.json"
    save(path, make_book())
    book = load(path)
    assert book == make_book()
    assert book.author_of(book.quotes[0]).born == date(1879, 3, 14)
    assert book.author_of(book.quotes[1]) is None          # that author's page was never scraped


def test_the_file_has_a_scraped_at_time(tmp_path):
    path = tmp_path / "quotes.json"
    save(path, make_book())
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["scraped_at"] == "2026-10-20T09:30:00+00:00"
    assert "André" in path.read_text(encoding="utf-8")      # readable, not é


def test_atomic_write_replaces_the_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("old", encoding="utf-8")
    with atomic_write(path) as file:
        file.write("new")
        assert path.read_text(encoding="utf-8") == "old"     # not replaced until the block ends
    assert path.read_text(encoding="utf-8") == "new"


def test_a_crash_halfway_leaves_the_old_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("old", encoding="utf-8")
    with pytest.raises(ZeroDivisionError):
        with atomic_write(path) as file:
            file.write("half of the new")
            1 / 0
    assert path.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.iterdir()) == [path]                # and no .tmp file left behind


def test_load_with_no_file(tmp_path):
    with pytest.raises(StorageError, match="python -m whosaidit scrape"):
        load(tmp_path / "quotes.json")


@pytest.mark.parametrize(
    "content",
    [
        '{"quotes": [',                                                       # cut off halfway
        '{"quotes": [], "authors": []}',                                      # no scraped_at
        '{"quotes": [{"text": ""}], "authors": [], "scraped_at": "2026-10-20T09:30:00+00:00"}',
        '[1, 2, 3]',
    ],
)
def test_load_a_damaged_file(tmp_path, content):
    path = tmp_path / "quotes.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StorageError, match="damaged"):
        load(path)


def test_load_a_file_with_no_quotes(tmp_path):
    path = tmp_path / "quotes.json"
    path.write_text('{"quotes": [], "authors": [], "scraped_at": "2026-10-20T09:30:00+00:00"}', encoding="utf-8")
    with pytest.raises(StorageError, match="no quotes"):
        load(path)


def test_save_into_a_missing_folder(tmp_path):
    with pytest.raises(StorageError, match="Couldn't save"):
        save(tmp_path / "no-such-folder" / "quotes.json", make_book())
