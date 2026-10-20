"""Tests for the type chart, built from the 18 /type answers saved in tests/fixtures/."""

import pytest

from pokedex.typechart import TYPES, TypeChart


@pytest.mark.parametrize(
    "attack, defender, multiplier",
    [
        ("fire", ("grass",), 2.0),
        ("water", ("fire",), 2.0),
        ("fire", ("water",), 0.5),
        ("normal", ("normal",), 1.0),
        ("electric", ("ground",), 0.0),          # no effect at all
        ("ghost", ("normal",), 0.0),
        ("ice", ("dragon", "flying"), 4.0),      # 2 x 2
        ("fire", ("water", "grass"), 1.0),       # 0.5 x 2
        ("bug", ("fire", "flying"), 0.25),       # 0.5 x 0.5
        ("ground", ("flying", "electric"), 0.0), # 0 x anything is 0
    ],
)
def test_multiplier(chart, attack, defender, multiplier):
    assert chart.multiplier(attack, defender) == multiplier


def test_every_type_is_in_the_chart(chart):
    assert sorted(chart.table) == sorted(TYPES)


def test_an_unknown_attack_type_does_normal_damage(chart):
    assert chart.multiplier("typeless", ("ghost",)) == 1.0


def test_from_api_with_a_tiny_chart():
    answers = [{"name": "fire", "damage_relations": {
        "double_damage_to": [{"name": "grass"}],
        "half_damage_to": [{"name": "water"}],
        "no_damage_to": [],
        "double_damage_from": [{"name": "water"}],   # "_from" lists are about defending, so they're ignored
        "half_damage_from": [],
        "no_damage_from": [],
    }}]
    assert TypeChart.from_api(answers).table == {"fire": {"grass": 2.0, "water": 0.5}}
