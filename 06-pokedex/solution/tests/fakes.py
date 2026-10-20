"""Stand-ins for requests, so the tests never touch the internet."""

from pathlib import Path

import requests

# Real PokéAPI answers, saved (and trimmed) for the tests to read.
FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    """Pretends to be a requests.Response, with a status code and some JSON."""

    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self.data = data if data is not None else {}

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)


class FakeSession:
    """Pretends to be a requests.Session, without the internet.

    Give it the answers it should hand out, in order. An answer can also be
    an exception, like requests.Timeout(), which it raises instead. It
    remembers every request, so a test can check how many there were. If
    it runs out of answers, the test fails.
    """

    def __init__(self, *answers):
        self.answers = list(answers)
        self.requests = []          # (url, timeout) for every request
        self.headers = {}
        self.closed = False

    def get(self, url, timeout=None):
        self.requests.append((url, timeout))
        if not self.answers:
            raise AssertionError(f"An unexpected request to {url}")
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def close(self):
        self.closed = True
