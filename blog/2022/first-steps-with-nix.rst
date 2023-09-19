.. post:: 2022-12-27
   :tags: nix, esbonio, python
   :author: Alex Carney
   :language: en
   :excerpt: 4

My First Steps with Nix
=======================

.. highlight:: none

Nix, depending on the context, can refer to a `programming language`_, a `package manager`_ or a `Linux Distro`_.

Personally, I'm most insterested in the package manager aspect and the promise of it being able to create declarative, reproducable development environments.
With a configuration file and the `nix develop`_ command you can activate a kind of "virtual environment" that contains not just your Python packages - but *any* program defined by the configuration!

I find that idea particuarly exciting when working on a language server like `esbonio`_, since it needs to be able to work against a variety of Python versions, Sphinx versions, as well as various code editors and all their versions!
Having the ability to define a particular configuration and have some tool automatically recreate it would be amazing.

But I'm getting ahead of myself, let's see if I can get to a point where I can easily test ``esbonio`` against a range of Python versions.

Intalling Nix
-------------

What a nightmare! 😭

I should say though, my issues aren't really Nix's fault.
Trying to install Nix directly on `Fedora Kinoite`_ means dealing with issues caused by SELinux (which the Nix installer does `not support <https://github.com/NixOS/nix/issues/2374>`__) and working around the immutable root filesystem.

Basically, don't do as I do! 😄

If you do find yourself in my situation though, here's a few things you might find useful

- `This guide <https://gist.github.com/matthewpi/08c3d652e7879e4c4c30bead7021ff73>`__ will get you 90% of the way, I was able to piece together the remaining steps from links in the comments.

- The Nix installer has been updated since the guide was written to bail if it detects that SELinux has been enabled.
  You will need to patch out the ``check_selinux`` function in the ``install-multi-user`` script in the release tarball that the Nix installer downloads.

- If you get a cryptic ::

     error: could not set permissions on '/nix/var/nix/profiles/per-user' to 755: Operation not permitted

  message whenever you run a nix command, chances are the nix-daemon is not running.
  Use ``systemctl status nix-daemon.service`` to check its status.

- If you see an error in the output of ``systemctl status nix-daemon.service`` along the lines of::

     nix-daemon.service: Failed to locate executable /nix/store/xdlpraypxdimjyfrr4k06narrv8nmfgh-nix-2.11.1/bin/nix-daemon: Permission denied

  you need to re-apply the SELinux policies defined in the guide linked above by running ``sudo restorecon -RF /nix``


A Simple Flake
--------------

.. note::

   I'm not the best person to learn how to use Nix from - I'm still trying to figure it out myself!
   Instead here are a few resources that I've found useful which go into more detail.

   - `Nix Flakes: An Introduction <https://xeiaso.net/blog/nix-flakes-1-2022-02-21>`__, part one of a `series <https://xeiaso.net/blog/series/nix-flakes>`__ of posts.
   - Jon Ringer's `Youtube Channel <https://www.youtube.com/@elitespartan117j27>`__


From what I can gather, `flakes`_ are a good starting point as they have a well defined structure and seem to be where things are going when it comes to Nix based workflows.

As mentioned in the intro I'd like to get to the point where I can easily test ``esbonio`` against a range of Python versions, so let's start off by writing a ``flake.nix`` that provides a ``devShell`` containing Python.

.. code-block:: nix

   {
     description = "The Esbonio language server";

     inputs = {
       nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
       utils.url = "github:numtide/flake-utils";
     };

     outputs = { self, nixpkgs, utils }:
       utils.lib.eachDefaultSystem (system:
         let pkgs = import nixpkgs { inherit system; }; in {

         devShell = with pkgs;
            mkShell {
               packages = [ python3 ];
            };
         }
      );
   }

Using ``nix flake show`` we can see what outputs are produced by this flake

.. code-block:: console

   $ nix flake show
   warning: Git tree '/var/home/alex/Projects/esbonio' is dirty
   error: getting status of '/nix/store/9s8zs1hrqiingklv86fd18x2mbgsfw0w-source/lib/esbonio/flake.nix': No such file or directory

