.. post:: 2023-01-25
   :tags: nix, pytest-lsp, python
   :author: me
   :language: en
   :excerpt: 3

My Next Steps with Nix: Overlays
================================

:doc:`Last time </blog/2022/first-steps-with-nix>`, I experimented with writing a flake that defined development environments for the :pypi:`esbonio` package spanning multiple Python versions.
During that process I also packaged :pypi:`pytest-lsp` using an ad-hoc nix expression as part of the ``esbonio`` repo.

In this post I look into writing a similar flake for the ``pytest-lsp`` package itself, but this time using overlays to override and extend the nixpkgs package set.

If you are interested, you can find the final version of the code
`here <https://github.com/swyddfa/lsp-devtools/commit/a7b8d545364cc14c1cd054fd56831d0bd3517659>`__.

Packaging ``pytest-lsp``
------------------------

Adapting the
`flake.nix <https://github.com/alcarney/esbonio/commit/f62e1d486bb7899d802bfd668f98f21b71702317#diff-12d8883e85761c056008578af1202737eabc12dbdb4cee164b96cdb77a8be96b>`__
file and using the
`package definition <https://github.com/alcarney/esbonio/commit/f62e1d486bb7899d802bfd668f98f21b71702317#diff-592a771a0632b893c90066d07d7b260e4847eff70e8b47e9dcd0806014dcfc6d>`_
from the previous post, it's easy enough to sketch out a flake that should give us a ``devShell`` to work on the ``pytest-lsp`` package.

However, trying to activate one we encounter a problem.

.. code-block:: console
   :emphasize-lines: 11,12

   $ nix develop -c .#py310
   error: builder for '/nix/store/dfd5bixdgkvfcnfa7f9z0ibp4m5zlhkz-python3.10-pytest-lsp-0.2.1.drv' failed with exit code 1;
          last 10 log lines:
          > installing
          > Executing pipInstallPhase
          > /build/pytest-lsp/dist /build/pytest-lsp
          > Processing ./pytest_lsp-0.2.1-py3-none-any.whl
          > Requirement already satisfied: appdirs in /nix/store/yidjmqc5q1j0fz2dk79qgk1fy7dqcliy-python3.10-appdirs-1.4.4/lib/python3.10/site-packages (from pytest-lsp==0.2.1) (1.4.4)
          > Requirement already satisfied: pytest-asyncio in /nix/store/dvz12bivdc0dkn6849zm58754ga06hs6-python3.10-pytest-asyncio-0.20.3/lib/python3.10/site-packages (from pytest-lsp==0.2.1) (0.20.3)
          > Requirement already satisfied: pytest in /nix/store/z5pkmmsdg3bmb35pmsv4rjca1qi7dbnf-python3.10-pytest-7.2.0/lib/python3.10/site-packages (from pytest-lsp==0.2.1) (7.2.0)
          > ERROR: Could not find a version that satisfies the requirement pygls>=1.0.0 (from pytest-lsp) (from versions: none)
          > ERROR: No matching distribution found for pygls>=1.0.0
          >
          For full logs, run 'nix log /nix/store/dfd5bixdgkvfcnfa7f9z0ibp4m5zlhkz-python3.10-pytest-lsp-0.2.1.drv'.
   error: 1 dependencies of derivation '/nix/store/kfzlz750xdk71fxwvsgpdbw1w00jbvf9-py310-env.drv' failed to build


In the time between writing the previous blog post and this one, the ``pytest-lsp`` package has been migrated to the latest version of ``pygls``.
The version available through nixpkgs however, is still the previous release.

While there is an open `pull request <https://github.com/NixOS/nixpkgs/pull/204457>`__ updating ``pygls`` to ``1.0``, at the time of writing it's blocked on downstream packages which haven't migrated yet.

That said, we don't have to wait for nixpkgs but can instead use an overlay to update it just for this project.

Overriding pygls' version
-------------------------

Overlays can be used to override sections of an existing package definition.

