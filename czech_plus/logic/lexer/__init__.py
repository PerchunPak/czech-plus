"""Package for parsing input from the cards."""
import abc
import typing as t
from collections.abc import Callable, Generator, Iterator

import typing_extensions as te
from czech_plus._vendor.loguru import logger

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

    def lex(self, string: str) -> Iterator[t.Union[tokens.BaseToken, str]]:
        r"""Lex ``string`` argument.

        Yields:
            :mod:`Token <czech_plus.logic.lexer.tokens>` or :obj:`string <str>`\ .
        """
        logger.debug(f"Lexing: {string}")
        rerun, skip = False, False
        temp_string = ""
        on_next_hook: t.Optional[_ON_NEXT_HOOK] = None

        for i, symbol in enumerate(string):
            while True:
                logger.debug(f"Lexing {symbol!r} (index: {i}) in {string=}")
                if skip:
                    logger.debug("skip is True")
                    skip = False
                    break

                if on_next_hook is not None:
                    logger.debug("on_next_hook is not None")
                    while True:
                        try:
                            token = on_next_hook.send(symbol)
                        except StopIteration as exception:
                            logger.debug(f"`on_next_hook` raised StopIteration with values: {exception.value}")
                            rerun, skip = exception.value  # return statement in generator
                            on_next_hook = None
                            break
                        else:
                            logger.debug(f"`on_next_hook` returned: {token=}")
                            if token is None:
                                logger.trace("token is None")
                                break

                            if temp_string != "":
                                logger.debug(f"temp_string != '' ({temp_string=})")
                                if isinstance(token, tokens.FutureFormToken):
                                    logger.trace(f"isinstance(token, tokens.FutureFormToken) is True")
                                    temp_string = temp_string[:-1]
                                    if temp_string == "":
                                        logger.trace("After stripping temp string, it's empty.")
                                        yield token
                                        continue

                                yield temp_string
                                temp_string = ""
                            yield token

                    logger.trace(f"{rerun=}")
                    if not rerun:
                        break
                    rerun = False

                hook = self._hooks.get(symbol)
                logger.debug(f"Got {hook=} on {symbol=}")
                if hook is None:
                    logger.trace("hook is None")
                    temp_string += symbol
                    break

                handle_hook_generator = self._handle_hook(hook)
                while True:
                    logger.trace(f"Handling `handle_hook_generator` with {hook=}")
                    try:
                        token = next(handle_hook_generator)
                    except StopIteration as exception:
                        logger.debug(f"`handle_hook_generator` raised StopIteration with values: {exception.value}")
                        rerun, skip = exception.value  # return statement in generator
                        assert rerun is False, "This doesn't make sense if you rerun symbol in first iteration!"
                        break
                    else:
                        logger.debug(f"`handle_hook_generator` returned: {token=}")
                        if token is None:
                            logger.trace("token is None")
                            on_next_hook = handle_hook_generator
                            break

                        if temp_string != "":
                            logger.trace("temp_string != ''")
                            yield temp_string
                            temp_string = ""
                        yield token
                logger.debug(f"Ended lexing for {symbol!r} (index: {i}).")
                break  # pragma: no cover # somewhy doesn't catch this string

        if on_next_hook is not None:
            logger.debug("on_next_hook is not None, but lexed full string.")
            yield t.cast(tokens.BaseToken, on_next_hook.send(None))
        if temp_string != "":
            logger.debug("temp_string != '', but lexed full string.")
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
        logger.debug(f"Handling {hook=}...")
        result = next(generator := hook())
        logger.debug(f"{result=}")
        while result is None:
            result = generator.send((yield))  # type: ignore[misc] # Yield value expected
            logger.debug(f"send {result=}")

        token, rerun, skip = result
        yield token

        return rerun, skip

    def _escape_one_symbol(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Escape one symbol.

        See :meth:`._handle_hook` for signature description.
        """
        logger.debug("Escaping one symbol...")
        next_symbol = yield  # type: ignore[misc] # Yield value expected
        logger.trace(f"{next_symbol=}")
        if next_symbol is None:
            logger.debug("next_symbol is None; falling back to ''")
            next_symbol = ""

        yield tokens.EscapedToken(next_symbol), False, False

    def _escape_entire_word(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Escape entire word.

        See :meth:`._handle_hook` for signature description.
        """
        logger.debug("Escaping entire word...")
        escaped_part = ""

        while True:
            symbol = yield  # type: ignore[misc] # Yield value expected
            logger.trace(f"Received {symbol=}")
            if symbol in (self.SEPARATE_SYMBOL, self.ADDITIONAL_SEPARATE_SYMBOL, None):
                logger.trace("Received symbol is separate symbol or None.")
                break
            escaped_part += t.cast(str, symbol)

        logger.debug(f"Escaped word: {escaped_part!r}")
        yield tokens.EscapedToken(escaped_part), True, False

    def _separate_words(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Separate words.

        See :meth:`._handle_hook` for signature description.
        """
        logger.debug("Separating words...")
        yield tokens.SeparatorToken(), False, True

    def _additional_separate_words(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Separate words with additional separate symbol.

        See :meth:`._handle_hook` for signature description.
        """
        logger.debug("Separating words with additional separate symbol...")
        yield tokens.AdditionalSeparatorToken(), False, True

    def _skip_word(self) -> _HOOK_GENERATOR_SIGNATURE:
        """Skip word.

        See :meth:`._handle_hook` for signature description.
        """
        logger.debug("Skipping word...")
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
        logger.debug("Finding word future form...")
        word = ""
        while True:
            symbol = yield  # type: ignore[misc] # Yield value expected
            logger.trace(f"Received {symbol=}")
            if symbol == self.FUTURE_FORM_END_SYMBOL or symbol is None:
                logger.trace(r"Received symbol is future form end symbol or None.")
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
