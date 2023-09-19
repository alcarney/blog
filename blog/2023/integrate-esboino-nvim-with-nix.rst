.. post:: 2023-04-21
   :tags: nix, python, esbonio
   :author: Alex Carney
   :language: en
   :excerpt: 3

Integrating Esbonio with Neovim Using Nix
=========================================

So far I've been learning how to use Nix by trying to package and define development shells for `esbonio`_ (see :ref:`here <tag-nix>` if you are interested).
While useful, the end result is not too dissimilar to what you can get with standard Python tooling.
Indeed, the main reason I started looking into Nix was the promise of it being able to manage more than just Python libraries.

Since ``esbonio`` is a language server, it would be useful for Nix to create standardised environments where the language server is pre-configured for a given editor - great for debugging and demos!

In this blog post I try to define an environment in which Neovim is installed and configured to use the ``esbonio`` language server for reStructuredText files.

.. admonition:: Try it yourself!

   If I've done all my homework right, you **should** be able to try the result of this blog post for yourself
   Assuming you have nix installed

   .. code-block:: console

      $ nix run github:alcarney/esbonio?rev=a077efeed176dcad2ae5e4fd221179d266f88ca1

   should be the only command you need.
   Let me know if you run into any issues!

Defining Applications
---------------------

One of the `defined flake outputs <https://nixos.wiki/wiki/Flakes#Output_schema>`__ is ``apps.<system>.<name>`` which as the name suggests allows you to export applications from a flake.

.. code-block:: nix

   {
     description = "Esbonio";

     inputs = {
       nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
       utils.url = "github:numtide/flake-utils";
     };

     outputs = { self, nixpkgs, utils }:
       utils.lib.eachDefaultSystem (system:
         let
           pkgs = import nixpkgs { inherit system; };
         in {
           apps.default = { type = "app"; program = "${pkgs.neovim}/bin/nvim"; };
         }
       );
   }

This simple ``flake.nix`` exports neovim as an application which we can launch by running ``nix run .`` from the folder containing this flake.

.. figure:: /images/nix-nvim-myconfig.png
   :width: 50%
   :align: center

Which works as expected however, it's also picking up my personal config - not so useful when you're trying to create a standard, isolated environment.

Isolated Configuration
----------------------

As with most things in Nix, the neovim package definition allows for certain fields to be overridden - including the config.
Let's start by trying provide an empty ``init.vim`` file.

.. code-block:: nix

   utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        neovim = pkgs.neovim.override {
          configure = {
            customRC = ''
            '';
          };
        };
      in {
        apps.default = {
          type = "app";
          program = "${neovim}/bin/nvim";
        };
      }
    );

And try ``nix run .`` again

.. figure:: /images/nix-nvim-emptyconfig.png
   :width: 50%
   :align: center


Which worked! Sort of... well... not really. 😕

It worked in the sense that it loaded the empty ``init.vim`` file we specified (notice that the screenshot above has no line numbers).
However, it's not truly isolated since it went ahead and loaded my plugins anyway due to my user's home folder being included in the ``runtimepath``

.. tip::

   To get the contents of your `runtimepath <https://neovim.io/doc/user/options.html#'runtimepath'>`__
   into a buffer.

   #. In ``INSERT`` mode type ``<c-r>=&rtp`` and hit enter
   #. Replace all commas with newlines ``:%s/,/\r/g``


So how can we exclude them?

``nvim --clean``
^^^^^^^^^^^^^^^^

Reading through `:h 'runtimepath' <https://neovim.io/doc/user/options.html#'runtimepath'>`__ there's a lot of detail around which paths are searched by default and in what order.
But right at the end there's a little note

.. pull-quote::

   With ``--clean`` the home directory entries are not included.

Which sounds like just what we need!
The question is... how do we start ``nvim`` with that flag?

