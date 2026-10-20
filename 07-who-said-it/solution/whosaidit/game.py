"""The game: show a quote, take up to 4 guesses, and give a hint after each wrong one."""

from __future__ import annotations

import random
import re
import unicodedata
from collections.abc import Callable

from whosaidit.models import Author, Quote
from whosaidit.storage import QuoteBook

GUESSES = 4

# Words at the end of a name that aren't the surname: "Martin Luther King Jr."
SUFFIXES = {"jr", "sr", "fils", "ii", "iii"}
# Words at the start that aren't part of the initials: "Dr. Seuss"
TITLES = {"dr", "mr", "mrs", "ms", "sir"}

QUIT_WORDS = {"quit", "q", "exit"}

Ask = Callable[[str], str]      # like input(): show a prompt, return what was typed
Say = Callable[[str], None]     # like print()


class Quit(Exception):
    """The player typed "quit"."""


def normalise(text: str) -> str:
    """Make a name easy to compare: "  André GIDE " gives "andre gide", and "J.K. Rowling" gives "jk rowling".

    - NFKD splits "é" into a plain "e" followed by a separate accent mark.
    - Lowercase, and hyphens become spaces.
    - Then every character that isn't a letter, a digit or a space is
      removed: the dots, the apostrophes, and those accent marks too. So
      "André" and "Andre" come out the same.
    - Runs of spaces become one space.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.lower().replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return " ".join(text.split())


def name_words(name: str) -> list[str]:
    """The normalised words of a name, without a suffix like "Jr." at the end."""
    words = normalise(name).split()
    while len(words) > 1 and words[-1] in SUFFIXES:
        words.pop()
    return words


def is_match(guess: str, name: str) -> bool:
    """Is this guess right? The full name, or just the surname, in any capitals, with or without accents.

    Spaces are ignored too, so "jk rowling", "j.k. rowling" and "J K Rowling"
    all match "J.K. Rowling". "einstein" matches "Albert Einstein", and
    "king" matches "Martin Luther King Jr.". A first name on its own
    ("albert") doesn't count: there could be lots of Alberts.
    """
    squashed = normalise(guess).replace(" ", "")
    if not squashed:
        return False
    words = name_words(name)
    return squashed in {"".join(words), words[-1], normalise(name).replace(" ", "")}


def initials(name: str) -> str:
    """ "J.K. Rowling" gives "J. K. R.", and "Martin Luther King Jr." gives "M. L. K."."""
    words = [word for word in re.split(r"[\s.]+", name) if word]
    keep = [word for word in words if normalise(word) not in SUFFIXES | TITLES]
    return " ".join(word[0].upper() + "." for word in keep)


def hints(quote: Quote, author: Author | None) -> list[str]:
    """The three hints, in order: when they were born, where, and their initials."""
    if author is not None and author.born is not None:
        # %B is the month's name. The day is written separately, because
        # "%-d" (a day without a leading 0) doesn't work on Windows.
        born = f"They were born on {author.born.day} {author.born:%B %Y}."
    else:
        born = "Nobody knows exactly when they were born."
    if author is not None and author.birthplace:
        place = f"They were born in {author.birthplace}."
    else:
        place = "Nobody knows where they were born."
    return [born, place, f"Their initials are {initials(quote.author)}"]


def visible_tags(quote: Quote) -> list[str]:
    """The tags that are safe to show. A tag like "jane-austen" or
    "misattributed-mark-twain" would give the answer away, so any tag that
    shares a word (of 3 letters or more) with the author's name is hidden."""
    name = {word for word in name_words(quote.author) if len(word) >= 3}
    return [tag for tag in quote.tags if not name & set(normalise(tag).split())]


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def ask_for_guess(ask: Ask, say: Say, prompt: str) -> str:
    """Ask until the player types something. Raises Quit if they type "quit"."""
    while True:
        guess = ask(prompt).strip()
        if guess.lower() in QUIT_WORDS:
            raise Quit
        if guess:
            return guess
        say("Type a name, or quit to stop.")


def play_round(quote: Quote, author: Author | None, ask: Ask, say: Say) -> int:
    """One quote. Returns the points: 4 for a first-guess answer, then 3, 2, 1, or 0."""
    say("")
    say(f"“{quote.text}”")
    tags = visible_tags(quote)
    if tags:
        say(f"Tags: {', '.join(tags)}")
    clues = hints(quote, author)
    for number in range(1, GUESSES + 1):
        guess = ask_for_guess(ask, say, f"Guess {number} of {GUESSES}. Who said it? ")
        if is_match(guess, quote.author):
            points = GUESSES - number + 1
            say(f"Yes! It was {quote.author}. {plural(points, 'point')}.")
            return points
        if number < GUESSES:
            say(f"Not quite. Hint: {clues[number - 1]}")
    say(f"Out of guesses! It was {quote.author}.")
    return 0


def play(book: QuoteBook, rng: random.Random, ask: Ask = input, say: Say = print) -> int:
    """Play rounds until the player stops, or every quote has been used. Returns the total score."""
    order = list(book.quotes)
    rng.shuffle(order)          # a random order, with no quote twice
    total = rounds = 0
    try:
        for quote in order:
            points = play_round(quote, book.author_of(quote), ask, say)
            # Counted only once the round is over, so quitting halfway
            # through a round doesn't count it against you.
            rounds += 1
            total += points
            say(f"Score: {total} out of {rounds * GUESSES}.")
            if ask("Another one? (Enter for yes, n for no) ").strip().lower() in {"n", "no"} | QUIT_WORDS:
                break
        else:
            say("That's every quote. Well done!")
    except (Quit, EOFError, KeyboardInterrupt):
        # EOFError is Ctrl+D (Ctrl+Z on Windows), and KeyboardInterrupt is Ctrl+C.
        say("")
    say(f"Final score: {total} out of {rounds * GUESSES}. Thanks for playing!")
    return total
