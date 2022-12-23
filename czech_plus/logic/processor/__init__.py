"""Package for processors of the words."""
import typing as t

from czech_plus._vendor.loguru import logger

from czech_plus.config import Config
from czech_plus.logic.processor.implementations import (
    adjective,
    base,
    noun,
    verb,
)

__all__ = ["get_processor", "process_card"]


def get_processor(note_type: str) -> t.Optional[base.BaseProcessor]:
    """Get processor for the note type.

    Args:
        note_type: Name of the note type.

    Returns:
        Processor for the note type or None, if it wasn't found.
    """
    logger.trace(f"Getting processor for {note_type=}.")
    config = Config()

    parsers_table: dict[str, type[base.BaseProcessor]] = {
        config.cards.nouns.note_type_name: noun.NounProcessor,
        config.cards.verbs.note_type_name: verb.VerbProcessor,
        config.cards.adjectives.note_type_name: adjective.AdjectiveProcessor,
    }
    if note_type not in parsers_table.keys():
        return None

    return parsers_table[note_type]()


def process_card(content: dict[str, str], note_type: str) -> t.Optional[str]:
    """Process the card.

    Args:
        content: Content of the card.
        note_type: Name of the note type.

    Returns:
        Processed content of the card or None, if processor wasn't found.
    """
    logger.debug(f"Processing card with {note_type=}...")
    logger.trace(str(content))

    processor = get_processor(note_type)
    if processor is None:
        logger.debug("No processor for this note type.")
        return None

    processed = processor.process(content)
    logger.debug(f"Processed: {processed=}")
    return processed
