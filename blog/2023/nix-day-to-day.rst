.. post:: 2023-07-27
   :tags: nix, python, esbonio
   :author: Alex Carney
   :language: en
   :excerpt: 1

Nix: Day to Day Usage
=====================

This blog post marks a change in my usage of Nix, I'm (just!) past the point of trying to get *something* to work and now starting to incorporate it into some of my regular workflows.
So instead of trying to accomplish some major task, this post is a small collection of things I've learned over the past few weeks.

A better ``devShell`` definition
--------------------------------

The original issue I'm trying to solve dates back to my :doc:`first post </blog/2022/first-steps-with-nix>` on using Nix.
That is, defining a ``devShell`` containing the dependencies of a local Python package doesn't mean that the local package itself is importable when the ``devShell`` is activated.

.. code-block::

   $ nix develop .#py310
   (nix-shell) $ pytest
   ================================================= test session starts =================================================
   platform linux -- Python 3.10.12, pytest-7.2.1, pluggy-1.0.0
   rootdir: /var/home/alex/Projects/lsp-devtools/lib/pytest-lsp, configfile: pyproject.toml
   plugins: typeguard-3.0.2, asyncio-0.20.3
   asyncio: mode=auto
   collected 16 items / 1 error

   ======================================================= ERRORS ========================================================
   ________________________________________ ERROR collecting tests/test_client.py ________________________________________
   ImportError while importing test module '/var/home/alex/Projects/lsp-devtools/lib/pytest-lsp/tests/test_client.py'.
   Hint: make sure your test modules/packages have valid Python names.
   Traceback:
   /nix/store/1r6n7v2wam7gkr18gxccpg7p5ywgw551-python3-3.10.12/lib/python3.10/importlib/__init__.py:126: in import_module
       return _bootstrap._gcd_import(name[level:], package, level)
   tests/test_client.py:9: in <module>
       import pytest_lsp
   E   ModuleNotFoundError: No module named 'pytest_lsp'
   =============================================== short test summary info ===============================================
   ERROR tests/test_client.py
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   ================================================== 1 error in 0.16s ===================================================

Initially I tried to solve this by also including the Nix package defined for the local Python package itself in the definition of the ``devShell`` but with any :ref:`tests disabled <nix-overlays-disable-tests>`.
While this worked, it wasn't very useful when trying to do any real development with it.

The problem is that upon activating the shell, Nix will freeze the source as part of the build process.
Which means for any edits to take effect, you have to exit the shell and re-enter it to trigger another build to pick up the changes.
Not only does this fill your ``/nix/store`` with 100s of copies of your project, it gets tedious very quickly!

Since then however, I've learned that when installating a Python package, Nix is only adding the ``/nix/store`` path for it to the ``PYTHONPATH`` environment variable::

  (nix-shell) $ echo $PYTHONPATH | tr ':' '\n'
  /nix/store/99i2wwkhcgr98kjn5wnr25sb87dk4zkk-python3.10-pygls-1.0.1/lib/python3.10/site-packages
  /nix/store/ckmh39zca1gjagq4cmharbvzggcmm4qx-python3.10-lsprotocol-2023.0.0a2/lib/python3.10/site-packages
  /nix/store/n80x8k099gfslvbg4s13hpaiiynimsw5-python3.10-attrs-22.2.0/lib/python3.10/site-packages
  /nix/store/1r6n7v2wam7gkr18gxccpg7p5ywgw551-python3-3.10.12/lib/python3.10/site-packages
  /nix/store/aiabj9kh174a3ybdr00q3zpm7w6vqv99-python3.10-cattrs-22.2.0/lib/python3.10/site-packages
  /nix/store/4bv2ic5mbp639xi0r75y5aq3d8yd04qa-python3.10-exceptiongroup-1.1.0/lib/python3.10/site-packages
  /nix/store/jxpkywimbcxzmsc604gfgibdvlj8x3ch-python3.10-typeguard-3.0.2/lib/python3.10/site-packages
  /nix/store/5vwslcxd6w3ck9dlgf8zw87ha2cnf5zz-python3.10-importlib-metadata-6.0.0/lib/python3.10/site-packages
  /nix/store/4s0w0rp502c09f7vngmnwdmxaans4k70-python3.10-toml-0.10.2/lib/python3.10/site-packages
  /nix/store/6zrrhy4mv339hd6rhc19immll0qpm9fr-python3.10-zipp-3.15.0/lib/python3.10/site-packages
  /nix/store/082nwhxg32ykrc4bcd9wacj1pzgyf7ii-python3.10-typing-extensions-4.5.0/lib/python3.10/site-packages
  /nix/store/hzv8xjxk35i72jrljvjhl9y5i00vnsqn-python3.10-pytest-7.2.1/lib/python3.10/site-packages
  /nix/store/064q1k7k7g05ls3m7cqdh32nisj51pgw-python3.10-iniconfig-2.0.0/lib/python3.10/site-packages
  /nix/store/c5fh1flbs76jpgmvzz96xa26c3fwsq2s-python3.10-packaging-23.0/lib/python3.10/site-packages
  /nix/store/0mkyiplpq1iy1y4kvkpj4gwcfism1bkw-python3.10-pluggy-1.0.0/lib/python3.10/site-packages
  /nix/store/4k182588zcl6j9n08qmy8395qanxw86r-python3.10-py-1.11.0/lib/python3.10/site-packages
  /nix/store/k40s1gy6pkzdzb7l14jhsmfamwjmpgnk-python3.10-tomli-2.0.1/lib/python3.10/site-packages
  /nix/store/3k5y2a1my07fpbv1p24a7gplk6nqpnpf-python3.10-pytest-asyncio-0.20.3/lib/python3.10/site-packages

