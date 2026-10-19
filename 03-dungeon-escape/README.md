# Project 3: Dungeon Escape

**Level:** Beginner → Intermediate · **Uses chapters:** 5–10 and 12, plus one idea from 13

You wake up in a dungeon with a torch and 3 health points. You explore the rooms, pick things up, fight a goblin and a dragon, find the key and escape. And if you need to stop halfway, you save your game and carry on tomorrow.

In this project you'll build that game. It's the first project where you write your own **classes**: a `Player`, `Room`s, `Item`s and `Enemy`s, each looking after its own little part of the game.

```
== Old armory ==
Racks of broken spears and dented shields line the walls.
You can see: sword
Exits: west

Health ♥♥♥   Carrying: torch
> take sword
You pick up the sword.
Something small scuttles past your feet.

Health ♥♥♥   Carrying: torch, sword
> 
```

---

## What's in this folder

| File | What it is |
|---|---|
| `starter.py` | **Start here.** The game with 17 pieces missing, for you to fill in. |
| `dungeon.json` | The map: every room, exit, item and enemy. Change it to make your own dungeon, with no code changes needed. |
| `solution.py` | One finished version. Have a real go before you look. |
| `savegame.json` | Not there yet. The game writes it when you type `save`. |

## How to run it

Open a terminal in this folder and type:

```bash
python3 starter.py
```

On Windows, type `python` (or `py`) instead of `python3`. You can also open the file in VS Code and press the ▶ button.

Try `python3 solution.py` first and play the finished game for a few minutes. It's much easier to build something once you've seen it working.

---

## How to play

| Type this | What happens |
|---|---|
| `look` | Describe the room you're in |
| `go north` | Walk through an exit (north, south, east or west) |
| `take sword` | Pick up something in the room |
| `use potion` | Drink a potion (gives back 2 health) |
| `use key` | Unlock a door, if you're next to the right one |
| `inventory` | List what you're carrying |
| `save` / `load` | Save your game, or go back to your last save |
| `help` | List the commands |
| `quit` | Stop playing |

**Fights.** Walk into a room with an enemy and a fight starts. Each round you choose `attack`, `use potion` or `run`. Then, if the enemy is still standing, it attacks you. Running takes you back to the room you came from, but the enemy remembers how hurt it is.

**Enemies.** Goblins are weak, and sometimes they throw sand instead of attacking. Dragons are tougher, and every third turn they breathe fire, which never misses.

**Winning and losing.** Get through the locked gate to escape. If your health reaches 0, it's game over.

---

## How the code is organised

Each class has one job:

| Class | What it knows | What it can do |
|---|---|---|
| `Item` | its name, description, how much it heals, how much damage it adds | describe itself |
| `Room` | its exits, its items, its enemy, which exits are locked | describe itself, hand over an item, unlock an exit |
| `Player` | which room you're in, your health, what you're carrying | show a status bar, take damage, heal |
| `Enemy` | its name, health and damage | attack the player |
| `Goblin`, `Dragon` | the same as `Enemy`, because they're built on it | attack in their own special way |
| `Game` | all of the above | read your commands and make everything work together |

Notice that a `Room` never knows about the `Player`. That's on purpose. The [big idea](#the-big-idea-what-belongs-in-which-class) section explains why.

### Your must-have checklist

- [ ] The dungeon is loaded from `dungeon.json`, and changing that file changes the game
- [ ] `Player`, `Room`, `Item` and `Enemy` classes, with `Goblin` and `Dragon` overriding `attack()`
- [ ] Commands go through one command table: a dictionary of word → method
- [ ] All eight commands work: `go`, `take`, `use`, `inventory`, `look`, `save`, `load`, `quit`
- [ ] Turn-based fights, using `random` with a seed
- [ ] `GameOver` is raised when health hits 0, and caught in `main()`
- [ ] `save` and `load` remember everything, including which items you've taken and which enemies you've beaten
- [ ] `print(player)` shows a status bar, thanks to `__str__`
- [ ] A recursive function checks the way out can be reached, before the game starts
- [ ] A generator produces random spooky events every few turns

---

## Building it, one step at a time

Open `starter.py`. A lot is already written. Read through it first: the finished parts show you how the missing parts should look. The `Item` class is complete, and it's a good small example of a class.

**You can run the file at any time.** Each unfinished function has a *placeholder* that keeps the game running. Until you write TODO 2, the only command that works is `quit`. After that, the game comes alive a piece at a time.

