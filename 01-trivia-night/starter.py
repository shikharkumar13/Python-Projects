"""
Trivia Night: your starter file.

Work through the TODOs in order, from TODO 1 to TODO 14. Each one is a
small function. README.md has a hint for every step if you get stuck.

Run it with:  python3 starter.py

The very first time, it just says "Welcome" and then "Goodbye". That's
because the menu (TODO 1) isn't written yet. It comes alive as you go.

The settings at the top and main() at the bottom are already written.
You only need to fill in the functions marked TODO. Each one currently
says `pass`, which means "do nothing". Delete the `pass` when you write
your own code.
"""

import json
import random
from pathlib import Path


# ---------------------------------------------------------------------------
# Settings (already done)
# These never change while the game runs, so we write them in CAPITALS.
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
    # TODO 1
    # - Use a `while True:` loop so you can keep asking.
    # - Print the menu:  1) Play   2) High scores   3) Quit
    # - Read what the player types with input().
    # - Turn it into a number with int(). Put that inside try/except ValueError,
    #   because int("banana") crashes otherwise.
    # - Inside the except, print a message and then write `continue`. That
    #   jumps back to the top of the loop. Without it, the code carries on
    #   and tries to use a number that was never made.
    # - If the number is 1, 2 or 3, return it. If not, print a message and
    #   let the loop ask again.
    pass


def ask_name():
    """Ask for the player's name. An empty answer isn't allowed."""
    # TODO 2
    # - Keep asking until the name isn't empty.
    # - Use .strip() so that "   " (only spaces) counts as empty too.
    # - Return the name.
    pass


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

def load_questions():
    """Read every question from questions.json and return them as a list."""
    # TODO 3
    # - Open QUESTIONS_FILE with `with open(...)`.
    # - Use json.load() to turn the file into a Python list, and return it.
    pass


def pick_questions(all_questions, per_level=QUESTIONS_PER_LEVEL):
    """Pick a few random questions from each level, easy ones first.

    This is what makes the game get harder as you go. `per_level` has a
    default value, so pick_questions(all_questions) picks 3 per level, and
    pick_questions(all_questions, 4) picks 4.
    """
    # TODO 4
    # - Start with an empty list called `chosen`.
    # - Loop over LEVELS ("easy", then "medium", then "hard").
    #   - For each level, make a list of the questions at that level.
    #   - Use random.sample(that_list, per_level) to pick a few.
    #   - Add them to `chosen` with .extend().
    # - Return `chosen`.
    pass


def make_choices(question):
    """Shuffle the four options and label them A to D.

    Returns a dictionary such as {"A": "Seoul", "B": "Tokyo", ...}.
    """
    # TODO 5
    # - Make ONE list holding the right answer and the three wrong ones.
    #   Hint: [question["answer"]] + question["wrong"]
    # - Shuffle it with random.shuffle().
    # - Build a dictionary: LETTERS[0] -> first option, LETTERS[1] -> second...
    # - Return the dictionary.
    pass


def show_choices(choices):
    """Print each option on its own line, like '  A) Tokyo'. (Already done.)"""
    for letter in choices:
        print(f"  {letter}) {choices[letter]}")


def show_question(number, total, question, choices):
    """Print the question number, the question and its options. (Already done.)"""
    print()
    print(f"Question {number} of {total}  ({question['category']}, {question['difficulty']})")
    print(question["question"])
    show_choices(choices)


def get_answer(choices, lifeline_available=False):
    """Keep asking until the player types a valid letter, or 50 for the lifeline.

    Returns the letter (like "B"), or "50" if they used the lifeline.
    If you leave out lifeline_available, it's False: no lifeline offered.
    """
    # TODO 6
    # - Keep asking in a loop.
    # - Clean up what they type with .strip().upper(), so " b " becomes "B".
    # - If the answer is one of the keys in `choices`, return it.
    #   (Hint: `"B" in choices` checks the keys of a dictionary.)
    # - If they typed LIFELINE and lifeline_available is True, return it.
    # - Otherwise print a helpful message and ask again.
    pass


