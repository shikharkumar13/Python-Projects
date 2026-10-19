# Project 2: Trip Splitter

**Level:** Beginner+ · **Uses chapters:** 2–7, 9 and 10

Five friends went to Goa. Everyone paid for different things along the way. Riya paid for the villa, Arjun hired the scooters, and three of them split a dinner at a beach shack. Now the trip's over and nobody knows who owes what.

In this project you'll write a program that reads all the expenses from a spreadsheet file, works out where everyone stands, and tells the group exactly who should pay whom, in just a handful of payments.

This is what it prints for the sample trip:

```
Trip total: ₹42,940.75 across 10 expenses

Name                Paid       Share   Balance
Arjun             ₹8,700   ₹9,506.67   owes ₹806.67
Kabir            ₹10,000   ₹8,206.91   gets back ₹1,793.09
Meera          ₹3,250.75   ₹8,240.25   owes ₹4,989.50
Riya             ₹19,000   ₹8,010.01   gets back ₹10,989.99
Zoya              ₹1,990   ₹8,976.91   owes ₹6,986.91

To settle up, make these 4 payments:
  Zoya pays Riya ₹6,986.91
  Meera pays Riya ₹4,003.08
  Meera pays Kabir ₹986.42
  Arjun pays Kabir ₹806.67
```

---

## What's in this folder

| File | What it is |
|---|---|
| `starter.py` | **Start here.** The program with 12 functions for you to fill in. |
| `friends.txt` | Who went on the trip, one name per line. |
| `expenses.csv` | Everything the group spent, one expense per line. |
| `expenses_with_errors.csv` | The same kind of file, full of mistakes. Use it to test your error messages. |
| `solution.py` | One finished version. Have a real go before you look. |
| `settlement.csv` | Not there yet. The program writes it, with the list of payments. |

## How to run it

Open a terminal in this folder and type:

```bash
python3 starter.py
```

On Windows, type `python` (or `py`) instead of `python3`. You can also open the file in VS Code and press the ▶ button.

The program asks which file to read. Press Enter to use `expenses.csv`, or type `expenses_with_errors.csv` to see what happens with bad data.

`.csv` files are plain text, so you can open them in VS Code. They also open in Excel or Google Sheets, where they look like a normal spreadsheet.

---

## How it works

### The expenses file

Each line is one thing someone paid for:

```
payer,amount,description,shared_by
Riya,18000,Villa for 3 nights,Riya;Arjun;Meera;Kabir;Zoya
Meera,3150.75,Dinner at the beach shack,Meera;Kabir;Zoya
Kabir,1800,Drinks on the beach,Arjun:2;Kabir;Zoya
```

- **payer** is who paid.
- **amount** is how much they paid, in rupees. `18000`, `3150.75` and `₹1350` are all fine. If you want a comma in it, like `1,350`, put quotes round it: `"1,350"`. Otherwise the comma looks like the start of a new column.
- **description** says what it was for.
- **shared_by** lists who it was for, with a `;` between names.

Usually everyone in `shared_by` pays an equal part. But if Arjun had two drinks while the others had one, you write `Arjun:2`. That gives Arjun **2 shares**. In the drinks line above there are 4 shares in total (Arjun 2, Kabir 1, Zoya 1), so Arjun pays half and the other two pay a quarter each.

### Balances

For each person the program works out:

- **Paid:** everything they paid for out of their own pocket.
- **Share:** their fair part of everything they took part in.
- **Balance:** paid minus share. If it's above zero, they get money back. If it's below zero, they owe.

All the balances always add up to exactly zero. Money just moves around the group; none is made or lost.

### Settling up

The program uses a simple rule, which is called a **greedy** rule:

1. Find the person who owes the most, and the person who is owed the most.
2. The first pays the second as much as they can: either everything they owe, or everything the other person is owed, whichever is smaller.
3. At least one of them is now at zero. Repeat until everyone is.

### Catching mistakes

Real spreadsheets have typos. The program checks every line, and for every problem it finds it prints a clear message **with the line number**, like `Line 6: 'Zoyaa' isn't in friends.txt. Is it a typo?`. It checks every line before it stops, so you can fix them all in one go.

