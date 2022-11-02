"""Module with some factories used in tests."""
import typing

import factory.fuzzy
import faker as faker_package

from czech_plus import models

faker = faker_package.Faker()


class NounWordFactory(factory.Factory):
    """Factory for :class:`~czech.models.NounWord` model."""

    class Meta:  # noqa: D106
        model = models.NounWord

    czech: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    gender: models.Gender = factory.fuzzy.FuzzyAttribute(lambda: faker.enum(models.Gender))
    translation: str = factory.fuzzy.FuzzyAttribute(faker.pystr)


class VerbWordFactory(factory.Factory):
    """Factory for :class:`~czech.models.VerbWord` model."""

    class Meta:  # noqa: D106
        model = models.VerbWord

    czech: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    preposition_and_case: list[tuple[typing.Optional[str], models.Case]] = None  # type: ignore[assignment] # will be set in _create
    translation: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    future_form: bool = factory.fuzzy.FuzzyAttribute(faker.pybool)

    @classmethod
    def _create(cls, model_class, *args, _preposition_is_none: typing.Callable[[], bool] = faker.pybool, **kwargs: typing.Any) -> models.VerbWord:  # type: ignore[misc]
        kwargs["preposition_and_case"] = [
            (faker.pystr() if _preposition_is_none() is True else None, faker.enum(models.Case))
            for _ in range(faker.pyint(1, 5))
        ]
        return super()._create(model_class, *args, **kwargs)  # type: ignore[no-any-return]


class AdjectiveWordFactory(factory.Factory):
    """Factory for :class:`~czech.models.AdjectiveWord` model."""

    class Meta:  # noqa: D106
        model = models.AdjectiveWord

    czech: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    completion_of_comparison_degrees: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    translation: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
