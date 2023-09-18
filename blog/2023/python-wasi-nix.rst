.. post:: 2023-09-18
   :tags: nix, python, wasm
   :author: me
   :language: en
   :excerpt: 1

Setting up a Python WASI Environment with Nix
=============================================

In this blog post I look at setting up a local development environment for the `WASI build of Python <https://github.com/brettcannon/cpython-wasi-build>`_  using Nix.
You can see the final result `here <https://github.com/alcarney/python-wasi-nix>`__

Why?
----

.. admonition:: WASM and Pyodide and WASI, Oh My!

   See Brett Cannon's `blog post <https://snarky.ca/webassembly-and-its-platform-targets/>`__ for a good overview of the different flavours of WebAssembly platforms.

Some :doc:`time ago </blog/2021/bringing-esbonio-to-the-browser>` now, I stated that I wanted to get the `esbonio`_ language server running in `vscode.dev <https://vscode.dev>`__.
While there
`has been <https://github.com/swyddfa/esbonio/pull/438>`__
some
`progress <https://github.com/swyddfa/esbonio/commit/046d63d8ca07d647498d800fb88f76792bd88ee8>`__
towards this goal it's been little more than proof of concepts.

One of the biggest challenges has been sharing the contents of the workspace with the `pyodide`_ runtime I was using to host the language server.
But now that the VSCode team are turning `VSCode into a WASI runtime <https://code.visualstudio.com/blogs/2023/06/05/vscode-wasm-wasi>`_ it might finally be possible to port ``esbonio`` to the web!

As a bonus, since `WASI <https://wasi.dev>`__ is a standard, I can use `wasmtime <https://wasmtime.dev>`__ as the host when working on the port locally.
Which brings us to the topic of this blog post.

Ok, but why use Nix?
--------------------

I'm sure you could achieve everything that I do here with a bash script but I've been playing with Nix :ref:`a lot <tag-nix>` recently and I think it's cool!

If you want Python + WASI without the Nix see `this blog post <https://snarky.ca/testing-a-project-using-the-wasi-build-of-cpython-with-pytest/>`__, which I used as the basis for figuring this out.

"Building" Python
-----------------

As an initial step, let's see if we can get to the point where we can launch a ``devShell`` in which we can run the WASI version of Python.

To get the WASM build of Python onto our machine we'll write a derivation that "builds" it by downloading the release artifact from GitHub and copying it to the output folder

.. admonition:: This is "wrong"

   To do this the "right" way, I should be using Nix to build the WASI version of Python from source.
   But since Brett Cannon is `publishing builds <https://github.com/brettcannon/cpython-wasi-build>`_ on GitHub I'm going to leave that as an exercise for the reader.

