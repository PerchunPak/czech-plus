"""Tests :mod:`czech_plus.logic.compiler`."""
import typing as t
from unittest.mock import MagicMock

import anki.notes
import pytest
from anki.collection import Collection as AnkiCollection
from faker import Faker
from pytest_mock import MockerFixture

from czech_plus.config import Config
from czech_plus.logic.compiler import Compiler

_T = t.TypeVar("_T")


@pytest.fixture
def anki_collection(mocker: MockerFixture) -> AnkiCollection:
    """Fixture for mocked Anki collection."""
    return mocker.patch("anki.collection.Collection")


class TestCompiler:
    """Tests :func:`czech_plus.logic.compiler.Compiler`."""

    @pytest.fixture
    def compiler(self, mocker: MockerFixture, anki_collection: AnkiCollection) -> Compiler:
        """Fixture for :class:`czech_plus.logic.compiler.Compiler` object."""
        return Compiler(mocker.MagicMock(return_value=anki_collection))

    @pytest.fixture(
        params=(
            lambda faker: [
                ("noun", faker.pyint()),
                ("verb", faker.pyint()),
                ("adjective", faker.pyint()),
            ]
        )(Faker())
    )
    def note_type_and_id(
        self, mocker: MockerFixture, request, mock_config: t.Callable[[str, _T], _T], faker: Faker
    ) -> tuple[str, int]:
        """Fixture for note type and id."""
        note_type, note_id = request.param
        note_type_name = t.cast(
            t.Callable[[], str],
            {
                "noun": lambda: mock_config("cards.nouns.note_type_name", faker.word()),
                "verb": lambda: mock_config("cards.verbs.note_type_name", faker.word()),
                "adjective": lambda: mock_config("cards.adjectives.note_type_name", faker.word()),
            }[note_type],
        )()

        mocker.patch("czech_plus.logic.compiler.Compiler._get_notes_ids", return_value=[(note_id, note_type_name)])
        return note_type_name, note_id

    def test_invalid_note_type_name_in_config(
        self,
        compiler: Compiler,
        anki_collection: AnkiCollection,
        mocker: MockerFixture,
        note_type_and_id: tuple[str, int],
        faker: Faker,
    ) -> None:
        """Test that if note type name is invalid, an error will be raised."""
        note_type, note_id = note_type_and_id
        mocked = mocker.patch("czech_plus.logic.processor.process_card", return_value=None)

        with pytest.raises(ValueError):
            compiler.compile_note(note_id, note_type)

        mocked.assert_called_once_with(
            dict(anki.notes.Note(anki_collection, id=t.cast(anki.notes.NoteId, note_id)).items()), note_type
        )

    def test_anki_collection_just_calls_getter_and_is_cached(self, mocker: MockerFixture) -> None:
        """Test that :func:`czech_plus.logic.compiler.Compiler.anki_collection` just calls getter and is cached."""
        stub = mocker.stub()
        compiler = Compiler(stub)
        stub.assert_not_called()
        assert compiler._anki_collection is stub.return_value
        assert compiler._anki_collection is stub.return_value
        stub.assert_called_once_with()

    def test_compile_all_notes_calls_compile_note(
        self, note_type_and_id: tuple[str, int], compiler: Compiler, mocker: MockerFixture, faker: Faker
    ) -> None:
        """Test that :meth:`czech_plus.logic.compiler.Compiler.compile_all_notes` just calls \
        :meth:`czech_plus.logic.compiler.Compiler.compile_note` for all notes."""
        note_type, note_id = note_type_and_id
        mocked_compile_note = mocker.patch("czech_plus.logic.compiler.Compiler.compile_note")
        mocked_get_cards_ids = t.cast(MagicMock, Compiler._get_notes_ids)

        compiler.compile_all_notes()

        mocked_compile_note.assert_called_once_with(note_id, note_type)
        mocked_get_cards_ids.assert_called_once_with()

    def test_compile_note_calls_what_and_how_expected(  # type: ignore[misc] # explicit any
        self,
        config: Config,
        compiler: Compiler,
        mocker: MockerFixture,
        faker: Faker,
        note_type_and_id: tuple[str, int],
        anki_collection: AnkiCollection,
        mock_config: t.Callable[[str, t.Any], None],
    ) -> None:
        """Test that :meth:`czech_plus.logic.compiler.Compiler.compile_note` calls what and how expected."""
        note_type, note_id = note_type_and_id
        processed_field_name = faker.word()
        original_note_type_name = {
            config.cards.nouns.note_type_name: "nouns",
            config.cards.verbs.note_type_name: "verbs",
            config.cards.adjectives.note_type_name: "adjectives",
        }[note_type]
        mock_config(f"cards.{original_note_type_name}.fields.processed", processed_field_name)

        mocked_note = mocker.patch("anki.notes.Note")
        mocked_process_card = mocker.patch(
            "czech_plus.logic.processor.process_card", return_value=(processed := faker.word())
        )

        compiler.compile_note(note_id, note_type)

        mocked_note.assert_called_once_with(anki_collection, id=note_id)
        mocked_process_card.assert_called_once_with(dict(mocked_note.return_value.items()), note_type)
        mocked_note.return_value.__setitem__.assert_called_once_with(processed_field_name, processed)
        mocked_note.return_value.flush.assert_called_once_with()

    def test_get_notes_ids(
        self, compiler: Compiler, anki_collection: MagicMock, mock_config: t.Callable[[str, _T], _T], faker: Faker
    ) -> None:
        """Test that :meth:`czech_plus.logic.compiler.Compiler._get_notes_ids` returns what expected."""
        nouns_note_type_name, noun_id = mock_config("cards.nouns.note_type_name", faker.word()), faker.pyint()
        verbs_note_type_name, verb_id = mock_config("cards.verbs.note_type_name", faker.word()), faker.pyint()
        adjectives_note_type_name, adjective_id = (
            mock_config("cards.adjectives.note_type_name", faker.word()),
            faker.pyint(),
        )

        anki_collection.models.nids.return_value = [faker.pyint() for _ in range(3)]
        anki_collection.models.id_for_name.side_effect = lambda name: name
        anki_collection.models.nids.side_effect = lambda name: {
            nouns_note_type_name: [noun_id],
            verbs_note_type_name: [verb_id],
            adjectives_note_type_name: [adjective_id],
        }[name]

        assert compiler._get_notes_ids() == [
            (noun_id, nouns_note_type_name),
            (verb_id, verbs_note_type_name),
            (adjective_id, adjectives_note_type_name),
        ]
