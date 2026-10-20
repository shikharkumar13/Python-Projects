"""Tests for the battle simulator, with real Pokémon from tests/fixtures/."""

import pytest

from pokedex.battle import Battle, Fighter, choose_move, damage
from pokedex.models import STRUGGLE, Move, Team

THUNDERBOLT = Move("thunderbolt", "electric", 90, 100, "special")
TACKLE = Move("tackle", "normal", 40, 100, "physical")
SHADOW_BALL = Move("shadow-ball", "ghost", 80, 100, "special")


@pytest.fixture
def fighter(saved):
    """fighter("pikachu", [moves]) makes a Fighter from a saved Pokémon."""
    def make(name, moves=(), team="Red"):
        return Fighter(team, saved.get_pokemon(name), list(moves))
    return make


def test_a_fighter_starts_with_full_hp(fighter):
    pikachu = fighter("pikachu")
    assert pikachu.hp == pikachu.max_hp == 95
    assert pikachu.name == "Red's Pikachu"
    assert pikachu.moves == [STRUGGLE]          # no moves given, so it can only Struggle


def test_hp_never_goes_below_zero(fighter):
    pikachu = fighter("pikachu")
    pikachu.take_damage(500)
    assert pikachu.hp == 0 and pikachu.fainted


def test_damage_worked_out_by_hand(chart, fighter):
    # Pikachu's Special Attack is 50 + 5 = 55, and Blastoise's Special Defense is 105 + 5 = 110.
    #   22 x 90 x 55 / 110 / 50 + 2  =  21.8
    #   x 1.5, because Pikachu is electric too (STAB)  =  32.7
    #   x 2, because electric is super effective on water  =  65.4, rounded down to 65
    assert damage(chart, fighter("pikachu"), fighter("blastoise"), THUNDERBOLT, roll=1.0) == 65


def test_damage_with_a_low_roll(chart, fighter):
    assert damage(chart, fighter("pikachu"), fighter("blastoise"), THUNDERBOLT, roll=0.85) == 55


def test_damage_when_it_has_no_effect(chart, fighter):
    assert damage(chart, fighter("snorlax"), fighter("gengar"), TACKLE, roll=1.0) == 0


def test_damage_is_at_least_1(chart, fighter):
    # A power-1 bug move against Charizard, who takes x0.25 from bug moves:
    # about 2.1 x 0.25 x 0.85 = 0.44, which int() would round down to 0.
    weak = Move("weak", "bug", 1, 100, "physical")
    assert damage(chart, fighter("magikarp"), fighter("charizard"), weak, roll=0.85) == 1


def test_choose_move_picks_the_strongest(chart, fighter):
    pikachu = fighter("pikachu", [TACKLE, THUNDERBOLT])
    assert choose_move(chart, pikachu, fighter("blastoise")) == THUNDERBOLT


def test_choose_move_counts_misses(chart, fighter):
    sure = Move("sure", "electric", 80, 100, "special")
    risky = Move("risky", "electric", 90, 50, "special")     # stronger, but misses half the time
    assert choose_move(chart, fighter("pikachu", [risky, sure]), fighter("blastoise")) == sure


def test_choose_move_struggles_when_nothing_works(chart, fighter):
    snorlax = fighter("snorlax", [TACKLE])            # normal moves can't touch a ghost
    assert choose_move(chart, snorlax, fighter("gengar")) == STRUGGLE


def battle(saved, chart, red_names, blue_names, seed):
    red = Team("Red", [saved.get_pokemon(name) for name in red_names])
    blue = Team("Blue", [saved.get_pokemon(name) for name in blue_names])
    moves = {pokemon.name: saved.get_battle_moves(pokemon) for pokemon in [*red, *blue]}
    return Battle(chart, red, blue, moves, seed).run()


def test_the_same_seed_replays_the_same_battle(saved, chart):
    first = battle(saved, chart, ["pikachu", "charizard"], ["blastoise", "venusaur"], seed=7)
    again = battle(saved, chart, ["pikachu", "charizard"], ["blastoise", "venusaur"], seed=7)
    assert first == again


def test_different_seeds_can_change_the_battle(saved, chart):
    logs = {tuple(battle(saved, chart, ["pikachu"], ["charizard"], seed).log) for seed in range(20)}
    assert len(logs) > 1


def test_a_battle_ends_with_a_winner(saved, chart):
    result = battle(saved, chart, ["pikachu", "charizard", "blastoise"], ["venusaur", "gengar", "snorlax"], seed=1)
    assert result.winner in ("Red", "Blue")
    assert 0 < result.turns < 100
    assert result.log[0] == "Red sends out Pikachu!"
    assert any("fainted!" in line for line in result.log)


def test_the_faster_pokemon_attacks_first(saved, chart):
    # Pikachu (speed 90) is much faster than Snorlax (speed 30).
    result = battle(saved, chart, ["snorlax"], ["pikachu"], seed=3)
    assert result.log[2].startswith("  Blue's Pikachu used")


def test_type_advantage_usually_wins(saved, chart):
    # Blastoise's water moves are super effective on Charizard.
    wins = sum(battle(saved, chart, ["blastoise"], ["charizard"], seed).winner == "Red" for seed in range(30))
    assert wins >= 25


def test_moves_can_miss(saved, chart):
    zap = Move("zap", "electric", 90, 10, "special")      # hits only 1 time in 10
    red = Team("Red", [saved.get_pokemon("pikachu")])
    blue = Team("Blue", [saved.get_pokemon("blastoise")])
    result = Battle(chart, red, blue, {"pikachu": [zap], "blastoise": [TACKLE]}, seed=4).run()
    assert "  Red's Pikachu used Zap, but it missed!" in result.log


def test_ditto_can_still_fight(saved, chart):
    # Ditto's only move is Transform, which does no damage, so it uses Struggle.
    result = battle(saved, chart, ["ditto"], ["magikarp"], seed=5)
    assert result.winner is not None
    assert any("Red's Ditto used Struggle!" in line for line in result.log)


def test_super_effective_is_in_the_log(saved, chart):
    result = battle(saved, chart, ["pikachu"], ["blastoise"], seed=2)
    assert any("Red's Pikachu used" in line and "super effective" in line for line in result.log)
