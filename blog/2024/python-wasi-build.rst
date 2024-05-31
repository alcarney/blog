.. post:: 2024-04-10
   :tags: nix, python, wasi
   :author: Alex Carney
   :language: en
   :excerpt: 2

Building the WASI version of CPython using Nix
==============================================

:doc:`Previously </blog/2023/python-wasi-nix>`, when setting up a development environment using the WASI build of Python with Nix, I "cheated" and just copied the result from an
`existing <https://github.com/brettcannon/cpython-wasi-build/releases>`__
build.
In this blog post I attempt to do it for real and use Nix to build the WASI version of CPython from source.

Thanks to the fact there are now
`docs available <https://devguide.python.org/getting-started/setup-building/#wasi>`__
as a well as a
`build script <https://github.com/python/cpython/blob/5d21d884b6ffa45dac50a5f9a07c41356a8478b4/Tools/wasm/wasi.py>`__
, the build process itself was quite straightforward.
The difficult part was getting all the dependencies setup correctly!

.. note::

   If you just want to see the final result, you can find it on `GitHub <>`__

On with the show!

Setup
-----

I've never built CPython from source before, so had no idea how different the WASI build might be when compared to a regular build.
I assumed however, that they should be similar enough that I could get away with taking an existing CPython derivation from nixpkgs and overriding the relevant attributes.

If we use a function that accepts an existing CPython derivation as input, it should be possible to derive a WASI build for any compatible version of Python.

.. code-block:: nix

   # In ./nix/to-wasi-build.nix
   { python }:

   python.overrideAttrs (prev: {})

Let's quickly test it out in a flake

.. code-block:: nix

   # In flake.nix
   outputs = { self, nixpkgs }:
     let
       system = "x86_64-linux";
       pkgs = nixpkgs.legacyPackages."${system}";
       toWasiBuild = import ./nix/to-wasi-build.nix;
     in {
       packages."${system}".default = toWasiBuild { python = pkgs.python312; };
     };

Of course, ``toWasiBuild`` doesn't do anything yet, so this should produce a derivation identical to the existing Python 3.12 derivation in nixpkgs

.. code-block:: console

   $ nix build
   $ ./result/bin/python
   Python 3.12.2 (main, Feb  6 2024, 20:19:44) [GCC 13.2.0] on linux
   Type "help", "copyright", "credits" or "license" for more information.
   >>>

And indeed it does! Nix happily fetched a pre-compiled copy from the binary cache!

In the ``Tools/wasm`` folder of the CPython repository, there is a ``wasm.py`` script that automates the build process.
So the most obvious thing to try is overriding the ``buildPhase`` of the derivation to call it.

.. code-block:: nix

   # In ./nix/to-wasi-build.nix
   python.overrideAttrs (prev: {
     buildPhase = ''
       ${python}/bin/python $src/Tools/wasm/wasi.py build
     '';
   })

.. note::
   :class: mt-4

   It turns out that this build script is so new that it does not exist in the published sources for ``3.12``!
   So I switched to trying to build Python ``3.13.0a5`` instead.

Let's give it a try and see what breaks...

.. code-block:: console

   $ nix build
   ValueError: WASI-SDK not found; download from https://github.com/WebAssembly/wasi-sdk and/or specify via $WASI_SDK_PATH or --wasi-sdk

Of course, we need a compiler capable of emitting WebAssembly!

Compiling the Compiler
----------------------

I had hoped that the `wasi-sdk <https://github.com/WebAssembly/wasi-sdk>`__, required to compile CPython to WebAssembly, would already be packaged in nixpkgs.
Unfortunately, despite finding a derivation for
`wasi-libc <https://github.com/NixOS/nixpkgs/blob/d8fe5e6c92d0d190646fb9f1056741a229980089/pkgs/development/libraries/wasilibc/default.nix>`__,
the only reference to the SDK itself I could find was
`this issue <https://github.com/NixOS/nixpkgs/issues/182356#issuecomment-1202457048>`__
which seems to suggest that you don't need the full SDK package.

