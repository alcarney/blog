:title: mal environment
:date: 2026-09-04
:tags: mal, python
:identifier: 20260904T190737
:signature: 10=5

The ``mal`` Environment
=======================

:project: mal-py
:filename: env.py

As with the reader, this is held separate.

.. code-block:: python

   from reader import S

   class Env:
       def __init__(
           self, outer: Env | None = None, binds: list[str] = None, exprs: list[Any] = None,
       ):
           self.data = {}
           self.outer = outer

           binds = binds or []
           exprs = exprs or []
           for b, e in zip(binds, exprs):
               self.set(b.name, e)

       def set(self, key: str, value):
           self.data[key] = value

       def get(self, key: str):
           if (value := self.data.get(key)) is None:
               if self.outer is not None:
                   return self.outer.get(key)
               raise KeyError(key)
           return value


The core
--------

:filename: core.py

From step 4, mal calls for a ``core.ns`` object that defines all the built-in functions for the language.

This defines a ``defn`` decorator that makes adding functions to the namespace nice.

.. code-block:: python

   ns = {}

   def defn(name):
       def wrap(fn):
           ns[name] = fn
           return fn
       return wrap

Math functions
^^^^^^^^^^^^^^

Plus, times, divide etc.

.. code-block:: python


   @defn('+')
   def plus(a, b):
       return a + b

   @defn('-')
   def minus(a, b):
       return a - b

   @defn('*')
   def multiply(a, b):
       return a * b

   @defn('/')
   def divide(a, b):
       return int(a/b)


Comparisons
^^^^^^^^^^^

.. code-block:: python

   @defn('=')
   def eql(x, y):
       return x == y

   @defn('<')
   def lt(x, y):
       return x < y

   @defn('>')
   def gt(x, y):
       return x > y

   @defn('<=')
   def lte(x, y):
       return x <= y

   @defn('>=')
   def gte(x, y):
       return x >= y


Printing
^^^^^^^^

We want to be able to print from within ``mal``

.. code-block:: python

   from printer import print_form

   @defn('prn')
   def printit(f):
       print(print_form(f))

Lists
^^^^^

It wouldn't be a Lisp without some list operators.

.. code-block:: python

   @defn('list')
   def make_list(*args):
       return list(args)

   @defn('list?')
   def is_list(x):
       return isinstance(x, list)

   @defn('empty?')
   def is_empty(x):
       return len(x) == 0

   @defn('count')
   def count(x):
       if not x:
           return 0
       return len(x)
