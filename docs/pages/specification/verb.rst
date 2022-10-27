#########
Verb Word
#########

******
Fields
******

.. class:: VerbCard

  .. attribute:: czech

    Number of words must be equal to number of words in
    :class:`~VerbCard.preposition_and_case` field separated with a dot and a
    space.

    You also can set future form of the word in ``[`` and ``]`` brackets.
    Syntax the same, so you can set multiple words.

  .. attribute:: preposition_and_case

    Preposition and case of the verb, which it gives. See
    :class:`~czech_plus.models.Case` class for all possible cases. Preposition
    and case must be separated with a space, and a case must be a number.
    Preposition can be any word (or can be unset), we don't care about it.
    You can set multiple words by separating them with ``.`` (dot with a
    space). Or separated with ``,`` (comma with a space) for set multiple cases
    for a word. Number of words here (separated with a dot and a space) must be
    equal to number of words in :class:`~VerbCard.czech` field.

    You also can set preposition and case for the future form of the word in
    ``[`` and ``]`` brackets. Syntax the same, so you can set multiple words.

  .. attribute:: translation

    Translation of the word to your language.

  .. admonition:: Example

    Lets use ``koukat (se), dívat se`` for :attr:`~VerbCard.czech` field. Note
    that ``(se)`` (and without brackets too) will be count as a part of word.
    We don't parse ``se`` and ``si`` for words. Here it's in brackets because
    it's optional. And lets set for :attr:`~VerbCard.preposition_and_case` -
    ``na 4, !kam?, po 7. na 4, z 2``. This addon will give
    ``koukat (se) (na koho? co?, kam?, po kým? čím?), dívat se (na koho? co?, z koho? čeho?)``
    in the result.


***********
What we do?
***********

Based on :attr:`~VerbCard.preposition_and_case` field, we add preposition
(if it's was given) and case (which this verb gives). You can look at
:class:`~czech_plus.models.Case` for questions in cases.

We don't touch :attr:`~VerbCard.translation` field.
