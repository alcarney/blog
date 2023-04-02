.. post:: 2023-03-31
   :tags: nix, python, pytest-lsp, esbonio
   :author: me
   :language: en
   :excerpt: 1

Nix Overlays: A follow up
=========================

It turns out there were a few issues with the setup I put together in my :doc:`previous post </blog/2023/nix-overlays>`.
This time I try and resolve them and get to the point where I have working overlays for both
`pytest-lsp <https://github.com/swyddfa/lsp-devtools/tree/develop/lib/pytest-lsp>`__
and
`esbonio <https://github.com/swyddfa/esbonio>`__.

``Dependency is not of valid type``
-----------------------------------

At the end of the previous post, I was left scratching my head after encountering a cryptic error message

.. code-block:: console

   $ nix develop .#py310
   error: Dependency is not of a valid type: element 4 of nativeBuildInputs for py310
   (use '--show-trace' to show detailed location information)

Which was coming from the following ``flake.nix``

.. code-block:: nix
   :emphasize-lines: 6, 10, 34

   {
     description = "The Esbonio language server";

     inputs = {
       nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
       pytest-lsp.url = "github:swyddfa/lsp-devtools?dir=lib/pytest-lsp";
       utils.url = "github:numtide/flake-utils";
     };

     outputs = { self, nixpkgs, pytest-lsp, utils }:

       let
         esbonio-overlay = import ./nix/esbonio-overlay.nix;
         eachPythonVersion = versions: f:
           builtins.listToAttrs (builtins.map (version: {name = "py${version}"; value = f version; }) versions);
       in {

       overlays.default = esbonio-overlay;

       devShells = utils.lib.eachDefaultSystemMap (system:
         let
           pkgs = import nixpkgs {
             inherit system;
             overlays = [ pytest-lsp.overlays.pytest-lsp esbonio-overlay ];
           };
         in
           eachPythonVersion [ "38" "39" "310" "311" ] (pyVersion:
             with pkgs; mkShell {
               name = "py${pyVersion}";
               packages = with pkgs."python${pyVersion}Packages"; [
                 esbonio
                 mock
                 pytest
                 pytest-lsp
                 pytest-timeout
               ];
             }
         )
       );
     };
   }

Originally, I thought this was caused by naming conflicts introduced by using ``pytest-lsp`` to reference both ``pytest-lsp`` the flake, and ``pytest-lsp`` the Python package.
Indeed, changing the name of the flake input to ``pytestlsp`` seemed to at least change the error message I was seeing...

.. code-block:: console

   $ nix develop .#py310
   error: undefined variable 'pytest-lsp'

          at /nix/store/dihmz79kgwxj1v5mqvxrj0f3ifgvpm9f-source/lib/esbonio/flake.nix:38:15:

              37|               pytest
              38|               pytest-lsp
                |               ^
              39|               pytest-timeout
   (use '--show-trace' to show detailed location information)

How can that be?!

Conflicting Overlays
--------------------

It turns out that the overlays ``pytestlsp.overlays.pytest-lsp`` and ``esbonio-overlay`` conflict with each other!
I am not sure what originally led me to try it, but by reversing their order in the array passed to ``nixpkgs`` I could produce a similar error for the ``esbonio`` package.

.. code-block:: console

   $ nix develop .#py310
   error: undefined variable 'esbonio'

          at /nix/store/vqff8bn03r11m1fg4f0b7ixnj731g9br-source/lib/esbonio/flake.nix:34:15:

              33|             packages = with pkgs."python${pyVersion}Packages"; [
              34|               esbonio
                |               ^
              35|
   (use '--show-trace' to show detailed location information)

But why? 🤔
I thought the whole point of overlays were so that they could be... well, overlayed on an underlying package set without conflicting with each other??

Use the Source Luke
-------------------

To find the answer, I had to remind myself that Nix is **not** magic (although it can appear to be!) and instead, at it's core, Nix is a programming language.
Which means this concept of "overlays" must be implemented in code *somewhere* and we can look for ourselves to see how they are handled.
Sure enough, after some splunking through the ``nixpkgs`` repo I was able to track down
`the commit <https://github.com/NixOS/nixpkgs/commit/f5dfe78a1eb5ff8dfcc7ab37cfc132c5f31d3cef>`__
introducing the concept.

The majority of that commit appears to be just passing the ``overlays`` array through to all the places that require it and updating the documentation.
The interesting part is where the overlays are actually applied at the bottom of
`pkgs/top-level/stage.nix <https://github.com/NixOS/nixpkgs/blob/f5dfe78a1eb5ff8dfcc7ab37cfc132c5f31d3cef/pkgs/top-level/stage.nix#L84-L96>`__

.. code-block:: nix

   let
     # The complete chain of package set builders, applied from top to bottom
     toFix = lib.foldl' (lib.flip lib.extends) (self: {}) ([
       stdenvBootstappingAndPlatforms
       stdenvAdapters
       trivialBuilders
       allPackages
       aliases
       stdenvOverrides
       configOverrides
       ] ++ overlays);
   in
     # Return the complete set of packages.
     lib.fix toFix

