This is cool, using ``mock.patch()`` to replace the implementation of something you wish to inspect further.

This can be something simple like adding in a logging statement.

.. code-block:: python

   from unittest.mock import patch

   from mymodule import original_func
   from mymodule import some_other_func

   def patched_func(a, b):
       logger.debug("Args %s %s", a, b)
       return original_func(a, b)

   with patch('mymodule.original_func', side_effect=patched_func):
       some_other_func(1, 2)

Or *very* useful if you want to interact with/visualise the situation you are trying to debug in a notebook!

.. code-block:: python

   from IPython.display import display

   def patched_func(a, b):
       widget = ... # Something that jupyter displays nicely.
       display(widget)

       return original_func(a, b)

   with patch('mymodule.original_func', side_effect=patched_func):
       some_other_func(1, 2)       