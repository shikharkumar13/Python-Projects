"""
Dungeon Escape: a text adventure with real objects.

This is the finished version. Try starter.py first, and come here when
you're done or properly stuck.

Run it with:  python3 solution.py
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
        for item in self.items:
            if item.name == name:
                self.items.remove(item)
                return item
        return None

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
        hearts = "♥" * self.health + "♡" * (self.max_health - self.health)
        if len(self.inventory) == 0:
            carrying = "nothing"
        else:
            carrying = ", ".join([item.name for item in self.inventory])
        return f"Health {hearts}   Carrying: {carrying}"

    def take_damage(self, amount):
        """Lose health. At zero, the game is over."""
        # Health never goes below 0, however hard you're hit.
        self.health = max(self.health - amount, 0)
        if self.health == 0:
            raise GameOver("Everything goes dark as you fall to the floor...")

    def heal(self, amount):
        """Gain health, but never more than the maximum. Returns how much you gained."""
        before = self.health
        self.health = min(self.health + amount, self.max_health)
        return self.health - before

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
        if random.random() < ENEMY_HIT_CHANCE:
            print(f"The {self.name} hits you for {self.damage}!")
            player.take_damage(self.damage)
        else:
            print(f"The {self.name} misses.")


class Goblin(Enemy):
    """Small, sneaky and not very strong."""

    def __init__(self):
        super().__init__("goblin", health=3, damage=1)

    def attack(self, player):
        """Goblins fight dirty. One time in three, they throw sand instead."""
        if random.random() < 1 / 3:
            print("The goblin throws sand in your face! It stings, but doesn't hurt.")
        else:
            # Otherwise, attack the normal way, using the Enemy version.
            super().attack(player)


class Dragon(Enemy):
    """Big, slow and very dangerous."""

    def __init__(self):
        super().__init__("dragon", health=6, damage=1)
        self.turns = 0

    def attack(self, player):
        """Every third turn, the dragon breathes fire instead of clawing."""
        # Fire never misses, so there's no random number here.
        self.turns = self.turns + 1
        if self.turns % 3 == 0:
            print("The dragon breathes fire! You lose 2 health.")
            player.take_damage(2)
        else:
            super().attack(player)


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
    # A fresh set on the first call. (visited=set() in the def line would be
    # shared between calls, just like the locked={} problem in Room.)
    if visited is None:
        visited = set()

    if current == goal:
        return True
    visited.add(current)

    for next_room in rooms[current].exits.values():
        if next_room not in visited:
            if can_reach(rooms, next_room, goal, visited):
                return True
    return False


def check_map(rooms, start, escape):
    """Make sure the dungeon can actually be played, before it starts."""
    for room_id in rooms:
        for direction, target in rooms[room_id].exits.items():
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
    messages = [
        "You hear footsteps somewhere above you...",
        "A cold draught makes your torch flicker.",
        "Something small scuttles past your feet.",
        "Far away, something very large lets out a snore.",
    ]
    turn = 0
    while True:
        turn = turn + 1
        if turn % every == 0:
            yield random.choice(messages)
        else:
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
            self.item_catalog = self.build_items()
            self.rooms, self.player = self.build_world()
            self.escape = self.map_data["escape"]
            check_map(self.rooms, self.map_data["start"], self.escape)
        except KeyError as error:
            raise MapError(f"it mentions {error}, but that isn't defined anywhere.")

        self.commands = self.build_commands()
        self.events = random_events(EVENT_EVERY)
        self.running = True

    def build_items(self):
        """Make one Item object for each item in the map."""
        catalog = {}
        for name, info in self.map_data["items"].items():
            catalog[name] = Item(name, info["description"], info.get("heal", 0), info.get("damage", 0))
        return catalog

    def build_world(self):
        """Build fresh rooms and a fresh player from the map.

        Used when the game starts, and again when you load a saved game.
        """
        rooms = {}
        for room_id, info in self.map_data["rooms"].items():
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
        return {
            "go": self.go,
            "take": self.take,
            "use": self.use,
            "inventory": self.show_inventory,
            "look": self.look,
            "save": self.save,
            "load": self.load,
            "help": self.show_help,
            "quit": self.quit,
        }

    # ----- the main loop ---------------------------------------------------

    def play(self):
        print(self.map_data["title"])
        print(self.map_data["intro"])
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
        words = command.strip().lower().split(maxsplit=1)
        if len(words) == 0:
            return

        verb = words[0]
        if len(words) > 1:
            noun = words[1]
        else:
            noun = ""

        if verb not in self.commands:
            print(f"I don't know how to '{verb}'. Type help to see what you can do.")
            return

        # Look up the method in the table, and call it with the noun.
        self.commands[verb](noun)

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
            print(self.map_data["win_text"])
            self.running = False
        elif room.enemy is not None:
            self.fight(room)

    def go(self, direction):
        """Move through an exit, like "go north"."""
        room = self.current_room()
        if direction == "":
            print("Go where? Try something like: go north")
        elif direction not in room.exits:
            print(f"You can't go {direction} from here.")
        elif direction in room.locked:
            print(f"The way {direction} is locked.")
        else:
            self.enter_room(room.exits[direction])

    # ----- items -----------------------------------------------------------

    def take(self, name):
        """Pick up an item from the room, like "take sword"."""
        if name == "":
            print("Take what? Try something like: take sword")
            return
        item = self.current_room().take_item(name)
        if item is None:
            print(f"There's no {name} here.")
        else:
            self.player.inventory.append(item)
            print(f"You pick up the {item.name}.")

    def use(self, name):
        """Use something you're carrying, like "use potion" or "use key"."""
        if name == "":
            print("Use what? Try something like: use potion")
            return
        item = self.player.get_item(name)
        if item is None:
            print(f"You aren't carrying a {name}.")
            return

        if item.heal > 0:
            if self.player.health == self.player.max_health:
                print("You're already at full health. Better save it for later.")
            else:
                gained = self.player.heal(item.heal)
                self.player.remove_item(name)
                print(f"You drink the {name} and get back {gained} health.")
            return

        # Not a potion. Does it open anything in this room?
        direction = self.current_room().unlock(name)
        if direction is not None:
            print(f"You use the {name}. The way {direction} is open!")
        else:
            print(f"You wave the {name} around. Nothing happens.")

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
        enemy = room.enemy
        print()
        print(f"A {enemy.name} attacks!")

        while enemy.is_alive():
            print()
            print(f"Your health: {self.player.health}   {enemy}")
            choice = input("What do you do? (attack / use potion / run): ").strip().lower()

            if choice == "attack":
                if random.random() < PLAYER_HIT_CHANCE:
                    damage = self.player.attack_damage()
                    enemy.take_damage(damage)
                    print(f"You hit the {enemy.name} for {damage}!")
                else:
                    print("You swing and miss!")
            elif choice == "use potion":
                if not self.player.has_item("potion"):
                    print("You don't have a potion!")
                    continue
                if self.player.health == self.player.max_health:
                    print("You're already at full health.")
                    continue
                self.use("potion")
            elif choice == "run":
                if self.player.previous_room is None:
                    print("There's nowhere to run!")
                    continue
                print("You run back the way you came!")
                self.enter_room(self.player.previous_room)
                return
            else:
                print("Type attack, use potion or run.")
                continue    # a typo doesn't cost you a turn

            # The enemy's turn. If this takes your last health point, it
            # raises GameOver, which jumps all the way out to main().
            if enemy.is_alive():
                enemy.attack(self.player)

        print(f"You beat the {enemy.name}!")
        room.enemy = None
        print()
        print(room.describe())

    # ----- saving and loading ----------------------------------------------

    def save(self, noun):
        """Write everything that can change to savegame.json."""
        rooms = {}
        for room_id, room in self.rooms.items():
            enemy_health = None
            if room.enemy is not None:
                enemy_health = room.enemy.health
            rooms[room_id] = {
                "items": [item.name for item in room.items],
                "locked": room.locked,
                "enemy_health": enemy_health,
            }

        data = {
            "room": self.player.room_id,
            "previous_room": self.player.previous_room,
            "health": self.player.health,
            "inventory": [item.name for item in self.player.inventory],
            "rooms": rooms,
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        print("Game saved.")

    def load(self, noun):
        """Read savegame.json and carry on from there."""
        try:
            with open(SAVE_FILE, encoding="utf-8-sig") as file:
                data = json.load(file)
        except FileNotFoundError:
            print("There's no saved game yet. Type save to make one.")
            return
        except json.JSONDecodeError:
            print("The save file is damaged, so I can't load it.")
            return

        # Build a brand new world from the map, then change it to match the
        # save. We only swap it in at the very end. If anything goes wrong
        # halfway, the game you're playing now isn't touched.
        rooms, player = self.build_world()
        try:
            if data["room"] not in rooms:
                raise KeyError(data["room"])
            player.room_id = data["room"]
            player.previous_room = data["previous_room"]
            player.health = data["health"]
            player.inventory = [self.item_catalog[name] for name in data["inventory"]]

            for room_id, saved in data["rooms"].items():
                room = rooms[room_id]
                room.items = [self.item_catalog[name] for name in saved["items"]]
                room.locked = saved["locked"]
                if saved["enemy_health"] is None:
                    room.enemy = None
                else:
                    room.enemy.health = saved["enemy_health"]
        except (KeyError, TypeError, AttributeError):
            # KeyError: a room or item the map doesn't have.
            # TypeError or AttributeError: the file has the wrong shape,
            # like an enemy's health saved for a room with no enemy.
            print("That save file doesn't match this dungeon, so I can't load it.")
            return

        self.rooms = rooms
        self.player = player
        print("Game loaded.")
        print()
        self.look("")


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


main()
