"""Tests for the @retry decorator, on small made-up functions."""

import pytest

from pokedex.retry import retry


class Flaky:
    """A function that fails with the given errors first, then works."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0
        self.__name__ = "flaky"     # real functions have a name, and retry() logs it

    def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "it worked"


def test_it_works_first_time_without_waiting(sleeps):
    flaky = Flaky()
    assert retry(retry_on=(TimeoutError,))(flaky)() == "it worked"
    assert flaky.calls == 1
    assert sleeps == []


def test_it_tries_again_after_a_listed_error(sleeps):
    flaky = Flaky(TimeoutError(), TimeoutError())
    assert retry(retry_on=(TimeoutError,), attempts=3)(flaky)() == "it worked"
    assert flaky.calls == 3
    assert sleeps == [0.5, 1.0]         # it waits twice as long each time


def test_it_gives_up_and_raises_the_last_error(sleeps):
    flaky = Flaky(TimeoutError("one"), TimeoutError("two"), TimeoutError("three"))
    with pytest.raises(TimeoutError, match="three"):
        retry(retry_on=(TimeoutError,), attempts=3, base_delay=2)(flaky)()
    assert flaky.calls == 3
    assert sleeps == [2, 4]


def test_other_errors_are_not_retried(sleeps):
    flaky = Flaky(KeyError("oops"))
    with pytest.raises(KeyError):
        retry(retry_on=(TimeoutError,))(flaky)()
    assert flaky.calls == 1
    assert sleeps == []


def test_it_keeps_the_function_name_and_docstring():
    @retry(retry_on=(TimeoutError,))
    def download(url):
        """Download something."""
        return url

    assert download.__name__ == "download"
    assert download.__doc__ == "Download something."
    assert download("x") == "x"         # arguments get passed through


def test_at_least_one_attempt():
    with pytest.raises(ValueError):
        retry(retry_on=(TimeoutError,), attempts=0)