Oh! I always forget, when working with flakes nix will only see a file if it is tracked by git - we don't need to commit it, but it needs to at least be staged.

.. code-block:: console

   $ git add flake.nix
   $ nix flake show
   warning: Git tree '/var/home/alex/Projects/esbonio' is dirty
   git+file:///var/home/alex/Projects/esbonio?dir=lib%2fesbonio
   └───devShell
      ├───aarch64-darwin: development environment 'nix-shell'
      ├───aarch64-linux: development environment 'nix-shell'
      ├───x86_64-darwin: development environment 'nix-shell'
      └───x86_64-linux: development environment 'nix-shell'

This shows that we've already defined development environments for MacOS and Linux on both x86 and Arm platforms!
To "activate" the correct environment we only need to run ``nix develop``.
Nix is smart enough to choose the one compatible with our current system and will proceed to setup all the packages required for that environment.

.. code-block:: console

   $ nix develop
   (nix-shell) $ command -v python
   /nix/store/qc8rlhdcdxaf6dwbvv0v4k50w937fyzj-python3-3.10.8/bin/python

   (nix-shell) $ python
   Python 3.10.8 (main, Oct 11 2022, 11:35:05) [GCC 11.3.0] on linux
   Type "help", "copyright", "credits" or "license" for more information.
   >>>

Nice!

.. tip::

   See `here <https://github.com/alcarney/dotfiles/blob/90d90d1d2f67a03a7f8b73803784b13362027e13/bash/20-prompt#L12-L20>`__ for details on how I configured my bash prompt to detect if I'm in a nix shell or not.

Adding Python Packages
----------------------

Of course, this environment isn't that useful at the moment as any of the packages required for ``esbonio`` and its test suite are not available

.. code-block:: console

   (nix-shell) $ pytest
   bash: pytest: command not found

If we're lucky, the packages we need are already part of `nixpkgs`_ and we just need to add them to the devShell's ``packages``.

.. code-block:: nix

   devShell = with pkgs;
     mkShell {
       packages = [
         python3

         # esbonio's dependencies
         python3Packages.appdirs
         python3Packages.sphinx
         python3Packages.pygls
         python3Packages.typing-extensions

         # test suite dependencies
         python3Packages.mock
         python3Packages.pytest
         python3Packages.pytest-lsp
         python3Packages.pytest-timeout
       ];
     };

And reactivate the environment

.. code-block:: console

   $ nix develop
   warning: Git tree '/var/home/alex/Projects/esbonio' is dirty
   error: attribute 'pytest-lsp' missing

         at /nix/store/ll2pir6ii65n4cplan9iykxy7cksw6k8-source/lib/esbonio/flake.nix:27:13:

            26|             python3Packages.pytest
            27|             python3Packages.pytest-lsp
              |             ^
            28|             python3Packages.pytest-timeout
   (use '--show-trace' to show detailed location information)

Unfortunately, ``pytest-lsp`` is not available through nixpkgs but since it's an unknown library I wrote to help test ``esbonio`` I can't say I'm surprised! 😄
It should however, be relatively straightforward to package it ourselves, especially if we use `an example <https://github.com/NixOS/nixpkgs/blob/nixos-unstable/pkgs/development/python-modules/pytest-timeout/default.nix>`__ from the nixpkgs repo as a guide.

.. code-block:: nix

   # In ./nix/pytest-lsp.nix
   { pythonPackages }:

   pythonPackages.buildPythonPackage rec {
     pname = "pytest-lsp";
     version = "0.1.3";

     src = pythonPackages.fetchPypi {
       inherit pname version;
       sha256 = "sha256-WxTh9G3tWyGzYx1uHufkwg3hN6jTbRjlGLKJR1eUNtY=";
     };

     buildInputs = [
       pythonPackages.appdirs
       pythonPackages.pygls
       pythonPackages.pytest
     ];

     propagatedBuildInputs = [
       pythonPackages.pytest-asyncio
     ];

     # Disable tests
     doCheck = false;
   }

