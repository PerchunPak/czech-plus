"""Module for implementing processing nouns."""
from collections.abc import Iterator

from czech_plus._vendor.loguru import logger

from czech_plus.models import NounWord


def process(card: list[NounWord]) -> Iterator[str]:
    """Process card with nouns."""
    logger.trace("Processing noun card...")
    for word in card:
        logger.trace(f"Processing noun word '{word.czech}'...")
        result = f"{word.gender.value} {word.czech}"
        logger.debug(f"Result of processing noun '{word.czech}': {result}")
        yield result