Looking around the nixpkgs repo for a bit I found a set of
`test cases <https://github.com/NixOS/nixpkgs/blob/d8f05d468eb7b0a97cef73b9b6631613cfac13a7/pkgs/applications/editors/neovim/tests/default.nix>`__
that made use of a
`utility <https://github.com/NixOS/nixpkgs/blob/d8f05d468eb7b0a97cef73b9b6631613cfac13a7/pkgs/applications/editors/neovim/utils.nix#L24>`__
for generating a config, along with a
`wrapper <https://github.com/NixOS/nixpkgs/blob/d8f05d468eb7b0a97cef73b9b6631613cfac13a7/pkgs/applications/editors/neovim/wrapper.nix>`__
which converts the given config into a shell script.
This shell script pulls together various components from ``/nix/store``, before ultimately launching our isolated instance of neovim.

.. dropdown:: Example wrapper script
   :class-container: admonition info
   :class-title: admonition-title

   Here is an example of a wrapper script generated by nix.

   .. code-block:: bash

      #! /nix/store/0hx32wk55ml88jrb1qxwg5c5yazfm6gf-bash-5.2-p15/bin/bash -e
      export NVIM_SYSTEM_RPLUGIN_MANIFEST='/nix/store/jjl5fy7dc5cxvc7mi781vxbk8ag89ih0-neovim-0.8.3-esbonio/rplugin.vim'
      export GEM_HOME='/nix/store/4mmkiw8n1nhlfsnh4g2kijzkxnp6fyxb-neovim-ruby-env/lib/ruby/gems/2.7.0'
      PATH=${PATH:+':'$PATH':'}
      if [[ $PATH != *':''/nix/store/4mmkiw8n1nhlfsnh4g2kijzkxnp6fyxb-neovim-ruby-env/bin'':'* ]]; then
          PATH=$PATH'/nix/store/4mmkiw8n1nhlfsnh4g2kijzkxnp6fyxb-neovim-ruby-env/bin'
      fi
      PATH=${PATH#':'}
      PATH=${PATH%':'}
      export PATH
      LUA_PATH=${LUA_PATH:+';'$LUA_PATH';'}
      LUA_PATH=${LUA_PATH/';''/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/share/lua/5.1/?/init.lua'';'/';'}
      LUA_PATH='/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/share/lua/5.1/?/init.lua'$LUA_PATH
      LUA_PATH=${LUA_PATH#';'}
      LUA_PATH=${LUA_PATH%';'}
      export LUA_PATH
      LUA_PATH=${LUA_PATH:+';'$LUA_PATH';'}
      LUA_PATH=${LUA_PATH/';''/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/share/lua/5.1/?.lua'';'/';'}
      LUA_PATH='/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/share/lua/5.1/?.lua'$LUA_PATH
      LUA_PATH=${LUA_PATH#';'}
      LUA_PATH=${LUA_PATH%';'}
      export LUA_PATH
      LUA_CPATH=${LUA_CPATH:+';'$LUA_CPATH';'}
      LUA_CPATH=${LUA_CPATH/';''/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/lib/lua/5.1/?.so'';'/';'}
      LUA_CPATH='/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/lib/lua/5.1/?.so'$LUA_CPATH
      LUA_CPATH=${LUA_CPATH#';'}
      LUA_CPATH=${LUA_CPATH%';'}
      export LUA_CPATH
      exec -a "$0" "/nix/store/1czj8mydgi30kyfimq6q4ifh06q131ch-neovim-unwrapped-0.8.3/bin/nvim"  -u /nix/store/fqjv4r08pl8k3vhy6ijxddrn8gpq2h7z-init.vim '--cmd' 'let g:loaded_node_provider=0 | let g:loaded_python_provider=0 | let g:python3_host_prog='\''/nix/store/jjl5fy7dc5cxvc7mi781vxbk8ag89ih0-neovim-0.8.3-esbonio/bin/nvim-python3'\'' | let g:ruby_host_prog='\''/nix/store/jjl5fy7dc5cxvc7mi781vxbk8ag89ih0-neovim-0.8.3-esbonio/bin/nvim-ruby'\''' "$@"

After some trial and error I was able to put together the following

.. code-block:: nix

   utils.lib.eachDefaultSystem (system:
     let
       pkgs = import nixpkgs { inherit system; };
       nvim-cfg = pkgs.neovimUtils.makeNeovimConfig {
         extraName = "-esbonio";
         customRC = ''
           set number
         '';
       };
       neovim-config = pkgs.lib.attrsets.updateManyAttrsByPath [
         {
           path = ["wrapperArgs"];
           update = old: old ++ [
             "--add-flags" "--clean"
           ];
         }
       ] nvim-cfg;
       neovim = pkgs.wrapNeovimUnstable pkgs.neovim-unwrapped neovim-config;
     in {
       apps.default = {
         type = "app";
         program = "${neovim}/bin/nvim";
       };
     }
   );

To summarize

- ``pkgs.neovimUtils.makeNeovimConfig`` as the name suggests is a utility that generates a neovim "config".
  "config" in this case is an attribute set containing all the arguments required to call ``pkgs.wrapNeovimUnstable``.

- One of these arguments is called ``wrapperArgs`` which contains the list of cli arguments to pass to the wrapped instance of neovim. Well almost.

  ``wrapperArgs`` aren't passed through to neovim directly, they are passed to a utility called ``makeWrapper`` which is a small program with it's own
  `set of arguments <https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/setup-hooks/make-wrapper.sh#L13-L35>`__
  that allow you to describe how you want to wrap an underlying executable.
  This is why I'm appending ``"--add-flags" "--clean"`` to ``wrapperArgs`` and not just ``--clean``.

- Finally, the config and base neovim derivation are passed to ``pkgs.wrapNeovimUnstable`` to bring it all together.

Unfortunately, after all that I still didn't end up with the result I was looking for

.. figure:: /images/nix-nvim-clean.png
   :width: 50%
   :align: center

   No plugins, but also note no line numbers 😢

Not only does the ``--clean`` flag prevent neovim from loading the plugins in my home folder, it also stopped neovim from loading the contents of my ``customRC`` - something I would've found out if I'd actually read the help text for ``--clean`` itself

.. pull-quote::

   ``--clean`` - Mimics a fresh install of Nvim:

   - Skips initializations from files and environment variables.

   - No 'shada' file is read or written.

   - Excludes user directories from 'runtimepath'

   - Loads builtin plugins, unlike -u NONE -i NONE.

It should be possible to work around this though by telling neovim to ``source`` our init file as well as giving it the ``--clean`` flag.
Let's take a look at the ``exec`` command nix is currently generating for us in the wrapper script.

.. code-block:: bash

   exec -a "$0" "/nix/store/1czj8mydgi30kyfimq6q4ifh06q131ch-neovim-unwrapped-0.8.3/bin/nvim" \
        -u /nix/store/fqjv4r08pl8k3vhy6ijxddrn8gpq2h7z-init.vim \
        --cmd '...' \
        --clean \
        "$@"

The ``-u /nix/store/fqj...-init.vim`` argument contains the contents of our ``customRC`` and I think changing the command to something like

.. code-block:: bash

   exec -a "$0" "/nix/store/1czj8mydgi30kyfimq6q4ifh06q131ch-neovim-unwrapped-0.8.3/bin/nvim" \
        --clean \
        --cmd 'source /nix/store/fqjv4r08pl8k3vhy6ijxddrn8gpq2h7z-init.vim' \
        "$@"

will result in the behaviour I'm looking for.

.. tip::

   So far I've neglected to mention how I'm finding the ``/nix/store`` path containing this wrapper script.
   Using the nix repl you can load your flake and inspect the values it contains.

   .. code-block:: console

      $ nix repl
      Welcome to Nix 2.11.1. Type :? for help.

      nix-repl> :lf .        # load the flake located at '.'
      warning: Git tree '/var/home/alex/Projects/esbonio-nix' is dirty
      Added 9 variables.

      nix-repl> outputs.apps.x86_64-linux.default
      { program = "/nix/store/knr1nfdmg9ld0xg813hb7ljl68060jlv-neovim-0.8.3-esbonio/bin/nvim"; type = "app"; }

   It's also useful for figuring out how the many utilities in nixpkgs work

   .. code-block:: console

      nix-repl> pkgs = import inputs.nixpkgs {system = "x86_64-linux"; }

      nix-repl> config = pkgs.neovimUtils.makeNeovimConfig { customRC = "set number"; }

      nix-repl> config.wrapperArgs
      [ "--inherit-argv0" "--add-flags" "'--cmd' 'let g:loaded_node_provider=0 | let g:loaded_python_provider=0 | let g:python3_host_prog='\\''/1rz4g4znpzjwh1xymhjpm42vipw92pr73vdgl6xs1hycac8kf2n9/bin/nvim-python3'\\'' | let g:ruby_host_prog='\\''/1rz4g4znpzjwh1xymhjpm42vipw92pr73vdgl6xs1hycac8kf2n9/bin/nvim-ruby'\\'''" "--set" "GEM_HOME" "/nix/store/4mmkiw8n1nhlfsnh4g2kijzkxnp6fyxb-neovim-ruby-env/lib/ruby/gems/2.7.0" "--suffix" "PATH" ":" "/nix/store/4mmkiw8n1nhlfsnh4g2kijzkxnp6fyxb-neovim-ruby-env/bin" "--prefix" "LUA_PATH" ";" "/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/share/lua/5.1/?.lua;/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/share/lua/5.1/?/init.lua" "--prefix" "LUA_CPATH" ";" "/nix/store/nlmk08cmald0zi7fc6hgpdqrjz7lh8qj-luajit-2.1.0-2022-10-04-env/lib/lua/5.1/?.so" ]

   .. raw:: html

      <p class="m-0 text-white dark:text-gray-800">.</p>

Unfortunately, I could not see an obvious way to rewrite the arguments to ``exec``.
The store path for the ``init.vim`` file is only generated in the depths of the ``wrapNeovimUnstable`` as it is written to disk and trying to manipulate ``wrapperArgs`` to extract it isn't something I'm willing to attempt in Nix just yet!

A New Approach
^^^^^^^^^^^^^^

It was at this point I started looking around to see what other people have come up with and before long I found
`this reddit thread <https://www.reddit.com/r/neovim/comments/v45zkv/any_solution_for_isolated_neovimvim_environments/>`__
which linked
`this flake <https://git.sr.ht/~whynothugo/dotfiles/tree/e7c0e701/item/v/flake.nix>`__
that looked very promising.
Not only did it provide a way of creating an isolated config but it also showed how to manage plugins and external binaries!

Following its example I was able to come up with the following definition

.. code-block:: nix

   utils.lib.eachDefaultSystem (system:
     let
       pkgs = import nixpkgs { inherit system ; };
       initVim = ''
         set number
       '';
       paths = pkgs.lib.makeBinPath [
         pkgs.neovim
       ];
       pluginList = with pkgs.vimPlugins; [
         nvim-lspconfig
       ];
       plugins = pkgs.stdenv.mkDerivation {
         name = "esbonio-nvim-plugins";
         buildCommand = ''
           mkdir -p $out/nvim/site/pack/plugins/start/
           ${pkgs.lib.concatMapStringsSep "\n" (path: "ln -s ${path} $out/nvim/site/pack/plugins/start/")  pluginList }
         '';
       };
       neovim = pkgs.writeShellScriptBin "nvim" ''
         export PATH=${paths}:$PATH
         export XDG_CONFIG_DIRS=
         export XDG_DATA_DIRS=${plugins.outPath}
         nvim --clean --cmd source ${pkgs.writeText "init.vim" initVim} "$@"
       '';
     in {
        apps.default = {
          type = "app";
          program = "${neovim}/bin/nvim";
        };
      }
   );

And trying ``nix run .`` once more

.. figure:: /images/nix-nvim-isolated.png
   :width: 50%
   :align: center

   Success!

Not only did I end up with the correct configuration, the ``runtimepath`` finally contains just the paths that are necessary!

Integrating Esboino
-------------------

Next we need to make sure the esbonio language server is available in this environment and include the necessary configuration for it in the config.

Including the server should be pretty straightforward as we get to reuse the overlay defined :doc:`previously </blog/2023/nix-overlays-p2>`.

.. code-block:: diff

     inputs = {
       nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
   +   esbonio.url = "path:lib/esbonio";
   +   esbonio.inputs.nixpkgs.follows = "nixpkgs";
       utils.url = "github:numtide/flake-utils";
     };

   - outputs = { self, nixpkgs, utils }:
   + outputs = { self, nixpkgs, esbonio, utils }:

    utils.lib.eachDefaultSystem (system:
      let
   -    pkgs = import nixpkgs { inherit system ; };
   +    pkgs = import nixpkgs { inherit system ; overlays = [ esbonio.overlays.default ];};
        initVim = ''
          set number
        '';
        paths = pkgs.lib.makeBinPath [
          pkgs.neovim
   +      pkgs.python310Packages.esbonio
        ];

**Should** being the key word here...

.. code-block:: console

   $ nix run .
   warning: Git tree '/var/home/alex/Projects/esbonio-nix' is dirty
   warning: updating lock file '/var/home/alex/Projects/esbonio-nix/flake.lock':
   • Added input 'esbonio':
       'path:lib/esbonio?lastModified=1&narHash=sha256-WiFypw4lUZo7P9h82NMudwb5DFV0Nde5cOu1SqDmhVQ=' (1970-01-01)
   • Added input 'esbonio/nixpkgs':
       follows 'nixpkgs'
   • Added input 'esbonio/pytest-lsp':
       'github:swyddfa/lsp-devtools/6ae80a24b55d2b6943b9d30805cf02440ebbaf5c?dir=lib%2fpytest-lsp' (2023-04-02)
   • Added input 'esbonio/pytest-lsp/nixpkgs':
       follows 'esbonio/nixpkgs'
   • Added input 'esbonio/pytest-lsp/utils':
       'github:numtide/flake-utils/93a2b84fc4b70d9e089d029deacc3583435c2ed6' (2023-03-15)
   • Added input 'esbonio/utils':
       'github:numtide/flake-utils/5aed5285a952e0b949eb3ba02c12fa4fcfef535f' (2022-11-02)
   warning: Git tree '/var/home/alex/Projects/esbonio-nix' is dirty
   error: undefined variable 'pytest-lsp'

          at /nix/store/96z740kkay7j0cbgmccj2mzbn5z8agvp-source/nix/esbonio-overlay.nix:22:11:

              21|           mock
              22|           pytest-lsp
                |           ^
              23|           pytest-timeout
   (use '--show-trace' to show detailed location information)

The overlay exported by the language server's flake doesn't include its dependency ``pytest-lsp`` which is provided through an overlay of its own.
A quick "fix" would be to also pull in the flake for pytest-lsp, but really the language server's flake should be exporting all of its dependencies.

Composing Overlays
^^^^^^^^^^^^^^^^^^

Thankfully, nixpkgs provides a function
`composeManyExtensions <https://github.com/NixOS/nixpkgs/blob/3eb57ca9451406a7131f54b8a90b82462ad89252/lib/fixed-points.nix#L86>`__
that handles this for us.
When exporting the overlay from within the language server's flake we can use it to merge the overlay from pytest-lsp with the overlay containing esbonio.

.. code-block::

   # In lib/esbonio/flake.nix
   overlays.default = self: super: nixpkgs.lib.composeManyExtensions [
     pytest-lsp-overlay
     esbonio-overlay
   ] self super

However, since ``flake.lock`` freezes the language server's flake as it was before we made this change we need to also update the lock file before trying again

.. code-block:: console

   $ nix flake lock --update-input esbonio
   warning: Git tree '/var/home/alex/Projects/esbonio-nix' is dirty
   warning: updating lock file '/var/home/alex/Projects/esbonio-nix/flake.lock':
   • Updated input 'esbonio':
       'path:lib/esbonio?lastModified=1&narHash=sha256-WiFypw4lUZo7P9h82NMudwb5DFV0Nde5cOu1SqDmhVQ=' (1970-01-01)
     → 'path:lib/esbonio?lastModified=1&narHash=sha256-QgSDxOPSrtsaqjeStalef07+bUE3qkzz7pJC4y43ltw=' (1970-01-01)
   warning: Git tree '/var/home/alex/Projects/esbonio-nix' is dirty

Now trying ``nix run .`` again neovim launches as before, running the command ``:r !python -m esbonio --help`` we can verify that the language server is indeed available to the editor.

.. figure:: /images/nix-nvim-esbonio-help.png
   :width: 50%
   :align: center

   Almost there!

.. admonition:: Editor's Note

   Since writing this section and taking the above screenshot, I have been unable to re-produce it!
   Now ``:r !python -m esbonio --help`` results in a ``esbonio: Module not found`` error...

   When debugging this, I'm not sure how the original ever worked since the flake definition does not include
   a Python interpreter meaning that ``python -m esbonio --help`` is running under the system Python.

   The fix then, was to switch from ``python -m esbonio --help`` to calling ``esbonio --help`` directly, which thankfully, did not require me to change any of the Nix code.

Configuring Neovim
^^^^^^^^^^^^^^^^^^

Now all that's left to do is updating our ``initVim`` variable to contain the relevant configuration for the language server.
Thanks to the
`example configuration <https://swyddfa.github.io/esbonio/docs/latest/en/lsp/getting-started.html?editor=neovim-lspconfig#examples>`__
available in the documentation, this can be as straightforward as replacing our hardcoded configuration with a call to Nix (the language's) builtin
`readFile <https://nixos.org/manual/nix/stable/language/builtins.html#builtins-readFile>`__
function.

.. code-block:: diff

    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system ; overlays = [ esbonio.overlays.default ];};
   -    initVim = ''
   -      set number
   -    '';
   +    initVim = builtins.readFile ./docs/lsp/editors/nvim-lspconfig/init.vim;
        paths = pkgs.lib.makeBinPath [
          pkgs.neovim
          pkgs.python310Packages.esbonio
        ];

And try opening a Sphinx project with it

.. figure:: /images/nix-nvim-esbonio-minimal.png
   :align: center
   :width: 50%

   It's not pretty, but it works!

Wrapping Up
-----------

The experience as is currently stands is not that inspiring however, with the nix foundations laid it's now more of a configuring neovim problem rather than a nix one!
I am mildly disappointed that this required to dive so deep on the specifics of how neovim is configured, since that probably means you'd have to go to a similar depth to incorporate other editors.
That said, once you've solved it for a given editor it's probably solved "forever".

Next I think I'd be interested in exploring how (or if it's even possible) to make these Nix definitions more dynamic e.g.

- Using the language server from ``$EDITOR`` using Python ``3.x``
- Run the language server tests, but with a local checkout of `pygls <https://github.com/openlawlibrary/pygls>`__
- Edit docs for ``$PROJECT`` using Sphinx ``vX``

Obviously, you could achieve a lot of that by just editing the Nix definitions and rebuilding but I wonder if it's possible to build in support for swapping parts out that can be wrapped up in a Makefile or similar 🤔

.. _esbonio: https://github.com/swyddfa/esbonio
