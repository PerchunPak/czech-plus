##############
Adjective Word
##############

******
Fields
******

.. class:: AdjectiveWord

  .. attribute:: czech

    Word in Czech. Number of words here must be equal to number of words in
    :class:`~AdjectiveWord.completion_of_comparison_degrees` field.

  .. attribute:: completion_of_comparison_degrees

    Completion of comparison degrees of the adjective. Can have any value,
    even another word. For example, if the word has irregular form. Can be
    unset, if the adjective doesn't have comparison degrees. Number of words
    here must be equal to number of words in :class:`~AdjectiveWord.czech`
    field.

  .. attribute:: translation

    Translation of the word to your language.

  .. admonition:: Example

    Lets use ``hezký`` for :attr:`~AdjectiveWord.czech` field.
    And for :attr:`~AdjectiveWord.completion_of_comparison_degrees` - ``čí``.
    This addon will give ``hezký (čí)`` in the result.

    Or if we unset :attr:`~AdjectiveWord.completion_of_comparison_degrees`
    field, addon just will return ``hezký``.


**************
What do we do?
**************

We just add :attr:`~AdjectiveWord.completion_of_comparison_degrees` to the end.
See example upper.

We don't touch :attr:`~VerbCard.translation` field.
