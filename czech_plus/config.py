"""Module for config management."""
import dataclasses
import json
import threading
import time
import typing as t
from enum import IntEnum
from pathlib import Path

import aqt
from czech_plus._vendor.loguru import logger

from czech_plus.utils import Singleton

if t.TYPE_CHECKING:
    import typing_extensions as te

BASE_DIR = Path(__file__).parent.parent
_CONFIG_PATH = BASE_DIR / "config.json"
_ADDON_META_PATH = BASE_DIR / "meta.json"
_CONFIG_AS_DICT: "te.TypeAlias" = "dict[str, t.Union[str, _CONFIG_AS_DICT]]"


def _get_anki_config() -> _CONFIG_AS_DICT:
    """Get the config from Anki."""
    if aqt.mw is None:
        return {}
    return t.cast(_CONFIG_AS_DICT, aqt.mw.addonManager.getConfig(BASE_DIR.stem))


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
    processed: str = "Processed"
    """Name of the field, where already processed card is."""


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
        self._start_watching_for_changes()

    def _setup(self) -> None:
        """Perform setup of the config."""
        self._write_config()
        config = _get_anki_config()

        self._set_values(self, config)

        # special handling for enums
        if isinstance(self.logging.level, str):  # type: ignore[unreachable]
            object.__setattr__(self.logging, "level", LogLevel[self.logging.level])  # type: ignore[unreachable]

    def _write_config(self) -> None:
        """Write config to the file."""
        config = t.cast(_CONFIG_AS_DICT, dataclasses.asdict(self))
        config["logging"]["level"] = config["logging"]["level"].name  # type: ignore[index,union-attr]

        with _CONFIG_PATH.open("w", encoding="utf8") as config_file:
            config_file.write(json.dumps(config, indent=4, ensure_ascii=False))

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

    @classmethod
    def _start_watching_for_changes(cls) -> None:
        """Start watching for changes in config.

        This ensures that we will never start two config watchers in one time.
        """
        if not hasattr(cls, "_watcher"):
            logger.trace("Watcher wasn't started yet, starting it now.")
            cls._watcher: threading.Thread = threading.Thread(target=lambda: cls._watch_for_changes(cls()), daemon=True)  # type: ignore[misc,attr-defined]
            cls._watcher.start()  # type: ignore[attr-defined]
        else:
            logger.trace("Watcher was started before.")

    def _watch_for_changes(self) -> None:
        """Watch for changes in config file and update ``self`` based on changes."""
        logger.debug("Start watching for changes in config file.")
        stamp = _ADDON_META_PATH.stat().st_mtime

        while True:
            new_stamp = _ADDON_META_PATH.stat().st_mtime
            if new_stamp != stamp:
                logger.info("Config file changed. Reloading it.")
                stamp = new_stamp
                self._setup()

            time.sleep(1)
