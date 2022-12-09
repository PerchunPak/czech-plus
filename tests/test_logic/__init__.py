"""Tests :mod:`czech_plus.logic` package."""
import typing as t
from collections.abc import Callable

from faker import Faker

__all__ = "FakesGenerator"


class FakesGenerator:
    """Class for generating fake data in Czech.

    This exists for getting same data for the same key.

    Examples:
        .. code-block:: python

            >>> Faker.seed(0)
            >>> fakes = FakesGenerator("pyint", 1, 20)
            >>> fakes[0]
            13
            >>> fakes[1]
            14
    """

    __cz_faker = Faker("cs_CZ")

    def __init__(self, __method: str, *__args, **__kwargs) -> None:
        self.__method: Callable[[t.Any], str] = getattr(self.__cz_faker, __method)  # type: ignore[misc] # Explicit Any
        self.__args, self.__kwargs = __args, __kwargs
        self.__vault: dict[int, str] = {}

    def __getitem__(self, key: int) -> str:
        """Return the same value for the same key.

        Args:
            key: Key to get the value for.

        Returns:
            The value for the vault.
        """
        if (item := self.__vault.get(key)) is not None:
            return item
        value = self.__method(*self.__args, **self.__kwargs)
        self.__vault[key] = value
        return value
