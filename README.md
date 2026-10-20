# Python Practice Projects

Seven practice projects for learning Python, ordered from beginner to intermediate. Each one is a small program you'd actually want to use or show off: a quiz game, a holiday bill splitter, a text adventure, a habit tracker, a "Wrapped" report for your group chat, a Pokémon team builder that talks to a real API, and a quote game built on a website you scrape yourself.

<p>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="7 projects" src="https://img.shields.io/badge/projects-7-F37626">
  <img alt="tests: pytest" src="https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white">
</p>

The projects go with the **[Python Programming Series](https://github.com/shikharkumar13/Python-Programming-Code)**, a 20-chapter course from first literals to a tested, packaged program ([read the articles](https://shikharkumar13.github.io/Python-Programming-Code/index.html)). Each project practises a handful of the course's chapters, and together they cover chapters 1 to 19. You don't have to follow the course, though. If you know the Python each project lists, you can start there.

---

## Contents

- [The projects at a glance](#the-projects-at-a-glance)
- [How each project works](#how-each-project-works)
- [Getting started](#getting-started)
- [The seven projects](#the-seven-projects)
- [Which chapters each project practises](#which-chapters-each-project-practises)
- [Repository layout](#repository-layout)
- [Tips](#tips)

---

## The projects at a glance

| # | Project | Level | What you build | Steps | Tests |
|--:|---------|-------|----------------|------:|------:|
| 1 | [Trivia Night](01-trivia-night/) | Beginner | a terminal quiz with lifelines, streak bonuses and saved high scores | 14 | none |
| 2 | [Trip Splitter](02-trip-splitter/) | Beginner+ | who owes whom after a holiday, in the fewest payments | 12 | none |
| 3 | [Dungeon Escape](03-dungeon-escape/) | Beginner → Intermediate | a text adventure with classes, fights and saved games | 17 | none |
| 4 | [Streaks](04-streaks/) | Intermediate | a habit tracker with streaks and a GitHub-style heatmap | 18 | 63 |
| 5 | [Chat Wrapped](05-chat-wrapped/) | Intermediate | a "Spotify Wrapped" report for a WhatsApp group chat | 14 | 71 |
| 6 | [PokéDex Team Builder](06-pokedex/) | Intermediate | a Pokémon team builder and battle simulator, using a real API | 18 | 148 |
| 7 | ["Who Said It?"](07-who-said-it/) | Intermediate (capstone) | a quote-guessing game, built from a website you scrape | 18 | 154 |

**Steps** is the number of numbered TODOs in each starter. **Tests** is the number of pytest tests that pass in the finished solution.

---

## How each project works

Every project folder has the same three parts:

- **`README.md`, the guide.** It explains the problem in plain English. Then it walks you through building it, one numbered step at a time, with a hint for each step and a **Check it** line that tells you how to test what you've just written. It also has a must-have checklist, the one big idea the project is about, a "Try to break it" list of things to test by hand, and stretch goals.
- **The starter, where you work.** Every function you need to write is already there, with its name, its arguments and a docstring saying what it does. The body is a numbered `# TODO` with hints, and a *placeholder* that keeps the program running. You can run the starter at every stage, with nothing filled in, half done or finished, and it never crashes. The placeholders just say what's not written yet.
- **The solution, the finished program.** Have a real go first. When you're stuck, compare one function, not the whole file.

**Projects 1 to 3** are single files: `starter.py` and `solution.py`. Each one comes with its sample data, like a questions file, a CSV of expenses, or a dungeon map in JSON.

**Projects 4 to 7** are Python packages, run with `python -m`. Each one has a `starter/` folder and a `solution/` folder, and each of those has the package, its `tests/` and its sample data. Most tests fail when you start, and each one passes as you finish the step it checks. One step in each project asks you to **write a couple of tests yourself, before** the code they test. They're aimed at the bug that's easiest to make in that project.

**Stretch goals** come with hints, but no code. They're for when you've finished and want more.

**Nothing needs your personal data, and the tests never touch the internet.** Projects 6 and 7 ship with saved answers from the API and saved pages from the website, so every command works offline straight away. Project 5's chat is completely made up.

---

## Getting started

You need **Python 3.10 or newer**. Check with `python3 --version` (on Windows, `py --version`).

```bash
git clone https://github.com/shikharkumar13/Python-Projects.git
cd Python-Projects
```

**Projects 1 to 3 need nothing installed.** Go into a project's folder and run the starter:

```bash
cd 01-trivia-night
python3 starter.py              # on Windows: py starter.py
```

**Projects 4 to 7 need a virtual environment** for pytest (and, in projects 6 and 7, `requests` and `beautifulsoup4`). Work inside the project's `starter/` folder:

```bash
cd 04-streaks/starter
python3 -m venv .venv                     # on Windows: py -m venv .venv
source .venv/bin/activate                 # on Windows: .venv\Scripts\activate
python -m pip install pytest              # projects 4 and 5
python -m pip install -r requirements.txt # projects 6 and 7 instead
python -m pytest                          # run the tests
```

Once the virtual environment is active, plain `python` works on every computer. Each project's README has the exact commands.

---

## The seven projects

### 1. Trivia Night

**Beginner · chapters 1–6, 9 and 10 · [open the project](01-trivia-night/)**

You're hosting quiz night for friends, and you want a game that keeps score, gets harder as you go, and remembers who holds the high score.

- 18 questions loaded from `questions.json`, easy ones first and hard ones last, with the options shuffled
- points that depend on difficulty, and double after 3 right answers in a row
- a 50/50 lifeline you can use once per game
- input checking, so a typo never crashes the game
- the top 5 scores, saved to a file
- **The big idea:** keeping score without global variables

```bash
cd 01-trivia-night && python3 starter.py
```

### 2. Trip Splitter

**Beginner+ · chapters 2–7, 9 and 10 · [open the project](02-trip-splitter/)**

Five friends went to Goa, and everyone paid for different things. Work out the *fewest* payments that settle everyone up.

- expenses read from a CSV file with `csv.DictReader`, with equal splits or custom shares (`Arjun:2`)
- money stored as whole paise, never as a float, so it always adds up exactly
- each person's balance worked out with a dictionary, then a greedy rule that settles the debts in as few payments as possible
- the payments saved to `settlement.csv` with `csv.DictWriter`
- a custom `InvalidExpense` exception, with the line number in every message, tested on a file full of mistakes
- copes with what Excel does to CSV files

```bash
cd 02-trip-splitter && python3 starter.py
```

### 3. Dungeon Escape

**Beginner → Intermediate · chapters 5–10, 12 and 13 · [open the project](03-dungeon-escape/)**

You wake up in a dungeon with a torch and 3 health points. Explore the rooms, pick up items, fight a goblin, find the key and escape. Then save your game, and come back tomorrow.

- the whole map in `dungeon.json`, so changing that file changes the game
- `Player`, `Room`, `Item` and `Enemy` classes, with `Goblin` and `Dragon` overriding `attack()`
- a command table: a dictionary that maps each word you type to a method
- turn-based fights using `random` with a seed, so a fight replays the same way
- save and load to JSON, a recursive check that the way out can be reached, and a generator of spooky events
- `__str__` for a status bar, and a custom `GameOver` exception

```bash
cd 03-dungeon-escape && python3 starter.py
```

### 4. Streaks

**Intermediate · chapters 10, 11, 13, 14, 15 and 19 · [open the project](04-streaks/)**

A habit tracker you run from the terminal. It counts your streaks, and draws a GitHub-style heatmap of your last 12 weeks.

- a package, run with `python -m streaks add "read 20 pages"`, `done read`, `status`, `stats` and `remove`
- a `@dataclass Habit`, with current and longest streaks worked out with `datetime` and `timedelta`
- the commands registered by a decorator, and the data saved with an atomic write-then-rename context manager
- logging to a file, type hints checked with mypy, and pytest tests, starting with tests you write for awkward dates

```bash
cd 04-streaks/starter && python -m streaks status
```

### 5. Chat Wrapped

**Intermediate · chapters 7, 10, 12, 15 and 16 · [open the project](05-chat-wrapped/)**

Export a WhatsApp group chat, and get a funny yearly report: The Chatterbox, Emoji of the Year, The Night Owl, The Lightning Replier, The Great Silence and Words of the Year.

- a `re.VERBOSE` regular expression with named groups that reads each message line
- multi-line messages joined up, system lines skipped, and the last message never lost, with the tests for the two classic bugs written by you, first
- a generator that reads one message at a time, so a chat of 200,000 messages takes no more memory than one of 200
- `Counter`, `defaultdict`, `datetime`, `timedelta` and `itertools.pairwise` for the awards
- the report saved as Markdown
- a completely made-up sample chat, because real chats are other people's words

```bash
cd 05-chat-wrapped/starter && python -m wrapped sample_chat.txt
```

### 6. PokéDex Team Builder

**Intermediate · chapters 8, 9, 11–15, 17 and 19 · [open the project](06-pokedex/)**

Use the free [PokéAPI](https://pokeapi.co) to build a team whose types cover each other's weaknesses, then make two teams battle.

- a polite API client: a `requests.Session`, a named User-Agent, a timeout on every request, and every answer cached on disk, so asking again costs nothing
- a `@retry` decorator factory with exponential backoff, for timeouts and server errors only
- a `PokemonNotFound` exception for a 404, which is never retried
- a generator that pages through the API by following each page's `next` link, and a client that works with `with`
- `Pokemon`, `Move` and `Team` classes, and a type chart built from the API
- `itertools.combinations` to find the best team, and `functools.lru_cache` to save repeated work
- a turn-based battle simulator, seeded so a battle replays exactly
- **The big idea:** when something fails, should you try again? It depends on whose fault it was

```bash
cd 06-pokedex/starter && python -m pokedex battle pikachu,lapras,gengar charizard,venusaur,machamp 42
```

### 7. "Who Said It?"

**Intermediate, the capstone · nearly every chapter, especially 11, 12, 16, 18 and 19 · [open the project](07-who-said-it/)**

Scrape every quote and author from [quotes.toscrape.com](https://quotes.toscrape.com), a site built for practising scraping, and turn it into a game. You see a quote and get 4 guesses to name the author. Each wrong guess unlocks a hint: when they were born, then where, then their initials.

- polite scraping: `robots.txt` checked first, a named User-Agent, a pause between requests, and every page cached, so the site is only scraped once
- a generator that follows the "Next →" link from page to page
- BeautifulSoup with CSS selectors, and every field read through a safe helper, so a missing piece is skipped and logged instead of crashing
- birth dates parsed with `strptime`, and the curly quotes removed with a regex
- `Quote` and `Author` dataclasses that check their own data, saved with an atomic write
- forgiving guesses: "einstein" for Albert Einstein, "rowling" for J.K. Rowling, accents optional
- a `stats` command with the most quoted authors, the top tags and quotes by decade, using `Counter`
- **The big idea:** a web page is not an API, so expect the unexpected

```bash
cd 07-who-said-it/starter && python -m whosaidit scrape && python -m whosaidit play
```

---

## Which chapters each project practises

The chapter numbers are the [Python Programming Series](https://github.com/shikharkumar13/Python-Programming-Code)'s. The early projects stick to the chapters they build on. Project 1 has no classes, for example, because classes are chapter 8. The later ones assume everything that comes before.

| Ch | Topic | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|--:|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Introduction to Python | ✓ | | | | | | |
| 2 | Lists, tuples and strings | ✓ | ✓ | | | | | |
| 3 | Sets and dictionaries | ✓ | ✓ | | | | | |
| 4 | Operators | ✓ | ✓ | | | | | |
| 5 | Conditionals and loops | ✓ | ✓ | ✓ | | | | |
| 6 | Functions | ✓ | ✓ | ✓ | | | | |
| 7 | Lambda, `key=` and recursion | | ✓ | ✓ | | ✓ | | |
| 8 | Object-oriented programming | | | ✓ | | | ✓ | |
| 9 | Exceptions | ✓ | ✓ | ✓ | | | ✓ | ✓ |
| 10 | Files, CSV and JSON | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ |
| 11 | Modules, packages and virtual environments | | | | ✓ | | ✓ | ✓ |
| 12 | Iterators and generators | | | ✓ | | ✓ | ✓ | ✓ |
| 13 | Closures and decorators | | | ✓ | ✓ | | ✓ | |
| 14 | Context managers | | | | ✓ | | ✓ | ✓ |
| 15 | `collections`, `itertools`, `functools`, `datetime`, `dataclass` | | | | ✓ | ✓ | ✓ | ✓ |
| 16 | Regular expressions | | | | | ✓ | | ✓ |
| 17 | Working with APIs | | | | | | ✓ | ✓ |
| 18 | Web scraping | | | | | | | ✓ |
| 19 | Type hints, logging and pytest | | | | ✓ | | ✓ | ✓ |

The basics in chapters 1 to 6 are used everywhere, of course. The table marks where each one is *practised*. Each project's README ends with a "What you practised" table, which says exactly where each chapter shows up.

---

## Repository layout

```
.
├── 01-trivia-night/            README.md, starter.py, solution.py, questions.json
├── 02-trip-splitter/           README.md, starter.py, solution.py, friends.txt, two expense CSVs
├── 03-dungeon-escape/          README.md, starter.py, solution.py, dungeon.json
│
├── 04-streaks/                 from here on, each project is a package:
│   ├── README.md               the guide
│   ├── starter/                ← you work in here
│   │   ├── streaks/            the package
│   │   ├── tests/              the tests
│   │   └── pytest.ini
│   └── solution/               the same, finished
├── 05-chat-wrapped/            the same shape, with a made-up sample chat
├── 06-pokedex/                 the same shape, with saved PokéAPI answers in cache/
└── 07-who-said-it/             the same shape, with the saved website in html_cache/
```

The starter and the solution each keep their own data files and logs, so working in one never changes the other.

---

## Tips

- **Read the project's README first,** then do the steps in order. Each step builds on the one before, and each **Check it** line tells you when you're done.
- **Messages like "… is TODO 5." aren't bugs.** They're the placeholders saying which step comes next.
- **In projects 4 to 7, use the terminal, not the ▶ button in VS Code.** The ▶ button runs one file on its own, and then the files in the package can't find each other. In projects 1 to 3, the ▶ button works fine.
- **`python`, `python3` or `py`?** Inside an active virtual environment, `python` works everywhere. Without one, use `python3` on Mac and Linux, and `py` on Windows.
- **Play with your own data.** Your own WhatsApp export in project 5 is fine, but keep it, and its report, on your own computer. Never commit someone's messages. If you point project 7's scraper at another site, read that site's `robots.txt` and terms first.
- **Stuck?** Compare just the one function with the solution. Then close the solution and write it yourself.
