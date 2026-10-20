"""Talking to PokéAPI (https://pokeapi.co), politely.

- Every request has a timeout, and a User-Agent that says who's asking.
- Every answer is saved in cache/, so asking for the same thing twice
  costs one request, not two. PokéAPI's fair-use policy asks for this.
- A failed request is tried again, but only when trying again can help.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from types import TracebackType
from typing import Any

import requests

from pokedex.errors import NotFound, PokemonNotFound, ServerError
from pokedex.models import STRUGGLE, Move, Pokemon
from pokedex.retry import retry
from pokedex.typechart import TYPES, TypeChart

BASE_URL = "https://pokeapi.co/api/v2/"
USER_AGENT = "pokedex-team-builder/1.0 (a Python course practice project)"
TIMEOUT = 10            # seconds to wait for an answer before giving up
PAGE_SIZE = 20          # Pokémon names per page, when listing them
BATTLE_MOVES = 4        # moves each Pokémon takes into a battle
MAX_MOVE_LOOKUPS = 12   # how many of its moves we look at to find those 4

# The folder that holds the pokedex package. The cache and the log go here.
PROJECT_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_DIR / "cache"
LOG_FILE = PROJECT_DIR / "pokedex.log"

logger = logging.getLogger(__name__)


def cache_name(url: str) -> str:
    """The file name that the answer for a URL is saved under.

    ".../api/v2/pokemon/pikachu" gives "pokemon-pikachu.json", and
    ".../pokemon?offset=20&limit=20" gives "pokemon-offset-20-limit-20.json".
    Anything that isn't a letter or a digit becomes "-", because characters
    like ? and / aren't allowed in file names.
    """
    path = url.removeprefix(BASE_URL).strip("/").lower()
    return "".join(char if char.isalnum() else "-" for char in path) + ".json"


def clean_name(name: str) -> str:
    """Spell a name the way PokéAPI does: "  Mr. Mime " becomes "mr-mime".

    Raises PokemonNotFound for a name that can't be real, like "../secret",
    without asking the API at all.
    """
    name = name.strip().lower().replace(" ", "-").replace(".", "").replace("'", "")
    if name == "" or not all(char.isalnum() or char == "-" for char in name):
        raise PokemonNotFound(name)
    return name


class PokeClient:
    """A polite PokéAPI client. Use it in a `with` block, so its connection always gets closed:

        with PokeClient() as client:
            pikachu = client.get_pokemon("pikachu")

    Tests pass in their own cache folder, and a fake session that never
    touches the internet.
    """

    def __init__(self, cache_dir: Path = CACHE_DIR, session: requests.Session | None = None) -> None:
        self.cache_dir = cache_dir
        # A Session keeps one connection open for all our requests, which is
        # faster, and sends the same headers every time.
        self.session = session if session is not None else requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.requests_made = 0
        self.from_cache = 0

    def __enter__(self) -> PokeClient:
        # Whatever this returns is what `as client` gets.
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Runs when the `with` block ends, even if an error ended it.

        It returns None, which counts as False, and means "don't hide the
        error": if something went wrong inside the with block, it carries on upwards.
        """
        self.session.close()

    # -----------------------------------------------------------------------
    # Getting answers: from the cache first, from the internet if we must
    # -----------------------------------------------------------------------

    def get_json(self, url: str) -> dict[str, Any]:
        """PokéAPI's answer for a URL. From the cache if it's there, otherwise downloaded and saved."""
        path = self.cache_dir / cache_name(url)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                # OSError: we can't read the file at all. ValueError: it's damaged
                # (JSONDecodeError and UnicodeDecodeError are both ValueErrors).
                logger.warning("Can't use %s (%s), so downloading it again", path.name, error)
            else:
                if isinstance(data, dict):      # every PokéAPI answer is a JSON object
                    self.from_cache += 1
                    return data
                logger.warning("%s isn't a PokéAPI answer, so downloading it again", path.name)

        data = self._fetch(url)
        self._save(path, data)
        return data

    def _save(self, path: Path, data: dict[str, Any]) -> None:
        """Save an answer in the cache.

        It writes a .tmp file first, then renames it. A rename is all or
        nothing, so if the program is stopped halfway through writing, it
        can't leave a half-written file in the cache. If saving fails, that's
        not a disaster: we just log it, and download it again next time.
        """
        temp = path.with_suffix(".tmp")
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            temp.replace(path)
        except OSError as error:
            logger.warning("Couldn't save %s in the cache: %s", path.name, error)

    # Timeouts and server errors (5xx) are the server's problem, and might be
    # gone in a second, so they're worth another try. A 404, or any other 4xx,
    # means WE asked for something wrong. Asking again gives the same answer.
    @retry(retry_on=(requests.Timeout, ServerError), attempts=3, base_delay=0.5)
    def _fetch(self, url: str) -> dict[str, Any]:
        """Download one answer from PokéAPI.

        Raises NotFound for a 404, ServerError for a 5xx, and requests.HTTPError
        for any other bad status.
        """
        logger.info("GET %s", url)
        self.requests_made += 1
        response = self.session.get(url, timeout=TIMEOUT)
        if response.status_code == 404:
            raise NotFound(f"PokéAPI has nothing at {url}")
        if response.status_code >= 500:
            raise ServerError(f"PokéAPI had a problem ({response.status_code}) with {url}")
        response.raise_for_status()     # any other 4xx: our request was wrong
        data: dict[str, Any] = response.json()
        return data

    # -----------------------------------------------------------------------
    # Turning answers into objects
    # -----------------------------------------------------------------------

    def get_pokemon(self, name: str) -> Pokemon:
        """Look up a Pokémon by name (or by number, like "25"). Raises PokemonNotFound."""
        url = f"{BASE_URL}pokemon/{clean_name(name)}"
        try:
            data = self.get_json(url)
        except NotFound as error:
            # "raise ... from error" keeps the first error attached to the new
            # one, so a traceback would show both. The user just sees a
            # friendlier message that names the Pokémon.
            raise PokemonNotFound(name) from error
        return Pokemon.from_api(data)

    def get_move(self, name: str) -> Move:
        """Look up one move by name."""
        return Move.from_api(self.get_json(f"{BASE_URL}move/{name}"))

    def get_battle_moves(self, pokemon: Pokemon) -> list[Move]:
        """Up to 4 attacks for a battle, from the moves it learns last.

        Each move needs its own request, so this is lazy. The generator
        expressions don't look anything up until islice() asks for the next
        one, and islice() stops asking once it has 4. A Pokémon whose first
        4 moves are all attacks costs just 4 lookups.
        """
        looked_up = (self.get_move(name) for name in pokemon.move_names[:MAX_MOVE_LOOKUPS])
        attacks = (move for move in looked_up if move.is_attack)
        return list(islice(attacks, BATTLE_MOVES)) or [STRUGGLE]

    def get_type_chart(self) -> TypeChart:
        """The type chart, built from one /type/{name} answer for each of the 18 types."""
        return TypeChart.from_api(self.get_json(f"{BASE_URL}type/{name}") for name in TYPES)

    def iter_pokemon(self) -> Iterator[str]:
        """Every Pokémon's name in Pokédex order, fetched one page at a time.

        PokéAPI hands out a long list in pages. Each page has a "next" field
        with the URL of the page after it, and on the last page "next" is
        None. Because this is a generator, it only fetches a page when the
        names from the one before have run out. Taking the first 30 names
        costs 2 requests, not 68.
        """
        url: str | None = f"{BASE_URL}pokemon?offset=0&limit={PAGE_SIZE}"
        while url is not None:
            page = self.get_json(url)
            for result in page["results"]:
                yield result["name"]
            url = page["next"]
