"""
Dungeon Escape: your starter file.

Work through the TODOs in order, from TODO 1 to TODO 17. README.md has a
hint for every step if you get stuck.

Run it with:  python3 starter.py

A lot is already written for you: the settings, both exceptions, the Item
class, most of Room, Player and Enemy, and the parts of Game that load the
map and run the main loop. Read them. They show you how the rest should look.

Each unfinished function has a "placeholder", a line or two that keeps the
game running before you've written it. Replace the placeholder with your
own code. Until you do TODO 2, the only command that works is quit.
"""

import json
import random
from pathlib import Path


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# Path(__file__).parent is the folder this file is in, so the game finds
# its files wherever you run it from.
HERE = Path(__file__).parent
MAP_FILE = HERE / "dungeon.json"
SAVE_FILE = HERE / "savegame.json"

# The same seed gives the same "random" numbers every time. So if you type
# the same commands, you get exactly the same fights. Set it to None for
# different fights every game.
SEED = 7

PLAYER_DAMAGE = 1         # how hard you hit with your bare hands
PLAYER_HIT_CHANCE = 0.75  # 0.75 means you hit 3 times out of 4
ENEMY_HIT_CHANCE = 0.5
EVENT_EVERY = 4           # something spooky happens every 4 turns


# ---------------------------------------------------------------------------
# Our own exceptions
# ---------------------------------------------------------------------------

class GameOver(Exception):
    """Raised when the player's health reaches zero."""


class MapError(Exception):
    """Raised when dungeon.json describes a dungeon that can't work."""


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

class Item:
    """Something you can carry: a torch, a sword, a potion, a key."""

    def __init__(self, name, description, heal=0, damage=0):
        self.name = name
        self.description = description
        self.heal = heal        # health it gives back when you use it
        self.damage = damage    # extra damage it adds in a fight

    def __str__(self):
        return f"{self.name}: {self.description}"


# ---------------------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------------------

class Room:
    """One place in the dungeon.

    A room knows its exits, its items and its enemy. It does NOT know about
    the player. That keeps it simple: a room is just a place.
    """

    def __init__(self, name, description, exits, items, enemy=None, locked=None):
        self.name = name
        self.description = description
        self.exits = exits      # e.g. {"north": "corridor"}
        self.items = items      # a list of Item objects
        self.enemy = enemy      # an Enemy object, or None

        # Why not locked={} in the line above? Because that one dictionary
        # would be created once and shared by EVERY room. Unlock a door in
        # one room and it would unlock in all of them. None, then a fresh
        # {} here, gives each room its own.
        if locked is None:
            locked = {}
        self.locked = locked    # e.g. {"north": "key"}

    def describe(self):
        """Return a few lines describing the room, ready to print."""
        lines = [f"== {self.name} ==", self.description]

        if len(self.items) > 0:
            names = [item.name for item in self.items]
            lines.append("You can see: " + ", ".join(names))

        exits = []
        for direction in self.exits:
            if direction in self.locked:
                exits.append(f"{direction} (locked)")
            else:
                exits.append(direction)
        if len(exits) > 0:
            lines.append("Exits: " + ", ".join(exits))

        return "\n".join(lines)

    def take_item(self, name):
        """Remove an item from the room and return it, or None if it isn't here."""
        # TODO 4
        # - Loop over self.items. If an item's .name matches `name`, remove it from
        #   self.items and return it.
        # - If the loop finishes without finding it, return None.
        return None   # placeholder: replace this line

    def unlock(self, item_name):
        """Unlock the exit this item opens. Returns the direction, or None."""
        opened = None
        for direction in self.locked:
            if self.locked[direction] == item_name:
                opened = direction

        # We delete after the loop, not inside it: changing a dictionary
        # while you're looping over it makes Python stop with an error.
        if opened is not None:
            del self.locked[opened]
        return opened


# ---------------------------------------------------------------------------
# The player
# ---------------------------------------------------------------------------

