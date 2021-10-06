Python 3.x Gotchas
==================

Python continues to improve with plenty of new features and improvements with each release.
When working with older versions of Python 3.x it's easy to forget how new some features are.

Beware ``pathlib`` on 3.5
-------------------------

While :mod:`py35:pathlib` exists in Python 3.5, it's not fully integrated yet. Passing a
:class:`py35:pathlib.Path` object to the built-in :func:`py35:open` method will result in a surprising error

.. code-block:: python

   TypeError: invalid file: PosixPath('path/to/file.txt')

In this situation it's better to call the path's :meth:`~py35:pathlib.Path.open` method instead.
 