You probably don't want to use this as an example of packaging a Python package with Nix, as I don't fully understand what I'm doing and I've taken a few shortcuts (like disabling tests), but here's a few notes.

- The ``{ pythonPackages } :`` syntax at the top of the file is defining a function that accepts ``pythonPackages`` as an argument.
  This is what allows this definition to be used with multiple Python versions later on in this blog post.

- As the name implies, the ``fetchPypi`` function is used to pull the sources for ``pytest-lsp`` straight from PyPi.

- ``propagtedBuildInputs`` are also available for use at runtime, while ``buildInputs`` are "hidden" from the final runtime environment.

Then, to use this package definition in our ``flake.nix`` file we use the ``callPackage`` function and pass it the correct python package set.

.. _first-steps-nix-call-pytest-lsp:

.. code-block:: nix

   # In ./flake.nix
   let
      pkgs = import nixpkgs { inherit system; };
      pytest-lsp = pkgs.callPackage ./nix/pytest-lsp.nix { pythonPackages = pkgs.python3Packages; };
   in {
      devShell = with pkgs;
        mkShell {
          packages = [
            # ...
            pytest-lsp
          ];
        };
   }

Hopefully, we now have all we need to run the test suite.

.. code-block:: console

   (nix-shell) $ pytest
   =========================================================================================================== test session starts ============================================================================================================
   platform linux -- Python 3.10.8, pytest-7.1.3, pluggy-1.0.0
   rootdir: /var/home/alex/Projects/esbonio/lib/esbonio, configfile: pyproject.toml
   plugins: typeguard-2.13.3, lsp-0.1.3, asyncio-0.19.0, timeout-2.1.0
   asyncio: mode=auto
   collected 0 items / 1 error

   ================================================================================================================== ERRORS ==================================================================================================================
   ______________________________________________________________________________________________________ ERROR collecting test session _______________________________________________________________________________________________________
   /nix/store/qc8rlhdcdxaf6dwbvv0v4k50w937fyzj-python3-3.10.8/lib/python3.10/importlib/__init__.py:126: in import_module
      ...
   tests/sphinx-default/conftest.py:12: in <module>
      from esbonio.lsp.sphinx import InitializationOptions
   E   ModuleNotFoundError: No module named 'esbonio'
   ========================================================================================================= short test summary info ==========================================================================================================
   ERROR  - ModuleNotFoundError: No module named 'esbonio'

Ah... looks like we have to package ``esbonio`` itself, but we already know how to do that, aside from dependencies the only major difference is where we fetch the sources from.

.. code-block:: nix

   # In ./nix/esbonio.nix

   src = ./..

Now we should have everything setup correctly! 🤞

.. code-block:: console

   ==================================== test session starts =====================================
   platform linux -- Python 3.10.8, pytest-7.1.3, pluggy-1.0.0
   rootdir: /var/home/alex/Projects/esbonio/lib/esbonio, configfile: pyproject.toml
   plugins: typeguard-2.13.3, lsp-0.1.3, asyncio-0.19.0, timeout-2.1.0
   asyncio: mode=auto
   collected 2487 items

   ...

   =============== 2475 passed, 4 skipped, 8 xfailed in 132.96s (0:02:12) =======================

Success!

.. _first-steps-nix-multiple-python-versions:

Multiple Python Versions
------------------------


Switching to a Nix-ish style of pseudo code for a moment, let's summarize how our flake is currently defined.
We defined a function which takes a ``system`` and produces an attribute set (think Python dictionary) with a ``devShell`` field ::

  f(system) = { devShell = <devShell for system> }

We then passed that function to the ``eachDefaultSystem`` helper from the `flake-utils`_ repo.
This calls our function with each of the `default system architectures`_ before transforming it into a structure compatible with the flake `output schema`_ ::

  eachDefaultSystem(f) = applyTransform { aarch64-linux = f(aarch64-linux), ... }
                       = applyTransform { aarch64-linux = { devShell = <devShell for aarch64-linux> }, ... }
                       = { devShell.aarch64-linux.default = <devShell for aarch64-linux>, ... }

