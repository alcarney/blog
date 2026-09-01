:title: Building Emacs into a systemd-sysext
:date: 2026-09-01
:tags: blog, emacs, systemd
:identifier: 20250409T205418
:signature: 5=5=1

Building Emacs into a systemd-sysext
====================================

.. highlight:: none

.. container:: post-teaser

   Now that Emacs v31 is out I'm itching to play with all the new features.
   However, *I think* I need to wait for Fedora 45 to land before it becomes available through the repos.
   I *could* build it from source, but being on an image based OS you can't "just" install it when you are done.

   However, when Emacs v30 released, I did manage to figure out how to :denote:link:`install Emacs when packaged as a systemd-sysext <20250409T205419>`.
   So I guess this time I'm figuring out how to build a systemd-sysext for myself!

systemd-sysexts *can* be as simple as:

- a folder of files in the right place (``/var/lib/extensions``)

- in the right shape (`FHS <https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard>`__ under ``/usr``)

- with a "release" file signalling compatibity::

    /var/lib/extensions $ cat ./<name>/usr/lib/extension-release.d/extension-release.<name>
    ID=<distro>            # e.g. 'fedora'
    VERSION_ID=<release>   # e.g. '44'

If the above holds and the declared ``ID`` and ``VERSION_ID`` are compatible with what's in your ``/etc/os-release`` file then systemd will happily use the folder structure as a sysext.

Though of course, things rarely stick to the simplest case.

The plan
--------

To make a systemd-sysext for Emacs you would need to do the following:

#. Prepare an environment with the necessary tools to build Emacs.
#. Build and install Emacs into a ``/usr`` hierarchy.
#. Figure out which files are part of Emacs itself, or its runtime dependencies.
#. Extract those files into a separate, isolated, folder structure
#. Write the "release" file indicating which underlying host distro the sysext is compatible with.
#. (Bonus points) pack the whole folder structure into a "real" format like an erofs file system.

If only there was already a tool that could automate most of this process for us!

Building sysexts with mkosi
---------------------------

`mkosi <https://github.com/systemd/mkosi/>`_, among many other things can build systemd-sysexts.

Before jumping straight into building Emacs from source, let's adapt `this guide <https://mkosi.systemd.io/sysext.html>`_, to derive a sysext from the existing Emacs Fedora package.

#. Create a folder to act as the workspace e.g. ``/tmp/sysext-build``

#. Create a top-level config file to store common settings:

   .. code-block:: ini

      [Output]
      OutputDirectory=mkosi.output

      [Build]
      CacheDirectory=mkosi.cache

#. Create a config under ``mkosi.images/base/`` to define the base image:

   .. code-block:: ini

      [Output]
      Format=directory

      [Content]
      CleanPackageMetadata=no
      Packages=systemd
               udev

   Apparently, putting the base image in a plain ``directory`` means the build can be executed without root.

#. Create a config under ``mkosi.images/emacs`` that produces the sysext:

   .. code-block:: ini

      [Config]
      Dependencies=base

      [Output]
      Format=sysext
      Overlay=yes

      [Content]
      BaseTrees=%O/base
      Packages=emacs

   This takes the ``base`` image as a dependency, so that we have a functioning system on which we can run our build.
   In this example, the build is trivial - just install the packages listed in ``Packages``.

