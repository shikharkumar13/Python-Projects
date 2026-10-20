"""How well a team's types cover each other, and finding the best team from a shortlist."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations

from pokedex.errors import TeamError
from pokedex.models import MAX_TEAM_SIZE, Pokemon
from pokedex.typechart import TYPES, TypeChart


@dataclass(frozen=True)
class Matchups:
    """The attack types that hurt one Pokémon a lot, and the ones that hardly hurt it."""

    weak_to: frozenset[str]     # more than normal damage
    resists: frozenset[str]     # less than normal damage, or none at all


@lru_cache(maxsize=None)
def matchups(chart: TypeChart, types: tuple[str, ...]) -> Matchups:
    """Which attack types are strong and weak against a Pokémon with these types.

    @lru_cache remembers the answer for every (chart, types) it has seen, and
    hands it straight back the next time. best_team() asks about the same 15
    Pokémon hundreds of times, so it saves a lot of work.

    lru_cache stores the arguments as dictionary keys, so they must be
    hashable. That's why `types` is a tuple, not a list.
    """
    # TODO 14
    # - weak_to: a frozenset of every attack in TYPES where
    #   chart.multiplier(attack, types) is more than 1.
    # - resists: the same, for less than 1.
    # - Return Matchups(weak_to, resists).
    # @lru_cache is already on the line above the def. That's all it takes.
    return Matchups(frozenset(), frozenset())   # placeholder: replace this line


@dataclass
class Coverage:
    """How well a whole team copes with each attack type."""

    weak: dict[str, int]        # for each attack type, how many members are weak to it
    resist: dict[str, int]      # and how many resist it
    gaps: list[str]             # attack types someone is weak to, and nobody resists

    @property
    def score(self) -> tuple[int, int]:
        """Bigger is better: first, fewer gaps. If two teams tie, more types resisted."""
        resisted = sum(1 for count in self.resist.values() if count > 0)
        return (-len(self.gaps), resisted)


def team_coverage(chart: TypeChart, members: Iterable[Pokemon]) -> Coverage:
    """Count, for each attack type, how many members are weak to it and how many resist it."""
    weak = dict.fromkeys(TYPES, 0)
    resist = dict.fromkeys(TYPES, 0)
    for pokemon in members:
        found = matchups(chart, pokemon.types)
        for attack in found.weak_to:
            weak[attack] += 1
        for attack in found.resists:
            resist[attack] += 1
    gaps = [attack for attack in TYPES if weak[attack] > 0 and resist[attack] == 0]
    return Coverage(weak, resist, gaps)


def best_team(chart: TypeChart, shortlist: list[Pokemon], size: int = 3) -> tuple[Pokemon, ...]:
    """The team of `size` Pokémon from the shortlist with the best coverage.

    It simply tries every possible team. itertools.combinations() hands them
    out one at a time, without making a list: 455 teams of 3 from 15.
    If two teams have the same score, the one found first wins.
    """
    # TODO 15
    # - If size is less than 1 or more than MAX_TEAM_SIZE, raise TeamError.
    # - If size is more than len(shortlist), raise TeamError too.
    # - Return the max() of combinations(shortlist, size), with
    #   key=lambda team: team_coverage(chart, team).score
    return tuple(shortlist[:size])   # placeholder: just the first few
