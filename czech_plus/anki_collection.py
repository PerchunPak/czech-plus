"""Module for accessing ``Collection`` object.

Usage of such "non-python" feature should be limited only to one specific zone.
This is what this file about. ``mw`` variable must be firstly imported here.
"""

__all__ = ["collection"]

import typing

import anki.collection
from loguru import logger


class LazyCollectionProxy:
    """Simple proxy to :class:`anki.collection.Collection`.

    This is also lazy because Anki doesn't add ``mw`` variable to globals in import time.
    """

    def __init__(self) -> None:
        # if you found this variable name confusing, as type name is different - this is how Anki works here
        # see https://addon-docs.ankiweb.net/the-anki-module.html#the-collection
        self.__main_window: typing.Optional[anki.collection.Collection] = None

    def __getattr__(self, item: str) -> typing.Any:  # type: ignore[misc] # Explicit "Any" is not allowed
        if self.__main_window is None:
            logger.debug("Trying to get ``mw`` variable, as it's was firstly requested")

            try:
                self.__main_window = typing.cast(anki.collection.Collection, globals()["mw"])
            except NameError:
                logger.critical("Can't get ``mw`` variable from globals, using outside of Anki is not implemented yet.")
                raise NotImplementedError

            logger.success("Found ``mw`` variable, I'm in Anki!")

        return getattr(self.__main_window, item)


collection: anki.collection.Collection = LazyCollectionProxy()  # type: ignore[assignment]
