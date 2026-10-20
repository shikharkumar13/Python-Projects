"""Tests for counting words, emoji, silences and replies."""

from datetime import datetime, timedelta

import pytest

from wrapped.parser import Message
from wrapped.stats import analyse, emojis_in, fastest_replier, favourite_words, words_in

START = datetime(2025, 3, 12, 20, 0)


def at(minutes: float, sender: str, text: str = "hi") -> Message:
    """A message sent `minutes` after 20:00 on 12 March 2025."""
    return Message(START + timedelta(minutes=minutes), sender, text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Yaar the CAFE is open", ["yaar", "cafe", "open"]),    # lowercase, and "the" and "is" are stop words
        ("don't go there", ["go"]),                             # "don't" is one word, and a stop word
        ("look https://example.com/menu now", ["look"]),        # links are removed
        ("u r 2 good", ["good"]),                               # numbers and single letters are dropped
        ("Meera\u2019s cafe, don\u2019t", ["meera's", "cafe"]),     # a phone's curly apostrophe
        ("😂😂", []),
    ],
)
def test_words_in(text, expected):
    assert words_in(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("haha 😂😂", ["😂", "😂"]),
        ("nice 👍🏽", ["👍🏽"]),                    # a skin tone stays with its emoji
        ("love it ❤\ufe0f and ❤", ["❤", "❤"]),         # with and without the invisible emoji mark: the same emoji
        ("sunny ☀ today", ["☀"]),
        ("great ⭐ go India 🇮🇳", ["⭐", "🇮🇳"]),        # a flag is one emoji, made of two symbols
        ("no emoji here", []),
    ],
)
def test_emojis_in(text, expected):
    assert emojis_in(text) == expected


def test_counting_messages_emoji_and_night_owls():
    messages = [
        Message(datetime(2025, 3, 12, 1, 30), "Kabir", "can't sleep 😴"),
        Message(datetime(2025, 3, 12, 2, 0), "Kabir", "anyone?"),
        Message(datetime(2025, 3, 12, 21, 0), "Riya", "morning 😂😂"),
        Message(datetime(2025, 3, 12, 21, 1), "Riya", "<Media omitted>"),
    ]
    stats = analyse(messages)
    assert stats.total == 4
    assert stats.messages == {"Kabir": 2, "Riya": 2}
    assert stats.emojis == {"😴": 1, "😂": 2}
    assert stats.night == {"Kabir": 2}
    assert stats.hours == {1: 1, 2: 1, 21: 2}
    assert stats.weekdays == {2: 4}                      # 12 March 2025 was a Wednesday
    assert "media" not in stats.words["Riya"]            # photos don't count as words


def test_the_longest_silence_and_who_broke_it():
    stats = analyse([at(0, "Riya"), at(5, "Arjun"), at(605, "Meera"), at(610, "Riya")])
    silence = stats.longest_silence
    assert silence.length == timedelta(minutes=600)
    assert silence.broken_by == "Meera"
    assert silence.start == START + timedelta(minutes=5)


def test_replies_only_count_when_answering_someone_else_soon():
    stats = analyse([
        at(0, "Riya"),
        at(2, "Meera"),        # a reply after 2 minutes
        at(3, "Meera"),        # Meera again: not a reply to herself
        at(200, "Arjun"),      # over an hour later: not a reply
        at(201, "Riya"),       # a reply after 1 minute
    ])
    assert stats.replies == {"Meera": 1, "Riya": 1}
    assert stats.reply_time["Meera"] == timedelta(minutes=2)


def test_fastest_replier_needs_enough_replies():
    # Meera replies once, very fast. Riya replies three times, a bit slower.
    messages = [at(0, "Arjun"), at(0.1, "Meera")]
    for i in range(3):
        messages += [at(10 + i * 10, "Arjun"), at(12 + i * 10, "Riya")]
    stats = analyse(messages)
    name, average = fastest_replier(stats)
    assert name == "Riya"
    assert average == timedelta(minutes=2)


def test_no_fastest_replier_in_a_quiet_chat():
    assert fastest_replier(analyse([at(0, "Riya"), at(1, "Arjun")])) is None


def test_favourite_words():
    stats = analyse([at(0, "Riya", "yaar yaar chalo"), at(1, "Arjun", "bro"), at(2, "Riya", "yaar")])
    assert favourite_words(stats) == {"Riya": ("yaar", 3), "Arjun": ("bro", 1)}


def test_analyse_works_on_a_generator():
    # A generator expression, not a list: analyse() must not need a list.
    stats = analyse(at(minute, "Riya") for minute in range(1000))
    assert stats.total == 1000


def test_an_empty_chat():
    stats = analyse([])
    assert stats.total == 0 and stats.longest_silence is None