Now that we want to support multiple Python versions however, we want to define a function that returns an attribute set with a devShell for each Python version ::

  f(system) = { py37 = <py37 devShell for system>, py38 = <py38 devShell for system>, ... }

Which we can then pass to a ``mysteryHelper`` function to perform a similar (but structurally distinct!) transformation on the results of our function ``f`` ::

  devShells = mysteryHelper(f)
            = applyTransform { aarch64-linux = f(aarch64-linux), ... }
            = applyTransform {
                               aarch64-linux  = { py37 = <py37 devShell for aarch64-linux>,
                                                  py38 = <py38 devShell for aarch64-linux>,
                                                  ...
                                                },
                               ...,
                             }
            = {
                aarch64-linux.py37 = <py37 devShell for aarch64-linux>,
                aarch64-linux.py38 = <py38 devShell for aarch64-linux>,
                ...
              }

That's the idea at least, now to translate it into real Nix code.

Thankfully, finding an implementation for ``mysteryHelper`` isn't too difficult as the ``flake-utils`` repo provides ``eachDefaultSystemMap`` which does precisely what we want.

.. code-block:: nix

   outputs = { self, nixpkgs, utils }:
     devShells = utils.lib.eachDefaultSystemMap (system:
       f system;
     );

Now to replace our imaginary function ``f`` with an expression that defines our devShells.

.. important::

   Notice that we now assign to ``devShells``?

   It turns out that ``nix`` the command line tool does a little
   `transformation <https://github.com/NixOS/nix/blob/3dbf9b5af5950b615ec685c1f4155b1c8698bb78/src/nix/flake.cc#L517>`__
   to turn a ``devShell`` entry into a valid ``devShells`` entry.
   Unfortunately, this transformation only works when you define a single shell per system!

   Now that we're defining multiple shells per system, we have to make sure to use ``devShells`` - it took me a *long* time to spot this!

We could simply copy-paste the devShell definition from the previous section a bunch of times and switch out the Python version.

However, since the definitions for each Python version are going to be so similar, a better approach would be to define our own helper that would map a function over a list of versions and have it build the attribute set for us.

It turns out that the
`implementation <https://github.com/numtide/flake-utils/blob/5aed5285a952e0b949eb3ba02c12fa4fcfef535f/default.nix#L150>`__
of ``eachDefaultSystemMap`` is almost identical to what we need, so it was easy enough to adapt it to this use case.

.. code-block:: nix

   eachPythonVersion = versions: f: builtins.listToAttrs (builtins.map (version: { name = "py${version}"; value = f version; }) versions);

Bringing it all together gives us this final flake definition

.. code-block:: nix

  outputs = { self, nixpkgs, utils }:

    let
      eachPythonVersion = versions: f: builtins.listToAttrs (builtins.map (version: {name = "py${version}"; value = f version; }) versions);
    in {

    devShells = utils.lib.eachDefaultSystemMap (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
        eachPythonVersion [ "37" "38" "39" "310" "311" ] (pyVersion:
          let
            pytest-lsp = pkgs.callPackage ./nix/pytest-lsp.nix { pythonPackages = pkgs."python${pyVersion}Packages"; };
            esbonio = pkgs.callPackage ./nix/esbonio.nix { pythonPackages = pkgs."python${pyVersion}Packages"; };
          in

          with pkgs; mkShell {
            name = "py${pyVersion}";

            packages = [
              pkgs."python${pyVersion}"

              esbonio

              # test suite dependencies
              pkgs."python${pyVersion}Packages".mock
              pkgs."python${pyVersion}Packages".pytest
              pytest-lsp
              pkgs."python${pyVersion}Packages".pytest-timeout
            ];
          }
      )
    );
  };

With any luck, we should now see a per-python version devShell appear in the output of ``nix flake show``

