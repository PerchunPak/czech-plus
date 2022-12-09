"""Module for tokens, that then used inside lexer."""
import abc
import typing as t
from dataclasses import dataclass


@dataclass
class BaseToken(abc.ABC):
    """Base class for all tokens."""


@dataclass
class SeparatorToken(BaseToken):
    """Token for separator symbol."""


@dataclass
class AdditionalSeparatorToken(BaseToken):
    """Token for additional separator symbol."""


@dataclass
class EscapedToken(BaseToken):
    """Token for escape symbol."""

    content: str


@dataclass
class SkipToken(BaseToken):
    """Token for skip symbol."""


@dataclass
class FutureFormToken(BaseToken):
    """Token for verb's future form."""

    content: t.Iterator[t.Union[BaseToken, str]]
