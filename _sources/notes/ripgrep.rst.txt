ripgrep
=======

Searching code in Jupyter Notebooks
-----------------------------------

ripgrep's ``--pre <command>`` flag can be used to search the output of ``<command> filename`` instead of the contents of ``filename`` directly.

We can pair this with ``jq`` to extract just the source code contained in a jupyter notebook.

.. code-block:: console

   $ cat nbcat
   #!/bin/bash
   jq -j '.cells | map(select(.cell_type == "code")) | .[].source | join("")' $1
   
   $ rg --pre nbcat <pattern> example.ipynb
   
Searching code in Python packages
---------------------------------

Something I find myself wanting to do quite often is to search for a particular object within a Python package.

A nice trick is to use a tool like ``fd`` to gather all the relevant filepaths and pass them to ``rg`` for us

.. code-block:: console

   $ fd -e py . "${VIRTUAL_ENV}/lib/python3.10/site-packages/<package>" -X rg <pattern>
