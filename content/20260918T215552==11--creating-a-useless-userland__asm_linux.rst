:title: Creating a Useless Userland
:date: 2026-09-18
:tags: asm, linux
:identifier: 20260918T215552
:signature: 11

Creating a Useless Userland
===========================

For reasons.


Linux booting
-------------

kernel.org/docs

man 7 boot - sys v init
man 7 bootparam
man 7 bootup - systemd

Assembly
--------

:bib:man:`syscall(2)` - calling convention

:bib:man:`syscalls(2)` - list of syscalls.

Also need ``/usr/include/linux/unistd.h`` to get actual sys call numbers.

From there we can write a simple hello, world application!

.. code-block:: asm
   :project: dangosfi
   :filename: machines/useless/src/init.s
   :revison: 1

   .global _start
   .text

   _start:
       # write(1, msg, len)
       mov rdi, 1        # fd = stdout
       lea rsi, [msg]
       lea rdx, [len]
       mov rax, 1        # write()
       syscall

       # exit(0)
       mov rdi, 0
       mov rax, 60       # exit()
       syscall

   .data
   msg:
       .ascii "Hello, World!\n"
   len = . -msg

Compile

.. code-block:: makefile
   :project: dangosfi
   :filename: machines/useless/Makefile

   init: init.o

   %: %.o
       ld -o $@ $^

   %.o: %.s
       as -msyntax=intel -o $@ $<

.. code-block:: console

   $ make init
   as -msyntax=intel -o hello.o hello.s
   ld -o hello hello.o
   $ ./init
   Hello, World!


Initrd
------

.. code-block:: makefile
   :project: dangosfi
   :filename: machines/useless/Makefile

   initramfs.cpio.gz: init
           mkdir initrd
           cp init initrd
           cd initrd && find . | cpio --quiet -H newc -o | gzip -9 -n > ../$@
           rm -r initrd


.. code-block:: console

   ❯ tree init/
   init/
   └── init

   1 directory, 1 file

Which we can pack into a cpio archive.

.. code-block:: console

   init/ $ find . | cpio --quiet -H newc -o | gzip -9 -n > initramfs.cpio.gz

First boot
----------

.. seealso::

   Great talk! - https://www.youtube.com/watch?v=Sk9TatW9ino&pp=ygUeYnVpbGRpbmcgc2ltcGxlc3QgbGludXggc3lzdGVt

Grabbing the kernel I happen to have booted::

  KERNEL=/boot/ostree/default-95a60ab226446d1abd6908acfc3f412b4047cc71b31336f3a252c82ce0036736/vmlinuz-7.2.4-200.fc44.x86_64

Again keeping things simple(?) let's try and boot the kernel directly

.. code-block:: console

   qemu-system-x86_64 -kernel $KERNEL \
                      -initrd initramfs.cpio.gz \
                      -append "console=ttyS0 root=/dev/ram0 panic=1" \
                      -nographic \
                      --no-reboot

To my surprise, it works!

.. code-block::

   [    2.558204] Freeing unused kernel image (rodata/data gap) memory: 1692K
   [    2.770099] x86/mm: Checked W+X mappings: passed, no W+X pages found.
   [    2.770639] Run /init as init process
   [    2.771023]   with arguments:
   [    2.771226]     /init
   [    2.771333]   with environment:
   [    2.771460]     HOME=/
   [    2.771560]     TERM=linux
   Hello, World!
   [    2.801666] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000000
   [    2.802446] CPU: 0 UID: 0 PID: 1 Comm: init Not tainted 7.2.4-200.fc44.x86_64 #1 PREEMPT(lazy)
   [    2.802966] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.17.0-10.fc44 06/10/2025
   [    2.803451] Call Trace:
   [    2.803613]  <TASK>
   [    2.803882]  dump_stack_lvl+0x5d/0x80
   [    2.804231]  vpanic+0x246/0x450
   [    2.804350]  panic+0x6b/0x70
   [    2.804460]  do_exit.cold+0x15/0x15
   [    2.804590]  __x64_sys_exit+0x1b/0x20
   [    2.804731]  x64_sys_call+0x152e/0x1530
   [    2.804969]  do_syscall_64+0xe2/0x570
   [    2.805116]  ? do_fault+0x1fc/0x380
   [    2.805246]  ? __handle_mm_fault+0x47c/0x6c0
   [    2.805406]  ? count_memcg_events+0xd9/0x210
   [    2.805564]  ? handle_mm_fault+0x24b/0x340
   [    2.805811]  ? do_user_addr_fault+0x2cd/0x840
   [    2.805986]  ? irqentry_exit+0x45/0x760
   [    2.806141]  ? do_syscall_64+0x99/0x570
   [    2.806281]  ? exc_page_fault+0x90/0x1e0
   [    2.806428]  entry_SYSCALL_64_after_hwframe+0x76/0x7e
   [    2.806891] RIP: 0033:0x400148
   [    2.807289] Code: 00 48 8d 34 25 48 11 40 00 48 8d 14 25 0e 00 00 00 48 c7 c0 01 00 00 00 0f 05 48 c7 c7 00 00 00 00 480
   [    2.808040] RSP: 002b:00007ffd267cd5a0 EFLAGS: 00000202 ORIG_RAX: 000000000000003c
   [    2.808346] RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 0000000000400148
   [    2.808603] RDX: 000000000000000e RSI: 0000000000401148 RDI: 0000000000000000
   [    2.808968] RBP: 0000000000000000 R08: 0000000000000000 R09: 0000000000000000
   [    2.809226] R10: 0000000000000000 R11: 0000000000000202 R12: 0000000000000000
   [    2.809469] R13: 0000000000000000 R14: 0000000000000000 R15: 0000000000000000
   [    2.809830]  </TASK>
   [    2.810348] Kernel Offset: 0x2f000000 from 0xffffffff81000000 (relocation range: 0xffffffff80000000-0xffffffffbfffffff)
   [    2.811044] Rebooting in 1 seconds..

For a very generous definition of "works".

Shutdown
--------

Rather than using the ``exit`` syscall, we should shutdown the system.
Bizarrely, the syscall for shutting down is called... ``reboot``

.. code-block:: asm
   :project: dangosfi
   :filename: machines/useless/src/init.s
   :revision: 2

   .global _start
   .text

   _start:
       # write(1, msg, len)
       mov rdi, 1           # fd = stdout
       lea rsi, [msg]
       lea rdx, [len]
       mov rax, 1           # write()
       syscall

       # reboot(op)
       mov rdi, 0x4321FEDC  # LINUX_REBOOT_CMD_POWER_OFF
       mov rax, 169         # reboot()
       syscall

   .data
   msg:
       .ascii "Hello, World!\n"
   len = . -msg