From what I understand

- `lib.foldl' <https://github.com/NixOS/nixpkgs/blob/f5dfe78a1eb5ff8dfcc7ab37cfc132c5f31d3cef/lib/lists.nix#L61>`__
  applies some combination function - ``(lib.flip lib.extends)`` in this case, to a list resulting in a single aggregated value.
- `lib.flip <https://github.com/NixOS/nixpkgs/blob/f5dfe78a1eb5ff8dfcc7ab37cfc132c5f31d3cef/lib/trivial.nix#L82>`__
  switches the order of the arguments given to ``lib.extends``
- `lib.extends <https://github.com/NixOS/nixpkgs/blob/f5dfe78a1eb5ff8dfcc7ab37cfc132c5f31d3cef/lib/trivial.nix#L54>`__
  is the function we're actually interested in as it is responsible for applying the overlays.
- `lib.fix <https://github.com/NixOS/nixpkgs/blob/f5dfe78a1eb5ff8dfcc7ab37cfc132c5f31d3cef/lib/trivial.nix#L29>`__
  appears to resolve all references to ``self`` in ``toFix`` to a "proper" value, but I'm not entirely sure how.

Here is the implementation of ``lib.extends`` as of the commit introducing overlays

.. code-block:: nix

   extends = f: rattrs: self: let super = rattrs self; in super // f self super;

As with most things in Nix, I don't really understand the fine details but it's interesting to see that it uses the ``//`` operator to merge the result of an overlay (``f self super``) with the current state of the package set (``super``).
One thing that's interesting to note, when combining attribute sets with the ``//`` operator, if both sets contain the same key, then the value from the original set is replaced with the value provided by the second.

.. code-block:: console

   $ nix repl
   Welcome to Nix 2.11.1. Type :? for help.

   nix-repl> x = {a = 1 ; b = 2; c = 3;}

   nix-repl> y = {d = 4; c = 5;}

   nix-repl> x // y
   { a = 1; b = 2; c = 5; d = 4; }


*Foreshadowing...*


The Problem
-----------

Armed with my new found knowledge I had another look at the definitions of the problematic overlays.

.. container:: flex flex-col md:flex-row justify-between gap-4

   .. code-block:: nix
      :class: overflow-x-auto
      :emphasize-lines: 9

      # pytest-lsp-overlay.nix
      let
        eachPythonVersion = ...
      in

      self: super:

      eachPythonVersion [ "38" "39" "310" "311" ] (pyVersion:
        super."python${pyVersion}".override {
          packageOverrides = pyself: pysuper: {
            pytest-lsp = pysuper.buildPythonPackage { ... };
          };
      })

   .. code-block:: nix
      :class: overflow-x-auto
      :emphasize-lines: 9

      # esbonio-overlay.nix
      let
        eachPythonVersion = ...
      in

      self: super:

      eachPythonVersion [ "38" "39" "310" "311" ] (pyVersion:
        super."python${pyVersion}".override {
          packageOverrides = pyself: pysuper: {
            esbonio = pysuper.buildPythonPackage { ... };
          };
      })

Well no wonder they conflict with each other, they're overriding the base ``pythonXY`` package directly!
Any ``packageOverrides`` provided by the first overlay would be wiped out when the second is applied.
Surely then there must be a better way to provide your own Python package definitions 🤔

The Solution
------------

Somewhat buried on the `Python page <https://nixos.org/manual/nixpkgs/stable/#python>`__ in the Nixpkgs manual is this handy FAQ question

.. pull-quote::

   17.27.3.9. How to override a Python package for all Python versions using extensions?

   The following overlay overrides the call to buildPythonPackage for the foo package for all interpreters by appending a Python extension to the pythonPackagesExtensions list of extensions.

   .. code-block:: nix

      final: prev: {
        pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
          (
             python-final: python-prev: {
               foo = python-prev.foo.overridePythonAttrs (oldAttrs: { ... });
             }
          )
        ];
      }