class Player:
    """You! Your health, what you're carrying, and where you are."""

    def __init__(self, room_id, health, inventory):
        self.room_id = room_id
        self.previous_room = None   # where you came from, so you can run back
        self.health = health
        self.max_health = health
        self.inventory = inventory  # a list of Item objects

    def __str__(self):
        """The status bar, e.g.  Health ♥♥♡   Carrying: torch, sword"""
        # TODO 8
        # - Make the hearts:  "♥" * self.health + "♡" * (self.max_health - self.health)
        # - Make a list of the names of the items you're carrying, and join them
        #   with ", ". If you aren't carrying anything, use "nothing".
        # - Return one line, like:  Health ♥♥♡   Carrying: torch, sword
        return "(The status bar is TODO 8.)"   # placeholder: replace this line

    def take_damage(self, amount):
        """Lose health. At zero, the game is over."""
        # TODO 9
        # - Take `amount` off self.health, but never go below 0. max() helps here.
        # - If your health is now 0, raise GameOver with a dramatic message.
        #   You don't need to catch it here. main() catches it, right at the top.
        pass   # placeholder: replace this line

    def heal(self, amount):
        """Gain health, but never more than the maximum. Returns how much you gained."""
        # TODO 6
        # - Remember your health before healing.
        # - Add `amount`, but never go above self.max_health. min() helps here.
        # - Return how much health you actually gained (after minus before).
        return 0   # placeholder: replace this line

    def get_item(self, name):
        """Return the item with this name if you're carrying it, or None."""
        for item in self.inventory:
            if item.name == name:
                return item
        return None

    def has_item(self, name):
        return self.get_item(name) is not None

    def remove_item(self, name):
        item = self.get_item(name)
        if item is not None:
            self.inventory.remove(item)

    def attack_damage(self):
        """Your damage: bare hands, plus your best weapon."""
        best = 0
        for item in self.inventory:
            if item.damage > best:
                best = item.damage
        return PLAYER_DAMAGE + best


# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------

class Enemy:
    """The base class for every enemy. Goblin and Dragon build on it."""

    def __init__(self, name, health, damage):
        self.name = name
        self.health = health
        self.damage = damage

    def __str__(self):
        return f"{self.name} (health {self.health})"

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health = max(self.health - amount, 0)

    def attack(self, player):
        """A plain attack: hits half the time, for this enemy's damage."""
        # TODO 10
        # - random.random() gives a random number between 0 and 1. If it's less than
        #   ENEMY_HIT_CHANCE, the attack hits:
        #     - print that the enemy hits you, and for how much (self.damage)
        #     - call player.take_damage(self.damage)
        # - Otherwise, print that it misses.
        print(f"The {self.name} glares at you. (Attacking is TODO 10.)")   # placeholder


class Goblin(Enemy):
    """Small, sneaky and not very strong."""

    def __init__(self):
        super().__init__("goblin", health=3, damage=1)

    def attack(self, player):
        """Goblins fight dirty. One time in three, they throw sand instead."""
        # TODO 11
        # - This replaces (overrides) Enemy.attack, just for goblins.
        # - One time in three (random.random() < 1 / 3), the goblin throws sand
        #   instead: print a message, and do no damage.
        # - Otherwise, attack the normal way:  super().attack(player)
        #   super() means "the class I'm built on", which is Enemy.
        super().attack(player)   # placeholder: attacks the plain Enemy way for now


class Dragon(Enemy):
    """Big, slow and very dangerous."""

    def __init__(self):
        super().__init__("dragon", health=6, damage=1)
        self.turns = 0

    def attack(self, player):
        """Every third turn, the dragon breathes fire instead of clawing."""
        # TODO 12
        # - Add 1 to self.turns every time the dragon attacks.
        # - Every third turn (self.turns % 3 == 0), it breathes fire: print a
        #   message and call player.take_damage(2). Fire never misses.
        # - On the other turns, attack the normal way with super().attack(player).
        super().attack(player)   # placeholder: attacks the plain Enemy way for now


# The map file says "goblin" or "dragon". This dictionary turns that word
# into the class to build. Adding a new enemy means adding a line here.
ENEMY_TYPES = {"goblin": Goblin, "dragon": Dragon}


# ---------------------------------------------------------------------------
# Checking the map
# ---------------------------------------------------------------------------

def can_reach(rooms, current, goal, visited=None):
    """Can you get from `current` to `goal` by following exits?

    This is a depth-first search: try one exit, follow it as far as it
    goes, and only come back to try the next exit if that one didn't work.
    """
    # TODO 16  (recursion: a function that calls itself)
    # - If visited is None, make it a new empty set. (README: why not visited=set()?)
    # - If current == goal, you've found it: return True.
    # - Add current to visited.
    # - For each next_room in rooms[current].exits.values():
    #     - If you haven't visited it yet, and can_reach(rooms, next_room, goal,
    #       visited) is True, return True.
    # - If no exit led to the goal, return False.
    return True   # placeholder: replace this line


