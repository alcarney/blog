Custom Directives
=================

Based on ``Directive``
----------------------

For basic directives, or if you want maximum portability, you can base your directive on
the ``Directive`` class from ``docutils``::

   from docutils.parsers.rst import Directive

   class MyCustom(Directive):
       
       def run(self):
           return []

Arguments
^^^^^^^^^

Directive arguments are declared by setting the ``required_arguments`` and ``optional_arguments`` fields to
an appropriate value::

   class MyCustom(Directive):

       required_arguments = 1
       optional_arguments = 0  # (The default)

These arguments can then be accessed using the ``arguments`` field during the ``run`` method::

   class MyCustom(Directive):

       def run(self):
           for arg in self.arguments:
               ...

Options
^^^^^^^

Directive options are declared using the ``option_spec`` field. This is a dictionary mapping option names to
the functions used to parse them::

   from docutils.parsers.rst import Directive

   class MyCustom(Directive):

       option_spec = {
          "arg-name": paser_function
       }
       
       def run(self):
           return []

where the following built in parsers are available

``docutils.parsers.rst.directives.choice``
   A helper function to write a parser function that ensures the argument is one of a valid set of choices.
   For example::

      from docutils.parsers.rst import directives

      def yesorno(argument):
          return directives.choice(argument, ('yes', 'no'))

``docutils.parsers.rst.directives.class_option``
   Converts a string separated list of values into a list of valid class names.

``docutils.parsers.rst.directives.encoding``
   Ensures the argument is a valid character encoding.

``docutils.parsers.rst.directives.flag``
   Option is a flag, raises an error if a value is given

``docutils.parsers.rst.directives.length_or_unitless``
   A valid length value (``em``, ``ex``, ``px``, ``in``, ``cm``, ``mm``, ``pt``, ``pc``) or 
   a unitless value. 

``docutils.parsers.rst.directives.length_or_percentage_or_unitless``
   A valid length, percentage or unitless value. 

``docutils.parsers.rst.directives.path``
   From the docutils docs.

      Return the path arguments unwrapped (with newlines removed).
      Rase ``ValueError`` if no argument is found

   But I'm not entirely sure what this means...

``docutils.parsers.rst.directives.nonnegative_int``
   Ensure the argument given is a positive integer (zero included).

``docutils.parsers.rst.directives.percentage``
   Argument should be a positive integer - with optional percentage sign

``docutils.parsers.rst.directives.positive_int``
   Ensure the argument given is a positive integer (zero excluded).

``docutils.parsers.rst.directives.positive_int_list``
   A CSV or space separated list of positive integers.

``docutils.parsers.rst.directives.single_char_or_unicode``
   Passes through a single character as-is, or if a unicode character code is given it gets
   converted into a unicode character.

``docutils.parsers.rst.directives.single_char_or_whitespace_or_unicode``
   Same as above but ``tab`` or ``space`` are also supported.

``docutils.parsers.rst.directives.unchanged``
   Pass the option through unchanged

``docutils.parsers.rst.directives.unchanged_required``
   Option is required, pass it through unchanged 

``docutils.parsers.rst.directives.unicode_code``
   Converts a unicode character code (e.g. ``U+262E``) into a unicode character.

``docutils.parsers.rst.directives.uri``
   Ensure the argument given is an URI

These options can then be accessed using the ``options`` field during the ``run`` method::

   class MyCustom(Directive):

       def run(self):
           opt = self.options.get('arg-name', None)

Including files
^^^^^^^^^^^^^^^

If your directive mimics the ``.. include::`` directive in some way it's easy enough to
insert some reStructuredText into the final document.

.. code-block:: python

   def run(self):
      ...

      filename = pathlib.Path(...)
      with filename.open() as f:
         content = f.read().splitlines()
         self.state_machine.insert_input(content, str(readme))

.. note:: 

   The actual ``.. include::`` directive does a lot more work to handle edge cases particuarly
   when it comes to whitespace, so the above approach may not be sufficient in all cases.


Based on ``SphinxDirective``
----------------------------

If the directive is only for use within Sphinx projects, it's a good idea to base it
on :class:`~sphinx:sphinx.util.docutils.SphinxDirective` as it exposes more of Sphinx's 
internals potentially leading into better integration.

Referencing Files
^^^^^^^^^^^^^^^^^

If you are referencing files from a directive, chances are you want to reference that
file either relative to the document's source or the root of the documentation project.
Thankfully, there is the :meth:`~sphinx:sphinx.environment.BuildEnvironment.relfn2path`
method that implements that logic for you

.. code-block:: python

   def run(self): 
      ...
      relpath, abspath = self.env.relfn2path(filename)

which returns

``relpath``
   The path of the file relative to the project's ``srcdir``

``abspath``
   The absolute path of the file.

Noting Dependencies
^^^^^^^^^^^^^^^^^^^

If the result of your directive depends on more than just the source file that contains 
it you can use the :meth:`~sphinx:sphinx.environment.BuildEnvironment.note_dependency`
method to indicate the document should be rebuild if one of these external files change.

.. code-block:: python

   def run(self):
      ...
      self.env.note_dependency(filename)

During a build, Sphinx will look and issue warnings for any document not included in some
``toctree``. If however, an rst file is included by your directive and not directly included
in the ``toctree`` the ``note_included`` method can be used to suppress the warning.

.. code-block:: python

   def run(self):
      ...
      self.env.note_included(filename)
