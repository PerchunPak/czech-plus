"""Module for config management."""
from dataclasses import dataclass
from enum import IntEnum


class LogLevel(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass(frozen=True)
class LogSettings:
    level: LogLevel
    json: bool


@dataclass(frozen=True)
class Config:
    # TODO implement actual config
    logging: LogSettings

    @classmethod
    def setup(cls) -> "Config":
        return cls(LogSettings(LogLevel.DEBUG, False))

    @property
    def in_app(self):
        return False  # TODO make it


config: Config = Config.setup()
