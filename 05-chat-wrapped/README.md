# Project 5: Chat Wrapped

**Level:** Intermediate · **Uses chapters:** 7, 10, 12, 15 and 16

You know how Spotify sends you a "Wrapped" every December, with your top songs of the year? In this project you'll build one for your WhatsApp group chat. Export the chat, run your program, and get a report like this:

```markdown
# Sample Chat: Wrapped 2025 🎁

**5,125 messages** from 5 people, between 1 January and 31 December 2025.

## 🏆 The Chatterbox: Riya
1,381 messages, which is 27% of the whole chat.

## 😂 Emoji of the Year: 😂
Used 489 times.
Runners-up: 🔥 218, 😍 203, ❤ 162.

## 🦉 The Night Owl: Kabir
224 messages between 1 am and 5 am. Go to sleep!

## ⚡ The Lightning Replier: Meera
Replies in 2 min 9 s on average.

## 🤫 The Great Silence
12 days, 8 hours without a single message, from 10 Jun, 00:10 until **Arjun** broke it on 22 Jun, 08:47.

## 💬 Words of the Year
- **Riya**: "yaar" (601 times)
- **Kabir**: "bhai" (443 times)
- **Arjun**: "bro" (421 times)
- **Meera**: "haha" (390 times)
```

Along the way, you'll write your first serious **regular expressions**, and a **generator** that can read a chat of 200,000 messages while only ever holding one in memory.

> **Privacy first.** A group chat is other people's words, not just yours. `sample_chat.txt` is completely made up. If you try your own chat, keep the file and the report on your own computer. Never upload a real chat to GitHub or anywhere else, even "just for a minute".

---

## What's in this folder

```
05-chat-wrapped/
├── README.md               this guide
├── starter/                ← you work in here
│   ├── wrapped/            the package
│   │   ├── __main__.py     runs when you type: python -m wrapped
│   │   ├── cli.py          reads the command line, puts the pieces together
│   │   ├── parser.py       reads the chat file, one message at a time
│   │   ├── stats.py        counts everything the awards need
│   │   └── report.py       writes the report
│   ├── tests/              the tests
│   ├── pytest.ini
│   ├── sample_chat.txt     a made-up chat: five friends, one year
│   └── make_big_chat.py    makes a huge chat, to test the generator
└── solution/               the same, finished. Have a real go first!
```

## Getting set up

Everything happens inside `starter/`:

```bash
cd starter
```

You'll need pytest, as in Project 4. If you're using a virtual environment, activate it first. Once it's active, `python` works on every computer. Without one, type `python3` on Mac and Linux, and `py` on Windows.

## Using it

```bash
python -m wrapped sample_chat.txt          # a report for the latest year in the chat
python -m wrapped sample_chat.txt 2024     # a report for a year you choose
```

The report is printed, and also saved next to the chat as `sample_chat_wrapped_2025.md`. A `.md` file is Markdown: open it in VS Code and press the preview button (or `Ctrl+Shift+V`, `Cmd+Shift+V` on a Mac) to see it nicely formatted.

**The ▶ button in VS Code won't work for this project.** It runs one file on its own, as if you'd typed `python wrapped/__main__.py`, and then the files in the package can't find each other. Use the terminal.

**Trying your own chat.** In WhatsApp, open the group, tap the three dots (Android) or the group name (iPhone), then choose **Export chat → Without media**. Save the `.txt` file into `starter/`, and run `python -m wrapped "WhatsApp Chat with Goa Gang.txt"`. Use quotes, because the name has spaces in it.

Two things to know about real exports:

