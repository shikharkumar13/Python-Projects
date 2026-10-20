"""Shared fixtures. pytest reads this file by itself, before any test runs."""

import time

import pytest


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Stop the scraper from really pausing, in every test. The list records how long it wanted to wait."""
    waited = []
    monkeypatch.setattr(time, "sleep", waited.append)
    return waited
