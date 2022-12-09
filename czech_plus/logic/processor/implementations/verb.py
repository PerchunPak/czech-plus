"""Module for implementing processing verbs."""
import typing as t

from czech_plus._vendor.loguru import logger

from czech_plus import models
from czech_plus.logic.lexer import VerbLexer, tokens
from czech_plus.logic.processor.implementations import BaseProcessor

_T = t.TypeVar("_T", bound=t.Iterator[t.Union[str, tokens.BaseToken]])


class VerbProcessor(BaseProcessor):
    """Verb processor."""

    def __init__(self) -> None:
        super().__init__()

        self.__czech_field_name = self._config.cards.verbs.fields.czech
        self.__pac_field_name = self._config.cards.verbs.fields.prepositions_and_cases

    def process(self, content: dict[str, str], /) -> str:
        """Process the content.

        Args:
            content: Card fields inside dict.

        Returns:
            The processed ``czech`` field, ready to be inserted into the card.
        """
        logger.trace(
            f"Parsing verb card\n"
            f"{self.__czech_field_name} (Czech field): {content[self.__czech_field_name]}\n"
            f"{self.__pac_field_name} (Prepositions and Cases field): {content[self.__pac_field_name]}"
        )

        lexer = VerbLexer()
        lexed_czech = self._navigate_over(lexer.lex(content[self.__czech_field_name]))
        lexed_prepositions_and_cases = self._navigate_over(
            lexer.lex(content[self.__pac_field_name]), dont_skip_escaped=True
        )
        get_token_or_string = self._get_token_or_string(lexed_czech)  # type: ignore[type-var]

        skip = False
        result = ""
        processed_prepositions_and_cases = ""
        for prepositions_and_cases in lexed_prepositions_and_cases:
            logger.trace(f"{prepositions_and_cases=}")

            if skip:
                skip = False
                continue

            if isinstance(prepositions_and_cases, tokens.SeparatorToken):
                token_or_string = get_token_or_string()
                assert isinstance(token_or_string, str)
                result += f"{token_or_string} ({processed_prepositions_and_cases}), "
                processed_prepositions_and_cases = ""
            elif isinstance(prepositions_and_cases, tokens.AdditionalSeparatorToken):
                processed_prepositions_and_cases += ", "

            elif isinstance(prepositions_and_cases, tokens.FutureFormToken):
                token_or_string = get_token_or_string()
                assert isinstance(token_or_string, str)
                result += f"{token_or_string} ({processed_prepositions_and_cases}) "
                processed_prepositions_and_cases = ""

                token_or_string_generator = get_token_or_string()
                assert isinstance(token_or_string_generator, tokens.FutureFormToken)
                token_or_string = next(token_or_string_generator.content)
                assert isinstance(token_or_string, str)

                for prepositions_and_cases_item in prepositions_and_cases.content:
                    if isinstance(prepositions_and_cases_item, str):
                        processed_prepositions_and_cases += self._process_prepositions_and_cases(
                            prepositions_and_cases_item
                        )
                    elif isinstance(prepositions_and_cases_item, tokens.AdditionalSeparatorToken):
                        processed_prepositions_and_cases += ", "
                    else:  # pragma: no cover
                        raise NotImplementedError("We don't support other scenarios here.")

                result += f"[{token_or_string} ({processed_prepositions_and_cases})], "
                processed_prepositions_and_cases = ""
                skip = True

            elif isinstance(prepositions_and_cases, tokens.SkipToken):
                token_or_string = get_token_or_string()
                assert isinstance(token_or_string, str)
                result += token_or_string + ", "
                skip = True

            elif isinstance(prepositions_and_cases, (str, tokens.EscapedToken)):
                processed_prepositions_and_cases += self._process_prepositions_and_cases(prepositions_and_cases)
            else:  # pragma: no cover
                raise NotImplementedError("We don't support other scenarios here.")

        if processed_prepositions_and_cases != "":
            token_or_string = get_token_or_string()
            assert isinstance(token_or_string, str)
            result += f"{token_or_string} ({processed_prepositions_and_cases})"

        return result.rstrip(", ")

    def _get_token_or_string(self, lexed_czech: t.Iterator[_T], /) -> t.Callable[[], _T]:
        r"""Get token or string from the lexed Czech field.

        Args:
            lexed_czech: Iterator over lexed Czech field.

        Returns:
            Function that logs the token, and asserts that it's not :class:`~czech_plus.logic.lexer.tokens.SeparatorToken`
            and if it's an :class:`~czech_plus.logic.lexer.tokens.AdditionalSeparatorToken`\ , the function will return
            next element.
        """

        def get_token_or_string() -> _T:
            token_or_string = next(lexed_czech)
            logger.trace(f"{token_or_string=}")
            assert not isinstance(token_or_string, tokens.SeparatorToken)

            if isinstance(token_or_string, tokens.AdditionalSeparatorToken):
                return get_token_or_string()  # type: ignore[unreachable] # has coverage in tests

            return token_or_string

        return get_token_or_string

    def _process_prepositions_and_cases(self, preposition_and_case: t.Union[str, tokens.BaseToken], /) -> str:
        """Process prepositions and cases.

        Args:
            preposition_and_case: Preposition and case to process.

        Returns:
            Processed preposition and case.
        """
        logger.trace(f"Processing preposition and case: {preposition_and_case!r}")

        if isinstance(preposition_and_case, str):
            split = preposition_and_case.split(" ")
            if len(split) == 1:
                return models.Case(int(split[0])).questions  # type: ignore[no-untyped-call]
            elif split[1] == "":
                # Preposition before escaped case
                #
                # prep !case
                # ^^^^^
                # notice that last symbol is a space, but it has deleted by split
                return preposition_and_case

            preposition, case = split
            return f"{preposition} {models.Case(int(case)).questions}"  # type: ignore[no-untyped-call]
        elif isinstance(preposition_and_case, tokens.EscapedToken):
            return preposition_and_case.content
        else:  # pragma: no cover
            raise NotImplementedError("We don't support other scenarios here.")