def use_fifty_fifty(choices, right_answer):
    """Remove two wrong options and return the two that are left."""
    # TODO 7
    # - Make a list of the letters whose option is NOT the right answer.
    # - Pick two of them at random with random.sample(..., 2).
    # - Build a NEW dictionary with every letter except those two. Return it.
    pass


# ---------------------------------------------------------------------------
# Scoring and playing
# ---------------------------------------------------------------------------

def points_for(difficulty, streak):
    """Work out how many points a right answer is worth.

    `streak` is how many questions in a row were right *before* this one.
    Once it reaches STREAK_NEEDED, every right answer is worth double.
    """
    # TODO 8
    # - Look up the points for this difficulty in the POINTS dictionary.
    # - If streak is STREAK_NEEDED or more, double them.
    # - Return the points.
    pass


def play_question(question, number, total, state):
    """Ask one question, update the game state, and return it.

    `state` is a dictionary holding everything that changes during a game:
    the score, the current streak and whether the 50/50 has been used.
    """
    # TODO 9  (the biggest step, so take it slowly)
    # 1. Make the choices with make_choices() and show them with show_question().
    # 2. Get the player's answer with get_answer(). The lifeline is available
    #    if state["lifeline_used"] is False.
    # 3. If they typed LIFELINE:
    #      - set state["lifeline_used"] to True
    #      - replace `choices` with use_fifty_fifty(...)
    #      - show the two remaining choices with show_choices()
    #      - ask again with get_answer(choices). Leaving out the second
    #        argument means "no lifeline this time", thanks to its default.
    # 4. Check the answer: choices[answer] is the text they picked.
    #      - Right: add points_for(...) to state["score"] and add 1 to state["streak"].
    #      - Wrong: tell them the right answer and set state["streak"] back to 0.
    # 5. Print the score and streak, then return state.
    pass


def play_game(all_questions):
    """Play one full game and return the final score."""
    # TODO 10
    # - Make the state dictionary: {"score": 0, "streak": 0, "lifeline_used": False}
    # - Get this game's questions with pick_questions().
    # - Loop over them. For each one:  state = play_question(question, number, total, state)
    #   (Keep your own `number` counter that starts at 1.)
    # - Print the final score and return it.
    pass


# ---------------------------------------------------------------------------
# High scores
# ---------------------------------------------------------------------------

def load_high_scores():
    """Read the saved high scores. Returns an empty list if there are none yet."""
    # TODO 11
    # - Open HIGH_SCORES_FILE and json.load() it, inside a try block.
    # - except FileNotFoundError: nobody has played yet, so return [].
    # - except json.JSONDecodeError: the file is broken, so print a note and return [].
    pass


def add_high_score(scores, name, score):
    """Put a new score in the right place (best first) and keep the top few."""
    # TODO 12
    # - The list is already sorted, best first. Find where the new score goes:
    #   start a `position` counter at 0, and move it forward with a while loop
    #   as long as there's an entry there AND its score is >= the new score.
    # - Insert {"name": name, "score": score} at that position with .insert().
    # - Keep only the first MAX_HIGH_SCORES entries (slicing!) and return them.
    pass


def save_high_scores(scores):
    """Write the high scores to highscores.json."""
    # TODO 13
    # - Open HIGH_SCORES_FILE in "w" (write) mode.
    # - json.dump(scores, file, indent=2)  (indent=2 makes the file easy to read)
    pass


def show_high_scores(scores):
    """Print the high score table."""
    # TODO 14
    # - If the list is empty, print "No scores yet. Be the first!"
    # - Otherwise print each entry with its rank:  1. Riya   14
    #   Tip: f"{entry['name']:<15}" pads the name so the scores line up.
    pass


# ---------------------------------------------------------------------------
# The main program (already done)
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


# Want to try one function on its own? Put a # in front of main() below,
# and add a line like this instead:   print(points_for("hard", 3))
main()
