:title: Nvim Config
:date: 2025-02-16
:tags: nvim
:identifier: 20250216T190621

Neovim
======

.. highlight:: none

Neovim configuration

.. code-block:: make
   :filename: Makefile

   .PHONY: nvim
   nvim:
        test -L $(HOME)/.config/nvim || ln -s $(shell pwd)/nvim $(HOME)/.config/nvim

It's been some time since I have used (n)vim as my primary editor, certainly pre nvim ``v0.5`` (nvim ``v0.10.1`` is now available at the time of writing).

Needless to say a lot has changed (such as using lua for configuration!) so the overall structure of this config has been heavily influenced by/stolen from :gh:`nvim-lua/kickstart.nvim`

Basic Options
-------------

Appearance
^^^^^^^^^^

For the time being, use the default colorscheme with ``notermguicolors`` set so that ``nvim`` inherits the colorscheme used by the terminal. (Makes adapting to the system theme easier)

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.termguicolors = false

``breakindent``
^^^^^^^^^^^^^^^

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.breakindent = true

It ensures that when a long that is indented is wrapped, the next line starts at the same level of indentation i.e ::

   |   This is a very
   |   long line that
   |   has been wrapped

Instead of ::

   |   This is a very
   |long line that
   |has been wrapped

Searching
^^^^^^^^^

Disabling ``ignorecase`` will make searches case sensitive by default.
To make the search case insensitive add a ``\c`` to the search pattern e.g. ``/set\c/`` or ``/\cset/``

The ``inccomand = 'split'`` tells neovim to open a dedicated split to preview the result of the current ``:%s/../../`` command.

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.inccommand = 'split'
   vim.opt.incsearch = true
   vim.opt.ignorecase = false

Line Numbers
^^^^^^^^^^^^

Enable line numbers

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.number = true

Reuse the line number column to render 'signs'

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.signcolumn = 'number'


Whitespace
^^^^^^^^^^

Render certain whitespace characters

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.list = true
   vim.opt.listchars = { tab = '».', trail = '·', extends = '→', precedes= '←' }

Keybindings
-----------

Keybindings that are useful anywhere.

Set the ``<leader>`` and ``<localleader>``

.. code-block:: lua
   :filename: nvim/init.lua

   vim.g.mapleader = ' '
   vim.g.maplocalleader = ' '

Mash :kbd:`Esc` to clear any search highlights

.. code-block:: lua
   :filename: nvim/init.lua

   vim.keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')


Easier movement between windows

.. code-block:: lua
   :filename: nvim/init.lua

   vim.keymap.set('n', '<C-h>', '<C-w><C-h>')
   vim.keymap.set('n', '<C-l>', '<C-w><C-l>')
   vim.keymap.set('n', '<C-j>', '<C-w><C-j>')
   vim.keymap.set('n', '<C-k>', '<C-w><C-k>')

Recenter the display after common movement commands

.. code-block:: lua
   :filename: nvim/init.lua

   vim.keymap.set('n', 'n', 'nzz')
   vim.keymap.set('n', 'N', 'Nzz')
   vim.keymap.set('n', 'G', 'Gzz')
   vim.keymap.set('n', '<c-i>', '<c-i>zz')
   vim.keymap.set('n', '<c-o>', '<c-o>zz')


Plugins
-------

The plugin manager du-jour appears to be :gh:`folke/lazy.nvim`, let's ensure that it's available.

.. code-block:: lua
   :filename: nvim/init.lua

   local lazypath = vim.fn.stdpath('data') .. '/lazy/lazy.nvim'
   if not vim.uv.fs_stat(lazypath) then
     local lazyrepo = 'https://github.com/folke/lazy.nvim.git'
     local out = vim.fn.system({ 'git', 'clone', '--filter=blob:none', '--branch=stable', lazyrepo, lazypath})

     if vim.v.shell_error ~= 0 then
       error('Error cloning lazy.nvim:\n' .. out)
     end
   end

And add the install location to the runtime path

.. code-block:: lua
   :filename: nvim/init.lua

   vim.opt.rtp:prepend(lazypath)

Finally, tell lazyvim what plugins to install and configure

.. code-block:: lua
   :filename: nvim/init.lua

   require('lazy').setup({
     'tpope/vim-sleuth',
     require 'alc.completion',
     require 'alc.lsp',
     require 'alc.telescope',
   })

Completion
----------

:gh:`hrsh7th/nvim-cmp` seems to be the completion framework of choice

