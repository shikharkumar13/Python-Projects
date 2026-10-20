"""The errors this package raises.

They all inherit from WhoSaidItError, so the command line can catch every
one of them with a single `except WhoSaidItError`.
"""


class WhoSaidItError(Exception):
    """Something went wrong that we can explain to the user."""


class NotAllowed(WhoSaidItError):
    """The site's robots.txt asks us not to fetch this page."""


class ValidationError(WhoSaidItError):
    """Data that breaks the rules, like a quote with no text."""


class StorageError(WhoSaidItError):
    """quotes.json is missing, damaged, or can't be saved."""


class UsageError(WhoSaidItError):
    """The command was typed wrongly."""
