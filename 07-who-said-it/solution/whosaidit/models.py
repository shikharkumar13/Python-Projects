"""Quote and Author: dataclasses that check their own data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from whosaidit.errors import ValidationError


@dataclass(frozen=True)
class Author:
    """Someone who said something quotable, from their page on the site."""

    slug: str                       # "Albert-Einstein", the last part of the link to their page
    name: str
    born: date | None = None
    birthplace: str | None = None   # "Ulm, Germany"

    def __post_init__(self) -> None:
        """Runs straight after the dataclass's own __init__, so a bad Author can never exist."""
        if not self.slug.strip():
            raise ValidationError("An author needs a slug (the end of their page's link).")
        if not self.name.strip():
            raise ValidationError(f"The author {self.slug} has no name.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "name": self.name,
            "born": self.born.isoformat() if self.born else None,     # dates aren't JSON, so "1879-03-14"
            "birthplace": self.birthplace,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Author:
        try:
            born = date.fromisoformat(data["born"]) if data["born"] else None
            return cls(data["slug"], data["name"], born, data["birthplace"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValidationError(f"An author in the file doesn't look right: {error!r}") from error


@dataclass(frozen=True)
class Quote:
    """One quote: what was said, who said it, and its tags."""

    text: str
    author: str                     # the name, as the quote page shows it
    author_slug: str                # which Author it belongs to
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValidationError(f"A quote by {self.author or 'nobody'} has no text.")
        if not self.author.strip():
            raise ValidationError(f"The quote {self.text[:30]!r} has no author.")
        if not self.author_slug.strip():
            raise ValidationError(f"The quote {self.text[:30]!r} has no link to its author.")
        if any(not tag.strip() for tag in self.tags):
            raise ValidationError(f"The quote {self.text[:30]!r} has an empty tag.")

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "author": self.author, "author_slug": self.author_slug, "tags": list(self.tags)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Quote:
        try:
            return cls(data["text"], data["author"], data["author_slug"], tuple(data["tags"]))
        except (KeyError, TypeError, AttributeError) as error:
            raise ValidationError(f"A quote in the file doesn't look right: {error!r}") from error