So why not put our local package's source there as well?

All we need to do is add a ``shellHook`` to the devShell's definiton that adds the working directory to the existing ``PYTHONPATH``::

  shellHook = ''
     export PYTHONPATH="./:$PYTHONPATH"
  '';

Now the ``devShell`` behaves like an `editable install <https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs>`__ of a Python package - no rebuilds required!

Defining a build matrix
-----------------------

So far, all my ``devShell`` definitions have been making use of a function I wrote called ``eachPythonVersion`` (see :ref:`this section <first-steps-nix-multiple-python-versions>` for more details) which would let me define a ``devShell`` once, but reuse it across multiple Python versions

.. code-block:: nix

   devShells = utils.lib.eachDefaultSystemMap (system:
       eachPythonVersion [ "38" "39" "310" "311" ] (pyVersion:
         with pkgs; mkShell {
           name = "py${pyVersion}";

           shellHook = ''
             export PYTHONPATH="./:$PYTHONPATH"
           '';

           packages = with pkgs."python${pyVersion}Packages"; [
             pygls
             pytest
             pytest-asyncio
           ];
         }
     )
   );

However, if you look at the implementation of ``eachPythonVersion``

.. code-block:: nix

   eachPythonVersion = versions: f:
     builtins.listToAttrs (builtins.map (version: {name = "py${version}"; value = f version; }) versions);

it

- only supports parametrising a single version number
- only supports producing a single 'thing' for each version number
- is not easily adapatable to other situations.

Currently I'm working on the next major version of `esbonio <https://github.com/swyddfa/esbonio>`__ and need to be able to define multiple ``devShells`` per Python version each containing a different version of Sphinx.

So ideally, I'd want to be able to define my build matrix

.. code-block:: nix

   buildMatrix = {
     py = [ "38" "39" "310" "311" ];
     sphinx = [ "5" "6" "7" ];
   };

and then apply it over some function to get definitions for all combinations of supported versions

.. code-block:: nix

   devShells = utils.lib.eachDefaultSystemMap (system:
     applyMatrix buildMatrix ({ py, sphinx, ...}: {
       "py${py}-esbonio" = pkgs.mkShell { };          # A shell without sphinx avaialable at all
       "py${py}-sphinx${sphinx}" = pkgs.mkShell { };  # A shell containing the given sphinx verison
     })
   );

