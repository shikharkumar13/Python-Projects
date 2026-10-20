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
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)      # keep func's name and docstring on the wrapper
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except retry_on as error:
                    if attempt == attempts:
                        raise       # out of tries: let the last error through
                    delay = base_delay * 2 ** (attempt - 1)
                    logger.warning(
                        "%s failed (%s). Waiting %.1f s before try %d of %d.",
                        func.__name__, error, delay, attempt + 1, attempts,
                    )
                    time.sleep(delay)
                    attempt += 1

        return wrapper

    return decorator
