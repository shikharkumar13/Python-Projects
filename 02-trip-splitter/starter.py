"""
Trip Splitter: your starter file.

Work through the TODOs in order, from TODO 1 to TODO 12. README.md has a
hint for every step if you get stuck.

Run it with:  python3 starter.py

Some functions are already written for you: our exception, clean(), the
two show_ functions, choose_file() and main(). You fill in the rest.

Each unfinished function returns a "placeholder", an empty value like
set() or {}, so the program can run before you've written everything.
Replace the placeholder line with your own code.
"""

import csv
from pathlib import Path


# ---------------------------------------------------------------------------
# Settings (already done)
# ---------------------------------------------------------------------------

# Path(__file__).parent is the folder this file is in, so the program finds
# its files wherever you run it from.
HERE = Path(__file__).parent
FRIENDS_FILE = HERE / "friends.txt"
DEFAULT_EXPENSES_FILE = "expenses.csv"
SETTLEMENT_FILE = HERE / "settlement.csv"

COLUMNS = ["payer", "amount", "description", "shared_by"]


# ---------------------------------------------------------------------------
# Our own exception (already done)
# ---------------------------------------------------------------------------

class InvalidExpense(Exception):
    """Raised when a row in the expenses file doesn't make sense."""


# ---------------------------------------------------------------------------
# Reading the files
# ---------------------------------------------------------------------------

def load_friends():
    """Read friends.txt and return the names as a set."""
    # TODO 1
    # - Start with an empty set:  friends = set()   ({} would be a dictionary!)
    # - Open FRIENDS_FILE with encoding="utf-8-sig" (the README explains
    #   why) and loop over it line by line.
    # - .strip() each line. If it isn't empty, .add() it to the set.
    # - Return the set.
    return set()   # placeholder: replace this line


def clean(text):
    """Strip spaces from a CSV cell. A missing cell comes through as None,
    so we treat that as empty text. (Already done.)"""
    if text is None:
        return ""
    return text.strip()


def parse_amount(text, line_number):
    """Turn text like "1,240.50" into a whole number of paise (124050)."""
    # TODO 2
    # - Remove any "₹" and "," from the text with .replace().
    # - If the text is now empty, raise InvalidExpense: the amount is missing.
    # - If it has a "." with more than 2 numbers after it, raise InvalidExpense.
    #   Hint: text.split(".")[1] is the part after the point.
    # - Inside ONE try, do both steps:  paise = round(float(text) * 100)
    #   Use round(), NOT int(). The README explains why.
    #   Catch both ValueError and OverflowError:
    #     except (ValueError, OverflowError):
    #   and raise InvalidExpense(f"Line {line_number}: ...") with a clear message.
    # - If the paise are 0 or less, raise InvalidExpense too.
    # - Return the paise.
    return 0   # placeholder: replace this line


def parse_shared_by(text, friends, line_number):
    """Turn "Riya;Arjun:2;Meera" into {"Riya": 1, "Arjun": 2, "Meera": 1}.

    The number after a colon is how many shares that person has.
    No number means 1 share.
    """
    # TODO 3
    # - Start with an empty dictionary called `shares`.
    # - Split the text on ";" and loop over the parts. .strip() each part,
    #   and skip any that are empty.
    # - If the part has a ":" in it, split it into a name and a count with
    #   part.split(":", 1), and turn the count into an int. Raise
    #   InvalidExpense if that fails, or if the count is less than 1.
    #   No ":" means the whole part is the name and the count is 1.
    # - Raise InvalidExpense if the name isn't in `friends`, or is already
    #   in `shares` (listed twice).
    # - Add the name and count to `shares`.
    # - After the loop, raise InvalidExpense if `shares` is still empty.
    # - Return `shares`.
    return {}   # placeholder: replace this line


def parse_row(row, friends, line_number):
    """Check one CSV row and turn it into a tidy expense dictionary."""
    # TODO 4
    # - `row` is a dictionary from csv.DictReader, like
    #   {"payer": "Riya", "amount": "18000", "description": "...", "shared_by": "..."}
    # - If the line had too many commas, DictReader puts the extra cells
    #   under the key None. So if `None in row`, raise InvalidExpense and
    #   tell the user to put quotes around values that contain a comma.
    # - Get the payer with clean(row["payer"]). Raise InvalidExpense if it's
    #   empty or not in `friends`.
    # - Return a new dictionary with four keys:
    #     "payer":       the cleaned payer
    #     "paise":       parse_amount(...) of the cleaned amount
    #     "description": the cleaned description
    #     "shares":      parse_shared_by(...) of the cleaned shared_by
    return {}   # placeholder: replace this line


