:title: Debugging Python Code
:date: 2025-06-15
:tags: emacs, python
:identifier: 20250615T135327
:signature: 5=4=1

Debugging Python Code
=====================

To my knowledge there are two main approaches to debugging some Python code in Emacs.

- :ref:`debug-python-code-pdb`
- :ref:`debug-python-code-dape`

.. _debug-python-code-pdb:

Using ``M-x pdb``
-----------------

.. termshot:: /images/emacs-pdb.cast
   :title: M-x pdb


Emacs supports Python's built-in :external+python:py:mod:`pdb` debugger out of the box thanks to the `Grand Unified Debugger <https://www.gnu.org/software/emacs/manual/html_node/emacs/Debuggers.html>`__.

Since everything is avaialable out of the box, there's nothing really to setup!
Just run ``M-x pdb``, Emacs will ask you how you want to invoke ``pdb``

.. code-block:: none

   Run pdb (like this): python -m pdb

Which you can of course modify to run your code.
What's cool about this is that it can be any ``python`` command that eventually results in a pdb session.

For example, I often will pass the ``--pdb`` flag to pytest to conduct a post-mortem on a particular test case, this will just work\ :sup:`TM` with Emacs' ``pdb`` command!

.. code-block:: none

   Run pdb (like this): hatch test -i py=3.11 -i sphinx=8 -- tests/example/test_example.py::test_this --pdb

Breakpoints can be added by adding a call to the built-in :external+python:py:func:`breakpoint` function.

.. _debug-python-code-dape:

Using ``dape``
--------------

.. admonition:: TODO

   Figure out how to use this.
