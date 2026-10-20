"""Tests for the commands, run through main() just like the real program.

main() lets us hand it a client, so these use `saved` (or a FakeSession)
and never touch the internet.
"""

import pytest
import requests

import pokedex.cli
from fakes import FIXTURES, FakeResponse, FakeSession
from pokedex.cli import COMMANDS, main
from pokedex.client import PokeClient


def test_every_command_is_registered():
    assert list(COMMANDS) == ["show", "list", "team", "best", "battle"]


def test_show(saved, capsys):
    assert main(["show", "pikachu"], saved) == 0
    out = capsys.readouterr().out
    assert "#25 Pikachu (electric)" in out
    assert "Weak to:  ground x2" in out
    assert "Thunderbolt" in out
    assert "(PokéAPI requests: 0." in out


def test_show_two_words(saved, capsys):
    assert main(["show", "Pikachu", ""], saved) == 0        # extra spaces don't matter


def test_show_a_four_times_weakness(saved, capsys):
    assert main(["show", "charizard"], saved) == 0
    assert "rock x4" in capsys.readouterr().out


def test_list(saved, capsys):
    assert main(["list", "25"], saved) == 0
    out = capsys.readouterr().out
    assert "   25  pikachu" in out and "   26" not in out


def test_team(saved, capsys):
    assert main(["team", "pikachu", "charizard", "gengar"], saved) == 0
    out = capsys.readouterr().out
    assert "Your team: Pikachu, Charizard and Gengar" in out
    assert "Gaps: water, psychic, rock, ghost, dark." in out


def test_best(saved, capsys, tmp_path, monkeypatch):
    shortlist = tmp_path / "shortlist.txt"
    shortlist.write_text("# my favourites\npikachu\ncharizard\n\nblastoise\nvenusaur\ngengar\n", encoding="utf-8")
    monkeypatch.setattr(pokedex.cli, "SHORTLIST_FILE", shortlist)
    assert main(["best", "2"], saved) == 0
    out = capsys.readouterr().out
    assert "5 Pokémon in shortlist.txt, so there are 10 possible teams of 2" in out
    assert "Best team:" in out and "lru_cache remembered" in out


def test_battle_with_a_seed_is_the_same_every_time(saved, capsys):
    assert main(["battle", "pikachu,charizard", "blastoise,venusaur", "7"], saved) == 0
    first = capsys.readouterr().out
    assert main(["battle", "pikachu,charizard", "blastoise,venusaur", "7"], saved) == 0
    again = capsys.readouterr().out
    # Everything up to the request counts at the bottom is the same.
    assert again.split("(PokéAPI")[0] == first.split("(PokéAPI")[0]
    assert "Seed: 7" in first and "wins after" in first
    assert "To watch this exact battle again" not in first


def test_battle_without_a_seed_says_how_to_replay_it(saved, capsys):
    assert main(["battle", "pikachu", "blastoise"], saved) == 0
    assert "To watch this exact battle again: python -m pokedex battle pikachu blastoise" in capsys.readouterr().out


@pytest.mark.parametrize(
    "argv, code, words",
    [
        (["show"], 2, "Which Pokémon?"),
        (["show", "../secret"], 1, "no Pokémon called"),
        (["list", "lots"], 2, "whole number"),
        (["list", "5", "6"], 2, "Just one number"),
        (["team"], 2, "needs at least one"),
        (["team", "pikachu", "pikachu"], 1, "already on Your team"),
        (["team", "a", "b", "c", "d", "e", "f", "g"], 1, "at most 6"),
        (["best", "three"], 2, "whole number"),
        (["battle", "pikachu"], 2, "Give two teams"),
        (["battle", "pikachu", "gengar", "seven"], 2, "whole number"),
        (["battle", "", "gengar"], 2, "Red needs at least one"),
        (["battle", "pikachu,", "gengar", "lapras"], 2, "Leave out the spaces after the commas"),
        (["list", "²"], 2, "whole number"),            # "²".isdigit() is True, but int("²") fails
        (["list", "-1"], 2, "whole number"),
        (["list", "0"], 2, "at least 1"),
        (["list", "99999999999999999999"], 2, "far too big"),
        (["battle", "pikachu", "gengar", "²"], 2, "whole number"),
        (["fight"], 2, "no command called 'fight'"),
    ],
)
def test_mistakes(saved, capsys, argv, code, words):
    assert main(argv, saved) == code
    assert words in capsys.readouterr().out


