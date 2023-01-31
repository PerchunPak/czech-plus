r"""Module for utils.

Some of those will be run in :mod:`czech_plus`\ .
Some will be used in other places.
"""
import sys
import typing

import aqt
from czech_plus._vendor.loguru import logger

from czech_plus import config as config_module

__all__ = ["setup_logging", "assert_that", "Singleton"]


def setup_logging() -> None:
    """Setup logging for the addon."""
    config = config_module.Config()

    logger.remove()
    if config.logging.level < config_module.LogLevel.WARNING:
        logger.add(
            sys.stdout,
            level=config.logging.level,
            filter=lambda record: record["level"].no < config_module.LogLevel.WARNING,
            colorize=True,
            serialize=config.logging.json,
            backtrace=True,
            diagnose=True,
        )
    logger.add(
        sys.stderr,
        level=config.logging.level,
        filter=lambda record: record["level"].no >= config_module.LogLevel.WARNING,
        colorize=True,
        serialize=config.logging.json,
        backtrace=True,
        diagnose=True,
    )
    logger.debug("Logging was setup!")


def compile_all_notes() -> None:
    """Just runs :meth:`czech_plus.logic.compiler.Compiler.compile_all_notes`."""
    from czech_plus.logic.compiler import Compiler  # circular import

    logger.catch(Compiler(lambda: aqt.mw.col.weakref()).compile_all_notes)()  # type: ignore[union-attr]


class Singleton(type):
    """Metaclass to do Singleton pattern."""

    _instances: dict[type, typing.Any] = {}  # type: ignore[misc] # Explicit "Any" is not allowed

    def __call__(cls, *args, **kwargs):
        """Actual logic in this class.

        See https://stackoverflow.com/a/6798042.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def assert_that(statement: bool, msg: str = "", /) -> None:
    """By default, Anki removes all asserts from the code, so we need to craft own assert.

    Example:
        .. code-block:: python

            assert next(generator) == str  # if this statement will not be executed - everything will fail.
    """
    if not statement:
        try:
            raise AssertionError(msg)
        except AssertionError:
            logger.exception("Oops, some assertion failed. It's either a bug nor error in syntax.")
