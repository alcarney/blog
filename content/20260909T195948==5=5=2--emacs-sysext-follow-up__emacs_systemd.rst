:title: Emacs sysext Follow-Up
:date: 2026-09-09
:tags: emacs, systemd
:identifier: 20260909T195948
:signature: 5=5=2

Emacs sysext Follow-Up
======================

It was not a flawless victory.

Reboot into Black Screen!
-------------------------

Luckily I was able to :kbd:`Ctrl+Alt+F1` and look at ``jounrnalctl``

.. code-block::

   $ journalctl -b
   Sep 09 11:41:42 aurora (sd-merge)[1626]: Using extensions 'emacs.raw', 'erofs-utils.raw'.
   Sep 09 11:41:42 aurora kernel: erofs (device loop1p1): mounted with root inode @ nid 41.
   Sep 09 11:41:42 aurora (sd-merge)[1626]: Merged extensions into '/usr'.
   Sep 09 11:41:42 aurora systemd[1]: Finished systemd-sysext.service - Merge System Extension Images into /usr/ and /opt/.
   Sep 09 11:41:42 aurora audit[1]: SERVICE_START pid=1 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:init_t:s0 m>
   Sep 09 11:41:42 aurora systemd[1]: Starting systemd-tmpfiles-setup.service - Create System Files and Directories...
   Sep 09 11:41:42 aurora audit[1631]: AVC avc:  denied  { search } for  pid=1631 comm="(sd-worker)" name="systemd" dev="overla>
   Sep 09 11:41:42 aurora audit[1631]: SYSCALL arch=c000003e syscall=59 success=no exit=-13 a0=5603e65c0778 a1=7ffc9ceb5f20 a2=>
   Sep 09 11:41:42 aurora audit: PROCTITLE proctitle="(sd-worker)"
   Sep 09 11:41:42 aurora audit[1632]: AVC avc:  denied  { search } for  pid=1632 comm="(sd-worker)" name="systemd" dev="overla>
   Sep 09 11:41:42 aurora audit[1632]: SYSCALL arch=c000003e syscall=59 success=no exit=-13 a0=5603e65c0778 a1=7ffc9ceb5f20 a2=>
   Sep 09 11:41:42 aurora audit: PROCTITLE proctitle="(sd-worker)"
   Sep 09 11:41:42 aurora (sd-worker)[1631]: Failed to start worker process: Permission denied
   Sep 09 11:41:42 aurora (sd-worker)[1632]: Failed to start worker process: Permission denied
   Sep 09 11:41:42 aurora systemd-userdbd[1026]: Worker 1631 died with a failure exit status 1, ignoring.
   Sep 09 11:41:42 aurora audit[1633]: AVC avc:  denied  { search } for  pid=1633 comm="(sd-worker)" name="systemd" dev="overla>
   Sep 09 11:41:42 aurora audit[1633]: SYSCALL arch=c000003e syscall=59 success=no exit=-13 a0=5603e65c0778 a1=7ffc9ceb5f20 a2=>
   Sep 09 11:41:42 aurora audit: PROCTITLE proctitle="(sd-worker)"
   Sep 09 11:41:42 aurora audit[1634]: AVC avc:  denied  { search } for  pid=1634 comm="(sd-worker)" name="systemd" dev="overla>
   Sep 09 11:41:42 aurora audit[1634]: SYSCALL arch=c000003e syscall=59 success=no exit=-13 a0=5603e65c0778 a1=7ffc9ceb5f20 a2=>
   Sep 09 11:41:42 aurora audit: PROCTITLE proctitle="(sd-worker)"
   Sep 09 11:41:42 aurora systemd-userdbd[1026]: Worker 1632 died with a failure exit status 1, ignoring.
   Sep 09 11:41:42 aurora (sd-worker)[1633]: Failed to start worker process: Permission denied
   Sep 09 11:41:42 aurora (sd-worker)[1634]: Failed to start worker process: Permission denied

And it continued like this... ad-infinitum.

On a hunch I removed my symlink to ``/var/lib/extensions.d/emacs.raw`` and rebooted.

Surprise, surprise, it came back up.

