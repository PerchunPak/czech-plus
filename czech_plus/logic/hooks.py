"""Module for hooks, that will be called by Anki."""

import aqt
from czech_plus._vendor.loguru import logger

from czech_plus.logic.compiler import Compiler

# TODO: A method how to add custom buttons to the deck browser,
#       maybe I will use it for `compile` button.
# def add_custom_button(_: "deckbrowser.DeckBrowser", content: "deckbrowser.DeckBrowserContent") -> None:
#     content.stats += "<div>Hello World!</div>"
# aqt.gui_hooks.deck_browser_will_render_content.append(add_custom_button)


def append_hooks() -> None:
    """Register our hooks."""
    aqt.gui_hooks.main_window_did_init.append(  # type: ignore[attr-defined] # see https://github.com/ankitects/anki/issues/2276
        logger.catch(Compiler(lambda: aqt.mw.col.weakref()).compile_all_notes)  # type: ignore[union-attr]
    )