def load_expenses(path, friends):
    """Read every row of the expenses file.

    Returns two lists: the good expenses, and an error message for each bad
    row. We check every row before stopping, so you can fix all the
    problems in one go instead of one per run.
    """
    # TODO 5
    # - Make two empty lists: `expenses` and `errors`.
    # - Open the file like this (the README explains both extra arguments):
    #     with open(path, encoding="utf-8-sig", newline="") as file:
    # - Make a csv.DictReader(file). reader.fieldnames holds the column names
    #   from the first line, or None if the file is completely empty.
    #   Raise InvalidExpense if it's None, or isn't the same as COLUMNS.
    #   (Showing the columns you actually found makes the message more useful.)
    # - Loop over the reader. For each row, call parse_row() inside a try.
    #   Use reader.line_num as the line number.
    #     - It worked: append the result to `expenses`.
    #     - except InvalidExpense as error: append str(error) to `errors`.
    # - Return both lists:  return expenses, errors
    return [], []   # placeholder: replace this line


# ---------------------------------------------------------------------------
# The maths
# ---------------------------------------------------------------------------

def split_amount(paise, shares):
    """Split an amount between people by their shares.

    Returns how much each person owes, e.g. {"Riya": 3334, "Arjun": 3333, ...}.
    The parts always add up to exactly `paise`.
    """
    # TODO 6
    # - Add up all the shares with sum(shares.values()).
    # - For each person, their part is  paise * their_count // total_shares
    #   Store it in a new dictionary called `owed`.
    # - // rounds down, so a few paise can go missing. Work out the leftover:
    #     leftover = paise - sum(owed.values())
    # - Give 1 extra paisa to each of the first `leftover` people.
    #   Hint: names = list(shares), then loop with range(leftover).
    # - Return `owed`.
    return {}   # placeholder: replace this line


def total_paid(expenses, friends):
    """Work out how much each person paid out of their own pocket."""
    # TODO 7
    # - Start everyone at 0. Use sorted(friends) so the order is the same
    #   every run:  paid = {name: 0 for name in sorted(friends)}
    # - Loop over the expenses and add each one's paise to its payer.
    # - Return `paid`.
    return {}   # placeholder: replace this line


def total_shares(expenses, friends):
    """Work out each person's fair share of everything they took part in."""
    # TODO 8
    # - Start everyone at 0, just like TODO 7.
    # - For each expense, call split_amount() and add each person's part
    #   to their total.
    # - Return the totals.
    return {}   # placeholder: replace this line


def net_balances(paid, share):
    """Paid minus share. Above zero means you get money back; below zero
    means you owe."""
    # TODO 9
    # - Return a new dictionary: for each name, paid[name] - share[name].
    #   One line with a dictionary comprehension does it.
    return {}   # placeholder: replace this line


def settle_up(balances):
    """Work out who pays whom, using a simple greedy rule.

    The person who owes the most pays the person who is owed the most,
    as much as they can. Repeat until everyone is at zero.
    """
    # TODO 10
    # - Make a copy first:  balances = balances.copy()
    # - Start an empty list called `payments`, then loop with `while True:`
    #     - Line the names up from lowest balance to highest:
    #         in_order = sorted(balances, key=lambda name: balances[name])
    #     - The first name owes the most (debtor = in_order[0]) and the last
    #       is owed the most (creditor = in_order[-1]).
    #     - If the creditor's balance is 0, everyone is even, so `break`.
    #     - The amount is the smaller of what the debtor owes (-their balance)
    #       and what the creditor is owed.
    #     - Append {"from": debtor, "to": creditor, "paise": amount}.
    #     - Add the amount to the debtor's balance and take it off the
    #       creditor's balance.
    # - Return `payments`.
    return []   # placeholder: replace this line


# ---------------------------------------------------------------------------
# Showing and saving the results
# ---------------------------------------------------------------------------

