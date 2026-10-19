"""
Trip Splitter: who owes whom after the holiday?

This is the finished version. Try starter.py first, and come here when
you're done or properly stuck.

Run it with:  python3 solution.py
"""

import csv
from pathlib import Path


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# Path(__file__).parent is the folder this file is in, so the program finds
# its files wherever you run it from.
HERE = Path(__file__).parent
FRIENDS_FILE = HERE / "friends.txt"
DEFAULT_EXPENSES_FILE = "expenses.csv"
SETTLEMENT_FILE = HERE / "settlement.csv"

COLUMNS = ["payer", "amount", "description", "shared_by"]


# ---------------------------------------------------------------------------
# Our own exception
# ---------------------------------------------------------------------------

class InvalidExpense(Exception):
    """Raised when a row in the expenses file doesn't make sense."""


# ---------------------------------------------------------------------------
# Reading the files
# ---------------------------------------------------------------------------

def load_friends():
    """Read friends.txt and return the names as a set."""
    friends = set()
    # "utf-8-sig" copes with an invisible mark that some editors (like old
    # versions of Windows Notepad) put at the very start of a file. Without
    # it, the first name would come out as "\ufeffRiya" instead of "Riya".
    with open(FRIENDS_FILE, encoding="utf-8-sig") as file:
        for line in file:
            name = line.strip()
            if name != "":          # skip blank lines
                friends.add(name)
    return friends


def clean(text):
    """Strip spaces from a CSV cell. A missing cell comes through as None,
    so we treat that as empty text."""
    if text is None:
        return ""
    return text.strip()


def parse_amount(text, line_number):
    """Turn text like "1,240.50" into a whole number of paise (124050)."""
    # People write money in all sorts of ways, so tidy it up first.
    text = text.replace("₹", "").replace(",", "")
    if text == "":
        raise InvalidExpense(f"Line {line_number}: the amount is missing.")

    # Money has at most 2 numbers after the point. 10.005 is almost
    # certainly a typo, so we say so instead of quietly rounding it.
    if "." in text and len(text.split(".")[1]) > 2:
        raise InvalidExpense(f"Line {line_number}: the amount '{text}' has more than 2 numbers after the point.")

    # round(), not int()! 19.99 * 100 is 1998.9999999999998 inside the
    # computer, and int() would chop that down to 1998.
    # round() sits inside the try too, because float() accepts the words
    # "nan" and "inf", and round() can't turn those into whole numbers.
    try:
        paise = round(float(text) * 100)
    except (ValueError, OverflowError):
        raise InvalidExpense(f"Line {line_number}: the amount '{text}' isn't a number.")

    if paise <= 0:
        raise InvalidExpense(f"Line {line_number}: the amount must be more than zero, not {text}.")
    return paise


def parse_shared_by(text, friends, line_number):
    """Turn "Riya;Arjun:2;Meera" into {"Riya": 1, "Arjun": 2, "Meera": 1}.

    The number after a colon is how many shares that person has.
    No number means 1 share.
    """
    shares = {}
    for part in text.split(";"):
        part = part.strip()
        if part == "":
            continue        # allows a stray ";" at the end

        if ":" in part:
            name, count_text = part.split(":", 1)
            name = name.strip()
            try:
                count = int(count_text)
            except ValueError:
                raise InvalidExpense(f"Line {line_number}: '{part}' should look like {name}:2.")
            if count < 1:
                raise InvalidExpense(f"Line {line_number}: {name} can't have {count} shares.")
        else:
            name = part
            count = 1

        if name not in friends:
            raise InvalidExpense(f"Line {line_number}: '{name}' isn't in friends.txt. Is it a typo?")
        if name in shares:
            raise InvalidExpense(f"Line {line_number}: {name} is listed twice.")
        shares[name] = count

    if len(shares) == 0:
        raise InvalidExpense(f"Line {line_number}: nobody is listed under shared_by.")
    return shares


def parse_row(row, friends, line_number):
    """Check one CSV row and turn it into a tidy expense dictionary."""
    # DictReader puts any extra cells under the key None. That nearly always
    # means a comma inside an amount or description that wasn't in quotes.
    if None in row:
        raise InvalidExpense(f'Line {line_number}: too many commas. Put quotes around any value with a comma in it, like "1,350".')

    payer = clean(row["payer"])
    if payer == "":
        raise InvalidExpense(f"Line {line_number}: nobody is listed as the payer.")
    if payer not in friends:
        raise InvalidExpense(f"Line {line_number}: the payer '{payer}' isn't in friends.txt.")

    return {
        "payer": payer,
        "paise": parse_amount(clean(row["amount"]), line_number),
        "description": clean(row["description"]),
        "shares": parse_shared_by(clean(row["shared_by"]), friends, line_number),
    }