These are the mistakes it catches:

- an amount that's missing, isn't a number, is zero or negative, or has more than 2 numbers after the point (like `10.005`)
- a payer who is missing, or isn't in `friends.txt`
- an empty `shared_by`
- a name in `shared_by` that isn't in `friends.txt`
- shares written wrongly, like `Arjun:two` or `Arjun:0`
- the same person listed twice
- a line with too many commas, usually from a comma that should have been inside quotes
- a file with the wrong column names, or nothing in it at all
- a file that Excel saved in an old format instead of UTF-8 (see the tip below)

> **Tip for Excel users:** when you save a CSV from Excel, choose **CSV UTF-8**. The plain "CSV" option uses an older format, and this program can't read letters like the é in Café from it.

### Your must-have checklist

- [ ] Expenses are read from a CSV file with `csv.DictReader`
- [ ] Equal splits and custom shares (`Arjun:2`) both work
- [ ] Every person's balance is worked out with a dictionary
- [ ] Money is stored as whole **paise**, never as a float
- [ ] The greedy rule produces a list of payments
- [ ] The report says things like "Meera pays Riya ₹1,240"
- [ ] The payments are saved to `settlement.csv` with `csv.DictWriter`
- [ ] Bad rows raise a custom `InvalidExpense`, and every message has its line number

---

## Building it, one step at a time

Open `starter.py`. A few parts are already written for you: the settings, the `InvalidExpense` exception, `clean()`, the two `show_` functions, `choose_file()` and `main()`. Your job is the 12 TODOs.

**You can run the file at any time.** Each unfinished function returns a *placeholder*, an empty value like `set()` or `{}`, so nothing crashes. As you finish each step, the program gets further. Until then, some of its messages won't be true, because they're based on placeholders:

- Before TODO 1, it says `No names found in friends.txt.`
- After TODO 1, it says `There are no expenses in expenses.csv yet.` until you finish TODO 5.
- After TODO 5, the report ends with `Everyone is already even.` until you finish TODO 10.

Nothing's wrong with the files. Those messages go away as you fill in the steps.

**To test one function on its own**, go to the last line, put a `#` in front of `main()`, and add a print:

```python
# main()
print(split_amount(10000, {"Riya": 1, "Arjun": 1, "Meera": 1}))
```

Put `main()` back when you're done.

### First, our own exception

Near the top of the file you'll find this:

```python
class InvalidExpense(Exception):
    """Raised when a row in the expenses file doesn't make sense."""
```

That's all it takes to make your own kind of error. You'll learn what `class` really means in chapter 8. For now, just know that you can `raise` it and `except` it exactly like `ValueError`:

```python
raise InvalidExpense("Line 4: the amount 'abc' isn't a number.")
```

Why not just use `ValueError`? Because our own name makes the code say what it means. In TODO 5, `except InvalidExpense` catches *our* problems with the data, and nothing else by accident.

### Step 1: Reading the friends (`load_friends`)

Open the file with `encoding="utf-8-sig"`. Some editors, like older versions of Windows Notepad, put an invisible mark at the very start of a file. With plain `"utf-8"` that mark sticks to the first name, so you'd get `"\ufeffRiya"`, and then every line with Riya would fail with "Riya isn't in friends.txt". `"utf-8-sig"` quietly removes the mark.

Loop over the file line by line, `.strip()` each line, and `.add()` the non-empty ones to a set.

Careful: an empty set is `set()`. Writing `{}` gives you an empty **dictionary**.

We use a set because the only question we ever ask is "is this person on the trip?", and a set answers that instantly. And if a name appears twice in the file, the set just keeps one.

**Check it:** `print(load_friends())` shows the five names. The order may change from run to run, because sets don't keep things in order.

### Step 2: Reading an amount (`parse_amount`)

First tidy the text: `text.replace("₹", "").replace(",", "")` turns `"₹1,350"` into `"1350"`. Then do two quick checks, each raising `InvalidExpense`:

- Is the text empty? Then the amount is missing.
- Are there more than 2 numbers after the point? `text.split(".")[1]` is the part after it. `10.005` is almost certainly a typo, and with money it's better to ask than to guess.

