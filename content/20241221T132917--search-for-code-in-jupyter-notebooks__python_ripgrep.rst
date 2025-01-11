:title: Search for Code in Jupyter Notebooks
:date: 2024-12-21T13:29:00+00:00
:tags: python, ripgrep
:identifier: 20241221T132917

Searching for Code in Jupyter Notebooks
=======================================

ripgrep's ``--pre <command>`` flag can be used to search the output of ``<command> filename`` instead of the contents of ``filename`` directly.

We can pair this with ``jq`` to extract just the source code contained in a jupyter notebook.

.. code-block:: console

   $ cat nbcat
   #!/bin/bash
   jq -j '.cells | map(select(.cell_type == "code")) | .[].source | join("")' $1

   $ rg --pre nbcat <pattern> example.ipynb
