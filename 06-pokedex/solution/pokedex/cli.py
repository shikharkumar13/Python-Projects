"""The commands you can type, and the code that runs them."""

from __future__ import annotations

import logging
import math
import random
from collections.abc import Callable
from itertools import islice
from pathlib import Path

import requests

from pokedex.battle import Battle
from pokedex.client import PROJECT_DIR, PokeClient
from pokedex.errors import PokedexError, TeamError, UsageError
from pokedex.models import STAT_NAMES, MAX_TEAM_SIZE, Pokemon, Team
from pokedex.teams import best_team, matchups, team_coverage
from pokedex.typechart import TYPES, TypeChart

logger = logging.getLogger(__name__)

SHORTLIST_FILE = PROJECT_DIR / "shortlist.txt"
LIST_LENGTH = 30        # how many names `list` shows, if you don't say
MAX_TEAMS = 1_000_000   # `best` refuses to try more teams than this. A million takes a few seconds

# Every command gets the client, and the words typed after the command's name.
CommandFunc = Callable[[PokeClient, list[str]], None]

COMMANDS: dict[str, CommandFunc] = {}


def command(name: str) -> Callable[[CommandFunc], CommandFunc]:
    """A decorator factory, like retry(): @command("list") registers a function as the `list` command.

    The name is given separately, because the function can't be called
    list(): that would hide Python's own list().
    """
    def register(func: CommandFunc) -> CommandFunc:
        COMMANDS[name] = func
        return func
    return register


def multiplier_text(value: float) -> str:
    """2.0 gives "x2", 0.25 gives "x0.25"."""
    return f"x{value:g}"


def whole_number(text: str, what: str) -> int:
    """Turn what the user typed into a whole number, or explain what went wrong."""
    # isdecimal(), not isdigit(): "²".isdigit() is True, but int("²") fails.
    if not text.isdecimal():
        raise UsageError(f"The {what} should be a whole number, like 3, not {text!r}.")
    if len(text) > 6:
        raise UsageError(f"{text} is far too big for the {what}.")
    return int(text)


def read_shortlist(path: Path) -> list[str]:
    """The names in the shortlist file: one per line, skipping blank lines and # comments."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        raise PokedexError(f"Can't find {path.name}. Make it, with one Pokémon name on each line.")
    except UnicodeDecodeError:
        raise PokedexError(f"{path.name} isn't saved as UTF-8. Open it, choose Save As, and pick UTF-8.")
    except OSError as error:
        raise PokedexError(f"Can't read {path.name}: {error.strerror}.")
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def print_coverage(chart: TypeChart, team: Team) -> None:
    """A table of how many team members are weak to, and resist, each attack type."""
    coverage = team_coverage(chart, team)
    print(f"{team.name}: {team}")
    print()
    print("Attack type   Weak  Resist")
    for attack in TYPES:
        note = "   <- a gap" if attack in coverage.gaps else ""
        print(f"{attack:<12}{coverage.weak[attack]:>6}{coverage.resist[attack]:>8}{note}")
    print()
    resisted = coverage.score[1]
    print(f"Someone on the team resists {resisted} of the {len(TYPES)} attack types.")
    if coverage.gaps:
        print(f"Gaps: {', '.join(coverage.gaps)}. They hit someone hard, and nobody resists them.")
    else:
        print("No gaps: every type that hits someone hard is resisted by someone else.")


def team_from(client: PokeClient, name: str, names: list[str]) -> Team:
    """Look up each Pokémon and put them in a team."""
    if not names:
        raise UsageError(f"{name} needs at least one Pokémon.")
    if len(names) > MAX_TEAM_SIZE:
        raise TeamError(f"That's {len(names)} Pokémon. A team can have at most {MAX_TEAM_SIZE}.")
    return Team(name, [client.get_pokemon(each) for each in names])


# ---------------------------------------------------------------------------
# The commands. The first line of each docstring is shown in the help.
# ---------------------------------------------------------------------------

@command("show")
def show(client: PokeClient, args: list[str]) -> None:
    """show pikachu                        a Pokémon's stats, weaknesses and battle moves"""
    if not args:
        raise UsageError("Which Pokémon? Try: python -m pokedex show pikachu")
    pokemon = client.get_pokemon(" ".join(args))      # so "show mr mime" works too
    chart = client.get_type_chart()

    print(pokemon)
    print()
    for stat in STAT_NAMES:
        value = pokemon.stats[stat]
        print(f"  {stat:<16}{value:>4}  {'█' * (value // 10)}")
    print()
    found = matchups(chart, pokemon.types)
    weak = [f"{attack} {multiplier_text(chart.multiplier(attack, pokemon.types))}"
            for attack in TYPES if attack in found.weak_to]
    resists = [f"{attack} {multiplier_text(chart.multiplier(attack, pokemon.types))}"
               for attack in TYPES if attack in found.resists]
    print(f"  Weak to:  {', '.join(weak) or 'nothing'}")
    print(f"  Resists:  {', '.join(resists) or 'nothing'}")
    print()
    print("  Battle moves:")
    for move in client.get_battle_moves(pokemon):
        accuracy = "never misses" if move.accuracy is None else f"{move.accuracy}% accurate"
        print(f"    {move.display_name:<16}{move.type:<10}power {move.power:>3}, {accuracy}")


