"""Module for tokens, that then used inside lexer."""
import abc
from dataclasses import dataclass


@dataclass
class BaseToken(abc.ABC):
    """Base class for all tokens."""


@dataclass
class TokenWithContent(BaseToken, abc.ABC):
    """Base class for all tokens, which contain ``content`` field."""

    content: str


@dataclass
class SeparatorToken(BaseToken):
    """Token for separator symbol."""


@dataclass
class AdditionalSeparatorToken(BaseToken):
    """Token for additional separator symbol."""


@dataclass
class EscapedToken(TokenWithContent):
    """Token for escape symbol."""


@dataclass
class SkipToken(BaseToken):
    """Token for skip symbol."""


@dataclass
class FutureFormToken(TokenWithContent):
    """Token for verb's future form."""
