"""Tests for the commands, run through main() just like the real program.

main() lets us choose the data file, the cache folder, the website (a fake
one) and the player's typing, so nothing touches the internet or your files.
"""

import pytest
import requests

from fakes import SITE, FakeSite, author_page, quote_page
from whosaidit.cli import main

PAGES = {
    SITE + "/": quote_page([("Imagination is everything.", "Albert Einstein", "Albert-Einstein", ["imagination"]),
                            ("There is no charm equal to tenderness of heart.", "Jane Austen", "Jane-Austen", ["charm"])],
                           next_href="/page/2/"),
    SITE + "/page/2/": quote_page([("Life is like riding a bicycle.", "Albert Einstein", "Albert-Einstein", ["life"])]),
    SITE + "/author/Albert-Einstein": author_page("Albert Einstein"),
    SITE + "/author/Jane-Austen": author_page("Jane Austen", "December 16, 1775", "in Steventon, The United Kingdom"),
}


def run(tmp_path, *argv, site=None, answers=()):
    answers = list(answers)
    return main(list(argv), data_file=tmp_path / "quotes.json", cache_dir=tmp_path / "cache",
                session=site if site is not None else FakeSite(PAGES, robots=""),
                ask=lambda prompt: answers.pop(0))


def test_scrape_then_stats(tmp_path, capsys):
    assert run(tmp_path, "scrape") == 0
    out = capsys.readouterr().out
    assert "Saved 3 quotes by 2 authors to quotes.json." in out
    assert "Requests to the site: 5." in out           # robots.txt, 2 pages, 2 authors

    assert run(tmp_path, "stats") == 0
    out = capsys.readouterr().out
    assert "Albert Einstein          2" in out
    assert "1770s" in out and "1870s" in out


def test_scraping_again_costs_no_requests(tmp_path, capsys):
    run(tmp_path, "scrape")
    site = FakeSite()                                   # an empty site: everything is a 404
    assert run(tmp_path, "scrape", site=site) == 0
    assert site.requests == []
    assert "Requests to the site: 0. Pages from html_cache/: 4." in capsys.readouterr().out


def test_play(tmp_path, capsys):
    run(tmp_path, "scrape")
    assert run(tmp_path, "play", "3", answers=["nobody", "quit"]) == 0
    out = capsys.readouterr().out
    assert "Who said it? 3 quotes." in out
    assert "Not quite. Hint: They were born on" in out
    assert "Final score: 0 out of 0." in out          # quit during the first round


def test_play_before_scraping(tmp_path, capsys):
    assert run(tmp_path, "play") == 1
    assert "python -m whosaidit scrape" in capsys.readouterr().out


def test_no_internet(tmp_path, capsys):
    class Offline(FakeSite):
        def get(self, url, timeout=None):
            raise requests.ConnectionError("no internet")
    assert run(tmp_path, "scrape", site=Offline()) == 1
    assert "Are you online?" in capsys.readouterr().out


def test_a_site_with_no_quotes(tmp_path, capsys):
    assert run(tmp_path, "scrape", site=FakeSite({SITE + "/": "<html><body>Under construction</body></html>"}, robots="")) == 1
    assert "No quotes found" in capsys.readouterr().out
    assert not (tmp_path / "quotes.json").exists()


def test_robots_txt_says_no(tmp_path, capsys):
    assert run(tmp_path, "scrape", site=FakeSite(PAGES, robots="User-agent: *\nDisallow: /\n")) == 1
    assert "robots.txt asks programs not to fetch" in capsys.readouterr().out


def test_robots_txt_blocks_only_the_author_pages(tmp_path, capsys):
    assert run(tmp_path, "scrape", site=FakeSite(PAGES, robots="User-agent: *\nDisallow: /author/\n")) == 0
    out = capsys.readouterr().out
    assert "Saved 3 quotes by 0 authors" in out
    assert "2 authors' pages couldn't be read" in out


def test_ctrl_c_while_scraping(tmp_path, capsys):
    class Interrupted(FakeSite):
        def get(self, url, timeout=None):
            if url.endswith("/page/2/"):
                raise KeyboardInterrupt
            return super().get(url, timeout)
    assert run(tmp_path, "scrape", site=Interrupted(PAGES, robots="")) == 1
    assert "carries on from there next time" in capsys.readouterr().out
    assert (tmp_path / "cache" / "index.html").exists()     # page 1 is kept
    assert not (tmp_path / "quotes.json").exists()


def test_play_with_an_empty_file(tmp_path, capsys):
    (tmp_path / "quotes.json").write_text('{"quotes": [], "authors": [], "scraped_at": "2026-10-20T09:30:00+00:00"}',
                                          encoding="utf-8")
    assert run(tmp_path, "play") == 1
    assert "has no quotes in it" in capsys.readouterr().out


@pytest.mark.parametrize(
    "argv, code, words",
    [
        ([], 0, "Usage"),
        (["help"], 0, "Usage"),
        (["dance"], 2, "no command called 'dance'"),
        (["scrape", "now"], 2, "doesn't take anything"),
        (["stats", "please"], 2, "doesn't take anything"),
        (["play", "seven"], 2, "whole number"),
        (["play", "²"], 2, "whole number"),
        (["play", "1", "2"], 2, "Just one number"),
    ],
)
def test_mistakes(tmp_path, capsys, argv, code, words):
    assert run(tmp_path, *argv) == code
    assert words in capsys.readouterr().out