.. code-block:: nix

   # In ./nix/python-wasi.nix
   { fetchzip, stdenv }:

   stdenv.mkDerivation {
     pname = "python-wasi";
     version = "3.11.4";

     src = fetchzip {
       url = "https://github.com/brettcannon/cpython-wasi-build/releases/download/v3.11.4/python-3.11.4-wasi_sdk-16.zip";
       stripRoot = false;
       sha256 = "sha256-AZGdgpRvHcu6FY/a7capldjDhTpkfhGkqYnm127nAN8=";
     };

     buildCommand = ''
      mkdir $out
      cp -r $src/* $out
     '';
   }

In a corresponding ``flake.nix`` file we can define a ``devShell`` containing both the WASI build of Python and the ``wasmtime`` program required to execute it

.. code-block:: nix

   # In ./flake.nix
   utils.lib.eachDefaultSystem(system:
     let
       pkgs = import nixpkgs { inherit system; };
       python-wasi = pkgs.callPackage ./nix/python-wasi.nix {};
     in {

       devShells.default = pkgs.mkShell {
         name = "wasi";
         shellHook = ''
            export PYTHON_WASI=${python-wasi}
         '';
         packages = with pkgs; [ wasmtime ];
       };
     }
   );

Which will be enough to give an an environment where we can try to run a simple Python script::

  (nix-shell) $ wasmtime run $PYTHON_WASI/python.wasm -- -c "import sys;print(sys.platform)"
  Could not find platform independent libraries <prefix>
  Could not find platform dependent libraries <exec_prefix>
  Python path configuration:
    PYTHONHOME = (not set)
    PYTHONPATH = (not set)
    program name = 'python.wasm'
    isolated = 0
    environment = 1
    user site = 1
    safe_path = 0
    import site = 1
    is in build tree = 0
    stdlib dir = '/usr/local/lib/python3.11'
    sys._base_executable = ''
    sys.base_prefix = '/usr/local'
    sys.base_exec_prefix = '/usr/local'
    sys.platlibdir = 'lib'
    sys.executable = ''
    sys.prefix = '/usr/local'
    sys.exec_prefix = '/usr/local'
    sys.path = [
      '/usr/local/lib/python311.zip',
      '/usr/local/lib/python3.11',
      '/usr/local/lib/python3.11/lib-dynload',
    ]
  Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding
  Python runtime state: core initialized
  ModuleNotFoundError: No module named 'encodings'

  Current thread 0x00000000 (most recent call first):
    <no Python frame>

Well, that was the plan at least! 😅

Making it work
--------------

Of course... introducing Nix is going to bring its own set of challenges.
Looking at the error message above we can see that Python assumes it has been installed on a traditional Linux operating system and is looking for its standard library under ``/usr/local``.
However, looking at the ``PYTHON_WASI`` environment variable we can see this is not the case::

   (nix-shell) $ echo $PYTHON_WASI
   /nix/store/5n0m7jxcnksmnp52maxa4li1q91gwq2v-python-wasi-3.11.4

   (nix-shell) $ ls $PYTHON_WASI
   lib/  python.wasm*

Thankfully, it's easy enough to fix with the `PYTHONHOME <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHOME>`__ environment variable, we can rename ``PYTHON_WASI`` to ``PYTHONHOME`` in the shell's ``shellHook``

.. code-block:: nix

   shellHook = ''
       export PYTHONHOME=${python-wasi}
   ''

However, since ``wasmtime`` implements a `capability security model <https://en.wikipedia.org/wiki/Capability-based_security>`__
we also have to grant access to the both the environment variable **and** the folder it points to::

  $ wasmtime run $PYTHONHOME/python.wasm --env PYTHONHOME=$PYTHONHOME --dir $PYTHONHOME -- -c "import sys; print(sys.platform)"
  wasi

Success!

Creating a Wrapper
------------------

While we can now run the WASI Python build, the command to invoke it is rather unwieldy... and we're not doing anything interesting yet!
Thankfully, we can also use Nix to hide some of these details for us.

A common pattern you will see in `nixpkgs <https://github.com/NixOS/nixpkgs>`_ is to have a ``<program-name>-unwrapped`` package whose job it is to build said program into a folder in the nix store.
Then a second ``<program-name>`` package containing a bash script that handles the details of invoking the program from within the ``/nix/store``.

So let's do the same here!

.. code-block:: nix

   # In ./nix/python.nix
   { wasmtime, python-wasi, writeShellScriptBin }:

   writeShellScriptBin "python" ''
      ${wasmtime}/bin/wasmtime run ${python-wasi}/python.wasm \
        --env PYTHONHOME=${python-wasi} \
        --dir ${python-wasi} \
        -- "$@"
   ''

Which allows us to update our ``devShell`` definition to the following.

.. code-block:: nix

   utils.lib.eachDefaultSystem(system:
     let
       pkgs = import nixpkgs { inherit system; };
       python-wasi = pkgs.callPackage ./nix/python-wasi.nix {};
       python = pkgs.callPackage ./nix/python.nix { python-wasi = python-wasi; };
     in {

       devShells.default = pkgs.mkShell {
         name = "wasi";
         packages = [ python ];
       };
     }
    );

Notice how we don't even need to reference ``wasmtime`` here anymore?
In fact (assuming the ``devShell`` is active), we can call Python as we would normally!::

  $ python -c "import sys; print(sys.platform)"
  linux

  $ nix develop
  (nix-shell) $ python -c "import sys; print(sys.platform)"
  wasi

🤯

.. tip::

   You can see the contents of the wrapper script we generated by running::

     (nix-shell) $ cat $(command -v python)
     #!/nix/store/ir0j7zqlw9dc49grmwplppc7gh0s40yf-bash-5.2-p15/bin/bash
     /nix/store/kv8y59aqkz8havf9whvvknm7z05by2dk-wasmtime-11.0.1/bin/wasmtime run /nix/store/5n0m7jxcnksmnp52maxa4li1q91gwq2v-python-wasi-3.11.4/python.wasm \
       --env PYTHONHOME=/nix/store/5n0m7jxcnksmnp52maxa4li1q91gwq2v-python-wasi-3.11.4 \
       --dir /nix/store/5n0m7jxcnksmnp52maxa4li1q91gwq2v-python-wasi-3.11.4 \
       -- "$@"

But we're not done yet!
Our Python process does not have access to any files outside of the stdlib

.. code-block:: python

   Python 3.11.4 (tags/v3.11.4-dirty:d2340ef, Jun  8 2023, 00:39:32) [Clang 14.0.4 (https://github.com/llvm/llvm-project 29f1039a7285a5c3a9c353d05414 on wasi
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import os
   >>> os.listdir('.')
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   PermissionError: [Errno 76] Capabilities insufficient: '.'

But passing an additional ``--dir .`` argument to ``wasmtime`` will solve that for us.
The more challenging issue to solve is passing through third party libraries

.. code-block:: python

   Python 3.11.4 (tags/v3.11.4-dirty:d2340ef, Jun  8 2023, 00:39:32) [Clang 14.0.4 (https://github.com/llvm/llvm-project 29f1039a7285a5c3a9c353d05414 on wasi
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import attrs
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   ModuleNotFoundError: No module named 'attrs'


Installing packages
-------------------

Here is where I'm going to take another shortcut, to do this "correctly" I should probably look at overriding the base Python derivation so that it (and everything that depends on it) uses the WASI build of Python.
This would trigger Nix to (lazily) rebuild all of the Python packages in ``nixpkgs`` against that version of Python.

However, there's a strong chance that a lot of builds will break and in reality all we really need is a folder full of Python files to import.

.. admonition:: What about packages like ``numpy``?

   While I think there are some moves towards enabling support for packages like ``numpy`` (via the WASM Component Model?),
   if you want to use packages that contain native code in WebAssembly, `pyodide`_  is probably the best bet for the time being, especially for data science libraries.

   This however, is beyond the scope of this blog post.

So why not reuse the packages already in ``nixpkgs``?

We can take a list of Python package derivations and construct a string to set as the `PYTHONPATH <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`__ environment variable - making all of the required dependencies available to the interpreter.

Gathering Dependencies
^^^^^^^^^^^^^^^^^^^^^^

The first thing we need to do is to figure out when given a Python package, is what all of its dependencies are.
Thankfully, to help us figure it out we can use the Nix REPL allowing us to inspect derivations and evaluate expressions::

   $ nix repl
   Welcome to Nix 2.11.1. Type :? for help.

   nix-repl> :lf .    # Load the flake located in the current directory
   Added 9 variables.

First let's locate a package that we're interested in, note that the ``inputs`` variable corresponds to the ``inputs`` attribute set we declared in our ``flake.nix`` file::

  nix-repl> pkgs = inputs.nixpkgs.legacyPackages.x86_64-linux.python311Packages
  nix-repl> pkgs.attrs
  «derivation /nix/store/bcgw61xp6ss6vaad5ghwqfbm2m795a2g-python3.11-attrs-22.2.0.drv»

To find out what attributes this derivation has we can type ``pkgs.attrs.`` and then hit :kbd:`Tab`::

  nix-repl> pkgs.attrs.
  pkgs.attrs.LANG                         pkgs.attrs.outPath
  pkgs.attrs.__ignoreNulls                pkgs.attrs.outputName
  pkgs.attrs.__structuredAttrs            pkgs.attrs.outputs
  pkgs.attrs.all                          pkgs.attrs.override
  pkgs.attrs.args                         pkgs.attrs.overrideAttrs
  pkgs.attrs.buildInputs                  pkgs.attrs.overrideDerivation
  pkgs.attrs.builder                      pkgs.attrs.overridePythonAttrs
  pkgs.attrs.cmakeFlags                   pkgs.attrs.passthru
  pkgs.attrs.configureFlags               pkgs.attrs.patches
  pkgs.attrs.depsBuildBuild               pkgs.attrs.pname
  pkgs.attrs.depsBuildBuildPropagated     pkgs.attrs.postFixup
  pkgs.attrs.depsBuildTarget              pkgs.attrs.postInstall
  pkgs.attrs.depsBuildTargetPropagated    pkgs.attrs.propagatedBuildInputs
  pkgs.attrs.depsHostHost                 pkgs.attrs.propagatedNativeBuildInputs
  pkgs.attrs.depsHostHostPropagated       pkgs.attrs.pythonImportsCheck
  pkgs.attrs.depsTargetTarget             pkgs.attrs.pythonModule
  pkgs.attrs.depsTargetTargetPropagated   pkgs.attrs.pythonPath
  pkgs.attrs.disallowedReferences         pkgs.attrs.requiredPythonModules
  pkgs.attrs.dist                         pkgs.attrs.src
  pkgs.attrs.doCheck                      pkgs.attrs.stdenv
  pkgs.attrs.doInstallCheck               pkgs.attrs.strictDeps
  pkgs.attrs.drvAttrs                     pkgs.attrs.system
  pkgs.attrs.drvPath                      pkgs.attrs.testout
  pkgs.attrs.inputDerivation              pkgs.attrs.tests
  pkgs.attrs.mesonFlags                   pkgs.attrs.type
  pkgs.attrs.meta                         pkgs.attrs.updateScript
  pkgs.attrs.name                         pkgs.attrs.userHook
  pkgs.attrs.nativeBuildInputs            pkgs.attrs.version
  pkgs.attrs.out

Well ``requiredPythonModules`` looks interesting::

  nix-repl> pkgs.attrs.requiredPythonModules
  [ «derivation /nix/store/2dml7fbspshiwb1j896jd3ajrsq81nl5-python3-3.11.4.drv» ]

I guess the only dependencies ``attrs`` has is Python itself, that's good to know as we will have to drop that from the list of dependencies::

  nix-repl> lib = inputs.nixpkgs.lib
  nix-repl> python = inputs.nixpkgs.legacyPackages.x86_64-linux.python311
  nix-repl> python
  «derivation /nix/store/2dml7fbspshiwb1j896jd3ajrsq81nl5-python3-3.11.4.drv»

  nix-repl> lib.remove python pkgs.attrs.requiredPythonModules
  [ ]

Now, how about another package?::

  nix-repl> lib.remove python pkgs.pygls.requiredPythonModules
  [
    «derivation /nix/store/dsx8aalkf97pi0ja8xs9mlss5lk4bzhv-python3.11-lsprotocol-2023.0.0a2.drv»
    «derivation /nix/store/86933r4czjpmyq3ikz5444f1k1q9rij6-python3.11-typeguard-2.13.3.drv»
    «derivation /nix/store/bcgw61xp6ss6vaad5ghwqfbm2m795a2g-python3.11-attrs-22.2.0.drv»
    «derivation /nix/store/f19ymrh2zv9hzh00wjvjv73v529n3ds4-python3.11-cattrs-23.1.2.drv»
  ]

Based on some experiments I think ``requiredPythonModules`` automatically handles transitive dependencies for us!

Setting ``PYTHONPATH``
^^^^^^^^^^^^^^^^^^^^^^

I'll spare you the trial and error and skip to the following lines of nix code which take a list of ``pyPackages`` and converts it into a value we can use with ``PYTHONPATH``

.. code-block:: nix

   pyDeps = lib.concatMap (pkg: lib.remove pkg.pythonModule pkg.requiredPythonModules) pyPackages;
   allPackages = lib.unique (pyPackages ++ pyDeps);
   pythonPath = lib.concatMapStringsSep ":" (pkg: "${pkg}/lib/python3.11/site-packages") allPackages;

Don't forget we will also have to grant the process access to each of the folders we add to the ``PYTHONPATH``

.. code-block:: nix

   lib.concatMapStringsSep "\\\n  " (pkg: "--dir '${pkg}/lib/python3.11/site-packages' ") allPackages

``mkPythonWASIShell``
^^^^^^^^^^^^^^^^^^^^^

We now have everything we need to rewrite our ``./nix/python.nix`` file to define a helper function  which takes a list of Python packages and creates a ``devShell`` containing the WASI build of Python and all of our declared dependencies.

.. code-block:: nix

   # In ./nix/python.nix

   # Dependencies for our function (mostly) coming from `nixpkgs`
   { lib
   , python-wasi
   , mkShell
   , stdenv
   , wasmtime
   , writeShellScriptBin
   }:

   # Arguments the user can set when invoking the function
   { pyPackages ? []
   }:

   # Implementation details
   let
     pyDeps = lib.concatMap (pkg: lib.remove pkg.pythonModule pkg.requiredPythonModules) pyPackages;
     allPackages = lib.unique (pyPackages ++ pyDeps);
     pythonPath = lib.concatMapStringsSep ":" (pkg: "${pkg}/lib/python3.11/site-packages") allPackages;

     # This should look familiar...
     python = writeShellScriptBin "python" ''
      ${wasmtime}/bin/wasmtime run ${python-wasi}/python.wasm \
        --env PYTHONHOME=${python-wasi} \
        --env PYTHONPATH='.:${pythonPath}' \
        --dir ${python-wasi} \
        ${lib.concatMapStringsSep "\\\n  " (pkg: "--dir '${pkg}/lib/python3.11/site-packages' ") allPackages} \
        --dir . \
        -- "$@"
     '';

   in
   # Our function's return value
   mkShell {
     name = "python-wasi";
     packages = [ python ];
   }

The function only gets a name when we import it into the top-level ``flake.nix`` file

.. code-block:: nix

   pkgs = import nixpkgs { inherit system; };
   python-wasi = pkgs.callPackage ./nix/python-wasi.nix {};
   mkPythonWASIShell = pkgs.callPackage ./nix/python.nix { python-wasi = python-wasi; };

The ``callPackage`` function uses some kind of ✨magic✨ to automatically pass through all the dependencies (like ``wasmtime``) we declared in ``./nix/python.nix`` - except for ``python-wasi`` which we pass through by hand.

Defining an environment based on ``mkPythonWASIShell`` would then look something like the following

.. code-block:: nix

   devShells.default = mkPythonWASIShell {
     pyPackages = with pkgs.python311Packages; [
       pygls
     ];
   };

Which we can now try to develop with::

  $ nix develop
  (nix-shell) $ python
  Python 3.11.4 (tags/v3.11.4-dirty:d2340ef, Jun  8 2023, 00:39:32) [Clang 14.0.4 (https://github.com/llvm/llvm-project 29f1039a7285a5c3a9c353d05414 on wasi
  Type "help", "copyright", "credits" or "license" for more information.
  >>> from pygls.server import LanguageServer
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/nix/store/g4p26w5gh74nndclnskypc74ni37jqm6-python3.11-pygls-1.0.1/lib/python3.11/site-packages/pygls/server.py", line 42, in <module>
      from multiprocessing.pool import ThreadPool
  ModuleNotFoundError: No module named 'multiprocessing'
  >>>

Assuming the packages support the WASI runtime that is! 😅

Next steps
----------

If you are interested you can find the final version of the code `here <https://github.com/alcarney/python-wasi-nix>`__.
I'm not really sure where it will go from here, as it's now "good enough" for me to start hacking on the WASI runtime, but there's certainly plenty that could be improved.

- Building Python WASI from source
- Automatically choosing the right Python package set to use with ``mkPythonWASIShell``, like ``python.withPackages``
- Extending ``mkPythonWASIShell`` to allow the user to set the permissions for the Python process
- Overriding a base ``python`` derivation so that packages are built against this version of Python.
- Extending this to work with packages that contain native modules?


.. _esbonio: https://github.com/swyddfa/esbonio
.. _pyodide: https://pyodide.org/en/stable/