Indeed, the
`README <https://github.com/WebAssembly/wasi-sdk/blob/a50a641f4b5a1398fcc811264272aae5bdd3b763/README.md>`__
for the SDK itself mentions that you can re-use an existing Clang installation by passing a WASI specific ``sysroot``
and "copying the ``libclang_rt.builtins-wasm32.a`` objects" to a specific location within the Clang installation...

Since those instructions didn't mean much to me and since the ``wasm.py`` build script itself looks like its meant to work with the full SDK build, I decided to bite the bullet and write a derivation for it myself.

After all, how hard can it be? 😅

First Attempt
^^^^^^^^^^^^^

The instructions for building the SDK were straightforward enough and before long I had put together an initial derivation to try

.. code-block:: nix

   # In ./nix/wasi-sdk.nix
   { fetchFromGitHub
   , stdenv
   , ninja
   , cmake
   }:

   let
     pname = "wasi-sdk";
     version = "20";
   in

   stdenv.mkDerivation {
     inherit pname version;

     src = fetchFromGitHub {
       owner = "WebAssembly";
       repo = "wasi-sdk";
       rev = "refs/tags/wasi-sdk-${version}";
       hash = "sha256-Vr/us4HLHsu1jb/vR3aGG/R6l7ffTC89IeGv0+U3fLE=";
     };

     nativeBuildInputs = [
       cmake
       ninja
     ];

     buildPhase = ''
       NINJA_FLAGS=-v make
     '';
   }


However, I got stuck on this error for a while...

.. code-block:: console

   error: builder for '/nix/store/rkrvgdxrilc130kcsqgl85wsk4qvpv1c-wasi-sdk-20.drv' failed with exit code 1;
          last 10 log lines:
          > fixing cmake files...
          > cmake flags: -DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF -DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF -DCMAKE_EXPORT_NO_PACKAGE_REGISTRY=ON -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DCMAKE_INSTALL_LOCALEDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/share/locale -DCMAKE_INSTALL_LIBEXECDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/libexec -DCMAKE_INSTALL_LIBDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/lib -DCMAKE_INSTALL_DOCDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/share/doc/wasi-sdk -DCMAKE_INSTALL_INFODIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/share/info -DCMAKE_INSTALL_MANDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/share/man -DCMAKE_INSTALL_OLDINCLUDEDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/include -DCMAKE_INSTALL_INCLUDEDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/include -DCMAKE_INSTALL_SBINDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/sbin -DCMAKE_INSTALL_BINDIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/bin -DCMAKE_INSTALL_NAME_DIR=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20/lib -DCMAKE_POLICY_DEFAULT_CMP0025=NEW -DCMAKE_OSX_SYSROOT= -DCMAKE_FIND_FRAMEWORK=LAST -DCMAKE_STRIP=/nix/store/kvlhk0gpm2iz1asbw1xjac2ch0r8kyw9-gcc-wrapper-13.2.0/bin/strip -DCMAKE_RANLIB=/nix/store/kvlhk0gpm2iz1asbw1xjac2ch0r8kyw9-gcc-wrapper-13.2.0/bin/ranlib -DCMAKE_AR=/nix/store/kvlhk0gpm2iz1asbw1xjac2ch0r8kyw9-gcc-wrapper-13.2.0/bin/ar -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_INSTALL_PREFIX=/nix/store/0wbzj0ks5f9ni2nd2q11f03yv9jimzph-wasi-sdk-20
          > CMake Warning:
          >   Ignoring extra path from command line:
          >
          >    ".."
          >
          >
          > CMake Error: The source directory "/build/source" does not appear to contain CMakeLists.txt.
          > Specify --help for usage, or press the help button on the CMake GUI.
          For full logs, run 'nix log /nix/store/rkrvgdxrilc130kcsqgl85wsk4qvpv1c-wasi-sdk-20.drv'.

It took me longer than I'd like to admit to figure that the build wasn't even failing in the ``buildPhase`` I'd specified!

