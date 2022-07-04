Detecting ``python -i``
=======================

An awesome feature of Python that I'm using more and more is running ``python -i <script>``.

This first runs the script before opening a standard Python REPL, it's fantastic for when I'm working on some code and quickly want to play around with some existing functions and figure out what the next step should be.
Unfortunately, because this sets ``__name__ = '__main__'`` if you're working on a cli script with a ``if __name__ == '__main__'`` block it will get executed along with all your function definitions.

But thanks to `this Stack Overflow answer <https://stackoverflow.com/a/640431>`__ it's possible to add a little ``ctypes`` magic to your script and only trigger the main block if Python has not been started with the ``-i`` flag!

.. code-block:: python 

   import ctypes


   def is_interactive_mode():
       """Check whether python was invoked with the -i flag."""

       interactive_flag = ctypes.cast(
           ctypes.pythonapi.Py_InteractiveFlag, ctypes.POINTER(ctypes.c_int)
       )
       return interactive_flag.contents.value > 0
 
   if __name__ == '__main__' and not is_interactive_mode():
       ...