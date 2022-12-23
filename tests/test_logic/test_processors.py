"""Tests for :mod:`czech_plus.logic.processors` package."""
import abc
import typing as t

import pytest
import typing_extensions as te
from faker import Faker
from pytest_mock import MockerFixture

from czech_plus import models
from czech_plus.logic.lexer import tokens
from czech_plus.logic.processor import get_processor, process_card
from czech_plus.logic.processor.implementations.adjective import (
    AdjectiveProcessor,
)
from czech_plus.logic.processor.implementations.base import BaseProcessor
from czech_plus.logic.processor.implementations.noun import NounProcessor
from czech_plus.logic.processor.implementations.verb import VerbProcessor

_GENERATOR: te.TypeAlias = t.Iterator[t.Union[str, tokens.BaseToken]]


@pytest.mark.parametrize(
    "note_type_name,expected",
    [
        ("nouns", NounProcessor),
        ("verbs", VerbProcessor),
        ("adjectives", AdjectiveProcessor),
    ],
)
def test_get_processor(  # type: ignore[misc]
    note_type_name: str, expected: type[BaseProcessor], mock_config: t.Callable[[str, t.Any], None], faker: Faker
) -> None:
    """Test for :func:`czech_plus.logic.processor.get_processor`."""
    mock_config(f"cards.{note_type_name}.note_type_name", (value := faker.word()))
    assert type(get_processor(value)) is expected


def test_get_processor_not_found(faker: Faker) -> None:
    """Test for :func:`czech_plus.logic.processor.get_processor` with invalid note type name."""
    assert get_processor(faker.word()) is None


def test_process_card(mocker: MockerFixture, faker: Faker) -> None:
    """Tests :func:`czech_plus.logic.processor.process_card`."""
    mock_processor = mocker.patch("czech_plus.logic.processor.get_processor")
    mock_processor.return_value.process.return_value = (value := faker.word())
    assert process_card({faker.word(): faker.word()}, faker.word()) == value


def test_process_card_but_processor_not_found(mocker: MockerFixture, faker: Faker) -> None:
    """Tests :func:`czech_plus.logic.processor.process_card` when processor wasn't found."""
    mock_processor = mocker.patch("czech_plus.logic.processor.get_processor")
    mock_processor.return_value.process.return_value = None
    assert process_card({faker.word(): faker.word()}, faker.word()) is None


