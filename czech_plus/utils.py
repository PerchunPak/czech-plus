r"""Module for utils.

Some of those will be run in :mod:`czech_plus`\ .
Some will be used in other places.
"""
import sys
import typing

from czech_plus._vendor.loguru import logger

from czech_plus import config as config_module

__all__ = ["setup_logging", "Singleton"]


def setup_logging() -> None:
    """Setup logging for the addon."""
    config = config_module.Config()
    kwargs: dict[str, typing.Any] = {}  # type: ignore[misc] # Explicit "Any" is not allowed

    if config.logging.level <= config_module.LogLevel.DEBUG:
        kwargs["diagnose"] = True

    logger.remove()
    logger.add(
        sys.stdout,
        level=config.logging.level,
        filter="czech_plus",
        colorize=True,
        serialize=config.logging.json,
        backtrace=True,
        **kwargs,
    )
    logger.debug("Logging was setup!")


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
