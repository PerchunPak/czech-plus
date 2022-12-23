"""Module for the card compiler."""
import typing as t

from anki.collection import Collection as AnkiCollection
from czech_plus._vendor.loguru import logger

from czech_plus.config import Config
from czech_plus.logic import processor

import anki.notes  # isort:skip # Circular import before importing anki.collection


class Compiler:
    """Compile a card (note in Anki) to processed and ready to use data.

    So in this way we solve two problems in once:
    1. We can use compiled content for TTS addon.
    2. We can use it on mobile.
    """

    def __init__(self, anki_collection_getter: t.Callable[[], AnkiCollection]) -> None:
        self._config = Config()
        self._get_anki_collection = anki_collection_getter
        self._cached_anki_collection: t.Optional[AnkiCollection] = None

    @property
    def _anki_collection(self) -> AnkiCollection:
        """Get the Anki collection object."""
        if self._cached_anki_collection is None:
            self._cached_anki_collection = self._get_anki_collection()
        return self._cached_anki_collection

    def compile_all_notes(self) -> None:
        """Compile all notes.

        Just fetches all notes via :meth:`_get_notes_ids` and calls
        :meth:`compile_note` for each of them.
        """
        logger.debug("Compile notes was called.")

        for note_id, note_type in self._get_notes_ids():
            self.compile_note(note_id, note_type)

    def compile_note(self, note_id: int, note_type: str) -> None:
        """Compile a note.

        Args:
            note_id: ID of the note.
            note_type: Name of the note type.
        """
        logger.debug(f"Compiling note {note_id} ({note_type})...")

        note = anki.notes.Note(self._anki_collection, id=anki.notes.NoteId(note_id))
        processed = processor.process_card(dict(note.items()), note_type)

        if processed is None:
            raise ValueError(f"You specified invalid note type name in config - {note_type!r}")

        processed_field_name = {
            self._config.cards.nouns.note_type_name: self._config.cards.nouns.fields.processed,
            self._config.cards.verbs.note_type_name: self._config.cards.verbs.fields.processed,
            self._config.cards.adjectives.note_type_name: self._config.cards.adjectives.fields.processed,
        }[note_type]

        note[processed_field_name] = processed
        note.flush()

    def _get_notes_ids(self) -> list[tuple[int, str]]:
        """Get IDs of all notes with needed note types.

        Returns:
            List of tuples with note ID and note type name.
        """
        note_type_id = self._anki_collection.models.id_for_name(self._config.cards.nouns.note_type_name)
        assert note_type_id is not None
        noun_notes_ids = self._anki_collection.models.nids(note_type_id)
        logger.trace(f"{noun_notes_ids=}")

        note_type_id = self._anki_collection.models.id_for_name(self._config.cards.verbs.note_type_name)
        assert note_type_id is not None
        verb_notes_ids = self._anki_collection.models.nids(note_type_id)
        logger.trace(f"{verb_notes_ids=}")

        note_type_id = self._anki_collection.models.id_for_name(self._config.cards.adjectives.note_type_name)
        assert note_type_id is not None
        adjective_notes_ids = self._anki_collection.models.nids(note_type_id)
        logger.trace(f"{adjective_notes_ids=}")

        notes_ids: list[tuple[int, str]] = [
            (note_id, self._config.cards.nouns.note_type_name) for note_id in noun_notes_ids
        ]
        notes_ids.extend((note_id, self._config.cards.verbs.note_type_name) for note_id in verb_notes_ids)
        notes_ids.extend((note_id, self._config.cards.adjectives.note_type_name) for note_id in adjective_notes_ids)

        return notes_ids