I discovered that ``stdenv.mkDerivation`` has a pre-defined ``configurePhase`` that is included by default.
Rather than look up the proper way to disable the ``configurePhase``, I opted to override it with a simple ``echo`` command and moved on.

.. code-block:: nix

   # In ./nix/wasi-sdk.nix
   configurePhase = ''
     echo "Skipping..."
   '';

Missing Sources
^^^^^^^^^^^^^^^

Now that the build was actually making it into the ``buildPhase`` I encountered my first real issue - there were no files under any of the ``src/`` directories!

It turns out that the ``wasi-sdk`` repo is a collection of build scripts which operate on source code defined in other repositories and that code is included via git submodules.
Not the end of the world, I looked up how to include submodules and updated the derivation

.. code-block:: nix

   # In ./nix/wasi-sdk.nix
   src = fetchFromGitHub {
     owner = "WebAssembly";
     repo = "wasi-sdk";
     rev = "refs/tags/wasi-sdk-${version}";
     hash = "sha256-Vr/us4HLHsu1jb/vR3aGG/R6l7ffTC89IeGv0+U3fLE=";
     fetchSubmodules = true;
   };

And yet, when I reran the build, the source folders were *still* empty.

Not sure why, but I can only conclude that the ``fetchSubmodules`` argument is invisible to however nix detects changes.
On a hunch I deleted the existing store path for the sources (``nix-store --delete /nix/store/<hash>-source``) and tried again, leading to the most cryptic git error I've seen in a while...

.. code-block:: console

   error: Server does not allow request for unadvertised object d546e3f738e14c62e732346fa355162d46700893

I have no idea why it works, but I was lucky enough to stumble across `this comment <https://github.com/NixOS/nixpkgs/issues/100498#issuecomment-1846499310>`__ and tried including the ``leaveDotGit = true`` argument.

.. code-block:: nix

   # In ./nix/wasi-sdk.nix
   src = fetchFromGitHub {
     owner = "WebAssembly";
     repo = "wasi-sdk";
     rev = "refs/tags/wasi-sdk-${version}";
     hash = "sha256-Vr/us4HLHsu1jb/vR3aGG/R6l7ffTC89IeGv0+U3fLE=";
     fetchSubmodules = true;
     leaveDotGit = true;
   };


It took **hours** to fully clone the repo and all of its submodules but I was finally able to get the source code downloaded (and thankfully!) cached in ``/nix/store`` 🎉

Install Time
^^^^^^^^^^^^

Once the source was available, getting it to build was actually quite easy, the only build dependency I needed add in addition to those on the project's README was python.

The next issue showed up during the ``installPhase``

.. code-block:: console

   error: builder for '/nix/store/b9mxjw6l57frlk21xc5dgvvrf8f8issj-wasi-sdk-20.drv' failed with exit code 1;
          last 10 log lines:
          > mkdir -p /build/source/build/install/opt/wasi-sdk/share/misc
          > cp src/config/config.sub src/config/config.guess /build/source/build/install/opt/wasi-sdk/share/misc
          > mkdir -p /build/source/build/install/opt/wasi-sdk/share/cmake
          > cp wasi-sdk.cmake /build/source/build/install/opt/wasi-sdk/share/cmake
          > cp wasi-sdk-pthread.cmake /build/source/build/install/opt/wasi-sdk/share/cmake
          > touch build/config.BUILT
          > buildPhase completed in 2 hours 35 minutes 4 seconds
          > Running phase: installPhase
          > install flags: -j4 install
          > ninja: error: loading 'build.ninja': No such file or directory
          For full logs, run 'nix log /nix/store/b9mxjw6l57frlk21xc5dgvvrf8f8issj-wasi-sdk-20.drv'.


Which in hindsight, was to be expected as the project's ``Makefile`` doesn't define an ``install`` target.
Taking a peek at the ``wasi.py`` script and the build artifacts `published <https://github.com/WebAssembly/wasi-sdk/releases>`__ on GitHub, I came up with the following

