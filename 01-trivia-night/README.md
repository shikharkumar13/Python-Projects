# Project 1: Trivia Night

**Level:** Beginner · **Uses chapters:** 1–6, 9 and 10

You're hosting quiz night for your friends. You want a game that asks the questions, keeps score, gets harder as it goes, and remembers who holds the high score. In this project you'll build that game, and it runs in the terminal.

Here's one question from a game:

```
Question 4 of 9  (Geography, medium)
Which is the largest ocean on Earth?
  A) Indian Ocean
  B) Arctic Ocean
  C) Atlantic Ocean
  D) Pacific Ocean
Your answer (A, B, C, D, or 50 for 50/50): banana
Please type one of these: A, B, C, D
Your answer (A, B, C, D, or 50 for 50/50): d
Correct! (+4)
Score: 7   Streak: 4
```

---

## What's in this folder

| File | What it is |
|---|---|
| `starter.py` | **Start here.** The game with the insides of each function missing. You fill them in. |
| `questions.json` | 18 questions: 6 easy, 6 medium and 6 hard. |
| `solution.py` | One finished version. Try not to peek until you've had a real go. |
| `highscores.json` | You won't see this yet. The game creates it the first time someone finishes a game. |

## How to run it

Open a terminal in this folder and type:

```bash
python3 starter.py
```

On Windows, type `python` (or `py`) instead of `python3`. You can also open the file in VS Code and press the ▶ button.

Want to see the finished game first? Run `python3 solution.py`. Playing it once is a good way to understand what you're building.

---

## The rules of the game

- **The menu.** The game starts with `1) Play   2) High scores   3) Quit`.
- **The questions.** Each game asks 9 questions: 3 easy, then 3 medium, then 3 hard. They're picked at random, so every game is a bit different.
- **Answering.** The four options are shuffled and labelled A, B, C and D. The player types a letter. Small letters are fine too.
- **Points.** Easy is worth 1 point, medium 2 and hard 3.
- **Streaks.** Once you've got 3 right in a row, every right answer after that is worth **double**. One wrong answer and your streak goes back to 0.
- **The 50/50 lifeline.** Once per game, the player can type `50` instead of a letter. Two wrong answers disappear, leaving the right one and one wrong one.
- **Bad input.** If someone types `E`, `banana` or nothing at all, the game asks again. It must never crash.
- **High scores.** The top 5 scores are saved in `highscores.json`, and the table is shown at the end of every game.

### Your must-have checklist

Tick these off as you go:

