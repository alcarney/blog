:title: Creating a Useless Userland
:date: 2026-11-15
:tags: asm, blog, linux
:identifier: 20260918T215552
:signature: 11

:in-project: dangosfi

Creating a Useless Linux Userland
=================================

.. highlight:: console

.. container:: post-teaser

   As you may or may not know, I run Linux on my laptop.

   .. pull-quote::

      Uh, what you're referring to as Linux, is in fact, GNU/Linux or as I've...

   Yes... I was getting to that!

   If you tinker with Linux long enough, you eventually learn that "Linux" is "just a kernel".
   The kernel knows *how* to operate your hardware e.g. mount disks, play sound, display graphics etc.

   But in order to have a functioning computer you also need to bring your own set of tools, often referred to as the system's "userland", that tell the kernel *what* to do.
   The majority(?) of Linux systems today use the tools provided by the GNU project as the foundation of their userland, hence GNU/Linux.

   Thinking it would be Fun\ :sup:`TM`, I decided I would see what it would take to create my own minimal userland environment for a bare Linux kernel.

   Fair warning though, it's going to be useless! 😅

First Boot
----------

At some point it could be Fun\ :sup:`TM` to try this on actual hardware, but for my sanity it's probably best to start off with a QEMU virtual machine.

Also, if I was going to do this "properly" I should compile my own kernel, but for this it probably makes sense to just grab whatever kernel I have currently booted::

  $ cat /boot/loader/entries/ostree-2.conf
  title Aurora (Version: latest-44.20261107.1) (ostree:0)
  version 2
  options ...
  linux /ostree/default-23f36689626b2946b6640fa78f1f355e7bc20903e245a3b84de744bd1b4f0136/vmlinuz-7.2.15-200.fc44.x86_64
  initrd /ostree/default-23f36689626b2946b6640fa78f1f355e7bc20903e245a3b84de744bd1b4f0136/initramfs-7.2.15-200.fc44.x86_64.img

Which we can try `booting directly <https://www.qemu.org/docs/master/system/linuxboot.html>`__ with QEMU::

  $ export KERNEL="/ostree/default-23f36689626b2946b6640fa78f1f355e7bc20903e245a3b84de744bd1b4f0136/vmlinuz-7.2.15-200.fc44.x86_64"
  $ qemu-system-x86_64 -kernel $KERNEL \
                       -append "console=ttyS0 panic=1" \
                       --no-reboot \
                       -nographic

where:

