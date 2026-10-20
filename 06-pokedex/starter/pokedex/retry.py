"""A decorator that tries a function again when it fails, waiting longer each time."""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")    # "whatever type the decorated function returns"


def retry(
    *,
    retry_on: tuple[type[Exception], ...],
    attempts: int = 3,
    base_delay: float = 0.5,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """A decorator FACTORY: retry(...) makes a decorator, and that decorator wraps a function.

        @retry(retry_on=(TimeoutError,), attempts=3)
        def download(): ...

    The function is tried up to `attempts` times. Only the errors in
    `retry_on` lead to another try. Any other error goes straight through,
    because trying again can't fix it. Before each new try, it waits
    base_delay seconds, then twice that, then twice that again (0.5, 1, 2,
    and so on). That's called exponential backoff: a struggling server gets
    more and more time to recover.

    retry_on has no default on purpose. You have to decide which errors are
    worth another try.
    """
    # TODO 1: the decorator factory. There are three functions, one inside the other:
    #   retry(...)       takes the settings, and returns `decorator`
    #   decorator(func)  takes the function, and returns `wrapper`
    #   wrapper(...)     runs func, trying again when it fails
    # - First, if attempts is less than 1, raise ValueError.
    # - Write `def decorator(func)`, and inside it `def wrapper(*args, **kwargs)`.
    #   Put @functools.wraps(func) on the line above `def wrapper`.
    # - In wrapper: start with attempt = 1, then loop with `while True:`
    #   - try: return func(*args, **kwargs)
    #   - except retry_on as error:  (any of the error types in the tuple)
    #     - if attempt == attempts: `raise` on its own, which re-raises the error
    #     - otherwise work out delay = base_delay * 2 ** (attempt - 1), log a
    #       warning with logger.warning(...), time.sleep(delay), and add 1 to attempt.
    # - decorator returns wrapper, and retry returns decorator. (No brackets!
    #   You're handing the function over, not calling it.)
    # The placeholder below already has decorator's def line, with its type
    # hints. Give wrapper this one:  def wrapper(*args: Any, **kwargs: Any) -> T:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        return func   # placeholder: hands func back unchanged, so nothing is retried yet
    return decorator