def load_expenses(path, friends):
    """Read every row of the expenses file.

    Returns two lists: the good expenses, and an error message for each bad
    row. We check every row before stopping, so you can fix all the
    problems in one go instead of one per run.
    """
    expenses = []
    errors = []

    # "utf-8-sig" also copes with the invisible mark Excel puts at the very
    # start of CSV files. newline="" is what the csv module asks for.
    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise InvalidExpense(f"{path.name} is completely empty.")
        if reader.fieldnames != COLUMNS:
            found = ",".join(reader.fieldnames)
            raise InvalidExpense(f"Line 1: the columns should be {','.join(COLUMNS)} but they are {found}")

        for row in reader:
            # reader.line_num is the line we're on in the file. It stays
            # right even if the file has blank lines in it.
            try:
                expenses.append(parse_row(row, friends, reader.line_num))
            except InvalidExpense as error:
                errors.append(str(error))

    return expenses, errors


# ---------------------------------------------------------------------------
# The maths
# ---------------------------------------------------------------------------

def split_amount(paise, shares):
    """Split an amount between people by their shares.

    Returns how much each person owes, e.g. {"Riya": 3334, "Arjun": 3333, ...}.
    The parts always add up to exactly `paise`.
    """
    total_shares = sum(shares.values())

    owed = {}
    for name, count in shares.items():
        # // rounds down, so this can come out a few paise short in total.
        owed[name] = paise * count // total_shares

    # Hand out the leftover paise one at a time, to people in the order
    # they were listed, until the parts add up exactly.
    leftover = paise - sum(owed.values())
    names = list(shares)
    for i in range(leftover):
        owed[names[i]] += 1

    return owed


def total_paid(expenses, friends):
    """Work out how much each person paid out of their own pocket."""
    # Sets have no fixed order, so we sort the names. That keeps the report
    # in the same order every time you run it.
    paid = {name: 0 for name in sorted(friends)}
    for expense in expenses:
        paid[expense["payer"]] += expense["paise"]
    return paid


def total_shares(expenses, friends):
    """Work out each person's fair share of everything they took part in."""
    share = {name: 0 for name in sorted(friends)}
    for expense in expenses:
        owed = split_amount(expense["paise"], expense["shares"])
        for name, amount in owed.items():
            share[name] += amount
    return share


def net_balances(paid, share):
    """Paid minus share. Above zero means you get money back; below zero
    means you owe."""
    return {name: paid[name] - share[name] for name in paid}


def settle_up(balances):
    """Work out who pays whom, using a simple greedy rule.

    The person who owes the most pays the person who is owed the most,
    as much as they can. Repeat until everyone is at zero.
    """
    # Work on a copy, so we don't wipe out the balances we were given.
    balances = balances.copy()
    payments = []

    while True:
        # Line everyone up from lowest balance to highest. The first person
        # owes the most, and the last person is owed the most.
        in_order = sorted(balances, key=lambda name: balances[name])
        debtor = in_order[0]
        creditor = in_order[-1]

        # If the person owed the most is owed nothing, everyone is even.
        if balances[creditor] == 0:
            break

        amount = min(-balances[debtor], balances[creditor])
        payments.append({"from": debtor, "to": creditor, "paise": amount})
        balances[debtor] += amount
        balances[creditor] -= amount

    return payments


# ---------------------------------------------------------------------------
# Showing and saving the results
# ---------------------------------------------------------------------------

def format_rupees(paise):
    """Turn 124050 into "₹1,240.50", and 124000 into "₹1,240"."""
    rupees = paise // 100
    leftover = paise % 100
    if leftover == 0:
        return f"₹{rupees:,}"
    return f"₹{rupees:,}.{leftover:02}"


def show_summary(expenses, paid, share, balances):
    """Print the trip total and a line for each person."""
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
    """Print the list of payments that settles everyone up."""
    print()
    if len(payments) == 0:
        print("Everyone is already even. Nothing to pay!")
        return
    print(f"To settle up, make these {len(payments)} payments:")
    for payment in payments:
        print(f"  {payment['from']} pays {payment['to']} {format_rupees(payment['paise'])}")


def save_plan(payments):
    """Save the payments to settlement.csv, so you can share it with the group."""
    with open(SETTLEMENT_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["from", "to", "amount"])
        writer.writeheader()
        for payment in payments:
            paise = payment["paise"]
            writer.writerow({
                "from": payment["from"],
                "to": payment["to"],
                # A plain number like 1240.50, which spreadsheets understand.
                "amount": f"{paise // 100}.{paise % 100:02}",
            })


# ---------------------------------------------------------------------------
# The main program
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


main()
