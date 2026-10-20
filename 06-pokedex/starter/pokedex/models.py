"""Pokémon, their moves, and teams."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from pokedex.errors import PokedexError, TeamError

MAX_TEAM_SIZE = 6

# The strongest move we use in battles. Moves stronger than this have a big
# catch in the real games (Explosion makes the user faint, Hyper Beam needs
# a turn to recharge), and our simple battles don't copy those catches.
MAX_POWER = 120

STAT_NAMES = ("hp", "attack", "defense", "special-attack", "special-defense", "speed")


@dataclass(frozen=True)
class Move:
    """One move, like Thunderbolt. frozen=True means it can't be changed once made."""

    name: str
    type: str                   # "electric"
    power: int                  # 0 for moves that don't do damage directly
    accuracy: int | None        # a percentage; None means it never misses
    damage_class: str           # "physical", "special" or "status"

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Move:
        """Make a Move from PokéAPI's answer for /move/{name}."""
        return cls(
            name=data["name"],
            type=data["type"]["name"],
            power=data["power"] or 0,       # the API says null (None) for no power
            accuracy=data["accuracy"],
            damage_class=data["damage_class"]["name"],
        )

    @property
    def is_attack(self) -> bool:
        """True for a move we can use in a battle: it does damage, and isn't too strong."""
        return self.damage_class != "status" and 0 < self.power <= MAX_POWER

    @property
    def display_name(self) -> str:
        """"thunder-punch" becomes "Thunder Punch"."""
        return self.name.replace("-", " ").title()


# What a Pokémon does when it has no attack that can hurt its opponent. In
# the real games, Struggle also hurts the user a little. Ours doesn't.
# "typeless" isn't in the type chart, so it always does normal damage.
STRUGGLE = Move("struggle", "typeless", 50, None, "physical")


def level_up_moves(data: dict[str, Any]) -> tuple[str, ...]:
    """The moves a Pokémon learns by levelling up, the latest-learned first.

    Pokémon learn their strongest moves last, so the first few of these make
    good battle moves. `data` is PokéAPI's answer for /pokemon/{name}. Each
    move lists the games it can be learned in, and how. We only want
    "level-up", and the highest level in any game.
    """
    # TODO 8
    # - Make an empty dictionary, `levels`: move name -> highest level.
    # - Loop over data["moves"]. For each entry, the name is entry["move"]["name"].
    #   Loop over entry["version_group_details"]. When
    #   detail["move_learn_method"]["name"] is "level-up", keep the bigger of
    #   levels.get(name, 0) and detail["level_learned_at"].
    # - Return the names as a tuple, sorted highest level first, and A to Z when
    #   the levels are the same: sorted(levels, key=lambda name: (-levels[name], name))
    return ()   # placeholder: replace this line


class Pokemon:
    """One kind of Pokémon, like Pikachu, as PokéAPI describes it."""

    def __init__(
        self,
        number: int,
        name: str,
        types: tuple[str, ...],
        stats: dict[str, int],
        move_names: tuple[str, ...] = (),
    ) -> None:
        self.number = number            # its number in the Pokédex: Pikachu is 25
        self.name = name                # PokéAPI's spelling: "pikachu", "mr-mime"
        self.types = types              # one or two types: ("fire", "flying")
        self.stats = stats              # base stats: {"hp": 35, "attack": 55, ...}
        self.move_names = move_names    # level-up moves, latest-learned first

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Pokemon:
        """Make a Pokemon from PokéAPI's answer for /pokemon/{name}.

        A classmethod is a second way to make an object. You call it on the
        class, Pokemon.from_api(data), and `cls` is the class itself.
        """
        # TODO 9
        # - types: a tuple of entry["type"]["name"] for each entry in data["types"].
        # - stats: a dictionary of entry["stat"]["name"]: entry["base_stat"] for each
        #   entry in data["stats"]. (A dictionary comprehension.)
        # - Return cls(data["id"], data["name"], types, stats, level_up_moves(data)).
        # Move.from_api, above, is a finished example. Open tests/fixtures/pokemon-pikachu.json
        # to see what `data` looks like.
        raise PokedexError("Making a Pokemon from PokéAPI's answer is TODO 9.")   # placeholder: replace this line

    @property
    def display_name(self) -> str:
        """"mr-mime" becomes "Mr-Mime"."""
        return self.name.title()

    def battle_stat(self, stat: str) -> int:
        """The stat at level 50, which is what battles use.

        This is the games' formula with the extras left out: HP is the base
        stat plus 60, and every other stat is the base stat plus 5.
        """
        if stat == "hp":
            return self.stats["hp"] + 60
        return self.stats[stat] + 5

    def __str__(self) -> str:
        return f"#{self.number} {self.display_name} ({'/'.join(self.types)})"

    def __repr__(self) -> str:
        return f"Pokemon({self.name!r})"


class Team:
    """Up to six different Pokémon, with a name."""

    def __init__(self, name: str, members: Iterable[Pokemon] = ()) -> None:
        self.name = name
        self.members: list[Pokemon] = []
        for pokemon in members:
            self.add(pokemon)

    def add(self, pokemon: Pokemon) -> None:
        """Add a Pokémon to the team. Raises TeamError if the team is full, or already has it."""
        # TODO 10
        # - If the team already has MAX_TEAM_SIZE members, raise TeamError.
        # - If `pokemon.name in self` (that uses __contains__, below), raise TeamError.
        # - Otherwise, append it to self.members.
        self.members.append(pokemon)   # placeholder: no rules yet

    # These "dunder" methods make a Team work with len(), for loops and `in`.

    def __len__(self) -> int:
        return len(self.members)

    def __iter__(self) -> Iterator[Pokemon]:
        return iter(self.members)

    def __contains__(self, name: object) -> bool:
        return any(pokemon.name == name for pokemon in self.members)

    def __str__(self) -> str:
        names = [pokemon.display_name for pokemon in self.members]
        if len(names) <= 1:
            return "".join(names)
        return ", ".join(names[:-1]) + " and " + names[-1]
