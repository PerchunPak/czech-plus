"""Module for our models."""
import enum
import typing
from abc import ABC
from dataclasses import dataclass


class MultiValueEnum(enum.Enum):
    """Base class for Enum with multiple values."""

    def __new__(cls, *values):
        """Construct new instance of the class."""
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values  # type: ignore[attr-defined]
        return obj

    def __repr__(self):
        """Nice string representation of the class."""
        return "<%s.%s: %s>" % (
            self.__class__.__name__,
            self._name_,
            ", ".join([repr(v) for v in self._all_values]),  # type: ignore[attr-defined]
        )


@enum.unique
class Gender(enum.Enum):
    """Gender of the noun."""

    M = "ten"
    """Masculine."""
    F = "ta"
    """Female."""
    N = "to"
    """Neuter."""
    mM = "mM"
    """Masculine plural."""
    mF = "mF"
    """Female plural."""
    mN = "mN"
    """Neuter plural."""


@enum.unique
class Case(MultiValueEnum):
    """Case of the noun word.

    Value of the item is question, you can also use numbers (from 1 to 7) as aliases.
    """

    nominative = "kdo? co?", 1
    genitive = "koho? čeho?", 2
    dative = "komu? čemu?", 3
    accusative = "koho? co?", 4
    vocative = "voláme", 5
    locative = "kom? čem?", 6
    instrumental = "kým? čím?", 7


@dataclass(frozen=True)
class BaseWord(ABC):
    """Base class for words."""

    czech: str
    translation: str


@dataclass(frozen=True)
class NounWord(BaseWord):
    """Class for representation of noun words."""

    gender: Gender


@dataclass(frozen=True)
class VerbWord(BaseWord):
    """Class for representation of verb words."""

    preposition_and_case: list[tuple[typing.Optional[str], Case]]
    future_form: bool


@dataclass(frozen=True)
class AdjectiveWord(BaseWord):
    """Class for representation of adjective words."""

    completion_of_comparison_degrees: str
