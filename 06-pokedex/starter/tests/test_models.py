"""Tests for Move, Pokemon and Team, using real PokéAPI answers saved in tests/fixtures/."""

import json

import pytest

from fakes import FIXTURES
from pokedex.errors import TeamError
from pokedex.models import STRUGGLE, Move, Pokemon, Team, level_up_moves


def saved_answer(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_move_from_api():
    move = Move.from_api(saved_answer("move-thunderbolt.json"))
    assert move == Move("thunderbolt", "electric", 90, 100, "special")
    assert move.display_name == "Thunderbolt"


def test_a_move_with_no_power():
    # The API says "power": null for a move like Transform. We store 0.
    move = Move.from_api(saved_answer("move-transform.json"))
    assert move.power == 0
    assert not move.is_attack


@pytest.mark.parametrize(
    "move, attack",
    [
        (Move("thunderbolt", "electric", 90, 100, "special"), True),
        (Move("tackle", "normal", 40, 100, "physical"), True),
        (Move("growl", "normal", 0, 100, "status"), False),
        (Move("explosion", "normal", 250, 100, "physical"), False),      # too strong
        (Move("outrage", "dragon", 120, 100, "physical"), True),         # exactly MAX_POWER is fine
    ],
)
def test_is_attack(move, attack):
    assert move.is_attack == attack


def test_struggle_never_misses():
    assert STRUGGLE.accuracy is None and STRUGGLE.is_attack


def test_pokemon_from_api():
    pikachu = Pokemon.from_api(saved_answer("pokemon-pikachu.json"))
    assert (pikachu.number, pikachu.name, pikachu.types) == (25, "pikachu", ("electric",))
    assert pikachu.stats == {"hp": 35, "attack": 55, "defense": 40,
                             "special-attack": 50, "special-defense": 50, "speed": 90}
    assert str(pikachu) == "#25 Pikachu (electric)"


def test_two_types_keep_their_order():
    assert Pokemon.from_api(saved_answer("pokemon-charizard.json")).types == ("fire", "flying")


def test_battle_stats_are_for_level_50():
    pikachu = Pokemon.from_api(saved_answer("pokemon-pikachu.json"))
    assert pikachu.battle_stat("hp") == 95
    assert pikachu.battle_stat("speed") == 95


def test_level_up_moves_latest_first():
    data = {"moves": [
        {"move": {"name": "tackle"}, "version_group_details": [
            {"level_learned_at": 1, "move_learn_method": {"name": "level-up"}}]},
        {"move": {"name": "surf"}, "version_group_details": [
            {"level_learned_at": 0, "move_learn_method": {"name": "machine"}}]},
        {"move": {"name": "thunder"}, "version_group_details": [
            {"level_learned_at": 44, "move_learn_method": {"name": "level-up"}},
            {"level_learned_at": 30, "move_learn_method": {"name": "level-up"}}]},
        {"move": {"name": "agility"}, "version_group_details": [
            {"level_learned_at": 1, "move_learn_method": {"name": "level-up"}}]},
        {"move": {"name": "spark"}, "version_group_details": [
            {"level_learned_at": 35, "move_learn_method": {"name": "level-up"}}]},
    ]}
    # surf is only taught by a machine, so it's left out. thunder counts as
    # level 44, its HIGHEST level, even though 30 comes after it, so it beats
    # spark (35). agility and tackle tie at level 1, so they go A to Z.
    assert level_up_moves(data) == ("thunder", "spark", "agility", "tackle")


def test_level_up_moves_from_a_real_answer():
    names = level_up_moves(saved_answer("pokemon-pikachu.json"))
    assert names[0] == "thunder"
    assert len(names) == len(set(names))       # no move twice


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def make(name):
    return Pokemon(1, name, ("normal",), {})


def test_a_team_works_with_len_for_and_in():
    team = Team("Red", [make("pikachu"), make("gengar")])
    assert len(team) == 2
    assert [pokemon.name for pokemon in team] == ["pikachu", "gengar"]
    assert "gengar" in team and "lapras" not in team
    assert str(team) == "Pikachu and Gengar"


def test_a_team_has_at_most_six():
    team = Team("Red", [make(name) for name in "abcdef"])
    with pytest.raises(TeamError, match="at most 6"):
        team.add(make("g"))
    assert len(team) == 6


def test_no_pokemon_twice():
    team = Team("Red", [make("pikachu")])
    with pytest.raises(TeamError, match="already"):
        team.add(make("pikachu"))


@pytest.mark.parametrize(
    "names, text",
    [([], ""), (["pikachu"], "Pikachu"), (["pikachu", "gengar", "lapras"], "Pikachu, Gengar and Lapras")],
)
def test_team_str(names, text):
    assert str(Team("Red", [make(name) for name in names])) == text
