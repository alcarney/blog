Extracting archives
-------------------

Archives can be extracted with the command

.. code-block:: console

   tar -vzxf archive.tar.gz

where
- ``-v``: verbose, list all files processed
- ``-x``: extract archive
- ``-z``: use ``gzip`` compression.
- ``-f``: to set the acutal file to process

Additionally

- ``--directory``: can be used to set the output directory.
- ``--strip <n>`` can be used to remove the first ``n`` directories from the extract
  hierarchy. (I think this is an alias for ``--strip-components``?)
