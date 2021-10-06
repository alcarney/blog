Custom Directives
=================

Based on ``Directive``
----------------------

For basic directives, or if you want maximum portability, you can base your directive on
the ``Directive`` class from ``docutils``.

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
      relpath, abspath = self.env.relfn2(filename)

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
