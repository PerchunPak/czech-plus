"""Module for implementing processing verbs."""
from collections.abc import Iterator

from czech_plus.models import VerbWord


def process(card: list[VerbWord]) -> Iterator[str]:
    """Process card with verbs."""
    for word in card:
        prepositions_and_cases = ", ".join(
            f"{(preposition + ' ') if preposition is not None else ''}{case.value}"
            for preposition, case in word.preposition_and_case
        )
        yield f"{word.czech} ({prepositions_and_cases})"
