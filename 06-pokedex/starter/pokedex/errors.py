"""The errors this package raises.

They all inherit from PokedexError, so the command line can catch every
one of them with a single `except PokedexError`.
"""


class PokedexError(Exception):
    """Something went wrong that we can explain to the user."""


class NotFound(PokedexError):
    """The API has nothing at this address (a 404). Asking again won't help."""


class PokemonNotFound(NotFound):
    """There's no Pokémon with this name."""

    def __init__(self, name: str) -> None:
        super().__init__(
            f"There's no Pokémon called {name!r}. Check the spelling, "
            "or see some real names with: python -m pokedex list"
        )
        self.name = name


class ServerError(PokedexError):
    """The server had a problem (a 5xx status). Trying again might work."""


class TeamError(PokedexError):
    """A team that breaks the rules, like a seventh member."""


class UsageError(PokedexError):
    """The command was typed wrongly, like a team size that isn't a number."""
