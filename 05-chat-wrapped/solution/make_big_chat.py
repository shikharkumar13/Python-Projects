"""Write big_chat.txt: 200,000 made-up messages, about 8 MB of text.

Run it from this folder with:  python make_big_chat.py
Then try:                      python -m wrapped big_chat.txt

The point is to see that the generator copes with a big chat just as
happily as a small one, because it only ever holds one message at a time.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "big_chat.txt"
MESSAGES = 200_000

PEOPLE = ["Riya", "Arjun", "Meera", "Kabir", "Zoya", "Dev", "Ananya", "Rohan"]
TEXTS = ["haha", "same", "yaar what", "bro I'm in", "omg 😍", "lol 😂", "who's free tonight",
         "ok see you there 👍", "bhai send the photos", "<Media omitted>", "can't wait 🔥",
         "Shopping list:\n- milk\n- bread"]


def main() -> None:
    random.seed(7)
    when = datetime(2025, 1, 1, 8, 0)
    # The file is written one line at a time too, so this script doesn't need
    # much memory either.
    with open(OUTPUT, "w", encoding="utf-8") as file:
        for _ in range(MESSAGES):
            when += timedelta(seconds=random.randint(5, 300))
            file.write(f"{when:%d/%m/%Y, %H:%M} - {random.choice(PEOPLE)}: {random.choice(TEXTS)}\n")
    size = OUTPUT.stat().st_size / 1_000_000
    print(f"Wrote {MESSAGES:,} messages to {OUTPUT.name} ({size:.1f} MB).")
    print("Now try:  python -m wrapped big_chat.txt")


main()
