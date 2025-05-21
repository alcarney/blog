:title: Installing Emacs with systemd-sysext
:date: 2025-05-02
:tags: blog, emacs, systemd
:identifier: 20250409T205418
:signature: 5=5=1

Intstalling Emacs with systemd-sysext
=====================================

.. highlight:: none

.. container:: post-teaser

   One issue with building :denote:link:`Emacs from source <20250409T205418>`, or more specifically my hack to ensure that the required system libraries are available on Aurora, is that in some situations the system version of Emacs "wins".

   For example, I wanted to experiment with running the Emacs daemon through systemd::

      $ systemctl --user start emacs

   Which failed to load my config correctly.
   It was only after a closer look did I realise that despite specifying the ``--user`` flag, systemd was defaulting to the ``emacs.service`` file provided by the system emacs package in ``/usr/...`` and was therefore running Emacs v29 and not my v30 build.

   But then I stumbled across systemd-sysext

Enter systemd-sysext
--------------------

I can't really tell you what a sysext is... I just know that they are yet another potential way to install software on an image based OS.
To quote the `extensions.fcos.fr <https://extensions.fcos.fr/>`__ website

.. pull-quote::

   systemd system extensions (sysexts) are filesystem images that bundle content (binaries, libraries and configuration files) that can be overlayed on demand on image based systems. The content of the sysexts are “merged” with the base content of the OS using an overlayfs mount.

   If you want to know more about sysexts, you can watch the `Waiter, an OS please, with some sysext sprinkled on top (video) <https://cfp.all-systems-go.io/all-systems-go-2024/talk/HJLF3C/>`__ talk at All systems go! Berlin 2024.

I saw that there was an Emacs layer(?), so thought I may as well give it a go!

Initial Setup
^^^^^^^^^^^^^

It looks like a "proper" frontend to these things is still `under development <https://github.com/bootc-dev/bootc/issues/7>`__ so for now we need to do the setup ourselves.
Thankfully the page for the `emacs sysext <https://travier.github.io/fedora-sysexts/>`__ provides the steps for us

**Create folders to manage sysexts**

This step is only necessary when you set up your very first sysext ::

   $ sudo install -d -m 0755 -o 0 -g 0 /var/lib/extensions /var/lib/extensions.d
   $ sudo restorecon -RFv /var/lib/extensions /var/lib/extensions.d

**Tell systemd about the sysext**

First we create a folder under ``/etc`` where we can place a ``*.conf`` file

::

   $ sudo install -d -m 0755 -o 0 -g 0 /etc/sysupdate.emacs.d
   $ sudo restorecon -RFv /etc/sysupdate.emacs.d

I'm not sure why you would create a folder here per sysext, but I'm sure there must be a good reason to.
In this folder, we place an ``emacs.conf`` file with the following contents

.. code-block:: systemd

   [Transfer]
   Verify=false

   [Source]
   Type=url-file
   Path=https://extensions.fcos.fr/extensions/emacs/
   MatchPattern=emacs-@v-%w-%a.raw

   [Target]
   InstancesMax=2
   Type=regular-file
   Path=/var/lib/extensions.d/
   MatchPattern=emacs-@v-%w-%a.raw
   CurrentSymlink=/var/lib/extensions/emacs.raw

Again, I don't really know the details, but the ``[Source]`` block appears to be telling systemd where to fetch the emacs sysext from and the ``[Target]`` block seems to be telling it where to put it on disk.

Install the sysext
^^^^^^^^^^^^^^^^^^

