"""Module for our models."""
import enum
import typing


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
