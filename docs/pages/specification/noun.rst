#########
Noun Word
#########

******
Fields
******

.. class:: NounCard

  .. attribute:: czech

    Word in Czech. Number of words here must be equal to number of words in
    :class:`~NounCard.gender` field.

  .. attribute:: gender

    Gender of the word. See :class:`~czech_plus.models.Gender` class for all
    possible values. Number of words here must be equal to number of words in
    :class:`~NounCard.czech` field.

  .. admonition:: Example

    Lets use ``kluk, hoch`` for :attr:`~NounCard.czech` field.
    And for :attr:`~NounCard.gender` - ``M, M``\ .
    This addon will give ``ten kluk, ten hoch`` in the result.

    If word is a plural, just prefix :attr:`~NounCard.gender` with a ``m``.
    So if we take ``šaty``, the gender will be ``mM`` and result - ``mM šaty``.
    If you have ideas what better to use for plural - open an issue please
    or write me somewhere. I don't use just plural pronouns because, for
    example, masculine inanimate and female have the same - ``ty``.


**************
What do we do?
**************

Based on the :attr:`~NounCard.gender` field, we add pronoun to the
:attr:`~NounCard.czech` field. See values inside
:class:`~czech_plus.models.Gender` to get full list of
pronouns that we add.