.. dropdown:: Which expands into a lot of devShells!

   .. code-block:: none

      $ nix flake show
      git+file:///var/home/alex/Projects/esbonio-beta?dir=lib%2fesbonio
      ├───devShells
      │   ├───aarch64-darwin
      │   │   ├───py310-esbonio: development environment 'py310-esbonio'
      │   │   ├───py310-sphinx5: development environment 'py310-sphinx5'
      │   │   ├───py310-sphinx6: development environment 'py310-sphinx6'
      │   │   ├───py310-sphinx7: development environment 'py310-sphinx7'
      │   │   ├───py311-esbonio: development environment 'py311-esbonio'
      │   │   ├───py311-sphinx5: development environment 'py311-sphinx5'
      │   │   ├───py311-sphinx6: development environment 'py311-sphinx6'
      │   │   ├───py311-sphinx7: development environment 'py311-sphinx7'
      │   │   ├───py38-esbonio: development environment 'py38-esbonio'
      │   │   ├───py38-sphinx5: development environment 'py38-sphinx5'
      │   │   ├───py38-sphinx6: development environment 'py38-sphinx6'
      │   │   ├───py38-sphinx7: development environment 'py38-sphinx7'
      │   │   ├───py39-esbonio: development environment 'py39-esbonio'
      │   │   ├───py39-sphinx5: development environment 'py39-sphinx5'
      │   │   ├───py39-sphinx6: development environment 'py39-sphinx6'
      │   │   └───py39-sphinx7: development environment 'py39-sphinx7'
      │   ├───aarch64-linux
      │   │   ├───py310-esbonio: development environment 'py310-esbonio'
      │   │   ├───py310-sphinx5: development environment 'py310-sphinx5'
      │   │   ├───py310-sphinx6: development environment 'py310-sphinx6'
      │   │   ├───py310-sphinx7: development environment 'py310-sphinx7'
      │   │   ├───py311-esbonio: development environment 'py311-esbonio'
      │   │   ├───py311-sphinx5: development environment 'py311-sphinx5'
      │   │   ├───py311-sphinx6: development environment 'py311-sphinx6'
      │   │   ├───py311-sphinx7: development environment 'py311-sphinx7'
      │   │   ├───py38-esbonio: development environment 'py38-esbonio'
      │   │   ├───py38-sphinx5: development environment 'py38-sphinx5'
      │   │   ├───py38-sphinx6: development environment 'py38-sphinx6'
      │   │   ├───py38-sphinx7: development environment 'py38-sphinx7'
      │   │   ├───py39-esbonio: development environment 'py39-esbonio'
      │   │   ├───py39-sphinx5: development environment 'py39-sphinx5'
      │   │   ├───py39-sphinx6: development environment 'py39-sphinx6'
      │   │   └───py39-sphinx7: development environment 'py39-sphinx7'
      │   ├───x86_64-darwin
      │   │   ├───py310-esbonio: development environment 'py310-esbonio'
      │   │   ├───py310-sphinx5: development environment 'py310-sphinx5'
      │   │   ├───py310-sphinx6: development environment 'py310-sphinx6'
      │   │   ├───py310-sphinx7: development environment 'py310-sphinx7'
      │   │   ├───py311-esbonio: development environment 'py311-esbonio'
      │   │   ├───py311-sphinx5: development environment 'py311-sphinx5'
      │   │   ├───py311-sphinx6: development environment 'py311-sphinx6'
      │   │   ├───py311-sphinx7: development environment 'py311-sphinx7'
      │   │   ├───py38-esbonio: development environment 'py38-esbonio'
      │   │   ├───py38-sphinx5: development environment 'py38-sphinx5'
      │   │   ├───py38-sphinx6: development environment 'py38-sphinx6'
      │   │   ├───py38-sphinx7: development environment 'py38-sphinx7'
      │   │   ├───py39-esbonio: development environment 'py39-esbonio'
      │   │   ├───py39-sphinx5: development environment 'py39-sphinx5'
      │   │   ├───py39-sphinx6: development environment 'py39-sphinx6'
      │   │   └───py39-sphinx7: development environment 'py39-sphinx7'
      │   └───x86_64-linux
      │       ├───py310-esbonio: development environment 'py310-esbonio'
      │       ├───py310-sphinx5: development environment 'py310-sphinx5'
      │       ├───py310-sphinx6: development environment 'py310-sphinx6'
      │       ├───py310-sphinx7: development environment 'py310-sphinx7'
      │       ├───py311-esbonio: development environment 'py311-esbonio'
      │       ├───py311-sphinx5: development environment 'py311-sphinx5'
      │       ├───py311-sphinx6: development environment 'py311-sphinx6'
      │       ├───py311-sphinx7: development environment 'py311-sphinx7'
      │       ├───py38-esbonio: development environment 'py38-esbonio'
      │       ├───py38-sphinx5: development environment 'py38-sphinx5'
      │       ├───py38-sphinx6: development environment 'py38-sphinx6'
      │       ├───py38-sphinx7: development environment 'py38-sphinx7'
      │       ├───py39-esbonio: development environment 'py39-esbonio'
      │       ├───py39-sphinx5: development environment 'py39-sphinx5'
      │       ├───py39-sphinx6: development environment 'py39-sphinx6'
      │       └───py39-sphinx7: development environment 'py39-sphinx7'

