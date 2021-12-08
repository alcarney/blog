(N)Vim
======

Notes on using ``vim`` and ``nvim``

Common
------

Notes that should apply to both flavours of vim.

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

Neovim Only
-----------

Notes that apply to just ``nvim``.

Vim Only
--------

Notes that apply to just ``vim``.