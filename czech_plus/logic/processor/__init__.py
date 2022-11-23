"""Package for processors of the words."""
import typing
from collections.abc import Iterator

from czech_plus._vendor.loguru import logger

from czech_plus import models
from czech_plus.logic.processor.implementations import (
    adjective as adjective_implementation,
)
from czech_plus.logic.processor.implementations import (
    noun as noun_implementation,
)
from czech_plus.logic.processor.implementations import (
    verb as verb_implementation,
)


def process_word_or_card(word_or_card: typing.Union[list[models.AnyWord], models.AnyWord]) -> Iterator[str]:
    """Process word or card."""
    logger.trace(f"Processing word or card: {word_or_card}")
    word_was_provided = False
    if isinstance(word_or_card, models.BaseWord):
        word_was_provided = True
        logger.trace("Word was provided.")
        card = [typing.cast(models.AnyWord, word_or_card)]
    else:
        logger.trace("Card was provided.")
        card = word_or_card
    del word_or_card

    if len(card) == 0:
        logger.trace("Card is empty, returning...")
        return []

    result = {  # type: ignore[operator]
        models.NounWord: noun_implementation.process,
        models.VerbWord: verb_implementation.process,
        models.AdjectiveWord: adjective_implementation.process,
    }[type(card[0])](card)

    if word_was_provided:
        processed_word = next(result)
        logger.debug(f"Result of word processing: {processed_word}")
        yield processed_word
    else:
        logger.trace("Card was given, returning iterator with results...")
        return result