def format_rupees(paise):
    """Turn 124050 into "₹1,240.50", and 124000 into "₹1,240"."""
    # TODO 11
    # - Whole rupees:  paise // 100.    Leftover paise:  paise % 100.
    # - f"{rupees:,}" adds the commas, and f"{leftover:02}" turns 5 into "05".
    # - If the leftover is 0, leave off the ".00".
    return ""   # placeholder: replace this line


def show_summary(expenses, paid, share, balances):
    """Print the trip total and a line for each person. (Already done.)"""
    trip_total = sum(paid.values())
    print()
    print(f"Trip total: {format_rupees(trip_total)} across {len(expenses)} expenses")
    print()
    print(f"{'Name':<12}{'Paid':>12}{'Share':>12}   Balance")
    for name in balances:
        if balances[name] > 0:
            status = f"gets back {format_rupees(balances[name])}"
        elif balances[name] < 0:
            status = f"owes {format_rupees(-balances[name])}"
        else:
            status = "all square"
        print(f"{name:<12}{format_rupees(paid[name]):>12}{format_rupees(share[name]):>12}   {status}")


def show_payments(payments):
    """Print the list of payments that settles everyone up. (Already done.)"""
    print()
    if len(payments) == 0:
        print("Everyone is already even. Nothing to pay!")
        return
    print(f"To settle up, make these {len(payments)} payments:")
    for payment in payments:
        print(f"  {payment['from']} pays {payment['to']} {format_rupees(payment['paise'])}")


def save_plan(payments):
    """Save the payments to settlement.csv, so you can share it with the group."""
    # TODO 12
    # - Open SETTLEMENT_FILE in "w" mode, with encoding="utf-8" and newline="".
    # - Make a csv.DictWriter(file, fieldnames=["from", "to", "amount"]) and
    #   call .writeheader() on it.
    # - For each payment, .writerow() a dictionary with those three keys.
    #   Write the amount as a plain number like 1240.50, without the ₹ or commas:
    #     f"{paise // 100}.{paise % 100:02}"
    pass


# ---------------------------------------------------------------------------
# The main program (already done)
# ---------------------------------------------------------------------------

def choose_file():
    """Ask which expenses file to use. Pressing Enter picks expenses.csv."""
    name = input(f"Which expenses file? (press Enter for {DEFAULT_EXPENSES_FILE}): ").strip()
    if name == "":
        name = DEFAULT_EXPENSES_FILE
    return HERE / name


def main():
    print("Trip Splitter")

    try:
        friends = load_friends()
    except FileNotFoundError:
        print("I can't find friends.txt. Make sure it's in the same folder as this file.")
        return
    if len(friends) == 0:
        print("No names found in friends.txt.")
        return

    path = choose_file()
    try:
        expenses, errors = load_expenses(path, friends)
    except FileNotFoundError:
        print(f"I can't find {path.name}. Make sure it's in the same folder as this file.")
        return
    except UnicodeDecodeError:
        # Excel's plain "CSV" option saves accented letters (like the é in
        # Café) in an older format that isn't UTF-8.
        print(f"{path.name} isn't saved as UTF-8 text. In Excel, use Save As and pick 'CSV UTF-8'.")
        return
    except InvalidExpense as error:
        print(error)
        return

    if len(errors) > 0:
        print(f"I found {len(errors)} problem(s) in {path.name}. Fix them and run me again:")
        for error in errors:
            print("  " + error)
        return
    if len(expenses) == 0:
        print(f"There are no expenses in {path.name} yet.")
        return

    paid = total_paid(expenses, friends)
    share = total_shares(expenses, friends)
    balances = net_balances(paid, share)

    # Money is never created or lost: what was paid out must equal what was
    # shared, to the paisa. This is why we count in whole paise.
    assert sum(balances.values()) == 0, "The balances don't add up to zero!"

    show_summary(expenses, paid, share, balances)
    payments = settle_up(balances)
    show_payments(payments)
    try:
        save_plan(payments)
    except PermissionError:
        # On Windows, a file that's open in Excel can't be written to.
        print()
        print(f"I couldn't save {SETTLEMENT_FILE.name}. Is it open in another program, like Excel? Close it and run me again.")
        return
    print()
    print(f"Saved the plan to {SETTLEMENT_FILE.name}.")


# Want to try one function on its own? Put a # in front of main() below,
# and add a line like this instead:   print(split_amount(10000, {"Riya": 1, "Arjun": 1, "Meera": 1}))
main()
