"""Tests for lexer (:mod:`czech_plus.logic.lexer` package)."""
import typing as t

import pytest
from faker import Faker

from czech_plus.logic import lexer
from czech_plus.logic.lexer import tokens
from tests.test_logic import FakesGenerator

_ANY_LEXER = [lexer.BaseLexer, lexer.NounLexer, lexer.VerbLexer, lexer.AdjectiveLexer]
_ANY_LEXER_EXCEPT_VERB = [lexer.BaseLexer, lexer.NounLexer, lexer.AdjectiveLexer]


__sentence = FakesGenerator("sentence")
__word = FakesGenerator("word")
__symbol = FakesGenerator("pystr", 1, 1)


@pytest.mark.parametrize(
    "classes_to_test,input,output",
    [
        (_ANY_LEXER, f"\\{__symbol[1]}", [tokens.EscapedToken(__symbol[1])]),
        (_ANY_LEXER, f"!{__word[1]}", [tokens.EscapedToken(__word[1])]),
        (
            _ANY_LEXER,
            f"!{__word[2]}, {__word[3]}",
            [tokens.EscapedToken(__word[2]), tokens.SeparatorToken(), __word[3]],
        ),
        (
            _ANY_LEXER,
            f"{__word[4]}, !{__word[5]}, {__word[6]}",
            [
                __word[4],
                tokens.SeparatorToken(),
                tokens.EscapedToken(__word[5]),
                tokens.SeparatorToken(),
                __word[6],
            ],
        ),
        (
            _ANY_LEXER,
            f"{__word[7]}\\, {__word[8]}",
            [__word[7], tokens.EscapedToken(","), f" {__word[8]}"],
        ),
        (_ANY_LEXER, f"{__word[9]}, {__word[10]}", [__word[9], tokens.SeparatorToken(), __word[10]]),
        (
            [lexer.VerbLexer],
            f"{__word[11]}, {__word[12]}. {__word[13]}",
            [
                __word[11],
                tokens.AdditionalSeparatorToken(),
                __word[12],
                tokens.SeparatorToken(),
                __word[13],
            ],
        ),
        (_ANY_LEXER, "_", [tokens.SkipToken()]),
        (
            _ANY_LEXER,
            f"{__word[14]}, _, {__word[15]}",
            [__word[14], tokens.SeparatorToken(), tokens.SkipToken(), tokens.SeparatorToken(), __word[15]],
        ),
        (
            [lexer.VerbLexer],
            f"[{__word[15]}]",
            [tokens.FutureFormTokenStart(), __word[15], tokens.FutureFormTokenEnd()],
        ),
        (
            [lexer.VerbLexer],
            f"{__word[16]} [{__word[17]}]",
            [__word[16], tokens.FutureFormTokenStart(), __word[17], tokens.FutureFormTokenEnd()],
        ),
        (
            [lexer.VerbLexer],
            f"{__word[18]} [{__word[19]}]. {__word[20]}",
            [
                __word[18],
                tokens.FutureFormTokenStart(),
                __word[19],
                tokens.FutureFormTokenEnd(),
                tokens.SeparatorToken(),
                __word[20],
            ],
        ),
        (
            [lexer.VerbLexer],
            f"{__word[21]} [{__word[22]}]. {__word[23]} [{__word[24]}]",
            [
                __word[21],
                tokens.FutureFormTokenStart(),
                __word[22],
                tokens.FutureFormTokenEnd(),
                tokens.SeparatorToken(),
                __word[23],
                tokens.FutureFormTokenStart(),
                __word[24],
                tokens.FutureFormTokenEnd(),
            ],
        ),
        (
            [lexer.VerbLexer],
            f"[{__word[25]}. {__word[26]}]",
            [
                tokens.FutureFormTokenStart(),
                __word[25],
                tokens.SeparatorToken(),
                __word[26],
                tokens.FutureFormTokenEnd(),
            ],
        ),
        (
            [lexer.VerbLexer],
            f"[{__word[27]}, {__word[28]}]",
            [
                tokens.FutureFormTokenStart(),
                __word[27],
                tokens.AdditionalSeparatorToken(),
                __word[28],
                tokens.FutureFormTokenEnd(),
            ],
        ),
        (
            [lexer.VerbLexer],
            f"[{__word[29]}, {__word[30]}. {__word[31]}]",
            [
                tokens.FutureFormTokenStart(),
                __word[29],
                tokens.AdditionalSeparatorToken(),
                __word[30],
                tokens.SeparatorToken(),
                __word[31],
                tokens.FutureFormTokenEnd(),
            ],
        ),
        (_ANY_LEXER, "\\", [tokens.EscapedToken("")]),
        (_ANY_LEXER, f"{__word[32]} !{__word[33]}", [__word[32] + " ", tokens.EscapedToken(__word[33])]),
        ([lexer.VerbLexer], "[", [tokens.FutureFormTokenStart()]),
        ([lexer.VerbLexer], "]", [tokens.FutureFormTokenEnd()]),
        (
            [lexer.VerbLexer],
            f"[!{__word[34]}]",
            [tokens.FutureFormTokenStart(), tokens.EscapedToken(__word[34]), tokens.FutureFormTokenEnd()],
        ),
        # real examples from my vocabulary
        (_ANY_LEXER, "blůza, halenka", ["blůza", tokens.SeparatorToken(), "halenka"]),
        (
            [lexer.VerbLexer],
            "ušklíbat se [ušklíbnout se]",
            ["ušklíbat se", tokens.FutureFormTokenStart(), "ušklíbnout se", tokens.FutureFormTokenEnd()],
        ),
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

        assert parsed_output == list(class_to_test().lex(input))


@pytest.mark.parametrize(
    "classes_to_test,input,output",
    [
        (
            [lexer.VerbLexer],
            f"{__word[35]} [{__word[36]}\\]",
            [__word[35], tokens.FutureFormTokenStart(), f"{__word[36]}]", tokens.FutureFormTokenEnd()],
        ),
        (
            [lexer.VerbLexer],
            f"{__word[37]} [{__word[38]}\\], {__word[39]}",
            [__word[37], tokens.FutureFormTokenStart(), f"{__word[38]}], {__word[39]}", tokens.FutureFormTokenEnd()],
        ),
        (_ANY_LEXER, f"\\!{__sentence[1][:-1]}!!", [tokens.EscapedToken("!"), f"{__sentence[1][:-1]}!!"]),
        (
            _ANY_LEXER,
            f"{__word[40]}, !{__word[41]}\\, {__word[42]}",
            [__word[40], tokens.EscapedToken(f"{__word[41]}, {__word[42]}")],
        ),
        (
            _ANY_LEXER,
            f"{__word[43]}, !{__word[44]}\\,",
            [__word[43], tokens.EscapedToken(f"{__word[44]},")],
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
        assert list(class_to_test().lex(input)) != output
