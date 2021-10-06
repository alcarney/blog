Python 2.x Gotchas
==================

While Python 2 is finally out of support, there is a *lot* of legacy code out there.
Here are some of the things that often trip me up when working with Python 2.x code.

Missing Features
----------------

In the 10+ years since Python 3's release it's not surprising that it has
accumlated a bunch of features that simply don't exist in Python 2.x

No ``enum`` module
^^^^^^^^^^^^^^^^^^

The ``enum`` module was added in Python 3.4. In order to make use of this module
in versions of Python older than this we can install the :pypi:`enum34` package from
PyPi.

.. code-block:: console

   $ pip install enum34

Code that uses the standard ``enum`` module should now work as is.

.. note:: 

   It would seem that this package is not actively maintained with the most
   recent change being in 2016 at the time of writing.

No ``pathlib`` module
^^^^^^^^^^^^^^^^^^^^^

The ``pathlib`` module was added in Python 3.4. In order to make use of this
module in older versions of Python we can install the :pypi:`pathlib2` package on PyPi

.. code-block:: console

   $ pip install pathlib2

Then code written for the standard ``pathlib`` module should work as expected.

No ``FileNotFoundErrors``
^^^^^^^^^^^^^^^^^^^^^^^^^

Not sure when these were added. If you simply want to be able to throw one it's
easy enough to backport one yourself

.. code-block:: python

   class FileNotFoundError(OSError):
       pass

Moved / Changed Features
------------------------

There are a number of features that did exist in Python 2.x but were
renamed/moved or tweaked in someway in Python 3.x so that they are not directly
compatible with older interpreters anymore

``configparser`` is ``ConfigParser``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before Python 3 the ``configparser`` module was called ``ConfigParser``, I'm
struggling to see if there are any functional differences between the two
versions but there is a actively maintained :pypi:`configparser` package available which
has apparently backported a number of changes to older versions of Python

.. code-block:: console

   $ pip install configparser

In theory code using the standard ``configparser`` module will "just work".

"Best Practice"
---------------

Here is a miscellaneous collection things to do when writing code that will run
under Python 2.x that should hopefully minimise the amount of surprises!


Use new style classes
^^^^^^^^^^^^^^^^^^^^^

In Python 2.x new style classes are an explicit opt-in

.. code-block:: python

   class MyClass(object):
       ...

Define both ``__eq__`` and ``__ne__`` 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When creating a class that you wish to define equality for you need to ensure
that you define both the ``__eq__`` and ``__ne__`` special methods for your class to
have the behavior you would expect it to.

In Python 2.x the default implementation of ``__ne__`` is something like the
following.

.. code-block:: python

   def __ne__(self, other):
      return not (self is other)

For your class to behave as expected you will need to define it as follows

.. code-block:: python

   class MyClass(object):
       ...

       def __eq__(self, other):
           ...

       def __ne__(self, other):
           return not self.__eq__(other)

``str != str``
^^^^^^^^^^^^^^

In Python 3 the string related datatypes were overhauled to include built-in
support for unicode character encodings. This means that the ``str`` type in
Python 2.x is **not** equivalent to the ``str`` type in Python 3.x

So if you want to check that some value is an instance of the type ``str`` the
best way is to make use the :pypi:`six` compatibility package

.. code-block:: console

   $ pip install six

And to use the following code

.. code-block:: python

   import six

   if isinstance(value, six.string_types):
       ...