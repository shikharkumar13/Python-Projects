# Project 4: Streaks

**Level:** Intermediate · **Uses chapters:** 10, 11, 13, 14, 15 and 19

You want to read 20 pages a day, drink enough water and practise Python. In this project you'll build a small tool that tracks your habits from the terminal. It counts your streaks, and shows a GitHub-style heatmap of your last 12 weeks.

```
$ python -m streaks done read
Done: read 20 pages. Your streak is 2 days.

$ python -m streaks status
Your habits on Monday 19 October 2026

Habit            Today   Streak     Best
read 20 pages      ✓     2 days  11 days
drink water        ·     4 days  17 days   do it today to keep your streak going!
practise python    ·     0 days   5 days

The last 12 weeks:
     Aug       Sep     Oct
Mon  ░ ▓ █ ▓ █ ▓ ▓ ░ ▓ ▓ ▓ ░
Tue  █ ░ ▓ ▓ ▓ █ ▓ █ ▓ █ ▓
Wed  ▓ ░ ░ ▓ ▓ █ █ █ ▓ █ ·
Thu  ▓ ░ ▓ ▓ ░ █ ▓ ▓ █ █ █
Fri  █ · █ ▓ ▓ ░ ▓ █ █ █ ▓
Sat  ▓ █ █ ▓ █ █ · ▓ █ ░ ░
Sun  █ ▓ █ ░ █ █ █ █ ▓ ░ ▓
· none   ░ some   ▓ at least half   █ all done
```

This is the first project that's a real **package**, a folder of Python files that work together, and the first one that comes with **tests**.

---

## What's in this folder

```
04-streaks/
├── README.md               this guide
├── starter/                ← you work in here
│   ├── streaks/            the package
│   │   ├── __init__.py     marks the folder as a package
│   │   ├── __main__.py     runs when you type: python -m streaks
│   │   ├── habits.py       the Habit dataclass and the streak maths
│   │   ├── storage.py      saving and loading, safely
│   │   ├── heatmap.py      drawing the heatmap
│   │   └── cli.py          the commands
│   ├── tests/              the tests, with pytest
│   ├── pytest.ini          tells pytest where to find the package
│   └── make_sample_data.py makes some fake history to look at
└── solution/               the same, finished. Have a real go first!
```

When you use the program, it creates two files next to the package: `habits.json` (your habits) and `streaks.log` (a diary of what it did).

## Getting set up

Everything happens inside the `starter` folder, so go there first:

```bash
cd starter
```