We've now given systemd enough information to fetch the sysext::

   $ sudo /usr/lib/systemd/systemd-sysupdate update --component emacs
   Discovering installed instances…
   Discovering available instances…
   ⤵️ Acquiring manifest file https://extensions.fcos.fr/extensions/emacs/SHA256SUMS…
   Pulling 'https://extensions.fcos.fr/extensions/emacs/SHA256SUMS'.
   Downloading 406B for https://extensions.fcos.fr/extensions/emacs/SHA256SUMS.
   Acquired 406B.
   Download of https://extensions.fcos.fr/extensions/emacs/SHA256SUMS complete.
   Operation completed successfully.
   Exiting.
   Determining installed update sets…
   Determining available update sets…
   Selected update '1-29.4-44.fc41' for install.
   Making room for 1 updates…
   Removed no instances.
   ⤵️ Acquiring https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw → /var/lib/extensions.d/emacs-1-29.4-44.fc41-41-x86-64.raw...
   Pulling 'https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw', saving as '/var/lib/extensions.d/.#sysupdateemacs-1-29.4-44.fc41-41-x86-64.raw6b5d6dfbd735d210'.
   Downloading 286.2M for https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw.
   Got 1% of https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw.
   ...
   Got 98% of https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw. 268ms left at 17.4M/s.
   Acquired 286.2M.
   Download of https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw complete.
   Operation completed successfully.
   Exiting.
   Successfully acquired 'https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw'.
   Successfully installed 'https://extensions.fcos.fr/extensions/emacs/emacs-1-29.4-44.fc41-41-x86-64.raw' (url-file) as '/var/lib/extensions.d/emacs-1-29.4-44.fc41-41-x86-64.raw' (regular-file).
   Updated symlink '/var/lib/extensions/emacs.raw' → '../extensions.d/emacs-1-29.4-44.fc41-41-x86-64.raw'.
   ✨ Successfully installed update '1-29.4-44.fc41'.

However, while we can see the sysext on disk... ::

   $  ls /var/lib/extensions -l
   lrwxrwxrwx. 1 root root 50 Apr 27 19:44 emacs.raw -> ../extensions.d/emacs-1-29.4-44.fc41-41-x86-64.raw

Emacs itself is still not available ::

   $ emacs
   bash: emacs: command not found

Enabling the sysext
^^^^^^^^^^^^^^^^^^^

The sysext still needs to be enabled - or "merged" ::

   $ sudo systemctl restart systemd-sysext.service

Which, in theory, would finally make Emacs available to my system however running ``systemd-sysext status`` showed no extensions ::

 $ systemd-sysext status
 HIERARCHY EXTENSIONS SINCE
 /opt      none       -
 /usr      none       -

And there were errors in the ``systemd-sysext.service`` ::

    $ systemctl status systemd-sysext.service
    ● systemd-sysext.service - Merge System Extension Images into /usr/ and /opt/
         Loaded: loaded (/usr/lib/systemd/system/systemd-sysext.service; enabled; preset: enabled)
        Drop-In: /usr/lib/systemd/system/service.d
                 └─10-timeout-abort.conf, 50-keep-warm.conf
         Active: active (exited) since Sun 2025-04-27 19:56:39 BST; 1min 0s ago
     Invocation: 3d34eb06a325454b954ff1697193ba9c
           Docs: man:systemd-sysext.service(8)
        Process: 9596 ExecStart=systemd-sysext refresh (code=exited, status=0/SUCCESS)
       Main PID: 9596 (code=exited, status=0/SUCCESS)
       Mem peak: 4.1M
            CPU: 34ms

    Apr 27 19:56:38 aurora systemd[1]: Starting systemd-sysext.service - Merge System Extension Images into /usr/ and /opt/...
    Apr 27 19:56:39 aurora (sd-merge)[9612]: No suitable extensions found (1 ignored due to incompatible image(s)).
    Apr 27 19:56:39 aurora systemd[1]: Finished systemd-sysext.service - Merge System Extension Images into /usr/ and /opt/.

Digging Deeper
--------------

Without much to go on I started googling around for some more information.

What's in a sysext?
^^^^^^^^^^^^^^^^^^^

Eventually I found myself on the `manpage <https://www.freedesktop.org/software/systemd/man/latest/systemd-sysext.html>`__ for ``systemd-sysext``, trying to get a feel for what this ``*.raw`` file I downloaded actually looked like.

