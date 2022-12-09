"""Module for config management."""
from dataclasses import dataclass
from enum import IntEnum

from czech_plus.utils import Singleton


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

    level: LogLevel = LogLevel.WARNING
    """Log level for the app."""
    json: bool = False
    """Upload logs into JSON."""


@dataclass(frozen=True)
class BaseCardFields:
    """Base class for card fields."""

    czech: str = "Czech"
    """Name of the field, where czech word is."""
    translation: str = "Translation"
    """Name of the field, where translation is."""


@dataclass(frozen=True)
class NounCardFields(BaseCardFields):
    """Additional fields in noun cards."""

    gender: str = "Gender"
    """Name of the field, where gender is."""


@dataclass(frozen=True)
class VerbCardFields(BaseCardFields):
    """Additional fields in verb cards."""

    prepositions_and_cases: str = "Prepositions and Cases"
    """Name of the field, where prepositions and cases is."""


@dataclass(frozen=True)
class AdjectiveCardFields(BaseCardFields):
    """Additional fields in adjective cards."""

    completion_of_comparison_degrees: str = "Completion of Comparison Degrees"
    """Name of the field, where completion of comparison degrees is."""


@dataclass(frozen=True)
class NounCardsSettings:
    """Settings for noun cards."""

    note_type_name: str = "Noun"
    """Name of the Note Type for nouns."""
    fields: NounCardFields = NounCardFields()
    """Settings for fields in noun cards."""


@dataclass(frozen=True)
class VerbCardsSettings:
    """Settings for verb cards."""

    note_type_name: str = "Verb"
    """Name of the Note Type for verbs."""
    fields: VerbCardFields = VerbCardFields()
    """Settings for fields in verb cards."""


@dataclass(frozen=True)
class AdjectivesCardsSettings:
    """Settings for adjective cards."""

    note_type_name: str = "Adjective"
    """Name of the Note Type for adjectives."""
    fields: AdjectiveCardFields = AdjectiveCardFields()
    """Settings for fields in adjective cards."""


@dataclass(frozen=True)
class CardsSettings:
    """Settings for cards."""

    nouns: NounCardsSettings = NounCardsSettings()
    """Settings for noun cards."""
    verbs: VerbCardsSettings = VerbCardsSettings()
    """Settings for verb cards."""
    adjectives: AdjectivesCardsSettings = AdjectivesCardsSettings()
    """Settings for adjective cards."""


@dataclass(frozen=True)
class Config(metaclass=Singleton):
    """Config for the addon."""

    logging: LogSettings = LogSettings()
    """Settings for logs."""
    cards: CardsSettings = CardsSettings()
    """Settings for cards."""

    def __post_init__(self) -> None:
        """Post init hook.

        We use this method of setting attributes because we use frozen
        dataclass. This was found on https://github.com/python/cpython/issues/82625.

        Todo:
            In the future, this will contain actual logic for config loading.
        """
        object.__setattr__(self, "logging", LogSettings(LogLevel.TRACE))
