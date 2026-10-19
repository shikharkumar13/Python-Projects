"""
Trivia Night: a terminal quiz game.

This is the finished version. Try starter.py first, and come here when
you're done or properly stuck.

Run it with:  python3 solution.py
"""

import json
import random
from pathlib import Path


# ---------------------------------------------------------------------------
# Settings
# These never change while the game runs, so we write them in CAPITALS.
# That's a Python habit that says "this is a fixed setting, not game state".
# ---------------------------------------------------------------------------

# Path(__file__).parent is the folder this file is in. Building our file
# paths from it means the game finds questions.json wherever you run it from.
HERE = Path(__file__).parent
QUESTIONS_FILE = HERE / "questions.json"
HIGH_SCORES_FILE = HERE / "highscores.json"

LETTERS = ["A", "B", "C", "D"]
LEVELS = ["easy", "medium", "hard"]
POINTS = {"easy": 1, "medium": 2, "hard": 3}

QUESTIONS_PER_LEVEL = 3
STREAK_NEEDED = 3      # right answers in a row before points double
MAX_HIGH_SCORES = 5
LIFELINE = "50"        # what the player types to use their 50/50


# ---------------------------------------------------------------------------
# Menu and player name
# ---------------------------------------------------------------------------

def get_menu_choice():
    """Show the menu and keep asking until the player types 1, 2 or 3."""
    while True:
        print()
        print("1) Play   2) High scores   3) Quit")
        text = input("Choose 1, 2 or 3: ")

        # int("banana") raises a ValueError. We catch it and ask again
        # instead of letting the whole program crash.
        try:
            choice = int(text)
        except ValueError:
            print("That's not a number. Please type 1, 2 or 3.")
            continue

        if choice in (1, 2, 3):
            return choice
        print(f"There's no option {choice}. Please type 1, 2 or 3.")


def ask_name():
    """Ask for the player's name. An empty answer isn't allowed."""
    while True:
        name = input("What's your name? ").strip()
        if name != "":
            return name
        print("Please type at least one letter.")


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

def load_questions():
    """Read every question from questions.json and return them as a list."""
    with open(QUESTIONS_FILE, encoding="utf-8") as file:
        return json.load(file)


def pick_questions(all_questions, per_level=QUESTIONS_PER_LEVEL):
    """Pick a few random questions from each level, easy ones first.

    This is what makes the game get harder as you go. `per_level` has a
    default value, so pick_questions(all_questions) picks 3 per level, and
    pick_questions(all_questions, 4) picks 4.
    """
    chosen = []
    for level in LEVELS:
        # First collect every question at this level...
        at_this_level = []
        for question in all_questions:
            if question["difficulty"] == level:
                at_this_level.append(question)

        # ...then pick a few of them. random.sample() picks without
        # repeats, so you never get the same question twice in one game.
        chosen.extend(random.sample(at_this_level, per_level))
    return chosen


def make_choices(question):
    """Shuffle the four options and label them A to D.

    Returns a dictionary such as {"A": "Seoul", "B": "Tokyo", ...}.
    """
    # Put the right answer and the three wrong ones into a single new list.
    options = [question["answer"]] + question["wrong"]
    random.shuffle(options)

    choices = {}
    for i in range(len(options)):
        choices[LETTERS[i]] = options[i]
    return choices


def show_choices(choices):
    """Print each option on its own line, like '  A) Tokyo'."""
    for letter in choices:
        print(f"  {letter}) {choices[letter]}")


def show_question(number, total, question, choices):
    """Print the question number, the question and its options."""
    print()
    print(f"Question {number} of {total}  ({question['category']}, {question['difficulty']})")
    print(question["question"])
    show_choices(choices)


def get_answer(choices, lifeline_available=False):
    """Keep asking until the player types a valid letter, or 50 for the lifeline.

    Returns the letter (like "B"), or "50" if they used the lifeline.
    If you leave out lifeline_available, it's False: no lifeline offered.
    """
    letters = ", ".join(choices.keys())
    if lifeline_available:
        prompt = f"Your answer ({letters}, or {LIFELINE} for 50/50): "
    else:
        prompt = f"Your answer ({letters}): "

    while True:
        # .strip() removes stray spaces and .upper() lets "b" count as "B".
        answer = input(prompt).strip().upper()

        if answer in choices:
            return answer
        if answer == LIFELINE and lifeline_available:
            return answer

        if answer == LIFELINE:
            print("You've already used your 50/50 in this game.")
        else:
            print(f"Please type one of these: {letters}")


