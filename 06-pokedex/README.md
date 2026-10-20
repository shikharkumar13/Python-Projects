# Project 6: PokéDex Team Builder

**Level:** Intermediate · **Uses chapters:** 8, 9, 11, 12, 13, 14, 15, 17 and 19

In this project you'll talk to a real API. [PokéAPI](https://pokeapi.co) is free, needs no key, and knows every Pokémon there is. You'll use it to pick a team whose types cover each other's weaknesses, and then make two teams battle:

```
$ python -m pokedex battle pikachu,lapras,gengar charizard,venusaur,machamp 42
Red:  Pikachu, Lapras and Gengar
Blue: Charizard, Venusaur and Machamp
Seed: 42

Red sends out Pikachu!
Blue sends out Charizard!
  Blue's Charizard used Flare Blitz! Red's Pikachu lost 138 HP (0/95 left).
  Red's Pikachu fainted!
Red sends out Lapras!
  Blue's Charizard used Flare Blitz! Red's Lapras lost 76 HP (114/190 left).
  Red's Lapras used Hydro Pump! It's super effective! Blue's Charizard lost 131 HP (7/138 left).
  ...
Blue sends out Machamp!
  Red's Gengar used Dream Eater! It's super effective! Blue's Machamp lost 129 HP (21/150 left).
  Blue's Machamp used Struggle! Red's Gengar lost 43 HP (27/120 left).
  Red's Gengar used Dream Eater! It's super effective! Blue's Machamp lost 127 HP (0/150 left).
  Blue's Machamp fainted!

Red wins after 8 turns!

(PokéAPI requests: 0. Answers from the cache: 59.)
```

