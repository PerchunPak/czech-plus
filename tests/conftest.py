"""Module for pytest configuration and global fixtures."""
import typing as t

import pytest

from czech_plus.config import Config

_T = t.TypeVar("_T")


@pytest.fixture
def mock_config() -> t.Iterator[t.Callable[[str, _T], _T]]:
    """Fixture for mocking config.

    Returns:
        A function that mocks the config.
    """
    config = Config()
    processed: dict[str, t.Any] = {}  # type: ignore[misc]

    def _mock_config(key: str, value: _T) -> _T:
        """Mock config.

        Args:
            key: Key to mock.
            value: Value to set.

        Returns:
            The value that was set.
        """
        content = config
        parsed_key = key.split(".")
        for temp_key in parsed_key[:-1]:
            content = getattr(content, temp_key)

        processed[key] = getattr(content, parsed_key[-1])
        object.__setattr__(content, parsed_key[-1], value)
        return value

    yield _mock_config

    for key, value in processed.items():
        parsed_key = key.split(".")
        content = config

        for temp_key in parsed_key[:-1]:
            content = getattr(content, temp_key)
        object.__setattr__(content, parsed_key[-1], value)


@pytest.fixture(scope="session")
def config() -> Config:
    """Fixture for config."""
    return Config()