#. Run ``mkosi -f`` from the ``/tmp/sysext-build`` directory:

   .. code-block:: console

      /tmp/sysext-build $ mkosi -f
      ‣ Validating certificates and keys
      ‣ Syncing package manager metadata
      Updating and loading repositories:
      Repositories loaded.
      Metadata cache created.
      ‣ Building base image
      ‣  Installing Fedora Linux
      #   <dnf output omitted>
      ‣  Generating system users
      ‣  Generating volatile files
      ‣  Applying presets…
      Created symlink '/buildroot/etc/systemd/system/multi-user.target.wants/remote-integritysetup.target' → '/usr/lib/systemd/system/remote-integritysetup.target'.
      ‣  Generating hardware database
      ‣  /tmp/sysext-build/mkosi.output/base size is 136.0M.
      ‣ Building emacs image
      ‣  Mounting base trees…
      ‣   Installing extra packages for Fedora Linux
      #    <dnf output omitted>
      ‣ Removing duplicate path /usr/lib/sysimage/rpm/rpmdb.sqlite-wal from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/rpm/rpmdb.sqlite-shm from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/rpm/.rpm.lock from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/rpm/rpmdb.sqlite from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/transaction_history.sqlite from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/transaction_history.sqlite-wal from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/transaction_history.sqlite-shm from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/packages.toml from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/nevras.toml from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/groups.toml from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/environments.toml from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/system.toml from overlay
      ‣ Removing duplicate path /usr/lib/sysimage/libdnf5/modules.toml from overlay
      ‣  Removing empty directories…
      ‣  Building sysext extension image
      Pre-populating erofs filesystem of partition 10-root.conf to calculate minimal partition size
      Preparing to populate erofs filesystem.
      Failed to open source file '/buildroot/opt', skipping: No such file or directory
      Ready to populate erofs filesystem.
      mkfs.erofs binary not available.
      ‣ "systemd-repart --root=/buildroot --json=pretty --dry-run=no --no-pager --offline=yes --seed 1f4fb277-7943-41db-b853-c33514998b71 --empty=create --size=auto --definitions /work/tmp/tmpxw95dzaf/resources/repart/definitions/sysext-unsigned.repart.d /work/home/alex/.cache/mkosi/mkosi-workspace-7czb6oto/staging/emacs.raw" returned non-zero exit code 1.

Ah.