.. pull-quote::

   System extension images may be provided in the following formats:

   1. Plain directories or btrfs subvolumes containing the OS tree

   2. Disk images with a GPT disk label, following the Discoverable Partitions Specification

   3. Disk images lacking a partition table, with a naked Linux file system (e.g. erofs, squashfs or ext4)

Oh, so some kind of file system then?

Digging around in the GitHub Action workflows of the ``fedora-sysexts`` project, I `found <https://github.com/travier/fedora-sysexts/blob/c1c589e5214793295c2d0be36c03b5082eed2c67/sysext.just#L634>`__ where the ``*.raw`` files were actually produced::

   ${SUDO} mkfs.erofs -z{{compression}} {{name}}-${version}-${version_id}-${arch}.raw rootfs > /dev/null

Seeing this I wondered if I could just mount this file and take a look around::

   $ sudo mkdir /run/media/img
   $ sudo mount /var/lib/extensions.d/emacs-1-29.4-44.fc41-41-x86-64.raw /run/media/img
   $ tree -L 2 /run/media/img
   /run/media/img/
   └── usr
       ├── bin
       ├── etc
       ├── include
       ├── lib
       ├── lib64
       ├── libexec
       └── share

Sure enough, it was just a folder hierarchy that contained an installation of Emacs.
While it was nice to get some more details on what I was dealing with, it didn't actually help me get any closer to figuring out what was wrong - so I kept reading.

Compatibility Checks
^^^^^^^^^^^^^^^^^^^^

There is a simple check performed when merging a sysext in an attempt to ensure it's compatible with the base system.

.. pull-quote::

   A system extension image must carry a ``/usr/lib/extension-release.d/extension-release.NAME`` file, which must match its image name, that is compared with the host os-release file: the contained ``ID=`` fields have to match unless ``"_any"`` is set for the extension.

And here was my issue::

  $ grep '^ID=' /etc/os-release
  ID=aurora

  $ grep '^ID=' /run/media/img/usr/lib/extension-release.d/extension-release.emacs
  ID="fedora"

As far as systemd was concerned I am running an incompatible OS, so it refuses to enable the sysext.

Hacking it in
-------------

Just to check that my assumption was correct, I edited my ``/etc/os-release`` file so that the ``ID`` field was set to ``fedora`` and tried restarting the ``systemd-sysext.service`` again::

    Apr 27 23:26:46 aurora systemd[1]: Starting systemd-sysext.service - Merge System Extension Images into /usr/ and /opt/...
    Apr 27 23:26:46 aurora (sd-merge)[15118]: Using extensions 'emacs'.
    Apr 27 23:26:46 aurora (sd-merge)[15118]: Merged extensions into '/usr'.
    Apr 27 23:26:46 aurora systemd[1]: Finished systemd-sysext.service - Merge System Extension Images into /usr/ and /opt/.

Which looked promising!
I could even see the extension now using the ``systemd-sysext`` command::

   $ systemd-sysext list
   NAME  TYPE PATH                          TIME
   emacs raw  /var/lib/extensions/emacs.raw Sat 2025-04-26 14:30:33 BST

And the ``emacs`` command was available! ::

   $ emacs --version
   GNU Emacs 29.4
   Copyright (C) 2024 Free Software Foundation, Inc.
   GNU Emacs comes with ABSOLUTELY NO WARRANTY.
   You may redistribute copies of GNU Emacs
   under the terms of the GNU General Public License.
   For more information about these matters, see the file named COPYING.

The only issue now is that it's still not Emacs v30!
While I saw both Emacs v29 and v30 builds were available as sysexts I didn't think to check which fedora versions they were built for! 🤦‍♂️ ::

   emacs-1-29.4-44.fc41-41-aarch64.raw
   emacs-1-29.4-44.fc41-41-x86-64.raw
   emacs-1-30.1-11.fc42-42-aarch64.raw
   emacs-1-30.1-11.fc42-42-x86-64.raw

It turns out Emacs v30 is only available on Fedora 42 - regardless of the installation method used! 😅