.. code-block:: nix

   # In ./nix/wasi-sdk.nix
   installPhase = ''
     mkdir $out
     cp -r build/install/opt $out/opt
   '';

Building Python
---------------

Where were we?.. Oh yes, building Python!
Now that we've built the ``wasi-sdk`` we just need to make it available to the build

.. code-block:: nix

   # In ./nix/to-wasi-build.nix
   buildPhase = ''
    WASI_SDK_PATH=${wasi-sdk}/opt/wasi-sdk ${python}/bin/python Tools/wasm/wasi.py build
   '';

Run it again to see what fails

.. code-block:: console

   error: builder for '/nix/store/yrj06fy21g8lav1yif1ib5fycbnc34n8-python3-3.13.0a5.drv' failed with exit code 1;
          last 10 log lines:
          >                         pass_fds, cwd, env,
          >                         ^^^^^^^^^^^^^^^^^^^
          >     ...<5 lines>...
          >                         gid, gids, uid, umask,
          >                         ^^^^^^^^^^^^^^^^^^^^^^
          >                         start_new_session, process_group)
          >                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          >   File "/nix/store/6azrwi0qmbs62w9k7yxrjrvhc28v20kh-python3-3.13.0a5/lib/python3.13/subprocess.py", line 1959, in _execute_child
          >     raise child_exception_type(errno_num, err_msg, err_filename)
          > FileNotFoundError: [Errno 2] No such file or directory: 'git'

Add the missing ``git`` dependency

.. code-block:: nix

   # In ./nix/to-wasi-build.nix
   nativeBuildInputs = prev.nativeBuildInputs ++ [
     git
   ]


At this point, it looks like the build is going well.

I don't fully understand why, but the ``wasi.py`` script actually builds Python twice, the first is (I think) compiled for the host machine and somehow helps to build the second interpreter, which is the actual WASI version we're interested in.

The first interpreter builds without issue, but when it comes to the WASI version...

.. code-block:: console

   python3> checking whether the C compiler works... no
   python3> configure: error: in '/build/Python-3.13.0a5/cross-build/wasm32-wasi':
   python3> configure: error: C compiler cannot create executables


I'm fairly sure that's something a compiler should be able to do! 😅

Compiling the Compiler, Again!
------------------------------

To try and narrow down where the issue was, I attempted to compile a simple "Hello, World!" C program using the compiler I just built from the ``wasi-sdk``.

.. code-block:: console

   $ /nix/store/7552vglan9dha3gbw3d57d62nlbcy4ra-wasi-sdk-20/opt/wasi-sdk/bin/clang main.c -I /nix/store/7552vglan9dha3gbw3d57d62nlbcy4ra-wasi-sdk-20/opt/wasi-sdk/share/wasi-sysroot/include/
   wasm-ld: error: cannot open crt1.o: No such file or directory
   wasm-ld: error: unable to find library -lc
   wasm-ld: error: cannot open /nix/store/7552vglan9dha3gbw3d57d62nlbcy4ra-wasi-sdk-20/opt/wasi-sdk/lib/clang/16/lib/wasi/libclang_rt.builtins-wasm32.a: No such file or directory
   clang-16: error: linker command failed with exit code 1 (use -v to see invocation)

Ok... so something is wrong with the build, I checked and indeed, the file it's looking for is definitely missing...

Comparing my result with the version available from the project itself, I notice that the right files are being produced, but for some reason they're in the wrong place.
Specifically, my copy of ``libclang_rt.builtins-wasm32.a`` is in ``lib/clang/lib/wasi`` when it should be in ``lib/clang/16/lib/wasi``...

Spending some time reading the project's
`Makefile <https://github.com/WebAssembly/wasi-sdk/blob/2d7853c64b0b118d71764b132df1593c2c7545bf/Makefile>`__
I eventually spot the ``CLANG_VERSION`` variable used throughout the ``build/comiler-rt`` target

