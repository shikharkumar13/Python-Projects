"""The type chart: how much damage each type of attack does to each type of Pokémon."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

# The 18 types, in the games' usual order.
TYPES = (
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel", "fairy",
)

# What each list in PokéAPI's "damage_relations" means for the attacker.
RELATIONS = {"double_damage_to": 2.0, "half_damage_to": 0.5, "no_damage_to": 0.0}


class TypeChart:
    """How strong each type of attack is against each type.

        chart.multiplier("fire", ("grass",))            2.0   super effective
        chart.multiplier("fire", ("water",))            0.5   not very effective
        chart.multiplier("electric", ("ground",))       0.0   no effect at all
        chart.multiplier("ice", ("dragon", "flying"))   4.0   2 x 2, for two types
    """

    def __init__(self, table: dict[str, dict[str, float]]) -> None:
        # table["fire"]["grass"] is 2.0. A pair that isn't in the table does
        # normal damage, 1.0, so the table only has to hold the exceptions.
        self.table = table

    @classmethod
    def from_api(cls, answers: Iterable[dict[str, Any]]) -> TypeChart:
        """Build the chart from PokéAPI's answers for /type/{name}, one per type."""
        # TODO 12
        # - table = {}
        # - For each `data` in answers, make a row: an empty dictionary.
        #   For each relation and multiplier in RELATIONS.items(), loop over
        #   data["damage_relations"][relation], and set row[target["name"]] = multiplier.
        # - Store the row as table[data["name"]].
        # - Return cls(table).
        return cls({})   # placeholder: an empty chart, so every attack does normal damage

    def multiplier(self, attack_type: str, defender_types: Iterable[str]) -> float:
        """How many times normal damage an attack does. For two types, multiply them."""
        # TODO 13
        # - row = self.table.get(attack_type, {})
        # - Start with result = 1.0, and multiply it by row.get(defender, 1.0) for
        #   each of the defender's types.
        # - Return result.
        return 1.0   # placeholder: replace this line