.. note::

   As I mentioned in the previous post, I'm probably not the best person to learn Nix from.
   Instead, here are some resources you might useful which go into more detail.

   - The NixOS `wiki page <https://nixos.wiki/wiki/Overlays>`__ on Overlays
   - Nix Pills: `Chapter 14. Override design pattern <https://nixos.org/guides/nix-pills/override-design-pattern.html>`__

As far as I understand it:

- Overlays are a useful design pattern, rather than a fundamental concept of the Nix language.
- They are "just" a nix function that have access to both the modified version (usually called ``self`` or ``final``) of the "thing" they're modifying, as well as the unmodified version of it (``super`` or ``prev``)
- These functions make use of attributes like ``override`` or ``overrideAttrs`` to make their modifications.
- I have no idea how to make something overridable 😅

After reading through the `wiki page <https://nixos.wiki/wiki/Overlays>`__ on overlays a few times, particuarly the sections on overriding a version and python package overlays, I was able to put together an overlay which looked like it should work.

.. code-block:: nix

   # In ./nix/pygls-overlay.nix
   self: super: rec {

     python3 = super.python3.override {
       packageOverrides = pyself: pysuper: {

         pygls = pysuper.pygls.overrideAttrs (old: rec {
           version = "1.0.0";
           src = super.fetchFromGitHub {
             owner = "openlawlibrary";
             repo = "pygls";
             rev = "v${version}";
             hash = "sha256-31J4+giK1RDBS52Q/Ia3Y/Zak7fp7gRVTQ7US/eFjtM=";
           };
         });
       };
    };

    python3Packages = python3.pkgs;
  }

Using this in the flake is a matter of importing it and passing it to the ``overlays`` attribute when importing nixpkgs