.. code-block:: make

   build/compiler-rt.BUILT: build/llvm.BUILT
       # Do the build, and install it.
       mkdir -p build/compiler-rt
       cd build/compiler-rt && cmake -G Ninja \
               ...
               -DCMAKE_INSTALL_PREFIX=$(PREFIX)/lib/clang/$(CLANG_VERSION)/ \
               ...
       DESTDIR=$(DESTDIR) ninja $(NINJA_FLAGS) -C build/compiler-rt install
       # Install clang-provided headers.
       cp -R $(ROOT_DIR)/build/llvm/lib/clang $(BUILD_PREFIX)/lib/
       cp -R $(BUILD_PREFIX)/lib/clang/$(CLANG_VERSION)/lib/wasi $(BUILD_PREFIX)/lib/clang/$(CLANG_VERSION)/lib/wasip1
       cp -R $(BUILD_PREFIX)/lib/clang/$(CLANG_VERSION)/lib/wasi $(BUILD_PREFIX)/lib/clang/$(CLANG_VERSION)/lib/wasip2
       touch build/compiler-rt.BUILT

If ``CLANG_VERSION`` were not set, that would definitely explain the results I'm seeing...

.. code-block:: make

   CLANG_VERSION=$(shell $(BASH) ./llvm_version_major.sh $(LLVM_PROJ_DIR))
   VERSION:=$(shell $(BASH) ./version.sh)

Hmm, I guess this script must be failing...

.. code-block:: console

   $ nix log /nix/store/li46r4ib0fqk26i71p9ab906iiakzwpm-wasi-sdk-20.drv
   ...
   wasi-sdk> Running phase: buildPhase
   wasi-sdk> make: ./version.sh: No such file or directory
   wasi-sdk> make: ./llvm_version_major.sh: No such file or directory

Why this is not considered to be an error severe enough to halt the build I have no idea!

Anyway, it took me a **long** time to figure out why ``make`` couldn't find the scripts - they were clearly in the project's source! I could even ``cat`` their contents!!

Eventually I realised, that the file or directory ``make`` was unable to find, wasn't the scripts themselves, it was ``/bin/bash`` specified by the shebang on the first line of each script! 😭
After *much* trial and error, I came up with the following hacks to modify the scripts so that they would behave in a Nix context

.. code-block:: nix

   postPatch = ''
     substituteInPlace llvm_version_major.sh \
       --replace-fail /bin/bash "!${bash}/bin/bash"

     cat << EOF > version.sh
     #!${bash}/bin/bash
     echo "${version}"
     EOF
   '';

Building Python, Continued
--------------------------

After finally producing a WASI compiler that could... well, compile, I switched back to the Python build.
It seemed to be working perfectly, right up until the final step of the ``make_wasi_python`` function.

.. code-block:: console

   python-wasi> Error: failed to create cache directory: /homeless-shelter/.cache/wasmtime
   python-wasi> Caused by:
   python-wasi>     Permission denied (os error 13)
   python-wasi> Traceback (most recent call last):
   python-wasi>   File "/build/Python-3.13.0a5/Tools/wasm/wasi.py", line 347, in <module>
   python-wasi>     main()
   python-wasi>     ~~~~^^
   python-wasi>   File "/build/Python-3.13.0a5/Tools/wasm/wasi.py", line 343, in main
   python-wasi>     dispatch[context.subcommand](context)
   python-wasi>     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
   python-wasi>   File "/build/Python-3.13.0a5/Tools/wasm/wasi.py", line 265, in build_all
   python-wasi>     step(context)
   python-wasi>     ~~~~^^^^^^^^^
   python-wasi>   File "/build/Python-3.13.0a5/Tools/wasm/wasi.py", line 79, in wrapper
   python-wasi>     return func(context, working_dir)
   python-wasi>            ~~~~^^^^^^^^^^^^^^^^^^^^^^
   python-wasi>   File "/build/Python-3.13.0a5/Tools/wasm/wasi.py", line 257, in make_wasi_python
   python-wasi>     subprocess.check_call([exec_script, "--version"])
   python-wasi>     ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   python-wasi>   File "/nix/store/6azrwi0qmbs62w9k7yxrjrvhc28v20kh-python3-3.13.0a5/lib/python3.13/subprocess.py", line 4
   17, in check_call
   python-wasi>     raise CalledProcessError(retcode, cmd)
   python-wasi> subprocess.CalledProcessError: Command '[PosixPath('/build/Python-3.13.0a5/cross-build/wasm32-wasi/python.
   sh'), '--version']' returned non-zero exit status 1.

