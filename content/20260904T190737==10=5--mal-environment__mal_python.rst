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
       def __init__(self, outer: Env | None = None):
           self.data = {}
           self.outer = outer

       def set(self, key: str, value):
           self.data[key] = value

       def get(self, key: str):
           if (value := self.data.get(key)) is None:
               if self.outer is not None:
                   return self.outer.get(key)
               raise KeyError(key)
           return value