def check_map(rooms, start, escape):
    """Make sure the dungeon can actually be played, before it starts.

    One thing it can't catch: can_reach() treats locked exits as open, so a
    key hidden behind its own locked door would still pass.
    """
    for room_id in rooms:
        for direction, target in rooms[room_id].exits.items():
            if direction != direction.lower():
                raise MapError(f"the exit '{direction}' in '{room_id}' should be written in lowercase.")
            if target not in rooms:
                raise MapError(f"'{room_id}' has an exit {direction} to '{target}', but there's no room called that.")
    if start not in rooms:
        raise MapError(f"the start room '{start}' doesn't exist.")
    if escape not in rooms:
        raise MapError(f"the escape room '{escape}' doesn't exist.")
    if not can_reach(rooms, start, escape):
        raise MapError(f"there's no way to get from '{start}' to '{escape}'.")


# ---------------------------------------------------------------------------
# Random events
# ---------------------------------------------------------------------------

def random_events(every):
    """An endless generator. Each time you ask it for the next value, it
    gives you a spooky message every few turns, and None the rest of the time."""
    # TODO 17  (a generator: it uses yield instead of return)
    # - Make a list of 3 or 4 spooky messages.
    # - Start a turn counter at 0, then loop forever with `while True:`
    #     - Add 1 to the counter.
    #     - If turn % every == 0, yield random.choice(messages)
    #     - Otherwise, yield None
    # - It's fine that the loop never ends. A generator only runs when someone
    #   asks for the next value with next(), and then it pauses at the yield.
    while True:      # placeholder: no events until you write TODO 17
        yield None


# ---------------------------------------------------------------------------
# The game
# ---------------------------------------------------------------------------