**To test one thing on its own**, go to the last line, put a `#` in front of `main()`, and add a print instead:

```python
# main()
print(Player("cell", 3, []))
```

Put `main()` back when you're done.

### Part 1: Understanding commands

#### Step 1: The command table (`Game.build_commands`)

When the player types `take sword`, the game has to run the `take` method. You could do that with a long chain of `if`s:

```python
if verb == "go":
    self.go(noun)
elif verb == "take":
    self.take(noun)
elif verb == "use":
    ...and so on, for every command
```

But there's a neater way. In Python, a function (or method) is a value, just like a number or a string. You can store it in a dictionary, and call it later:

```python
commands = {"go": self.go, "take": self.take}
commands["take"]("sword")      # does the same as self.take("sword")
```

Look carefully: it's `self.go`, **not** `self.go()`. With the brackets, Python would run the method straight away and store whatever it returned. Without them, you're storing the method itself, ready to call later.

This dictionary is called a **command table**, or a *dispatch table*. Adding a new command is now just one more line in the table, plus the method.

#### Step 2: Running a command (`Game.handle`)

```python
words = command.strip().lower().split(maxsplit=1)
```

`maxsplit=1` means "split at the first space only". So `go north` gives `["go", "north"]`, and `take rusty sword` gives `["take", "rusty sword"]`, keeping the item's whole name together.

Then look up the verb and call it: `self.commands[verb](noun)`. That's why **every** command method takes a `noun`, even the ones that don't need one, like `look` and `quit`. `handle()` calls them all in exactly the same way, so they all have to accept it.

**Check it:** type `help`, then `look`, then `dance`. The last one should get a friendly "I don't know how to" message.

### Part 2: Moving and items

#### Step 3: Walking around (`Game.go`)

Check the problems one at a time, and only move if none of them apply: no direction, no such exit, a locked exit. To move, call `self.enter_room(...)`. It's already written, and it also starts fights and checks whether you've escaped.

`room.exits` is a dictionary like `{"north": "corridor", "south": "cell"}`. So `room.exits[direction]` gives you the id of the room in that direction.

> **A map is a graph.** Each room is a point, and each exit is an arrow to another point. A dictionary of rooms, each with a dictionary of exits, is all you need to store one. You'll use this again in Step 16.

#### Step 4: Handing over an item (`Room.take_item`)

Loop over the items. When you find the right one, `.remove()` it from the list and `return` it.

Usually it's a bad idea to remove things from a list while you're looping over it, because the loop gets confused about where it's up to. It's fine here, because you `return` straight away, so the loop never takes another step.

#### Step 5: Picking things up (`Game.take`)

The room hands over the item, and the game gives it to the player:

```python
item = self.current_room().take_item(name)
```

The room doesn't put the item in the player's inventory itself. It doesn't even know there *is* a player. The `Game` is the one that passes things between them.

#### Step 6: Healing (`Player.heal`)

`min(self.health + amount, self.max_health)` adds the health, but never goes past the maximum. Return how much health was actually gained, so the game can say "you get back 1 health" when you were only 1 short.

#### Step 7: Using things (`Game.use`)

Potions have `heal` above 0. Anything else might open a door, so ask the room with `self.current_room().unlock(name)`.

Have a look at `Room.unlock()`, which is already written. It finds the exit first, and deletes it from the dictionary only after the loop has finished. Deleting from a dictionary *while* looping over it makes Python stop with `RuntimeError: dictionary changed size during iteration`.

**Check it:** pick up the potion in the storeroom and try `use potion` at full health. It should refuse, and you should keep the potion.

### Part 3: The player's health

#### Step 8: The status bar (`Player.__str__`)

`__str__` is a special method. Python calls it whenever something needs your object as text, for example `print(player)` or `f"{player}"`. Without it, you'd see something unhelpful like `<__main__.Player object at 0x10a3b2f40>`.

```python
hearts = "♥" * self.health + "♡" * (self.max_health - self.health)
```

Multiplying a string repeats it, so 2 health out of 3 gives `♥♥♡`.

**Check it:** run the game. The status bar should appear above every `>` prompt.

#### Step 9: Taking damage (`Player.take_damage`)

`max(self.health - amount, 0)` takes the damage, but never goes below zero. Then, if health is 0:

```python
raise GameOver("Everything goes dark as you fall to the floor...")
```

Here's the clever part. You don't catch `GameOver` anywhere near here. It's raised deep inside a fight, inside `enter_room()`, inside `go()`, inside `handle()`, inside `play()`. It travels up through every one of those calls until it reaches the `try` in `main()`, which prints the message and ends the game cleanly. Without that exception, every one of those functions would need to check "is the player dead?" and pass the answer back up.

