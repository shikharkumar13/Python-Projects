"""Counting everything the awards need, in a single pass through the chat."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import chain, pairwise

from wrapped.parser import Message

MEDIA = "<Media omitted>"
DELETED = {"This message was deleted", "You deleted this message"}
NIGHT_HOURS = range(1, 5)               # 1:00 to 4:59 in the morning
REPLY_WINDOW = timedelta(hours=1)       # answering after longer than this isn't a "reply"
MIN_REPLIES = 3                         # one lucky quick reply doesn't win an award

# Words too common to be interesting. A frozenset is a set that can't be
# changed, which is just right for a fixed list like this.
STOP_WORDS = frozenset("""
    a an and are as at be but by can do for from get got have he her him his how
    i if in is it its it's just me my no not now of oh on or our she so that the
    them then there they this to too up us was we what when where who will with
    you your yes im i'm don't dont ur
    hai ka ki ke ko se toh na ho bhi ye wo kya nahi hain tha
""".split())

URL = re.compile(r"https?://\S+")
WORD = re.compile(r"[a-z]+(?:'[a-z]+)?")      # letters, and words like "don't"

# Emoji live in a few big blocks of Unicode. Some are followed by a skin
# tone (👍🏽) or by \ufe0f, an invisible "draw me as an emoji" mark (❤️).
# Both are kept with the emoji in front of them.
EMOJI = re.compile(
    r"""
    [\U0001F1E6-\U0001F1FF]{2}                         # a flag, like India's, is two "letter" symbols
    |                                                  # or
    [\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]   # an emoji (from \u2B00 there's the star)
    (?:[\U0001F3FB-\U0001F3FF]|\uFE0F)?                 # with an optional skin tone or emoji mark
    """,
    re.VERBOSE,
)


@dataclass
class Silence:
    """A gap in the chat: how long it was, and who finally broke it."""

    length: timedelta
    start: datetime
    end: datetime
    broken_by: str


@dataclass
class ChatStats:
    """Everything we count. Each field grows with the number of PEOPLE or
    WORDS in the chat, never with the number of messages."""

    total: int = 0
    first: datetime | None = None
    last: datetime | None = None
    messages: Counter[str] = field(default_factory=Counter)
    words: defaultdict[str, Counter[str]] = field(default_factory=lambda: defaultdict(Counter))
    emojis: Counter[str] = field(default_factory=Counter)
    night: Counter[str] = field(default_factory=Counter)
    hours: Counter[int] = field(default_factory=Counter)
    weekdays: Counter[int] = field(default_factory=Counter)
    reply_time: defaultdict[str, timedelta] = field(default_factory=lambda: defaultdict(timedelta))
    replies: Counter[str] = field(default_factory=Counter)
    longest_silence: Silence | None = None

    def add(self, message: Message) -> None:
        """Count one message."""
        # TODO 9
        # - Add 1 to self.total. Set self.first if it's still None, and always set self.last.
        # - Add 1 to the Counters: self.messages for the sender, self.hours for the
        #   hour, self.weekdays for message.when.weekday().
        # - If the hour is in NIGHT_HOURS, add 1 to self.night for the sender.
        # - self.emojis.update(...) with emojis_in() of the text. update() adds a whole list at once.
        # - Unless the text is MEDIA or one of DELETED, update self.words[sender]
        #   with words_in() of the text.
        pass   # placeholder: replace this line

    def add_gap(self, previous: Message, message: Message) -> None:
        """Look at the time between two messages next to each other."""
        # TODO 10
        # - gap = message.when - previous.when  (taking one datetime from another gives a timedelta)
        # - If there's no longest silence yet, or this gap is longer, store a new
        #   Silence(gap, previous.when, message.when, message.sender).
        # - If the sender is different from the previous one, and the gap is at most
        #   REPLY_WINDOW, it's a reply: add the gap to self.reply_time[sender], and
        #   add 1 to self.replies[sender].
        pass   # placeholder: replace this line


def words_in(text: str) -> list[str]:
    """The interesting words in a message: lowercase, no links, no stop words."""
    # TODO 7
    # - Lowercase the text, and turn phone-style curly apostrophes into plain
    #   ones, so "don't" stays one word. The curly one is "\u2019" in Python.
    # - Replace every link with a space: URL.sub(" ", text)
    # - WORD.findall(text) gives you a list of the words.
    # - Keep only the words that are longer than one letter and aren't in STOP_WORDS.
    #   A list comprehension does it in one line.
    return []   # placeholder: replace this line


def emojis_in(text: str) -> list[str]:
    """Every emoji in a message, in order. finditer() finds them one by one."""
    # TODO 8
    # - EMOJI.finditer(text) gives a match object for each emoji, one at a time.
    # - For each match, take match.group(), and remove "\ufe0f" from it.
    # - Return them as a list.
    return []   # placeholder: replace this line


def analyse(messages: Iterable[Message]) -> ChatStats:
    """Count everything, looking at each message exactly once.

    Nothing is ever kept in a list, so this works the same for 100 messages
    or 200,000.
    """
    # TODO 11
    # - stats = ChatStats(), and messages = iter(messages)
    # - first = next(messages, None). If it's None, there are no messages, so
    #   return stats. Otherwise, stats.add(first).
    # - Loop over pairwise(chain([first], messages)). For each (previous, message):
    #   stats.add(message), then stats.add_gap(previous, message).
    # - Return stats. Never make a list of the messages!
    return ChatStats()   # placeholder: replace this line


def fastest_replier(stats: ChatStats) -> tuple[str, timedelta] | None:
    """Who replies quickest on average? Only people with enough replies count."""
    # TODO 12
    # - Make a dictionary of each person's average reply time:
    #   stats.reply_time[name] / count, for everyone whose count in
    #   stats.replies is at least MIN_REPLIES.
    # - If it's empty, return None.
    # - Otherwise find the name with the smallest average, using min(..., key=...).
    #   Return (name, average).
    return None   # placeholder: replace this line


def favourite_words(stats: ChatStats) -> dict[str, tuple[str, int]]:
    """Each person's most-used word, and how many times they used it."""
    # TODO 13
    # - For each name in stats.messages, if stats.words[name] isn't empty, store
    #   its .most_common(1)[0], which is a (word, count) pair.
    # - Return the dictionary.
    return {}   # placeholder: replace this line