The tests need **pytest**. If you haven't installed it yet, a virtual environment is the tidy way (chapter 11):

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install pytest
```

On Windows, type `python` (or `py`) instead of `python3` everywhere in this guide.

## Using it

Run these from inside `starter/`:

| Type this | What it does |
|---|---|
| `python -m streaks add "read 20 pages"` | start tracking a habit |
| `python -m streaks done read` | mark it done today. The start of the name is enough |
| `python -m streaks status` | your streaks, and the heatmap |
| `python -m streaks stats` | your best day of the week, and how often you keep each habit |
| `python -m streaks remove read` | stop tracking a habit |
| `python -m streaks` | list the commands |

To see the heatmap filled in straight away, make some fake history first:

```bash
python make_sample_data.py
python -m streaks status
```

(That only works once you've finished the steps below. Try it in `solution/` first, if you'd like to see the finished thing.)

**Why `python -m streaks` and not `python streaks/cli.py`?** The files inside the package import each other, like `from streaks.habits import Habit`. For that to work, Python has to know that `streaks` is a package. `-m` tells Python "run this package", and it looks for it in the folder you're in. That's why you must be in `starter/`, the folder that *contains* `streaks/`. From anywhere else, you'll get `No module named streaks`.

## Running the tests

From inside `starter/`:

```bash
python -m pytest              # run every test
python -m pytest -v           # list each test and whether it passed
python -m pytest tests/test_habits.py                      # just one file
python -m pytest tests/test_habits.py::test_longest_streak # just one test
python -m pytest -k leap      # only the tests with "leap" in their name
```

When you start, most tests **fail**. That's on purpose. Each failing test is something still to build. Your goal is to see them all pass.

---

## How it works

### Streaks

- Your **current streak** is how many days in a row you've done a habit, up to today.
- If you haven't done it *yet* today, your streak is still alive, counting up to yesterday. You have until midnight. A streak only breaks once a whole day goes by without it.
- Your **best streak** is the longest run of days in a row, ever.

### How the package is organised

| File | What's in it | Your TODOs |
|---|---|---|
| `tests/test_habits.py` | tests for the streak maths | 1 |
| `streaks/habits.py` | `Habit`, the streak maths, finding a habit by name, stats | 2–7, 17, 18 |
| `streaks/storage.py` | saving and loading `habits.json` | 8–10 |
| `streaks/cli.py` | the `@command` decorator and the commands | 11–13 |
| `streaks/heatmap.py` | drawing the heatmap | 14–16 |

`__main__.py` sets up logging and calls `main()` in `cli.py`. `main()` loads your habits, runs the command, and saves if anything changed.

### Your must-have checklist

- [ ] A real package, run with `python -m streaks`
- [ ] `add`, `done` and `status` work. `stats` and `remove` too
- [ ] A `@dataclass Habit` with a name, a created date and a set of done dates
- [ ] Current and best streaks, and not having done it yet today doesn't break your streak
- [ ] A heatmap of the last 12 weeks, using `defaultdict`, `Counter` and `groupby`
- [ ] A `@command` decorator that registers each command in a dictionary
- [ ] Saving through an atomic-write context manager, so a crash can't break `habits.json`
- [ ] Logging to `streaks.log`
- [ ] Tests for the awkward dates (a one-day gap, a month boundary, a leap year, a habit created today), and every test passing

---

## Building it, one step at a time

Each unfinished function has a *placeholder*, a line that keeps everything running before you've written it. You can run the program and the tests at any time. Replace the placeholder with your own code.

### Part 1: Tests first

The spec for this project says: *date logic is where most bugs hide, so write the streak tests before the streak function.* That's exactly where we start.

#### Step 1: Write three tests (`tests/test_habits.py`)

Open `tests/test_habits.py`. Most of the tests are already there. Three of them are empty and say `pytest.skip`. Those three are yours to write.

A test is just a function whose name starts with `test_`, containing `assert` statements:

```python
def test_streak_across_a_month_boundary():
    habit = make_habit(date(2026, 9, 29), date(2026, 9, 30), date(2026, 10, 1))
    assert habit.current_streak(date(2026, 10, 1)) == 3
```

pytest finds every `test_` function and runs it. If every `assert` is true, the test passes. If one is false, pytest shows you both values, so you can see what went wrong.

Write the three tests, delete the `pytest.skip` lines, and run `python -m pytest -k "month_boundary or leap_day or created_today"`. **They should fail.** You haven't written the streak code yet, so `current_streak()` still returns its placeholder, 0. Seeing a test fail first proves it's really testing something. A test that has never failed might not be checking anything at all.

Have a look at `test_current_streak` too. `@pytest.mark.parametrize` runs the same test once for each row of the table, so one short function checks eight different situations.

### Part 2: The streak maths (`streaks/habits.py`)

First, read the `Habit` class at the top. `@dataclass` writes the boring parts of a class for you (`__init__`, a readable `__repr__`, and `==`) just from the list of fields:

```python
@dataclass
class Habit:
    name: str
    created: date
    done: set[date] = field(default_factory=set)
```

Why not `done: set[date] = set()`? It's the same trap you met with `locked={}` in Project 3: one default set would be shared by every habit. Dataclasses are so worried about this that they refuse to run if you try it. `field(default_factory=set)` means "call `set()` to make a new one for each habit".

#### Step 2: `mark_done`

A day is either done or not, so `done` is a set. Return `False` if the day was already there, so the `done` command can say "you've already done that today".

#### Step 3: `current_streak`

This is the heart of the project:

```python
if today in self.done:
    day = today
