# Project 7: "Who Said It?"

**Level:** Intermediate (the capstone) · **Uses chapters:** nearly all of them, especially 11, 12, 16, 18 and 19

[quotes.toscrape.com](https://quotes.toscrape.com) is a website built for people learning to scrape. It has 100 famous quotes, spread over 10 pages, and a page about each author. In this project you'll scrape all of it, politely, and turn it into a game:

```
“A lie can travel half way around the world while the truth is putting on its shoes.”
Tags: truth
Guess 1 of 4. Who said it? oscar wilde
Not quite. Hint: They were born on 30 November 1835.
Guess 2 of 4. Who said it? einstein
Not quite. Hint: They were born in Florida, Missouri, The United States.
Guess 3 of 4. Who said it? twain
Yes! It was Mark Twain. 2 points.
Score: 2 out of 4.
```

You get 4 guesses for each quote. Each wrong guess unlocks a hint: when the author was born, then where, then their initials. "twain" is good enough for Mark Twain, and "rowling" for J.K. Rowling.

This is the last project, and it uses almost everything from the course: a package, a generator that follows links, regular expressions, BeautifulSoup, dataclasses that check their own data, custom exceptions, logging, an atomic save, type hints and tests.

> **Scrape kindly.** This site exists so that people can practise on it. Before you point a scraper at any other site, read its `robots.txt` and its terms, and keep to the same good manners this project uses: say who you are, wait between requests, and never download the same page twice.

---

## What's in this folder

```
07-who-said-it/
├── README.md                this guide
├── starter/                 ← you work in here
│   ├── whosaidit/           the package
│   │   ├── __main__.py      runs when you type: python -m whosaidit
│   │   ├── cli.py           the three commands: scrape, play and stats
│   │   ├── scrape.py        fetches pages politely, following "Next →"
│   │   ├── parse.py         BeautifulSoup: HTML into dictionaries
│   │   ├── models.py        the Quote and Author dataclasses, which check their data
│   │   ├── storage.py       saving and loading quotes.json, atomically
│   │   ├── game.py          the game: matching guesses, hints and scores
│   │   ├── stats.py         counting authors, tags and decades
│   │   └── errors.py        the package's own exceptions
│   ├── tests/               the tests, and saved pages for them in tests/fixtures/
│   ├── html_cache/          every page of the site, already saved, so you can start offline
│   ├── requirements.txt     the packages this project needs
│   └── pytest.ini
└── solution/                the same, finished. Have a real go first!
```

## Getting set up

Everything happens inside `starter/`:

```bash
cd starter
python3 -m venv .venv                  # on Windows: py -m venv .venv
source .venv/bin/activate              # on Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

The first line uses `python3` (or `py`), because the virtual environment doesn't exist yet. Once it's active, plain `python` works on every computer, so the rest of this guide uses that. `requirements.txt` asks for `requests`, `beautifulsoup4`, `pytest`, `mypy` and `types-requests`.

## Using it

```bash
python -m whosaidit scrape        # get every quote and author, and save them in quotes.json
python -m whosaidit play          # the game. Type quit to stop
python -m whosaidit play 7        # the same order of quotes every time you use 7
python -m whosaidit stats         # the most quoted authors, the top tags, and quotes by decade
```

Run `scrape` first. It saves everything in `quotes.json`, and `play` and `stats` read that file.

**The cache.** `html_cache/` already holds every page of the site: the 10 pages of quotes, the 50 author pages, and `robots.txt`. So `scrape` works straight away, without the internet, and makes **zero** requests:

```
$ python -m whosaidit scrape
Saved 100 quotes by 50 authors to quotes.json.
Requests to the site: 0. Pages from html_cache/: 60.
Now play with: python -m whosaidit play
```

To see the real thing, delete `html_cache/` and run `scrape` again. It now makes 61 requests, one second apart, so it takes a minute or two. Run it once more, and it's back to zero. If it's stopped halfway (no internet, or Ctrl+C), the pages it already has are kept, so running it again carries on where it stopped.

**The log.** Every real request, and every item that's skipped (with the reason), is written to `whosaidit.log`, next to `html_cache/`.

**The ▶ button in VS Code won't work for this project.** It runs one file on its own, as if you'd typed `python whosaidit/__main__.py`, and then the files in the package can't find each other. Use the terminal.

## Running the tests

```bash
python -m pytest                                          # everything
python -m pytest tests/test_parse.py -v                   # one file, test by test
python -m pytest tests/test_game.py::test_initials        # one test
python -m mypy whosaidit                                  # check the type hints
```

Most tests fail when you start. Each one passes as you finish the step it checks.

**No test ever touches the internet.** The parsing tests read real pages saved in `tests/fixtures/`, plus two made-up broken ones, `broken_page.html` and `broken_author.html`, with pieces missing on purpose. The scraping tests use `FakeSite` from `tests/fakes.py`: a pretend website, built from a dictionary of URLs and their HTML, that answers 404 for anything else and remembers every request. And `conftest.py` stops the scraper's pauses from really waiting.

---

## How it works

### The site

A page of quotes looks like this. (It's simplified a little. Open `html_cache/index.html` in VS Code to see the real thing.)

```html
<div class="quote">
  <span class="text">“The world as we have created it is a process of our thinking. ...”</span>
  <span>by <small class="author">Albert Einstein</small>
        <a href="/author/Albert-Einstein">(about)</a></span>
  <div class="tags">
    Tags: <a class="tag" href="/tag/change/page/1/">change</a> <a class="tag" ...>thinking</a>
  </div>
</div>
...
<li class="next"><a href="/page/2/">Next <span>→</span></a></li>
```

Each quote is a `div.quote`, and **CSS selectors** (chapter 18) pick out its pieces: `span.text` is the quote, `small.author` the author, and `a.tag` each tag. At the bottom, `li.next > a` links to the next page. The last page has no such link. That's how you know it's the last.

Each author's page has their name in `h3.author-title`, their birth date in `span.author-born-date` ("March 14, 1879") and their birthplace in `span.author-born-location` ("in Ulm, Germany").

### Being polite

`Scraper` in `scrape.py` does all the fetching, and it behaves like a good guest:

- **`robots.txt` first.** A site puts its rules for programs in `/robots.txt`. Python's `RobotFileParser` reads them, and `can_fetch()` says whether a URL is allowed. This site doesn't have a `robots.txt` (a 404), and that means everything is allowed. A `robots.txt` that we're *not allowed to read* (401 or 403) means the opposite: keep out.
- **A `User-Agent`** that says who's asking: `whosaidit/1.0 (a Python course practice project)`.
- **A pause between requests.** `time.sleep(1.0)` before every request except the first. If `robots.txt` asks for a longer `Crawl-delay`, the scraper uses that instead.
- **A timeout** on every request, so a server that never answers can't make the program wait forever.
- **It stays on the site.** A site's `robots.txt` only speaks for that site, so a link to anywhere else is never followed.
- **A cache.** Every page is saved in `html_cache/` the first time. After that, the site is never asked for it again.

### From HTML to data

Web pages make no promises. A site can change its HTML tomorrow, or leave a piece out of one quote. So:

- **Every field goes through a safe helper.** `text_of(box, "small.author")` gives the text, or `None` if it isn't there. (That's chapter 18's `text_of` pattern.) A quote with a missing piece is **skipped and logged**, not allowed to crash the whole scrape.
- **The curly quotes come off** with a regular expression: `“Like this.”` becomes `Like this.`. The game puts them back when it shows the quote.
- **Dates become real dates.** `datetime.strptime("March 14, 1879", "%B %d, %Y")` gives a `datetime`, which can be compared, sorted and turned into a decade. A date in any other form is logged, and left as `None`.
- **`Quote` and `Author` check themselves.** They're dataclasses with a `__post_init__` method, which runs straight after `__init__`. A quote with no text raises `ValidationError`, so a broken `Quote` can never exist.
- **Quotes are matched to their authors by the link, not the name.** On the quote pages he's "Alexandre Dumas fils", but his own page calls him "Alexandre Dumas-fils". Names are written by people, and people aren't consistent. The link `/author/Alexandre-Dumas-fils` is the same everywhere, so the last part of it, the **slug**, is the key.

### Matching guesses

`is_match(guess, name)` is forgiving about everything except the name itself:

| Guess | Matches | Why |
|---|---|---|
| `einstein`, `EINSTEIN`, `Albert Einstein` | Albert Einstein | capitals and spaces at the ends don't matter, and the surname is enough |
| `rowling`, `jk rowling`, `j.k. rowling` | J.K. Rowling | dots and spaces inside the name don't matter either |
| `andre gide` | André Gide | accents don't matter |
| `king` | Martin Luther King Jr. | "Jr." isn't a surname, so it's skipped |
| `albert` | **not** Albert Einstein | a first name isn't enough: there could be lots of Alberts |
| `stein`, `einstien` | **not** Albert Einstein | part of a word, or a typo |

It works by **normalising** both names first: no accents, lowercase, no punctuation, single spaces. Then it compares them, with the spaces taken out.

### The game

Each round shows a quote, and its tags. Some tags would give the answer away, like `jane-austen` or `misattributed-mark-twain`, so any tag that shares a word with the author's name is hidden. You get 4 guesses, and 4 points for a first-guess answer, then 3, 2 and 1. Each wrong guess unlocks the next hint: the birth date, the birthplace, then the initials. Press Enter for another quote, or type `n`. Typing `quit`, or pressing Ctrl+C, stops at any time, and shows your score.

### Your must-have checklist

- [ ] A package, run with `python -m whosaidit scrape | play | stats`
- [ ] `robots.txt` checked with `RobotFileParser` before the first request
- [ ] A named `User-Agent`, a `time.sleep()` between requests, and every page cached, so the site is scraped once
- [ ] A generator that follows "Next →" from page to page, plus each author's page
- [ ] Every field read through a safe helper. Missing fields are skipped and logged, never crashing
- [ ] Birth dates turned into real dates with `strptime`, and curly quotes removed with a regex
- [ ] `@dataclass` `Quote` and `Author`, with validation in `__post_init__`
- [ ] `quotes.json` saved atomically, with a `scraped_at` timestamp
- [ ] Forgiving guesses: "einstein" for "Albert Einstein"
- [ ] A `stats` command with the most quoted authors, the top tags, and quotes per decade of birth, using `Counter`
- [ ] Tests for parsing, run against saved HTML, and for the guess matching. Every test passes

### How the package is organised

| File | What's in it | Your TODOs |
|---|---|---|
| `whosaidit/parse.py` | `text_of()`, cleaning, and parsing quote and author pages | 1–5 |
| `whosaidit/models.py` | `Quote` and `Author` | 6 |
| `whosaidit/storage.py` | `atomic_write()`, `save()` and `load()` | 7, 8 |
| `whosaidit/scrape.py` | `Scraper`: requests, `robots.txt`, the cache and the pages | 9–13 |
| `tests/test_game.py` | tests for the game | 14 |
| `whosaidit/game.py` | matching guesses, hints, and a round of the game | 15–17 |
| `whosaidit/stats.py` | the counting for `stats` | 18 |

`cli.py` and `errors.py` are already written, and so are some smaller pieces you'll use, like `attr_of()`, `Author`, `save()`, `cache_name()`, `hints()` and `play()`. Read them: they're worked examples for the TODOs next to them.

---

## Building it, one step at a time

Each unfinished part has a *placeholder* that keeps the program running. Until Step 13, `scrape` says `No quotes found`, and `play` and `stats` say there are no quotes yet. That's the placeholders talking. Nothing's wrong with the site.

### Part 1: Reading HTML (`parse.py`)

You can do all of Part 1 without a scraper. The tests hand your functions real pages from `tests/fixtures/`.

#### Step 1: `text_of`, the safe helper

```python
found = box.select_one("small.author")      # the first match, or None
```

`select_one()` gives `None` when there's no match. Calling `.get_text()` on `None` crashes with `AttributeError: 'NoneType' object has no attribute 'get_text'`, and that's the crash this whole project avoids. `text_of()` checks for `None` first. It also treats an empty element (`<small class="author"></small>`) as missing. `attr_of()`, just below it, is the same idea for attributes like `href`, and it's finished, as an example.

**Check it:** `python -m pytest tests/test_parse.py -k text_of`

#### Step 2: `QUOTE_MARKS` and `clean_quote`, with a regex

The site wraps every quote in curly quotes. Take them off with `QUOTE_MARKS.sub("", text)`. The pattern needs two halves, joined by `|` (or):

- `^[“"]+` means opening quote marks, curly or straight, at the **start** (`^`)
- `[”"]+$` means closing quote marks at the **end** (`$`)

Why not just `text.replace("“", "")`? Because that would also remove quote marks *inside* a quote, like `She said “hi” to me.` The `^` and `$` make sure only the ends are touched. Then `SPACES.sub(" ", text)` squashes any run of spaces and newlines into one space.

**Check it:** `python -m pytest tests/test_parse.py -k clean_quote`

#### Step 3: `parse_quotes`, a generator

For each `div.quote`, pull out the text, the author and the `(about)` link. The link is found with an attribute selector, `a[href*='/author/']`, which means "a link whose `href` contains `/author/`". If any of the three is missing, log a warning that says **which page, which quote and what's missing**, and skip it with `continue`. Otherwise, `yield` a dictionary.

The link is relative (`/author/Albert-Einstein`). `urljoin(page_url, link)` turns it into a full URL, the same way a browser does.

**Check it:** `python -m pytest tests/test_parse.py -k parse_quotes`. One of the tests runs on `broken_page.html` and checks the warnings in the log.

#### Step 4: `parse_born_date`, with `strptime`

```python
datetime.strptime("March 14, 1879", "%B %d, %Y").date()      # date(1879, 3, 14)
```

`%B` is the month's full name, `%d` the day and `%Y` a four-digit year. Anything that doesn't fit, even "February 30, 1900", raises `ValueError`. Catch it, log it, and return `None`. One odd date mustn't stop the other 49 authors.

**Check it:** `python -m pytest tests/test_parse.py -k born_date`

#### Step 5: `parse_author`

Use `text_of()` for the name, the birth date and the birthplace. Without a name, it isn't an author page, so log it and return `None`. The birthplace comes as `"in Ulm, Germany"`, so take the `in ` off the front with `.removeprefix("in ")`.

**Check it:** `python -m pytest tests/test_parse.py`. The whole file passes now. Look at `test_the_author_page_spells_some_names_differently` too: that's the Dumas-fils problem from [How it works](#from-html-to-data).

### Part 2: Data you can trust (`models.py` and `storage.py`)

#### Step 6: `Quote.__post_init__`

A dataclass writes `__init__` for you. If you also write `__post_init__`, it runs straight after, and it's the place to check the data. Raise `ValidationError` for a quote with no text, no author, no author slug, or an empty tag. `Author.__post_init__`, just above, is a finished example.

Because the dataclass is `frozen=True`, a `Quote` can't be changed once it's made. So once one exists, you know it's good, for ever.

**Check it:** `python -m pytest tests/test_models.py`

#### Step 7: `atomic_write`, a context manager

`@contextmanager` (chapter 14) turns a generator into something you can use with `with`. Everything before the `yield` runs when the `with` block starts, and everything after it runs when it ends:

```python
with atomic_write(path) as file:        # opens path.tmp
    json.dump(data, file)               # writes into path.tmp
# the block has ended: path.tmp replaces path, in one step
```

If the program crashes halfway through writing, only the `.tmp` file is half-written. The real `quotes.json` is untouched. `os.replace()` swaps the files in one step, so there's never a moment when the file is missing or only half there. Put the clean-up in a `finally`, so a leftover `.tmp` file is deleted even when an error is on its way out.

**Check it:** `python -m pytest tests/test_storage.py -k "atomic or crash"`

#### Step 8: `load`

`save()` is written for you. `load()` reads the file back. Turn each kind of failure into a `StorageError` with a message that says what to do:

- no file yet: run `scrape` first
- bad JSON, a missing key, or a quote that breaks the rules: the file is damaged, so scrape again
- any other `OSError`: say what went wrong
- a file with no quotes in it at all: there's nothing to play, so scrape again

**Check it:** `python -m pytest tests/test_storage.py`

### Part 3: The scraper (`scrape.py`)

#### Step 9: `download`, one polite request

Pause first (but not before the very first request), send the request with a timeout, and check the status. Two special cases come first:

- **`robots.txt` that we're not allowed to read (401 or 403) raises `NotAllowed`.** A site that hides its rules is saying "keep out".
- **With `missing_ok=True`, a 404 gives `""`.** A site with no `robots.txt` at all is the normal case, not an error.

Then the **encoding** (chapter 18). When a server doesn't say which character set it uses, `requests` guesses ISO-8859-1, and every `“` comes out as `â€œ`. If there's no `charset` in the `Content-Type` header, set `response.encoding = "utf-8"` before reading `response.text`.

**Check it:** `python -m pytest tests/test_scrape.py -k "download or charset"`

#### Step 10: `allowed`, with `RobotFileParser`

`_read_robots()` is written for you. It fetches `robots.txt` (from the cache, or with `download()`), and gives it to a `RobotFileParser`. Your `allowed()` reads it **once**, the first time it's asked, keeps it in `self.robots`, and then asks it `can_fetch(USER_AGENT, url)`. Also check `crawl_delay()`: if the site asks for a longer pause than ours, use theirs.

One trap: a `RobotFileParser` that has never been given a `robots.txt` says **no** to everything. If every page is suddenly "not allowed", check that you really did read it.

**Check it:** `python -m pytest tests/test_scrape.py -k test_allowed`

#### Step 11: `get`, with the cache

```
get(url)
  ├── on another site?  yes → raise NotAllowed
  ├── in html_cache/?   yes → return it. No request, so no robots.txt check, and no pause
  └── no → allowed?  no → raise NotAllowed
            └── yes → download() it → save it in html_cache/ → return it
```

The first check matters because `RobotFileParser` only looks at the *path* of a URL. Ask it about `https://elsewhere.example/author/X`, and it answers using quotes.toscrape.com's rules. `_read_cache()` and `_save()` are written for you. A cache file that can't be read is fetched again, and a page that can't be saved is still used, just not cached.

**Check it:** `python -m pytest tests/test_scrape.py -k "not quote_pages and not scrape_all"`

#### Step 12: `quote_pages`, a generator that follows links

Start at the front page. Fetch it, `yield` it, find the "Next →" link with `next_page_url()`, and go round again until there isn't one. Like `iter_pokemon()` in Project 6, it fetches a page only when the loop asks for it.

Two safety checks keep it from going wrong on a strange site:

- **A `seen` set.** If page 3's "Next" ever pointed back at page 2, a simple loop would go round for ever. Stop when you reach a page you've already seen.
- **Stay on the site.** If "Next" points at a different website, don't follow it. `urlparse(url).netloc` is the site part of a URL: `quotes.toscrape.com`.

In a generator, a bare `return` just means "no more values".

**Check it:** `python -m pytest tests/test_scrape.py -k quote_pages`

#### Step 13: `scrape_all`

Go through every page, turn each dictionary from `parse_quotes()` into a `Quote`, and skip (and log) any that `Quote` refuses. Keep a note of each author's page in a dictionary. `setdefault()` stores the first URL for each slug and ignores the rest, so each author's page is fetched once, however many quotes they have. Then fetch the author pages, and turn each into an `Author`. If an author's page is missing (`HTTPError`), or `robots.txt` asks us not to fetch it (`NotAllowed`), skip that author, and log why. Their quotes are still fine, and the game just gives vaguer hints.

**Check it:** `python -m pytest tests/test_scrape.py`, then `python -m whosaidit scrape`. It should say `Saved 100 quotes by 50 authors`, with 0 requests. Then `python -m whosaidit stats`, which has its first table now. The other two wait for Step 18, so until then the decades say `(No birth dates to count.)`.

### Part 4: The game (`game.py`)

#### Step 14: Two tests, before the matching (`tests/test_game.py`)

The guess matching is the part players will notice when it's wrong. So write its tests first. Find the two tests that say `pytest.skip` in `tests/test_game.py`:

1. **The surname is enough**, in any capitals: `"einstein"` and `"  EINSTEIN "` both match `"Albert Einstein"`.
2. **Part of a name isn't enough**: `"stein"` and `"albert"` don't match.

**Check it:** `python -m pytest tests/test_game.py -k "surname or part_of"`. The first test **fails**, as it should. The second one **passes already**, because the placeholder `is_match()` says `False` to everything. That's why you need both kinds of test. A function that always says no passes every "should be no" test. Only together do the two tests show that it really tells right from wrong.

#### Step 15: `normalise`

Make names easy to compare: `"  André GIDE "` becomes `"andre gide"`, and `"J.K. Rowling"` becomes `"jk rowling"`. The accents are the clever part. `unicodedata.normalize("NFKD", "é")` splits `é` into a plain `e` followed by a separate accent mark. Then a regex removes everything that isn't a letter, a digit or a space: the dots, the apostrophes, and the accent marks too. Without NFKD, the regex would remove the whole `é`, and "André" would become "andr".

**Check it:** `python -m pytest tests/test_game.py -k normalise`

#### Step 16: `is_match`

Normalise the guess, and take out its spaces. It's a match if it equals the whole name without spaces, or just the surname. `name_words()` is written for you: it gives the words of a name without a "Jr." or "fils" at the end, so the last word really is the surname.

**Check it:** `python -m pytest tests/test_game.py -k "match or part_of"`. Your two tests from Step 14 both pass now.

#### Step 17: `play_round`

Show the quote and its `visible_tags()`. Then up to 4 guesses: a right one scores `GUESSES - number + 1`, and a wrong one shows the next of the three hints. `ask_for_guess()` (written for you) keeps asking until the player types something, and raises `Quit` if they type `quit`.

`ask` and `say` are passed in, instead of calling `input()` and `print()` directly. In the real game they *are* `input` and `print`. In the tests, they're small functions that type pretend answers and collect what was said, so a whole game can be tested without anyone at the keyboard.

**Check it:** `python -m pytest tests/test_game.py`, then `python -m whosaidit play`

### Part 5: Stats (`stats.py`)

#### Step 18: `top_tags` and `quotes_per_decade`

`most_quoted()` is a finished example: `Counter(...).most_common(5)`. For the tags, count every tag of every quote, with a generator expression that has two `for`s, in the same order you'd write two loops:

```python
(tag for quote in quotes for tag in quote.tags)
```

For the decades, `1879 // 10 * 10` is `1870`. Skip quotes whose author has no birth date, and return the decades oldest first.

**Check it:** `python -m pytest`. **Everything** passes. Then `python -m whosaidit stats`, and `python -m mypy whosaidit`.

---

## The big idea: a web page is not an API

In Project 6, PokéAPI gave you JSON. It was made for programs, and it keeps its shape, because programs depend on it. A web page is made for **people**. It can change its layout any day, and nobody will warn you. Some items will have a piece missing, and the same thing can be written two different ways.

So a scraper has to expect the unexpected, and this project shows how:

- **Never assume an element is there.** Every field goes through `text_of()` or `attr_of()`, which give `None` instead of crashing.
- **Skip and log, don't crash.** One broken quote is skipped, and `whosaidit.log` says which page, which quote and why. The other 99 are kept.
- **Check the data as it comes in.** `Quote` and `Author` refuse to exist with missing pieces, so a bad item is caught at the door, not three functions later.
- **Pick keys that don't change.** Names are inconsistent ("Dumas fils" and "Dumas-fils"), so the link's slug is the key.
- **Look at what you've scraped.** It was only by playing the game that the tags turned out to give answers away (`misattributed-mark-twain`). Real data always has surprises like that. You find them by looking.
- **Save what you've fetched.** With the HTML cached, you can change your parsing code and run `scrape` again as often as you like, for free, without asking the site for anything.

When the site does change one day, `scrape` will say "No quotes found", or skip things and say why in the log. It won't crash with a traceback halfway through.

---

## Try to break it

Each of these should give a clear message, not a traceback:

- [ ] `python -m whosaidit play` and `python -m whosaidit stats` before you've scraped (move `quotes.json` away)
- [ ] Open `quotes.json`, delete a few lines from the middle, and run `stats`
- [ ] Make a backup copy of `html_cache/index.html`. Then, in `index.html`, delete one quote's `<small class="author">...</small>`. Run `scrape`, and look in `whosaidit.log`. (Put the backup back afterwards.)
- [ ] Change an author's birth date in their page in `html_cache/` to `14 March 1879`. They should lose that hint, not crash
- [ ] Turn off your Wi-Fi, delete one file from `html_cache/`, and run `scrape`. Then turn the Wi-Fi back on, and run it again
- [ ] Move `html_cache/` somewhere safe, run `scrape`, and press Ctrl+C after a few pages. Run it again: it starts where it stopped. (Then put your copy back.)
- [ ] Replace one file in `html_cache/` with a folder of the same name. `scrape` should fetch that page again, not crash
- [ ] In the game: press Enter without typing, type `quit` halfway through a round, and press Ctrl+C
- [ ] Guess `rowling`, `j k rowling`, `king` for Martin Luther King Jr., and `andre gide` without the accent
- [ ] `python -m whosaidit play seven`, `python -m whosaidit scrape now` and `python -m whosaidit dance`

---

## Stretch goals

Pick one. There's no solution for these.

### 1. Hard mode

`python -m whosaidit play --hard`: only quotes by authors with 3 or more quotes, and no tags shown.

- A `Counter` of authors (like `most_quoted()`) tells you who has 3 or more. Filter the quotes with a list comprehension.
- Pass a `show_tags` flag down to `play_round()`, with a default of `True`, so the tests that already exist keep working.
- Parse `--hard` in `play_command()`. Watch out: `play --hard 7` and `play 7 --hard` should both work.

### 2. A leaderboard

Ask for the player's name at the start, and save each game's score to `leaderboard.json`.

- Use `atomic_write()` again. Two players finishing at once mustn't corrupt the file.
- Store a list of `{"name": ..., "score": ..., "out_of": ..., "when": ...}`, and show the top 5 with `sorted(..., key=..., reverse=True)`.
- Compare scores fairly. 12 out of 16 is better than 14 out of 40, so sort by the fraction, or always play the same number of rounds.

### 3. A clean `quotes.csv`

Export everything as one table, ready for pandas in the next course: one row per quote, with the author's birth date and birthplace joined on.

- `csv.DictWriter` (chapter 10), with `encoding="utf-8"` and `newline=""`.
- Tags are a list, and a CSV cell is just text. Join them with `;`, and say so in the column name: `tags_semicolon_separated`.
- Write dates as `1879-03-14` (ISO format), so pandas reads them as dates and they sort properly.

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 9. Exceptions | your own exception classes, `raise ... from error`, and skipping bad items instead of crashing |
| 10. Files | `quotes.json`, the HTML cache, and `encoding="utf-8-sig"` |
| 11. Packages | `python -m whosaidit`, a virtual environment and `requirements.txt` |
| 12. Generators | `quote_pages()` following "Next →", `parse_quotes()` yielding one quote at a time, and generator expressions with two `for`s |
| 14. Context managers | `atomic_write()` with `@contextmanager`, and `with Scraper() as scraper:` |
| 15. The standard library | `@dataclass(frozen=True)` with `__post_init__`, `Counter`, `datetime.strptime`, `random.Random(seed)` and `unicodedata` |
| 16. Regular expressions | removing the quote marks with `^`, `$` and `|`, squashing spaces with `\s+`, and keeping only letters in `normalise()` |
| 17. APIs | `requests.Session`, headers, timeouts, status codes and the encoding |
| 18. Web scraping | `robots.txt` and `RobotFileParser`, BeautifulSoup, CSS selectors, `urljoin`, polite pauses and caching |
| 19. Reliable code | type hints and mypy, logging every skipped item, and pytest with saved HTML, a fake website and made-up typing |
