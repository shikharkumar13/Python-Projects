"""Tests for PokeClient: requests, retries, the cache and pages. None of them use the internet."""

import json
from itertools import islice

import pytest
import requests

from fakes import FIXTURES, FakeResponse, FakeSession
from pokedex.client import BASE_URL, TIMEOUT, USER_AGENT, PokeClient, cache_name, clean_name
from pokedex.errors import NotFound, PokemonNotFound, ServerError
from pokedex.models import STRUGGLE

PIKACHU = json.loads((FIXTURES / "pokemon-pikachu.json").read_text(encoding="utf-8"))
URL = BASE_URL + "pokemon/pikachu"


def client_with(tmp_path, *answers):
    """A client with an empty cache, and a fake session that gives these answers."""
    return PokeClient(cache_dir=tmp_path / "cache", session=FakeSession(*answers))


# ---------------------------------------------------------------------------
# The learning moment: what's worth trying again, and what isn't
# ---------------------------------------------------------------------------

def test_a_404_is_not_retried(tmp_path):
    client = client_with(tmp_path, FakeResponse(404))
    with pytest.raises(PokemonNotFound):
        client.get_pokemon("pikachoo")
    assert len(client.session.requests) == 1        # asked once, and never again


def test_a_server_error_is_retried(tmp_path):
    client = client_with(tmp_path, FakeResponse(503), FakeResponse(200, PIKACHU))
    assert client.get_json(URL)["name"] == "pikachu"
    assert len(client.session.requests) == 2


def test_a_timeout_is_retried_then_given_up_on(tmp_path, sleeps):
    client = client_with(tmp_path, requests.Timeout(), requests.Timeout(), requests.Timeout())
    with pytest.raises(requests.Timeout):
        client.get_json(URL)
    assert len(client.session.requests) == 3
    assert sleeps == [0.5, 1.0]


def test_too_many_server_errors(tmp_path):
    client = client_with(tmp_path, FakeResponse(500), FakeResponse(502), FakeResponse(503))
    with pytest.raises(ServerError):
        client.get_json(URL)
    assert len(client.session.requests) == 3


@pytest.mark.parametrize("status", [400, 403, 429])
def test_other_client_errors_are_not_retried(tmp_path, status):
    client = client_with(tmp_path, FakeResponse(status))
    with pytest.raises(requests.HTTPError):
        client.get_json(URL)
    assert len(client.session.requests) == 1


def test_no_internet_is_not_retried(tmp_path):
    client = client_with(tmp_path, requests.ConnectionError("no internet"))
    with pytest.raises(requests.ConnectionError):
        client.get_json(URL)
    assert len(client.session.requests) == 1


def test_pokemon_not_found_keeps_the_original_error(tmp_path):
    client = client_with(tmp_path, FakeResponse(404))
    with pytest.raises(PokemonNotFound) as caught:
        client.get_pokemon("pikachoo")
    assert "pikachoo" in str(caught.value)
    assert caught.value.__cause__ is not None       # from "raise ... from error"


# ---------------------------------------------------------------------------
# Being polite
# ---------------------------------------------------------------------------

def test_every_request_has_a_timeout_and_a_user_agent(tmp_path):
    client = client_with(tmp_path, FakeResponse(200, PIKACHU))
    client.get_json(URL)
    assert client.session.requests == [(URL, TIMEOUT)]
    assert client.session.headers["User-Agent"] == USER_AGENT


def test_a_real_session_gets_the_user_agent(tmp_path):
    with PokeClient(cache_dir=tmp_path) as client:
        assert isinstance(client.session, requests.Session)
        assert client.session.headers["User-Agent"] == USER_AGENT


def test_with_closes_the_session(tmp_path):
    with client_with(tmp_path) as client:
        assert not client.session.closed
    assert client.session.closed


def test_with_closes_the_session_even_after_an_error(tmp_path):
    client = client_with(tmp_path)
    with pytest.raises(ZeroDivisionError):     # __exit__ mustn't hide the error
        with client:
            1 / 0
    assert client.session.closed


# ---------------------------------------------------------------------------
# The cache
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "url, name",
    [
        (BASE_URL + "pokemon/pikachu", "pokemon-pikachu.json"),
        (BASE_URL + "type/fire/", "type-fire.json"),
        (BASE_URL + "pokemon?offset=20&limit=20", "pokemon-offset-20-limit-20.json"),
    ],
)
def test_cache_name(url, name):
    assert cache_name(url) == name


def test_the_second_time_costs_no_requests(tmp_path):
    client = client_with(tmp_path, FakeResponse(200, PIKACHU))     # only ONE answer
    first = client.get_json(URL)
    assert client.get_json(URL) == first
    assert len(client.session.requests) == 1
    assert (client.cache_dir / "pokemon-pikachu.json").exists()
    assert (client.requests_made, client.from_cache) == (1, 1)


def test_a_new_client_uses_the_saved_answer(tmp_path):
    client_with(tmp_path, FakeResponse(200, PIKACHU)).get_json(URL)
    later = client_with(tmp_path)        # no answers at all: any request fails the test
    assert later.get_json(URL)["id"] == 25