- This project reads the **Android** format with a **24-hour** clock: `12/03/2025, 21:45 - Riya: hi`. iPhone exports look different. Handling them is [a stretch goal](#1-iphone-exports-too).
- If your phone writes the **month before the day** (as in the US), set `DAY_FIRST = False` at the top of `parser.py`.
- WhatsApp sometimes shares the export as a `.zip` file. Unzip it first, and use the `.txt` file inside.

## Running the tests

```bash
python -m pytest                                            # everything
python -m pytest tests/test_parser.py -v                    # one file, test by test
python -m pytest tests/test_parser.py::test_sender          # one test
```

Most tests fail when you start. Each one passes as you finish the step it checks.

---

## How it works

### Reading the chat

An export looks like this:

```
27/12/2024, 19:03 - Riya added Arjun
12/03/2025, 21:45 - Riya: see you tomorrow!
12/03/2025, 21:46 - Arjun: Packing list:
- sunscreen
- chargers
12/03/2025, 21:50 - Meera: haha
```

- Every message starts with a **date and time**, then ` - `, then **who** sent it, a colon, and the text.
- A line **without** a date and time is the next line of the message above. That's how Arjun's packing list ends up as one message.
- A line with a date and time but **no name and colon** is a **system message**, like "Riya added Arjun" or the end-to-end encryption notice. Those are skipped.

### The awards

| Award | How it's worked out |
|---|---|
| 🏆 The Chatterbox | the most messages |
| Emoji of the Year | the most used emoji, across everyone |
| 🦉 The Night Owl | the most messages between 1:00 and 4:59 in the morning |
| ⚡ The Lightning Replier | the quickest average reply. A *reply* is a message within an hour of someone **else's** message. You need at least 3 replies to qualify, so one lucky quick answer doesn't win. (Exports only record the minute, not the second, so reply times are a good guess, not exact.) |
| 🤫 The Great Silence | the longest gap between two messages, and who finally broke it |
| ⏰ Rush Hour | the busiest hour of the day, and day of the week |
| 💬 Words of the Year | each person's most used word, leaving out boring ones like "the" and "and" |

### Your must-have checklist

- [ ] A `re.VERBOSE` regex with named groups reads each message line
- [ ] Lines without a timestamp join the message above
- [ ] System lines are skipped
- [ ] A generator yields one message at a time, so a huge chat never sits in memory
- [ ] `Counter` for messages per person, words (with stop words left out) and emoji, with `finditer` finding the emoji
- [ ] `datetime` for the busiest hour and weekday, and `timedelta` for the longest silence and reply times
- [ ] The report is saved as a Markdown file, with award titles
- [ ] Every test passes

### How the package is organised

| File | What's in it | Your TODOs |
|---|---|---|
| `wrapped/parser.py` | the two regex patterns, and the generator that reads messages | 1–3, 5, 6 |
| `tests/test_parser.py` | tests for reading chats | 4 |
| `wrapped/stats.py` | counting words, emoji, silences and replies | 7–13 |
| `wrapped/report.py` | turning the numbers into the report | 14 |

`cli.py` is already written. It reads the file twice: once quickly to find the latest year, then again to count that year's messages.

---

## Building it, one step at a time

Each unfinished part has a *placeholder* that keeps things running. Until Step 6 is done, the program says it couldn't find any messages, and until Step 11, it says there are none in 2025. That's just the placeholders talking. Nothing's wrong with the file.

### Part 1: Reading the chat (`wrapped/parser.py`)

#### Step 1: The `LINE_START` pattern

This is the heart of the whole project. Every message line starts like `12/03/2025, 21:45 - `, and your pattern has to recognise it, and pull out each part with a **named group**:

```python
(?P<day>\d{1,2})
```

`(?P<name>...)` is a group with a name. After a match, `match["day"]` gives you whatever it matched, like `"12"`. Without names, you'd write `match.group(1)` and have to count brackets to know which number was which.

Patterns like this get long, and hard to read. `re.VERBOSE` fixes that. In VERBOSE mode, spaces are ignored and `#` starts a comment, so you can lay the pattern out over several lines:

```python
LINE_START = re.compile(
    r"""
    ^
    (?P<day>\d{1,2}) / (?P<month>\d{1,2}) / ...    # the date
    ...
    """,
    re.VERBOSE,
)
```

Because spaces are ignored, a real space has to be written `\s`. The `EMOJI` pattern near the top of `stats.py` is a finished example of a VERBOSE pattern. Have a look at it.

- Days, months and hours can have one digit or two (`1/3/25, 9:05`), so use `\d{1,2}`.
- Years can have four digits or two: `\d{4}|\d{2}`. Python tries the choices from left to right. Here the order happens not to matter: if `\d{2}` grabbed just the `20` of `2025`, the comma that has to come next wouldn't be there, so Python would back up and try `\d{4}` instead. But get into the habit of putting the longer choice first. Without something after it to check, `\d{2}|\d{4}` would happily match only half of `2025`.
- Put the rest of the line, after ` - `, in a group called `rest`.

**Check it:** `python -m pytest -k line_start`. Each row in those tests is one line that should, or shouldn't, match.

#### Step 2: The `SENDER` pattern

`rest` is either `Riya: see you tomorrow!` (a message) or `Riya added Arjun` (a system line). `SENDER` tells them apart: if it matches, it's a message.

The tricky part is where the name stops. `[^:]+` means "one or more characters that aren't a colon". Add a `?` (`[^:]+?`) and it takes **as few as possible**, so it stops at the first colon. That way, `Riya: time: 9pm` is from Riya, and says `time: 9pm`.

There's one more trap, and it's a real one. When someone renames the group, WhatsApp writes a system line like this:

```
Riya changed the subject from "Trip: Goa" to "Goa"
```

That has a colon in it, so `[^:]+?` would decide it's a message from someone called `Riya changed the subject from "Trip`, and that "person" would turn up in your awards. System lines put group names in quotes, and real names never have quotes in them. So leave quotes out of the name too: `[^:"]+?`.

**Check it:** `python -m pytest -k "test_sender or no_sender"`.

#### Step 3: `parse_when`

Turn the matched pieces into a real `datetime`. `datetime(2025, 13, 1)` raises a `ValueError`, because there's no month 13. Catch it, and raise a `ChatFormatError` that says **which line** of the file it's on, and suggests `DAY_FIRST`. A US export read the wrong way round hits this as soon as a day is over 12.

#### Step 4: Two tests, before the generator (`tests/test_parser.py`)

Before writing the generator, write the two tests for the two bugs everyone makes with it. Open `tests/test_parser.py` and find the two tests that say `pytest.skip`:

1. **The last message gets lost.** (Step 5 explains why.)
2. **Multi-line messages lose their extra lines.**

Write them, delete the `pytest.skip` lines, and run them. **They should fail**, because the generator doesn't exist yet. When they pass after Step 5, you'll know it really works.

#### Step 5: `read_messages`, the generator

A **generator** is a function that uses `yield` instead of `return`. Each `yield` hands one value to whoever is looping over it, and the function then **pauses**, right there, until the loop asks for the next one.

That's what makes it work on huge files. The loop asks for a message, the generator reads just enough lines to make one, hands it over, and waits. At no point does it hold the whole chat.

There's one puzzle. When you read Arjun's first line, `Packing list:`, you don't know yet whether more lines are coming. So you can't hand the message over straight away. You **hold on to it** in a variable, `current`, and only `yield` it when the **next** timestamped line arrives, because then you know it's finished:

```python
if start is None:
    if current is not None:
        current.text += "\n" + line      # an extra line for the message we're holding
    continue

if current is not None:
    yield current                        # a new message has started, so the old one is done
```

And that's where the classic bug lives. The **last** message in the file has no "next message" to push it out. When the loop ends, it's still sitting in `current`. You need one more `yield` *after* the loop, or the last message silently disappears. Your test from Step 4 catches exactly that.

The file is opened with `encoding="utf-8-sig"`, because some tools put an invisible mark at the very start of a file. Some phones also scatter invisible `\u200e` characters through their exports, so remove those from each line too.

**Check it:** `python -m pytest tests/test_parser.py`. Everything in this file should pass now, including your two tests. The one exception is `test_latest_year`, which is the next step.

#### Step 6: `latest_year`

One line, using a **generator expression**, which is like a list comprehension with round brackets:

```python
max((message.when.year for message in messages), default=None)
```

A list comprehension builds the whole list first. A generator expression hands out one value at a time, so `max()` never needs every year at once. `default=None` is what `max()` returns if there's nothing at all, instead of crashing.

### Part 2: Counting (`wrapped/stats.py`)

Here's the plan. Everything the awards need goes into one `ChatStats` object, which is a dataclass full of `Counter`s, while the messages stream past **once**. No message is ever stored. So a chat of 200,000 messages takes no more memory than a chat of 200. All `ChatStats` remembers is the counts.

#### Step 7: `words_in`

```python
WORD.findall("yaar the cafe is OPEN".lower())    # ['yaar', 'the', 'cafe', 'is', 'open']
```

`findall()` gives every match as a list. Before that, remove links with `URL.sub(" ", text)`, or `https://example.com` would give you the "words" `https`, `example` and `com`. After it, leave out the `STOP_WORDS` (boring words like "the", "is" and "hai") and single letters.

Watch out for apostrophes. Phone keyboards usually swap `'` for a curly `’` as you type, so a real chat says `don’t`, not `don't`. `WORD` only knows the straight one, and it would split `don’t` into `don` and `t`. Then `don` might even win someone's Word of the Year! So first turn the curly one, `"\u2019"`, back into a plain `'`.

#### Step 8: `emojis_in`

`finditer()` is like `findall()`, but it gives you **match objects**, one at a time, instead of building a list. Call `.group()` on each one to get the text it matched.

Some emoji are really two characters. ❤️ is ❤ followed by `\ufe0f`, an invisible mark meaning "draw this as an emoji". Remove that mark, so ❤ and ❤️ count as the same emoji. A flag like 🇮🇳 is two special "letter" symbols side by side, which is why the pattern has a separate choice for flags.

The pattern doesn't handle everything. Some emoji are several emoji glued together with invisible joiners. A family emoji, for example, is really a man, a woman and a child joined up, and it gets counted as those three. Getting every emoji exactly right is a surprisingly deep rabbit hole, and this is close enough for a fun report.

#### Steps 9 and 10: `ChatStats.add` and `ChatStats.add_gap`

`add()` counts one message. With `Counter`s, counting is one line each:

```python
self.messages[message.sender] += 1          # a Counter starts every key at 0
self.emojis.update(emojis_in(message.text)) # update() counts a whole list at once
```

`self.words` is a `defaultdict(Counter)`: one `Counter` per person, made automatically the first time someone appears.

`add_gap()` looks at **two messages next to each other**. Taking one `datetime` from another gives a `timedelta`, the time between them:

```python
gap = message.when - previous.when
```

That one gap does two jobs. It might be the longest silence so far. And if a *different* person sent the second message within an hour, it's a reply.

The tests for Steps 9 and 10 go through `analyse()`, so they start passing after Step 11.

#### Step 11: `analyse`

Now the clever part. `add_gap()` needs each message *and the one before it*, but the messages arrive one at a time from a generator. You can't go back and look at the previous one. `itertools.pairwise()` solves that: it hands out overlapping pairs, `(m1, m2)`, `(m2, m3)`, `(m3, m4)`...

There's one wrinkle. The first message is never the *second* half of a pair, so it would never be counted. So take it off the front first, with `next()`:

```python
messages = iter(messages)
first = next(messages, None)      # the first message, or None if there aren't any
...
stats.add(first)
for previous, message in pairwise(chain([first], messages)):
    stats.add(message)
    stats.add_gap(previous, message)
```

`next()` takes one item from an iterator. `chain([first], messages)` then glues it back on in front of the rest, so it can be the "previous" for the second message. Every message is still read exactly once.

**Check it:** `python -m wrapped sample_chat.txt`. You should see a real report now.

#### Step 12: `fastest_replier`

Work out each person's average reply time (total time ÷ number of replies; you can divide a `timedelta` by a number). Then pick the smallest with `min(averages, key=...)`, just like `max(..., key=...)` in chapter 7.

#### Step 13: `favourite_words`

`stats.words[name].most_common(1)` gives a list with one `(word, count)` pair in it. Take `[0]` to get the pair itself.

### Part 3: The report (`wrapped/report.py`)

#### Step 14: `describe_duration`

Turn a `timedelta` into words a person would use. `divmod()` does a division and a remainder in one go:

```python
divmod(200, 60)    # (3, 20): 200 seconds is 3 minutes and 20 seconds
```

Split off the days, then the hours, then the minutes, and only show the two biggest parts. "12 days, 8 hours" is useful. "12 days, 8 hours, 13 minutes and 4 seconds" is just noise.

**Check it:** `python -m pytest`. Everything should pass.

---

## The big idea: a generator never holds the whole chat

Here are two ways to read every message:

```python
messages = list(read_messages(path))     # 1. read them all into a list first
stats = analyse(messages)

stats = analyse(read_messages(path))     # 2. hand the generator straight to analyse()
```

They give exactly the same report. But the first builds a list of every single message before counting starts. The second never does: each message is read, counted, and thrown away before the next one is even read.

You can see the difference. Make a big chat, then measure both ways with `tracemalloc`, a standard-library tool that tracks how much memory Python is using:

```bash
python make_big_chat.py           # writes big_chat.txt: 200,000 messages, about 8 MB
python -m wrapped big_chat.txt    # still takes about a second
```

```python
import tracemalloc
from pathlib import Path
from wrapped.parser import read_messages
from wrapped.stats import analyse

tracemalloc.start()
analyse(read_messages(Path("big_chat.txt")))
print(f"generator: {tracemalloc.get_traced_memory()[1] / 1_000_000:.1f} MB at most")

tracemalloc.stop()
tracemalloc.start()
analyse(list(read_messages(Path("big_chat.txt"))))
print(f"list:      {tracemalloc.get_traced_memory()[1] / 1_000_000:.1f} MB at most")
```

Save that as `measure.py` in `starter/`, and run `python measure.py`. On the computer this project was written on, the generator needed about 0.1 MB, and the list about 50 MB, five hundred times as much. Make the chat ten times bigger and the list needs ten times more memory, while the generator still needs the same tiny amount. That's why real tools that process logs, data files or chats are built this way.

There's one catch. **A generator can only be used once.** When it's finished, it's finished. That's why `cli.py` calls `read_messages(path)` twice: once to find the latest year, and once to count. Each call makes a fresh generator that starts again from the top of the file.

---

## Try to break it

Each of these should give a clear message, not a traceback:

- [ ] `python -m wrapped missing.txt`, a file that isn't there
- [ ] `python -m wrapped pytest.ini`, a file that isn't a chat at all
- [ ] `python -m wrapped sample_chat.txt 2019` and `python -m wrapped sample_chat.txt twenty`
- [ ] Copy `sample_chat.txt`, and change one date to `32/01/2025`. The error should name the line
- [ ] Add a message whose text has a colon in it, like `Riya: time: 9pm`. Check that it's from Riya
- [ ] Add a system line where the group is renamed to something with a colon: `12/03/2025, 21:45 - Riya changed the subject from "Trip: Goa" to "Goa"`. Nobody new should appear in the report
- [ ] Add a message with a curly apostrophe in it, like `don’t`. It should still count as one word
- [ ] Try `python -m wrapped export.zip`, and a line with a 12-hour time like `12/03/25, 9:45 pm - Riya: hi`
- [ ] Add a message with three extra lines under it, as the very **last** thing in the file
- [ ] Make a chat that ends on 2 January. The report for "the latest year" should suggest trying the year before
- [ ] Run it on `big_chat.txt` from `make_big_chat.py`

---

## Stretch goals

Pick one. There's no solution for these.

### 1. iPhone exports too

iPhone exports look like this:

```
[12/03/2025, 21:45:10] Riya: see you tomorrow!
```

There are square brackets, seconds, and no ` - `. Some phones also use a 12-hour clock: `12/03/2025, 9:45 pm - Riya: hi`.

- Write a second pattern, `IPHONE_START`, with the **same group names**. Then the rest of the code doesn't care which pattern matched.
- In `read_messages`, try one pattern, then the other: `LINE_START.match(line) or IPHONE_START.match(line)`.
- Test both formats with one `@pytest.mark.parametrize` test, with rows of `(line, expected datetime)`.
- For 12-hour times, add an optional `(?P<ampm>am|pm)` group, and fix the hour in `parse_when`. Watch out: 12 am is 0, and 12 pm is 12.

### 2. The Conversation Starter

Who sends the first message after a long quiet spell? Give an award to whoever most often breaks a silence of 6 hours or more.

- That's one more check in `add_gap()`: if the gap is at least `timedelta(hours=6)`, add 1 to a new `Counter` for `message.sender`.
- Don't forget to give the new field a `default_factory`.

### 3. Activity by month

Draw a bar for each month, with characters:

```
Jan  ████████████████  487
Feb  ███████████       341
```

- Count messages by month in `add()`, with a `Counter` keyed by `message.when.month`.
- Scale each bar so the busiest month is 30 characters wide: `round(count / biggest * 30)`.
- Markdown squashes spaces together, so put the bars inside a code block (three backticks above and below).

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 7. `key=` | `min(averages, key=...)` and `max(stats.hours, key=...)` |
| 10. Files | reading with `encoding="utf-8-sig"`, writing the `.md` report |
| 12. Generators | `read_messages()` with `yield`, generator expressions, `next()`, and a generator that can only be used once |
| 15. The standard library | `Counter`, `defaultdict(Counter)`, `datetime`, `timedelta`, `divmod()`, and `pairwise()` and `chain()` from `itertools` |
| 16. Regular expressions | `re.compile`, `re.VERBOSE`, named groups, lazy `+?`, `findall`, `finditer` and `sub` |