Now turn it into paise with `round(float(text) * 100)`. **Use `round()`, not `int()`.** [The big idea](#the-big-idea-never-store-money-as-a-float) below explains why.

Put that whole line inside **one** `try`. Here's why both steps need to be in there: `float()` happily accepts the words `"nan"` ("not a number") and `"inf"` (infinity). It's `round()` that fails on them, with a `ValueError` for `nan` and an `OverflowError` for `inf`. You can catch two kinds of error at once like this:

```python
except (ValueError, OverflowError):
```

Finally, raise `InvalidExpense` if the paise come out at 0 or less.

**Check it:**
`parse_amount("19.99", 2)` → `1999`
`parse_amount("₹1,350", 2)` → `135000`
`parse_amount("-5", 2)` → raises `InvalidExpense`
`parse_amount("nan", 2)` → raises `InvalidExpense`, not a crash

### Step 3: Reading who shared it (`parse_shared_by`)

This is the longest step. Split on `";"` and look at each part on its own:

- `"Riya"` has no colon, so the name is `"Riya"` and the count is 1.
- `"Arjun:2"` has a colon, so `part.split(":", 1)` gives `["Arjun", "2"]`. Then `int("2")` gives the count.

The `1` in `split(":", 1)` means "split at the first colon only", and it matters more than it looks. Suppose someone types `Arjun:2:3`. Without the `1`, you'd get three pieces, and `name, count_text = ...` crashes with `too many values to unpack`. With the `1`, you get `["Arjun", "2:3"]`. Then `int("2:3")` fails inside your `try`, and the user gets a clear message instead.

The checks are easiest as a row of `if` statements, each one raising `InvalidExpense` with its own message. Look at the list under [Catching mistakes](#catching-mistakes) for what to check.

**Check it:** `parse_shared_by("Riya; Arjun:2", load_friends(), 2)` → `{'Riya': 1, 'Arjun': 2}`

### Step 4: Checking one row (`parse_row`)

`csv.DictReader` gives you each row as a dictionary. If a line has more cells than there are columns, DictReader puts the extra ones under the key `None`. So start with `if None in row:` and raise an error that tells the user about quotes.

Then check the payer, then hand the other cells to the functions from Steps 2 and 3. Return a fresh dictionary holding the cleaned-up values.

Notice that you don't need any `try` in this function. If `parse_amount()` raises `InvalidExpense`, the error passes straight up through `parse_row()` to whoever called it. Exceptions travel up until something catches them.

### Step 5: Reading the whole file (`load_expenses`)

Open the file like this:

```python
with open(path, encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
```

- `newline=""` is something the `csv` module asks for. Without it, some line endings get mixed up.
- `"utf-8-sig"` copes with the same invisible mark as in Step 1. Excel adds it when it saves a CSV UTF-8 file, and with plain `"utf-8"` it would end up stuck to the first column name.

Before reading any rows, check the columns. `reader.fieldnames` is the list of names from the first line, or `None` if the file is completely empty. In your error message, show the columns you *found* as well as the ones you expected. A very common mistake is `payer, amount, ...` with a space after each comma, and it's easy to spot when both versions are printed together.

Then loop over the reader, and catch the errors **inside** the loop:

```python
for row in reader:
    try:
        expenses.append(parse_row(row, friends, reader.line_num))
    except InvalidExpense as error:
        errors.append(str(error))
```

Because the `try` is inside the loop, one bad row doesn't stop the others from being checked. `reader.line_num` is the line of the file we're on. It stays right even if the file has blank lines, which counting rows yourself wouldn't.

**Why not just `line.split(",")`?** Look at line 10 of `expenses.csv`: `"Fish thali, fries and juice"`. That description has commas in it, so it's wrapped in quotes. The `csv` module understands quotes; `split(",")` would chop the description into three pieces.

**Check it:** run the program with `expenses_with_errors.csv`. You should get 7 problems, on lines 3 to 9.

### Step 6: Splitting one amount (`split_amount`)

How do you split ₹100 (10,000 paise) between three people?

```python
10000 // 3     # 3333
```

Three lots of 3,333 is 9,999. One paisa has gone missing! `//` always rounds down, so this happens all the time. Here's the fix:

1. Give everyone their rounded-down part.
2. Work out what's left over: `leftover = paise - sum(owed.values())`
3. Hand out the leftover paise one at a time, starting with the first person listed.

Now ₹100 splits as 3,334 + 3,333 + 3,333, which adds up perfectly. That's why Riya's share in the sample ends in a stray paisa (`₹8,010.01`). She's listed first for the coconut water and for the last dinner, so she picked up the odd paise from both.

The leftover is always smaller than the number of people, so `names[i]` never runs off the end of the list.

**Check it:** `split_amount(10000, {"Riya": 1, "Arjun": 1, "Meera": 1})` → `{'Riya': 3334, 'Arjun': 3333, 'Meera': 3333}`

### Steps 7 and 8: Totals (`total_paid` and `total_shares`)

Both start everyone at 0 with a dictionary comprehension:

```python
paid = {name: 0 for name in sorted(friends)}
```

Why `sorted(friends)`? Sets have no fixed order, so the report would come out in a different order on different runs. Sorting fixes the order, and as a bonus the table comes out in alphabetical order.

`total_paid` adds each expense to its payer. `total_shares` calls `split_amount()` for each expense and adds each person's part to their total.

### Step 9: Balances (`net_balances`)

This is one line: a dictionary comprehension that does `paid[name] - share[name]` for every name.

Once this step works, `main()` checks your maths with:

```python
assert sum(balances.values()) == 0, "The balances don't add up to zero!"
```

If you ever see that `AssertionError`, a paisa has gone missing somewhere. Go back to Step 6.

### Step 10: Settling up (`settle_up`)

First make a copy with `balances.copy()`. Without it, your function would quietly change the dictionary that `main()` passed in.

Each time round the loop, line everyone up from lowest balance to highest:

```python
in_order = sorted(balances, key=lambda name: balances[name])
```

On its own, `sorted(balances)` would sort the *names*, alphabetically. `key=` tells it to sort by something else. Here, for each name it looks up that person's balance. So `in_order[0]` owes the most, and `in_order[-1]` is owed the most.

Then work out the payment, record it, and update both balances. Stop when the person at the end of the line is owed nothing, because that means everyone is at zero.

**Is it really the fewest payments?** Each payment brings at least one person to zero, so with 5 people you never need more than 4 payments. That's usually the best you can do, but not always. If Meera owed exactly what Kabir is owed, the two of them could settle with one payment and leave the rest separate. Finding the true minimum every time is a much harder problem. The greedy rule is simple, quick and good enough for a group of friends.

### Step 11: Showing money (`format_rupees`)

```python
rupees = 124050 // 100      # 1240
leftover = 124050 % 100     # 50
f"₹{rupees:,}.{leftover:02}"     # "₹1,240.50"
```

`:,` adds the commas. `:02` pads a number to two digits, so 5 paise shows as `.05`, not `.5`. If the leftover is 0, leave off the `.00`, so it shows `₹1,240`.

> The commas are placed the international way (`₹124,000`), not the Indian way (`₹1,24,000`). Python's `:,` only knows the first one.

### Step 12: Saving the plan (`save_plan`)

`csv.DictWriter` is the opposite of `DictReader`: you hand it dictionaries, and it writes lines.

```python
writer = csv.DictWriter(file, fieldnames=["from", "to", "amount"])
writer.writeheader()
writer.writerow({"from": "Meera", "to": "Riya", "amount": "4003.08"})
```

Open the file with `newline=""` here too. Afterwards, open `settlement.csv` in a spreadsheet and look at it.

---

## The big idea: never store money as a float

Try this in Python:

```python
>>> 0.1 + 0.2
0.30000000000000004
```

That isn't a Python bug. Computers store decimal numbers in binary, and most decimals, like 0.1, can't be stored exactly. They're stored as something extremely close. Usually nobody notices, but money is exactly where you do:

```python
>>> 19.99 * 100
1998.9999999999998
>>> int(19.99 * 100)
1998
```

`int()` doesn't round; it just chops off everything after the decimal point. So ₹19.99 would become 1,998 paise, and a paisa would silently disappear. Add up a few hundred of those and the trip doesn't balance.

That's why this program does two things:

1. **It stores every amount as a whole number of paise.** Whole numbers (`int`) are always exact. 1,999 paise is exactly 1,999 paise, forever.
2. **It rounds on purpose, once.** When reading an amount, `round(rupees * 100)` turns `1998.9999999999998` into `1999`. After that, every sum is done with whole numbers.

Then, when ₹100 has to be split three ways, the program decides exactly where the odd paisa goes (Step 6), instead of letting it vanish. That's what lets `main()` promise, with an `assert`, that the balances add up to exactly zero.

Real money software is careful in the same way. It either counts in the smallest coin (paise, cents), like we do, or uses special exact decimal numbers. Plain floats are kept well away from money.

---

## Try to break it

Make a copy of `expenses.csv` to experiment on, and run the program with the copy. Each of these should give a clear message, not a crash:

- [ ] Run it with `expenses_with_errors.csv`. You should see 7 problems, each with its line number
- [ ] Type the name of a file that doesn't exist
- [ ] Rename the `amount` column to `cost` in the first line
- [ ] Leave a completely blank line in the middle of the file. The line numbers in any error messages should still be right
- [ ] Add a line with only `Riya,500`, and nothing after it
- [ ] Write an amount as `"₹2,500"`, with the quotes. It should work. Then take the quotes away: you should get the "too many commas" message
- [ ] Add an expense of `0.01` shared by three people. The program should still balance
- [ ] Type `nan` as an amount. Python's `float()` accepts it, but your program shouldn't
- [ ] Type an amount with 3 numbers after the point, like `10.005`
- [ ] Make a file with just one expense, shared only by the person who paid it. It should say nobody needs to pay
- [ ] On Windows: open `settlement.csv` in Excel, leave it open, and run the program again

---

## Stretch goals

Finished? Pick one. There's no solution for these.

### 1. Category totals

Add a fifth column, `category`, with values like `food`, `travel` and `stay`. Then show how much the trip spent on each, with the biggest category highlighted.

- Add `"category"` to `COLUMNS`, and keep it in the dictionary that `parse_row()` returns.
- Add up the totals in a dictionary, just like `total_paid()`.
- `max(totals, key=lambda name: totals[name])` finds the biggest category. It's the same `key=` idea as Step 10.

### 2. Several currencies

Part of the trip was in Thailand, and someone paid in baht.

- Add a `currency` column (`INR`, `THB`, `USD`), and a fixed table of rates in paise, like `RATES = {"INR": 100, "THB": 245, "USD": 8350}`. Those rates are made up; look up real ones if you like.
- Give `parse_amount()` a third argument, `currency`, and pass in the cleaned value from the new column. Then convert with `round(float(text) * RATES[currency])`. Everything after that stays the same, because the rest of the program only ever sees paise.
- Raise `InvalidExpense` for a currency that isn't in the table.

### 3. Fairer leftover paise

Right now, the leftover paise always go to whoever is listed first. That means Riya might pay an extra paisa even when her share already came out exact. A fairer rule gives each leftover paisa to the person whose share was rounded down the most.

- `paise * count % total_shares` tells you how much was chopped off each person's part. A bigger number means more was rounded away.
- Sort the names by that number, biggest first (`sorted` with `key=` and `reverse=True`), and hand out the leftover paise in that order.

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 2. Lists, tuples and strings | `.split(";")`, `.strip()`, `.replace()`, f-string formats like `:,` and `:02`, `in_order[-1]`, returning `expenses, errors` as a tuple |
| 3. Sets and dictionaries | the set of friends, the shares, the balances, dictionary comprehensions, `.copy()` |
| 4. Operators | `//` and `%` for paise, why `0.1 + 0.2` isn't `0.3` |
| 5. Conditionals and loops | checking every row, the `while True` settle-up loop |
| 6. Functions | one job per function, with each one handing its result to the next |
| 7. Lambda and `key=` | `sorted(balances, key=lambda name: balances[name])` |
| 9. Exceptions | your own `InvalidExpense`, `raise`, catching two kinds of error at once, catching errors inside a loop, `assert` |
| 10. Files, CSV | `csv.DictReader` and `DictWriter`, `newline=""`, `utf-8-sig` |
