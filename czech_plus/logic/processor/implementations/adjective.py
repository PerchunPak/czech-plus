"""Module for implementing processing adjectives."""
from collections.abc import Iterator

from czech_plus.models import AdjectiveWord


def process(card: list[AdjectiveWord]) -> Iterator[str]:
    """Process card with adjectives."""
    for word in card:
        yield f"{word.czech} ({word.completion_of_comparison_degrees})"