class Game:
    """Holds everything together: the rooms, the player and the commands.

    Room, Player and Enemy each look after themselves. Game is the one that
    knows about all of them, and makes them work together.
    """

    def __init__(self, map_path):
        with open(map_path, encoding="utf-8-sig") as file:
            self.map_data = json.load(file)

        # If the map leaves something out, Python raises KeyError. We turn
        # that into a MapError with a clearer message.
        try:
            self.title = self.map_data["title"]
            self.intro = self.map_data["intro"]
            self.win_text = self.map_data["win_text"]
            self.item_catalog = self.build_items()
            self.rooms, self.player = self.build_world()
            self.escape = self.map_data["escape"]
            check_map(self.rooms, self.map_data["start"], self.escape)
        except KeyError as error:
            raise MapError(f"{error} is missing, or is spelled differently in one place.")

        self.commands = self.build_commands()
        self.events = random_events(EVENT_EVERY)
        self.running = True

    def build_items(self):
        """Make one Item object for each item in the map."""
        catalog = {}
        for name, info in self.map_data["items"].items():
            # Everything the player types is made lowercase, so "Sword" in
            # the map could never be picked up.
            if name != name.lower():
                raise MapError(f"the item '{name}' should be written in lowercase.")
            catalog[name] = Item(name, info["description"], info.get("heal", 0), info.get("damage", 0))
        return catalog

    def build_world(self):
        """Build fresh rooms and a fresh player from the map.

        Used when the game starts, and again when you load a saved game.
        """
        rooms = {}
        for room_id, info in self.map_data["rooms"].items():
            # Every potion in the game is the very same Item object from the
            # catalog. That's fine, because items never change once made.
            items = [self.item_catalog[name] for name in info.get("items", [])]
            enemy = None
            if info.get("enemy") is not None:
                enemy = ENEMY_TYPES[info["enemy"]]()
            # dict(...) makes a copy, so unlocking a door changes this
            # room only, and not the map data we'll rebuild from on a load.
            locked = dict(info.get("locked", {}))
            rooms[room_id] = Room(info["name"], info["description"], info.get("exits", {}), items, enemy, locked)

        start = self.map_data["player"]
        inventory = [self.item_catalog[name] for name in start["items"]]
        player = Player(self.map_data["start"], start["health"], inventory)
        return rooms, player

    def build_commands(self):
        """The command table: each word the player can type, and the method it runs.

        Notice there are no () after the method names. We're storing the
        methods themselves, to call later, not calling them now.
        """
        # TODO 1
        # - Return a dictionary. Each key is a word the player can type, and each
        #   value is the method that word should run.
        # - The words are: go, take, use, inventory, look, save, load, help, quit
        # - The methods are: self.go, self.take, self.use, self.show_inventory,
        #   self.look, self.save, self.load, self.show_help, self.quit
        # - Careful: write self.go, NOT self.go(). With the brackets you'd run the
        #   method straight away and store whatever it returned.
        return {}   # placeholder: replace this line

    # ----- the main loop ---------------------------------------------------

    def play(self):
        print(self.title)
        print(self.intro)
        print("Type help to see what you can do.")
        print()
        self.look("")

        while self.running:
            print()
            print(self.player)
            self.handle(input("> "))

            event = next(self.events)
            if event is not None and self.running:
                print(event)

    def handle(self, command):
        """Split what the player typed into a verb and a noun, and run it.

        "go north" becomes the verb "go" and the noun "north".
        "look" becomes the verb "look" and an empty noun.
        """
        # TODO 2
        # - Clean up the command and split it into at most two words:
        #     words = command.strip().lower().split(maxsplit=1)
        # - If there are no words (the player just pressed Enter), return.
        # - The first word is the verb. The second, if there is one, is the noun.
        #   If there isn't one, use "" for the noun.
        # - If the verb isn't in self.commands, print a friendly message and return.
        # - Otherwise, look up the method and call it with the noun:
        #     self.commands[verb](noun)
        # placeholder: until you write this, the only command that works is quit
        if command.strip().lower() == "quit":
            self.quit("")

    # ----- moving around ---------------------------------------------------

    def current_room(self):
        return self.rooms[self.player.room_id]

    def enter_room(self, room_id):
        """Move the player into a room, and deal with whatever is there."""
        self.player.previous_room = self.player.room_id
        self.player.room_id = room_id
        room = self.current_room()
        print()
        print(room.describe())

        if room_id == self.escape:
            print()
            print(self.win_text)
            self.running = False
        elif room.enemy is not None:
            self.fight(room)

    def go(self, direction):
        """Move through an exit, like "go north"."""
        # TODO 3
        # - Get the room you're in with self.current_room().
        # - If `direction` is "", print a hint like "Go where?".
        # - If it isn't one of room.exits, say you can't go that way.
        # - If it's in room.locked, say it's locked.
        # - Otherwise, move with:  self.enter_room(room.exits[direction])
        print("You can't move yet. Moving is TODO 3.")   # placeholder: replace this line

    # ----- items -----------------------------------------------------------

    def take(self, name):
        """Pick up an item from the room, like "take sword"."""
        # TODO 5
        # - If `name` is "", print a hint like "Take what?" and return.
        # - Ask the room for the item:  item = self.current_room().take_item(name)
        # - If you got None, say it isn't here.
        # - Otherwise, append it to self.player.inventory and say you picked it up.
        print("You can't pick things up yet. That's TODO 5.")   # placeholder: replace this line

    def use(self, name):
        """Use something you're carrying, like "use potion" or "use key"."""
        # TODO 7
        # - If `name` is "", print a hint like "Use what?" and return.
        # - Get the item with self.player.get_item(name). If it's None, say you
        #   aren't carrying one and return.
        # - If item.heal is more than 0, it's a potion:
        #     - At full health, say so and DON'T use it up.
        #     - Otherwise, call self.player.heal(item.heal), remove the potion with
        #       self.player.remove_item(name), and say how much health came back.
        #     - Then return.
        # - Anything else might open a door:  direction = self.current_room().unlock(name)
        #   If direction isn't None, say which way is now open.
        #   If it is None, say nothing happens.
        print("You can't use things yet. That's TODO 7.")   # placeholder: replace this line

    def show_inventory(self, noun):
        if len(self.player.inventory) == 0:
            print("You aren't carrying anything.")
            return
        print("You are carrying:")
        for item in self.player.inventory:
            print(f"  {item}")

    def look(self, noun):
        print(self.current_room().describe())

    def show_help(self, noun):
        print("You can type: " + ", ".join(self.commands))
        print("For example: go north, take sword, use potion")

    def quit(self, noun):
        print("Thanks for playing!")
        self.running = False

    # ----- fighting --------------------------------------------------------

    def fight(self, room):
        """Fight the enemy in this room, one round at a time."""
        # TODO 13  (the biggest step, so take it slowly)
        # - enemy = room.enemy. Print that it attacks.
        # - Loop while enemy.is_alive():
        #     - Show both healths, then ask:
        #         choice = input("What do you do? (attack / use potion / run): ").strip().lower()
        #     - "attack": if random.random() < PLAYER_HIT_CHANCE, the enemy takes
        #       self.player.attack_damage() damage. Otherwise you miss.
        #     - "use potion": if you have no potion, or you're at full health, say so
        #       and `continue` (that doesn't cost a turn). Otherwise, self.use("potion").
        #     - "run": if self.player.previous_room is None, say there's nowhere to
        #       run and `continue`. Otherwise, self.enter_room(self.player.previous_room),
        #       then return.
        #     - Anything else: say what to type, and `continue`.
        #     - If the enemy is still alive, it's its turn:  enemy.attack(self.player)
        # - After the loop you've won: say so, set room.enemy = None, and print
        #   room.describe() so the player can see what's in the room.
        print(f"A {room.enemy.name} is here, but fighting is TODO 13. You walk straight past it.")   # placeholder

    # ----- saving and loading ----------------------------------------------

    def save(self, noun):
        """Write everything that can change to savegame.json."""
        # TODO 14
        # - Build a `rooms` dictionary. For each room id and room in self.rooms.items(),
        #   store a small dictionary with:
        #     "items":        a list of the item NAMES (not the Item objects)
        #     "locked":       room.locked
        #     "enemy_health": room.enemy.health, or None if room.enemy is None
        # - Put that in one big dictionary with "room", "previous_room", "health",
        #   "inventory" (item names again) and "rooms".
        # - Write it to SAVE_FILE with json.dump(data, file, indent=2), and say it's saved.
        # - Why names and not Item objects? json can only save simple things like
        #   text, numbers, lists and dictionaries. The README explains more.
        print("Saving is TODO 14.")   # placeholder: replace this line

    def load(self, noun):
        """Read savegame.json and carry on from there."""
        # TODO 15
        # - Open SAVE_FILE and json.load() it, inside a try:
        #     - except FileNotFoundError: say there's no save yet, and return
        #     - except json.JSONDecodeError: say the file is damaged, and return
        # - Build a fresh world:  rooms, player = self.build_world()
        # - Inside a second try:
        #     - First CHECK the values, because anyone can edit a save file. The two
        #       room ids must be in `rooms` (previous_room can also be None). Turn
        #       the health into a number with int(), and check it's between 1 and
        #       player.max_health. raise KeyError or ValueError if anything is wrong.
        #     - Then copy everything from the save onto that fresh `rooms` and
        #       `player`. Turn item names back into Items with self.item_catalog[name].
        #       Use dict(saved["locked"]) and int(saved["enemy_health"]), which also
        #       fail on values of the wrong kind. An enemy_health of None means set
        #       room.enemy to None.
        # - except (KeyError, TypeError, ValueError, AttributeError): the save doesn't
        #   fit this map. Say so and return, WITHOUT changing self.rooms or self.player.
        # - Only at the very end:  self.rooms = rooms  and  self.player = player
        #   Then say it's loaded and call self.look("").
        print("Loading is TODO 15.")   # placeholder: replace this line


# ---------------------------------------------------------------------------
# The main program
# ---------------------------------------------------------------------------

def main():
    random.seed(SEED)

    try:
        game = Game(MAP_FILE)
    except FileNotFoundError:
        print("I can't find dungeon.json. Make sure it's in the same folder as this file.")
        return
    except json.JSONDecodeError as error:
        print(f"dungeon.json has a mistake in it: {error}")
        return
    except MapError as error:
        print(f"dungeon.json doesn't work: {error}")
        return

    # GameOver can be raised deep inside a fight. It travels up through
    # every function call until it reaches this try, and then we stop.
    try:
        game.play()
    except GameOver as error:
        print()
        print(error)
        print("*** GAME OVER ***")
        print("Run the game again and type load to carry on from your last save.")


# Want to try one function on its own? Put a # in front of main() below,
# and add a line like this instead:   print(Player("cell", 3, []))
main()
