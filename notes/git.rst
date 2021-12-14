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

Tags
----

Updating tags from remote
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

   $ git fetch --tags
   remote: Enumerating objects: 307, done.
   remote: Counting objects: 100% (228/228), done.
   remote: Total 307 (delta 228), reused 228 (delta 228), pack-reused 79
   Receiving objects: 100% (307/307), 311.14 KiB | 1.88 MiB/s, done.
   Resolving deltas: 100% (281/281), completed with 101 local objects.
   From https://github.com/neovim/neovim
   * [new tag]             eval-clear-rebase-1-compiles-and-passes-u-tests-3-next  -> eval-clear-rebase-1-compiles-and-passes-u-tests-3-next
   ...
   ! [rejected]            nightly                                                 -> nightly  (would clobber existing tag)
   ! [rejected]            stable                                                  -> stable  (would clobber existing tag)


For tags that move (e.g. neovim's ``nightly`` and ``stable`` tags) an additional ``-f`` flag is required.

.. code-block:: console

   $ git fetch --tags -f
   From https://github.com/neovim/neovim
   t [tag update]          nightly    -> nightly
   t [tag update]          stable     -> stable

Links & Resources
-----------------

- `How to "git clone" including submodules? <https://stackoverflow.com/questions/3796927/how-to-git-clone-including-submodules>`_
- `How to get rid of "would clobber existing tag" <https://stackoverflow.com/questions/58031165/how-to-get-rid-of-would-clobber-existing-tag>`_