Interestingly, once I logged in I could re-add the symlink, unmerge, merge and systemd would accept the sysext.
(Though Emacs itself was busted, more on that later).

So what gives?

I've been bitten by SE Linux issues enough now to at least choose that as my first culprit to investigate.

Turns out ``ls -Z`` lists the labels on a file! So let's see...

.. code-block::

   $ ls -lZ /var/lib.extensions.d/
   -rw-r--r--. 1 root root unconfined_u:object_r:var_lib_t:s0    422731776 Aug 27 08:27 emacs-1-30.2-28.fc44-44-x86-64.raw
   -rw-r--r--. 1 root root unconfined_u:object_r:var_lib_t:s0    318697472 Mar 12 10:09 emacs-1-30.2-6.fc43-43-x86-64.raw
   -rw-r--r--. 1 alex alex unconfined_u:object_r:cache_home_t:s0 354377728 Sep  9 11:01 emacs.raw
   -rw-r--r--. 1 root root unconfined_u:object_r:var_lib_t:s0      1052672 Aug 26 02:15 erofs-utils-1.9.2-2.fc44-44-x86-64.raw

I can see at least two issues there. ``root`` doesn't own the file and the file is tagged ``cache_home_t``, rather than ``var_lib_t`` like the others...

Fixing the ownership is easy enough..

.. code-block::

   /var/lib/extensions.d $ sudo chown root:root emacs.raw

Actually... let's see if that's sufficient... *reboots* ... *sigh*, it was not.

Ok, then let's try to fix the file's labels

.. code-block::

   /var/lib/extensions.d $ sudo restorecon -RFv emacs.raw
   Relabeled /var/lib/extensions.d/emacs.raw from unconfined_u:object_r:cache_home_t:s0 to system_u:object_r:var_lib_t:s0

I don't understand SE Linux in the slightest, but I've run this command enough to **think** I know what it does.
I believe it applies the default labels for the file's current location, which judging from the output above seems to correlate.

It has also changed ``unconfined_u`` to ``system_u``, but let's hope that's not important!

*reboots*

Still broken.

Let's think on this for a minute. Why is this an issue in the first place... *especially* when Emacs shouldn't be trying to run this early in the boot process!
It's only configured to launch as a user-level service when I log in, unless....

``emacs.raw`` is a filesystem... the .raw file itself is going to contain a bunch of files each with their own label!

.. code-block::

   $ ls -lZ $(command -v emacs)
   lrwxrwxrwx. 1 root root unconfined_u:object_r:cache_home_t:s0 10 Sep  9 11:01 /usr/bin/emacs -> emacs-31.1

Yep. Emacs itself has the same label... so what else is this sysext clobbering when it gets overlaid on ``/usr``?

``systemd-dissect``
"""""""""""""""""""

This is cool!

``systemd-dissect`` allows you to inspect these image files, just calling the command on the ``*.raw`` file gives you a nice overview

.. code-block::

   /var/lib/extensions.d $ systemd-dissect emacs.raw
   Failed to allocate user namespace with 64K users: Connection refused

*ah-hem!* I said, calling this command gives you a nice overview of the image

.. code-block::

   /var/lib/extensions.d $ sudo systemd-dissect emacs.raw
    File Name: emacs.raw
         Size: 337.9M
    Sec. Size: 512
        Arch.: x86-64
   Image UUID: 9cc5b0df-6c03-4674-9267-cbb7f2bc1921
   Image Name: emacs

    sysext R.: ID=fedora
               VERSION_ID=44
               SYSEXT_SCOPE=initrd system portable
               ARCHITECTURE=x86-64

       Use As: ✗ bootable system for UEFI
               ✗ bootable system for container
               ✗ portable service
               ✗ initrd
               ✓ sysext for system
               ✓ sysext for portable service
               ✓ sysext for initrd
               ✗ confext for system
               ✗ confext for portable service
               ✗ confext for initrd

   RW DESIGNATOR PARTITION UUID                       PARTITION LABEL FSTYPE ARCHITECTURE VERITY GROWFS PARTNO
   ro root       9055093f-3ca2-4252-85eb-b380c607c04c root-x86-64     erofs  x86-64       no     no          1