- ``-kernel $KERNEL``: Boots the given kernel directly
- ``-append``: Adds the given parameters to `the kernel command-line <https://docs.kernel.org/admin-guide/kernel-parameters.html>`__

  - ``console=ttyS0``: Attaches the console to ``ttyS0`` (I don't know the detail, but this gets QEMU to print the boot logs to the terminal)

  - ``panic=1``: Tells the kernel to automatically reboot 1 second after a kernel panic.

- ``--no-reboot``: Tells QEMU to exit if the VM reboots.
- ``-nographic``: Disables the graphical display

.. raw:: html

   <style>
     .qemu-output div.highlight { max-height: 400px; }
   </style>

.. container:: qemu-output

   Which results (surprise, surprise), in a kernel panic::

      SeaBIOS (version 1.17.0-10.fc44)


      iPXE (https://ipxe.org) 00:03.0 CA00 PCI2.10 PnP PMM+06FCBC10+06F0BC10 CA00



      Booting from ROM...
      Probing EDD (edd=off to disable)... o
      [    0.000000] Linux version 7.2.15-200.fc44.x86_64 (mockbuild@dc8a34586fbd46d7b2d0015e1704ecb5) (gcc (GCC) 16.2.1 20261029 (Red Hat 16.2.1-3), GNU ld version 2.46.1-1.fc44) #1 SMP PREEMPT_DYNAMIC Sun Nov  1 16:10:54 UTC 2026
      [    0.000000] Command line: console=ttyS0 panic=1
      [    0.000000] BIOS-provided physical RAM map:
      [    0.000000] BIOS-e820: [mem 0x0000000000000000-0x000000000009fbff]  System RAM
      [    0.000000] BIOS-e820: [mem 0x000000000009fc00-0x000000000009ffff]  device reserved
      [    0.000000] BIOS-e820: [gap 0x00000000000a0000-0x00000000000effff]
      [    0.000000] BIOS-e820: [mem 0x00000000000f0000-0x00000000000fffff]  device reserved
      [    0.000000] BIOS-e820: [mem 0x0000000000100000-0x0000000007fdffff]  System RAM
      [    0.000000] BIOS-e820: [mem 0x0000000007fe0000-0x0000000007ffffff]  device reserved
      [    0.000000] BIOS-e820: [gap 0x0000000008000000-0x00000000fffbffff]
      [    0.000000] BIOS-e820: [mem 0x00000000fffc0000-0x00000000ffffffff]  device reserved
      [    0.000000] BIOS-e820: [gap 0x0000000100000000-0x000000fcffffffff]
      [    0.000000] BIOS-e820: [mem 0x000000fd00000000-0x000000ffffffffff]  device reserved
      [    0.000000] NX (Execute Disable) protection: active
      [    0.000000] APIC: Static calls initialized
      [    0.000000] DMI: SMBIOS 2.8 present.
      [    0.000000] DMI: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.17.0-10.fc44 06/10/2025
      [    0.000000] DMI: Memory slots populated: 1/1
      [    0.000000] last_pfn = 0x7fe0 max_arch_pfn = 0x400000000
      [    0.000000] MTRR map: 4 entries (3 fixed + 1 variable; max 19), built from 8 variable MTRRs
      [    0.000000] x86/PAT: Configuration [0-7]: WB  WC  UC- UC  WB  WP  UC- WT
      [    0.000000] found SMP MP-table at [mem 0x000f54e0-0x000f54ef]
      [    0.000000] ACPI: Early table checksum verification disabled
      [    0.000000] ACPI: RSDP 0x00000000000F5320 000014 (v00 BOCHS )
      [    0.000000] ACPI: RSDT 0x0000000007FE2335 000034 (v01 BOCHS  BXPC     00000001 BXPC 00000001)
      [    0.000000] ACPI: FACP 0x0000000007FE21E9 000074 (v01 BOCHS  BXPC     00000001 BXPC 00000001)
      [    0.000000] ACPI: DSDT 0x0000000007FE0040 0021A9 (v01 BOCHS  BXPC     00000001 BXPC 00000001)
      [    0.000000] ACPI: FACS 0x0000000007FE0000 000040
      [    0.000000] ACPI: APIC 0x0000000007FE225D 000078 (v03 BOCHS  BXPC     00000001 BXPC 00000001)
      [    0.000000] ACPI: HPET 0x0000000007FE22D5 000038 (v01 BOCHS  BXPC     00000001 BXPC 00000001)
      [    0.000000] ACPI: WAET 0x0000000007FE230D 000028 (v01 BOCHS  BXPC     00000001 BXPC 00000001)
      [    0.000000] ACPI: Reserving FACP table memory at [mem 0x7fe21e9-0x7fe225c]
      [    0.000000] ACPI: Reserving DSDT table memory at [mem 0x7fe0040-0x7fe21e8]
      [    0.000000] ACPI: Reserving FACS table memory at [mem 0x7fe0000-0x7fe003f]
      [    0.000000] ACPI: Reserving APIC table memory at [mem 0x7fe225d-0x7fe22d4]
      [    0.000000] ACPI: Reserving HPET table memory at [mem 0x7fe22d5-0x7fe230c]
      [    0.000000] ACPI: Reserving WAET table memory at [mem 0x7fe230d-0x7fe2334]
      [    0.000000] No NUMA configuration found
      [    0.000000] Faking a node at [mem 0x0000000000000000-0x0000000007fdffff]
      [    0.000000] NODE_DATA(0) allocated [mem 0x07fb4f80-0x07fdffff]
      [    0.000000] ACPI: PM-Timer IO Port: 0x608
      [    0.000000] ACPI: LAPIC_NMI (acpi_id[0xff] dfl dfl lint[0x1])
      [    0.000000] IOAPIC[0]: apic_id 0, version 32, address 0xfec00000, GSI 0-23
      [    0.000000] ACPI: INT_SRC_OVR (bus 0 bus_irq 0 global_irq 2 dfl dfl)
      [    0.000000] ACPI: INT_SRC_OVR (bus 0 bus_irq 5 global_irq 5 high level)
      [    0.000000] ACPI: INT_SRC_OVR (bus 0 bus_irq 9 global_irq 9 high level)
      [    0.000000] ACPI: INT_SRC_OVR (bus 0 bus_irq 10 global_irq 10 high level)
      [    0.000000] ACPI: INT_SRC_OVR (bus 0 bus_irq 11 global_irq 11 high level)
      [    0.000000] ACPI: Using ACPI (MADT) for SMP configuration information
      [    0.000000] ACPI: HPET id: 0x8086a201 base: 0xfed00000
      [    0.000000] CPU topo: Max. logical packages:   1
      [    0.000000] CPU topo: Max. logical nodes:      1
      [    0.000000] CPU topo: Num. nodes per package:  1
      [    0.000000] CPU topo: Max. logical dies:       1
      [    0.000000] CPU topo: Max. dies per package:   1
      [    0.000000] CPU topo: Max. threads per core:   1
      [    0.000000] CPU topo: Num. cores per package:     1
      [    0.000000] CPU topo: Num. threads per package:   1
      [    0.000000] CPU topo: Allowing 1 present CPUs plus 0 hotplug CPUs
      [    0.000000] PM: hibernation: Registered nosave memory: [mem 0x00000000-0x00000fff]
      [    0.000000] PM: hibernation: Registered nosave memory: [mem 0x0009f000-0x000fffff]
      [    0.000000] [gap 0x08000000-0xfffbffff] available for PCI devices
      [    0.000000] Booting paravirtualized kernel on bare hardware
      [    0.000000] clocksource: refined-jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 1910969940391419 ns
      [    0.000000] Zone ranges:
      [    0.000000]   DMA      [mem 0x0000000000001000-0x0000000000ffffff]
      [    0.000000]   DMA32    [mem 0x0000000001000000-0x0000000007fdffff]
      [    0.000000]   Normal   empty
      [    0.000000]   Device   empty
      [    0.000000] Movable zone start for each node
      [    0.000000] Early memory node ranges
      [    0.000000]   node   0: [mem 0x0000000000001000-0x000000000009efff]
      [    0.000000]   node   0: [mem 0x0000000000100000-0x0000000007fdffff]
      [    0.000000] Initmem setup node 0 [mem 0x0000000000001000-0x0000000007fdffff]
      [    0.000000] On node 0, zone DMA: 1 pages in unavailable ranges
      [    0.000000] On node 0, zone DMA: 97 pages in unavailable ranges
      [    0.000000] On node 0, zone DMA32: 32 pages in unavailable ranges
      [    0.000000] setup_percpu: NR_CPUS:8192 nr_cpumask_bits:1 nr_cpu_ids:1 nr_node_ids:1
      [    0.000000] percpu: Embedded 85 pages/cpu s225280 r8192 d114688 u2097152
      [    0.000000] Kernel command line: console=ttyS0 panic=1
      [    0.000000] printk: log buffer data + meta data: 262144 + 1114112 = 1376256 bytes
      [    0.000000] Dentry cache hash table entries: 8192 (order: 4, 65536 bytes, linear)
      [    0.000000] Inode-cache hash table entries: 4096 (order: 3, 32768 bytes, linear)
      [    0.000000] Fallback order for Node 0: 0
      [    0.000000] Built 1 zonelists, mobility grouping on.  Total pages: 32638
      [    0.000000] Policy zone: DMA32
      [    0.000000] mem auto-init: stack:all(zero), heap alloc:on, heap free:off
      [    0.000000] SLUB: HWalign=64, Order=0-3, MinObjects=0, CPUs=1, Nodes=1
      [    0.000000] ftrace: allocating 64811 entries in 256 pages
      [    0.000000] ftrace: allocated 256 pages with 1 groups
      [    0.000000] Dynamic Preempt: lazy
      [    0.000000] rcu: Preemptible hierarchical RCU implementation.
      [    0.000000] rcu: 	RCU event tracing is enabled.
      [    0.000000] rcu: 	RCU restricting CPUs from NR_CPUS=8192 to nr_cpu_ids=1.
      [    0.000000] 	Trampoline variant of Tasks RCU enabled.
      [    0.000000] 	Rude variant of Tasks RCU enabled.
      [    0.000000] 	Tracing variant of Tasks RCU enabled.
      [    0.000000] rcu: RCU calculated value of scheduler-enlistment delay is 100 jiffies.
      [    0.000000] rcu: Adjusting geometry for rcu_fanout_leaf=16, nr_cpu_ids=1
      [    0.000000] RCU Tasks: Setting shift to 0 and lim to 1 rcu_task_cb_adjust=1 rcu_task_cpu_ids=1.
      [    0.000000] RCU Tasks Rude: Setting shift to 0 and lim to 1 rcu_task_cb_adjust=1 rcu_task_cpu_ids=1.
      [    0.000000] NR_IRQS: 524544, nr_irqs: 256, preallocated irqs: 16
      [    0.000000] rcu: srcu_init: Setting srcu_struct sizes based on contention.
      [    0.000000] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 1911260446275000 ns
      [    0.000000] kfence: initialized - using 2097152 bytes for 255 objects at 0x(____ptrval____)-0x(____ptrval____)
      [    0.000000] Console: colour VGA+ 80x25
      [    0.000000] printk: legacy console [ttyS0] enabled
      [    0.000000] ACPI: Core revision 20260408
      [    0.000000] clocksource: hpet: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 19112604467 ns
      [    0.003000] APIC: Switch to symmetric I/O mode setup
      [    0.007000] ..TIMER: vector=0x30 apic1=0 pin1=2 apic2=-1 pin2=-1
      [    0.016000] tsc: Unable to calibrate against PIT
      [    0.016000] tsc: using HPET reference calibration
      [    0.016000] tsc: Detected 3293.528 MHz processor
      [    0.000551] clocksource: tsc-early: mask: 0xffffffffffffffff max_cycles: 0x2f796aa6be4, max_idle_ns: 440795280959 ns
      [    0.001754] Calibrating delay loop (skipped), value calculated using timer frequency.. 6587.05 BogoMIPS (lpj=3293528)
      [    0.006137] Last level iTLB entries: 4KB 512, 2MB 255, 4MB 127
      [    0.006418] Last level dTLB entries: 4KB 512, 2MB 255, 4MB 127, 1GB 0
      [    0.006926] mitigations: Enabled attack vectors: user_kernel, user_user, guest_host, guest_guest, SMT mitigations: auto
      [    0.007907] Spectre V2 : Mitigation: Retpolines
      [    0.008686] Spectre V1 : Mitigation: usercopy/swapgs barriers and __user pointer sanitization
      [    0.009131] Spectre V2 : Spectre v2 / SpectreRSB: Filling RSB on context switch and VMEXIT
      [    0.012048] x86/fpu: x87 FPU will use FXSAVE
      [    0.527969] pid_max: default: 32768 minimum: 301
      [    0.544832] Yama: becoming mindful.
      [    0.545244] SELinux:  Initializing.
      [    0.556597] LSM support for eBPF active
      [    0.557091] landlock: Up and running.
      [    0.561639] Mount-cache hash table entries: 512 (order: 0, 4096 bytes, linear)
      [    0.562067] Mountpoint-cache hash table entries: 512 (order: 0, 4096 bytes, linear)
      [    0.572313] VFS: Finished mounting rootfs on nullfs
      [    0.704537] smpboot: CPU0: AMD QEMU Virtual CPU version 2.5+ (family: 0xf, model: 0x6b, stepping: 0x1)
      [    0.716214] Performance Events: PMU not available due to virtualization, using software events only.
      [    0.718441] signal: max sigframe size: 1440
      [    0.721867] rcu: Hierarchical SRCU implementation.
      [    0.722103] rcu: 	Max phase no-delay instances is 400.
      [    0.730306] NMI watchdog: Perf NMI watchdog permanently disabled
      [    0.734658] smp: Bringing up secondary CPUs ...
      [    0.736321] smp: Brought up 1 node, 1 CPU
      [    0.736692] smpboot: Total of 1 processors activated (6587.05 BogoMIPS)
      [    0.745150] Memory: 54336K/130552K available (24467K kernel code, 4815K rwdata, 18660K rodata, 5324K init, 4212K bss, 71300K reserved, 0K cma-reserved)
      [    0.753313] devtmpfs: initialized
      [    0.757114] x86/mm: Memory block size: 128MB
      [    0.764828] posixtimers hash table entries: 512 (order: 1, 8192 bytes, linear)
      [    0.765396] futex hash table entries: 256 (16384 bytes on 1 NUMA nodes, total 16 KiB, linear).
      [    0.778420] PM: RTC time: 18:10:35, date: 2026-11-07
      [    0.792289] NET: Registered PF_NETLINK/PF_ROUTE protocol family
      [    0.798940] DMA: preallocated 128 KiB GFP_KERNEL|GFP_DMA pool for atomic allocations
      [    0.799591] DMA: preallocated 128 KiB GFP_KERNEL|GFP_DMA32 pool for atomic allocations
      [    0.800555] audit: initializing netlink subsys (disabled)
      [    0.802950] audit: type=2000 audit(1794075034.818:1): state=initialized audit_enabled=0 res=1
      [    0.873150] thermal_sys: Registered thermal governor 'fair_share'
      [    0.873229] thermal_sys: Registered thermal governor 'bang_bang'
      [    0.873537] thermal_sys: Registered thermal governor 'step_wise'
      [    0.873828] thermal_sys: Registered thermal governor 'user_space'
      [    0.874826] cpuidle: using governor menu
      [    0.877417] Freeing SMP alternatives memory: 60K
      [    0.877974] acpiphp: ACPI Hot Plug PCI Controller Driver version: 0.5
      [    0.881880] PCI: Using configuration type 1 for base access
      [    0.882945] virt/tdx: TDX not supported by the host platform
      [    0.885447] kprobes: kprobe jump-optimization is enabled. All kprobes are optimized if possible.
      [    0.917606] HugeTLB: registered 2.00 MiB page size, pre-allocated 0 pages
      [    0.918117] HugeTLB: 28 KiB vmemmap can be freed for a 2.00 MiB page
      [    0.979267] raid6: using intx1 recovery algorithm
      [    0.983563] raid6: skipped pq benchmark and selected sse2x4
      [    0.995853] ACPI: Added _OSI(Module Device)
      [    0.996062] ACPI: Added _OSI(Processor Device)
      [    0.996253] ACPI: Added _OSI(Processor Aggregator Device)
      [    1.057361] ACPI: 1 ACPI AML tables successfully acquired and loaded
      [    1.108133] ACPI: \_SB_: platform _OSC: OS support mask [006e7eff]
      [    1.121116] ACPI: Interpreter enabled
      [    1.126510] ACPI: PM: (supports S0 S3 S4 S5)
      [    1.126601] ACPI: Using IOAPIC for interrupt routing
      [    1.134604] PCI: Using host bridge windows from ACPI; if necessary, use "pci=nocrs" and report a bug
      [    1.135047] PCI: Ignoring E820 reservations for host bridge windows
      [    1.141209] ACPI: Enabled 2 GPEs in block 00 to 0F
      [    1.218475] ACPI: PCI Root Bridge [PCI0] (domain 0000 [bus 00-ff])
      [    1.221639] acpi PNP0A03:00: fail to add MMCONFIG information, can't access extended configuration space under this bridge
      [    1.233401] acpiphp: Slot [3] registered
      [    1.233715] acpiphp: Slot [4] registered
      [    1.233960] acpiphp: Slot [5] registered
      [    1.234250] acpiphp: Slot [6] registered
      [    1.236055] acpiphp: Slot [7] registered
      [    1.236325] acpiphp: Slot [8] registered
      [    1.236562] acpiphp: Slot [9] registered
      [    1.236796] acpiphp: Slot [10] registered
      [    1.237037] acpiphp: Slot [11] registered
      [    1.237332] acpiphp: Slot [12] registered
      [    1.237652] acpiphp: Slot [13] registered
      [    1.237879] acpiphp: Slot [14] registered
      [    1.238071] acpiphp: Slot [15] registered
      [    1.238301] acpiphp: Slot [16] registered
      [    1.238647] acpiphp: Slot [17] registered
      [    1.238853] acpiphp: Slot [18] registered
      [    1.239161] acpiphp: Slot [19] registered
      [    1.239630] acpiphp: Slot [20] registered
      [    1.239887] acpiphp: Slot [21] registered
      [    1.240103] acpiphp: Slot [22] registered
      [    1.240453] acpiphp: Slot [23] registered
      [    1.241076] acpiphp: Slot [24] registered
      [    1.241354] acpiphp: Slot [25] registered
      [    1.241606] acpiphp: Slot [26] registered
      [    1.241818] acpiphp: Slot [27] registered
      [    1.242036] acpiphp: Slot [28] registered
      [    1.242278] acpiphp: Slot [29] registered
      [    1.242593] acpiphp: Slot [30] registered
      [    1.242810] acpiphp: Slot [31] registered
      [    1.243263] PCI host bridge to bus 0000:00
      [    1.243727] pci_bus 0000:00: root bus resource [io  0x0000-0x0cf7 window]
      [    1.244124] pci_bus 0000:00: root bus resource [io  0x0d00-0xffff window]
      [    1.244556] pci_bus 0000:00: root bus resource [mem 0x000a0000-0x000bffff window]
      [    1.244916] pci_bus 0000:00: root bus resource [mem 0x08000000-0xfebfffff window]
      [    1.245549] pci_bus 0000:00: root bus resource [mem 0x100000000-0x17fffffff window]
      [    1.246111] pci_bus 0000:00: root bus resource [bus 00-ff]
      [    1.248196] pci 0000:00:00.0: [8086:1237] type 00 class 0x060000 conventional PCI endpoint
      [    1.252860] pci 0000:00:01.0: [8086:7000] type 00 class 0x060100 conventional PCI endpoint
      [    1.253941] pci 0000:00:01.1: [8086:7010] type 00 class 0x010180 conventional PCI endpoint
      [    1.255003] pci 0000:00:01.1: BAR 4 [io  0xc040-0xc04f]
      [    1.255337] pci 0000:00:01.1: BAR 0 [io  0x01f0-0x01f7]: legacy IDE quirk
      [    1.255592] pci 0000:00:01.1: BAR 1 [io  0x03f6]: legacy IDE quirk
      [    1.255960] pci 0000:00:01.1: BAR 2 [io  0x0170-0x0177]: legacy IDE quirk
      [    1.256593] pci 0000:00:01.1: BAR 3 [io  0x0376]: legacy IDE quirk
      [    1.257835] pci 0000:00:01.3: [8086:7113] type 00 class 0x068000 conventional PCI endpoint
      [    1.258629] pci 0000:00:01.3: quirk: [io  0x0600-0x063f] claimed by PIIX4 ACPI
      [    1.258990] pci 0000:00:01.3: quirk: [io  0x0700-0x070f] claimed by PIIX4 SMB
      [    1.260038] pci 0000:00:02.0: [1234:1111] type 00 class 0x030000 conventional PCI endpoint
      [    1.260582] pci 0000:00:02.0: BAR 0 [mem 0xfd000000-0xfdffffff pref]
      [    1.260890] pci 0000:00:02.0: BAR 2 [mem 0xfebf0000-0xfebf0fff]
      [    1.261557] pci 0000:00:02.0: ROM [mem 0xfebe0000-0xfebeffff pref]
      [    1.261984] pci 0000:00:02.0: Video device with shadowed ROM at [mem 0x000c0000-0x000dffff]
      [    1.263012] pci 0000:00:03.0: [8086:100e] type 00 class 0x020000 conventional PCI endpoint
      [    1.263880] pci 0000:00:03.0: BAR 0 [mem 0xfebc0000-0xfebdffff]
      [    1.264133] pci 0000:00:03.0: BAR 1 [io  0xc000-0xc03f]
      [    1.264553] pci 0000:00:03.0: ROM [mem 0xfeb80000-0xfebbffff pref]
      [    1.274782] ACPI: PCI: Interrupt link LNKA configured for IRQ 10
      [    1.275680] ACPI: PCI: Interrupt link LNKB configured for IRQ 10
      [    1.276370] ACPI: PCI: Interrupt link LNKC configured for IRQ 11
      [    1.276960] ACPI: PCI: Interrupt link LNKD configured for IRQ 11
      [    1.277363] ACPI: PCI: Interrupt link LNKS configured for IRQ 9
      [    1.282037] iommu: Default domain type: Translated
      [    1.282290] iommu: DMA domain TLB invalidation policy: lazy mode
      [    1.284371] SCSI subsystem initialized
      [    1.285921] ACPI: bus type USB registered
      [    1.286613] usbcore: registered new interface driver usbfs
      [    1.287107] usbcore: registered new interface driver hub
      [    1.287417] usbcore: registered new device driver usb
      [    1.288000] pps_core: LinuxPPS API ver. 1 registered
      [    1.288185] pps_core: Software ver. 5.3.6 - Copyright 2005-2007 Rodolfo Giometti <giometti@linux.it>
      [    1.288604] PTP clock support registered
      [    1.289723] EDAC MC: Ver: 3.0.0
      [    1.298958] NetLabel: Initializing
      [    1.299168] NetLabel:  domain hash size = 128
      [    1.299342] NetLabel:  protocols = UNLABELED CIPSOv4 CALIPSO
      [    1.300177] NetLabel:  unlabeled traffic allowed by default
      [    1.300422] mctp: management component transport protocol core
      [    1.300558] NET: Registered PF_MCTP protocol family
      [    1.301096] PCI: Using ACPI for IRQ routing
      [    1.301960] e820: register RAM buffer resource [mem 0x0009fc00-0x0009ffff]
      [    1.302389] e820: register RAM buffer resource [mem 0x07fe0000-0x07ffffff]
      [    1.306537] pci 0000:00:02.0: vgaarb: setting as boot VGA device
      [    1.306537] pci 0000:00:02.0: vgaarb: bridge control possible
      [    1.306537] pci 0000:00:02.0: vgaarb: VGA device added: decodes=io+mem,owns=io+mem,locks=none
      [    1.306643] vgaarb: loaded
      [    1.308872] hpet: 3 channels of 0 reserved for per-cpu timers
      [    1.309429] hpet0: at MMIO 0xfed00000, IRQs 2, 8, 0
      [    1.309769] hpet0: 3 comparators, 64-bit 100.000000 MHz counter
      [    1.315537] clocksource: Switched to clocksource tsc-early
      [    1.331307] VFS: Disk quotas dquot_6.6.0
      [    1.331841] VFS: Dquot-cache hash table entries: 512 (4096 bytes)
      [    1.336073] pnp: PnP ACPI init
      [    1.340159] pnp: PnP ACPI: found 5 devices
      [    1.364932] clocksource: acpi_pm: mask: 0xffffff max_cycles: 0xffffff, max_idle_ns: 2085701024 ns
      [    1.366885] NET: Registered PF_INET protocol family
      [    1.367953] IP idents hash table entries: 2048 (order: 2, 16384 bytes, linear)
      [    1.374412] tcp_listen_portaddr_hash hash table entries: 256 (order: 0, 4096 bytes, linear)
      [    1.374943] Table-perturb hash table entries: 65536 (order: 6, 262144 bytes, linear)
      [    1.375724] TCP established hash table entries: 512 (order: 0, 4096 bytes, linear)
      [    1.376159] TCP bind hash table entries: 512 (order: 2, 16384 bytes, linear)
      [    1.376529] TCP: Hash tables configured (established 512 bind 512)
      [    1.377947] MPTCP token hash table entries: 256 (order: 1, 6144 bytes, linear)
      [    1.378446] UDP hash table entries: 256 (order: 2, 16384 bytes, linear)
      [    1.380353] NET: Registered PF_UNIX/PF_LOCAL protocol family
      [    1.380956] NET: Registered PF_XDP protocol family
      [    1.381986] pci_bus 0000:00: resource 4 [io  0x0000-0x0cf7 window]
      [    1.382305] pci_bus 0000:00: resource 5 [io  0x0d00-0xffff window]
      [    1.382527] pci_bus 0000:00: resource 6 [mem 0x000a0000-0x000bffff window]
      [    1.382851] pci_bus 0000:00: resource 7 [mem 0x08000000-0xfebfffff window]
      [    1.383100] pci_bus 0000:00: resource 8 [mem 0x100000000-0x17fffffff window]
      [    1.383922] pci 0000:00:01.0: PIIX3: Enabling Passive Release
      [    1.384241] pci 0000:00:00.0: Limiting direct PCI/PCI transfers
      [    1.384559] PCI: CLS 0 bytes, default 64
      [    1.400219] Initialise system trusted keyrings
      [    1.402850] Key type blacklist registered
      [    1.406372] workingset: timestamp_bits=36 (anon: 31) max_order=14 bucket_order=0 (anon: 0)
      [    1.431078] integrity: Platform Keyring initialized
      [    1.431812] integrity: Machine keyring initialized
      [    1.433878] cryptd: max_cpu_qlen set to 1000
      [    1.481884] NET: Registered PF_ALG protocol family
      [    1.482300] Key type asymmetric registered
      [    1.482530] Asymmetric key parser 'x509' registered
      [    1.491218] Block layer SCSI generic (bsg) driver version 0.4 loaded (major 244)
      [    1.493356] io scheduler mq-deadline registered
      [    1.494342] io scheduler kyber registered
      [    1.494926] io scheduler bfq registered
      [    1.500288] xor: measuring software checksum speed
      [    1.504538]    prefetch64-sse  :   850 MB/sec
      [    1.507894]    sse             :  1144 MB/sec
      [    1.508430] xor: using function: sse (1144 MB/sec)
      [    1.510875] atomic64_test: passed for x86-64 platform with CX8 and with SSE
      [    1.514672] input: Power Button as /devices/platform/LNXPWRBN:00/input/input0
      [    1.515926] ACPI: button: Power Button [PWRF]
      [    1.520647] Serial: 8250/16550 driver, 32 ports, IRQ sharing enabled
      [    1.524929] 00:04: ttyS0 at I/O 0x3f8 (irq = 4, base_baud = 115200) is a 16550A
      [    1.556763] Non-volatile memory driver v1.3
      [    1.559519] ACPI: bus type drm_connector registered
      [    1.572137] scsi host0: ata_piix
      [    1.575884] scsi host1: ata_piix
      [    1.576507] ata1: PATA max MWDMA2 cmd 0x1f0 ctl 0x3f6 bmdma 0xc040 irq 14 lpm-pol 0
      [    1.577009] ata2: PATA max MWDMA2 cmd 0x170 ctl 0x376 bmdma 0xc048 irq 15 lpm-pol 0
      [    1.584395] CAN device driver interface
      [    1.587551] usbcore: registered new interface driver usbserial_generic
      [    1.588095] usbserial: USB Serial support registered for generic
      [    1.589295] i8042: PNP: PS/2 Controller [PNP0303:KBD,PNP0f13:MOU] at 0x60,0x64 irq 1,12
      [    1.592880] serio: i8042 KBD port at 0x60,0x64 irq 1
      [    1.593295] serio: i8042 AUX port at 0x60,0x64 irq 12
      [    1.595027] mousedev: PS/2 mouse device common for all mice
      [    1.598200] input: AT Translated Set 2 keyboard as /devices/platform/i8042/serio0/input/input1
      [    1.598784] rtc_cmos PNP0B00:00: RTC can wake from S4
      [    1.602862] rtc_cmos PNP0B00:00: registered as rtc0
      [    1.604956] rtc_cmos PNP0B00:00: setting system clock to 2026-11-07T18:10:36 UTC (1794075036)
      [    1.607914] rtc_cmos PNP0B00:00: alarms up to one day, y3k, 242 bytes nvram
      [    1.608654] device-mapper: core: CONFIG_IMA_DISABLE_HTABLE is disabled. Duplicate IMA measurements will not be recorded in the IMA log.
      [    1.609257] device-mapper: uevent: version 1.0.3
      [    1.610510] device-mapper: ioctl: 4.50.0-ioctl (2025-04-28) initialised: dm-devel@lists.linux.dev
      [    1.614296] hid: raw HID events driver (C) Jiri Kosina
      [    1.614978] usbcore: registered new interface driver usbhid
      [    1.615204] usbhid: USB HID core driver
      [    1.616394] drop_monitor: Initializing network drop monitor service
      [    1.618139] Initializing XFRM netlink socket
      [    1.619221] NET: Registered PF_INET6 protocol family
      [    1.628928] Segment Routing with IPv6
      [    1.629142] RPL Segment Routing with IPv6
      [    1.629550] In-situ OAM (IOAM) with IPv6
      [    1.630091] mip6: Mobile IPv6
      [    1.630455] NET: Registered PF_PACKET protocol family
      [    1.630749] can: controller area network core
      [    1.631480] NET: Registered PF_CAN protocol family
      [    1.634528] IPI shorthand broadcast: enabled
      [    1.656121] sched_clock: Marking stable (1672078700, -16462685)->(1665586847, -9970832)
      [    1.659974] registered taskstats version 1
      [    1.663513] Loading compiled-in X.509 certificates
      [    1.678289] Loaded X.509 cert 'Fedora kernel signing key: 888ad6a088753a2f992396b5fb2ecc334b7fd45d'
      [    1.736933] ata2: found unknown device (class 0)
      [    1.745007] ata2.00: ATAPI: QEMU DVD-ROM, 2.5+, max UDMA/100
      [    1.769250] scsi 1:0:0:0: CD-ROM            QEMU     QEMU DVD-ROM     2.5+ PQ: 0 ANSI: 5
      [    1.777908] Loaded X.509 cert 'Fedora IMA CA: a8a00c31663f853f9c6ff2564872e378af026b28'
      [    1.826705] Demotion targets for Node 0: null
      [    1.827174] page_owner is disabled
      [    1.829178] sr 1:0:0:0: [sr0] scsi3-mmc drive: 4x/4x cd/rw xa/form2 tray
      [    1.831273] Key type .fscrypt registered
      [    1.831456] Key type fscrypt-provisioning registered
      [    1.834343] cdrom: Uniform CD-ROM driver Revision: 3.20
      [    1.849359] sr 1:0:0:0: Attached scsi generic sg0 type 5
      [    1.850184] Btrfs loaded, zoned=yes, fsverity=yes
      [    1.852468] Key type big_key registered
      [    1.863201] Key type encrypted registered
      [    1.863791] ima: No TPM chip found, activating TPM-bypass!
      [    1.864317] Loading compiled-in module X.509 certificates
      [    1.866264] Loaded X.509 cert 'Fedora kernel signing key: 888ad6a088753a2f992396b5fb2ecc334b7fd45d'
      [    1.868093] ima: Allocated hash algorithm: sha256
      [    1.872318] ima: No architecture policies found
      [    1.873353] evm: Initialising EVM extended attributes:
      [    1.873590] evm: security.selinux
      [    1.873855] evm: security.SMACK64 (disabled)
      [    1.874027] evm: security.SMACK64EXEC (disabled)
      [    1.874251] evm: security.SMACK64TRANSMUTE (disabled)
      [    1.874525] evm: security.SMACK64MMAP (disabled)
      [    1.874789] evm: security.apparmor (disabled)
      [    1.874958] evm: security.ima
      [    1.875070] evm: security.capability
      [    1.875265] evm: HMAC attrs: 0x1
      [    1.883856] alg: No test for 842 (842-scomp)
      [    1.933829] alg: No test for mldsa65 (mldsa65-lib)
      [    1.936911] alg: No test for mldsa87 (mldsa87-lib)
      [    1.939971] alg: No test for mldsa44 (mldsa44-lib)
      [    1.948883] PM:   Magic number: 2:84:190
      [    1.955353] acpi device:1c: hash matches
      [    1.961887] RAS: Correctable Errors collector initialized.
      [    1.987260] clk: Disabling unused clocks
      [    1.992738] PM: genpd: Disabling unused power domains
      [    2.235971] random: crng init done
      [    2.266893] input: ImExPS/2 Generic Explorer Mouse as /devices/platform/i8042/serio1/input/input3
      [    2.277644] md: Waiting for all devices to be available before autodetect
      [    2.277928] md: If you don't use raid, use raid=noautodetect
      [    2.278172] md: Autodetecting RAID arrays.
      [    2.281105] md: autorun ...
      [    2.281248] md: ... autorun DONE.
      [    2.289705] /dev/root: Can't open blockdev
      [    2.292254] VFS: Cannot open root device "" or unknown-block(0,0): error -6
      [    2.292524] Please append a correct "root=" boot option; here are the available partitions:
      [    2.294780] 0b00         1048575 sr0
      [    2.294840]  driver: sr
      [    2.295131] List of all bdev filesystems:
      [    2.295319]  ext3
      [    2.295352]  ext2
      [    2.296320]  ext4
      [    2.296423]  btrfs
      [    2.296505]
      [    2.296868] Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
      [    2.297682] CPU: 0 UID: 0 PID: 1 Comm: swapper/0 Not tainted 7.2.15-200.fc44.x86_64 #1 PREEMPT(lazy)
      [    2.298080] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.17.0-10.fc44 06/10/2025
      [    2.298602] Call Trace:
      [    2.298755]  <TASK>
      [    2.299137]  dump_stack_lvl+0x5d/0x80
      [    2.299533]  vpanic+0x246/0x450
      [    2.299653]  panic+0x6b/0x70
      [    2.299767]  mount_root_generic+0x25d/0x3c0
      [    2.299940]  prepare_namespace+0x1d0/0x270
      [    2.300086]  kernel_init_freeable+0x14d/0x160
      [    2.300314]  ? __pfx_kernel_init+0x10/0x10
      [    2.300465]  kernel_init+0x1a/0x140
      [    2.300589]  ret_from_fork+0x1a1/0x270
      [    2.300723]  ? __pfx_kernel_init+0x10/0x10
      [    2.300869]  ret_from_fork_asm+0x1a/0x30
      [    2.301051]  </TASK>
      [    2.301662] Kernel Offset: 0x36200000 from 0xffffffff81000000 (relocation range: 0xffffffff80000000-0xffffffffbfffffff)
      [    2.302273] Rebooting in 1 seconds..

This is of course, due to the fact we didn't provide the kernel with any userland applications to run so there was nothing for it to do!

Initrd
------

Being a well established project that has had to support numerous use cases over the years, there appear to be many ways for you to give a Linux kernel code to run.

I've opted to follow what I think is the standard way of doing this, by providing the kernel with an `initial ramdisk <https://docs.kernel.org/admin-guide/initrd.html>`__, or initrd.

The idea behind the initrd is that you can provide the kernel with a minimal environment in which you can perform extended initialization steps (e.g. load drivers, mount file systems) before switching to the real root filesystem and booting the target system.

For the simple experiment in this post, there's no need to ever switch into a "real" root filesystem.
In fact, my initrd is going to contain a single binary ``init``.

::

   $ tree initrd/
   initrd/
   └── init

   1 directory, 1 file

Which is packed into a cpio archive to become the initial ramdisk.

.. code-block::
   :in-file: machines/useless/Makefile

   initramfs.cpio.gz: initrd/init
   {{ "\t" }}cd initrd && find . | cpio --quiet -H newc -o | gzip -9 -n > ../$@


.. admonition:: Author's Note

   I'm using `awdur <https://github.com/swyddfa/awdur>`__ to extract code blocks on this page into source files.
   The ugly ``{{ "\t" }}`` syntax is needed to insert the tab characters needed for a valid Makefile.

   At some point Soon\ :sup:`TM` I'll figure out a way to hide that implementation detail from the web version of this file! 😅


To pass the initramfs to the kernel we need to tweak our QEMU command

.. code-block::
   :in-file: machines/useless/Makefile

   .PHONY: vm
   vm: initramfs.cpio.gz
   {{ "\t" }}qemu-system-x86_64 -kernel $(KERNEL) \
                                -initrd initramfs.cpio.gz \
                                -append "console=ttyS0 root=/dev/ram0 panic=1" \
                                -nographic \
                                --no-reboot

where:

- ``-initrd initramfs.cpio.gz``: Tells qemu which archive to load into the VM
- ``root=/dev/ram0``: Tells the kernel to look for ``init`` in the initial ramdisk.

But first we actually need to write our ``init`` program!

Writing ``init``
----------------

As long you provide everything a program needs to run, technically you could implement ``init`` in any language.
However with such a minimal environment, assembly not only fits with the theme, it also clearly demonstrates how user applications interact with the kernel.

Assembly Programming
""""""""""""""""""""

There are many resources on the internet that will explain the nature of assembly much better than I can, but the following should suffice for our purposes:

- Every CPU is different, so there is no one assembly language.
  However, the CPU architecture (x86, ARM, RISC-V etc.) dictates the major conventions followed.
  My kernel is compiled for x86_64 machines, so that's the assembly I'll be using.

- CPUs provide named slots, called registers, that programs can use to store values.
  In x86_64 assembly, the "main" slots hold 64 bit values and are labelled ``rax``, ``rdi``, ``rsi``, ``rdx``.
  I don't know what the rhyme or reason is behind the register names, or even if I've listed them in the correct order! 😅

- To drastically over-simplify things, programming at this level is "just" a matter of shuffling values into and out of these registers and performing operations on them.

Syscalls & Calling Conventions
""""""""""""""""""""""""""""""

The Linux kernel provides a :bib:man:`long list <syscalls(2)>` of syscalls (i.e. functions) that a userland application can call to "make stuff happen" on the underlying machine.
These syscalls cover everything interesting, from opening files, memory allocation, network connections, to rebooting the machine.

How do applications call these functions?
Well, they use the only interface available... the CPU registers.

Let's look at the :bib:man:`write(2)` syscall as pseudo-code, note that I've not bothered to include types, since at this level everything is numbers anyway::

   WRITE = 1
   num_bytes = syscall(WRITE, fd, buf, count)

where:

- ``WRITE``, each syscall is assigned a number, on (most?) platforms, the ``write`` syscall is given the number ``1``,
- ``fd`` is the file (descriptor) to write to,
- ``buf`` is the location of the (buffer of) data to write,
- ``count`` is the size of ``buf`` in bytes,
- ``num_bytes`` is the return value from the kernel, indicating how many bytes were actually written (can be less than ``count``).

Each argument and return value is assigned a CPU register, like so::

  cpu.rax = WRITE
  cpu.rdi = fd
  cpu.rsi = &buf
  cpu.rdx = count

  syscall()

  num_byes = cpu.rax

Note that the kernel overwrites the value we placed in ``rax`` in order to tell us the number of bytes that were written.

.. admonition:: How do we know which register to use for which value?

   Each architecture uses a different mapping of arguments to register names (known as the calling convention) and it is documented on the :bib:man:`syscall(2)` man page.

   See also:

   - ``/usr/include/linux/unistd.h``: Defines the actual syscall numbers for the platform.

"Hello, World!"
"""""""""""""""

Time to put it all into practice, let's try writing a simple "Hello, World!" application in x86_64 assembly.

For our purposes, an assembly program has two sections ``.data`` and ``.text``

- ``.data`` holds any static, global data needed by the program (such as hardcoded strings).
- ``.text`` (not ``.code`` as I would've expected), holds the assembly instructions that define the program's behaviour.

.. code-block::
   :in-file: machines/useless/src/init.s

   .data
   {{ insert(slots.data) }}

   .global _start
   .text
   _start:
   {{ insert(slots.text, indent=4) }}

To start with we need to add the message we want to print to the ``.data`` section of our program

.. code-block:: asm
   :in-file: machines/useless/src/init.s
   :in-slot: data

   buf:
       .ascii "Hello, World!\n"

As we saw in the previous section, we'll need to pass the ``write`` syscall the number of bytes contained in the message.
Rather than count them ourselves, we can ask the assembler to do it.

.. code-block::
   :in-file: machines/useless/src/init.s
   :in-slot: data

   count = . - buf

Here, the ``.`` stands for the memory address of the current location, subtracting the address of the previous label (``buf``), gives us the length of the message.

Then in the ``.text`` section of the program, we need to translate our pseudo-code into actual assembly instructions.

.. code-block:: asm
   :in-file: machines/useless/src/init.s
   :at-revision: 1
   :in-slot: text

   mov rax, 1        # cpu.rax = WRITE
   mov rdi, 1        # cpu.rdi = 1 (fd)
   lea rsi, [buf]    # cpu.rsi = &buf
   lea rdx, [count]  # cpu.rdx = *count
   syscall

where:

- ``mov``, as the name suggests indicates that we want to ``mov``\ e the value into the given register.

- ``lea``, I think stands for "load equivalent address".
  We don't want to move the value of ``buf`` or ``count`` themselves into a register, but instead the value at the addresses they refer to.

  I haven't yet figured out why I need both ``lea`` and the ``[buf]`` syntax, since I thought ``[buf]`` already does the "interpret this symbol as a memory location" bit... 🤔

Technically, we should also add code to make sure that the whole message was written and that no errors have occurred, but I'll leave that as an exercise for the reader!

I'm not sure if we *have* to do this, but to be a well-behaved process we should also ask the kernel to exit with a return code of 0 to signal that our process completed successfully.

.. code-block:: asm
   :in-file: machines/useless/src/init.s
   :at-revision: 1
   :in-slot: text

   mov rax, 60       # cpu.rax = EXIT
   mov rdi, 0        # cpu.rdi = 0
   syscall

Program Assembly
""""""""""""""""

For some reason, assembly programs are "assembled", rather than "compiled" (I guess because an assembler typically translates your code as-is).

For no particular reason other than it was there, I'm using the `GNU as assmebler <https://sourceware.org/binutils/docs/as/index.html>`__.
The following Makefile rule will translate ``init.s`` file into ``init.o`` file using the ``as`` command

.. code-block::
   :in-file: machines/useless/Makefile

   src/init.o: src/init.s
   {{ "\t" }}as -msyntax=intel -mnaked-reg -o $@ $<

GNU as defaults to "AT&T" syntax, so ``-msyntax=intel`` changes the syntax to intel and ``-mnaked-reg`` removes the need to prefix registers with ``%`` characters.

Despite not needing to link with any libraries, we still need to pass our ``.o`` files through a linker so that they are converted into a valid ELF binary.

.. code-block::
   :in-file: machines/useless/Makefile

   initrd/init: src/init.o
   {{ "\t" }}[ -d initrd ] || mkdir initrd
   {{ "\t" }}ld -o $@ $^

Let's test it.

::

   $ make initrd/init
   as -msyntax=intel -mnaked-reg -o src/init.o src/init.s
   [ -d initrd ] || mkdir initrd
   ld -o initrd/init src/init.o

   $ ./initrd/init
   Hello, World!

Second boot
-----------

So ``init`` works on my machine, but the real test is if it works in the VM.

To my surprise, it **almost** worked!::

   $ make vm
   ...
   [    2.650258] x86/mm: Checked W+X mappings: passed, no W+X pages found.
   [    2.650935] Run /init as init process
   Hello, World!
   [    2.679520] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000000
   [    2.680196] CPU: 0 UID: 0 PID: 1 Comm: init Not tainted 7.2.15-200.fc44.x86_64 #1 PREEMPT(lazy)

Buried in the usual kernel output is our "Hello, World!" message, but the kernel still panics.

This is because the ``init`` program (aka PID 1) is special and is responsible for orchestrating the rest of the system.
For that reason it should never exit, otherwise the kernel is left with nothing to do again!

Press enter to continue...
--------------------------

So, instead of exiting, let's adjust the ``init`` program to shutdown the machine.
It would also be nice to have the machine wait for some input, so we have time to read the message before it powers down.

The easiest way to do that, I think, is to ask the kernel to read from the process' stdin.

.. code-block:: asm
   :in-file: machines/useless/src/init.s
   :in-slot: text
   :at-revision: 2

   mov rax, 1        # cpu.rax = WRITE
   mov rdi, 1        # cpu.rdi = 1 (fd)
   lea rsi, [buf]    # cpu.rsi = &buf
   lea rdx, [count]  # cpu.rdx = *count
   syscall

   mov rax, 0        # cpu.rax = READ
   mov rdi, 0        # cpu.rdi = 0 (fd)
   lea rsi, [buf]    # cpu.rsi = &buf
   lea rdx, [count]  # cpu.rdx = *count
   syscall

As you can see reading is very similar to writing since it accepts the same arguments, though their interpretation is slightly different:

- ``fd = 0`` says to read from the program's stdin
- ``buf`` this time is the destination to write the data to
- ``count`` the max number of bytes to read.

Of course, reading into ``buf`` corrupts our original message!
(It also shows that ``.data`` is mutable at runtime!)
We're only getting away with it since we've already printed it by this point and we're not going to use it again.

Speaking of the message, let's tweak it to inform the user what to do.

.. code-block::
   :in-file: machines/useless/src/init.s
   :in-slot: data
   :at-revision: 2

   buf:
       .ascii "Press enter to continue... "
   count = . - buf

Finally, to shutdown the machine we need to... :bib:man:`reboot(2)` it 😅.

Reading the man page this syscall does a lot!
It's used to `kexec <https://wiki.archlinux.org/title/Kexec>`__ into a new kernel, enable/disable :kbd:`Ctrl+Alt+Delete`, shutdown the machine, and yes... it can also reboot it.

.. code-block:: asm
   :in-file: machines/useless/src/init.s
   :in-slot: text
   :at-revision: 2

   mov rax, 169          # cpu.rax = REBOOT
   mov rdi, 0xfee1dead   # cpu.rdi = LINUX_REBOOT_MAGIC1
   mov rsi, 0x28121969   # cpu.rsi = LINUX_REBOOT_MAGIC2
   mov rdx, 0x4321fedc   # cpu.rdx = LINUX_REBOOT_CMD_POWER_OFF
   syscall

As you can see, to call the ``reboot`` syscall correctly you need to pass it some "magic" numbers in addition to the number that actually represents the command you wish to perform.
I don't really know why... perhaps it's a guard against a bug in your code leading to an unexpected shutdown? 🤔

Final boot
----------

Anyway, with the updated ``init`` program written, all that's left is to try it out!::

   $ make vm
   ...
   [    2.585771] Run /init as init process
   Press enter to continue...
   [    6.798351] ACPI: PM: Preparing to enter system sleep state S5
   [    6.800230] reboot: Power down

Success! No kernel panics in sight!

Now what?
---------

Now that we have a functioning (yet, entirely useless) userland environment the obvious question is what to do next?
With the fundamentals covered we're firmly in `draw the rest of the owl <https://knowyourmeme.com/memes/how-to-draw-an-owl>`__ territory.

We could start trying to mount a disk and doing some file I/O, or making a network request, or drawing some graphics?
But to support those endeavours, you're likely going to need to know how to allocate memory, spawn processes and take user input.
And while it could be its own brand of Fun\ :sup:`TM` to write all of in assembly, having access to a higher level language would likely make the whole experience much more pleasant.

So umm, yeah, I'm currently just sat here asking myself - Now what? 😅