def use_fifty_fifty(choices, right_answer):
    """Remove two wrong options and return the two that are left."""
    wrong_letters = []
    for letter in choices:
        if choices[letter] != right_answer:
            wrong_letters.append(letter)

    to_remove = random.sample(wrong_letters, 2)

    remaining = {}
    for letter in choices:
        if letter not in to_remove:
            remaining[letter] = choices[letter]
    return remaining


# ---------------------------------------------------------------------------
# Scoring and playing
# ---------------------------------------------------------------------------

def points_for(difficulty, streak):
    """Work out how many points a right answer is worth.

    `streak` is how many questions in a row were right *before* this one.
    Once it reaches STREAK_NEEDED, every right answer is worth double.
    """
    points = POINTS[difficulty]
    if streak >= STREAK_NEEDED:
        points = points * 2
    return points


def play_question(question, number, total, state):
    """Ask one question, update the game state, and return it.

    `state` is a dictionary holding everything that changes during a game:
    the score, the current streak and whether the 50/50 has been used.
    """
    choices = make_choices(question)
    show_question(number, total, question, choices)

    lifeline_available = not state["lifeline_used"]
    answer = get_answer(choices, lifeline_available)

    if answer == LIFELINE:
        state["lifeline_used"] = True
        choices = use_fifty_fifty(choices, question["answer"])
        print("50/50! Two wrong answers are gone:")
        show_choices(choices)
        answer = get_answer(choices)    # no lifeline this time

    if choices[answer] == question["answer"]:
        points = points_for(question["difficulty"], state["streak"])
        state["score"] = state["score"] + points
        state["streak"] = state["streak"] + 1
        print(f"Correct! (+{points})")
        if state["streak"] == STREAK_NEEDED:
            print(f"{STREAK_NEEDED} in a row! Your next right answers score double.")
    else:
        print(f"Wrong! The answer was {question['answer']}.")
        if state["streak"] >= STREAK_NEEDED:
            print("Your streak is over.")
        state["streak"] = 0

    print(f"Score: {state['score']}   Streak: {state['streak']}")
    return state


def play_game(all_questions):
    """Play one full game and return the final score."""
    # Everything that changes during a game lives in this one dictionary.
    # It gets passed into play_question() and handed back each time.
    state = {"score": 0, "streak": 0, "lifeline_used": False}

    game_questions = pick_questions(all_questions)
    total = len(game_questions)

    number = 1
    for question in game_questions:
        state = play_question(question, number, total, state)
        number = number + 1

    print()
    print(f"Game over! Your final score is {state['score']}.")
    return state["score"]


# ---------------------------------------------------------------------------
# High scores
# ---------------------------------------------------------------------------

def load_high_scores():
    """Read the saved high scores. Returns an empty list if there are none yet."""
    try:
        with open(HIGH_SCORES_FILE, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # Nobody has played yet, so the file doesn't exist. That's fine.
        return []
    except json.JSONDecodeError:
        # The file exists but isn't valid JSON (maybe someone edited it).
        print("The high score file couldn't be read, so we'll start a fresh table.")
        return []


def add_high_score(scores, name, score):
    """Put a new score in the right place (best first) and keep the top few."""
    # Walk down the list, past every score that is as good as or better than
    # the new one. Where we stop is where the new score belongs.
    position = 0
    while position < len(scores) and scores[position]["score"] >= score:
        position = position + 1

    scores.insert(position, {"name": name, "score": score})
    return scores[:MAX_HIGH_SCORES]


def save_high_scores(scores):
    """Write the high scores to highscores.json."""
    with open(HIGH_SCORES_FILE, "w", encoding="utf-8") as file:
        json.dump(scores, file, indent=2)


def show_high_scores(scores):
    """Print the high score table."""
    print()
    print("===== High scores =====")
    if len(scores) == 0:
        print("No scores yet. Be the first!")
        return

    rank = 1
    for entry in scores:
        # :<15 pads the name to 15 characters so the scores line up.
        print(f"{rank}. {entry['name']:<15} {entry['score']}")
        rank = rank + 1


# ---------------------------------------------------------------------------
# The main program
# ---------------------------------------------------------------------------

def main():
    print("Welcome to Trivia Night!")

    try:
        all_questions = load_questions()
    except FileNotFoundError:
        print("I can't find questions.json. Make sure it's in the same folder as this file.")
        return
    except json.JSONDecodeError as error:
        # Usually a missing comma or quote after editing the file by hand.
        print(f"questions.json has a mistake in it: {error}")
        return

    while True:
        choice = get_menu_choice()

        if choice == 1:
            name = ask_name()
            score = play_game(all_questions)
            scores = load_high_scores()
            scores = add_high_score(scores, name, score)
            save_high_scores(scores)
            show_high_scores(scores)
        elif choice == 2:
            show_high_scores(load_high_scores())
        else:
            print("Thanks for playing. Goodbye!")
            break


main()
