:title: Building Emacs from Source
:date: 2025-04-09
:tags: emacs
:identifier: 20250409T205418
:signature: 5=5

Building Emacs from Source
==========================

.. highlight:: none

I suppose it was bound to happen sooner or later, the following is a simple script for building Emacs from source and installing it under ``${HOME}/.local``

.. code-block:: bash

   #!/bin/bash
   set -eux

   SRC="${HOME}/Projects/gnu/emacs/master"
   PREFIX="${HOME}/.local"

   pushd "$SRC"

   # Install build dependencies...
   sudo dnf builddep -y emacs

   ./configure \
       --prefix="${PREFIX}" \
       --disable-gc-mark-trace \
       --with-pgtk \
       --with-native-compilation=aot \
       --without-x

   read -p "Continue? [y/N] " -n 1 -r

   if [[ $REPLY =~ ^[Yy]$ ]]
   then
       make -j $(nproc)
   fi

Using Aurora as my OS poses a few challenges, so in order to make the above work

- The build itself was executed in a fedora distrobox

- I still have the fedora ``emacs`` package layered::

    $ rpm-ostree status
    State: idle
    AutomaticUpdates: stage; rpm-ostreed-automatic.timer: no runs since boot
    Deployments:

    ● ostree-image-signed:docker://ghcr.io/ublue-os/aurora-dx:stable
                       Digest: sha256:87643ac3caee7c17334a08dea4203266e81ab9c8de7a55ea5aed59a77ec28588
                      Version: 41.20250330.1 (2025-03-30T06:02:52Z)
              LayeredPackages: emacs

      ostree-image-signed:docker://ghcr.io/ublue-os/aurora-dx:stable
                       Digest: sha256:0b48d807d1e773328de4d82f344c2b53415c96249fac4eb3c9167522aede911d
                      Version: 41.20250316.1 (2025-03-16T06:06:05Z)
              LayeredPackages: emacs

  I have not un-layered the package to test it, but my assumption is that this enables the version of Emacs I compile to work by ensuring all the runtime dependencies are present.
