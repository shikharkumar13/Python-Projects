"""A turn-based battle between two teams.

All the luck (misses, damage rolls, speed ties) comes from one
random.Random(seed). The same seed gives exactly the same battle, every time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from pokedex.models import STRUGGLE, Move, Pokemon, Team
from pokedex.typechart import TypeChart

LEVEL = 50          # every Pokémon fights at level 50
STAB = 1.5          # "same-type attack bonus": a fire Pokémon's fire moves hit harder
MAX_TURNS = 500     # a safety net. Every battle should end long before this


class Fighter:
    """A Pokémon in a battle: which team it's on, its moves, and the HP it has left."""

    def __init__(self, team: str, pokemon: Pokemon, moves: list[Move]) -> None:
        self.team = team
        self.pokemon = pokemon
        self.moves = moves or [STRUGGLE]
        self.max_hp = pokemon.battle_stat("hp")
        self.hp = self.max_hp

    @property
    def name(self) -> str:
        """Like "Red's Pikachu", so you can tell two Pikachus apart."""
        return f"{self.team}'s {self.pokemon.display_name}"

    @property
    def fainted(self) -> bool:
        return self.hp == 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)


def damage(chart: TypeChart, attacker: Fighter, defender: Fighter, move: Move, roll: float) -> int:
    """How much HP a move takes off the defender. A simpler version of the games' formula.

    `roll` is a random number from 0.85 to 1.0, so the same attack doesn't
    always do exactly the same damage. Pass roll=1.0 for the most it can do.
    """
    multiplier = chart.multiplier(move.type, defender.pokemon.types)
    if multiplier == 0:
        return 0
    # Physical moves (punches, bites) use Attack against Defense. Special
    # moves (beams, flames) use Special Attack against Special Defense.
    if move.damage_class == "physical":
        attack = attacker.pokemon.battle_stat("attack")
        defence = defender.pokemon.battle_stat("defense")
    else:
        attack = attacker.pokemon.battle_stat("special-attack")
        defence = defender.pokemon.battle_stat("special-defense")

    amount = (2 * LEVEL / 5 + 2) * move.power * attack / defence / 50 + 2
    if move.type in attacker.pokemon.types:
        amount *= STAB
    return max(1, int(amount * multiplier * roll))     # a hit always does at least 1


def choose_move(chart: TypeChart, attacker: Fighter, defender: Fighter) -> Move:
    """Pick the move that does the most damage on average, counting the chance of a miss.

    If none of its moves can hurt the defender at all, it uses Struggle.
    """
    def average(move: Move) -> float:
        hit_chance = 1.0 if move.accuracy is None else move.accuracy / 100
        return damage(chart, attacker, defender, move, roll=1.0) * hit_chance

    best = max(attacker.moves, key=average)
    if average(best) == 0:
        return STRUGGLE
    return best


@dataclass
class BattleResult:
    winner: str | None      # the winning team's name, or None for a draw
    turns: int
    log: list[str]          # what happened, one line at a time


class Battle:
    """Two teams fight, one Pokémon each at a time, until one team has nobody left."""

    def __init__(self, chart: TypeChart, first: Team, second: Team, moves: dict[str, list[Move]], seed: int) -> None:
        self.chart = chart
        self.random = random.Random(seed)
        self.sides = [
            (first.name, [Fighter(first.name, pokemon, moves.get(pokemon.name, [])) for pokemon in first]),
            (second.name, [Fighter(second.name, pokemon, moves.get(pokemon.name, [])) for pokemon in second]),
        ]
        self.log: list[str] = []

    def send_out(self, team: str, fighters: list[Fighter]) -> Fighter | None:
        """The team's next Pokémon that hasn't fainted, or None if there's nobody left."""
        for fighter in fighters:
            if not fighter.fainted:
                self.log.append(f"{team} sends out {fighter.pokemon.display_name}!")
                return fighter
        return None

    def attack(self, attacker: Fighter, defender: Fighter) -> None:
        """One attack: choose a move, see if it hits, take off the damage, and log it all."""
        move = choose_move(self.chart, attacker, defender)
        if move.accuracy is not None and self.random.randint(1, 100) > move.accuracy:
            self.log.append(f"  {attacker.name} used {move.display_name}, but it missed!")
            return

        amount = damage(self.chart, attacker, defender, move, self.random.uniform(0.85, 1.0))
        defender.take_damage(amount)

        line = f"  {attacker.name} used {move.display_name}!"
        multiplier = self.chart.multiplier(move.type, defender.pokemon.types)
        if multiplier > 1:
            line += " It's super effective!"
        elif multiplier < 1:
            line += " It's not very effective..."
        line += f" {defender.name} lost {amount} HP ({defender.hp}/{defender.max_hp} left)."
        self.log.append(line)
        if defender.fainted:
            self.log.append(f"  {defender.name} fainted!")

    def take_turn(self, one: Fighter, other: Fighter) -> None:
        """Both Pokémon attack, the faster one first. One that faints doesn't get its attack."""
        one_speed = one.pokemon.battle_stat("speed")
        other_speed = other.pokemon.battle_stat("speed")
        if one_speed > other_speed or (one_speed == other_speed and self.random.random() < 0.5):
            first, second = one, other
        else:
            first, second = other, one
        self.attack(first, second)
        if not second.fainted:
            self.attack(second, first)

    def run(self) -> BattleResult:
        """Fight until one team has nobody left, and say who won."""
        (first_name, first_team), (second_name, second_team) = self.sides
        first = self.send_out(first_name, first_team)
        second = self.send_out(second_name, second_team)
        turns = 0
        while first is not None and second is not None and turns < MAX_TURNS:
            turns += 1
            self.take_turn(first, second)
            if first.fainted:
                first = self.send_out(first_name, first_team)
            if second.fainted:
                second = self.send_out(second_name, second_team)

        if first is not None and second is None:
            winner: str | None = first_name
        elif second is not None and first is None:
            winner = second_name
        else:
            winner = None       # nobody won before MAX_TURNS
        return BattleResult(winner, turns, self.log)
