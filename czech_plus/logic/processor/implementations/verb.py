"""Module for implementing processing verbs."""
from collections.abc import Iterator

from czech_plus._vendor.loguru import logger

from czech_plus.models import VerbWord


def process(card: list[VerbWord]) -> Iterator[str]:
    """Process card with verbs."""
    logger.trace("Processing verb card...")
    for word in card:
        logger.trace(f"Processing verb word '{word.czech}'...")

        prepositions_and_cases = ", ".join(
            f"{(preposition + ' ') if preposition is not None else ''}{case.value}"
            for preposition, case in word.preposition_and_case
        )
        result = f"{word.czech} ({prepositions_and_cases})"

        logger.debug(f"Result of processing verb '{word.czech}': {result}")
        yield result
