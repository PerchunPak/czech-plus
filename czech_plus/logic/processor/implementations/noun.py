"""Module for implementing processing nouns."""
from czech_plus._vendor.loguru import logger

from czech_plus import models
from czech_plus.logic.lexer import NounLexer, tokens
from czech_plus.logic.processor.implementations import BaseProcessor


class NounProcessor(BaseProcessor):
    """Noun processor."""

    def __init__(self) -> None:
        super().__init__()

        self.__czech_field_name = self._config.cards.nouns.fields.czech
        self.__gender_field_name = self._config.cards.nouns.fields.gender

    def process(self, content: dict[str, str], /) -> str:
        """Process the content.

        Args:
            content: Card fields inside dict.

        Returns:
            The processed ``czech`` field, ready to be inserted into the card.
        """
        logger.trace(
            f"Parsing noun card\n"
            f"{self.__czech_field_name} (Czech field): {content[self.__czech_field_name]}\n"
            f"{self.__gender_field_name} (Gender field): {content[self.__gender_field_name]}"
        )
        if not content[self.__gender_field_name]:
            logger.warning(f"Gender field is empty, skipping. Czech field: {content[self.__czech_field_name]}")
            return content[self.__czech_field_name]

        lexer = NounLexer()
        lexed_czech = self._navigate_over(lexer.lex(content[self.__czech_field_name]))
        lexed_gender = self._navigate_over(lexer.lex(content[self.__gender_field_name]))

        result = ""
        for token_or_string in lexed_czech:
            gender = next(lexed_gender)
            logger.trace(f"{token_or_string=} {gender=}")

            if isinstance(gender, tokens.SeparatorToken):
                assert isinstance(token_or_string, tokens.SeparatorToken)
                result += ", "
            elif isinstance(gender, tokens.SkipToken):
                assert isinstance(token_or_string, str)
                result += token_or_string
            elif isinstance(gender, str):
                assert isinstance(token_or_string, str)
                result += f"{models.Gender[gender].value} {token_or_string}"
            else:  # pragma: no cover
                raise NotImplementedError("We don't support other scenarios here.")

        return result
