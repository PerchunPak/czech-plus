"""Module for abstract processor class."""
import abc
import typing as t

from czech_plus.config import Config
from czech_plus.logic.lexer import tokens

_T = t.TypeVar("_T", bound=t.Iterator[t.Union[str, tokens.BaseToken]])


class BaseProcessor(abc.ABC):
    """Abstract processor class."""

    def __init__(self) -> None:
        self._config = Config()

    @abc.abstractmethod
    def process(self, content: dict[str, str], /) -> str:
        """Process the content.

        Args:
            content: Card fields inside dict.

        Returns:
            The processed ``czech`` field, ready to be inserted into the card.
        """

    def _navigate_over(self, generator: _T, /, *, dont_skip_escaped: bool = False) -> _T:  # type: ignore[misc]
        r"""Navigate over the generator.

        This method yields the same values as the generator, but if ``dont_skip_escaped`` is :obj:`False`\ ,
        it skips the escaped tokens and yields them as just a string. It also recursively navigates over
        :class:`future form tokens <czech_plus.logic.lexer.tokens.FutureFormToken>` content.

        Args:
            generator: Generator to navigate over.
            dont_skip_escaped: Whether to skip escaped tokens.

        Returns:
            The same generator.
        """
        temp_string = ""
        for token_or_string in generator:
            if isinstance(token_or_string, str):
                temp_string += token_or_string
            elif isinstance(token_or_string, tokens.EscapedToken):
                if dont_skip_escaped:
                    if temp_string != "":
                        yield temp_string
                        temp_string = ""
                    yield token_or_string
                else:
                    temp_string += token_or_string.content
            elif isinstance(token_or_string, tokens.FutureFormToken):
                if temp_string != "":
                    yield temp_string
                    temp_string = ""
                yield tokens.FutureFormToken(
                    self._navigate_over(token_or_string.content, dont_skip_escaped=dont_skip_escaped)
                )
            else:
                if temp_string != "":
                    yield temp_string
                    temp_string = ""
                yield token_or_string
        if temp_string != "":
            yield temp_string
