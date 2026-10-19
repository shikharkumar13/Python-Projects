"""Make a habits.json with 12 weeks of made-up history, so the heatmap has
something to show straight away.

Run it from this folder with:  python make_sample_data.py

It won't overwrite a habits.json that's already there.
"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "habits.json"

# Each habit, and how likely it is to be done on any one day.
HABITS = {"read 20 pages": 0.8, "drink water": 0.9, "practise python": 0.55}


def main() -> None:
    if DATA_FILE.exists():
        print(f"{DATA_FILE.name} already exists, so I've left it alone.")
        print("Move it somewhere else first if you want the sample data.")
        return

    random.seed(4)       # the same "random" history every time
    today = date.today()
    start = today - timedelta(weeks=12)

    habits = []
    for name, chance in HABITS.items():
        done = []
        day = start
        while day < today:           # up to yesterday: today is yours to do
            if random.random() < chance:
                done.append(day.isoformat())
            day += timedelta(days=1)
        habits.append({"name": name, "created": start.isoformat(), "done": done})

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump({"habits": habits}, file, indent=2)
    print(f"Wrote {DATA_FILE.name} with {len(habits)} habits and 12 weeks of history.")
    print("Now try:  python -m streaks status")


main()