This is also **encapsulation**: the rules about health (never below 0, never above the maximum, game over at 0) live inside `Player`, next to the health itself. During play, the rest of the game just calls `take_damage()` and `heal()`, and never changes `player.health` directly. (Loading a save is the one exception. It puts back a saved number, after checking that the number makes sense.)

### Part 4: Enemies

#### Step 10: A plain attack (`Enemy.attack`)

```python
if random.random() < ENEMY_HIT_CHANCE:
```

`random.random()` gives a random number between 0 and 1. It's below 0.5 half the time, so that's a 50% chance to hit.

The player is handed in as an argument (`attack(self, player)`), so the enemy can call `player.take_damage()`. The enemy uses the player for a moment, but doesn't keep hold of it.

#### Step 11: The goblin's sneaky attack (`Goblin.attack`)

Look at the first line: `class Goblin(Enemy):`. A Goblin is an Enemy, so it gets everything Enemy has (health, `is_alive()`, `take_damage()`) without writing any of it again. That's **inheritance**.

When you write `attack()` inside `Goblin`, it replaces Enemy's `attack()`, for goblins only. That's called **overriding**. And inside it, `super().attack(player)` means "now do it the normal Enemy way". So a goblin can add its sand trick and still reuse the ordinary attack:

```python
if random.random() < 1 / 3:
    print("The goblin throws sand in your face! ...")
else:
    super().attack(player)
```

#### Step 12: The dragon's fire (`Dragon.attack`)

`Dragon.__init__` is already written, and it sets up `self.turns = 0`. Each dragon remembers its own count. If there were two dragons, each would keep its own. Add 1 every attack, and when `self.turns % 3 == 0`, breathe fire instead.

Here's what's nice about this. The fight code just calls `enemy.attack(self.player)`. It never asks "is this a goblin or a dragon?", because each kind of enemy knows how to attack in its own way.

### Part 5: Fighting

#### Step 13: The fight (`Game.fight`)

This is the biggest step. The TODO lists every part. Two things to watch:

- **`continue` doesn't cost a turn.** If the player makes a typo, or tries to drink a potion they don't have, `continue` goes straight back to the top of the loop, and the enemy doesn't get a free hit.
- **The enemy only attacks if it's still alive.** If your hit just finished it off, it doesn't get a last swing.

After the loop, set `room.enemy = None`, so the enemy stays beaten.

> **About the seed.** `main()` calls `random.seed(SEED)` once at the start. After that, the "random" numbers come out in the same order every time. So if you type exactly the same commands, you get exactly the same fights. This is great for finding bugs: when something strange happens, you can make it happen again. Change `SEED` to get different fights, or set it to `None` for a different game every time.
>
> One honest note: it's the *whole game* that replays, not one fight on its own. If you take a different route to the dragon, the numbers will be used up in a different order, and the fight will go differently.

### Part 6: Saving and loading

#### Step 14: Saving (`Game.save`)

Save everything that can change: where you are, your health and what you carry. Save the **rooms** too. Otherwise, loading would put back the sword you've already picked up, and bring the goblin back to life.

Save item **names**, not the `Item` objects themselves. `json` only understands simple things: text, numbers, `True`/`False`/`None`, lists and dictionaries. Give it an `Item` and you get:

```
TypeError: Object of type Item is not JSON serializable
```

So save `"sword"`, and turn it back into an `Item` when you load.

**Check it:** type `save`, then open `savegame.json` in your editor. It's just text, and you should be able to read it.

#### Step 15: Loading (`Game.load`)

The safe way to load is to **build first, swap last**:

1. Build a brand new world from the map with `self.build_world()`.
2. Change that new world to match the save.
3. Only if all of that worked, swap it in with `self.rooms = rooms` and `self.player = player`.

Why bother? Imagine someone has edited the save file, and it mentions an item called `"laser"` that doesn't exist. Halfway through loading, you'd get a `KeyError`. If you'd been changing the real game as you went, it would now be half old and half new: a broken mess. With build-first-swap-last, the error happens to the new world, which you simply throw away. The game you were playing isn't touched.

There's a second thing to watch for. A save file is just text, and anyone can edit it. If someone changes `"health": 2` to `"health": "abc"`, a load with no checks would work fine: `"abc"` is copied in like any other value. The crash only comes later, the first time the status bar tries to draw `"♥" * "abc"`. By then, the load is long over, and the error is very confusing.

