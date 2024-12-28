:title: Search for Code in Python Packages
:date: 2024-12-28T19:07:17+00:00
:tags: python, ripgrep
:identifier: 20241228T190717

Searching for Code in Python Packages
=====================================

Something I find myself wanting to do quite often is to search for a particular object within a Python package.

A nice trick is to use a tool like ``fd`` to gather all the relevant filepaths and pass them to ``rg`` for us

.. code-block:: console

   $ fd -e py . "${VIRTUAL_ENV}/lib/python3.10/site-packages/<package>" -X rg <pattern>