class BaseTestProcessor(abc.ABC):
    """Base class for tests of processors."""

    @pytest.fixture(scope="class")
    def faker(self) -> Faker:
        """Translate faker to Czech."""
        return Faker("cs_CZ")

    @abc.abstractmethod
    def processor(self, faker: Faker) -> BaseProcessor:
        """Fixture for initialised processor."""

    @abc.abstractmethod
    def second_field_name(self) -> str:
        """Fixture for second field name (like gender)."""

    def test_navigate_over(self, processor: BaseProcessor, faker: Faker) -> None:
        r"""Basic test for :meth:`~czech_plus.logic.processor.BaseProcessor._navigate_over`\ ."""
        word = faker.word()

        def stub() -> _GENERATOR:
            yield word

        assert list(processor._navigate_over(stub())) == [word]

    def test_navigate_over_skips_escaped_token(self, processor: BaseProcessor, faker: Faker) -> None:
        """Tests that :meth:`~czech_plus.logic.processor.BaseProcessor._navigate_over` skips escaped tokens."""
        word = faker.word()

        def stub() -> _GENERATOR:
            yield tokens.EscapedToken(word)

        assert list(processor._navigate_over(stub())) == [word]

    def test_navigate_over_dont_skip_escaped_token(self, processor: BaseProcessor, faker: Faker) -> None:
        """Tests that :meth:`~czech_plus.logic.processor.BaseProcessor._navigate_over` doesn't skip escaped tokens, \
        if ``dont_skip_escaped`` is :obj:`True:\\ ."""  # noqa: D301 # Use r""" if any backslashes in a docstring
        word = faker.word()

        def stub() -> _GENERATOR:
            yield tokens.EscapedToken(word)

        assert list(processor._navigate_over(stub(), dont_skip_escaped=True)) == [tokens.EscapedToken(word)]

    def test_navigate_over_dont_skip_escaped_token_and_first_word(self, processor: BaseProcessor, faker: Faker) -> None:
        """Tests that :meth:`~czech_plus.logic.processor.BaseProcessor._navigate_over` doesn't skip escaped tokens, \
        and word before was yielded."""
        word1, word2 = faker.word(), faker.word()

        def stub() -> _GENERATOR:
            yield word1
            yield tokens.EscapedToken(word2)

        assert list(processor._navigate_over(stub(), dont_skip_escaped=True)) == [word1, tokens.EscapedToken(word2)]

    def test_navigate_over_with_token(self, processor: BaseProcessor) -> None:
        """Tests that :meth:`~czech_plus.logic.processor.BaseProcessor._navigate_over` yields exact the same token."""
        token = tokens.BaseToken()

        def stub() -> _GENERATOR:
            yield token

        result = list(processor._navigate_over(stub(), dont_skip_escaped=True))
        assert result == [token]
        assert result[0] is token

    def test_navigate_over_with_token_and_first_word(self, processor: BaseProcessor, faker: Faker) -> None:
        """Tests that :meth:`~czech_plus.logic.processor.BaseProcessor._navigate_over` yields exact the same token, \
        when firstly word was given."""
        token, word = tokens.BaseToken(), faker.word()

        def stub() -> _GENERATOR:
            yield word
            yield token

        result = list(processor._navigate_over(stub(), dont_skip_escaped=True))
        assert result == [word, token]
        assert result[1] is token

    def test_return_czech_field_if_second_field_is_empty(
        self, czech_field_name: str, second_field_name: str, processor: BaseProcessor
    ) -> None:
        """Tests that :meth:`~czech_plus.logic.processor.BaseProcessor.process` \
        returns czech field, if second field is empty."""
        assert processor.process({czech_field_name: (czech := object()), second_field_name: ""}) == czech  # type: ignore[dict-item] # object as a value


class TestNounProcessor(BaseTestProcessor):
    """Tests for :class:`~czech_plus.logic.processor.implementations.noun.NounProcessor`."""

    @pytest.fixture
    def czech_field_name(self, faker: Faker) -> str:
        """Fixture for czech field name."""
        return t.cast(str, faker.word())

    @pytest.fixture
    def gender_field_name(self, faker: Faker) -> str:
        """Fixture for gender field name."""
        return t.cast(str, faker.word())

    @pytest.fixture
    def second_field_name(self, gender_field_name: str) -> str:  # type: ignore[override]
        """Proxy to ``gender_field_name``."""
        return gender_field_name

    @pytest.fixture
    def processor(self, faker: Faker) -> NounProcessor:
        """Fixture for initialised noun processor."""
        return NounProcessor()

    @pytest.fixture(autouse=True)
    def _mock_processor(
        self, processor: NounProcessor, czech_field_name: str, gender_field_name: str, mocker: MockerFixture
    ) -> None:
        """Mock processor's fields."""
        mocker.patch.object(processor, "_NounProcessor__czech_field_name", czech_field_name)
        mocker.patch.object(processor, "_NounProcessor__gender_field_name", gender_field_name)

    @pytest.mark.parametrize("gender", list(models.Gender))
    def test_gender_correct(
        self,
        gender: models.Gender,
        processor: NounProcessor,
        czech_field_name: str,
        gender_field_name: str,
        faker: Faker,
    ) -> None:
        """Tests processing with correct gender."""
        assert (
            processor.process(
                {czech_field_name: (word := faker.word()), gender_field_name: gender.name},
            )
            == f"{gender.value} {word}"
        )

    def test_skipped_gender(
        self, processor: NounProcessor, czech_field_name: str, gender_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with skipped gender."""
        assert (
            processor.process(
                {
                    czech_field_name: (word := faker.word()),
                    gender_field_name: "_",
                },
            )
            == word
        )

    def test_genders_with_few_words(
        self, processor: NounProcessor, czech_field_name: str, gender_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few words."""
        words = [faker.word() for _ in range(faker.pyint(2, 5))]
        genders = [faker.enum(models.Gender) for _ in range(len(words))]

        result = ""
        for i in range(len(words)):
            result += f"{genders[i].value} {words[i]}, "
        result = result[:-2]

        assert (
            processor.process(
                {czech_field_name: ", ".join(words), gender_field_name: ", ".join(gender.name for gender in genders)}
            )
            == result
        )

    @pytest.mark.parametrize("skip_position", ["0", "1", "len(words) - 1"])
    def test_skipped_gender_with_few_words(
        self, skip_position: str, processor: NounProcessor, czech_field_name: str, gender_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few words and one skipped gender."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]
        genders = [faker.enum(models.Gender) for _ in range(len(words))]
        eval_skip_position = eval(skip_position, {"words": words})

        result = ""
        for i in range(len(words)):
            if i == eval_skip_position:
                result += words[i] + ", "
                continue
            result += f"{genders[i].value} {words[i]}, "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    gender_field_name: ", ".join(
                        gender.name if i != eval_skip_position else "_" for i, gender in enumerate(genders)
                    ),
                }
            )
            == result
        )