else:
    day = today - ONE_DAY          # not done yet today, so start from yesterday
```

Then step backwards one day at a time while each day is in `self.done`, counting as you go. `ONE_DAY` is `timedelta(days=1)`. Taking it away from a date gives the day before, and Python handles the hard parts for you: month ends, leap years and New Year.

**Check it:** `python -m pytest -k "month_boundary or leap_day or created_today"`. Your three tests from Step 1 should pass now. (The longest-streak tests still fail. That's Step 4.)

#### Step 4: `longest_streak`

Sort the days (sets have no order), then walk through them. If a day is exactly one day after the one before, the run keeps going. Otherwise a new run starts at 1. Remember the longest run you see.

#### Steps 5 and 6: `to_dict` and `from_dict`

`json` only knows about text, numbers, lists and dictionaries. It has no idea what a `date` or a `set` is. So `to_dict()` turns them into things json understands:

```python
date(2026, 10, 19).isoformat()          # "2026-10-19"
date.fromisoformat("2026-10-19")        # date(2026, 10, 19)
```

`from_dict` is a `@classmethod`: you call it on the class itself, as `Habit.from_dict(data)`, because there's no habit yet to call it on. Inside it, `cls` means `Habit`.

#### Step 7: `find_habit`

This is what lets you type `done read` instead of `done "read 20 pages"`. The rules:

1. An exact name always wins. If you have habits called `run` and `running club`, typing `run` means `run`.
2. Otherwise the text has to match the **start** of exactly one name.
3. If it matches none, or more than one, raise `StreaksError` with a helpful message.

### Part 3: Saving safely (`streaks/storage.py`)

#### Step 8: `atomic_write`

Imagine your laptop's battery dies while `habits.json` is being written. Half the file is new, the other half is gone, and months of streaks are lost. An **atomic** write makes that impossible:

1. Write everything to a temporary file, `habits.json.tmp`.
2. Only when that's completely finished, swap it into place with `os.replace()`. That's a single step, so there's never a moment when `habits.json` is half-written.

`@contextmanager` turns a function with one `yield` into something you can use with `with`. Everything before the `yield` runs when the `with` block starts. Whatever the caller does in their `with` block happens *at* the `yield`. Everything after it runs when the block ends.

```python
temp = path.with_name(path.name + ".tmp")
try:
    with open(temp, "w", encoding="utf-8") as file:
        yield file
    os.replace(temp, path)
finally:
    if temp.exists():
        temp.unlink()
```

**Why the `try` and `finally`?** If the caller's code raises an exception, it comes out of the `yield`. Without a `try`, everything after the `yield` is simply skipped: no `os.replace`, which is good, but also no tidying up, so a `.tmp` file is left lying around. The `finally` runs whatever happens. After a successful `os.replace` the temp file has gone, so if it still exists, something went wrong, and you delete it.

**Check it:** `python -m pytest tests/test_storage.py`. One test pretends the power goes off halfway through a write. It checks that the old file survives, and that no `.tmp` file is left behind. The placeholder fails that test. Yours should pass it.

#### Step 9: `load_habits`

- No file yet just means no habits yet: return `{}`.
- A **damaged** file is different. Raise `StreaksError`, and don't touch the file. If the program carried on with no habits and then saved, it would overwrite your whole history with nothing. Better to stop and tell you.

Broken JSON raises `json.JSONDecodeError`, which is a kind of `ValueError`. A bad date like `"2026-13-45"` raises `ValueError` too. So `except (ValueError, KeyError, TypeError)` catches every way the file can be wrong.

#### Step 10: `save_habits`

Build the data with `to_dict()`, and write it inside `with atomic_write(path) as file:`. Then log what happened.

### Part 4: Commands (`streaks/cli.py`)

#### Step 11: The `@command` decorator

In Project 3, you built the command table by hand: `{"go": self.go, "take": self.take, ...}`. Every new command meant remembering to add a line to it. A decorator can do that for you.

Writing `@command` above a function:

```python
@command
def add(habits, args, today):
    ...
