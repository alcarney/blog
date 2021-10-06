Notes on Git
============

Submodules
----------

To clone a repo that contains submodules we can run the following command

.. code-block:: console

   $ git clone --recurse-submodules <repo-url>

Or if you've already cloned a repo only to later discover that it contained
submodules

.. code-block:: console

   $ git submodule update --init --recursive
 
Links & Resources
-----------------

- `How to "git clone" including submodules? <https://stackoverflow.com/questions/3796927/how-to-git-clone-including-submodules>`_