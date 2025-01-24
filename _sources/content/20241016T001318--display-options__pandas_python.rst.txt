:title: Display Options
:date: 2024-10-16
:tags: pandas, python
:identifier: 20241016T001318

Display Options
===============

When doctesting pandas code, it's quite useful to be able to force pandas to print a dataframe in full without omitting or wrapping columns.
This can be by setting the following options

.. code-block:: python

   import pandas as pd

   pd.set_option('display.width', 0)
   pd.set_option('display.max_columns', None)
