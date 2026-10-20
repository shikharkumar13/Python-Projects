"""Shared fixtures for the tests. pytest reads this file by itself, before any test runs.

No test ever uses the internet. Some use FakeSession (in fakes.py), which
hands out answers the test chose. The rest use `saved`, a client that reads
the real PokéAPI answers saved in tests/fixtures/.
"""

import time

import pytest

from fakes import FIXTURES, FakeSession
from pokedex.client import PokeClient


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Stop retry() from really waiting, in every test. The list records how long it wanted to wait."""
    waited = []
    monkeypatch.setattr(time, "sleep", waited.append)
    return waited


@pytest.fixture
def saved():
    """A client that reads the saved answers in tests/fixtures/. Any real request fails the test."""
    return PokeClient(cache_dir=FIXTURES, session=FakeSession())


@pytest.fixture
def chart(saved):
    return saved.get_type_chart()