(Machamp used Struggle because every one of its moves is a normal or fighting move, and those can't touch a ghost like Gengar.)

Look at the last line: **0 requests**. Every answer the program has ever had from PokéAPI is saved on your computer, so asking again costs the server nothing. Being polite to a free API is a big part of this project. So is the most important idea in it: **when something goes wrong, should you try again?** Sometimes the answer is yes, and sometimes trying again is the worst thing you can do. There's a whole section on that [near the end](#the-big-idea-should-you-try-again).

---

## What's in this folder

```
06-pokedex/
├── README.md                this guide
├── starter/                 ← you work in here
│   ├── pokedex/             the package
│   │   ├── __main__.py      runs when you type: python -m pokedex
│   │   ├── cli.py           the commands: show, list, team, best, battle
│   │   ├── client.py        talks to PokéAPI, politely
│   │   ├── retry.py         the @retry decorator
│   │   ├── errors.py        the package's own exceptions
│   │   ├── models.py        Move, Pokemon and Team
│   │   ├── typechart.py     which types are strong against which
│   │   ├── teams.py         type coverage, and finding the best team
│   │   └── battle.py        the battle simulator
│   ├── tests/               the tests, and saved answers for them in tests/fixtures/
│   ├── cache/               answers already saved from PokéAPI, so you can start offline
│   ├── shortlist.txt        the 15 Pokémon that `best` picks a team from
│   ├── requirements.txt     the packages this project needs
│   └── pytest.ini
└── solution/                the same, finished. Have a real go first!
```

## Getting set up

Everything happens inside `starter/`:

```bash
cd starter
```

This is the first project that needs a package that isn't part of Python: `requests`. Make a virtual environment, activate it, and install everything in `requirements.txt` in one go (chapter 11 explains all of this):

```bash
python3 -m venv .venv                  # on Windows: py -m venv .venv
source .venv/bin/activate              # on Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

The first line uses `python3` (or `py`), because the virtual environment doesn't exist yet. Once it's active, plain `python` works on every computer, so the rest of this guide uses that.

`requirements.txt` asks for `requests`, `pytest`, `mypy`, and `types-requests`. That last one only describes the *types* used in `requests`, so that mypy can check your code that calls it.

## Using it

```bash
python -m pokedex show pikachu                                  # types, stats, weaknesses, battle moves
python -m pokedex list 50                                       # the first 50 Pokémon names
python -m pokedex team pikachu charizard gengar                 # how well a team covers itself
python -m pokedex best                                          # the best team of 3 from shortlist.txt
python -m pokedex battle pikachu,gengar charizard,lapras 42     # a battle. 42 is the seed
```

In `battle`, the names in each team are separated by **commas, with no spaces**, and a space separates the two teams. (In Windows PowerShell, a comma means something special, so put each team in quotes: `"pikachu,gengar" "charizard,lapras"`.) The **seed** decides all the luck in the battle. Use the same seed, and you get exactly the same battle, every time. Leave it out, and the program picks one, and tells you how to watch that battle again.

**The cache.** `cache/` already holds PokéAPI's answers for 17 Pokémon (the 15 in `shortlist.txt`, plus Ditto and Magikarp), all 18 types, their moves, and the first 60 names for `list`. So everything above works without the internet. Ask for any other Pokémon, like `python -m pokedex show eevee`, and the program downloads it, saves it in `cache/`, and never needs to ask for it again. Open `cache/` and have a look: each answer is a plain JSON file. Saved answers never expire. Pokémon data hardly ever changes, but when a new game adds new Pokémon, delete the `pokemon-offset-...` files so that `list` fetches fresh pages.

The saved answers were downloaded from PokéAPI, then **trimmed** to just the parts this project uses, to keep them small. A fresh download is the whole answer. For Pikachu, that's about 300 KB to download, and nearly 500 KB once it's saved neatly indented, instead of 8 KB. Most of it is a list of every game each move appears in.

**The ▶ button in VS Code won't work for this project.** It runs one file on its own, as if you'd typed `python pokedex/__main__.py`, and then the files in the package can't find each other. Use the terminal.

**The log.** Every real request, and every retry, is written to `pokedex.log`, next to `cache/`. It's the place to look when you want to know what the program actually sent.

## Running the tests

```bash
python -m pytest                                           # everything
python -m pytest tests/test_client.py -v                   # one file, test by test
python -m pytest tests/test_client.py::test_cache_name     # one test
python -m mypy pokedex                                     # check the type hints
```

Most tests fail when you start. Each one passes as you finish the step it checks.

**No test ever touches the internet.** A test that depends on a real website fails when you're offline, or when the website changes, or when it's having a bad day. That tells you nothing about *your* code. So the tests use two tricks instead:

- **Saved answers.** `tests/fixtures/` holds real PokéAPI answers, saved as JSON files, the same way chapter 17 used `sample_data/`. The `saved` fixture in `tests/conftest.py` is a client that reads from that folder.
- **A fake internet.** `tests/fakes.py` has a `FakeSession` that pretends to be a `requests.Session`. You give it the answers it should hand out, in order. They can be good answers, a 404 or a 503, or an exception like `requests.Timeout()`. It also counts the requests, so a test can check that a 404 was asked **once** and never again.

`conftest.py` also replaces `time.sleep` in every test, so the retry tests don't really wait.

---

## How it works

### Talking to PokéAPI

Every answer comes from a URL:

| URL | What you get |
|---|---|
| `https://pokeapi.co/api/v2/pokemon/pikachu` | Pikachu: its number, types, base stats, and the moves it can learn |
| `https://pokeapi.co/api/v2/move/thunderbolt` | one move: its type, power and accuracy |
| `https://pokeapi.co/api/v2/type/fire` | what fire is strong and weak against |
| `https://pokeapi.co/api/v2/pokemon?offset=0&limit=20` | one page of names, with a link to the next page |

`PokeClient` in `client.py` does all the talking, and it does it **politely**:

- **A `requests.Session`.** It keeps one connection open for every request, which is faster than starting again each time, and sends the same headers with all of them.
- **A `User-Agent`** header that says who's asking: `pokedex-team-builder/1.0 (a Python course practice project)`. If a program misbehaves, the people who run the API can see what it is.
- **A `timeout`** on every request. Without one, a request to a server that never answers would wait **forever**.
- **The cache.** Before asking the internet, the client looks in `cache/`. PokéAPI's fair-use policy asks everyone to do this. Its data hardly ever changes, so there's no reason to download Pikachu twice.
- **`with`.** The client is a context manager, so `with PokeClient() as client:` closes its connection at the end, even if something goes wrong.

### Retrying, but only when it can help

Sometimes a request fails. The question is whether to try again. A **5xx** status (500, 502, 503, ...) means the *server* had a problem. That's often over in a second, so it's worth another go. The same goes for a **timeout**. A **404** means *you* asked for something that doesn't exist, like a Pokémon called "pikachoo". Asking again gets the same answer, so you don't.

The `@retry` decorator in `retry.py` does the trying again. You tell it **which** errors to retry, and it waits twice as long before each new try: half a second before the second try, 1 second before the third, and so on. That's called **exponential backoff**. [The big idea](#the-big-idea-should-you-try-again) has the whole story.

### Types

Every Pokémon has one or two **types**, like fire, or ghost and poison. Every move has one type too. The type chart says how hard each type of move hits each type of Pokémon:

| Attack | Defender | Damage |
|---|---|---|
| fire | grass | ×2, "super effective" |
| fire | water | ×½, "not very effective" |
| electric | ground | ×0, "no effect" |
| ice | dragon **and** flying | ×4. For two types, multiply: 2 × 2 |

The chart is built from 18 answers, one for each type, like `/type/fire`. Each answer has three lists for the attacker: `double_damage_to`, `half_damage_to` and `no_damage_to`.

### Coverage: what makes a good team

Every Pokémon has weaknesses. Charizard (fire and flying) takes ×4 damage from rock moves. A good team has someone who **resists** each of the others' weaknesses, so there's always someone safe to send out.

For each of the 18 attack types, `team_coverage()` counts how many team members are **weak** to it (more than ×1) and how many **resist** it (less than ×1, including ×0). A **gap** is an attack type that someone is weak to and **nobody** resists:

```
Attack type   Weak  Resist
water            1       0   <- a gap
psychic          1       0   <- a gap
```

To find the **best** team, `best_team()` tries every possible team from the shortlist, and keeps the one with the fewest gaps. If two teams tie, it prefers the one that resists more types.

### Battles

A battle is a series of **turns**. Each team sends out its first Pokémon. On each turn, both Pokémon attack, the faster one first (the higher **speed** stat). If one faints, it doesn't get its attack, and its team sends out the next one. The first team with nobody left loses.

- **Moves.** Each Pokémon takes up to 4 attacks into battle, from the moves it learns last when it levels up. Those tend to be its strongest. Moves with no damage are skipped, and so are moves stronger than 120, like Explosion. In the real games those have a big catch (Explosion makes the user faint), and our simple battles don't copy those catches. They leave out the smaller side effects of every other move too. For example, Solar Beam doesn't need a turn to charge, and Dream Eater works even when the target isn't asleep.
- **Choosing.** On each turn, a Pokémon picks the move that does the most damage **on average**, counting the chance that it misses.
- **Damage.** It uses a simpler version of the games' formula. Stronger moves, and a higher Attack against a lower Defense, mean more damage. The type chart multiplies it. A move that matches the attacker's own type does ×1.5 (the "same-type attack bonus"). And a random **roll** from 0.85 to 1.0 means the same attack doesn't always do exactly the same damage.
- **Struggle.** A Pokémon with no attacks at all (Ditto only knows Transform), or none that can hurt its opponent, uses Struggle. Struggle has no type, so it always does normal damage.
- **Luck.** Misses, the damage roll, and speed ties all come from one `random.Random(seed)`. That's why the same seed replays the same battle.

### Your must-have checklist

- [ ] `PokeClient` uses a `requests.Session`, a `User-Agent`, a `timeout` on every request, and `raise_for_status()`
- [ ] It works with `with`, through `__enter__` and `__exit__`
- [ ] Every answer is cached on disk. Running the same command twice costs zero requests the second time
- [ ] A `@retry` decorator factory with exponential backoff, for timeouts and 5xx errors only
- [ ] A 404 raises `PokemonNotFound`, and is never retried
- [ ] A generator that pages through `/pokemon` by following each page's `next` URL
- [ ] `Pokemon`, `Move` and `Team` classes, and a type chart built from `/type/{name}`
- [ ] `itertools.combinations` finds the best team, and `functools.lru_cache` saves repeated work
- [ ] A turn-based battle with a damage formula, stats and type multipliers, seeded so it replays exactly
- [ ] The tests use saved answers, never the network. Every test passes

### How the package is organised

| File | What's in it | Your TODOs |
|---|---|---|
| `pokedex/retry.py` | the `@retry` decorator factory | 1 |
| `tests/test_client.py` | tests for the client | 2 |
| `pokedex/client.py` | `PokeClient`: the cache, requests, pages and moves | 3–7, 11 |
| `pokedex/models.py` | `Move`, `Pokemon` and `Team` | 8–10 |
| `pokedex/typechart.py` | `TypeChart` | 12, 13 |
| `pokedex/teams.py` | `matchups()`, `team_coverage()` and `best_team()` | 14, 15 |
| `pokedex/battle.py` | `Fighter`, `damage()`, `choose_move()` and `Battle` | 16–18 |

`cli.py` and `errors.py` are already written, and so are some smaller pieces you'll use, like `cache_name()`, `clean_name()`, `Move` and `team_coverage()`. Read them: they're worked examples for the TODOs next to them.

---

## Building it, one step at a time

Each unfinished part has a *placeholder* that keeps the program running. For a while, every command just says something like `Looking up a Pokémon is TODO 4.` That's the placeholder talking, not a bug. The message tells you which step is next.

### Part 1: Talking to PokéAPI (`retry.py` and `client.py`)

#### Step 1: The `@retry` decorator factory

Chapter 13 built decorators like this one:

```python
def shout(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper
```

`@retry` needs **settings**: which errors to retry, how many tries, and how long to wait. So it's a decorator *factory*, which is one more function wrapped around the outside. `retry(...)` takes the settings and returns a decorator. The decorator takes the function and returns `wrapper`. And `wrapper` does the real work:

```python
@retry(retry_on=(requests.Timeout, ServerError), attempts=3, base_delay=0.5)
def _fetch(self, url): ...

# is the same as:
_fetch = retry(retry_on=(requests.Timeout, ServerError), attempts=3, base_delay=0.5)(_fetch)
```

Inside `wrapper`, try the function in a loop. If it raises one of the `retry_on` errors, wait and go round again. If it was the last try, re-raise the error with a bare `raise`. Any **other** error isn't caught at all, so it goes straight through. `except retry_on as error:` works because `except` accepts a tuple of exception types.

The waits double each time: `base_delay * 2 ** (attempt - 1)` gives 0.5, 1, 2, 4... Put `@functools.wraps(func)` above `wrapper`, so the wrapped function keeps its own name and docstring. (One of the tests checks.)

**Check it:** `python -m pytest tests/test_retry.py`. All 6 should pass.

#### Step 2: Two tests, before the downloading (`tests/test_client.py`)

These are the two tests for the learning moment. Write them **before** `_fetch()`, which is Step 5. Open `tests/test_client.py`, and find the two tests that say `pytest.skip`:

1. **A 404 is not retried.** The fake internet answers 404. `get_pokemon("pikachoo")` should raise `PokemonNotFound`, after exactly **one** request.
2. **A server error is retried.** The fake internet answers 503 and then 200. `get_json()` should give back the answer, after **two** requests.

`client_with(tmp_path, ...)` at the top of the file makes a client with an empty cache and a fake internet. `len(client.session.requests)` is how many requests it made.

**Check it:** `python -m pytest tests/test_client.py -k "test_a_404 or test_a_server"`. Both should **fail** for now, since nothing can download anything yet. They'll pass after Step 5.

#### Step 3: `get_json`, the cache

```
get_json(url)
  ├── is it in cache/?  yes → read it, and return it
  └── no → _fetch(url) downloads it → _save() writes it to cache/ → return it
```

`cache_name()` is written for you. It turns a URL into a safe file name: `.../pokemon/pikachu` becomes `pokemon-pikachu.json`. Read the file inside a `try`. If it's damaged (somebody edited it, or the computer crashed halfway through writing it), `json.loads` raises a `ValueError`. If it can't be read at all, `read_text` raises an `OSError`. Catch both, log a warning, and download it again. Do the same if the file holds JSON that isn't an object (a dictionary), like `null`, because every PokéAPI answer is one. `try` / `except` / `else` fits nicely here: the `else` part only runs when there was no error.

`_save()` is written for you too. It writes to a `.tmp` file first, then renames it over the real one. A rename either happens completely or not at all, so the cache can never end up with half a file in it.

**Check it:** `python -m pytest tests/test_client.py -k saved_answers`. That test reads Gengar from the saved answers and checks that it took zero requests.

#### Step 4: `get_pokemon`

Build the URL with `clean_name(name)`, which is written for you. It turns `"  Mr. Mime "` into `"mr-mime"`, the way PokéAPI spells it. It also refuses a name like `../secret` before anything is sent.

When the API says 404, `get_json()` raises `NotFound` (once Step 5 is done). Catch it and raise `PokemonNotFound(name)` instead, which has a much friendlier message:

```python
except NotFound as error:
    raise PokemonNotFound(name) from error
```

`from error` **chains** the two exceptions (chapter 9). The new error remembers the old one in its `__cause__`, so if it's ever printed as a traceback, you see both.

**Check it:** `python -m pytest tests/test_client.py -k impossible_names` (5 should pass). Then `python -m pokedex show pikachu` should say `Making a Pokemon from PokéAPI's answer is TODO 9.` It found Pikachu in the cache, so it got further than before.

#### Step 5: `_fetch`, one request

This is the only place in the whole project where a request is actually sent:

```python
response = self.session.get(url, timeout=TIMEOUT)
```

Then look at `response.status_code`. For 404, raise `NotFound`. For 500 and above, raise `ServerError`. For anything else, call `response.raise_for_status()`, which raises `requests.HTTPError` for any other bad status (and does nothing for a good one). Then return `response.json()`.

The `@retry(...)` line above `_fetch` is already there. Look at what it retries: `requests.Timeout` and `ServerError`. Not `NotFound`, and not `HTTPError`. **That one line is the learning moment.**

**Check it:** `python -m pytest tests/test_client.py -k "retried or errors or not_found"`. Your two tests from Step 2 pass now, along with the tests for timeouts, other 4xx statuses, and having no internet.

#### Step 6: `__exit__`

A context manager is any object with `__enter__` and `__exit__` methods (chapter 14). `with PokeClient() as client:` calls `__enter__` at the start, and whatever it returns becomes `client`. `__enter__` is done for you: it returns `self`.

`__exit__` runs when the `with` block ends, **however** it ends, even with an error. Close the session there. Then don't return anything. If `__exit__` returns `True`, Python **swallows** the error that ended the `with` block, as if it never happened. That's almost never what you want.

**Check it:** `python -m pytest tests/test_client.py -k with_closes`. One of the 2 tests ends its `with` block with a `ZeroDivisionError`, on purpose, and checks that the error still gets out.

#### Step 7: `iter_pokemon`, a generator over pages

There are over 1,300 Pokémon. PokéAPI hands the list out in **pages**:

```json
{
  "count": 1351,
  "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
  "previous": null,
  "results": [{"name": "bulbasaur", "url": "..."}, {"name": "ivysaur", "url": "..."}, ...]
}
```

Fetch a page, `yield` each name in it, then move on to the URL in `"next"`. On the last page, `"next"` is `null` in JSON, which is `None` in Python. That's when the loop stops.

**Follow `next`. Don't build the URLs yourself.** The API knows where the next page is, and the link keeps working even if the page size or the URL format changes one day.

Because it's a generator (chapter 12), it fetches nothing until somebody asks for a name, and then only one page at a time. `list 25` takes 25 names with `islice()`, which costs 2 pages, not 68.

**Check it:** `python -m pytest tests/test_client.py -k iter_pokemon`, then `python -m pokedex list 45`. The second one reads 3 pages from the cache. The footer says so.

### Part 2: Pokémon and their moves (`models.py`, and one more in `client.py`)

#### Step 8: `level_up_moves`

Open `tests/fixtures/pokemon-pikachu.json` to see what PokéAPI says about a Pokémon. `"moves"` is a list, and each move lists the games it can be learned in, and how:

```json
{"move": {"name": "thunderbolt"},
 "version_group_details": [{"level_learned_at": 42, "move_learn_method": {"name": "level-up"}, ...}]}
```

Pokémon learn their strongest moves **last**, so the battle moves come from the moves learned by `"level-up"`, the highest level first. In a fresh download, a move appears once for each game, often at different levels. Keep the highest. (The saved answers were trimmed to just that one.) Then sort, with a tuple as the key:

```python
sorted(levels, key=lambda name: (-levels[name], name))
```

Tuples are compared one item at a time. So this sorts by level, highest first (that's what the minus does), and then A to Z when two levels are the same. Without the second part, moves at the same level could come out in a different order on different computers.

**Check it:** `python -m pytest tests/test_models.py -k level_up`

#### Step 9: `Pokemon.from_api`

`from_api` is a **classmethod** (chapter 8): a second way to make an object, straight from the API's answer. `Move.from_api` just above it is a finished example. Yours pulls out the types as a tuple, the stats as a dictionary, and the level-up moves.

Why is `Move` a `@dataclass(frozen=True)`, and `Pokemon` a normal class? A move is just a few values that never change, which is exactly what a frozen dataclass is for (chapter 15). It even writes `__init__`, `__repr__` and `==` for you. `Pokemon` has more going on: a classmethod, a property, a method that works out stats, and its own `__str__`.

**Check it:** `python -m pytest tests/test_models.py -k "from_api or types or battle_stats"`. Then `python -m pokedex show pikachu` shows Pikachu's stats. Its weaknesses say "nothing" until Part 3.

#### Step 10: `Team.add`

A team has at most 6 Pokémon, and no Pokémon twice. Raise `TeamError` for either. `pokemon.name in self` works because `Team` has a `__contains__` method. The other "dunder" methods underneath it make `len(team)` and `for pokemon in team` work too.

**Check it:** `python -m pytest tests/test_models.py`. The whole file passes now.

#### Step 11: `get_battle_moves`, lazy lookups (`client.py`)

Each move needs its own request. Pikachu learns 24 moves by levelling up, but a battle only needs 4 attacks. So look them up **lazily**, with two generator expressions and `islice()`:

```python
looked_up = (self.get_move(name) for name in pokemon.move_names[:MAX_MOVE_LOOKUPS])
attacks = (move for move in looked_up if move.is_attack)
moves = list(islice(attacks, BATTLE_MOVES))
```

Nothing is looked up on the first two lines. A generator expression doesn't run until something asks it for a value. `islice()` asks for one attack at a time, and `attacks` asks `looked_up` for moves until it finds one that's an attack. After the 4th attack, `islice()` stops asking, and the moves after it are never looked up at all.

If there are no attacks at all, return `[STRUGGLE]`.

**Check it:** `python -m pytest tests/test_client.py -k "battle_moves or struggle"`. Now the whole of `tests/test_client.py` passes. Try `python -m pokedex show ditto` too.

### Part 3: Types and teams (`typechart.py` and `teams.py`)

#### Step 12: `TypeChart.from_api`

Open `tests/fixtures/type-fire.json`. The interesting part is `"damage_relations"`:

```json
"double_damage_to": [{"name": "bug"}, {"name": "steel"}, {"name": "grass"}, {"name": "ice"}],
"half_damage_to":   [{"name": "rock"}, {"name": "fire"}, {"name": "water"}, {"name": "dragon"}],
"no_damage_to":     [],
```

Turn each type's answer into a row of the table: `table["fire"] = {"bug": 2.0, ..., "rock": 0.5, ...}`. The `RELATIONS` dictionary at the top of the file maps each list's name to its multiplier. Leave out anything that does normal damage. The table only needs the exceptions. (There are three `..._from` lists too. Those are the same facts again, from the defender's side, so you can ignore them.)

**Check it:** `python -m pytest tests/test_typechart.py -k "every_type or tiny"`

#### Step 13: `TypeChart.multiplier`

Look up the attack's row, and multiply together its value for each of the defender's types. Use `.get(..., 1.0)` for anything that isn't there. That gives normal damage, and also copes with Struggle's `"typeless"`.

**Check it:** `python -m pytest tests/test_typechart.py`

#### Step 14: `matchups`, with `@lru_cache`

For one set of types, work out which attack types are strong against it (more than ×1) and which are weak against it (less than ×1). Return them as a `Matchups`.

The `@lru_cache(maxsize=None)` line above it is already written, and it does something clever. It remembers the answer for every set of arguments it has seen. The second time `matchups()` is called with the same chart and types, it hands back the saved answer without running the function at all. `best_team()` in the next step needs that: it asks about the same 15 Pokémon over a thousand times.

There's one rule. `lru_cache` keeps its answers in a dictionary, with the arguments as the key, so the arguments must be **hashable**. A tuple is. A list isn't, because a list can change. That's why a Pokémon's `types` is a tuple. (A `TypeChart` is hashable too. A normal class is hashable by default, by its identity.)

**Check it:** `python -m pytest tests/test_teams.py -k "matchups or coverage or no_gaps"`. Then `python -m pokedex show gengar`, and `python -m pokedex team pikachu charizard gengar`.

#### Step 15: `best_team`, with `itertools.combinations`

```python
>>> from itertools import combinations
>>> list(combinations(["a", "b", "c", "d"], 3))
[('a', 'b', 'c'), ('a', 'b', 'd'), ('a', 'c', 'd'), ('b', 'c', 'd')]
```

`combinations()` hands out every possible group, one at a time, without ever building a list. **Count them first**, the way chapter 15 suggests. `math.comb(15, 3)` is 455, which is nothing. `math.comb(15, 6)` is 5,005, still fine. But `math.comb(1351, 6)` is about 8 × 10¹⁵. Checking a million teams a second would take over 250 years. The `best` command works out the count before it starts, for exactly this reason. It refuses anything over `MAX_TEAMS` (a million), which would take more than a few seconds.

Then `max()` with a `key` picks the best one. `Coverage.score` is a tuple, `(-gaps, resisted)`, so tuples do the work again: fewer gaps wins first, and more types resisted breaks a tie.

**Check it:** `python -m pytest tests/test_teams.py`, then `python -m pokedex best`. Look at the last line. It says how many times `lru_cache` saved `matchups()` the work.

### Part 4: Battles (`battle.py`)

#### Step 16: `damage`

```python
amount = (2 * LEVEL / 5 + 2) * move.power * attack / defence / 50 + 2
```

That's the games' own formula, with the rarer extras left out. Every Pokémon fights at level 50, so the first bracket is always 22. Physical moves use Attack against Defense, and special moves use Special Attack against Special Defense. Then multiply by ×1.5 if the move's type is one of the attacker's own types, then by the type chart's multiplier, then by the roll. A hit always does at least 1, unless the type chart says ×0.

`test_damage_worked_out_by_hand` works through one example, number by number, in its comments. If your answer is different, follow along with a calculator.

**Check it:** `python -m pytest tests/test_battle.py -k damage`

#### Step 17: `choose_move`

Write a small function inside `choose_move` that gives a move's **average** damage: its damage with `roll=1.0`, times the chance it hits. Then `max(attacker.moves, key=average)`. A 90-power move that misses half the time averages less than an 80-power move that never misses.

If even the best move averages 0, every move this Pokémon has is useless against this opponent. Return `STRUGGLE`.

**Check it:** `python -m pytest tests/test_battle.py -k choose_move`

#### Step 18: `Battle.attack`

The rest of `Battle` is written for you: `take_turn()` decides who goes first, and `run()` keeps going until a team runs out. `attack()` is one Pokémon's move: choose it, see if it hits, take off the damage, and write it all in the log.

Every bit of luck must come from `self.random`, never from the `random` module directly. `self.random` is a `random.Random(seed)`: a random number generator of its own, started from the seed. Two generators started from the same seed give exactly the same numbers in the same order. So as long as `self.random` is the only source of luck, the same seed gives the same battle. Call `random.randint()` just once, anywhere, and replays stop working.

**Check it:** `python -m pytest`. **Everything** passes. Then:

```bash
python -m pokedex battle pikachu,charizard,blastoise venusaur,gengar,snorlax 7
python -m pokedex battle pikachu,charizard,blastoise venusaur,gengar,snorlax 7
```

Exactly the same battle, twice. And `python -m mypy pokedex` should say `Success`.

---

## The big idea: should you try again?

When a request fails, it's tempting to wrap it in a loop and keep trying until it works. Sometimes that's right. Sometimes it's a disaster. It depends on **whose fault** the failure was.

**"The server failed."** A 500, 502 or 503 status, or no answer before the timeout. The server is overloaded, restarting, or having a bad moment. It's not your fault, and it may well be fine in a second or two. **Try again**, but give it room to recover: wait half a second, then 1, then 2. That's exponential backoff. If every program hammered a struggling server the moment it failed, it would never get back on its feet.

**"You asked for something that doesn't exist."** A 404. The server is working perfectly, and it's telling you, correctly, that there's no Pokémon called "pikachoo". Ask again, and you get the same answer, every time. Retrying a 404 just wastes two more requests and a second and a half of waiting, before failing anyway. The fix is on *your* side: check the spelling. So `_fetch` raises `NotFound`, `@retry` isn't told to retry it, and the user gets a clear message straight away.

The same goes for the other 4xx statuses. 400 means "your request makes no sense". 403 means "you're not allowed". 429 means "too many requests: slow down". Asking again straight away fixes none of them. (A 429 is a special case. It's worth trying again later, which is [stretch goal 2](#2-smarter-waiting).)

And "no internet at all" (`requests.ConnectionError`) isn't retried either. If your Wi-Fi is off, three tries in a second and a half won't turn it back on. The program says "Are you online?", and reminds you that anything already in `cache/` still works.

That's why `retry_on` has no default value. A decorator that retried everything by default would make the wrong choice for you, without you noticing. You have to say which errors are worth another try:

```python
@retry(retry_on=(requests.Timeout, ServerError), attempts=3, base_delay=0.5)
```

---

## Try to break it

Each of these should give a clear message, not a traceback:

- [ ] `python -m pokedex show pikachoo`. You need the internet for this one: PokéAPI answers 404. Check `pokedex.log`: there was exactly **one** request
- [ ] Turn off your Wi-Fi, and try `python -m pokedex show eevee`. Then `python -m pokedex show pikachu`, which still works, from the cache
- [ ] `python -m pokedex show ../secret` and `python -m pokedex show "pika?chu"`. Neither is even sent to PokéAPI
- [ ] `python -m pokedex show "  PIKACHU  "`, then (with the internet) `python -m pokedex show Mr. Mime` and `python -m pokedex show 25`
- [ ] Run `python -m pokedex show eevee` twice. The footer says 0 requests the second time. Now open `cache/pokemon-eevee.json`, delete half of it, and run it again
- [ ] `python -m pokedex team pikachu pikachu`, and a team of 7
- [ ] `python -m pokedex battle ditto magikarp`. Ditto has no attacks at all
- [ ] `python -m pokedex battle pikachu gengar` a few times without a seed, then with one of the seeds it suggests
- [ ] `python -m pokedex best 7`, `python -m pokedex best three`, and `best` with only 2 names in `shortlist.txt`, or with one name twice
- [ ] `python -m pokedex battle pikachu, gengar lapras`, with a space after the comma
- [ ] `python -m pokedex list 0`, `python -m pokedex list -5` and `python -m pokedex list ²`. (`"²".isdigit()` is `True`, but `int("²")` crashes. `isdecimal()` gets it right.)
- [ ] `python -m pokedex list 100`. It needs the internet for pages 4 and 5. Run it again: 0 requests

---

## Stretch goals

Pick one. There's no solution for these.

### 1. A tournament

Every team fights every other team, and you print a leaderboard.

- Put a few teams in a file, one team per line, like `pikachu,gengar,lapras`.
- `itertools.combinations(teams, 2)` gives every pairing exactly once.
- Play each pairing a few times, with different seeds. Then swap who's Red: being first in the list shouldn't decide anything, but check!
- Count wins with a `Counter`, and print it with `.most_common()`.
- Give the whole tournament one seed, and make the seed for each battle from it, so the whole tournament replays too.

### 2. Smarter waiting

Two things real API clients do that ours doesn't:

- **Jitter.** If a thousand programs all fail at the same moment, they all retry after exactly 0.5 seconds, and hit the server at the same moment again. Add a little randomness to each wait, like `delay * random.uniform(0.5, 1.5)`, so they spread out. Make it an option of `@retry`, and test it with a `random.Random` that you pass in.
- **`Retry-After`.** With a 429, servers often send a `Retry-After` header that says how many seconds to wait. Raise a new `RateLimited` error that stores that number, and teach `@retry` to wait that long for it. Your `FakeResponse` will need a `headers` dictionary.

### 3. Attack coverage

`best_team()` only looks at **defence**: who resists what. A team can also be judged on **attack**: for how many of the 18 types does somebody on the team have a super-effective move?

- Write `attack_coverage(chart, team, moves)` that returns the set of types somebody can hit for ×2 or more.
- Combine both into a new score. What if the defence and attack scores disagree? Decide which matters more, and write a test that shows it.
- This needs each Pokémon's moves, which means more requests the first time. How many? Try it with `python -m pokedex show` for each one first, and look at the footer.

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 8. OOP | the classes `PokeClient`, `Pokemon`, `Team`, `TypeChart`, `Fighter` and `Battle`; the classmethods `from_api`; properties; `__str__`, `__len__`, `__iter__` and `__contains__`; exceptions that inherit from `PokedexError` |
| 9. Exceptions | your own exception classes, `raise ... from error`, `try` / `except` / `else`, and deciding which errors to retry |
| 11. Packages | `python -m pokedex`, a virtual environment and `requirements.txt` |
| 12. Generators | `iter_pokemon()` following each page's `next`, and lazy generator expressions with `islice()` |
| 13. Decorators | `@retry(...)`, a decorator factory with arguments, and `@command("list")`, with `functools.wraps` |
| 14. Context managers | `__enter__` and `__exit__` on `PokeClient` |
| 15. The standard library | `@dataclass(frozen=True)`, `@lru_cache` and `cache_info()`, `combinations()` and `islice()` from `itertools`, `math.comb()` and `random.Random(seed)` |
| 17. APIs | `requests.Session`, headers, timeouts, status codes, `raise_for_status()`, pagination, caching and retries |
| 19. Reliable code | type hints and mypy, `logging` to a file, and pytest with fixtures, `monkeypatch`, a fake session and saved answers |
