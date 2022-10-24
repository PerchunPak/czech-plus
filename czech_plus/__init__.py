"""Main package for ``czech-plus`` addon."""
import typing

from loguru import logger
import sys
from czech_plus import config


def setup_logging() -> None:
    kwargs: dict[str, typing.Any] = {}  # type: ignore[misc] # Explicit "Any" is not allowed

    if config.config.logging.level <= config.LogLevel.DEBUG:
        kwargs["diagnose"] = True

    logger.add(
        sys.stdout,
        level=config.config.logging.level,
        filter="czech_plus",
        colorize=True,
        serialize=config.config.logging.json,
        backtrace=True,
        **kwargs,
    )


setup_logging()
