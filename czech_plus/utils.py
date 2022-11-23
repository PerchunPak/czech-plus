r"""Module for utils. Those will be run in :mod:`czech_plus`\ ."""
import sys
import typing

from czech_plus._vendor.loguru import logger

from czech_plus import config

__all__ = ["setup_logging"]


def setup_logging() -> None:
    """Setup logging for the addon."""
    kwargs: dict[str, typing.Any] = {}  # type: ignore[misc] # Explicit "Any" is not allowed

    if config.config.logging.level <= config.LogLevel.DEBUG:
        kwargs["diagnose"] = True

    logger.remove()
    logger.add(
        sys.stdout,
        level=config.config.logging.level,
        filter="czech_plus",
        colorize=True,
        serialize=config.config.logging.json,
        backtrace=True,
        **kwargs,
    )
    logger.debug("Logging was setup!")
