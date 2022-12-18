"""Module for hooks, that will be called by Anki."""
import typing as t

from aqt import gui_hooks
from czech_plus._vendor.loguru import logger

from czech_plus.logic.processor import get_processor

if t.TYPE_CHECKING:
    from anki.cards import Card  # circular import


def process_card_hook(html: str, card: "Card", _: str) -> str:
    """Main hook, that will change the card's content."""
    logger.debug("Hook was called.")

    content = dict(card.note().items())
    note_type = t.cast(str, card.note_type()["name"])
    parser = get_processor(note_type)

    if parser is None:
        logger.debug("No parser for this note type.")
        return html

    parsed = parser.process(content)
    logger.debug(f"Parsed: {parsed!r}")
    return html


def append_hooks() -> None:
    """Register our hooks."""
    gui_hooks.card_will_show.append(process_card_hook)
