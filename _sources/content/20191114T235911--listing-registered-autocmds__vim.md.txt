---
title: Listing Registered autocmds
date: 2019-11-14T23:59:11+00:00
tags:
  - vim
identifier: 20191114T235911
---

# Listing Registered ``autocmds``

``:autocmd`` lists all registered ``autocmds``.

``:autocmd <Event>`` lists all registered ``autocmds`` for the given event. e.g.

```vim
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
```
