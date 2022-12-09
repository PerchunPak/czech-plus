"""Module for pytest configuration and global fixtures."""
import typing as t

import pytest

from czech_plus.config import Config


@pytest.fixture
def mock_config() -> t.Iterator[t.Callable[[str, t.Any], None]]:  # type: ignore[misc]
    """Fixture for mocking config.

    Returns:
        A function that mocks the config.
    """
    config = Config()
    content = config
    original = default = object()
    parsed_key: t.Optional[list[str]] = None

    def _mock_config(key: str, value: t.Any) -> None:  # type: ignore[misc]
        """Mock config.

        Args:
            key: Key to mock.
            value: Value to set.
        """
        nonlocal original, parsed_key, content

        parsed_key = key.split(".")
        for temp_key in parsed_key[:-1]:
            content = getattr(content, temp_key)

        original = getattr(content, parsed_key[-1])
        object.__setattr__(content, parsed_key[-1], value)

    yield _mock_config

    assert original is not default and parsed_key is not None
    object.__setattr__(content, parsed_key[-1], original)