```

is exactly the same as writing this underneath it:

```python
add = command(add)
```

So `command()` is called once for each command, when Python first reads `cli.py`. It gets the function, stores it in `COMMANDS` under its own name (`func.__name__` is `"add"`), and hands it back unchanged.

Now adding a new command really is just writing one decorated function. `main()` finds it in `COMMANDS`, and the help text picks it up from its docstring.

**Check it:** `python -m streaks` should now list five commands. Before this step, it lists none.

#### Steps 12 and 13: `add` and `done`

Every command gets the same three things: the habits, the extra words you typed, and today's date. It returns `True` if it changed something, so `main()` knows whether to save. `done` uses your `find_habit()` and `mark_done()` from Part 2.

Problems are raised as `StreaksError`, not printed. `main()` catches them, prints the message, and returns exit code 1. You can see exit codes in the terminal: run a command, then `echo $?` (Mac and Linux) or `echo %errorlevel%` (Windows Command Prompt). 0 means it worked.

**Check it:** `python -m streaks add "read 20 pages"`, then `python -m streaks done read`, then `python -m streaks status`. Then look inside `streaks.log`.

### Part 5: The heatmap (`streaks/heatmap.py`)

#### Step 14: `shade`

`·` none, `░` some, `▓` at least half, `█` all. With one habit, every day is either `·` or `█`.

#### Step 15: `heatmap`

The heatmap has one **row** per day of the week, and one **column** per week. Two tools from chapter 15 make it short:

- A **`Counter`** counts how many habits were done on each day. It's a dictionary that starts every key at 0, so `counts[day]` works even for a day nobody touched.
- A **`defaultdict(list)`** holds the rows. The first time you use `rows[0]` (Monday), it makes an empty list for you, so there's no "is this row there yet?" check.

```python
for day in days:
    rows[day.weekday()].append(shade(counts[day], len(habits)))