.. code-block:: console

   $ nix flake show
   git+file:///var/home/alex/Projects/esbonio?dir=lib%2fesbonio&ref=refs%2fheads%2fnix&rev=4a548327974dff1750099df4d793638a64b663e6
   └───devShells
       ├───aarch64-darwin
       │   ├───py310: development environment 'py310'
       │   ├───py311: development environment 'py311'
       │   ├───py37: development environment 'py37'
       │   ├───py38: development environment 'py38'
       │   └───py39: development environment 'py39'
       ├───aarch64-linux
       │   ├───py310: development environment 'py310'
       │   ├───py311: development environment 'py311'
       │   ├───py37: development environment 'py37'
       │   ├───py38: development environment 'py38'
       │   └───py39: development environment 'py39'
       ├───x86_64-darwin
       │   ├───py310: development environment 'py310'
       │   ├───py311: development environment 'py311'
       │   ├───py37: development environment 'py37'
       │   ├───py38: development environment 'py38'
       │   └───py39: development environment 'py39'
       └───x86_64-linux
           ├───py310: development environment 'py310'
           ├───py311: development environment 'py311'
           ├───py37: development environment 'py37'
           ├───py38: development environment 'py38'
           └───py39: development environment 'py39'

To reference a given environment we'd use the ``.#<envname>`` syntax when calling ``nix develop``.
The ``--command`` flag also allows us to run a command within the named environment without having to activate it first!

.. code-block:: console

   $ nix develop .#py310 --command pytest
   =========================== test session starts ================================
   platform linux -- Python 3.10.8, pytest-7.1.3, pluggy-1.0.0
   rootdir: /var/home/alex/Projects/esbonio/lib/esbonio, configfile: pyproject.toml
   plugins: typeguard-2.13.3, lsp-0.1.3, asyncio-0.19.0, timeout-2.1.0
   asyncio: mode=auto
   collected 2508 items

   ...

   ======== 2496 passed, 4 skipped, 8 xfailed in 344.10s (0:05:27) ================

   $ nix develop .#py39 --command pytest
   =========================== test session starts ================================
   platform linux -- Python 3.9.15, pytest-7.1.3, pluggy-1.0.0
   rootdir: /var/home/alex/Projects/esbonio/lib/esbonio, configfile: pyproject.toml
   plugins: typeguard-2.13.3, lsp-0.1.3, asyncio-0.19.0, timeout-2.1.0
   asyncio: mode=auto
   collected 2508 items

   ...

   ======== 2496 passed, 4 skipped, 8 xfailed in 344.10s (0:05:44) ================

Achievement unlocked! 🏆

Next Steps
----------

This was mainly a "Hello, World" type exercise looking to see if I could get Nix up and running in a real project, but so far I haven't achieved anything you can't already do with traditional Python tools like `tox`_.
However, this should hopefully serve as a good foundation on which I can explore

- Changing the source where dependent libraries are fetched from (e.g. local vs git vs PyPi)
- Using overlays (these might help with the previous point?)
- Defining environments that contain particular text editor configurations.

If you are interested, you can find the final Nix definitions
`here <https://github.com/alcarney/esbonio/commit/f62e1d486bb7899d802bfd668f98f21b71702317>`__.

.. _default system architectures: https://github.com/numtide/flake-utils/blob/5aed5285a952e0b949eb3ba02c12fa4fcfef535f/default.nix#L3-L8
.. _esbonio: https://github.com/swyddfa/esbonio/
.. _Fedora Kinoite: https://kinoite.fedoraproject.org/
.. _flakes: https://nixos.wiki/wiki/Flakes
.. _flake-utils: https://github.com/numtide/flake-utils
.. _Linux Distro: https://nixos.org/manual/nixos/stable/#sec-installation
.. _nix develop: https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-develop.html
.. _nixpkgs: https://github.com/NixOS/nixpkgs
.. _output schema: https://nixos.wiki/wiki/Flakes#Output_schema
.. _programming language: https://nixos.org/manual/nix/stable/language/index.html
.. _package manager: https://nixos.org/manual/nixpkgs/stable/#preface
.. _tox: https://tox.wiki/en/latest/index.html
