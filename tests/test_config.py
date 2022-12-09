"""Tests for the :mod:`czech_plus.config` module."""
import dataclasses
import json
import pathlib
import typing as t

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from czech_plus import config
from tests import factories


class TestConfig:
    """Tests for the :class:`czech_plus.config.Config` class."""

    @pytest.fixture(autouse=True)
    def remove_cached_config(self) -> t.Callable[[], None]:
        """Remove the cached config.

        Returns:
            A function to remove the cached config. It was called before each test
            automatically, but you can trigger it manually too.
        """

        def _remove_cached_config() -> None:
            config.Config._instances.pop(config.Config)

        _remove_cached_config()
        return _remove_cached_config

    def test_config_writes_default_config_if_it_does_not_exist(
        self, remove_cached_config: t.Callable[[], None], tmp_path: pathlib.Path, mocker: MockerFixture, faker: Faker
    ) -> None:
        """Test that the config writes the default config if it does not exist."""
        config_path = tmp_path / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        mocker.patch("czech_plus.config._CONFIG_PATH", config_path)
        cfg = config.Config()

        remove_cached_config()
        mocker.patch("czech_plus.config.Config._setup")
        default_cfg = config.Config()

        assert cfg == default_cfg

    def test_config_correctly_read_from_file(
        self, remove_cached_config: t.Callable[[], None], tmp_path: pathlib.Path, mocker: MockerFixture, faker: Faker
    ) -> None:
        """Test that the config is correctly read from a file."""
        config_path = tmp_path / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        custom_cfg = factories.ConfigFactory()
        config_as_dict = dataclasses.asdict(custom_cfg)
        t.cast(dict[str, str], config_as_dict["logging"])["level"] = t.cast(
            dict[str, config.LogLevel], config_as_dict["logging"]
        )["level"].name
        config_path.write_text(json.dumps(config_as_dict, indent=4, ensure_ascii=False), encoding="utf8")
        remove_cached_config()

        mocker.patch("czech_plus.config._CONFIG_PATH", config_path)
        cfg = config.Config()

        assert cfg == custom_cfg
