"""Tests :mod:`czech.logic.processor.implementations` package."""
import pytest

from czech_plus import models
from czech_plus.logic.processor.implementations import adjective, noun, verb
from tests import factories


def _generate_parametrize_for_noun_testing() -> list[tuple[list[models.NounWord], list[str]]]:
    result: list[tuple[list[models.NounWord], list[str]]] = []
    for gender in models.Gender:
        word = factories.NounWordFactory(gender=gender)
        result.append(([word], [f"{gender.value} {word.czech}"]))

    return result


@pytest.mark.parametrize(
    "word",
    [factories.NounWordFactory(gender=gender) for gender in models.Gender],
)
def test_process_noun(word: models.NounWord) -> None:
    """Tests :func:`czech.logic.processor.implementations.noun.process`."""
    iterator = noun.process([word])
    result = next(iterator)

    assert result == f"{word.gender.value} {word.czech}"

    with pytest.raises(StopIteration):
        next(iterator)


@pytest.mark.parametrize("word", [factories.VerbWordFactory(_preposition_is_none=True), factories.VerbWordFactory()])
def test_process_verb(word: models.VerbWord) -> None:
    """Tests :func:`czech.logic.processor.implementations.verb.process`."""
    iterator = verb.process([word])
    result = next(iterator)

    prepositions_and_cases = ", ".join(
        f"{(preposition + ' ') if preposition is not None else ''}{case.value}"
        for preposition, case in word.preposition_and_case
    )
    assert result == f"{word.czech} ({prepositions_and_cases})"

    with pytest.raises(StopIteration):
        next(iterator)


@pytest.mark.parametrize(
    "word", [factories.AdjectiveWordFactory(), factories.AdjectiveWordFactory(completion_of_comparison_degrees=None)]
)
def test_process_adjective(word: models.AdjectiveWord) -> None:
    """Tests :func:`czech.logic.processor.implementations.adjective.process`."""
    iterator = adjective.process([word])
    result = next(iterator)

    assert result == f"{word.czech} ({word.completion_of_comparison_degrees})"

    with pytest.raises(StopIteration):
        next(iterator)