.. code-block:: lua
   :filename: nvim/lua/alc/completion.lua

   function setup()
     local cmp = require('cmp')

     cmp.setup {
       completion = { completeopt = 'menu,menuone,noinsert' },
       mapping = cmp.mapping.preset.insert {
          ['<C-n>'] = cmp.mapping.select_next_item(),
          ['<C-p>'] = cmp.mapping.select_prev_item(),
          ['<C-b>'] = cmp.mapping.scroll_docs(-4),
          ['<C-f>'] = cmp.mapping.scroll_docs(4),
          ['<C-y>'] = cmp.mapping.confirm { select = true },
        },
       sources = {
          { name = 'nvim_lsp' },
        },
     }
   end

.. code-block:: lua
   :filename: nvim/lua/alc/completion.lua

   return {
     'hrsh7th/nvim-cmp',
     event = 'InsertEnter',
     dependencies = {
       'hrsh7th/cmp-nvim-lsp',
     },
     config = setup
   }

Language Servers
----------------

The following is a function that will be called each time a connection to a server is made, allowing LSP specific keybindings etc to be configured.

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/init.lua

   function lsp_attach(event)
     vim.keymap.set('n', 'gd', require('telescope.builtin').lsp_definitions, { buffer = event.buf })
     vim.keymap.set('n', 'gr', require('telescope.builtin').lsp_references, { buffer = event.buf })
     vim.keymap.set('n', 'gI', require('telescope.builtin').lsp_implementations, { buffer = event.buf })
     vim.keymap.set('n', '<leader>D', require('telescope.builtin').lsp_type_definitions, { buffer = event.buf })
     vim.keymap.set('n', '<leader>ds', require('telescope.builtin').lsp_document_symbols, { buffer = event.buf })
     vim.keymap.set('n', '<leader>ws', require('telescope.builtin').lsp_dynamic_workspace_symbols, { buffer = event.buf })
     vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, { buffer = event.buf })
     vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, { buffer = event.buf })
     vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, { buffer = event.buf })
   end

Finally, the block of ``lazy.nvim`` configuration that ties it all together

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/init.lua

   return {
      'neovim/nvim-lspconfig',
      dependencies = {
        'hrsh7th/cmp-nvim-lsp',
        { 'j-hui/fidget.nvim', opts = {
            notification = {
              override_vim_notify = true,
            }
          }
        },
      },
      config = function()
        vim.api.nvim_create_autocmd('LspAttach', {
          group = vim.api.nvim_create_augroup('alc-lsp-attach', { clear = true }),
          callback = lsp_attach
        })

        -- Ensure the additional capabilities provided by nvim-cmp are provided to the server
        local capabilities = vim.lsp.protocol.make_client_capabilities()
        capabilities = vim.tbl_deep_extend('force', capabilities, require('cmp_nvim_lsp').default_capabilities())

        -- Setup each server
        local use_devtools = os.getenv('LSP_DEVTOOLS') ~= nil
        require('alc.lsp.esbonio').setup { capabilities = capabilities, devtools = use_devtools }
        require('alc.lsp.python').setup { capabilities = capabilities }
      end
   }

esbonio
^^^^^^^

Of course, I use :gh:`swyddfa/esbonio` with my documentation projects.

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/esbonio.lua

   function setup(opts)
      opts = opts or {}

      if not opts.capabilities then
        opts.capabilities = vim.lsp.protocol.make_client_capabilities()
      end

      require('lspconfig').esbonio.setup {
        cmd = get_esbonio_cmd(opts),
        capabilities = capabilities,
        handlers = {
          ["sphinx/clientCreated"] = client_created,
          ["sphinx/appCreated"] = app_created,
          ["sphinx/clientErrored"] = client_errored,
          ["sphinx/clientDestroyed"] = client_destroyed,
        },
        commands = {
          EsbonioPreviewFile = {
            preview_file,
            description = 'Preview Current File',
          },
        },
        settings = {
          esbonio = {
            logging = {
              level = 'debug',
              window = opts.devtools or false,
            }
          }
        }
      }
   end

The following function determines the command that should be used to launch ``esbonio``, useful for the occasions where I need to debug it or use some of the :gh:`swyddfa/lsp-devtools` tooling.

.. note::

   Until I can configure nvim to send URIs relative to the devcontainer e.g. ::

      file:///var/home/alex/Projects/alcarney/blog -> file:///workspaces/blog

   it is pointless trying to run an LSP from inside the container.

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/esbonio.lua

   function get_esbonio_cmd(opts)
     local cmd = {}

     -- TODO: Devcontainer support.
     --
     -- local workspace = require('alc.devcontainer').workspace()
     -- if workspace then
     --   table.insert(cmd, 'devcontainer')
     --   table.insert(cmd, 'exec')
     --   table.insert(cmd, '--workspace-folder')
     --   table.insert(cmd, workspace)
     -- end

     if opts.devtools then
       table.insert(cmd, 'lsp-devtools')
       table.insert(cmd, 'agent')
       table.insert(cmd, '--')
     end

     table.insert(cmd, 'esbonio')
     return cmd
   end