Thank you.

But I want to see *inside* the image, luckily, there's a flag for that

.. code-block::

   /var/lib/extensions.d $ sudo systemd-dissect emacs.raw --list | grep '\.so'
   usr/lib64/libICE.so.6
   usr/lib64/libICE.so.6.3.0
   usr/lib64/libSM.so.6
   usr/lib64/libSM.so.6.0.1
   usr/lib64/libXaw.so.7
   usr/lib64/libXaw7.so.7
   usr/lib64/libXaw7.so.7.0.0
   usr/lib64/libXmu.so.6
   usr/lib64/libXmu.so.6.2.0
   usr/lib64/libXmuu.so.1
   usr/lib64/libXmuu.so.1.0.0
   usr/lib64/libXpm.so.4
   usr/lib64/libXpm.so.4.11.0
   usr/lib64/libXt.so.6
   usr/lib64/libXt.so.6.0.0
   usr/lib64/libgccjit.so.0
   usr/lib64/libgccjit.so.0.0.1
   usr/lib64/libotf.so.1
   usr/lib64/libotf.so.1.0.0
   usr/lib64/libtree-sitter.so.0
   usr/lib64/libtree-sitter.so.0.26

I briefly looked up these libraries, unlike I'm mistake they are all X11 related... I guess my display manager needs to pull them in?
Which explains how I'm able to still use a tty?

But the important thing to note is that they *are* being clobbered

.. code-block::

   $ ls -lZ /usr/lib64/libICE.so.6.3.0
   -rwxr-xr-x. 1 root root unconfined_u:object_r:unlabeled_t:s0 111936 Jan 16  2026 /usr/lib64/libICE.so.6.3.0*

   $ sudo systemd-sysext unmerge
   Unmerged '/usr'.

   $ ls -lZ /usr/lib64/libICE.so.6.3.0
   -rwxr-xr-x. 1 root root system_u:object_r:lib_t:s0 111936 Jan  1  1970 /usr/lib64/libICE.so.6.3.0*

So how do I fix it?

It did not take long to find `this issue <https://github.com/systemd/mkosi/issues/130>`__ which seems to suggest that ``mkosi`` will automatically relabel files if it finds the relevant policies installed.

Install ``selinux-policies`` in base image

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
            man
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
            # Needed to fix SE Linux labelling
            selinux-policy
            # Needed for mkosi?
            systemd
            udev

And enable relabelling

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
   SELinuxRelabel=enabled

And after rebuild it appears to have worked.

.. code-block::

   $ sudo mkdir -p /run/media/img
   $ sudo systemd-dissect mkosi.output/emacs.raw --mount /run/media/img
   $ ls /run/media/img/usr/lib64/libICE.so.6.3.0  -lZ
   -rwxr-xr-x. 1 root root system_u:object_r:lib_t:s0 111936 Jan 16  2026 /run/media/img/usr/lib64/libICE.so.6.3.0*

Moment of truth... *reboots*

It was not enough.

Now stumped, I go back and re-read some of the error messages in the ``journalctl`` logs.

.. code-block::

   avc:  denied  { search } for  pid=7389 comm="(sd-worker)" name="systemd" dev="overlay" ino=14
                                 scontext=system_u:system_r:systemd_userdbd_t:s0
                                 tcontext=unconfined_u:object_r:unlabeled_t:s0
                                 tclass=dir
                                 permissive=0

Which, if I squint at it, I think the ``scontext`` is saying who was denied, the ``tcontext`` tells me the labels of the thing they were trying to access and the ``tclass`` tells me it's a directory.

So I'm looking for some unlabelled directory coming from my image...

Just comparing ``/usr`` with and without the sysext enabled reveals it.

