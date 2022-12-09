"""Module for our models."""
import enum
import typing
from abc import ABC
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    import typing_extensions


class MultiValueEnum(enum.Enum):
    """Base class for Enum with multiple values."""

    def __new__(cls, *values):
        """Construct new instance of the class."""
        obj = object.__new__(cls)
        for other_value in values:
            cls._value2member_map_[other_value] = obj
        return obj

    def __repr__(self):
        """Nice string representation of the class."""
        return "<%s.%s: %s>" % (
            self.__class__.__name__,
            self._name_,
            ", ".join([repr(v) for v in self._value_]),
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

    @property
    def questions(self) -> str:
        r"""Get questions of the case.

        Just an alias to :attr:`Case.value`\ [0].
        """
        return typing.cast(str, self.value[0])

    @property
    def number(self) -> int:
        r"""Get number of the case.

        Just an alias to :attr:`Case.value`\ [1].
        """
        return typing.cast(int, self.value[1])


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

    cocd: str
    """Completion of Comparison Degrees."""


AnyWord: "typing_extensions.TypeAlias" = typing.Union[NounWord, VerbWord, AdjectiveWord]
