"""Module for implementing processing nouns."""
from collections.abc import Iterator

from czech_plus.models import NounWord


def process(card: list[NounWord]) -> Iterator[str]:
    """Process card with nouns."""
    for word in card:
        yield f"{word.gender.value} {word.czech}"
