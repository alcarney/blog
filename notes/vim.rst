(N)Vim
======

Notes on using ``vim`` and ``nvim``

Common
------

Notes that should apply to both flavours of vim.

Keybindings
^^^^^^^^^^^

===========  =====  ===========
Keybinding   Mode   Description
===========  =====  ===========
``<C-w> H``  ``N``  Move the current window to the far left, resizing it to be full-height.
``<C-w> J``  ``N``  Move the current window to the bottom, resizing it to be full-width. 
``<C-w> K``  ``N``  Move the current window to the top, resizing it to be full-width.
``<C-w> L``  ``N``  Move the current window to the far right, resizing it to be full-height.
===========  =====  ===========

Listing Registered ``autocmds``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``:autocmd`` lists all registered ``autocmds``.

``:autocmd <Event>`` lists all registered ``autocmds`` for the given event. e.g.

.. code-block:: vim

   :autocmd FileType                                                                                                                                                                                       
   --- Autocommands ---
   filetypeplugin  FileType
       *         call s:LoadFTPlugin()
   filetypeindent  FileType
       *         call s:LoadIndent()
   syntaxset  FileType
       *         exe "set syntax=" . expand("<amatch>")
   packer_load_aucmds  FileType
       python    lua require("packer.load")({'black'}, { ft = "python" }, _G.packer_plugins)

Synced Scrolling
^^^^^^^^^^^^^^^^

To have 2 or more windows scroll together, simply ``:set scrollbind`` in each window you want to syncronise!

- ``:h scroll-binding``
- ``:h scrollbind``
- ``:h scrollopt``

Neovim Only
-----------

Notes that apply to just ``nvim``.

Vim Only
--------

Notes that apply to just ``vim``.