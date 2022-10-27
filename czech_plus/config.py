"""Module for config management."""
from dataclasses import dataclass
from enum import IntEnum


class LogLevel(IntEnum):
    """Log level for the addon."""

    TRACE = 5
    """Use only for tracing error without a debugger."""
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass(frozen=True)
class LogSettings:
    """Settings for logs."""

    level: LogLevel
    """Log level for the app."""
    json: bool
    """Upload logs into JSON."""


@dataclass(frozen=True)
class Config:
    """Config for the addon."""

    # TODO implement actual config
    logging: LogSettings
    """Settings for logs."""

    @classmethod
    def setup(cls) -> "Config":
        """Setup config instance."""
        return cls(LogSettings(LogLevel.DEBUG, False))

    @property
    def in_app(self):
        return False  # TODO make it


config: Config = Config.setup()
"""Initialised config variable."""
