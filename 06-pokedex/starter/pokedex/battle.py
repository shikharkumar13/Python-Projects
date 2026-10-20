"""A turn-based battle between two teams.

All the luck (misses, damage rolls, speed ties) comes from one
random.Random(seed). The same seed gives exactly the same battle, every time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from pokedex.errors import PokedexError
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
    # TODO 16
    # - multiplier = chart.multiplier(move.type, defender.pokemon.types). If it's 0, return 0.
    # - For a "physical" move, use the attacker's battle_stat("attack") and the
    #   defender's battle_stat("defense"). Otherwise, "special-attack" and
    #   "special-defense".
    # - amount = (2 * LEVEL / 5 + 2) * move.power * attack / defence / 50 + 2
    # - If move.type is one of the attacker's types, multiply amount by STAB.
    # - Return max(1, int(amount * multiplier * roll)).
    return 10   # placeholder: every attack does 10 damage


def choose_move(chart: TypeChart, attacker: Fighter, defender: Fighter) -> Move:
    """Pick the move that does the most damage on average, counting the chance of a miss.

    If none of its moves can hurt the defender at all, it uses Struggle.
    """
    # TODO 17
    # - Inside this function, write a small function average(move) that returns
    #   damage(chart, attacker, defender, move, roll=1.0) times the chance of
    #   hitting: 1.0 if move.accuracy is None, otherwise move.accuracy / 100.
    # - best = max(attacker.moves, key=average)
    # - If average(best) is 0, return STRUGGLE. Otherwise, return best.
    return attacker.moves[0]   # placeholder: always the first move


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
        # TODO 18
        # - move = choose_move(self.chart, attacker, defender)
        # - If the move has an accuracy, and self.random.randint(1, 100) is more than
        #   it, it missed: log "  Red's Pikachu used Thunder, but it missed!" and return.
        # - amount = damage(...), with self.random.uniform(0.85, 1.0) as the roll.
        #   Then defender.take_damage(amount).
        # - Build the log line: "  Red's Pikachu used Thunderbolt!", then, using
        #   multiplier = self.chart.multiplier(move.type, defender.pokemon.types),
        #   " It's super effective!" if the multiplier is more than 1, or
        #   " It's not very effective..." if it's less than 1, then
        #   " Blue's Blastoise lost 65 HP (74/139 left)." Append it to self.log.
        # - If the defender fainted, log "  Blue's Blastoise fainted!" too.
        # Use attacker.name and defender.name: they give "Red's Pikachu".
        # Use self.random, never the random module, or the seed won't work.
        raise PokedexError("Attacking is TODO 18.")   # placeholder: replace this line

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