class TestVerbProcessor(BaseTestProcessor):
    """Tests for :class:`~czech_plus.logic.processor.implementations.verb.VerbProcessor`."""

    @pytest.fixture
    def czech_field_name(self, faker: Faker) -> str:
        """Fixture for czech field name."""
        return t.cast(str, faker.word())

    @pytest.fixture
    def pac_field_name(self, faker: Faker) -> str:
        """Fixture for prepositions and cases field name."""
        return t.cast(str, faker.word())

    @pytest.fixture
    def second_field_name(self, pac_field_name: str) -> str:  # type: ignore[override]
        """Proxy to ``pac_field_name``."""
        return pac_field_name

    @pytest.fixture
    def processor(self, faker: Faker) -> VerbProcessor:
        """Fixture for initialised verb processor."""
        return VerbProcessor()

    @pytest.fixture(autouse=True)
    def _mock_processor(
        self, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, mocker: MockerFixture
    ) -> None:
        """Mock processor's fields."""
        mocker.patch.object(processor, "_VerbProcessor__czech_field_name", czech_field_name)
        mocker.patch.object(processor, "_VerbProcessor__pac_field_name", pac_field_name)

    def test_pac_correct(
        self, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with correct preposition and case."""
        preposition, case, word = faker.word(), faker.enum(models.Case), faker.word()
        assert (
            processor.process({czech_field_name: word, pac_field_name: f"{preposition} {case.number}"})
            == f"{word} ({preposition} {case.questions})"
        )

    def test_case_correct(
        self, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with correct case but without preposition."""
        case, word = faker.enum(models.Case), faker.word()
        assert (
            processor.process({czech_field_name: word, pac_field_name: f"{case.number}"})
            == f"{word} ({case.questions})"
        )

    def test_skipped_pac(
        self, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with skipped preposition and case."""
        assert (
            processor.process(
                {czech_field_name: (word := faker.word()), pac_field_name: "_"},
            )
            == word
        )

    def test_pacs_with_few_words(
        self, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few words."""
        words = [faker.word() for _ in range(faker.pyint(2, 5))]
        prepositions = [faker.word() for _ in range(len(words))]
        cases: list[models.Case] = [faker.enum(models.Case) for _ in range(len(words))]

        result = ""
        for i in range(len(words)):
            result += f"{words[i]} ({prepositions[i]} {cases[i].questions}), "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    pac_field_name: ". ".join(f"{prepositions[i]} {cases[i].number}" for i in range(len(words))),
                }
            )
            == result
        )

    @pytest.mark.parametrize("skip_position", ["0", "1", "len(words) - 1"])
    def test_skipped_pac_with_few_words(
        self, skip_position: str, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few words and one skipped preposition and case."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]
        prepositions = [faker.word() for _ in range(len(words))]
        cases: list[models.Case] = [faker.enum(models.Case) for _ in range(len(words))]
        eval_skip_position = eval(skip_position, {"words": words})

        result = ""
        for i in range(len(words)):
            if i == eval_skip_position:
                result += f"{words[i]}, "
                continue
            result += f"{words[i]} ({prepositions[i]} {cases[i].questions}), "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    pac_field_name: ". ".join(
                        f"{prepositions[i]} {cases[i].number}" if i != eval_skip_position else "_"
                        for i in range(len(words))
                    ),
                }
            )
            == result
        )

    def test_cases_with_few_words(
        self, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few words and without prepositions."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]
        cases: list[models.Case] = [faker.enum(models.Case) for _ in range(len(words))]

        result = ""
        for i in range(len(words)):
            result += f"{words[i]} ({cases[i].questions}), "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    pac_field_name: ". ".join(f"{cases[i].number}" for i in range(len(words))),
                }
            )
            == result
        )

    @pytest.mark.parametrize("skip_position", ["0", "1", "len(words) - 1"])
    def test_skipped_cases_with_few_words(
        self, skip_position: str, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few words and one skipped case."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]
        cases: list[models.Case] = [faker.enum(models.Case) for _ in range(len(words))]
        eval_skip_position = eval(skip_position, {"words": words})

        result = ""
        for i in range(len(words)):
            if i == eval_skip_position:
                result += f"{words[i]}, "
                continue
            result += f"{words[i]} ({cases[i].questions}), "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    pac_field_name: ". ".join(
                        str(cases[i].number) if i != eval_skip_position else "_" for i in range(len(words))
                    ),
                }
            )
            == result
        )

    @pytest.mark.parametrize("words_count", ["1", "faker.pyint(2, 5)"])
    def test_multiple_pacs_for_one_word(
        self, words_count: str, processor: VerbProcessor, czech_field_name: str, pac_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with multiple prepositions and cases for one word."""
        words = [faker.word() for _ in range(eval(words_count, {"faker": faker}))]
        words_to_pacs: dict[str, list[tuple[str, models.Case]]] = {}
        for word in words:
            words_to_pacs[word] = [(faker.word(), faker.enum(models.Case)) for _ in range(faker.pyint(1, 5))]

        input_pacs: list[str] = []
        result: list[str] = []
        for i in range(len(words)):
            temp_input_pacs = ""
            temp_result = ""

            for preposition, case in words_to_pacs[words[i]]:
                temp_result += f"{preposition} {case.questions}, "
                temp_input_pacs += f"{preposition} {case.number}, "

            result.append(f"{words[i]} ({temp_result[:-2]})")
            input_pacs.append(temp_input_pacs[:-2])

        assert processor.process(
            {
                czech_field_name: ", ".join(words),
                pac_field_name: ". ".join(input_pacs),
            }
        ) == ", ".join(result)

    @pytest.mark.parametrize("custom_question_position", ["0", "1", "len(words) - 1"])
    def test_custom_case_question(
        self,
        custom_question_position: str,
        processor: VerbProcessor,
        czech_field_name: str,
        pac_field_name: str,
        faker: Faker,
    ) -> None:
        """Tests processing with custom case question."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]

        eval_custom_question_position = eval(custom_question_position, {"words": words})
        prepositions = [faker.word() for _ in range(len(words))]
        cases: list[t.Union[models.Case, str]] = [
            faker.enum(models.Case) if i != eval_custom_question_position else "!" + faker.word()
            for i in range(len(words))
        ]

        result = ""
        for i in range(len(words)):
            result += (
                f"{words[i]} ({prepositions[i]} "
                f"{cases[i].questions if isinstance(cases[i], models.Case) else cases[i].lstrip('!')}), "  # type: ignore[union-attr] # mypy ignores `isinstance`
            )
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    pac_field_name: ". ".join(
                        f"{prepositions[i]} {cases[i].number if isinstance(cases[i], models.Case) else cases[i]}"  # type: ignore[union-attr] # mypy ignores `isinstance`
                        for i in range(len(words))
                    ),
                }
            )
            == result
        )

    @pytest.mark.parametrize("custom_question_position", ["0", "1", "len(words) - 1"])
    def test_custom_case_question_without_prepositions(
        self,
        custom_question_position: str,
        processor: VerbProcessor,
        czech_field_name: str,
        pac_field_name: str,
        faker: Faker,
    ) -> None:
        """Tests processing with custom case question without prepositions."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]

        eval_custom_question_position = eval(custom_question_position, {"words": words})
        cases: list[t.Union[models.Case, str]] = [
            faker.enum(models.Case) if i != eval_custom_question_position else "!" + faker.word()
            for i in range(len(words))
        ]

        result = ""
        for i in range(len(words)):
            result += f"{words[i]} ({cases[i].questions if isinstance(cases[i], models.Case) else cases[i].lstrip('!')}), "  # type: ignore[union-attr] # mypy ignores `isinstance`
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    pac_field_name: ". ".join(
                        str(cases[i].number) if isinstance(cases[i], models.Case) else cases[i]  # type: ignore[union-attr,misc] # mypy ignores `isinstance`
                        for i in range(len(words))
                    ),
                }
            )
            == result
        )

    @pytest.mark.parametrize("position", ["1", "len(words) - 1"])
    def test_future_form(
        self,
        position: str,
        processor: VerbProcessor,
        czech_field_name: str,
        pac_field_name: str,
        faker: Faker,
    ) -> None:
        """Tests processing with future form."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]
        prepositions = [faker.word() for _ in range(len(words))]
        cases: list[models.Case] = [faker.enum(models.Case) for _ in range(len(words))]
        eval_position = eval(position, {"words": words})

        czech_input = ""
        pac_input = ""
        result = ""

        for i in range(len(words)):
            if i == eval_position:
                czech_input += f" [{words[i]}]"
                pac_input += f" [{prepositions[i]} {cases[i].number}]"
                result += f" [{words[i]} ({prepositions[i]} {cases[i].questions})]"
                continue
            czech_input += f", {words[i]}"
            pac_input += f". {prepositions[i]} {cases[i].number}"
            result += f", {words[i]} ({prepositions[i]} {cases[i].questions})"

        czech_input = czech_input.lstrip(", ")
        pac_input = pac_input.lstrip(". ")
        result = result.lstrip(", ")

        assert processor.process({czech_field_name: czech_input, pac_field_name: pac_input}) == result

    @pytest.mark.parametrize("words_count", ["2", "faker.pyint(3, 5)"])
    @pytest.mark.parametrize("position", ["1", "len(words) - 1"])
    def test_multiple_pacs_for_one_word_in_future_form(
        self,
        words_count: str,
        position: str,
        processor: VerbProcessor,
        czech_field_name: str,
        pac_field_name: str,
        faker: Faker,
    ) -> None:
        """Tests processing with multiple pacs for one word in future form."""
        words = [faker.word() for _ in range(eval(words_count, {"faker": faker}))]
        words_to_pacs: dict[str, list[tuple[str, models.Case]]] = {}
        for word in words:
            words_to_pacs[word] = [(faker.word(), faker.enum(models.Case)) for _ in range(faker.pyint(1, 5))]
        eval_position = eval(position, {"words": words})

        czech_input = ""
        pac_input = ""
        result = ""

        for i in range(len(words)):
            if i == eval_position:
                czech_input += f" [{words[i]}]"
                pac_input += " ["
                result += f" [{words[i]} ("

                for preposition, case in words_to_pacs[words[i]]:
                    pac_input += f"{preposition} {case.number}, "
                    result += f"{preposition} {case.questions}, "

                pac_input = pac_input.rstrip(", ") + "]"
                result = result.rstrip(", ") + ")]"
                continue

            czech_input += f", {words[i]}"
            pac_input += ". "
            result += f", {words[i]} ("
            for preposition, case in words_to_pacs[words[i]]:
                pac_input += f"{preposition} {case.number}, "
                result += f"{preposition} {case.questions}, "
            pac_input = pac_input.strip(", ")
            result = result.rstrip(", ") + ")"

        czech_input = czech_input.lstrip(", ")
        pac_input = pac_input.lstrip(". ")
        result = result.lstrip(", ")

        assert processor.process({czech_field_name: czech_input, pac_field_name: pac_input}) == result

    def test_navigate_over_with_future_form(self, processor: BaseProcessor, faker: Faker) -> None:
        """Tests navigate over with future form."""
        word = faker.word()

        def another_stub() -> _GENERATOR:
            yield word

        def stub() -> _GENERATOR:
            yield tokens.FutureFormToken(another_stub())

        result = list(processor._navigate_over(stub()))
        assert len(result) == 1
        assert isinstance(result[0], tokens.FutureFormToken)
        assert list(result[0].content) == [word]

    def test_navigate_over_with_future_form_and_first_word(self, processor: BaseProcessor, faker: Faker) -> None:
        """Tests navigate over with future form and word yielded before."""
        word1, word2 = faker.word(), faker.word()

        def another_stub() -> _GENERATOR:
            yield word2

        def stub() -> _GENERATOR:
            yield word1
            yield tokens.FutureFormToken(another_stub())

        result = list(processor._navigate_over(stub()))
        assert len(result) == 2
        assert result[0] == word1
        assert isinstance(result[1], tokens.FutureFormToken)
        assert list(result[1].content) == [word2]