The question is, how do we implement ``applyMatrix``?

Well, fast forwarding through plenty of trial and error and a few "aha!" moments I'm now able to tell you!

First, we need to take the ``buildMatrix`` and expand it out into all possible combinations - thankfully ``nixpkgs`` provides a function that does exactly that

.. code-block:: none

   $ nix repl
   > buildMatrix = { py = [ "38" "39" "310" "311" ]; sphinx = [ "5" "6" "7" ]; }
   > allCombinations = nixpkgs.lib.cartesianProductOfSets buildMatrix
   > :p allCombinations  # ':p' Overrides nix's lazy evaluation to print the
                         # fully expanded version of an object
   [
     { py = "38"; sphinx = "5"; }
     { py = "38"; sphinx = "6"; }
     { py = "38"; sphinx = "7"; }
     { py = "39"; sphinx = "5"; }
     { py = "39"; sphinx = "6"; }
     { py = "39"; sphinx = "7"; }
     { py = "310"; sphinx = "5"; }
     { py = "310"; sphinx = "6"; }
     { py = "310"; sphinx = "7"; }
     { py = "311"; sphinx = "5"; }
     { py = "311"; sphinx = "6"; }
     { py = "311"; sphinx = "7"; }
   ]

Next we need to apply some function over this list to produce the corresponding environment

.. code-block:: none

   > shells = builtins.map ({py, sphinx}: {"py${py}-sphinx${sphinx}" = { }; }) allCombinations
   > :p shells
   [
     { py38-sphinx5 = { }; }
     { py38-sphinx6 = { }; }
     { py38-sphinx7 = { }; }
     { py39-sphinx5 = { }; }
     { py39-sphinx6 = { }; }
     { py39-sphinx7 = { }; }
     { py310-sphinx5 = { }; }
     { py310-sphinx6 = { }; }
     { py310-sphinx7 = { }; }
     { py311-sphinx5 = { }; }
     { py311-sphinx6 = { }; }
     { py311-sphinx7 = { }; }
   ]

Finally, we need to merge the list of attribute sets down into a single set containing all of the definitions

.. code-block:: none

   > result = builtins.foldl' (x: y: x // y) {} shells
   > :p result
   {
     py310-sphinx5 = { };
     py310-sphinx6 = { };
     py310-sphinx7 = { };
     py311-sphinx5 = { };
     py311-sphinx6 = { };
     py311-sphinx7 = { };
     py38-sphinx5 = { };
     py38-sphinx6 = { };
     py38-sphinx7 = { };
     py39-sphinx5 = { };
     py39-sphinx6 = { };
     py39-sphinx7 = { };
   }

Bringing it all together results in a surprisingly compact function definition!

.. code-block:: nix

   applyMatrix = matrix: f:
     builtins.foldl' (x: y: x // y) {}
       (builtins.map f (nixpkgs.lib.cartesianProductOfSets matrix));


Flakes and Monorepos
--------------------

:doc:`Previously </blog/2023/integrate-esboino-nvim-with-nix>` I tried adding a "top-level" ``flake.nix`` to the git repository for the `esbonio <https://github.com/swyddfa/esbonio>`__ language server that depended on another ``flake.nix`` within a sub directory of the same repository.

It... `didn't work <https://github.com/swyddfa/esbonio/issues/570>`__.

I'm still trying to figure out the best way to approach this but I'm currently leaning towards keeping the multiple ``flake.nix`` files where

- the top-level ``flake.nix`` contains "public" entry-points e.g. ``apps`` and ``overlays``
- "local" ``flake.nix`` files for each sub-project containing entry-points that are mainly useful for contributors to the project e.g. ``devShells``
- rather than have the top-level  ``flake.nix`` depend on the "local" flakes, use Nix's ``import`` statement to pull in reusable snippets of Nix code from the subprojects.

🤞 it works out!
