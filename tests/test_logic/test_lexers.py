"""Tests for lexer (:mod:`czech_plus.logic.lexer` package)."""
import typing as t
from collections.abc import Callable

import pytest
from faker import Faker

from czech_plus.logic import lexer
from czech_plus.logic.lexer import tokens

_ANY_LEXER = [lexer.BaseLexer, lexer.NounLexer, lexer.VerbLexer, lexer.AdjectiveLexer]
_ANY_LEXER_EXCEPT_VERB = [lexer.BaseLexer, lexer.NounLexer, lexer.AdjectiveLexer]


class __BaseGenerator:
    __cz_faker = Faker("cs_CZ")

    def __init__(self, __method: str, *__args, **__kwargs) -> None:
        self.__method: Callable[[t.Any], str] = getattr(self.__cz_faker, __method)  # type: ignore[misc] # Explicit Any
        self.__args, self.__kwargs = __args, __kwargs
        self.__vault: dict[int, str] = {}

    def __getitem__(self, key: int) -> str:
        if (item := self.__vault.get(key)) is not None:
            return item
        value = self.__method(*self.__args, **self.__kwargs)
        self.__vault[key] = value
        return value


__sentence_gen = __BaseGenerator("sentence")
__word_gen = __BaseGenerator("word")
__symbol_gen = __BaseGenerator("pystr", 1, 1)


@pytest.mark.parametrize(
    "classes_to_test,input,output",
    [
        (_ANY_LEXER, f"\\{__symbol_gen[1]}", [tokens.EscapedToken(__symbol_gen[1])]),
        (_ANY_LEXER, f"!{__word_gen[1]}", [tokens.EscapedToken(__word_gen[1])]),
        (
            _ANY_LEXER,
            f"!{__word_gen[2]}, {__word_gen[3]}",
            [tokens.EscapedToken(__word_gen[2]), tokens.SeparatorToken(), __word_gen[3]],
        ),
        (
            _ANY_LEXER,
            f"{__word_gen[4]}, !{__word_gen[5]}, {__word_gen[6]}",
            [
                __word_gen[4],
                tokens.SeparatorToken(),
                tokens.EscapedToken(__word_gen[5]),
                tokens.SeparatorToken(),
                __word_gen[6],
            ],
        ),
        (
            _ANY_LEXER,
            f"{__word_gen[7]}\\, {__word_gen[8]}",
            [__word_gen[7], tokens.EscapedToken(","), f" {__word_gen[8]}"],
        ),
        (_ANY_LEXER, f"{__word_gen[9]}, {__word_gen[10]}", [__word_gen[9], tokens.SeparatorToken(), __word_gen[10]]),
        (
            [lexer.VerbLexer],
            f"{__word_gen[11]}, {__word_gen[12]}. {__word_gen[13]}",
            [
                __word_gen[11],
                tokens.AdditionalSeparatorToken(),
                __word_gen[12],
                tokens.SeparatorToken(),
                __word_gen[13],
            ],
        ),
        (_ANY_LEXER, "_", [tokens.SkipToken()]),
        (
            _ANY_LEXER,
            f"{__word_gen[14]}, _, {__word_gen[15]}",
            [__word_gen[14], tokens.SeparatorToken(), tokens.SkipToken(), tokens.SeparatorToken(), __word_gen[15]],
        ),
        ([lexer.VerbLexer], f"[{__word_gen[15]}]", [tokens.FutureFormToken(__word_gen[15])]),
        (
            [lexer.VerbLexer],
            f"{__word_gen[16]} [{__word_gen[17]}]",
            [__word_gen[16], tokens.FutureFormToken(__word_gen[17])],
        ),
        (
            [lexer.VerbLexer],
            f"{__word_gen[18]} [{__word_gen[19]}]. {__word_gen[20]}",
            [__word_gen[18], tokens.FutureFormToken(__word_gen[19]), tokens.SeparatorToken(), __word_gen[20]],
        ),
        (
            [lexer.VerbLexer],
            f"{__word_gen[21]} [{__word_gen[22]}]. {__word_gen[23]} [{__word_gen[24]}]",
            [
                __word_gen[21],
                tokens.FutureFormToken(__word_gen[22]),
                tokens.SeparatorToken(),
                __word_gen[23],
                tokens.FutureFormToken(__word_gen[24]),
            ],
        ),
        (
            [lexer.VerbLexer],
            f"{__word_gen[25]} [{__word_gen[26]}] [{__word_gen[27]}]",
            [__word_gen[25], tokens.FutureFormToken(__word_gen[26]), tokens.FutureFormToken(__word_gen[27])],
        ),
        (_ANY_LEXER, "\\", [tokens.EscapedToken("")]),
        ([lexer.VerbLexer], "[", [tokens.FutureFormToken("")]),
        # real examples from my vocabulary
        (_ANY_LEXER, "blůza, halenka", ["blůza", tokens.SeparatorToken(), "halenka"]),
        ([lexer.VerbLexer], "ušklíbat se [ušklíbnout se]", ["ušklíbat se", tokens.FutureFormToken("ušklíbnout se")]),
    ],
)
def test_with_examples(
    classes_to_test: list[type[lexer.BaseLexer]], input: str, output: list[t.Union[tokens.BaseToken, str]], faker: Faker
) -> None:
    """Test lexers with examples, instead of unit testing."""
    for class_to_test in classes_to_test:
        if (
            class_to_test is lexer.VerbLexer
            and classes_to_test is _ANY_LEXER
            and len(tuple(filter(lambda el: isinstance(el, tokens.SeparatorToken), output)))
        ):
            parsed_output = list(
                map(
                    lambda val: tokens.AdditionalSeparatorToken() if isinstance(val, tokens.SeparatorToken) else val,
                    output,
                )
            )
        else:
            parsed_output = output

        assert list(class_to_test({faker.word(): input}).lex()) == parsed_output


@pytest.mark.parametrize(
    "classes_to_test,input,output",
    [
        (
            [lexer.VerbLexer],
            f"{__word_gen[28]} [{__word_gen[29]}\\], {__word_gen[30]}",
            [__word_gen[28], tokens.FutureFormToken(f"{__word_gen[29]}], {__word_gen[30]}")],
        ),
        (_ANY_LEXER, f"\\!{__sentence_gen[1][:-1]}!!", [tokens.EscapedToken("!"), f"{__sentence_gen[1][:-1]}!!"]),
        (
            _ANY_LEXER,
            f"{__word_gen[31]}, !{__word_gen[32]}\\, {__word_gen[33]}",
            [__word_gen[31], tokens.EscapedToken(f"{__word_gen[32]}, {__word_gen[33]}")],
        ),
        (
            _ANY_LEXER,
            f"{__word_gen[34]}, !{__word_gen[35]}\\,",
            [__word_gen[34], tokens.EscapedToken(f"{__word_gen[35]},")],
        ),
        (
            [lexer.VerbLexer],
            f"{__word_gen[36]} [{__word_gen[37]}\\]",
            [__word_gen[36], tokens.FutureFormToken(f"{__word_gen[37]}]")],
        ),
    ],
)
def test_with_unsupported_examples(
    classes_to_test: list[type[lexer.BaseLexer]], input: str, output: list[t.Union[tokens.BaseToken, str]], faker: Faker
) -> None:
    """Tests unsupported examples, but possible future features.

    If this test fails, just move parametrize entry to `test_with_examples`.
    """
    for class_to_test in classes_to_test:
        assert list(class_to_test({faker.word(): input}).lex()) != output