- [ ] Questions are loaded from `questions.json`
- [ ] Options are shuffled and the player answers with A/B/C/D
- [ ] The game gets harder: easy questions first, hard ones last
- [ ] Points depend on difficulty, and double after 3 right in a row
- [ ] The 50/50 lifeline works, and only once per game
- [ ] Bad input never crashes the game, either in the menu or when answering
- [ ] The top 5 scores are saved and shown at the end
- [ ] No global variables for the score (see [the big idea](#the-big-idea-keeping-score-without-global-variables) below)

---

## Building it, one step at a time

Open `starter.py`. The settings at the top and `main()` at the bottom are already written. Your job is to fill in the 14 TODOs, in order. Each TODO is one small function.

**You can run the file at any time.** Functions you haven't written yet just do nothing, so the game won't crash. It just won't do much yet. The very first time, it says "Welcome" and then straight away "Goodbye", because there's no menu until you write TODO 1.

**Testing one function on its own** is the fastest way to check your work. Go to the very last line, put a `#` in front of `main()`, and add a print below it:

```python
# main()
print(points_for("hard", 3))     # should print 6
```

Put `main()` back when you're done.

### Step 1: The menu (`get_menu_choice`)

The player types something, and you need a number. `int()` turns text into a number, but it crashes on text like `"banana"`. So wrap it in `try`/`except`:

```python
try:
    choice = int(text)
except ValueError:
    print("That's not a number. Please type 1, 2 or 3.")
    continue          # jump back to the top of the while loop
```

Don't forget the `continue`. Without it, Python carries on to the next line and tries to use `choice`, which was never made, so the game crashes with a `NameError`.

After that, check the number is 1, 2 or 3 before you return it. `7` is a number, but it isn't on the menu.

### Step 2: The player's name (`ask_name`)

This works like Step 1, but simpler. Keep asking until the name isn't empty. If you call `.strip()` first, someone who types only spaces gets asked again too.

### Step 3: Loading the questions (`load_questions`)

Three lines will do it. Open the file with `with open(QUESTIONS_FILE, encoding="utf-8") as file:` and return `json.load(file)`.

**Check it:** `print(len(load_questions()))` should print `18`.

### Step 4: Picking this game's questions (`pick_questions`)

Loop over `LEVELS`. For each level, build a list of only the questions at that level (a `for` loop with an `if` inside). Then pick 3 of them:

```python
random.sample(at_this_level, QUESTIONS_PER_LEVEL)
```

`random.sample()` picks without repeats, so you never get the same question twice in one game. Use `.extend()` to add the picked questions to your `chosen` list.

Look at the first line of the function: `per_level=QUESTIONS_PER_LEVEL`. That's a **default argument**. If you call `pick_questions(all_questions)`, `per_level` is 3. If you call `pick_questions(all_questions, 4)`, it's 4. So use `per_level` inside the function, not `QUESTIONS_PER_LEVEL`.

**Check it:** print the `"difficulty"` of each picked question. You should see easy, easy, easy, medium, medium, medium, hard, hard, hard.

### Step 5: Shuffling the options (`make_choices`)

Put all four options in one list, shuffle it, and label them:

```python
options = [question["answer"]] + question["wrong"]
random.shuffle(options)
```

Now loop with `for i in range(len(options)):` and set `choices[LETTERS[i]] = options[i]`.

**Why not just add the answer to the wrong list?** You might try this:

```python
options = question["wrong"]
options.append(question["answer"])     # don't do this!
```

But `options` isn't a copy. It's another name for the **same** list as `question["wrong"]`. So `.append()` sneaks the right answer into the question's wrong answers, and the list grows every time the question is asked. Joining two lists with `+` makes a brand new list, which is safe to shuffle.

### Step 6: Getting a valid answer (`get_answer`)

This is a lot like the menu. Loop until the input is good. Two things help:

- `.strip().upper()` turns `" b "` into `"B"`.
- `answer in choices` checks whether `answer` is one of the dictionary's **keys**. After a 50/50 there are only two keys left, so this check automatically rejects the letters that have been removed.

Remember the lifeline: if the player types `LIFELINE` (which is `"50"`) and `lifeline_available` is `True`, return it.

`lifeline_available=False` in the first line is another default argument. After a 50/50 you can simply write `get_answer(choices)`, and no lifeline is offered.

### Step 7: The 50/50 (`use_fifty_fifty`)

1. Loop over the letters and collect the ones whose option is **not** the right answer. There will be three.
2. `random.sample(wrong_letters, 2)` picks the two to remove.
3. Build a new dictionary with every letter that isn't being removed.

**Check it:** the dictionary you return should have 2 entries, and one of them must be the right answer.

### Step 8: Working out the points (`points_for`)

Look up `POINTS[difficulty]`. If `streak >= STREAK_NEEDED`, double it.

**Check it:**
`points_for("easy", 0)` → `1`
`points_for("hard", 2)` → `3`
`points_for("hard", 3)` → `6`

### Step 9: Playing one question (`play_question`)

This is the biggest step. It joins up everything you've written so far. The TODO in the starter file lists the five parts. Do them one at a time and run the game after each one.

Be careful with the streak: work out the points **before** you add 1 to the streak. `points_for()` wants the streak from *before* this answer.

### Step 10: Playing a whole game (`play_game`)

Create the `state` dictionary, pick the questions, and loop over them. The important line is:

```python
state = play_question(question, number, total, state)
```

The state goes in, gets updated, and comes back out. After this step **you can play the game!**

### Step 11: Loading high scores (`load_high_scores`)

The first time anyone plays, `highscores.json` doesn't exist yet. Opening a missing file raises `FileNotFoundError`. That isn't really an error here: it just means "no scores yet", so catch it and return an empty list `[]`.

Also catch `json.JSONDecodeError`. This happens if the file exists but someone has typed rubbish into it.

### Step 12: Adding a score (`add_high_score`)

The list is always kept best first, so you don't need to sort it. You only need to find where the new score fits. Think of joining a queue of people lined up from tallest to shortest: you walk past everyone at least as tall as you, and step in there.

```python
position = 0
while position < len(scores) and scores[position]["score"] >= score:
    position = position + 1
```

The order of that `and` matters. Python checks the left side first, and if it's `False` it doesn't look at the right side at all. So when you reach the end of the list, it never tries `scores[position]`, which would be an `IndexError`.

Then `scores.insert(position, {"name": name, "score": score})`, and keep only the top 5 with a slice: `scores[:MAX_HIGH_SCORES]`.

(In chapter 7 you'll meet `sorted()` with `key=`, which is another way to do this.)

### Step 13: Saving high scores (`save_high_scores`)

Open the file in `"w"` mode and call `json.dump(scores, file, indent=2)`. Afterwards, open `highscores.json` in your editor and look at it. It's just text!

### Step 14: Showing the table (`show_high_scores`)

If the list is empty, say so. Otherwise print each entry with its rank, using a counter that starts at 1. To line the scores up neatly, `f"{entry['name']:<15}"` pads each name with spaces to 15 characters.

---

## The big idea: keeping score without global variables

The score, the streak and "has the lifeline been used?" all change while the game runs. Lots of different functions need them. The tempting fix is to make them global:

```python
score = 0

def play_question(question):
    global score
    score = score + 3     # any function, anywhere, can change this
```

It works at first. But once the program grows, you can't tell which function changed the score just by looking at it. And starting a second game means remembering to reset every global by hand.

This project does something else. Everything that changes lives in **one dictionary**, and that dictionary is passed **into** each function and handed **back**:

```python
state = {"score": 0, "streak": 0, "lifeline_used": False}

for question in game_questions:
    state = play_question(question, number, total, state)
```

Now you can see exactly where the state goes just by reading the code. A new game is just a new dictionary, so there's nothing to reset.

> **A small secret:** dictionaries can be changed in place, so `play_question()` is changing the very same dictionary it was given. Strictly speaking, the `return state` isn't needed. We return it anyway because it makes the flow easy to see, and because it's the habit you'll need for values that *can't* be changed in place, like numbers.

The settings at the top of the file (`POINTS`, `LETTERS` and the rest) are a different case. They never change, so it's fine for them to live at the top. Writing them in CAPITALS tells the reader "this is a fixed setting".

---

## Try to break it

When your game works, try to crash it. Every one of these should give a friendly message, not an error:

- [ ] At the menu, type `banana`, then `7`, then press Enter on an empty line
- [ ] For your name, type only spaces
- [ ] For an answer, type `E`, then `banana`, then nothing at all
- [ ] Type a small letter, like `b`. It should count as `B`
- [ ] Use the 50/50, then type one of the letters that was removed
- [ ] Try to use the 50/50 a second time in the same game
- [ ] Delete `highscores.json` and play again. The table should simply start fresh
- [ ] Open `highscores.json`, replace everything in it with the word `hello`, save it, and play again
- [ ] Rename `questions.json` to something else and start the game. Then name it back, delete one comma from it, and try again
- [ ] Play 6 games. Only the best 5 should be kept

If something crashes, read the **last line** of the error message first. It tells you what went wrong. The lines above it tell you where.

---

## Stretch goals

Finished? Try one of these. There's no solution for them. You're on your own now, which is the fun part.

### 1. Fresh questions from the internet

The [Open Trivia Database](https://opentdb.com/) gives away free questions, and you don't need a key. Open this link in your browser to see what comes back:

```
https://opentdb.com/api.php?amount=10&type=multiple
```

Hints:
- You can fetch it with `urllib.request.urlopen(url)` from the standard library, so nothing needs installing. Read the response and pass it to `json.loads()`. (Chapter 17 shows a nicer way using the `requests` package.)
- The questions are inside `data["results"]`. Each one has `correct_answer` and `incorrect_answers` where our file has `answer` and `wrong`. Write a small function that converts one into the other, so the rest of your game doesn't need to change at all.
- Their `difficulty` values are `easy`, `medium` and `hard`, the same as ours.
- Some text comes back looking like `&quot;Hello&quot;`. `html.unescape()` turns it back into `"Hello"`.
- No internet? Catch the error and fall back to `questions.json`.

### 2. A time limit

Slow answers should score less.

- `time.perf_counter()` gives you a time in seconds. Call it once before `input()` and once after, and subtract the two.
- `input()` can't be interrupted. So you can't cut the player off; you can only score them less afterwards. For example, over 10 seconds could mean half points (`points // 2`).
- Print how long they took: `f"{seconds:.1f} seconds"` shows one decimal place.

### 3. Two players

Take turns, and see who wins.

- Ask for two names, and give each player their **own** state dictionary. Keep both in a list: `players = [state1, state2]`.
- Put the name inside each state too, like `"name": "Riya"`.
- Alternate turns: odd-numbered questions go to the first player and even ones to the second. The `%` operator helps: `number % 2` is `1` for odd numbers and `0` for even ones.
- 9 questions don't split fairly between two people. Call `pick_questions(all_questions, 4)` to get 12. This is where the default argument from Step 4 pays off.
- Each player gets their own 50/50 and their own streak. That part comes free because you used state dictionaries instead of globals.

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 1. Variables and types | the settings at the top, the score |
| 2. Lists, tuples and strings | the options list, `.insert()`, slicing the top 5, the menu tuple `(1, 2, 3)`, `.strip()`, `.upper()`, f-strings |
| 3. Dictionaries | each question, the choices, the game state, the high scores |
| 4. Operators | `in`, `>=`, `not`, `and` stopping early, doubling the points |
| 5. Conditionals and loops | the menu loop, the question loop, re-asking on bad input |
| 6. Functions | small functions with one job each, default arguments, passing state in and returning it |
| 9. Exceptions | `ValueError` from `int()`, a missing or broken high score file |
| 10. Files and JSON | reading the questions, saving the high scores |
