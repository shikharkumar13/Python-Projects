"""Turning the numbers into a fun Markdown report."""

from __future__ import annotations

from datetime import datetime, timedelta

from wrapped.stats import ChatStats, fastest_replier, favourite_words

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def plural(count: int, word: str) -> str:
    """plural(1, "message") is "1 message", plural(1200, "message") is "1,200 messages"."""
    if count == 1:
        return f"1 {word}"
    return f"{count:,} {word}s"


def describe_duration(length: timedelta) -> str:
    """Say a length of time the way a person would: "2 min 10 s", "11 days, 3 hours"."""
    seconds = int(length.total_seconds())
    days, seconds = divmod(seconds, 24 * 60 * 60)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        return f"{plural(days, 'day')}, {plural(hours, 'hour')}"
    if hours > 0:
        return f"{plural(hours, 'hour')}, {minutes} min"
    if minutes > 0:
        return f"{minutes} min {seconds} s"
    return f"{seconds} s"


def nice_hour(hour: int) -> str:
    """21 becomes "9 pm", 0 becomes "midnight"."""
    if hour == 0:
        return "midnight"
    if hour == 12:
        return "noon"
    if hour < 12:
        return f"{hour} am"
    return f"{hour - 12} pm"


def nice_time(moment: datetime) -> str:
    """A date and time like "14 Jun, 21:02"."""
    return f"{moment.day} {moment:%b}, {moment:%H:%M}"


def nice_date(moment: datetime) -> str:
    """A date like "1 January"."""
    return f"{moment.day} {moment:%B}"


def build_report(stats: ChatStats, title: str, year: int) -> str:
    """The whole report, as Markdown text."""
    # main() only asks for a report when there's at least one message.
    assert stats.first is not None and stats.last is not None
    lines = [f"# {title}: Wrapped {year} 🎁", ""]
    people = len(stats.messages)
    lines.append(
        f"**{plural(stats.total, 'message')}** from {people} {'person' if people == 1 else 'people'}, "
        f"between {nice_date(stats.first)} and {nice_date(stats.last)} {year}."
    )

    # --- The Chatterbox --------------------------------------------------
    winner, count = stats.messages.most_common(1)[0]
    lines += ["", f"## 🏆 The Chatterbox: {winner}", ""]
    lines.append(f"{plural(count, 'message')}, which is {count / stats.total:.0%} of the whole chat.")
    lines += ["", "| Who | Messages |", "|---|---:|"]
    for name, sent in stats.messages.most_common():
        lines.append(f"| {name} | {sent:,} |")

    # --- Emoji of the Year -----------------------------------------------
    lines += [""]
    if len(stats.emojis) == 0:
        lines += ["## 😶 Emoji of the Year: none", "", "Not a single emoji all year. Impressive."]
    else:
        top = stats.emojis.most_common(4)
        emoji, used = top[0]
        lines += [f"## {emoji} Emoji of the Year: {emoji}", "", f"Used {plural(used, 'time')}."]
        if len(top) > 1:
            runners_up = ", ".join(f"{e} {n:,}" for e, n in top[1:])
            lines.append(f"Runners-up: {runners_up}.")

    # --- The Night Owl ---------------------------------------------------
    lines += [""]
    if len(stats.night) == 0:
        lines += ["## 🦉 The Night Owl: nobody", "", "Nobody sent a single message between 1 am and 5 am. Well rested!"]
    else:
        owl, late = stats.night.most_common(1)[0]
        lines += [f"## 🦉 The Night Owl: {owl}", "", f"{plural(late, 'message')} between 1 am and 5 am. Go to sleep!"]

    # --- The Lightning Replier -------------------------------------------
    lines += [""]
    fastest = fastest_replier(stats)
    if fastest is None:
        lines += ["## ⚡ The Lightning Replier: nobody yet", "", "Not enough replies to pick a winner."]
    else:
        name, average = fastest
        lines += [f"## ⚡ The Lightning Replier: {name}", "", f"Replies in {describe_duration(average)} on average."]

    # --- The Great Silence -----------------------------------------------
    silence = stats.longest_silence
    if silence is not None:
        lines += ["", "## 🤫 The Great Silence", ""]
        lines.append(
            f"{describe_duration(silence.length)} without a single message, from {nice_time(silence.start)} "
            f"until **{silence.broken_by}** broke it on {nice_time(silence.end)}."
        )

    # --- Rush Hour -------------------------------------------------------
    busiest_hour = max(stats.hours, key=lambda hour: stats.hours[hour])
    busiest_day = max(stats.weekdays, key=lambda day: stats.weekdays[day])
    lines += ["", "## ⏰ Rush Hour", ""]
    lines.append(f"The chat is busiest at **{nice_hour(busiest_hour)}**, and on **{DAY_NAMES[busiest_day]}s**.")

    # --- Words of the Year -----------------------------------------------
    favourites = favourite_words(stats)
    if len(favourites) > 0:
        lines += ["", "## 💬 Words of the Year", ""]
        for name, (word, times) in favourites.items():
            lines.append(f"- **{name}**: \"{word}\" ({plural(times, 'time')})")

    return "\n".join(lines) + "\n"
