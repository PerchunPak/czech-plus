"""Package for parsing input from the cards."""
import abc
import typing as t
from collections.abc import Callable, Generator, Iterator

import typing_extensions as te
from czech_plus._vendor.loguru import logger

from czech_plus import models
from czech_plus.logic.lexer import tokens

_HOOK_GENERATOR_SIGNATURE: te.TypeAlias = Generator[
    t.Optional[tuple[tokens.BaseToken, bool, bool]], t.Union[str, t.Literal[None]], None
]
_HOOK_SIGNATURE: te.TypeAlias = Callable[[], _HOOK_GENERATOR_SIGNATURE]
_ON_NEXT_HOOK: te.TypeAlias = Generator[t.Optional[tokens.BaseToken], t.Union[str, t.Literal[None]], tuple[bool, bool]]


class BaseLexer(abc.ABC):
    """Main class for transforming raw strings to tokens."""

    SEPARATE_SYMBOL = ","
    ADDITIONAL_SEPARATE_SYMBOL: t.Optional[str] = None
    ESCAPE_SYMBOL = "\\"
    WORD_ESCAPE_SYMBOL = "!"
    SKIP_SYMBOL = "_"

    def __init__(self, raw: dict[str, str]) -> None:
        self.__raw = raw

    def lex(self) -> Iterator[t.Union[tokens.BaseToken, str]]:
        r"""Lex :attr:`~czech_plus.logic.lexer.BaseLexer.__raw` attribute.

        Yields:
            :mod:`Token <czech_plus.logic.lexer.tokens>` or :obj:`string <str>`\ .
        """
        for string in self.__raw.values():
            rerun, skip = False, False
            temp_string = ""
            on_next_hook: t.Optional[_ON_NEXT_HOOK] = None

            for i, symbol in enumerate(string):
                while True:
                    if skip:
                        skip = False
                        break

                    if on_next_hook is not None:
                        while True:
                            try:
                                token = on_next_hook.send(symbol)
                            except StopIteration as exception:
                                rerun, skip = exception.value  # return statement in generator
                                on_next_hook = None
                                break
                            else:
                                if token is None:
                                    break

                                if temp_string != "":
                                    if isinstance(token, tokens.FutureFormToken):
                                        temp_string = temp_string[:-1]
                                        if temp_string == "":
                                            yield token
                                            continue

                                    yield temp_string
                                    temp_string = ""
                                yield token

                        if not rerun:
                            break
                        rerun = False

                    hook = self._hooks.get(symbol)
                    if hook is None:
                        temp_string += symbol
                        break

                    handle_hook_generator = self._handle_hook(hook)
                    while True:
                        try:
                            token = next(handle_hook_generator)
                        except StopIteration as exception:
                            rerun, skip = exception.value  # return statement in generator
                            assert rerun is False, "This doesn't make sense if you rerun symbol in first iteration!"
                            break
                        else:
                            if token is None:
                                on_next_hook = handle_hook_generator
                                break

                            if temp_string != "":
                                yield temp_string
                                temp_string = ""
                            yield token
                    break  # pragma: no cover # somewhy doesn't catch this string

            if on_next_hook is not None:
                yield t.cast(tokens.BaseToken, on_next_hook.send(None))
            if temp_string != "":
                yield temp_string

    def _handle_hook(self, hook: _HOOK_SIGNATURE) -> _ON_NEXT_HOOK:
        r"""Handle hook and yield result.

        Args:
            hook: Hook callable, that returns generator.

        Yields:
            :obj:`None` or :mod:`token <czech_plus.logic.lexer.tokens>`\ .

        .. note::
            You can send these params, with :obj:`generator.send` method. It takes :obj:`string <str>` or :obj:`None`\ ,
            where :obj:`string <str>` means next symbol, and :obj:`None` - end of input.

        Returns:
            .. note:: This value can be accessed with :obj:`StopIteration`\ ``.value``\ .

            :obj:`Tuple <tuple>` with two elements, where both are :obj:`bool`\ s.
            First is whether you need to rerun this symbol with new hook, and second one
            whether you need to skip next symbol.

        Example:
            .. code-block:: python

                handle_hook_generator = _handle_hook(hook)
                while True:
                    try:
                        token = next(handle_hook_generator)
                    except StopIteration as exception:
                        rerun, skip = exception.value  # return statement in generator
                        break
                    else:
                        # some token handling code

            Or you can ignore ``rerun`` and ``skip`` variables:

            .. code-block:: python

                for token in _handle_hook():
                    # some token handling code
        """
        result = next(generator := hook())
        while result is None:
            result = generator.send((yield))  # type: ignore[misc] # Yield value expected

        token, rerun, skip = result
        yield token

        return rerun, skip

    def _escape_one_symbol(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Escape one symbol.

        See :meth:`._handle_hook` for signature description.
        """
        next_symbol = yield  # type: ignore[misc] # Yield value expected
        if next_symbol is None:
            next_symbol = ""

        yield tokens.EscapedToken(next_symbol), False, False

    def _escape_entire_word(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Escape entire word.

        See :meth:`._handle_hook` for signature description.
        """
        escaped_part = ""

        while True:
            symbol = yield  # type: ignore[misc] # Yield value expected
            if symbol in (self.SEPARATE_SYMBOL, self.ADDITIONAL_SEPARATE_SYMBOL, None):
                break
            escaped_part += t.cast(str, symbol)

        yield tokens.EscapedToken(escaped_part), True, False

    def _separate_words(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Separate words.

        See :meth:`._handle_hook` for signature description.
        """
        yield tokens.SeparatorToken(), False, True

    def _additional_separate_words(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Separate words with additional separate symbol.

        See :meth:`._handle_hook` for signature description.
        """
        yield tokens.AdditionalSeparatorToken(), False, True

    def _skip_word(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Skip word.

        See :meth:`._handle_hook` for signature description.
        """
        yield tokens.SkipToken(), False, False

    @property
    def _hooks(self) -> dict[str, _HOOK_SIGNATURE]:
        """Dict, where first element is symbol for hook, and value is a hook.

        See :meth:`._handle_hook` for hook signature description.
        """
        hooks: dict[str, _HOOK_SIGNATURE] = {
            self.ESCAPE_SYMBOL: self._escape_one_symbol,
            self.WORD_ESCAPE_SYMBOL: self._escape_entire_word,
            self.SEPARATE_SYMBOL: self._separate_words,
            self.SKIP_SYMBOL: self._skip_word,
        }

        if self.ADDITIONAL_SEPARATE_SYMBOL:
            hooks[self.ADDITIONAL_SEPARATE_SYMBOL] = self._additional_separate_words

        return hooks


class NounLexer(BaseLexer):
    """Lexer for nouns."""


class VerbLexer(BaseLexer):
    """Lexer for verbs."""

    SEPARATE_SYMBOL = "."
    ADDITIONAL_SEPARATE_SYMBOL = ","
    FUTURE_FORM_START_SYMBOL, FUTURE_FORM_END_SYMBOL = "[", "]"

    def _future_form(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Find future form.

        See :meth:`~.BaseLexer._handle_hook` for signature description.
        """
        word = ""
        while True:
            symbol = yield  # type: ignore[misc] # Yield value expected
            if symbol == self.FUTURE_FORM_END_SYMBOL or symbol is None:
                break
            word += symbol

        yield tokens.FutureFormToken(word), False, False

    @property
    def _hooks(self) -> dict[str, _HOOK_SIGNATURE]:
        hooks = super()._hooks
        hooks[self.FUTURE_FORM_START_SYMBOL] = self._future_form
        return hooks


class AdjectiveLexer(BaseLexer):
    """Lexer for adjectives."""