def test_help(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "Usage" in out and "battle pikachu,gengar" in out


def test_best_with_no_shortlist(saved, capsys, tmp_path, monkeypatch):
    monkeypatch.setattr(pokedex.cli, "SHORTLIST_FILE", tmp_path / "nope.txt")
    assert main(["best"], saved) == 1
    assert "Can't find nope.txt" in capsys.readouterr().out


def test_best_counts_a_pokemon_only_once(saved, capsys, tmp_path, monkeypatch):
    shortlist = tmp_path / "shortlist.txt"
    shortlist.write_text("pikachu\nPikachu\ngengar\nvenusaur\n", encoding="utf-8")
    monkeypatch.setattr(pokedex.cli, "SHORTLIST_FILE", shortlist)
    assert main(["best", "3"], saved) == 0
    out = capsys.readouterr().out
    assert "Pikachu is in shortlist.txt more than once" in out
    assert "3 Pokémon in shortlist.txt, so there is 1 possible team of 3" in out


def test_best_refuses_far_too_many_teams(saved, capsys, tmp_path, monkeypatch):
    shortlist = tmp_path / "shortlist.txt"
    shortlist.write_text("pikachu\ncharizard\nblastoise\nvenusaur\ngengar\n", encoding="utf-8")
    monkeypatch.setattr(pokedex.cli, "SHORTLIST_FILE", shortlist)
    monkeypatch.setattr(pokedex.cli, "MAX_TEAMS", 5)     # 5 Pokémon in pairs is 10 teams
    assert main(["best", "2"], saved) == 1
    assert "makes 10 teams. That would take too long" in capsys.readouterr().out


def test_best_with_a_shortlist_that_is_not_utf8(saved, capsys, tmp_path, monkeypatch):
    # Old versions of Notepad save as "ANSI", where é is one byte that isn't UTF-8.
    shortlist = tmp_path / "shortlist.txt"
    shortlist.write_bytes("# my Pokémon\npikachu\ngengar\n".encode("cp1252"))
    monkeypatch.setattr(pokedex.cli, "SHORTLIST_FILE", shortlist)
    assert main(["best", "2"], saved) == 1
    assert "isn't saved as UTF-8" in capsys.readouterr().out


def test_best_with_too_few_in_the_shortlist(saved, capsys, tmp_path, monkeypatch):
    shortlist = tmp_path / "shortlist.txt"
    shortlist.write_text("pikachu\ngengar\n", encoding="utf-8")
    monkeypatch.setattr(pokedex.cli, "SHORTLIST_FILE", shortlist)
    assert main(["best", "3"], saved) == 1
    assert "only has 2" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# When the internet goes wrong
# ---------------------------------------------------------------------------

def online(tmp_path, *answers):
    """A client with an empty cache, whose fake internet gives these answers."""
    return PokeClient(cache_dir=tmp_path, session=FakeSession(*answers))


def test_a_pokemon_that_does_not_exist(tmp_path, capsys):
    client = online(tmp_path, FakeResponse(404))
    assert main(["show", "pikachoo"], client) == 1
    assert "There's no Pokémon called 'pikachoo'" in capsys.readouterr().out
    assert client.session.closed            # the with block closed it


def test_no_internet(tmp_path, capsys):
    assert main(["show", "eevee"], online(tmp_path, requests.ConnectionError())) == 1
    assert "Are you online?" in capsys.readouterr().out


def test_no_answer_in_time(tmp_path, capsys):
    client = online(tmp_path, requests.Timeout(), requests.Timeout(), requests.Timeout())
    assert main(["show", "eevee"], client) == 1
    assert "didn't answer in time" in capsys.readouterr().out


def test_the_server_keeps_failing(tmp_path, capsys):
    client = online(tmp_path, FakeResponse(500), FakeResponse(500), FakeResponse(500))
    assert main(["show", "eevee"], client) == 1
    assert "PokéAPI had a problem (500)" in capsys.readouterr().out


def test_too_many_requests(tmp_path, capsys):
    assert main(["show", "eevee"], online(tmp_path, FakeResponse(429))) == 1
    assert "Something went wrong talking to PokéAPI: 429" in capsys.readouterr().out


def test_the_saved_answers_are_all_there():
    # If this fails, a file is missing from tests/fixtures/.
    assert len(list(FIXTURES.glob("type-*.json"))) == 18