Installing ``erofs-utils``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Typically, sysexts appear to use the ``erofs`` filesystem (no I don't know what it is! 😅).
So to make one you need the necessary utilities installed.

Luckily, there is already a sysext from https://fedora-sysexts.github.io/fedora/ that provides them for me, it's just a case of installing it.

.. tip::

   If you've never used a systemd-sysext, you also need to setup the ``/var/lib/extensions{.d}`` folders.

   .. code-block:: console

      $ sudo install -d -m 0755 -o 0 -g 0 /var/lib/extensions /var/lib/extensions.d
      $ sudo restorecon -RFv /var/lib/extensions /var/lib/extensions.d

#. Create a ``/etc/sysupdate.erofs-utils.d/`` folder

   .. code-block:: console

      $ sudo install -d -m 0755 -o 0 -g 0 /etc/sysupdate.erofs-utils.d
      $ sudo restorecon -RFv /etc/sysupdate.erofs-utils.d

#. Create a ``/etc/sysupdate.erofs-utils.d/erofs-utils.transfer`` file

   .. code-block:: ini

      [Transfer]
      Verify=false

      [Source]
      Type=url-file
      Path=https://extensions.fcos.fr/extensions/erofs-utils/
      MatchPattern=erofs-utils-@v-%w-%a.raw

      [Target]
      InstancesMax=2
      Type=regular-file
      Path=/var/lib/extensions.d/
      MatchPattern=erofs-utils-@v-%w-%a.raw
      CurrentSymlink=/var/lib/extensions/erofs-utils.raw

This allows for the use of the ``systemd-sysupdate`` command to automate the installation and update of the sysext.

.. code-block:: console

   $ sudo /usr/lib/systemd/systemd-sysupdate update --component erofs-utils
   Discovering available instances…
   ⤵ Acquiring manifest file https://extensions.fcos.fr/extensions/erofs-utils/SHA256SUMS…
   Pulling 'https://extensions.fcos.fr/extensions/erofs-utils/SHA256SUMS'.
   Downloading 1.6K for https://extensions.fcos.fr/extensions/erofs-utils/SHA256SUMS.
   Got 81% of https://extensions.fcos.fr/extensions/erofs-utils/SHA256SUMS.
   Acquired 1.6K.
   Download of https://extensions.fcos.fr/extensions/erofs-utils/SHA256SUMS complete.
   Operation completed successfully.
   Exiting.
   Determining installed update sets…
   Determining available update sets…
   Selected update '1.9.2-2.fc44' for install.
   Making room for 1 updates…
   Found nothing to remove.
   ⤵ Acquiring https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw → /var/lib/extensions.d/erofs-utils-1.9.2-2.fc44-44-x86-64.raw...
   Pulling 'https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw', saving as '/var/lib/extensions.d/.#sysupdateerofs-utils-1.9.2-2.fc44-44-x86-64.rawfaea62476ebc8520'.
   Downloading 1M for https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw.
   Got 1% of https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw.
   Acquired 1M.
   Download of https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw complete.
   Operation completed successfully.
   Exiting.
   Successfully acquired 'https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw'.
   Successfully installed 'https://extensions.fcos.fr/extensions/erofs-utils/erofs-utils-1.9.2-2.fc44-44-x86-64.raw' (url-file) as '/var/lib/extensions.d/erofs-utils-1.9.2-2.fc44-44-x86-64.raw' (regular-file).
   Updated symlink '/var/lib/extensions/erofs-utils.raw' → '../extensions.d/erofs-utils-1.9.2-2.fc44-44-x86-64.raw'.
   ✨ Successfully installed update '1.9.2-2.fc44'.

To activate the sysext run the unmerge (if necessary) and merge commands

.. code-block:: console

   $ sudo systemd-sysext unmerge
   Unmerged '/usr'

   $ sudo systemd-sysext merge
   Using extensions 'erofs-utils.raw'.
   Merged extensions into '/usr'.

.. _5-5-1-build-the-sysext:

Building the sysext
^^^^^^^^^^^^^^^^^^^

With the necessary tools installed, it should now be possible to build the sysext.

.. code-block:: console

   /tmp/sysext-build $ mkosi -f
   # <output skipped>
   ‣  Building sysext extension image
   Pre-populating erofs filesystem of partition 10-root.conf to calculate minimal partition size
   Preparing to populate erofs filesystem.
   Failed to open source file '/buildroot/opt', skipping: No such file or directory
   Ready to populate erofs filesystem.
   mkfs.erofs 1.9.2
   Build completed.
   ------
   Filesystem UUID: a738a716-f4c1-4914-91f7-b053b6103c19
   Filesystem total blocks: 204508 (of 4096-byte blocks)
   Filesystem total inodes: 18645
   Filesystem total metadata blocks: 7608
   Filesystem total deduplicated bytes (of source files): 0
   /var/tmp/.#repartbe3ba45d64095527 successfully formatted as erofs (uuid a738a716-f4c1-4914-91f7-b053b6103c19, no label)
   Minimal partition size of erofs filesystem of partition 10-root.conf is 798.8M
   Automatically determined minimal disk image size as 799.8M.
   Sized '/work/home/alex/.cache/mkosi/mkosi-workspace-4beygy4j/staging/emacs.raw' to 799.8M.
   Applying changes to /work/home/alex/.cache/mkosi/mkosi-workspace-4beygy4j/staging/emacs.raw.
   Copying in '/var/tmp/.#repartbe3ba45d64095527' (798.8M) on block level into future partition 0.
   Copying in of '/var/tmp/.#repartbe3ba45d64095527' on block level completed.
   Syncing future partition 0 contents to disk.
   Block level copying and synchronization of partition 0 complete in 294.448ms (2.6G/s).
   Adding new partition 0 to partition table.
   Writing new partition table.
   All done.
   ‣  /tmp/sysext-build/mkosi.output/emacs.raw size is 799.9M, consumes 798.9M.

Thanks to the cache dirs setup in the top-level config file, the second attempt builds *much* faster!

.. note::

   This config also results in a "main image" being built...

   .. code-block:: console

      ‣ Building main image
      ‣  Installing Fedora Linux
      #   <dnf output omitted>
      ‣  Generating system users
      ‣  Generating volatile files
      ‣  Applying presets…
      ‣  Generating hardware database
      No hwdb files found, skipping.
      ‣  Generating disk image
      MountPoint= is not specified for any eligible partitions, not generating /etc/fstab
      EncryptedVolume= is not specified for any eligible partitions, not generating /etc/crypttab
      Pre-populating btrfs filesystem of partition 10-root.conf to calculate minimal partition size
      Preparing to populate btrfs filesystem.
      Ready to populate btrfs filesystem.
      btrfs-progs v7.1
      See https://btrfs.readthedocs.io for more information.

      NOTE: default settings have changed in version 6.19 (supported since linux 6.1):
            - enable block-group-tree (-O bgt)

      Rootdir from:       /var/tmp/.#repart2d08eeaaa49d72c5
        Compress:         no
        Shrink:           yes
      Label:              root-x86-64
      UUID:               a738a716-f4c1-4914-91f7-b053b6103c19
      Node size:          16384
      Sector size:        4096        (CPU page size: 4096)
      Filesystem size:    101.00MiB
      Block group profiles:
        Data:             single            8.00MiB
        Metadata:         DUP              32.00MiB
        System:           DUP               8.00MiB
      SSD detected:       no
      Zoned device:       no
      Features:           extref, skinny-metadata, no-holes, free-space-tree, block-group-tree
      Checksum:           crc32c
      Number of devices:  1
      Devices:
         ID        SIZE  PATH
          1   101.00MiB  /var/tmp/.#repart8c5b8b5a4db184b4

      /var/tmp/.#repart8c5b8b5a4db184b4 successfully formatted as btrfs (label "root-x86-64", uuid a738a716-f4c1-4914-91f7-b053b6103c19)
      Minimal partition size of btrfs filesystem of partition 10-root.conf is 101M
      Automatically determined minimal disk image size as 102M.
      Sized '/work/home/alex/.cache/mkosi/mkosi-workspace-gqb4a69k/staging/image.raw' to 102M.
      Applying changes to /work/home/alex/.cache/mkosi/mkosi-workspace-gqb4a69k/staging/image.raw.
      Copying in '/var/tmp/.#repart8c5b8b5a4db184b4' (101M) on block level into future partition 0.
      Copying in of '/var/tmp/.#repart8c5b8b5a4db184b4' on block level completed.
      Syncing future partition 0 contents to disk.
      Block level copying and synchronization of partition 0 complete in 7.890ms.
      Adding new partition 0 to partition table.
      Writing new partition table.
      All done.
      ‣  Formatting ESP/XBOOTLDR partitions
      Automatically determined minimal disk image size as 102M, current block device/image size is 102M.
      File '/work/home/alex/.cache/mkosi/mkosi-workspace-gqb4a69k/staging/image.raw' already is of requested size or larger, not growing. (102M >= 102M)
      No changes.
      ‣  /tmp/sysext-build/mkosi.output/image.raw size is 102.0M, consumes 6.5M.

   I don't really understand why, or what's in it.
   But it's the ``mkosi.output/emacs.raw`` file we are interested in.

The final step is to "install it"

.. code-block:: console

   $ sudo cp /tmp/sysext-build/mkosi.output/emacs.raw /var/lib/extensions.d/
   $ sudo ln -s /var/lib/extensions.d/emacs.raw /var/lib/extensions/emacs.raw
   $ sudo systemd-sysext unmerge
   $ sudo systemd-sysext merge
   $ emacs-30.2-gtk+x11 --version
   GNU Emacs 30.2
   Copyright (C) 2025 Free Software Foundation, Inc.
   GNU Emacs comes with ABSOLUTELY NO WARRANTY.
   You may redistribute copies of GNU Emacs
   under the terms of the GNU General Public License.
   For more information about these matters, see the file named COPYING.

The slightly odd executable name is a quirk of how Fedora packages Emacs.
The ``emacs`` "executable" is a symlink to ``/etc/alternatives/emacs`` which *I think*, in turn should be a symlink to ``emacs-30.2-gtk+x11``.

This setup doesn't reproduce that, but I'm not going to fix that since my real goal with this is to...

Build Emacs from Source
-----------------------

.. seealso::

   Be sure to refer to the `upstream documentation <https://github.com/systemd/mkosi/blob/1da3299aecc56a1ba590a7fb7ae868275bb46d93/mkosi/resources/man/mkosi.1.md>`__ for a much more detailed explanation of the ``mkosi`` build process and the various config options and extension points.

Now we have a end-to-end workflow with ``mkosi`` setup, we "just" have to tweak the above config so that it builds Emacs v31 from source, rather than repackaging the Fedora package.

After some wailing and gnashing of teeth, I eventually arrived at the following.

**Top Level**

.. code-block:: ini
   :project: emacs-sysext
   :filename: mkosi.conf

   [Output]
   OutputDirectory=mkosi.output

   [Build]
   CacheDirectory=mkosi.cache
   BuildSources=/var/home/alex/Projects/gnu/emacs/master:emacs
   BuildSourcesEphemeral=true

Interestingly, ``BuildSources`` can only be specified at the top level - that means it's available to the ``base`` image build even though it's only needed for the ``emacs`` image.
I *think* ``[Match]`` rules can be used to change this, but to keep things simple I didn't look into it.

The ``<src>:<dest>`` syntax means when the build executes ``<src>`` on the host is mapped to ``/work/src/<dest>`` in the image.
Before running the build, I made sure to have the ``emacs-31.1`` tag checked out in my copy of the Emacs git repo.

``BuildSourcesEphemeral`` is cool, when enabled the build is done in an overlay so all the gumph generated by the build (e.g. ``*.o`` files ) are automatically discarded by throwing the overlay away at the end.


**Base Image**

.. code-block:: ini
   :project: emacs-sysext
   :filename: mkosi.images/base/mkosi.conf

   [Output]
   Format=directory

   [Content]
   CleanPackageMetadata=no
   Packages=# Build tools
            autoconf
            awk
            make
            gcc
            git
            pkgconf-pkg-config
            rpm
            tar
            texinfo
            # Emacs build dependencies
            gnutls-devel
            gtk3-devel
            libjpeg-turbo-devel
            libpng-devel
            librsvg2-devel
            libselinux-devel
            libtiff-devel
            libwebp-devel
            libxml2-devel
            ncurses-devel
            sqlite-devel
            # Needed for mkosi?
            systemd
            udev

The base image config needed to be updated to include all the build tools and (most) build dependencies.
The hardest part of this was figuring out enough of the list of build tools to bootstrap the ``./configure`` script.

**Emacs Sysext**

.. code-block:: ini
   :project: emacs-sysext
   :filename: mkosi.images/emacs/mkosi.conf

   [Output]
   Format=sysext
   Overlay=yes

   [Content]
   BaseTrees=%O/base
   Packages=libgccjit,libotf,libtree-sitter
   BuildPackages=libgccjit-devel,libotf-devel,libtree-sitter-devel

Before discovering ``mkosi`` could build systemd-sysexts I was playing around with doing the build inside a `distrobox <https://distrobox.it/>`__.
During that process, I discovered that my base system already provides the majority of Emacs' runtime dependencies, so I was able to get away with listing just the couple that were missing.

As you might expect ``Packages`` are included in the final image, while ``BuildPackages`` are discarded after the build step.

.. code-block:: bash
   :project: emacs-sysext
   :filename: mkosi.images/emacs/mkosi.build.chroot

   #!/bin/bash
   set -euo pipefail
   pushd emacs

   ./autogen.sh
   ./configure --prefix=/usr \
               --disable-gc-mark-trace \
               --with-pgtk \
               --with-native-compilation=aot \
               --without-x
    make -j $(nproc)
    make install

If you include an executable script named ``mkosi.build`` that gets called by ``mkosi`` during the build stage to... well build your software.
By default, this script is executed **on the host**, append ``.chroot`` to the name if you want it to be executed from within the image you are building.

.. note::

   I don't really know which options I should/should not be passing to ``./configure`` so if you have any suggestions please let me know! 😀

With the config updated, repeating the steps in :ref:`5-5-1-build-the-sysext` was all that was needed to produce a sysext containing Emacs v31.1!

.. code-block:: console

   $ emacs --version
   GNU Emacs 31.1
   Development version a360712c9d27 on HEAD branch; build date 2026-09-01.
   Copyright (C) 2026 Free Software Foundation, Inc.
   GNU Emacs comes with ABSOLUTELY NO WARRANTY.
   You may redistribute copies of GNU Emacs
   under the terms of the GNU General Public License.
   For more information about these matters, see the file named COPYING.

It's Looking Promising!
-----------------------

Although I am writing this post from within my freshly built Emacs, it's only been an hour a two, so too early to declare this a flawless victory but it's certainly looking good.
Also, thanks to the sysext approach, if the worst happens and I need to roll back, I still have the previous versions lying around

.. code-block:: console

   $ ls -lh /var/lib/extensions.d/
   total 1.1G
   -rw-r--r--. 1 root root 404M Aug 27 08:27 emacs-1-30.2-28.fc44-44-x86-64.raw
   -rw-r--r--. 1 root root 304M Mar 12 10:09 emacs-1-30.2-6.fc43-43-x86-64.raw
   -rw-r--r--. 1 root root 338M Sep  1 14:53 emacs.raw
   -rw-r--r--. 1 root root 1.1M Aug 26 02:15 erofs-utils-1.9.2-2.fc44-44-x86-64.raw

So while it's not "one-click", by tweaking a symlink and running a couple of commands I can easily roll back to the previous version.

Or... now that I've figured how to do this... roll forward to a build containing the new `Canvas <https://www.monadicsheep.org/blog/an-introduction-to-canvas-in-emacs.html>`__! 🤔
