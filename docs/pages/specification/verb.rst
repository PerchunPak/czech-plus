#########
Verb Word
#########

******
Fields
******

.. class:: VerbCard

  .. attribute:: czech

    Number of words must be equal to number of words in
    :attr:`~VerbCard.preposition_and_case` field

    Words must be separated with ``.`` (a dot and a space).

    You also can set future form of the word in ``[`` and ``]`` brackets.
    Syntax the same with :attr:`~VerbCard.preposition_and_case` field,
    so you can set multiple words.

  .. attribute:: preposition_and_case

    Preposition and case of the verb, which it gives. See
    :class:`~czech_plus.models.Case` class for all possible cases. Preposition
    and case must be separated with a space, and a case must be a number.
    Preposition can be any word (or can be unset), we don't care about it.
    You can set multiple words by separating them with ``.`` (a dot with a
    space). Or separated with ``,`` (a comma with a space) to set multiple
    cases for one word. Number of words here (separated with a dot and a space)
    must be equal to number of words in :class:`~VerbCard.czech` field.

    You also can set preposition and case for the future form of the word in
    ``[`` and ``]`` brackets. You can set multiple words in one brackets. For
    example ``word [future1, future2]`` will be rendered as
    ``word [future1, future2]``\ .

  .. admonition:: Example

    Lets use ``koukat (se), dívat se`` for :attr:`~VerbCard.czech` field. Note
    that ``(se)`` (and without brackets too) will be count as a part of word.
    We don't have special parsing for ``se`` and ``si`` in words. In example
    it's in brackets because it's optional. And lets set for
    :attr:`~VerbCard.preposition_and_case` - ``na 4, !kam?, po 7. na 4, z 2``.
    This addon will give
    ``koukat (se) (na koho? co?, kam?, po kým? čím?), dívat se (na koho? co?, z koho? čeho?)``
    in the result.


**************
What do we do?
**************

Based on :attr:`~VerbCard.preposition_and_case` field, we add preposition
(if it was given) and case (which this verb gives). You can look at
:class:`~czech_plus.models.Case` for questions in cases.
