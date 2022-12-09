"""Module with some factories used in tests."""
import typing as t

import factory.fuzzy
import faker as faker_package

from czech_plus import config, models

faker = faker_package.Faker()


class WordFactory(factory.Factory):
    """Factory for any subclass of :class:`~czech.models.BaseWord` model."""

    class Meta:  # noqa: D106
        model = models.BaseWord

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create random subclass of :class:`~czech.models.BaseWord` model."""
        return faker.random_element((NounWordFactory, VerbWordFactory, AdjectiveWordFactory))()


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
    preposition_and_case: list[tuple[t.Optional[str], models.Case]] = None  # type: ignore[assignment] # will be set in _create
    translation: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    future_form: bool = factory.fuzzy.FuzzyAttribute(faker.pybool)

    @classmethod
    def _create(cls, model_class, *args, _preposition_is_none: t.Callable[[], bool] = faker.pybool, **kwargs: t.Any) -> models.VerbWord:  # type: ignore[misc]
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
    cocd: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    translation: str = factory.fuzzy.FuzzyAttribute(faker.pystr)


class LogSettingsFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.LogSettings` class."""

    class Meta:  # noqa: D106
        model = config.LogSettings

    level: config.LogLevel = factory.fuzzy.FuzzyAttribute(lambda: faker.enum(config.LogLevel))
    json: bool = factory.fuzzy.FuzzyAttribute(faker.pybool)


class BaseCardFieldsFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.BaseCardFields` class."""

    class Meta:  # noqa: D106
        model = config.BaseCardFields

    czech: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    translation: str = factory.fuzzy.FuzzyAttribute(faker.pystr)


class NounCardFieldsFactory(BaseCardFieldsFactory):
    """Factory for :class:`~czech_plus.config.NounCardFields` class."""

    class Meta:  # noqa: D106
        model = config.NounCardFields

    gender: str = factory.fuzzy.FuzzyAttribute(faker.pystr)


class VerbCardFieldsFactory(BaseCardFieldsFactory):
    """Factory for :class:`~czech_plus.config.VerbCardFields` class."""

    class Meta:  # noqa: D106
        model = config.VerbCardFields

    prepositions_and_cases: str = factory.fuzzy.FuzzyAttribute(faker.pystr)


class AdjectiveCardFieldsFactory(BaseCardFieldsFactory):
    """Factory for :class:`~czech_plus.config.AdjectiveCardFields` class."""

    class Meta:  # noqa: D106
        model = config.AdjectiveCardFields

    completion_of_comparison_degrees: str = factory.fuzzy.FuzzyAttribute(faker.pystr)


class NounCardsSettingsFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.NounCardsSettings` class."""

    class Meta:  # noqa: D106
        model = config.NounCardsSettings

    note_type_name: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    fields: config.NounCardFields = factory.SubFactory("tests.factories.NounCardFieldsFactory")


class VerbCardsSettingsFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.VerbCardsSettings` class."""

    class Meta:  # noqa: D106
        model = config.VerbCardsSettings

    note_type_name: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    fields: config.VerbCardFields = factory.SubFactory("tests.factories.VerbCardFieldsFactory")


class AdjectivesCardsSettingsFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.AdjectivesCardsSettings` class."""

    class Meta:  # noqa: D106
        model = config.AdjectivesCardsSettings

    note_type_name: str = factory.fuzzy.FuzzyAttribute(faker.pystr)
    fields: config.AdjectiveCardFields = factory.SubFactory("tests.factories.AdjectiveCardFieldsFactory")


class CardsSettingsFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.CardsSettings` class."""

    class Meta:  # noqa: D106
        model = config.CardsSettings

    nouns: config.NounCardsSettings = factory.SubFactory("tests.factories.NounCardsSettingsFactory")
    verbs: config.VerbCardsSettings = factory.SubFactory("tests.factories.VerbCardsSettingsFactory")
    adjectives: config.AdjectivesCardsSettings = factory.SubFactory("tests.factories.AdjectivesCardsSettingsFactory")


class ConfigFactory(factory.Factory):
    """Factory for :class:`~czech_plus.config.Config` class."""

    class Meta:  # noqa: D106
        model = config.Config

    logging: config.LogSettings = factory.SubFactory("tests.factories.LogSettingsFactory")
    cards: config.CardsSettings = factory.SubFactory("tests.factories.CardsSettingsFactory")

    @classmethod
    def _create(cls, *args, **kwargs) -> config.Config:
        assert config.Config not in config.Config._instances
        return t.cast(config.Config, super()._create(*args, **kwargs))
