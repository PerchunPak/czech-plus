"""Module for implementing processing adjectives."""
from collections.abc import Iterator

from czech_plus._vendor.loguru import logger

from czech_plus.models import AdjectiveWord


def process(card: list[AdjectiveWord]) -> Iterator[str]:
    """Process card with adjectives."""
    logger.trace("Processing adjective card...")
    for word in card:
        logger.trace(f"Processing adjective word '{word.czech}'...")
        result = f"{word.czech} ({word.completion_of_comparison_degrees})"
        logger.debug(f"Result of processing adjective '{word.czech}': {result}")
        yield result
