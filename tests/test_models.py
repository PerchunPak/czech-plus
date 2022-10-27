"""It can be strange, but some code in our models require tests."""
import pytest

from czech_plus import models

_CASE_TO_QUESTION = {
    models.Case.nominative: "kdo? co?",
    models.Case.genitive: "koho? čeho?",
    models.Case.dative: "komu? čemu?",
    models.Case.accusative: "koho? co?",
    models.Case.vocative: "voláme",
    models.Case.locative: "kom? čem?",
    models.Case.instrumental: "kým? čím?",
}
_CASE_TO_NUMBER = {
    models.Case.nominative: 1,
    models.Case.genitive: 2,
    models.Case.dative: 3,
    models.Case.accusative: 4,
    models.Case.vocative: 5,
    models.Case.locative: 6,
    models.Case.instrumental: 7,
}


@pytest.mark.parametrize("case", models.Case)
def test_case_enum_gives_correct_value(case):
    """Tests that :class:`czech.models.Case`.value returns question, not a tuple/number."""
    assert case.value == _CASE_TO_QUESTION[case]


@pytest.mark.parametrize("case", models.Case)
def test_case_get_by_number(case):
    """Tests that a case number can be used as an alias in :class:`czech.models.Case`."""
    assert models.Case(_CASE_TO_NUMBER[case]) == case  # type: ignore[no-untyped-call]
