:title: mal reader
:date: 2026-09-04
:tags: mal, python
:identifier: 20260904T122549
:signature: 10=3

The ``mal`` Reader
==================

:project: mal-py

.. seealso::

   `Mal: Step 1 <https://github.com/kanaka/mal/blob/master/process/guide.md#step-1-read-and-print>`__

In ``mal`` the reader exists "outside" the regular steps since once it is setup, it's not going to change much.
That said many data types are optional to start with so, I'm likely to only add them on demand as I progress through the steps.

Tokenising
----------

:filename: reader.py

The first step is to chop up the input stream into a sequence of tokens, the suggested way to do this is with a fairly intimidating regular expression.
Thankfully, by compiling it with ``re.VERBOSE`` we can at least annotate it.

.. code-block:: python

   import re

   TOKEN = re.compile(
       r"""
           [\s,]*                            # tokens are separated by whitespace or commas
           (                                 # a token is ...
             ~@                              #   a literal '~@'
           | [\[\]{}()'`~^@]                 #   or a literal  "[", "]", "{", "}", "(", ")", "'", "`", "~", "^", "@"
           | "(?:                            #   or a string i.e. '"' followed by
                 \\.                         #      an escaped character e.g. '\n'
               | [^\\"]                      #      anything except '\' or '"'
              )*                             #      (repeated zero or more times)
             "?                              #      closed by a '"' (made optional to also handle invalid strings)
           | ;.*                             #   or a comment i.e. ';' followed by anything (except newlines) zero or more times
           | [^\s\[\]{}()'"`,;]*             #   or a symbol i.e. a sequence of zero or more non-special characters
           )
       """,
       re.VERBOSE,
   )

The ``(?:`` syntax was new to me, apparently this defines a "non-capturing group". It allows you to express ``A or B`` without the group showing up in ``Match.groups()`` - nice!.

Using this pattern, we can now define a function that takes a string and return a list of tokens.

.. code-block:: python

   def tokenise(text: str) -> list[str]:
       return TOKEN.findall(text)

Reading
-------

Now we have a stream of tokens, the next step is to construct a data structure representing the code inputted.

The Reader
^^^^^^^^^^

To help manage the stream of tokens, the mal guide suggests creating a ``Reader`` object

.. code-block:: python

   class Reader:

       def __init__(self, tokens):
           self.tokens = tokens
           self.pos = 0

   {{ insert(slots['reader-methods'], indent=4) }}

Which provides the following methods:

- A ``next`` method to return the current token and advances the position.

  .. code-block:: python
     :slot: reader-methods

     def next(self):
         try:
             tok = self.tokens[self.pos]
         except IndexError:
             raise EOFError()
         self.pos += 1
         return tok

- A ``peek`` method that simply returns the current token

  .. code-block:: python
     :slot: reader-methods

     def peek(self):
         try:
             return self.tokens[self.pos]
         except IndexError:
             raise EOFError()

read_form
^^^^^^^^^

The generic ``read_form`` method dispatches to specialised read methods depending on what the current token is.

.. code-block:: python

   def read_form(reader: Reader):
       match reader.peek():
           case '(':
               return read_list(reader)
           case _:
               return read_atom(reader)


read_list
^^^^^^^^^

As you would expect ``read_list`` is responsible for constructing lists

.. code-block:: python

   def read_list(reader: Reader):
       if (tok := reader.next()) != '(':
           raise RuntimeError(f"Expected '(', got {tok!r}")

       items = []
       while reader.peek() != ')':
           items.append(read_form(reader))

       if (tok := reader.next()) != ')':
           raise RuntimeError(f"Expected ')', got {tok!r}")

       return items

read_atom
^^^^^^^^^

An atom is "everything else"

.. code-block:: python

   import contextlib

   def read_atom(reader: Reader):
       tok = reader.next()
       if tok in {'(', ')'}:
           raise RuntimeError(f"Expected atom, got {tok!r}")

       with contextlib.suppress(ValueError):
           return int(tok)

       match tok:
           case 'true':
               return True
           case 'false':
               return False
           case 'nil':
               return None
           case _:
               return S(tok)

read_str
^^^^^^^^

Finally, ``read_str`` ties it all together.

.. code-block:: python

   def read_str(ins: str):
       reader = Reader(tokenise(ins))
       return read_form(reader)


Data Types
----------


Symbols
^^^^^^^

The ``S`` class represents a symbol.

.. code-block:: python

   class S:
       __match_args__ = ("name",)

       def __init__(self, name: str):
           self.name = name

       def __repr__(self):
           return self.name


The ``mal`` printer
-------------------

:filename: printer.py

Like the reader, the ``mal`` printer is handled "outside" of the steps.

.. code-block:: python

   def print_form(form):
       if callable(form):
           return r"#\<function>"

       match form:
          case [*fs]:
              inner = " ".join(print_form(f) for f in fs)
              return f"({inner})"
          case True:
              return 'true'
          case False:
              return 'false'
          case None:
              return 'nil'
          case _:
              return str(form)
