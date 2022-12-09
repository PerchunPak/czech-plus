"""Module for config management."""
import dataclasses
import json
import typing as t
from enum import IntEnum
from pathlib import Path

from czech_plus.utils import Singleton

if t.TYPE_CHECKING:
    import typing_extensions as te

BASE_DIR = Path(__file__).parent
_CONFIG_PATH = BASE_DIR / "config.json"
_CONFIG_AS_DICT: "te.TypeAlias" = "dict[str, t.Union[str, _CONFIG_AS_DICT]]"


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


@dataclasses.dataclass(frozen=True)
class LogSettings:
    """Settings for logs."""

    level: LogLevel = LogLevel.WARNING
    """Log level for the app."""
    json: bool = False
    """Upload logs into JSON."""


@dataclasses.dataclass(frozen=True)
class BaseCardFields:
    """Base class for card fields."""

    czech: str = "Czech"
    """Name of the field, where czech word is."""
    translation: str = "Translation"
    """Name of the field, where translation is."""


@dataclasses.dataclass(frozen=True)
class NounCardFields(BaseCardFields):
    """Additional fields in noun cards."""

    gender: str = "Gender"
    """Name of the field, where gender is."""


@dataclasses.dataclass(frozen=True)
class VerbCardFields(BaseCardFields):
    """Additional fields in verb cards."""

    prepositions_and_cases: str = "Prepositions and Cases"
    """Name of the field, where prepositions and cases is."""


@dataclasses.dataclass(frozen=True)
class AdjectiveCardFields(BaseCardFields):
    """Additional fields in adjective cards."""

    completion_of_comparison_degrees: str = "Completion of Comparison Degrees"
    """Name of the field, where completion of comparison degrees is."""


@dataclasses.dataclass(frozen=True)
class NounCardsSettings:
    """Settings for noun cards."""

    note_type_name: str = "Noun"
    """Name of the Note Type for nouns."""
    fields: NounCardFields = NounCardFields()
    """Settings for fields in noun cards."""


@dataclasses.dataclass(frozen=True)
class VerbCardsSettings:
    """Settings for verb cards."""

    note_type_name: str = "Verb"
    """Name of the Note Type for verbs."""
    fields: VerbCardFields = VerbCardFields()
    """Settings for fields in verb cards."""


@dataclasses.dataclass(frozen=True)
class AdjectivesCardsSettings:
    """Settings for adjective cards."""

    note_type_name: str = "Adjective"
    """Name of the Note Type for adjectives."""
    fields: AdjectiveCardFields = AdjectiveCardFields()
    """Settings for fields in adjective cards."""


@dataclasses.dataclass(frozen=True)
class CardsSettings:
    """Settings for cards."""

    nouns: NounCardsSettings = NounCardsSettings()
    """Settings for noun cards."""
    verbs: VerbCardsSettings = VerbCardsSettings()
    """Settings for verb cards."""
    adjectives: AdjectivesCardsSettings = AdjectivesCardsSettings()
    """Settings for adjective cards."""


@dataclasses.dataclass(frozen=True)
class Config(metaclass=Singleton):
    """Config for the addon."""

    logging: LogSettings = LogSettings()
    """Settings for logs."""
    cards: CardsSettings = CardsSettings()
    """Settings for cards."""

    def __post_init__(self) -> None:
        """Post init hook."""
        self._setup()

    def _setup(self) -> None:
        """Perform setup of the config."""
        config: _CONFIG_AS_DICT
        if not _CONFIG_PATH.exists():
            config = t.cast(_CONFIG_AS_DICT, dataclasses.asdict(self))
            t.cast(dict[str, str], config["logging"])["level"] = t.cast(dict[str, LogLevel], config["logging"])[
                "level"
            ].name

            with _CONFIG_PATH.open("w", encoding="utf8") as config_file:
                config_file.write(json.dumps(config, indent=4, ensure_ascii=False))
        else:
            with _CONFIG_PATH.open("r", encoding="utf8") as config_file:
                config = t.cast(_CONFIG_AS_DICT, json.load(config_file))

        self._set_values(self, config)

        # special handling for enums
        object.__setattr__(self.logging, "level", LogLevel[t.cast(str, self.logging.level)])

    def _set_values(self, object_to_set: t.Any, config: _CONFIG_AS_DICT, /) -> None:  # type: ignore[misc] # Explicit "Any" is not allowed
        """Set values from dict config to object.

        We use this method of setting attributes because we use frozen
        dataclass. This was found on https://github.com/python/cpython/issues/82625.

        Args:
            object_to_set: Object to set values to. To support recursion.
            config: Dict config to set values from.
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._set_values(getattr(object_to_set, key), value)
                continue
            object.__setattr__(object_to_set, key, value)