class TestAdjectiveProcessor(BaseTestProcessor):
    """Tests for :class:`~czech_plus.logic.processor.implementations.adjective.AdjectiveProcessor`."""

    @pytest.fixture
    def czech_field_name(self, faker: Faker) -> str:
        """Fixture for czech field name."""
        return t.cast(str, faker.word())

    @pytest.fixture
    def cocd_field_name(self, faker: Faker) -> str:
        """Fixture for cocd field name."""
        return t.cast(str, faker.word())

    @pytest.fixture
    def second_field_name(self, cocd_field_name: str) -> str:  # type: ignore[override]
        """Proxy to ``cocd_field_name``."""
        return cocd_field_name

    @pytest.fixture
    def processor(self, faker: Faker) -> AdjectiveProcessor:
        """Fixture for initialised adjective processor."""
        return AdjectiveProcessor()

    @pytest.fixture(autouse=True)
    def _mock_processor(
        self, processor: AdjectiveProcessor, czech_field_name: str, cocd_field_name: str, mocker: MockerFixture
    ) -> None:
        """Mocks processor's fields."""
        mocker.patch.object(processor, "_AdjectiveProcessor__czech_field_name", czech_field_name)
        mocker.patch.object(processor, "_AdjectiveProcessor__cocd_field_name", cocd_field_name)

    def test_with_cocd(
        self, processor: AdjectiveProcessor, czech_field_name: str, cocd_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with valid Completion of Comparison Degrees."""
        assert (
            processor.process(
                {
                    czech_field_name: (word := faker.word()),
                    cocd_field_name: (cocd := faker.word()),
                }
            )
            == f"{word} ({cocd})"
        )

    def test_skipped_cocd(
        self, processor: AdjectiveProcessor, czech_field_name: str, cocd_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with skipped Completion of Comparison Degrees."""
        assert (
            processor.process(
                {
                    czech_field_name: (word := faker.word()),
                    cocd_field_name: "_",
                }
            )
            == word
        )

    def test_cocd_with_few_words(
        self, processor: AdjectiveProcessor, czech_field_name: str, cocd_field_name: str, faker: Faker
    ) -> None:
        """Tests processing with few valid Completions of Comparison Degrees and few words."""
        words = [faker.word() for _ in range(faker.pyint(2, 5))]
        cocds = [faker.word() for _ in range(len(words))]

        result = ""
        for i in range(len(words)):
            result += f"{words[i]} ({cocds[i]}), "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    cocd_field_name: ", ".join(cocd for cocd in cocds),
                }
            )
            == result
        )

    @pytest.mark.parametrize("skip_position", ["0", "1", "len(words) - 1"])
    def test_skipped_cocd_with_few_words(
        self,
        skip_position: str,
        processor: AdjectiveProcessor,
        czech_field_name: str,
        cocd_field_name: str,
        faker: Faker,
    ) -> None:
        """Tests processing with one skipped Completion of Comparison Degrees and few words."""
        words = [faker.word() for _ in range(faker.pyint(3, 5))]
        cocds = [faker.word() for _ in range(len(words))]
        eval_skip_position = eval(skip_position, {"words": words})

        result = ""
        for i in range(len(words)):
            if i == eval_skip_position:
                result += words[i] + ", "
                continue
            result += f"{words[i]} ({cocds[i]}), "
        result = result[:-2]

        assert (
            processor.process(
                {
                    czech_field_name: ", ".join(words),
                    cocd_field_name: ", ".join(
                        cocd if i != eval_skip_position else "_" for i, cocd in enumerate(cocds)
                    ),
                }
            )
            == result
        )
