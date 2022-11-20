##############
General Syntax
##############

For some special syntax see specification for a card type.
Here is described only general syntax which is supported
everywhere, unless otherwise stated.

********
Escaping
********

You can escape one symbol with ``\``, and escape entire word with a ``!``.

So for example we have word, which contains space/comma/dot etc. We can set
``so\, me word`` and our parser will not touch this string! This string will
be counted as one word, even if word separator is ``,``.

Also lets look to ``word, !other word, third``. First word will be parsed as
expected, we will not touch the second word and third word is also parsed as
expected. ``!`` works only until next word starts.

****************
Separating words
****************

Usually words separated with a ``,`` (comma with a space). You can specify
``_`` in non-\ ``czech`` fields, if want to skip this word. For example, you
have ``kapsa, kapuce`` and want to set gender only for second word. Set
:class:`~NounWord.gender` to ``_, F`` and you will get ``kapsa, ta kapuce``.

You can also use ``_`` if you have few words with the same cases/gender etc.
