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
        table: dict[str, dict[str, float]] = {}
        for data in answers:
            row: dict[str, float] = {}
            for relation, multiplier in RELATIONS.items():
                for target in data["damage_relations"][relation]:
                    row[target["name"]] = multiplier
            table[data["name"]] = row
        return cls(table)

    def multiplier(self, attack_type: str, defender_types: Iterable[str]) -> float:
        """How many times normal damage an attack does. For two types, multiply them."""
        row = self.table.get(attack_type, {})     # an unknown attack type does normal damage
        result = 1.0
        for defender in defender_types:
            result *= row.get(defender, 1.0)
        return result
