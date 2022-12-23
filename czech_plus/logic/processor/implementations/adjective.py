"""Module for implementing processing adjectives."""
from czech_plus._vendor.loguru import logger

from czech_plus.logic.lexer import AdjectiveLexer, tokens
from czech_plus.logic.processor.implementations import BaseProcessor


class AdjectiveProcessor(BaseProcessor):
    """Class for processing adjectives."""

    def __init__(self) -> None:
        super().__init__()

        self.__czech_field_name = self._config.cards.adjectives.fields.czech
        self.__cocd_field_name = self._config.cards.adjectives.fields.completion_of_comparison_degrees

    def process(self, content: dict[str, str], /) -> str:
        """Process the content of the card.

        Args:
            content: The content of the card.

        Returns:
            The processed content.
        """
        logger.trace(
            f"Parsing adjective card\n"
            f"{self.__czech_field_name} (Czech field): {content[self.__czech_field_name]}\n"
            f"{self.__cocd_field_name} (CoCD field): {content[self.__cocd_field_name]}"
        )
        if not content[self.__cocd_field_name]:
            logger.warning(f"CoCD field is empty, skipping. Czech field: {content[self.__czech_field_name]}")
            return content[self.__czech_field_name]

        lexer = AdjectiveLexer()
        lexed_czech = self._navigate_over(lexer.lex(content[self.__czech_field_name]))
        lexed_cocd = self._navigate_over(lexer.lex(content[self.__cocd_field_name]))

        result = ""
        for token_or_string in lexed_czech:
            cocd = next(lexed_cocd)
            logger.trace(f"{token_or_string=} {cocd=}")

            if isinstance(cocd, tokens.SeparatorToken):
                assert isinstance(token_or_string, tokens.SeparatorToken)
                result += ", "
            elif isinstance(cocd, tokens.SkipToken):
                assert isinstance(token_or_string, str)
                result += token_or_string
            elif isinstance(cocd, str):
                assert isinstance(token_or_string, str)
                result += f"{token_or_string} ({cocd})"
            else:  # pragma: no cover
                raise NotImplementedError("We don't support other scenarios here.")

        return result
