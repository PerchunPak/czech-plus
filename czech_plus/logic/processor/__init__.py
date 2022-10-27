"""Package for processors of the words."""
import typing
from collections.abc import Iterator

import typing_extensions

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

_any_word: typing_extensions.TypeAlias = typing.Union[models.NounWord, models.VerbWord, models.AdjectiveWord]


def process_word_or_card(word_or_card: typing.Union[list[_any_word], _any_word]) -> Iterator[str]:
    """Process word or card."""
    word_was_provided = False
    if isinstance(word_or_card, models.BaseWord):
        word_was_provided = True
        card = [typing.cast(_any_word, word_or_card)]
    else:
        card = word_or_card
    del word_or_card

    if len(card) == 0:
        return []

    result = {  # type: ignore[operator]
        models.NounWord: noun_implementation.process,
        models.VerbWord: verb_implementation.process,
        models.AdjectiveWord: adjective_implementation.process,
    }[type(card[0])](card)

    if word_was_provided:
        yield next(result)
    else:
        return result