So **check each value as you load it**:

- `int(data["health"])` turns the health into a number, or raises `ValueError` for something like `"abc"`. Then check it's between 1 and the maximum.
- Check that the room ids are real rooms.
- `dict(saved["locked"])` makes a fresh copy, and fails if the value isn't shaped like a dictionary.

You can catch several kinds of error with one `except`:

```python
except (KeyError, TypeError, ValueError, AttributeError):
```

**Check it:** save, pick something up, then load. The item should be back in the room.

### Part 7: Checking the map and spooky events

#### Step 16: Can you get out? (`can_reach`)

Before the game starts, `check_map()` makes sure the dungeon can actually be escaped. If someone edits `dungeon.json` and accidentally cuts off the gate, it's much better to find out straight away than after an hour of playing.

`can_reach()` answers the question with **recursion**: a function that calls itself. The idea is:

> "Can I get from here to the goal?
> Yes, if I'm already there.
> Otherwise, yes if I can get to the goal from any of my exits."

That last line asks the very same question again, just from a different room. So the function calls itself:

```python
for next_room in rooms[current].exits.values():
    if next_room not in visited:
        if can_reach(rooms, next_room, goal, visited):
            return True
```

**Why `visited`?** The cell's exit leads to the corridor, and the corridor's exits lead back to the cell. Without remembering where you've been, the function would go cell → corridor → cell → corridor... forever, until Python gives up with a `RecursionError`. The `visited` set stops it going round in circles.

**Why `visited=None`, and not `visited=set()`?** This trips up almost everyone once. A default value is made **once**, when Python first reads the `def` line, not each time the function is called. With `visited=set()`, every call would share the same set, and the second time you checked a map, every room would already be "visited". So the default is `None`, and you make a fresh set inside the function. (`Room.__init__` does the same with `locked=None`, for the same reason.)

This way of searching is called **depth-first search**. It follows one path as deep as it can go before coming back to try another.

**Check it:** in `dungeon.json`, change the gate's `"north": "outside"` to `"north": "hall"`, and start the game. It should refuse with "there's no way to get from 'cell' to 'outside'". Then change it back.

**What it can't catch.** `can_reach()` treats locked exits as if they were open. So if you hid the key *behind* the gate it opens, the check would still pass, and nobody could ever win. Catching that needs a cleverer search, one that keeps track of the keys you've picked up along the way.

#### Step 17: Spooky events (`random_events`)

A **generator** is a function that uses `yield` instead of `return`. Each time you call `next()` on it, it runs until it reaches a `yield`, hands over that value, and then *pauses* right there. The next `next()` carries on from where it paused.

```python
events = random_events(4)
next(events)    # None
next(events)    # None
next(events)    # None
next(events)    # one of the spooky messages, picked at random
```

That's why `while True:` is fine here, even though it never ends. The generator only does one step each time the game asks for one. The game loop in `play()` (already written) asks once per command.

---

## The big idea: what belongs in which class

When you start writing classes, the hard part isn't the syntax. It's deciding **where each piece of code should live**.

Here's a version that seems perfectly reasonable at first:

```python
class Room:
    def __init__(self, ...):
        self.player = None        # the player, when they're in this room

class Player:
    def __init__(self, ...):
        self.room = None          # the Room object the player is in
```

Now the room points to the player, and the player points to the room. Every time the player moves, both have to be updated, and if you forget one, they disagree about where the player is. Saving gets harder too, because you'd have to untangle all the objects pointing at each other before writing anything.

This game follows three simple rules instead:

1. **Each class looks after its own data.** `Player` owns your health, so the rules about health live in `Player`. `Room` owns its items, so `take_item()` lives in `Room`.
2. **Rooms are just places.** A `Room` never knows about the player. The player stores the room's *id*, a plain string like `"armory"`, rather than the `Room` object itself. Strings are easy to save, and there's nothing to keep in step.
3. **One class is in charge of the others.** `Game` knows about everything, and it's the only one that passes things between objects: taking an item out of a room and giving it to the player, or bringing a player and an enemy together for a fight.

When the enemy attacks, it's *handed* the player for that one moment (`attack(self, player)`) instead of keeping a permanent link to it. That's the difference between "Room knows about the Player" and "an enemy is given the player when it needs it".

A good test when you're not sure where something goes: **which class owns the data it changes?** Put the code there.

---

## Try to break it

Each of these should give a sensible message, not a crash:

