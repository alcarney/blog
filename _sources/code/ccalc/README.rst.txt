A CPython extension that embeds the ``simple-ast`` program into Python.

.. code-block:: python

   >>> import ccalc
   >>> expression = (ccalc.Literal(1) + 2) * 3
   >>> expression
   Multiply<Plus<Literal<1.0>, Literal<2.0>>, Literal<3.0>>

   >>> ccalc.eval_ast(expression)
   9.0

Building
--------

It's probably worth creating a virtual environment to work in

.. code-block:: console

   $ python -m venv .env

Assuming you have a C compiler available, building the extension is as easy as
running the following command

.. code-block:: console

   (.env) $ python setup.py install 
