"""Tests for type coverage and the best-team search."""

from math import comb

import pytest

from pokedex.errors import TeamError
from pokedex.models import Pokemon
from pokedex.teams import best_team, matchups, team_coverage


def make(name, *types):
    return Pokemon(1, name, types, {})


def test_matchups(chart):
    found = matchups(chart, ("electric",))
    assert found.weak_to == {"ground"}
    assert found.resists == {"electric", "flying", "steel"}


def test_matchups_counts_immunity_as_resisting(chart):
    assert "ground" in matchups(chart, ("flying",)).resists       # 0 x damage


def test_matchups_for_two_types(chart):
    found = matchups(chart, ("grass", "poison"))    # Venusaur
    assert found.weak_to == {"fire", "ice", "flying", "psychic"}
    assert "grass" in found.resists


def test_matchups_is_cached(chart):
    matchups.cache_clear()
    for _ in range(5):
        matchups(chart, ("fire", "flying"))
    info = matchups.cache_info()
    assert (info.hits, info.misses) == (4, 1)


def test_matchups_needs_a_tuple(chart):
    # lru_cache can't store a list as a key, because a list can change.
    with pytest.raises(TypeError):
        matchups(chart, ["fire"])


def test_team_coverage(chart):
    coverage = team_coverage(chart, [make("pikachu", "electric"), make("golem", "rock", "ground")])
    assert coverage.weak["ground"] == 2         # both are weak to ground
    assert coverage.resist["electric"] == 2     # Pikachu resists it, and Golem is immune
    assert "ground" in coverage.gaps            # weak, and nobody resists it
    assert "water" in coverage.gaps


def test_a_team_with_no_gaps(chart):
    team = [make("lapras", "water", "ice"), make("venusaur", "grass", "poison"), make("charizard", "fire", "flying")]
    coverage = team_coverage(chart, team)
    assert "ice" not in coverage.gaps           # Charizard is weak to ice, but Lapras resists it


def test_best_team_tries_every_combination(chart):
    shortlist = [make("a", "grass"), make("b", "fire"), make("c", "water"), make("d", "normal")]
    assert comb(len(shortlist), 3) == 4
    # Grass, fire and water each resist what the other two are weak to.
    assert [pokemon.name for pokemon in best_team(chart, shortlist, 3)] == ["a", "b", "c"]


def test_fewer_gaps_beats_more_resistances(chart):
    # Steelix resists 10 types, but has 4 gaps (fire, water, fighting, ground).
    # Pikachu only resists 3, but has just 1 gap (ground). Fewer gaps wins.
    shortlist = [make("steelix", "steel", "ground"), make("pikachu", "electric")]
    assert best_team(chart, shortlist, 1)[0].name == "pikachu"


@pytest.mark.parametrize("size", [0, 7, 3])
def test_best_team_bad_sizes(chart, size):
    with pytest.raises(TeamError):
        best_team(chart, [make("a", "fire"), make("b", "water")], size)