This might be just what we need!
Not only do we avoid messing with the base Python package, we also get our packages automatically added to each Python version without the need to roll our own ``eachPythonVerison`` helper!

Converting my :ref:`previous overlay attempts <nix-overlays-sharing>` to the above approach results in overlay definitions that are a lot more straight forward.
Notice that I was even able to enable tests for them now!

.. container:: flex flex-col md:flex-row justify-between gap-4

   .. code-block:: nix
      :class: overflow-x-auto

      # pytest-lsp-overlay.nix
      final: prev: {
        pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [(
          python-final: python-prev: {
            pytest-lsp = python-prev.buildPythonPackage {
              pname = "pytest-lsp";
              version = "0.2.1";

              src = ./..;

              propagatedBuildInputs = with python-prev; [
                pygls
                pytest
                pytest-asyncio
              ];

              doCheck = true;

              nativeCheckInputs = with python-prev; [
                pytestCheckHook
              ];

              pythonImportsCheck = [ "pytest_lsp" ];
            };
          }
        )];
      }

   .. code-block:: nix
      :class: overflow-x-auto

      # esbonio-overlay.nix
      final: prev: {
        pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [(
          python-final: python-prev: {
            esbonio = python-prev.buildPythonPackage {
              pname = "esbonio";
              version = "0.16.1";

              src = ./..;

              propagatedBuildInputs = with python-prev; [
                appdirs
                pygls
                pyspellchecker
                sphinx
                # typing-extensions; only required for Python 3.7
              ];

              doCheck = true;

              nativeCheckInputs = with python-prev; [
                mock
                pytest-lsp
                pytest-timeout
                pytestCheckHook
              ];

              pythonImportsCheck = [ "esbonio.lsp" ];
            };
          }
        )];
      }

All that is left to do is to try and enter the ``devShell`` for esbonio again

.. code-block:: console

   $ nix develop .#py310
   error: builder for '/nix/store/027wakjv9wvws6190c66nf5gxc6smc54-python3.10-esbonio-0.16.1.drv' failed with exit code 2;
          last 10 log lines:
          > /nix/store/l69b9xl4pnqqgdx9vp1yg1cbckgcjsfx-python3.10-pytest-7.2.0/lib/python3.10/site-packages/_pytest/assertion/rewrite.py:168: in exec_module
          >     exec(co, module.__dict__)
          > tests/sphinx-default/conftest.py:53: in <module>
          >     ClientServerConfig(
          > E   TypeError: ClientServerConfig.__init__() got an unexpected keyword argument 'client'
          > =========================== short test summary info ============================
          > ERROR  - TypeError: ClientServerConfig.__init__() got an unexpected keyword argument...
          > !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
          > =============================== 1 error in 0.60s ===============================
          > /nix/store/3yfs41f4b60jya2gk6xikx4s97zsxjr0-stdenv-linux/setup: line 1573: pop_var_context: head of shell_variables not a function context
   For full logs, run 'nix log /nix/store/027wakjv9wvws6190c66nf5gxc6smc54-python3.10-esbonio-0.16.1.drv'.
   error: 1 dependencies of derivation '/nix/store/nms3hs5pz1fmyki4k547gfs1281klgl3-py310-env.drv' failed to build


Hey! At least the Nix part is finally working!

Disabling Tests
---------------

There's one final detail left to clear up.

Of course, if you are consuming a package (like how ``esbonio`` is pulling in ``pytest-lsp``) it's good to have the tests run so that you can verify everything is working as expected.
However, when you are setting up a ``devShell`` to work on a package, you don't really want the tests to run since they will prevent you entering the shell if they fail - as is the case here.

Thankfully, it should just be a case of setting the ``doCheck`` flag for esbonio to ``false`` when using it within the flake's ``devShell`` definition.

.. code-block:: nix

   devShells = utils.lib.eachDefaultSystemMap (system:
     let
       pkgs = import nixpkgs {
         inherit system;
         overlays = [ pytest-lsp-overlay esbonio-overlay ];
       };
     in
       eachPythonVersion [ "38" "39" "310" "311" ] (pyVersion:
         pkgs.mkShell {
           name = "py${pyVersion}";

           packages = with pkgs."python${pyVersion}Packages"; [
             esbonio.overridePythonAttrs (_: { doCheck = false; })

             mock
             # Still necessary to avoid a naming conflict with pytest-lsp, the flake
             pkgs."python${pyVersion}Packages".pytest-lsp
             pytest-timeout
           ];
         }
     )
   );

And activating the shell as normal.

.. code-block:: console

   $ nix develop .#py310
   error: Dependency is not of a valid type: element 1 of nativeBuildInputs for py310
   (use '--show-trace' to show detailed location information)

No! Not again! 😭

To be honest, I nearly gave up on the whole idea then and there but in a last ditch attempt I moved the overriden ``esbonio`` package out into a ``let`` binding.

.. code-block:: nix
   :emphasize-lines: 11

   devShells = utils.lib.eachDefaultSystemMap (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ pytest-lsp-overlay esbonio-overlay ];
        };
      in
        eachPythonVersion [ "38" "39" "310" "311" ] (pyVersion:

          let
            esbonio = pkgs."python${pyVersion}Packages".esbonio.overridePythonAttrs (_: { doCheck = false; });
          in

          pkgs.mkShell {
            name = "py${pyVersion}";

            packages = with pkgs."python${pyVersion}Packages"; [
              esbonio

              mock
              pkgs."python${pyVersion}Packages".pytest-lsp
              pytest-timeout
            ];
          }
      )
    );