- [ ] Press Enter on an empty line. Type `dance`. Type `go` with no direction, and `go up`
- [ ] `take dragon`, `use nothing`, `use torch`
- [ ] Drink a potion at full health. It shouldn't be wasted
- [ ] In a fight, type `atack` with a typo. The enemy shouldn't get a free hit
- [ ] Run away from the goblin, then come back. It should still be as hurt as you left it
- [ ] Save, pick something up, then load. The item should be back where it was
- [ ] Type `load` before you've ever saved
- [ ] Open `savegame.json`, type some rubbish into it, and load
- [ ] In `savegame.json`, change `"sword"` to `"laser"`, and load. The game you're playing shouldn't change at all
- [ ] In `savegame.json`, change the health to `"abc"`, then to `99`, and load each time. Both should be refused
- [ ] In `dungeon.json`, point an exit at a room that doesn't exist, like `"east": "nowhere"`
- [ ] In `dungeon.json`, change one exit to `"North"`, with a capital N
- [ ] Walk to the dragon without the sword. You'll probably lose, and the game should end cleanly
- [ ] Play twice with the same commands and the same `SEED`. Both games should go exactly the same way

---

## Build your own dungeon

Everything about the dungeon lives in `dungeon.json`, so you can make a new one without touching the code. Each room looks like this:

```json
"armory": {
  "name": "Old armory",
  "description": "Racks of broken spears and dented shields line the walls.",
  "exits": {"west": "corridor"},
  "items": ["sword"],
  "enemy": "goblin",
  "locked": {"north": "key"}
}
```

Only `name` and `description` are required. `"locked": {"north": "key"}` means the north exit needs the key. Items are listed once, at the top of the file, under `"items"`. Give an item `"heal"` to make it a potion, or `"damage"` to make it a weapon.

Write directions and item names in **lowercase**. The game lowercases everything the player types, so an exit called `"North"` could never be used.

If you make a mistake, the game tells you what's wrong before it starts. That includes an exit to a room that doesn't exist, an item that isn't defined, a missing `"title"`, `"intro"` or `"win_text"`, a name with capital letters, or no way at all to reach the escape. The one thing it can't spot is a key locked away behind its own door (see Step 16).

---

## Stretch goals

Finished? Pick one. There's no solution for these.

### 1. Shortcuts

Typing `go north` gets tiring. Let the player type `n`, `s`, `e` and `w` to move, and `i` for inventory.

- `"i": self.show_inventory` is one extra line in the command table.
- The directions are trickier, because `n` should run `self.go("north")` and ignore whatever noun it was given. A tiny `lambda` does it: `"n": lambda noun: self.go("north")`. That's chapter 7's lambda, doing a real job.
- `show_help()` lists every word in the table, so your shortcuts will appear there automatically. Run `help` and check it still reads well.

### 2. A dark room, and a reason to keep your torch

Add `"dark": true` to the storeroom in `dungeon.json`. In a dark room without a torch, you can't see any items. Then add a `drop` command, so the torch can actually be lost.

- Give `Room` a `dark` attribute, read from the map.
- Change `describe()` to `describe(self, can_see)`, and have `Game` pass in `self.player.has_item("torch")`. The room still doesn't know about the player: it's just told whether there's light.
- `drop` is like `take` in reverse: remove the item from the player, and append it to the room's items.
- Check that saving and loading still work with dropped items.

### 3. Enemies drop loot

When you beat an enemy, it drops something, like gold or a second key.

- Add a `"loot": ["gold"]` list to a room in `dungeon.json`. Add `"gold"` to the items at the top too.
- In `fight()`, after the enemy is beaten, add the loot to `room.items`.
- Think about saving: if you save after the fight, is the loot saved properly? (Try it. Step 14 might already handle it for free.)

---

## What you practised

| Chapter | Where it shows up |
|---|---|
| 5. Conditionals and loops | the game loop, the fight loop, `continue` for a free retry |
| 6. Functions | default arguments, and the `visited=None` trap |
| 7. Recursion | `can_reach()`, a depth-first search |
| 8. Object-oriented programming | five classes, `__init__`, `__str__`, inheritance, overriding with `super()`, keeping health rules inside `Player` |
| 9. Exceptions | your own `GameOver` and `MapError`, an exception that travels up to `main()`, catching several kinds at once |
| 10. Files and JSON | loading the map, saving and loading the game |
| 12. Generators | `random_events()`, with `yield` and `next()` |
| 13. First-class functions | the command table: a dictionary of word → method |
