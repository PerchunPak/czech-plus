"""Module for implementing processing verbs."""
import typing as t

from czech_plus._vendor.loguru import logger

from czech_plus import models
from czech_plus.logic.lexer import VerbLexer, tokens
from czech_plus.logic.processor.implementations import BaseProcessor
from czech_plus.utils import assert_that

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
        logger.debug(
            "Processing verb card\n"
            f"{self.__czech_field_name} (Czech field): {content[self.__czech_field_name]}\n"
            f"{self.__pac_field_name} (Prepositions and Cases field): {content[self.__pac_field_name]}"
        )

        pre_processed = self._pre_process(content)
        if not content[self.__pac_field_name]:
            logger.warning(f"PaC field is empty, skipping. Czech field: {content[self.__czech_field_name]}")
            return content[self.__czech_field_name]
        return self._process(pre_processed)

    def _pre_process(
        self, content: dict[str, str]
    ) -> t.Iterator[
        tuple[
            t.Union[str, tokens.FutureFormTokenStart, tokens.FutureFormTokenEnd], list[t.Union[tokens.BaseToken, str]]
        ]
    ]:
        logger.debug(
            "Pre-processing verb card\n"
            f"{self.__czech_field_name} (Czech field): {content[self.__czech_field_name]}\n"
            f"{self.__pac_field_name} (Prepositions and Cases field): {content[self.__pac_field_name]}"
        )

        lexer = VerbLexer()
        lexed_czech = self._navigate_over(lexer.lex(content[self.__czech_field_name]))
        lexed_prepositions_and_cases = self._navigate_over(
            lexer.lex(content[self.__pac_field_name]), dont_skip_escaped=True
        )

        future_form_was = False
        for czech in lexed_czech:
            logger.debug(f"Pre-processing czech {czech!r}.")
            if isinstance(czech, tokens.AdditionalSeparatorToken):
                logger.debug("Skipping additional separator token.")
                continue
            elif isinstance(czech, str):
                prepositions_and_cases = list(self._pre_process_czech_token(czech, lexed_prepositions_and_cases))
                logger.debug(f"Pre-processed prepositions and cases here: {prepositions_and_cases!r}.")
                if len(prepositions_and_cases) > 0 and isinstance(
                    prepositions_and_cases[-1], (tokens.FutureFormTokenStart, tokens.FutureFormTokenEnd)
                ):
                    logger.debug("Future form was found.")
                    future_form_was = True
                    prepositions_and_cases.pop()
                yield czech, prepositions_and_cases
            elif isinstance(czech, (tokens.FutureFormTokenStart, tokens.FutureFormTokenEnd)):
                logger.debug("Processing future form.")
                if not future_form_was and isinstance(czech, tokens.FutureFormTokenStart):
                    assert_that(list(self._pre_process_czech_token(czech, lexed_prepositions_and_cases)) == [czech])
                future_form_was = False
                yield czech, [czech]
            else:  # pragma: no cover
                raise NotImplementedError(f"Unexpected czech token type: {czech} ({type(czech)})")

    def _pre_process_czech_token(
        self,
        czech: t.Union[tokens.BaseToken, str],
        lexed_prepositions_and_cases: t.Iterator[t.Union[tokens.BaseToken, str]],
    ) -> t.Iterator[t.Union[tokens.BaseToken, str]]:
        logger.debug(f"Pre-processing czech token {czech!r}.")
        if isinstance(czech, tokens.FutureFormTokenStart):
            assert_that(next(lexed_prepositions_and_cases) == tokens.FutureFormTokenStart())
            yield tokens.FutureFormTokenStart()
        elif isinstance(czech, str):
            for i, preposition_and_case in enumerate(lexed_prepositions_and_cases):
                logger.debug(f"Pre-processing preposition and case {preposition_and_case!r} in czech token {czech!r}.")
                if isinstance(preposition_and_case, tokens.SeparatorToken):
                    logger.debug(f"Skipping separator token (index={i}).")
                    assert i != 0
                    break

                yield preposition_and_case

                if isinstance(preposition_and_case, tokens.FutureFormTokenStart):
                    logger.trace("'tokens.FutureFormTokenStart' was found.")
                    break
        else:  # pragma: no cover
            raise NotImplementedError(f"Unexpected czech token type: {czech} ({type(czech)})")

    def _process(
        self,
        pre_processed: t.Iterator[
            tuple[
                t.Union[str, tokens.FutureFormTokenStart, tokens.FutureFormTokenEnd],
                list[t.Union[tokens.BaseToken, str]],
            ]
        ],
    ) -> str:
        result: str = ""
        for czech, prepositions_and_cases in pre_processed:
            logger.debug(f"Processing {czech=} {prepositions_and_cases=} in pre-processed.")

            skip = False
            processed_prepositions_and_cases = ""
            for i, preposition_and_case in enumerate(prepositions_and_cases):
                logger.debug(
                    f"Processing {preposition_and_case=} (index={i}) in prepositions and cases. "
                    f"Already processed: {processed_prepositions_and_cases!r}"
                )
                if skip:
                    logger.debug(f"Skipping {preposition_and_case=} (index={i}), skip was True.")
                    skip = False
                    continue

                if isinstance(preposition_and_case, tokens.SkipToken):
                    logger.debug("Found skip token.")
                    if i == len(prepositions_and_cases) - 1 and processed_prepositions_and_cases.endswith(", "):
                        logger.trace("Removing trailing comma on the end.")
                        processed_prepositions_and_cases = processed_prepositions_and_cases[:-2]
                        break
                    skip = True
                    continue

                processed_prepositions_and_cases += (
                    added_part := self._process_preposition_and_case(preposition_and_case)
                )
                logger.trace(f"Added {added_part!r} to processed prepositions and cases.")

            if isinstance(czech, (tokens.FutureFormTokenStart, tokens.FutureFormTokenEnd)):
                logger.debug(f"'czech' is future form. ({czech=} {processed_prepositions_and_cases=})")
                to_add = ((" " if result else "") + "[") if isinstance(czech, tokens.FutureFormTokenStart) else "]"
                logger.trace(f"Adding {to_add!r} to the result.")
                result += to_add
            else:
                logger.trace(f"'czech' is not a future form. ({czech=} {processed_prepositions_and_cases=})")
                result += ", " if result and not result.endswith("[") else ""
                result += czech
                if processed_prepositions_and_cases != "":
                    result += " (" + processed_prepositions_and_cases + ")"
        logger.debug(f"Processed result: {result!r}.")
        return result

    def _process_preposition_and_case(self, preposition_and_case: t.Union[tokens.BaseToken, str], /) -> str:
        logger.trace(f"Processing preposition and case: {preposition_and_case!r}.")
        if isinstance(preposition_and_case, tokens.AdditionalSeparatorToken):
            return ", "
        elif isinstance(preposition_and_case, tokens.EscapedToken):
            return preposition_and_case.content
        elif isinstance(preposition_and_case, str):
            return self._process_raw_preposition_and_case(preposition_and_case)
        elif isinstance(preposition_and_case, tokens.FutureFormTokenStart):
            return "["
        elif isinstance(preposition_and_case, tokens.FutureFormTokenEnd):
            return "]"
        else:  # pragma: no cover
            raise NotImplementedError(
                f"Unexpected preposition and case token type: {preposition_and_case} ({type(preposition_and_case)})"
            )

    def _process_raw_preposition_and_case(self, preposition_and_case: str, /) -> str:
        """Process raw preposition and case, when they're numbers for example.

        Args:
            preposition_and_case: Preposition and case to process.

        Returns:
            Processed preposition and case.
        """
        logger.trace(f"Processing preposition and case: {preposition_and_case!r}")

        split = preposition_and_case.split(" ")
        if len(split) == 1:
            return models.Case(int(split[0])).questions  # type: ignore[no-untyped-call]
        elif split[1] == "":
            # Preposition before escaped case
            #
            # prep !case
            # ^^^^^
            # notice that last symbol is a space, but it was deleted by split
            logger.trace("Found preposition before escaped case.")
            return preposition_and_case

        preposition, case = split
        return f"{preposition} {models.Case(int(case)).questions}"  # type: ignore[no-untyped-call]