**Previews**

The following command triggers a preview of the file vistied by the current buffer as well as setting up an autocommand to syncronise the scroll state with the preview.

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/esbonio.lua

   function preview_file()
     local params = {
       command = 'esbonio.server.previewFile',
       arguments = {
         { uri = vim.uri_from_bufnr(0), show = true },
       },
     }

     local clients = require('lspconfig.util').get_lsp_clients {
       bufnr = vim.api.nvim_get_current_buf(),
       name = 'esbonio',
     }
     for _, client in ipairs(clients) do
       client.request('workspace/executeCommand', params, nil, 0)
     end

     local augroup = vim.api.nvim_create_augroup("EsbonioSyncScroll", { clear = true })
     vim.api.nvim_create_autocmd({"WinScrolled"}, {
       callback = scroll_view, group = augroup, buffer = 0
     })
   end

Scrolling the view itself is handled by the following function

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/esbonio.lua

   function scroll_view(event)
     local esbonio = vim.lsp.get_active_clients({ bufnr = 0, name = 'esbonio' })[1]
     local view = vim.fn.winsaveview()

     local params = { uri = vim.uri_from_bufnr(0),  line = view.topline }
     esbonio.notify('view/scroll', params)
   end


Sphinx Processes
^^^^^^^^^^^^^^^^

These handlers help shed some light on the status of the underlying sphinx processes managed by ``esbonio``.

**sphinx/clientCreated**

Emitted when a new process is created.

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/esbonio.lua

   function client_created(err, result, ctx, config)
     vim.notify("Sphinx client created in " .. result.scope, vim.log.levels.INFO)
   end

   function app_created(err, result, ctx, config)
     vim.notify("Application created", vim.log.levels.INFO)
   end

   function client_errored(err, result, ctx, config)
     vim.notify("Client error: " .. result.error, vim.log.levels.ERROR)
   end

   function client_destroyed(err, result, ctx, config)
     vim.notify("Sphinx client destroyed", vim.log.levels.INFO)
   end

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/esbonio.lua

   return {
     setup = setup
   }


Python
^^^^^^

I currently use the :gh:`microsoft/pyright` language server for Python projects.

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/python.lua

   function setup(opts)
      opts = opts or {}

      if not opts.capabilities then
        opts.capabilities = vim.lsp.protocol.make_client_capabilities()
      end

      require('lspconfig').pyright.setup {
        capabilities = capabilities,
        settings = {
          python = {
          }
        }
      }
   end

.. code-block:: lua
   :filename: nvim/lua/alc/lsp/python.lua

   return {
     setup = setup
   }



Telescope
---------

The ``vertico`` of the neovim world, telescope offers a nice "select item from list" UI

.. code-block:: lua
   :filename: nvim/lua/alc/telescope.lua

   return {
     'nvim-telescope/telescope.nvim',
     event = 'VimEnter',
     branch = '0.1.x',
     dependencies = {
       'nvim-lua/plenary.nvim',
       'nvim-telescope/telescope-ui-select.nvim',
     },
     config = function()
       local themes = require('telescope.themes')

       require('telescope').setup {
         defaults = themes.get_ivy(opts)
       }

       pcall(require('telescope').load_extension, 'ui-select')

       local builtin = require 'telescope.builtin'
       vim.keymap.set('n', '<leader>ff', builtin.find_files)
     end
   }

Libraries & Helpers
-------------------

What follows is a series of helper libraries I've written to support the configuration above.

``alc.devcontainer``
^^^^^^^^^^^^^^^^^^^^

Thanks to switching to :gh:`ublue-os/bluefin` (well, Aurora) I'm finally got a setup where devcontainers work for me.
This helper library helps me make use of the :gh:`devcontainers/cli` from within ``nvim``.

The following function will check to see if there is a ``.devcontainer/`` for the repo and return the relevant
workspace folder if it exists.

.. code-block:: lua
   :filename: nvim/lua/alc/devcontainer.lua

   function workspace()
     local cwd = vim.uv.cwd()
     if not cwd then
       return nil
     end

     local repo = require('lspconfig.util').find_git_ancestor(cwd)
     if not repo then
       return nil
     end

     local devcontainer = vim.fs.joinpath(repo, '.devcontainer')
     if not vim.uv.fs_stat(devcontainer) then
       return nil
     end

     return repo
   end

Finally, export all the public functions from this module

.. code-block:: lua
   :filename: nvim/lua/alc/devcontainer.lua

   return {
     workspace = workspace
   }