.. code-block:: nix
   :emphasize-lines: 5,11

   # In flake.nix
   outputs = { self, nixpkgs, utils }:

    let
      pygls-overlay = import ./nix/pygls-overlay.nix;
      eachPythonVersion = ...
    in {

    devShells = utils.lib.eachDefaultSystemMap (system:
      let
        pkgs = import nixpkgs { inherit system; overlays = [ pygls-overlay ]; };
      in
        eachPythonVersion [ "37" "38" "39" "310" "311" ] (pyVersion:
          let
            pytest-lsp = pkgs.callPackage ./nix/pytest-lsp.nix { pythonPackages = pkgs."python${pyVersion}Packages"; };
          in


With some luck, running ``nix develop`` this time should bring in the latest ``pygls`` version

.. code-block:: console

   $ nix develop -c .#py310
   error: builder for '/nix/store/1sha5j0dfyn2g4z82rpk4yqv32awmjfr-python3.10-pytest-lsp-0.2.1.drv' failed with exit code 1;
          ...
          > ERROR: No matching distribution found for pygls>=1.0.0

Huh, same error... 🤔

Let's take a closer look at where we pull in the ``pytest-lsp`` package definition in the flake...

.. code-block:: nix

   pytest-lsp = pkgs.callPackage ./nix/pytest-lsp.nix {
     pythonPackages = pkgs."python${pyVersion}Packages";
   };

Assuming we're trying to enter the ``python310`` devShell, then we're passing in the ``python310Packages`` package set.
But in the overlay, we're overriding the ``python3Packages`` package set, I wonder if we change the overlay to match the flake...

.. code-block:: nix

   # In ./nix/pygls-overlay.nix
   self: super: rec {
     python310 = super.python310.override { ... };
     python310Packages = python310.pkgs;
   }

And try again

.. _nix-overlays-build-pygls-output:

.. code-block:: console
   :emphasize-lines: 11,12

   $ nix develop .#py310
   error: builder for '/nix/store/jl23ai588n2b6amaicy5532bdxjiciyy-python3.10-pygls-0.13.0.drv' failed with exit code 1;
          last 10 log lines:
          > removing build/bdist.linux-x86_64/wheel
          > Finished executing setuptoolsBuildPhase
          > installing
          > Executing pipInstallPhase
          > /build/source/dist /build/source
          > Processing ./pygls-0.13.0-py3-none-any.whl
          > Requirement already satisfied: typeguard<3,>=2.10.0 in /nix/store/m4jjcrvbi928pi2d14qh8np1miqfvc0b-python3.10-typeguard-2.13.3/lib/python3.10/site-packages (from pygls==0.13.0) (2.13.3)
          > ERROR: Could not find a version that satisfies the requirement lsprotocol (from pygls) (from versions: none)
          > ERROR: No matching distribution found for lsprotocol
          >
          For full logs, run 'nix log /nix/store/jl23ai588n2b6amaicy5532bdxjiciyy-python3.10-pygls-0.13.0.drv'.
   error: 1 dependencies of derivation '/nix/store/f5vasy4x9zpdhcq9jh9rz06qpvriblwp-python3.10-pytest-lsp-0.2.1.drv' failed to build
   error: 1 dependencies of derivation '/nix/store/86v8bcxvjq1g9dhpx1wgmckba8bnag7h-py310-env.drv' failed to build

Progress!

Packaging ``lsprotocol``
------------------------

pygls is failing to build as the package definition in nixpkgs is missing the new ``lsprotcol`` dependency, easy enough to fix - if it was available in nixpkgs.
Thankfully, overlays can do more than just override attributes on existing packages, they can be used to extend a package set with entirely new definitions!

We just need to know how to package ``lsprotocol`` itself and thanks to the PR linked above we get to cheat a little.

.. code-block:: nix

   # In ./nix/pygls-overlay.nix
   lsprotocol = pysuper.buildPythonPackage rec {
     pname = "lsprotocol";
     version = "2022.0.0a9";
     format = "pyproject";

     src = super.fetchFromGitHub {
       owner = "microsoft";
       repo = pname;
       rev = version;
       hash = "sha256-6XecPKuBhwtkmZrGozzO+VEryI5wwy9hlvWE1oV6ajk=";
     };

     nativeBuildInputs = with super.python310Packages; [
       flit-core
     ];

     propagatedBuildInputs = with super.python310Packages; [
       cattrs
       attrs
     ];

     # Disable tests
     doCheck = false;
   };

Note that I've cut some corners by disabling any tests, but it allows me to dodge packaging anything else 😅

Then we can also override pygls' dependencies and reference the newly created ``lsprotocol`` package from the modified version of the ``python310Packages`` set.

.. code-block:: nix

   pygls = pysuper.pygls.overrideAttrs (_: rec {
     ...
     propagatedBuildInputs = with self.python310Packages; [
       lsprotocol
       typeguard
     ];
   });

With that taken care of, we should be good to go right?

Unlucky ``0.13``
----------------

Attempting to enter the devShell yet again we encounter a familiar error message

.. code-block:: console
   :emphasize-lines: 10,11

   error: builder for '/nix/store/s5xp7fr2r9faxgqw7rvs6ffah10f2fz7-python3.10-pytest-lsp-0.2.1.drv' failed with exit code 1;
          last 10 log lines:
          > Finished executing setuptoolsBuildPhase
          > installing
          > Executing pipInstallPhase
          > /build/pytest-lsp/dist /build/pytest-lsp
          > Processing ./pytest_lsp-0.2.1-py3-none-any.whl
          > Requirement already satisfied: pytest-asyncio in /nix/store/dvz12bivdc0dkn6849zm58754ga06hs6-python3.10-pytest-asyncio-0.20.3/lib/python3.10/site-packages (from pytest-lsp==0.2.1) (0.20.3)
          > Requirement already satisfied: pytest in /nix/store/z5pkmmsdg3bmb35pmsv4rjca1qi7dbnf-python3.10-pytest-7.2.0/lib/python3.10/site-packages (from pytest-lsp==0.2.1) (7.2.0)
          > ERROR: Could not find a version that satisfies the requirement pygls>=1.0.0 (from pytest-lsp) (from  versions: none)
          > ERROR: No matching distribution found for pygls>=1.0.0
          >
          For full logs, run 'nix log /nix/store/s5xp7fr2r9faxgqw7rvs6ffah10f2fz7-python3.10-pytest-lsp-0.2.1.drv'.
   error: 1 dependencies of derivation '/nix/store/a0smpmj63fw1fzp78i3z53xvd0zsvvhp-py310-env.drv' failed to build

But we just upgraded pygls to ``1.0`` right? That's why we had to package ``lsprotocol`` in the previous section?

You might have already noticed in the log output :ref:`above <nix-overlays-build-pygls-output>`, that despite overriding the ``version`` field to ``1.0`` the Python package was still coming out as ``0.13.0`` - despite it containing the ``1.0`` version of the codebase!

.. code-block:: console

   > Processing ./pygls-0.13.0-py3-none-any.whl

Plenty of head scratching later, I finally remembered that pygls uses `setuptools_scm <https://github.com/pypa/setuptools_scm>`_ to automatically derive the version number based on tags in its git repository.
But the build is not taking place in a git repo... so nix must be setting that version somehow right?

Yep. A quick trip to the actual file containing pygls' package definition on nixpkgs (and not just the diff view in the PR!) reveals an additional attribute that needed to be overriden

.. code-block:: nix

   # In ./nix/pygls-overlay.nix
   pygls = pysuper.pygls.overrideAttrs (_: rec {
        version = "1.0.0";
        SETUPTOOLS_SCM_PRETEND_VERSION = version;
        ...
   });

Now if we try activating that devShell?

.. code-block:: console

   $ nix develop .#py310
   (nix-shell) $ pytest
   ================================== test session starts =================================
   platform linux -- Python 3.10.9, pytest-7.2.0, pluggy-1.0.0
   rootdir: /var/home/alex/Projects/lsp-devtools/lib/pytest-lsp, configfile: pyproject.toml
   plugins: lsp-0.2.1, typeguard-2.13.3, asyncio-0.20.3
   asyncio: mode=auto
   collected 27 items

   tests/test_client.py ...                                    [ 11%]
   tests/test_client_methods.py ...................            [ 81%]
   tests/test_plugin.py ....                                   [ 96%]
   tests/test_server.py .                                      [100%]

   ================================= 27 passed in 8.57s ==================================

Success!

.. note::

   I'm not 100% sure if I've overriden the pygls' version number correctly, since inspecting the ``PYTHONPATH`` the devShell is using shows that the version number of the nix package is *still* ``0.13.0``!

   .. code-block:: console

      (nix-shell) $ echo $PYTHONPATH | tr ':' '\n' | grep pygls
      /nix/store/s5jh5s9m5f1163hxzj8768jc5li7cdfg-python3.10-pygls-0.13.0/lib/python3.10/site-packages

   But in Python land, everything appears at least, to be consistent, so I'm going with it for now.

Mutliple Python Versions
------------------------

Now that we've got it working for Python 3.10, we need to generalise the overlay so that we can use it with any of the Python versions supported by ``pytest-lsp``.

Ideally, what we'd want is to write an expression like the following

.. code-block:: nix

   # In ./nix/pygls-overlay.nix
   self: super:

   eachPythonVersion ["37" "38" "39" "310" "311"] (pyVersion:
     super."python${pyVersion}".override {
       packageOverrides = pyself: pysuper: {

          lsprotocol = pysuper.buildPythonPackage rec {
            ...
            nativeBuildInputs = with super."python${pyVersion}Packages"; [
              flit-core
            ];

            propagatedBuildInputs = with super."python${pyVersion}Packages"; [
              cattrs
              attrs
            ];
          };

          pygls = pysuper.pygls.overrideAttrs (_: rec {
            ...
            propagatedBuildInputs = with self."python${pyVersion}Packages"; [
              lsprotocol
              typeguard
            ];
         });
      };
   })

And have the ``eachPythonVersion`` function handle the details of performing all the overrides.

To start with, let's define a helper ``doPythonOverride`` that ``eachPythonVersion`` can use.
It should take a ``version`` and a function ``f`` and use it to perform the override for a single Python version, something like the following pseudo code.

.. code-block:: none

   doPythonOverride(version, f) = { "python${version}" = f(version);
                                    "python${version}Packages" = "python${version}".pkgs; }

The only issue is that (as far as I can tell), you can't use strings as keys in a nix attribute set.
However, you can use the
`builtins.listToAttrs <https://nixos.org/manual/nix/stable/language/builtins.html#builtins-listToAttrs>`_
function to build an attribute set from a list of ``{ name = "xxx"; value = 123; }`` attribute sets, which allows us to define ``doPythonOverride`` as follows.

.. code-block:: nix

   doPythonOverride = version: f:
     let
       overridenPython = f version;
     in
       builtins.listToAttrs [ {name = "python${version}"; value = overridenPython; }
                              {name = "python${version}Packages"; value = overridenPython.pkgs; }];

From there, we can define ``eachPythonVersion`` to map the ``doPythonOverride`` helper across each of the given Python versions and merge the results into a single attribute set using the
`foldl' <https://nixos.org/manual/nix/stable/language/builtins.html#builtins-foldl'>`__
function.

.. code-block:: nix

   eachPythonVersion = versions: f: builtins.foldl' (a: b: a // b) {}
     (builtins.map (version: doPythonOverride version f) versions);

Now we should have successfully overriden pygls' version across all supported Python versions!

Sharing Overlays
----------------

Up until now, I've been mostly focusing on the ``devShells`` output of a flake.
There are, however, `many other <https://nixos.wiki/wiki/Flakes#Output_schema>`__ items that can be exported from a flake - including overlays.
Following the same pattern as the previous section it's easy enough to convert the ``pytest-lsp`` package definition into an overlay

.. code-block:: nix

   # In ./nix/pytest-lsp-overlay.nix
   let
     doPythonOverride = version: f:
       let
         overridenPython = f version;
       in
         builtins.listToAttrs [ {name = "python${version}" ; value = overridenPython ; }
                                {name = "python${version}Packages" ; value = overridenPython.pkgs ; }];

     eachPythonVersion = versions: f: builtins.foldl' (a: b: a // b) {}
       (builtins.map (version: doPythonOverride version f) versions);
   in

   self: super:

   eachPythonVersion [ "37" "38" "39" "310" "311" ] (pyVersion:
     super."python${pyVersion}".override {
       packageOverrides = pyself: pysuper: {

         pytest-lsp = pysuper.buildPythonPackage {
           pname = "pytest-lsp";
           version = "0.2.1";
           src = ./..;
           propagatedBuildInputs = with super."python${pyVersion}Packages"; [
             pygls
             pytest
             pytest-asyncio
           ];
         };
       };
     })

We can then include it in the main ``flake.nix`` file just as we did with the pygls overlay, but also assign it to the ``overlays`` output to make it available to other projects.

.. code-block:: nix
   :emphasize-lines: 6, 9, 13

   # In flake.nix
   outputs = { self, nixpkgs, utils }:

     let
      pygls-overlay = import ./nix/pygls-overlay.nix;
      pytest-lsp-overlay = import ./nix/pytest-lsp-overlay.nix;
    in {

    overlays.pytest-lsp = pytest-lsp-overlay;

    devShells = utils.lib.eachDefaultSystemMap (system:
      let
        pkgs = import nixpkgs { inherit system; overlays = [ pygls-overlay pytest-lsp-overlay ]; };
      in
        ...

In theory, we can update the flake we previously wrote for ``esbonio`` to use this overlay to provide the ``pytest-lsp`` package definition

.. code-block:: nix
   :emphasize-lines: 5, 17

   # In esbonio/flake.nix

   inputs = {
     nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
     pytest-lsp.url = "github:swyddfa/lsp-devtools?dir=lib/pytest-lsp";
     utils.url = "github:numtide/flake-utils";
   };

   outputs = { self, nixpkgs, pytest-lsp, utils }:

     let
       pygls-overlay = import ./nix/pygls-overlay.nix;
     in {

     devShells = utils.lib.eachDefaultSystemMap (system:
       let
         pkgs = import nixpkgs { inherit system; overlays = [ pygls-overlay pytest-lsp.overlays.pytest-lsp ]; };
       in
         ...

Finally, we should be able to activate a devShell for ``esbonio`` as before.

.. code-block:: console

   $ nix develop .#py310
   error: Dependency is not of a valid type: element 5 of nativeBuildInputs for py310
   (use '--show-trace' to show detailed location information)

Ah, well, perhaps that's a job for another day! 😅
