"""Tests for the game: matching guesses, hints, and whole rounds with made-up typing."""

import random
from datetime import date, datetime, timezone

import pytest

from whosaidit.game import hints, initials, is_match, normalise, play, play_round, visible_tags
from whosaidit.models import Author, Quote
from whosaidit.storage import QuoteBook

EINSTEIN = Author("Albert-Einstein", "Albert Einstein", date(1879, 3, 14), "Ulm, Germany")
QUOTE = Quote("Imagination is everything.", "Albert Einstein", "Albert-Einstein", ("imagination",))


# ---------------------------------------------------------------------------
# Matching guesses
# ---------------------------------------------------------------------------

def test_the_full_name_matches():
    assert is_match("Albert Einstein", "Albert Einstein")


def test_the_surname_matches_in_any_capitals():
    assert is_match("einstein", "Albert Einstein")
    assert is_match("  EINSTEIN ", "Albert Einstein")


def test_part_of_a_name_is_not_enough():
    assert not is_match("stein", "Albert Einstein")
    assert not is_match("albert", "Albert Einstein")


@pytest.mark.parametrize(
    "guess, name",
    [
        ("j.k. rowling", "J.K. Rowling"),
        ("jk rowling", "J.K. Rowling"),
        ("J K Rowling", "J.K. Rowling"),
        ("rowling", "J.K. Rowling"),
        ("andre gide", "André Gide"),                      # no accent needed
        ("gide", "André Gide"),
        ("king", "Martin Luther King Jr."),                # "Jr." isn't the surname
        ("martin luther king", "Martin Luther King Jr."),
        ("dumas", "Alexandre Dumas fils"),
        ("lengle", "Madeleine L'Engle"),
        ("l'engle", "Madeleine L'Engle"),
        ("seuss", "Dr. Seuss"),
        ("dr seuss", "Dr. Seuss"),
    ],
)
def test_close_enough_guesses_match(guess, name):
    assert is_match(guess, name)


@pytest.mark.parametrize(
    "guess, name",
    [
        ("albert", "Albert Einstein"),     # a first name isn't enough
        ("stein", "Albert Einstein"),      # part of a word doesn't count
        ("einstien", "Albert Einstein"),   # a typo
        ("", "Albert Einstein"),
        ("...", "Albert Einstein"),        # nothing left once the dots go
        ("jr", "Martin Luther King Jr."),
        ("mark twain", "Albert Einstein"),
    ],
)
def test_wrong_guesses_do_not_match(guess, name):
    assert not is_match(guess, name)


@pytest.mark.parametrize(
    "text, normal",
    [("  André GIDE ", "andre gide"), ("J.K. Rowling", "jk rowling"), ("Dumas-fils", "dumas fils"), ("L'Engle", "lengle")],
)
def test_normalise(text, normal):
    assert normalise(text) == normal


# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "name, letters",
    [("Albert Einstein", "A. E."), ("J.K. Rowling", "J. K. R."), ("Martin Luther King Jr.", "M. L. K."),
     ("Dr. Seuss", "S."), ("Madeleine L'Engle", "M. L.")],
)
def test_initials(name, letters):
    assert initials(name) == letters


def test_hints_in_order():
    assert hints(QUOTE, EINSTEIN) == [
        "They were born on 14 March 1879.",
        "They were born in Ulm, Germany.",
        "Their initials are A. E.",
    ]


def test_hints_with_nothing_known():
    clues = hints(QUOTE, None)
    assert clues[0].startswith("Nobody knows exactly when")
    assert clues[1].startswith("Nobody knows where")
    assert clues[2] == "Their initials are A. E."


def test_tags_that_give_the_answer_away_are_hidden():
    quote = Quote("Twenty years from now...", "Mark Twain", "Mark-Twain", ("misattributed-mark-twain", "dreams"))
    assert visible_tags(quote) == ["dreams"]
    austen = Quote("Hi.", "Jane Austen", "Jane-Austen", ("jane-austen", "love"))
    assert visible_tags(austen) == ["love"]


# ---------------------------------------------------------------------------
# Rounds, with made-up typing
# ---------------------------------------------------------------------------

def typing(*answers):
    """An ask() that types these answers, one per question, and remembers the questions."""
    answers = list(answers)
    asked = []
    def ask(prompt):
        asked.append(prompt)
        return answers.pop(0)
    ask.asked = asked
    return ask


@pytest.mark.parametrize(
    "answers, points",
    [
        (["einstein"], 4),
        (["newton", "einstein"], 3),
        (["newton", "darwin", "curie", "einstein"], 1),
        (["newton", "darwin", "curie", "bohr"], 0),
    ],
)
def test_points_for_each_guess(answers, points):
    said = []
    assert play_round(QUOTE, EINSTEIN, typing(*answers), said.append) == points


def test_each_wrong_guess_gives_the_next_hint():
    said = []
    play_round(QUOTE, EINSTEIN, typing("newton", "darwin", "curie", "bohr"), said.append)
    hint_lines = [line for line in said if line.startswith("Not quite.")]
    assert hint_lines == [
        "Not quite. Hint: They were born on 14 March 1879.",
        "Not quite. Hint: They were born in Ulm, Germany.",
        "Not quite. Hint: Their initials are A. E.",
    ]
    assert said[-1] == "Out of guesses! It was Albert Einstein."


def test_a_round_hides_tags_that_give_the_answer_away():
    twain = Quote("A lie can travel half way around the world.", "Mark Twain", "Mark-Twain",
                  ("misattributed-mark-twain", "truth"))
    said = []
    play_round(twain, None, typing("twain"), said.append)
    assert "Tags: truth" in said


def test_an_empty_guess_does_not_count():
    said = []
    ask = typing("", "   ", "einstein")
    assert play_round(QUOTE, EINSTEIN, ask, said.append) == 4
    assert said.count("Type a name, or quit to stop.") == 2


def book_of(count):
    quotes = [Quote(f"Quote number {n}.", "Albert Einstein", "Albert-Einstein") for n in range(count)]
    return QuoteBook(quotes, {"Albert-Einstein": EINSTEIN}, datetime(2026, 10, 20, tzinfo=timezone.utc))


def test_play_until_the_player_says_no():
    said = []
    total = play(book_of(5), random.Random(1), typing("einstein", "", "newton", "einstein", "n"), said.append)
    assert total == 4 + 3
    assert said[-1] == "Final score: 7 out of 8. Thanks for playing!"


def test_quit_in_the_middle_of_a_round():
    said = []
    assert play(book_of(5), random.Random(1), typing("einstein", "", "quit"), said.append) == 4
    # The round that was quit halfway through doesn't count against you.
    assert said[-1] == "Final score: 4 out of 4. Thanks for playing!"


def test_ctrl_d_ends_the_game_politely():
    def end_of_input(prompt):
        raise EOFError
    said = []
    assert play(book_of(3), random.Random(1), end_of_input, said.append) == 0
    assert said[-1].startswith("Final score: 0")


def test_every_quote_once_then_stop():
    said = []
    play(book_of(2), random.Random(1), typing("einstein", "", "einstein", ""), said.append)
    quotes_shown = [line for line in said if line.startswith("“")]
    assert sorted(quotes_shown) == ["“Quote number 0.”", "“Quote number 1.”"]
    assert "That's every quote. Well done!" in said


def test_the_same_seed_gives_the_same_order():
    def first_quote(seed):
        said = []
        play(book_of(20), random.Random(seed), typing("quit"), said.append)
        return [line for line in said if line.startswith("“")]
    assert first_quote(7) == first_quote(7)
    assert len({tuple(first_quote(seed)) for seed in range(10)}) > 1