@command("list")
def list_names(client: PokeClient, args: list[str]) -> None:
    """list 50                             the first 50 Pokémon names (30 if you don't say)"""
    if len(args) > 1:
        raise UsageError("Just one number after list, like: python -m pokedex list 50")
    how_many = whole_number(args[0], "number of names") if args else LIST_LENGTH
    if how_many == 0:
        raise UsageError("Ask for at least 1 name, like: python -m pokedex list 50")
    # islice() stops the generator after how_many names, so no extra pages are fetched.
    for number, name in enumerate(islice(client.iter_pokemon(), how_many), start=1):
        print(f"{number:>5}  {name}")


@command("team")
def team(client: PokeClient, args: list[str]) -> None:
    """team pikachu gengar lapras          how well up to 6 Pokémon cover each other"""
    print_coverage(client.get_type_chart(), team_from(client, "Your team", args))


@command("best")
def best(client: PokeClient, args: list[str]) -> None:
    """best 3                              the best team of 3 from shortlist.txt"""
    if len(args) > 1:
        raise UsageError("Just one number after best, like: python -m pokedex best 3")
    size = whole_number(args[0], "team size") if args else 3
    shortlist: list[Pokemon] = []
    for name in read_shortlist(SHORTLIST_FILE):
        pokemon = client.get_pokemon(name)
        if pokemon.name in [each.name for each in shortlist]:
            print(f"{pokemon.display_name} is in {SHORTLIST_FILE.name} more than once, so it only counts once.")
        else:
            shortlist.append(pokemon)
    chart = client.get_type_chart()

    # Count first, the way chapter 15 does: 15 Pokémon in teams of 6 would
    # be 5,005 teams, and 50 in teams of 6 would be nearly 16 million.
    teams = math.comb(len(shortlist), size)
    if teams > MAX_TEAMS:
        raise TeamError(f"{len(shortlist)} Pokémon in teams of {size} makes {teams:,} teams. "
                        f"That would take too long, so try a shorter shortlist or a smaller team.")
    possible = "is 1 possible team" if teams == 1 else f"are {teams:,} possible teams"
    print(f"{len(shortlist)} Pokémon in {SHORTLIST_FILE.name}, so there {possible} of {size}. Trying them all...")
    print()
    matchups.cache_clear()
    winners = best_team(chart, shortlist, size)
    info = matchups.cache_info()

    print_coverage(chart, Team("Best team", winners))
    print()
    print(f"matchups() was asked {info.hits + info.misses:,} times, but only worked something out "
          f"{info.misses} times. lru_cache remembered the other {info.hits:,} answers.")


@command("battle")
def battle(client: PokeClient, args: list[str]) -> None:
    """battle pikachu,gengar lapras 42     two teams fight. The same seed replays the same battle"""
    if any(arg.startswith(",") or arg.endswith(",") for arg in args):
        # "pikachu, gengar" arrives as two words: "pikachu," and "gengar".
        raise UsageError("Leave out the spaces after the commas, like this:\n"
                         "  python -m pokedex battle pikachu,gengar lapras,golem 42")
    if len(args) not in (2, 3):
        raise UsageError("Give two teams, with commas between the names, and a seed if you like:\n"
                         "  python -m pokedex battle pikachu,gengar lapras,golem 42")
    chose_seed = len(args) == 3
    seed = whole_number(args[2], "seed") if chose_seed else random.randint(1, 9999)

    red = team_from(client, "Red", [name for name in args[0].split(",") if name.strip()])
    blue = team_from(client, "Blue", [name for name in args[1].split(",") if name.strip()])
    chart = client.get_type_chart()
    moves = {pokemon.name: client.get_battle_moves(pokemon) for pokemon in [*red, *blue]}

    print(f"Red:  {red}")
    print(f"Blue: {blue}")
    print(f"Seed: {seed}")
    print()
    result = Battle(chart, red, blue, moves, seed).run()
    for line in result.log:
        print(line)
    print()
    if result.winner is None:
        print(f"It's a draw: nobody won in {result.turns} turns.")
    else:
        print(f"{result.winner} wins after {result.turns} turns!")
    if not chose_seed:
        print(f"To watch this exact battle again: python -m pokedex battle {args[0]} {args[1]} {seed}")


# ---------------------------------------------------------------------------

def usage() -> str:
    lines = ["Usage: python -m pokedex <command>", ""]
    for func in COMMANDS.values():
        lines.append("  " + (func.__doc__ or "").splitlines()[0])
    lines += ["", "Answers from PokéAPI are saved in cache/, so asking again costs no requests."]
    return "\n".join(lines)


def main(argv: list[str], client: PokeClient | None = None) -> int:
    """Run one command. Returns the exit code: 0 for OK, 1 for a problem, 2 for a typo.

    Tests pass in their own client, which reads saved answers and never
    touches the internet.
    """
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(usage())
        return 0
    name, args = argv[0], argv[1:]
    if name not in COMMANDS:
        print(f"There's no command called {name!r}.")
        print()
        print(usage())
        return 2

    if client is None:
        client = PokeClient()
    with client:
        try:
            COMMANDS[name](client, args)
        except UsageError as error:
            print(error)
            return 2
        except PokedexError as error:
            print(error)
            return 1
        except requests.ConnectionError:
            print("Couldn't connect to PokéAPI. Are you online? "
                  "Pokémon that are already in cache/ work without the internet.")
            return 1
        except requests.Timeout:
            print("PokéAPI didn't answer in time, even after 3 tries. Try again in a minute.")
            return 1
        except requests.RequestException as error:
            logger.exception("Request failed")
            print(f"Something went wrong talking to PokéAPI: {error}")
            return 1

    print()
    print(f"(PokéAPI requests: {client.requests_made}. Answers from the cache: {client.from_cache}.)")
    return 0