And tried again

.. code-block:: console

   $ nix develop .#py310 -L  # -L = enable verbose logging, useful to actually see what the builds are doing.
   python3.10-esbonio> Sourcing python-remove-tests-dir-hook
   python3.10-esbonio> Sourcing python-catch-conflicts-hook.sh
   python3.10-esbonio> Sourcing python-remove-bin-bytecode-hook.sh
   python3.10-esbonio> Sourcing setuptools-build-hook
   python3.10-esbonio> Using setuptoolsBuildPhase
   python3.10-esbonio> Using setuptoolsShellHook
   python3.10-esbonio> Sourcing pip-install-hook
   python3.10-esbonio> Using pipInstallPhase
   ...
   python3.10-esbonio> patching script interpreter paths in /nix/store/a9xjjxv1zh3dmhfaxgph8kq0zaxl92g3-python3.10-esbonio-0.16.1-dist
   python3.10-esbonio> Rewriting #!/nix/store/sp5x6s8n36gjlwck74xhj1i61p66vcpa-python3-3.10.9/bin/python3.10 to #!/nix/store/sp5x6s8n36gjlwck74xhj1i61p66vcpa-python3-3.10.9
   python3.10-esbonio> wrapping `/nix/store/91b7mh7ib0fxwn2kgv47v0sdpl05xqh1-python3.10-esbonio-0.16.1/bin/esbonio'...
   python3.10-esbonio> Rewriting #!/nix/store/sp5x6s8n36gjlwck74xhj1i61p66vcpa-python3-3.10.9/bin/python3.10 to #!/nix/store/sp5x6s8n36gjlwck74xhj1i61p66vcpa-python3-3.10.9
   python3.10-esbonio> wrapping `/nix/store/91b7mh7ib0fxwn2kgv47v0sdpl05xqh1-python3.10-esbonio-0.16.1/bin/esbonio-sphinx'...
   python3.10-esbonio> Executing pythonRemoveTestsDir
   python3.10-esbonio> Finished executing pythonRemoveTestsDir
   python3.10-esbonio> pythonCatchConflictsPhase
   python3.10-esbonio> pythonRemoveBinBytecodePhase
   python3.10-esbonio> pythonImportsCheckPhase
   python3.10-esbonio> Executing pythonImportsCheckPhase
   python3.10-esbonio> Check whether the following modules can be imported: esbonio.lsp

   (nix-shell) $

And it actually worked! 🤯

Conclusion
----------

I have no idea why Nix needed me to move the ``overridePythonAttrs`` call out into a separate ``let`` binding, but hey it works!

I've finally managed to recreate the setup I had in my :doc:`original </blog/2022/first-steps-with-nix>` blog post, spinning up ``devShells`` in order to test ``esbonio`` against a range of Python versions - just with the added flexibility that working with overlays can bring.

If you're interested you can find the final version of all my ``*.nix`` files
`here (pytest-lsp) <https://github.com/swyddfa/lsp-devtools/commit/6ae80a24b55d2b6943b9d30805cf02440ebbaf5c>`__
and
`here (esbonio) <https://github.com/alcarney/esbonio/commit/6830a5fd0fe4c4f197d591d35d189a17fc561146>`__.
Hopefully next time we can build on this and finally use Nix for something you can't get out of standard Python tooling! 😅
