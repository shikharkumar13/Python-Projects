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
        self.total += 1
        if self.first is None:
            self.first = message.when
        self.last = message.when

        self.messages[message.sender] += 1
        self.hours[message.when.hour] += 1
        self.weekdays[message.when.weekday()] += 1
        if message.when.hour in NIGHT_HOURS:
            self.night[message.sender] += 1

        self.emojis.update(emojis_in(message.text))
        if message.text != MEDIA and message.text not in DELETED:
            self.words[message.sender].update(words_in(message.text))

    def add_gap(self, previous: Message, message: Message) -> None:
        """Look at the time between two messages next to each other."""
        gap = message.when - previous.when

        if self.longest_silence is None or gap > self.longest_silence.length:
            self.longest_silence = Silence(gap, previous.when, message.when, message.sender)

        # A reply is an answer to someone else, and not too long after.
        if message.sender != previous.sender and gap <= REPLY_WINDOW:
            self.reply_time[message.sender] += gap
            self.replies[message.sender] += 1


def words_in(text: str) -> list[str]:
    """The interesting words in a message: lowercase, no links, no stop words."""
    # Phone keyboards usually turn ' into a curly one (\u2019), so "don't"
    # would split into "don" and "t". Turning it back first keeps it one word.
    text = URL.sub(" ", text.lower().replace("\u2019", "'"))
    return [word for word in WORD.findall(text) if len(word) > 1 and word not in STOP_WORDS]


def emojis_in(text: str) -> list[str]:
    """Every emoji in a message, in order. finditer() finds them one by one."""
    # \ufe0f is removed so that ❤ and ❤️ count as the same emoji.
    return [match.group().replace("\ufe0f", "") for match in EMOJI.finditer(text)]


def analyse(messages: Iterable[Message]) -> ChatStats:
    """Count everything, looking at each message exactly once.

    Nothing is ever kept in a list, so this works the same for 100 messages
    or 200,000.
    """
    stats = ChatStats()
    messages = iter(messages)

    # Take the first message on its own. next() with a default gives None
    # instead of an error when there are no messages at all.
    first = next(messages, None)
    if first is None:
        return stats
    stats.add(first)

    # pairwise() hands out each message together with the one before it:
    # (m1, m2), (m2, m3), ... chain() puts the first message back in front
    # of the rest, so it can be the "one before" the second message.
    for previous, message in pairwise(chain([first], messages)):
        stats.add(message)
        stats.add_gap(previous, message)
    return stats


def fastest_replier(stats: ChatStats) -> tuple[str, timedelta] | None:
    """Who replies quickest on average? Only people with enough replies count."""
    averages = {
        name: stats.reply_time[name] / count
        for name, count in stats.replies.items()
        if count >= MIN_REPLIES
    }
    if len(averages) == 0:
        return None
    name = min(averages, key=lambda person: averages[person])
    return name, averages[name]


def favourite_words(stats: ChatStats) -> dict[str, tuple[str, int]]:
    """Each person's most-used word, and how many times they used it."""
    favourites = {}
    for name in stats.messages:          # in the order people first spoke
        if len(stats.words[name]) > 0:
            favourites[name] = stats.words[name].most_common(1)[0]
    return favourites