.. code-block::

   $ ls -lZ /usr/
   total 52
   drwxr-xr-x.   1 root root system_u:object_r:bin_t:s0            137 Aug 26 02:15 bin/
   drwxr-xr-x. 166 root root system_u:object_r:etc_t:s0           6067 Jan  1  1970 etc/
   drwxr-xr-x.   2 root root system_u:object_r:usr_t:s0             27 Jan  1  1970 games/
   drwxr-xr-x.   1 root root unconfined_u:object_r:unlabeled_t:s0   53 Sep  9 13:50 include/
   drwxr-xr-x.   1 root root system_u:object_r:lib_t:s0             79 Aug 26 02:15 lib/
   drwxr-xr-x.   1 root root system_u:object_r:lib_t:s0            104 Aug 26 02:15 lib64/
   drwxr-xr-x.   1 root root unconfined_u:object_r:unlabeled_t:s0   44 Sep  9 13:50 libexec/
   lrwxrwxrwx.   1 root root system_u:object_r:usr_t:s0             15 Jan  1  1970 local -> ../var/usrlocal/
   lrwxrwxrwx.   1 root root system_u:object_r:bin_t:s0              3 Jan  1  1970 sbin -> bin/
   drwxr-xr-x.   1 root root system_u:object_r:usr_t:s0             77 Aug 26 02:15 share/
   drwxr-xr-x.   4 root root system_u:object_r:usr_t:s0             63 Jan  1  1970 src/
   lrwxrwxrwx.   1 root root system_u:object_r:usr_t:s0             10 Jan  1  1970 tmp -> ../var/tmp/

   $ sudo systemd-sysext unmerge

   $ ls -lZ /usr/
   total 240
   drwxr-xr-x.   2 root root system_u:object_r:bin_t:s0  73728 Jan  1  1970 bin/
   drwxr-xr-x. 166 root root system_u:object_r:etc_t:s0   6067 Jan  1  1970 etc/
   drwxr-xr-x.   2 root root system_u:object_r:usr_t:s0     27 Jan  1  1970 games/
   drwxr-xr-x.  52 root root system_u:object_r:usr_t:s0   4096 Jan  1  1970 include/
   drwxr-xr-x.  57 root root system_u:object_r:lib_t:s0   1259 Jan  1  1970 lib/
   drwxr-xr-x. 142 root root system_u:object_r:lib_t:s0 118784 Jan  1  1970 lib64/
   drwxr-xr-x.  61 root root system_u:object_r:bin_t:s0   8192 Jan  1  1970 libexec/
   lrwxrwxrwx.   1 root root system_u:object_r:usr_t:s0     15 Jan  1  1970 local -> ../var/usrlocal/
   lrwxrwxrwx.   1 root root system_u:object_r:bin_t:s0      3 Jan  1  1970 sbin -> bin/
   drwxr-xr-x. 324 root root system_u:object_r:usr_t:s0   8192 Jan  1  1970 share/
   drwxr-xr-x.   4 root root system_u:object_r:usr_t:s0     63 Jan  1  1970 src/
   lrwxrwxrwx.   1 root root system_u:object_r:usr_t:s0     10 Jan  1  1970 tmp -> ../var/tmp/

In fact, *all* of the dirs in my image appear to be unlabelled.

.. code-block::

   $ sudo systemd-dissect emacs.raw --mount /run/media/img/
   $ ls -lZ /run/media/img🔒
   total 4
   drwxr-xr-x. 8 root root unconfined_u:object_r:unlabeled_t:s0 129 Sep  9 13:50 usr/

   ls -lZ /run/media/img/usr🔒
   total 24
   dr-xr-xr-x.  2 root root unconfined_u:object_r:unlabeled_t:s0 202 Sep  9 13:50 bin/
   drwxr-xr-x.  2 root root unconfined_u:object_r:unlabeled_t:s0  53 Sep  9 13:50 include/
   dr-xr-xr-x.  5 root root unconfined_u:object_r:unlabeled_t:s0  98 Sep  9 13:50 lib/
   dr-xr-xr-x.  3 root root unconfined_u:object_r:unlabeled_t:s0 589 Sep  9 13:50 lib64/
   drwxr-xr-x.  3 root root unconfined_u:object_r:unlabeled_t:s0  44 Sep  9 13:50 libexec/
   drwxr-xr-x. 11 root root unconfined_u:object_r:unlabeled_t:s0 191 Sep  9 13:50 share/


The question is... how do I fix these labels?
