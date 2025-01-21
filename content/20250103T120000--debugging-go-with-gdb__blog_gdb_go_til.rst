:title: Debugging Go with GDB
:identifier: 20250103T120000
:date: 2025-01-03
:tags: blog, gdb, go, til
:author: Alex Carney
:language: en

TIL: Debugging go programs with ``gdb``
=======================================

.. role:: strike
   :class: line-through

.. highlight:: none

.. container:: post-teaser

   .. code-block:: console

      $ gdb --args podman info
      (gdb) run
      Starting program: /usr/bin/podman info
      [Thread debugging using libthread_db enabled]
      ...
      WARN[0000] Found incomplete layer "6748b9a4e6f2d75763acd0d8351dfb92d4281a0b3546cc68042fb8cb5e1b7c3c", deleting it

      Thread 9 "podman" received signal SIGSEGV, Segmentation fault.
      [Switching to Thread 0x7fbacbfff6c0 (LWP 10496)]
      Downloading source file /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go
      github.com/containers/storage.(*layerStore).load (r=0xc00024c140, lockedForWriting=true, ~r0=<optimized out>, ~r0=<optimized out>, ~r1=..., ~r1=...) at /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go:917
      917                     if layer.Flags == nil {


   *<Freeze frame, record scratch>*

   *You might be wondering how I got here...*

   And no, I wasn't trying to work on `podman <https://github.com/containers/podman>`__!

.. _debug-go-with-gdb-getting-here:

How I got here
--------------

.. note::

   This section has nothing to do with using ``gdb``, I just find it amusing how many tangents I let myself take!
   Feel free to skip this and start with the :ref:`next section <debug-go-with-gdb-setup>`

I was working on a `PR <https://github.com/swyddfa/esbonio/pull/937>`__ for esbonio, and ran into some test failures that I couldn't easily figure out from the CI logs alone.
Trouble was, the tests all relate to my arch nemesis - Windows file paths.

No problem! I'll use `quickemu <https://github.com/quickemu-project/quickemu>`__ to fire up a Windows VM

.. code-block:: console

   $  quickemu --vm windows-11.conf
   ERROR! Requested 'spicy' as viewer, but 'spicy' is not installed.

Oh yes, I haven't spun up a VM on this machine yet so don't have a frontend installed.
I've used ``remote-viewer`` in the past, let's install that... umm... which package provides this again?

*It was in this moment he made a grave mistake*

Rather than do the sane thing and Google it, I thought this would be a good chance to ask my :ref:`local AI model <local-llms-with-ollama-gptel>` for the ``dnf`` incantation to search for the package that provides the ``remote-viewer`` command.
However, I quickly realised none of my containers were working since almost any podman command resulted in a go panic.

.. code-block:: console

   $ podman info
   WARN[0000] Found incomplete layer "6748b9a4e6f2d75763acd0d8351dfb92d4281a0b3546cc68042fb8cb5e1b7c3c", deleting it
   panic: runtime error: invalid memory address or nil pointer dereference
   [signal SIGSEGV: segmentation violation code=0x1 addr=0x100 pc=0x55fab5c85217]

   goroutine 1 gp=0xc0000061c0 m=16 mp=0xc00050f508 [running]:
   panic({0x55fab6c906e0?, 0x55fab7bac9e0?})
           /usr/lib/golang/src/runtime/panic.go:804 +0x168 fp=0xc00005eda8 sp=0xc00005ecf8 pc=0x55fab529aa88
   runtime.panicmem(...)
           /usr/lib/golang/src/runtime/panic.go:262
   runtime.sigpanic()

   [Many, many more lines omitted...]

After a quick rummage around some issue trackers I found that not only was this a known issue, it `has a fix <https://github.com/containers/storage/pull/2185>`__.
Unfortunately the fix hasn't made it into my version of ``podman`` yet, so as a workaround, I will have to remove the incomplete layer myself.

*<Insert Thanos meme here>*

And since I don't know which file(s)/folder(s) need deleting, I thought the :strike:`quickest`, most fun way to figure this out would be to debug the process.

Which brings us onto the subject of this blog post!

.. _debug-go-with-gdb-setup:

Setup
-----

Since I'm using the ``-dx`` version of `Aurora <https://getaurora.dev/>`__, I found that I already had ``gdb`` installed.
From there all you have to do is pass it the program (and any arguments) you want it to run

.. code-block:: console

   $ gdb --args podman
   GNU gdb (Fedora Linux) 15.2-3.fc41
   Reading symbols from podman...

   This GDB supports auto-downloading debuginfo from the following URLs:
     <https://debuginfod.fedoraproject.org/>
   Enable debuginfod for this session? (y or [n])

You want to say yes to this!

.. code-block::

   Debuginfod has been enabled.
   To make this setting permanent, add 'set debuginfod enabled on' to .gdbinit.
   Downloading 70.28 M separate debug info for /usr/bin/podman
   Reading symbols from /home/alex/.cache/debuginfod_client/6c1be8511a45f7f8eef6df8bc94c20641d96eb9a/debuginfo...
   /var/home/alex/info: No such file or directory.
   warning: Missing auto-load script at offset 0 in section .debug_gdb_scripts
   of file /var/home/alex/.cache/debuginfod_client/6c1be8511a45f7f8eef6df8bc94c20641d96eb9a/debuginfo.
   Use `info auto-load python-scripts [REGEXP]' to list them.

Once enabled, ``gdb`` will be able to download any debug symbols it needs automatically, on demand!


.. code-block:: console

   (gdb) run
   Starting program: /usr/bin/podman
   Downloading separate debug info for system-supplied DSO at 0x7f6e30ef1000
   Downloading 188.48 K separate debug info for /lib64/libresolv.so.2
   Downloading 187.84 K separate debug info for /lib64/libsubid.so.4
   Downloading 94.60 K separate debug info for /var/home/alex/.cache/debuginfod_client/05cb3df691d3ecacb634897526293dabb8834d87/debuginfo
   Downloading 1.20 M separate debug info for /lib64/libgpgme.so.11
   Downloading 2.77 M separate debug info for /var/home/alex/.cache/debuginfod_client/ad0ff4afb064a77890eb5b5dfae388c7598f3180/debuginfo
   Downloading 319.12 K separate debug info for /lib64/libseccomp.so.2
   Downloading 610.38 K separate debug info for /lib64/libgcc_s.so.1
   Downloading 6.22 M separate debug info for /var/home/alex/.cache/debuginfod_client/a120aca96a83fdaa1dbff64ccb67f9b3e46a86fc/debuginfo
   Downloading 6.70 M separate debug info for /lib64/libc.so.6
   [Thread debugging using libthread_db enabled]
   Using host libthread_db library "/lib64/libthread_db.so.1".
   Downloading 168.53 K separate debug info for /lib64/libaudit.so.1
   Downloading 30.00 K separate debug info for /var/home/alex/.cache/debuginfod_client/894985c591daedd80a91b4221c8725fc8aacb96b/debuginfo
   Downloading 540.78 K separate debug info for /lib64/libselinux.so.1
   Downloading 82.43 K separate debug info for /var/home/alex/.cache/debuginfod_client/a77b40fbe465e7cfd1b53f220a51f41837976591/debuginfo
   Downloading 916.87 K separate debug info for /lib64/libsemanage.so.2
   Downloading 15.68 K separate debug info for /var/home/alex/.cache/debuginfod_client/92a110d4e6ddc3d7ec8219622107d2ade30338e3/debuginfo
   Downloading 129.88 K separate debug info for /lib64/libeconf.so.0
   Downloading 5.09 K separate debug info for /var/home/alex/.cache/debuginfod_client/12df41e5399f930a9b1520115cc1f2ed776edfa7/debuginfo
   Downloading 392.91 K separate debug info for /lib64/libcrypt.so.2
   Downloading 61.04 K separate debug info for /var/home/alex/.cache/debuginfod_client/3b22db61e60f5ba97c4e0bb1cbee6a8107f3f313/debuginfo
   Downloading 125.27 K separate debug info for /lib64/libacl.so.1
   Downloading separate debug info for /var/home/alex/.cache/debuginfod_client/6e078332ae36e8358da618b723ea4463791c70fc/debuginfo
   Downloading separate debug info for /lib64/libattr.so.1
   Downloading 7.69 K separate debug info for /var/home/alex/.cache/debuginfod_client/45c3b76fd658b1e86c6ff09d1f06babadf71fa78/debuginfo
   Downloading 193.53 K separate debug info for /lib64/libpam.so.0
   Downloading separate debug info for /var/home/alex/.cache/debuginfod_client/dc4d461ec91383087257839ec7862ed0f230a765/debuginfo
   Downloading 34.12 K separate debug info for /lib64/libpam_misc.so.0
   Downloading 299.74 K separate debug info for /lib64/libassuan.so.0
   Downloading 555.48 K separate debug info for /lib64/libgpg-error.so.0
   Downloading 28.08 K separate debug info for /var/home/alex/.cache/debuginfod_client/1966004cd3bdfb76ca6c281c7ea322057ca67c08/debuginfo
   Downloading separate debug info for /lib64/libcap-ng.so.0
   Downloading 9.07 K separate debug info for /var/home/alex/.cache/debuginfod_client/32db198012cdf3b3d1fe4db5414ca51ee36474d9/debuginfo
   Downloading 1.50 M separate debug info for /lib64/libpcre2-8.so.0
   Downloading 77.46 K separate debug info for /var/home/alex/.cache/debuginfod_client/ecf3f9c874cd4aa76ed4bd9e4f4d87d2d2ab9373/debuginfo
   Downloading 2.95 M separate debug info for /lib64/libsepol.so.2
   Downloading 163.20 K separate debug info for /lib64/libbz2.so.1
   Downloading separate debug info for /var/home/alex/.cache/debuginfod_client/e55f754492a153b4068a131340d25bf80918f8cf/debuginfo
   Downloading 2.09 M separate debug info for /lib64/libm.so.6

Debugging
---------

.. seealso::

   `Debugging Go Code with GDB <https://go.dev/doc/gdb>`__
      A guide from the GO documentation on using ``gdb`` to debug a program

Finally, we're caught up with where we were at the start of the blog post

(If you skipped the :ref:`debug-go-with-gdb-getting-here` section, all I'm hoping to acheive is finding out where the incomplete layer is stored, so I can delete it myself)

.. code-block:: console

   (gdb) run
   Starting program: /usr/bin/podman info
   [Thread debugging using libthread_db enabled]
   Using host libthread_db library "/lib64/libthread_db.so.1".
   [New Thread 0x7fbb1feff6c0 (LWP 19987)]
   [New Thread 0x7fbb1f6fe6c0 (LWP 19988)]
   [New Thread 0x7fbb1e6fc6c0 (LWP 19990)]
   [New Thread 0x7fbb1eefd6c0 (LWP 19989)]
   [New Thread 0x7fbb1defb6c0 (LWP 19991)]
   [New Thread 0x7fbb1d55a6c0 (LWP 19992)]
   [New Thread 0x7fbb1cd096c0 (LWP 19993)]
   [New Thread 0x7fbb17fff6c0 (LWP 19994)]
   [New Thread 0x7fbb177fe6c0 (LWP 19995)]
   [New Thread 0x7fbb16ffd6c0 (LWP 19996)]
   [New Thread 0x7fbb167fc6c0 (LWP 19997)]
   [Detaching after vfork from child process 19998]
   [Detaching after vfork from child process 19999]
   [Detaching after vfork from child process 20001]
   [Detaching after vfork from child process 20002]
   [Detaching after vfork from child process 20004]
   [Detaching after vfork from child process 20005]
   [Detaching after vfork from child process 20006]
   [Detaching after vfork from child process 20008]
   [Detaching after vfork from child process 20009]
   [Detaching after vfork from child process 20011]
   [Detaching after vfork from child process 20013]
   [Detaching after vfork from child process 20015]
   [Detaching after vfork from child process 20016]
   [New Thread 0x7fbb15ffb6c0 (LWP 20017)]
   WARN[0000] Found incomplete layer "6748b9a4e6f2d75763acd0d8351dfb92d4281a0b3546cc68042fb8cb5e1b7c3c", deleting it

   Thread 11 "podman" received signal SIGSEGV, Segmentation fault.
   [Switching to Thread 0x7fbb16ffd6c0 (LWP 19996)]
   github.com/containers/storage.(*layerStore).load (r=0xc0004ea000, lockedForWriting=true, ~r0=<optimized out>, ~r0=<optimized out>, ~r1=..., ~r1=...) at /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go:917
   917                     if layer.Flags == nil {

The ``l`` command prints the code around where the panic happened.

.. code-block:: console

   (gdb) l
   912             // Last step: try to remove anything that a previous
   913             // user of this storage area marked for deletion but didn't manage to
   914             // actually delete.
   915             var incompleteDeletionErrors error // = nil
   916             for _, layer := range r.layers {
   917                     if layer.Flags == nil {
   918                             layer.Flags = make(map[string]interface{})
   919                     }
   920                     if layerHasIncompleteFlag(layer) {
   921                             logrus.Warnf("Found incomplete layer %#v, deleting it", layer.ID)

The ``p`` command allows us to inspect the value of a variable.
As expected, ``layer`` contains a null pointer.

.. code-block:: console

   (gdb) p layer
   $1 = (github.com/containers/storage.Layer *) 0x0

There are limits to gdb's Go support however, and trying to look at the contents of the ``layers`` array does not make much sense to me.

.. code-block:: console

   (gdb) p r.layers
   $2 = {array = 0xc0001d7800, len = 35, cap = 64}
   (gdb) p r.layers.array
   $3 = (github.com/containers/storage.Layer **) 0xc0001d7800

This must be some of Go's implementation details showing through...

Setting a Breakpoint
--------------------

It also doesn't help that the crash has already happened, I want to inspect the state of the program just before the crash.
Thankfully, the warning message about the incomplete layer provides the ideal place to set the breakpoint.

After starting a fresh debug session, I can use the ``break`` command to set a breakpoint

.. code-block:: console

   (gdb) break /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go:921
   Breakpoint 1 at 0xa63324: file /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go, line 921.
   (gdb) run
   Starting program: /usr/bin/podman info
   [Thread debugging using libthread_db enabled]
   Using host libthread_db library "/lib64/libthread_db.so.1".
   ...

   Thread 13 "podman" hit Breakpoint 1, github.com/containers/storage.(*layerStore).load (r=0xc000622000, lockedForWriting=true, ~r0=<optimized out>, ~r0=<optimized out>, ~r1=..., ~r1=...) at /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go:921
   921                             logrus.Warnf("Found incomplete layer %#v, deleting it", layer.ID)
   (gdb)


Using the ``n(ext)`` and ``s(tep)`` commands I was eventually able to step into the function responsible for removing the layer

.. code-block:: console

   (gdb) n
   921                             logrus.Warnf("Found incomplete layer %#v, deleting it", layer.ID)
   (gdb) n
   WARN[0014] Found incomplete layer "6748b9a4e6f2d75763acd0d8351dfb92d4281a0b3546cc68042fb8cb5e1b7c3c", deleting it
   922                             err := r.deleteInternal(layer.ID)
   (gdb) s
   github.com/containers/storage.(*layerStore).deleteInternal (r=0xc0004f4000, id=..., ~r0=...) at /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go:1888
   1888    func (r *layerStore) deleteInternal(id string) error {


.. note::
   :class: mt-4

   It actually took me a few attempts to step into the ``deleteInternal`` function.

   ``podman`` spins up a lot of goroutines and depending on how slow I was, one of the background goroutines would segfault before I could get to it.
   This would switch the debugger's context away from the goroutine I was interested in.

   I am sure there is a way to switch back but I didn't try looking it up.

After a few more `n` commands I arrived at some code that looks like it should be able to tell me where the layers are stored.

.. code-block:: go

   1911           os.Remove(r.tspath(id))
   1912           os.RemoveAll(r.datadir(id))


And sure enough I was able to locate the directory where the layer was stored

.. code-block::

   github.com/containers/storage.(*layerStore).tspath (r=0xc000686000, id=...) at /usr/src/debug/podman-5.3.1-1.fc41.x86_64/vendor/github.com/containers/storage/layers.go:1870
   1870           return filepath.Join(r.layerdir, id+tarSplitSuffix)
   (gdb) p r.layerdir
   $7 = 0xc0005a29c0 "/var/home/alex/.local/share/containers/storage/overlay-layers"

Fixing the Panic
----------------

Turns out the problematic layer (``6748b9a4e6f2d75763acd0d8351dfb92d4281a0b3546cc68042fb8cb5e1b7c3c``) had been removed, but the record of it still existed in the ``layers.json`` metadata file.
After manually removing it ``podman`` once again worked as expected!