This step tries to execute a ``wasmtime run`` command that had been written to a shell script during the configure step of the build - something that isn't going to work out of the box in Nix context.

The easiest thing to do is to modify the script to simply not call it, especially when it's only doing the equivalent of ``python --version``.

.. code-block:: nix

   postPatch = ''
     substituteInPlace Tools/wasm/wasi.py \
       --replace-fail 'subprocess.check_call([exec_script, "--version"])' ""
   '';


Finally, all that remains is to copy the build artifacts to the derivation's ``$out`` directory.
This was less straightforward than I was expecting simply because Python's standard library is not automatically copied into a ``lib/python3.x`` folder as you might expect.

However, thanks to Brett Cannon's
`existing build pipeline <https://github.com/brettcannon/cpython-wasi-build/blob/main/.github/workflows/release.yml>`__
I had something I could reference.

.. code-block:: nix

   installPhase = ''
     export LIB_DIR=$out/lib/python${lib.versions.majorMinor prev.version}
     mkdir -p $LIB_DIR/site-packages

     cp cross-build/wasm32-wasi/python.wasm $out

     cp -r Lib/* $LIB_DIR
     mkdir $LIB_DIR/lib-dynload

     pushd $LIB_DIR
     rm -rf curses/ \
            ctypes/test/ \
            ensurepip/ \
            distutils/ \
            idlelib/ \
            lib2to3/ \
            multiprocessing/ \
            test/ \
            tkinter/ \
            turtledemo/ \
            unittest/test/ \
            venv/

     find -name __pycache__ -exec rm -rf {} \;
     popd

     cp cross-build/wasm32-wasi/build/lib.wasi-wasm32-*/_sysconfigdata_*.py $LIB_DIR

   '';

However, the result this breaks the rules...

.. code-block:: console

   $ nix build
   error: output '/nix/store/x3j1wpiqf1fcqzw24ww2qmr50a5mxfi5-python-wasi-3.13.0a5' is not allowed to refer to the following paths:
       /nix/store/yg75achq89wgqn2fi3gglgsd77kjpi03-openssl-3.0.13-dev



Running it
----------

Assuming that the build is equivalent to one I was using previously, everything should be identical from here on out.
However, ``wasmtime`` has changed its CLI slightly since I tried it last.

.. code-block:: console

   (nix-shell) > python
   warning: this CLI invocation of Wasmtime will be parsed differently in future
            Wasmtime versions -- see this online issue for more information:
            https://github.com/bytecodealliance/wasmtime/issues/7384

            Wasmtime will now execute with the old (<= Wasmtime 13) CLI parsing,
            however this behavior can also be temporarily configured with an
            environment variable:

            - WASMTIME_NEW_CLI=0 to indicate old semantics are desired and silence this warning, or
            - WASMTIME_NEW_CLI=1 to indicate new semantics are desired and use the latest behavior
   Python 3.13.0a5 (main, Mar 12 2024, 20:11:08) [Clang 16.0.0 ] on wasi
   Type "help", "copyright", "credits" or "license" for more information.
   >>>

So, a few tweaks to the wrapper derivation are in order.

- Rather than hardcoding the ``lib/python3.x`` path, let's compute is based on the Python version
- Enable ``WASI Preview 2 <https://github.com/WebAssembly/WASI/blob/main/preview2/README.md>`__ ``--wasi preview2``
- All arguments to ``wasmtime`` itself, must come before the ``*.wasm`` binary itself.