```

`day.weekday()` is 0 for Monday and 6 for Sunday. The days are in order, so each row fills up one week at a time, left to right.

#### Step 16: `month_header`

`groupby()` from `itertools` groups items that sit **next to each other** and share the same key. The Mondays are in date order, so all of August's Mondays are together, then all of September's:

```python
for month, group in groupby(mondays, key=lambda monday: monday.strftime("%b")):
```

That gives `"Aug"` with its 5 Mondays, then `"Sep"` with 4, and so on. Each week is 2 characters wide, so each month name gets `2 * len(list(group))` characters.

The "next to each other" part matters. `groupby` only looks at neighbours. Give it `["a", "b", "a"]` and you get three groups, not two. It works here only because the dates are in order.

### Part 6: Stats (`streaks/habits.py` again)

#### Step 17: `completion_rate`

Days done ÷ days since you created the habit. Count the created day itself, or a habit started today and done today would come out at 1 ÷ 0.

#### Step 18: `weekday_counts`

Another `Counter`: for every check-in, add 1 to that weekday's name. The `stats` command (already written) then asks `counts.most_common(1)` for your best day.

**Check it:** `python -m pytest`. Everything should pass.

---

## The big idea: never ask the clock inside your logic

Look at how `current_streak` gets today's date:

```python
def current_streak(self, today: date) -> int:
```

It's **given** `today`. It never calls `date.today()` itself. Nothing in `habits.py` or `heatmap.py` does. Only `main()` asks the clock, once, and passes the answer down.

That one decision is what makes this project testable. To check the leap year, a test just says:

```python
assert leap.current_streak(date(2024, 3, 1)) == 3
```

If `current_streak` called `date.today()` itself, how would you test 1 March 2024? Or New Year's Day? Or "what happens tomorrow if I don't do it today?" You'd have to wait for those dates to come round, or change your computer's clock. Because `today` is passed in, a test can pretend it's any day it likes.

`main()` works the same way: `main(argv, data_file, today)`. The real program uses your real `habits.json` and the real date. The tests in `test_cli.py` pass in a temporary file and a made-up date, so they can never mess up your actual habits, and they give the same result whatever day you run them.

This idea, passing in the things a function depends on instead of letting it reach out and grab them, is worth taking into every project you write.

### Logging, and why it's only set up in one place

Each file gets its own logger with `logging.getLogger(__name__)`, and writes to it with lines like:

```python
logger.info("Marked %r done on %s", habit.name, today)
```

But **where** the messages go (the `streaks.log` file, and the format with the time) is set up just once, in `__main__.py`. That file only runs when you use `python -m streaks`. The tests import the other files directly, so they never write a log file. A package's own code should *log*. Only the program's entry point should decide where the logs go.

Open `streaks.log` after using the program for a bit. It's a diary of everything that happened, with times. That's very handy when you're trying to work out why yesterday's streak looks wrong.

### Type hints, and checking them

The code has **type hints**, like `def current_streak(self, today: date) -> int:`. Python itself ignores them. They're notes for people, and for tools. If you'd like to check them (chapter 19), install mypy and run it:

```bash
python3 -m pip install mypy
python3 -m mypy streaks
```

Try passing a string where a date should go, and see what mypy says.

---

## Try to break it

Each of these should give a clear message, not a traceback:

- [ ] `python -m streaks done` with no habit, and `python -m streaks done swim` for one that doesn't exist
- [ ] Add `read` and `run`, then type `python -m streaks done r`. Which one did you mean?
- [ ] `python -m streaks add READ` when you already have `read`
- [ ] Mark the same habit done twice in one day
- [ ] Open `habits.json`, type some rubbish into it, and run `status`. Check the file afterwards: it should be exactly as you left it
- [ ] Delete `habits.json`. You should simply start again with no habits
- [ ] `cd ..` out of `starter/` and run `python -m streaks status`. Why doesn't it work? (See [Using it](#using-it).)
- [ ] `python -m streaks dance`, then `echo $?`. It should be 2
- [ ] Read `streaks.log`. Can you see everything you just did?

---

## Stretch goals

Finished? Pick one. There's no solution for these, and remember: **tests first**.

### 1. Proper `--help` with `argparse`

`argparse` is the standard library's tool for command-line arguments. It gives you `--help`, error messages for wrong arguments, and more.

- Make a parser with `argparse.ArgumentParser(prog="python -m streaks")`, then `subparsers = parser.add_subparsers(dest="command", required=True)`.
- Loop over `COMMANDS` and add one subparser for each: `subparsers.add_parser(name, help=...)`. Use the first line of the docstring for the help, just like `usage()` does. Your decorator registry still does the work.
- Give each subparser `add_argument("words", nargs="*")`, so `add read 20 pages` still works.

### 2. Weekly targets

Some habits aren't daily: "gym 3 times a week".

- Add a field `per_week: int | None = None` to `Habit`. In `from_dict`, use `data.get("per_week")`, so your old `habits.json` still loads.
- A weekly streak counts **weeks** in a row where the target was met. `week_start()` in `heatmap.py` and a `Counter` will group the days into weeks for you.
- The same midnight rule applies, but for weeks: this week isn't a failure until Sunday is over.
- Write the tests first. What should happen in a week split across two months? Or across New Year?

### 3. Catching up on missed days

You went for a run yesterday but forgot to type it in. Let `done` take a date: `python -m streaks done run --date 2026-10-18`.

- In `done`, check whether the last two words are `--date` and a date, and use `date.fromisoformat()` on the date.
- Refuse dates in the future, and dates before the habit was created.
- Bonus: accept the word `yesterday` too.

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 10. Files and JSON | `habits.json`, with `to_dict` and `from_dict` for the types json doesn't know |
| 11. Modules and packages | a real package, `__init__.py`, `__main__.py`, `python -m`, importing between files |
| 13. Decorators | the `@command` registry, and what `@` really does |
| 14. Context managers | `atomic_write`, with `@contextmanager`, `yield` and `finally` |
| 15. The standard library | `@dataclass`, `field(default_factory=...)`, `date`, `timedelta`, `Counter`, `defaultdict`, `groupby` |
| 19. Writing reliable code | type hints, docstrings, `logging`, `pytest`, `parametrize`, `tmp_path`, tests first |