def test_saved_answers_cost_no_requests(saved):
    assert saved.get_json(BASE_URL + "pokemon/gengar")["name"] == "gengar"
    assert (saved.requests_made, saved.from_cache) == (0, 1)


def test_get_pokemon_cleans_the_name(saved):
    assert saved.get_pokemon("  Gengar ").types == ("ghost", "poison")


def test_a_damaged_cache_file_is_downloaded_again(tmp_path):
    client = client_with(tmp_path, FakeResponse(200, PIKACHU))
    client.cache_dir.mkdir()
    (client.cache_dir / "pokemon-pikachu.json").write_text('{"id": 25, "na', encoding="utf-8")
    assert client.get_json(URL)["name"] == "pikachu"
    assert json.loads((client.cache_dir / "pokemon-pikachu.json").read_text(encoding="utf-8"))["id"] == 25


def test_an_unreadable_cache_file_is_downloaded_again(tmp_path):
    # A folder where the file should be: reading it raises an OSError.
    client = client_with(tmp_path, FakeResponse(200, PIKACHU))
    (client.cache_dir / "pokemon-pikachu.json").mkdir(parents=True)
    assert client.get_json(URL)["name"] == "pikachu"
    assert len(client.session.requests) == 1        # it couldn't save it either, but that's fine


@pytest.mark.parametrize("saved_text", ["null", "[1, 2]", '"pikachu"'])
def test_a_cache_file_that_is_not_an_object_is_downloaded_again(tmp_path, saved_text):
    client = client_with(tmp_path, FakeResponse(200, PIKACHU))
    client.cache_dir.mkdir()
    (client.cache_dir / "pokemon-pikachu.json").write_text(saved_text, encoding="utf-8")
    assert client.get_json(URL)["id"] == 25


def test_not_found_is_never_saved(tmp_path):
    client = client_with(tmp_path, FakeResponse(404), FakeResponse(404))
    for _ in range(2):
        with pytest.raises(NotFound):
            client.get_json(BASE_URL + "pokemon/pikachoo")
    assert len(client.session.requests) == 2     # it might exist tomorrow, so it isn't saved


@pytest.mark.parametrize(
    "typed, cleaned",
    [("pikachu", "pikachu"), ("  Pikachu ", "pikachu"), ("Mr. Mime", "mr-mime"), ("farfetch'd", "farfetchd"), ("25", "25")],
)
def test_clean_name(typed, cleaned):
    assert clean_name(typed) == cleaned


@pytest.mark.parametrize("typed", ["", "   ", "../secret", "pika?chu", "pika/chu"])
def test_impossible_names_never_reach_the_api(tmp_path, typed):
    client = client_with(tmp_path)          # no answers: a request would fail the test
    with pytest.raises(PokemonNotFound):
        client.get_pokemon(typed)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def page(names, next_url):
    return FakeResponse(200, {"count": 3, "next": next_url, "previous": None,
                              "results": [{"name": name, "url": ""} for name in names]})


def test_iter_pokemon_follows_next_until_it_is_none(tmp_path):
    client = client_with(tmp_path, page(["bulbasaur", "ivysaur"], BASE_URL + "pokemon?offset=2&limit=2"),
                         page(["venusaur"], None))
    assert list(client.iter_pokemon()) == ["bulbasaur", "ivysaur", "venusaur"]
    assert [url for url, _ in client.session.requests][1] == BASE_URL + "pokemon?offset=2&limit=2"


def test_iter_pokemon_only_fetches_the_pages_it_needs(saved):
    names = list(islice(saved.iter_pokemon(), 25))      # pages of 20, so 2 pages
    assert names[0] == "bulbasaur" and names[24] == "pikachu"
    assert saved.from_cache == 2


def test_iter_pokemon_is_lazy(tmp_path):
    client = client_with(tmp_path)          # no answers
    client.iter_pokemon()                   # making the generator asks for nothing yet
    assert client.session.requests == []


# ---------------------------------------------------------------------------
# Battle moves
# ---------------------------------------------------------------------------

def test_battle_moves_stop_after_four(saved):
    pikachu = saved.get_pokemon("pikachu")
    moves = saved.get_battle_moves(pikachu)
    assert [move.name for move in moves] == ["thunder", "wild-charge", "discharge", "thunderbolt"]
    # Thunderbolt was the 4th attack, so nothing after it was looked up.
    looked_up = pikachu.move_names.index("thunderbolt") + 1
    assert saved.from_cache == 1 + looked_up        # Pikachu itself, then the moves
    assert looked_up < len(pikachu.move_names)


def test_battle_moves_skip_moves_that_are_not_attacks(saved):
    # Gengar's latest moves include Mean Look and Nightmare, which do no damage, so they're skipped.
    moves = saved.get_battle_moves(saved.get_pokemon("gengar"))
    assert len(moves) == 4 and all(move.is_attack for move in moves)


def test_no_attacks_means_struggle(saved):
    assert saved.get_battle_moves(saved.get_pokemon("ditto")) == [STRUGGLE]
