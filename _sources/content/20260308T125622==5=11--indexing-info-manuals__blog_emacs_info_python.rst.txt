:title: Indexing Info Manuals
:date: 2026-03-09
:tags: blog, emacs, info, python
:identifier: 20260308T125622
:signature: 5=11

Indexing Info Manuals
=====================

.. highlight:: none

.. container:: post-teaser

   I've been working around this issue for a while now.

   By default, the :kbd:`C-h i` binding in Emacs opens the list of available
   `info manuals <https://en.wikipedia.org/wiki/Info_(Unix)>`__ for you to browse through.
   Unfortunately, I would only be shown manuals that had been included with third-party Emacs packages like
   `denote <https://protesilaos.com/emacs/denote>`__.
   System provided manuals, such as the one for Emacs itself, were nowhere to be seen::

      File: dir,	Node: Top	This is the top of the INFO tree

        This (the Directory node) gives a menu of major topics.
        Typing "q" exits, "H" lists all Info commands, "d" returns here,
        "h" gives a primer for first-timers,
        "mEmacs<Return>" visits the Emacs manual, etc.

        In Emacs, you can click mouse button 2 on a menu item or cross reference
        to select it.

      * Menu:

      Emacs
      * Denote Sequence: (denote-sequence).
                                      Sequence notes or Folgezettel with Denote.
      * Denote: (denote).             Simple notes with an efficient file-naming
                                        scheme.
      * Eat: (eat).                   Emulate A Terminal.
      * Embark: (embark).             Emacs Mini-Buffer Actions Rooted in Keymaps.
      * Forge: (forge).               Access Git Forges from Magit.
      * Ghub: (ghub).                 Client library for the Github API.
      * Magit: (magit).               Using Git from Emacs with Magit.
      * Magit-Section: (magit-section).
                                      Use Magit sections in your own packages.
      * Orderless: (orderless).       Completion style for matching regexps in any
                                        order.
      * Tempel: (tempel).             Simple templates for Emacs.
      * Transient: (transient).       Transient Commands.
      * With-Editor: (with-editor).   Using the Emacsclient as $EDITOR.


   However, I could clearly see files like ``/usr/share/info/emacs.info.gz`` on my system and I could access specific info nodes by evaluating expressions like ``(info "(emacs)Displaying Buffers")``.

   I've now reached the point where it's bugging me enough to actually dig in and try to figure out what is going on.

``dir`` files
-------------

It turns out that the buffer you see when invoking :kbd:`C-h i` is assembled from all the places Emacs is configured to search for info manuals (via the ``Info-directory-list`` variable).
Each directory is expected to contain a file called ``dir`` that would provide a list of all info manuals in the directory.
For example in the ``denote`` package::

  ~/.emacs.d/elpa/denote-4.1.3/ $ cat ./dir

  This is the file .../info/dir, which contains the
  topmost node of the Info hierarchy, called (dir)Top.
  The first time you invoke Info you start off looking at this node.
  
  File: dir,	Node: Top	This is the top of the INFO tree

    This (the Directory node) gives a menu of major topics.
    Typing "q" exits, "H" lists all Info commands, "d" returns here,
    "h" gives a primer for first-timers,
    "mEmacs<Return>" visits the Emacs manual, etc.

    In Emacs, you can click mouse button 2 on a menu item or cross reference
    to select it.

  * Menu:

  Emacs misc features
  * Denote: (denote).             Simple notes with an efficient file-naming
                                    scheme.

where ``(denote).`` instructs Emacs to look for a file called ``denote.info``.

Armed with this knowledge, you would expect to find a similar file in ``/usr/share/info``, but unsurprsingly, it's missing in my case.
The obvious solution then, would be to ensure that a ``dir`` file is present in the ``/usr/share/info`` directory however, my Linux flavour of choice (`Aurora <https://getaurora.dev/en/>`__) makes this a bit more interesting::

  $ touch /usr/share/info/dir
  touch: cannot touch '/usr/share/info/dir': Read-only file system

Interestingly however, this didn't turn out to be a big deal as manually editing the ``dir`` file provided by denote I proved to myself that you didn't actually need the ``.info`` file to be in the same folder as the ``dir`` file, as long as it was *somewhere* listed in ``Info-directory-list``

.. code-block:: diff

    * Menu:

    Emacs misc features
  + * Emacs: (emacs).               The Emacs manual.
    * Denote: (denote).             Simple notes with an efficient file-naming
                                    scheme.

Now all that's left is to build a ``dir`` file indexing all the missing manuals.


.. note::

   The "correct" way to do this is is to use the
   `install-info <https://www.gnu.org/software/texinfo/manual/texinfo/html_node/Invoking-install_002dinfo.html>`__
   command from the
   `texinfo <https://www.gnu.org/software/texinfo/>`__ project.

   But since I don't have the ``texinfo`` package installed I thought it would be fun to write a small Python script to do the same.


``build-info-dir.py``
---------------------

.. code-block:: python
   :project: build-info-dir
   :filename: build-info-dir.py

   """build-info-dir.py <directory> <output>

   Index all info manuals in a given directory and produce a ``dir`` index file.
   """
   import argparse
   import gzip
   import pathlib
   import sys

As we can see from the examples above, the format of a ``dir`` file is quite straightforward, the hardest part is figuring out the title and description of each manual along with which sections to group them under.

The `texinfo documentation <https://www.gnu.org/software/texinfo/manual/texinfo/html_node/Installing-Dir-Entries.html>`__ states that manuals export specific info nodes to the top-level ``dir`` using the following syntax (example taken from the info file for ``denote``)::

  INFO-DIR-SECTION Emacs misc features
  START-INFO-DIR-ENTRY
  * Denote: (denote).     Simple notes with an efficient file-naming scheme.
  END-INFO-DIR-ENTRY

Which can be extracted as follows:

.. code-block:: python
   :project: build-info-dir
   :filename: build-info-dir.py

   DIR_SECTION = "INFO-DIR-SECTION "

   def extract_dir_nodes(filename: pathlib.Path) -> dict[str, list[str]]:
       nodes: dict[str, list[str]] = {}

       section: str = ""
       entry: list[str] | None = None

       with open_info_file(filename) as f:
           for line in f.readlines():
               text = line.decode(errors="ignore").rstrip()
               if text.startswith(DIR_SECTION):
                   section = text.replace(DIR_SECTION, "")
                   continue

               elif text == "START-INFO-DIR-ENTRY":
                   entry = []
                   continue

               elif text == "END-INFO-DIR-ENTRY":
                   nodes.setdefault(section, []).extend(entry)
                   entry = None

               elif isinstance(entry, list):
                   entry.append(text)

       return nodes

``open_info_file`` is a separate helper function as info manuals can be gzipped.

.. code-block:: python
   :project: build-info-dir
   :filename: build-info-dir.py

   def open_info_file(filename: pathlib.Path):
       if ".gz" in filename.suffix:
           return gzip.open(filename)

       return filename.open()

All that's left is the infrastructure to find and aggregate the result of each info file.

.. code-block:: python
   :project: build-info-dir
   :filename: build-info-dir.py

   def index_info_dir(info_dir: pathlib.Path) -> str:
       nodes: dict[str, list[str]] = {}

       for filename in info_dir.glob("*.info*"):
           # Some manuals are split into mutliple files, we only need to index the top-level file
           if "info-" in filename.name:
               continue

           print(f"Indexing {filename.name}...", file=sys.stderr)
           index = extract_dir_nodes(filename)
           for section, items in index.items():
               nodes.setdefault(section, []).extend(items)

       lines = [
           chr(0x1f),
           "File: dir\tNode: Top\tThis is the top of the INFO tree",
           "",
           "* Menu:",
           ""
       ]

       for section, items in nodes.items():
           lines.append(section)
           lines.extend(items)

       return "\n".join(lines)

After **much** trial and error, I eventually figured out that the ``dir`` file **must** contain

- the special character ``"\x1f"`` (rendered as ``^_`` by Emacs),
- the ``File: dir...`` header and
- the ``* Menu:`` string

in order to be parsed correctly.

Other than that, it appears like you can add any other text you'd like and it would be rendered in the final ``*info*`` buffer.
I was tempted to add a count of all the manuals found, but since the file we're generating here isn't the only source, any counts are unlikely to be accurate.

Finally, to make the script useful let's wrap it in a simple CLI interface.

.. code-block:: python
   :project: build-info-dir
   :filename: build-info-dir.py

   def main():
       cli = argparse.ArgumentParser()
       cli.add_argument("infodir", type=pathlib.Path)
       cli.add_argument("-o", "--output", type=argparse.FileType("w"), default="-")

       args = cli.parse_args()
       content = index_info_dir(args.infodir)
       print(content, file=args.output)


   if __name__ == "__main__":
       main()

Building and Using the Index
----------------------------

To get Emacs to use the the index, we of course have to generate it::

  $ mkdir -p ~/.local/share/info
  $ python build-info-dir.py /usr/share/info -o ~/.local/share/info/dir
  ...
  Indexing url.info.gz...
  Indexing use-package.info.gz...
  Indexing vhdl-mode.info.gz...
  Indexing vip.info.gz...
  Indexing viper.info.gz...
  Indexing vtable.info.gz...
  Indexing widget.info.gz...
  Indexing wisent.info.gz...
  Indexing woman.info.gz...

And make sure Emacs is configured to search the folder

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (add-to-list 'Info-directory-list
                (concat (getenv "HOME") "/.local/share/info/"))


Success!

.. raw:: html

   <style>
     #info-dir { max-height: 350px; overflow: scroll; }
   </style>

.. code-block::
   :name: info-dir

   File: dir	Node: Top	This is the top of the INFO tree

   * Menu:

   Software development
   * As: (as).                     The GNU assembler.
   * Gas: (as).                    The GNU assembler.
   * Bfd: (bfd).                   The Binary File Descriptor library.
   * Binutils: (binutils).         The GNU binary utilities.
   * bison: (bison).       GNU parser generator (Yacc replacement).
   * Cpp: (cpp).                  The GNU C preprocessor.
   * Cpplib: (cppinternals).      Cpplib internals.
   * CTF: (ctf-spec).         The CTF file format.
   * gcc: (gcc).                  The GNU Compiler Collection.
   * g++: (gcc).                  The GNU C++ compiler.
   * gcov: (gcc) Gcov.            ‘gcov’--a test coverage program.
   * gcov-tool: (gcc) Gcov-tool.  ‘gcov-tool’--an offline gcda profile processing program.
   * gcov-dump: (gcc) Gcov-dump.  ‘gcov-dump’--an offline gcda and gcno profile dump tool.
   * lto-dump: (gcc) lto-dump.    ‘lto-dump’--Tool for
   * flex: (flex).      Fast lexical analyzer generator (lex replacement).
   dumping LTO object files.
   * Gccgo: (gccgo).           A GCC-based compiler for the Go language
   * gccinstall: (gccinstall).    Installing the GNU Compiler Collection.
   * gccint: (gccint).            Internals of the GNU Compiler Collection.
   * GNUstep Make: (gnustep-make).         The GNUstep build system.
   * gprof: (gprof).                Profiling your program's execution
   * Ld: (ld).                       The GNU linker.
   * Ld-Internals: (ldint).	The GNU linker internals.
   * Make: (make).            Remake files automatically.
   * SFrame: (sframe-spec).         The Simple Frame format.
   Basics
   * Bash: (bash).                     The GNU Bourne-Again SHell.
   * Coreutils: (coreutils).       Core GNU (file, text, shell) utilities.
   * Common options: (coreutils)Common options.
   * File permissions: (coreutils)File permissions.  Access modes.
   * Date input formats: (coreutils)Date input formats.
   * Ed: (ed).                     The GNU line editor
   * Finding files: (find).        Operating on files matching certain criteria.
   * Time: (time).                  GNU time utility.
   Math
   * bc: (bc).                    An arbitrary precision calculator language.
   Individual utilities
   * addr2line: (binutils)addr2line. Convert addresses to file and line.
   * ar: (binutils)ar.               Create, modify, and extract from archives.
   * c++filt: (binutils)c++filt.	  Filter to demangle encoded C++ symbols.
   * cxxfilt: (binutils)c++filt.     MS-DOS name for c++filt.
   * dlltool: (binutils)dlltool.	  Create files needed to build and use DLLs.
   * nm: (binutils)nm.               List symbols from object files.
   * objcopy: (binutils)objcopy.	  Copy and translate object files.
   * objdump: (binutils)objdump.     Display information from object files.
   * ranlib: (binutils)ranlib.       Generate index to archive contents.
   * readelf: (binutils)readelf.	  Display the contents of ELF format files.
   * size: (binutils)size.           List section sizes and total size.
   * strings: (binutils)strings.     List printable strings from files.
   * strip: (binutils)strip.         Discard symbols.
   * elfedit: (binutils)elfedit.     Update ELF header and property of ELF files.
   * windmc: (binutils)windmc.	  Generator for Windows message resources.
   * windres: (binutils)windres.	  Manipulate Windows resources.
   * arch: (coreutils)arch invocation.             Print machine hardware name.
   * b2sum: (coreutils)b2sum invocation.           Print or check BLAKE2 digests.
   * base32: (coreutils)base32 invocation.         Base32 encode/decode data.
   * base64: (coreutils)base64 invocation.         Base64 encode/decode data.
   * basename: (coreutils)basename invocation.     Strip directory and suffix.
   * basenc: (coreutils)basenc invocation.         Encoding/decoding of data.
   * cat: (coreutils)cat invocation.               Concatenate and write files.
   * chcon: (coreutils)chcon invocation.           Change SELinux CTX of files.
   * chgrp: (coreutils)chgrp invocation.           Change file groups.
   * chmod: (coreutils)chmod invocation.           Change access permissions.
   * chown: (coreutils)chown invocation.           Change file owners and groups.
   * chroot: (coreutils)chroot invocation.         Specify the root directory.
   * cksum: (coreutils)cksum invocation.           Print POSIX CRC checksum.
   * comm: (coreutils)comm invocation.             Compare sorted files by line.
   * cp: (coreutils)cp invocation.                 Copy files.
   * csplit: (coreutils)csplit invocation.         Split by context.
   * cut: (coreutils)cut invocation.               Print selected parts of lines.
   * date: (coreutils)date invocation.             Print/set system date and time.
   * dd: (coreutils)dd invocation.                 Copy and convert a file.
   * df: (coreutils)df invocation.                 Report file system usage.
   * dir: (coreutils)dir invocation.               List directories briefly.
   * dircolors: (coreutils)dircolors invocation.   Color setup for ls.
   * dirname: (coreutils)dirname invocation.       Strip last file name component.
   * du: (coreutils)du invocation.                 Report file usage.
   * echo: (coreutils)echo invocation.             Print a line of text.
   * env: (coreutils)env invocation.               Modify the environment.
   * expand: (coreutils)expand invocation.         Convert tabs to spaces.
   * expr: (coreutils)expr invocation.             Evaluate expressions.
   * factor: (coreutils)factor invocation.         Print prime factors
   * false: (coreutils)false invocation.           Do nothing, unsuccessfully.
   * fmt: (coreutils)fmt invocation.               Reformat paragraph text.
   * fold: (coreutils)fold invocation.             Wrap long input lines.
   * groups: (coreutils)groups invocation.         Print group names a user is in.
   * head: (coreutils)head invocation.             Output the first part of files.
   * hostid: (coreutils)hostid invocation.         Print numeric host identifier.
   * hostname: (coreutils)hostname invocation.     Print or set system name.
   * id: (coreutils)id invocation.                 Print user identity.
   * install: (coreutils)install invocation.       Copy files and set attributes.
   * join: (coreutils)join invocation.             Join lines on a common field.
   * kill: (coreutils)kill invocation.             Send a signal to processes.
   * link: (coreutils)link invocation.             Make hard links between files.
   * ln: (coreutils)ln invocation.                 Make links between files.
   * logname: (coreutils)logname invocation.       Print current login name.
   * ls: (coreutils)ls invocation.                 List directory contents.
   * md5sum: (coreutils)md5sum invocation.         Print or check MD5 digests.
   * mkdir: (coreutils)mkdir invocation.           Create directories.
   * mkfifo: (coreutils)mkfifo invocation.         Create FIFOs (named pipes).
   * mknod: (coreutils)mknod invocation.           Create special files.
   * mktemp: (coreutils)mktemp invocation.         Create temporary files.
   * mv: (coreutils)mv invocation.                 Rename files.
   * nice: (coreutils)nice invocation.             Modify niceness.
   * nl: (coreutils)nl invocation.                 Number lines and write files.
   * nohup: (coreutils)nohup invocation.           Immunize to hangups.
   * nproc: (coreutils)nproc invocation.           Print the number of processors.
   * numfmt: (coreutils)numfmt invocation.         Reformat numbers.
   * od: (coreutils)od invocation.                 Dump files in octal, etc.
   * paste: (coreutils)paste invocation.           Merge lines of files.
   * pathchk: (coreutils)pathchk invocation.       Check file name portability.
   * pinky: (coreutils)pinky invocation.           Print information about users.
   * pr: (coreutils)pr invocation.                 Paginate or columnate files.
   * printenv: (coreutils)printenv invocation.     Print environment variables.
   * printf: (coreutils)printf invocation.         Format and print data.
   * ptx: (coreutils)ptx invocation.               Produce permuted indexes.
   * pwd: (coreutils)pwd invocation.               Print working directory.
   * readlink: (coreutils)readlink invocation.     Print referent of a symlink.
   * realpath: (coreutils)realpath invocation.     Print resolved file names.
   * rm: (coreutils)rm invocation.                 Remove files.
   * rmdir: (coreutils)rmdir invocation.           Remove empty directories.
   * runcon: (coreutils)runcon invocation.         Run in specified SELinux CTX.
   * seq: (coreutils)seq invocation.               Print numeric sequences
   * sha1sum: (coreutils)sha1sum invocation.       Print or check SHA-1 digests.
   * sha2: (coreutils)sha2 utilities.              Print or check SHA-2 digests.
   * shred: (coreutils)shred invocation.           Remove files more securely.
   * shuf: (coreutils)shuf invocation.             Shuffling text files.
   * sleep: (coreutils)sleep invocation.           Delay for a specified time.
   * sort: (coreutils)sort invocation.             Sort text files.
   * split: (coreutils)split invocation.           Split into pieces.
   * stat: (coreutils)stat invocation.             Report file(system) status.
   * stdbuf: (coreutils)stdbuf invocation.         Modify stdio buffering.
   * stty: (coreutils)stty invocation.             Print/change terminal settings.
   * sum: (coreutils)sum invocation.               Print traditional checksum.
   * sync: (coreutils)sync invocation.             Sync files to stable storage.
   * tac: (coreutils)tac invocation.               Reverse files.
   * tail: (coreutils)tail invocation.             Output the last part of files.
   * tee: (coreutils)tee invocation.               Redirect to multiple files.
   * test: (coreutils)test invocation.             File/string tests.
   * timeout: (coreutils)timeout invocation.       Run with time limit.
   * touch: (coreutils)touch invocation.           Change file timestamps.
   * tr: (coreutils)tr invocation.                 Translate characters.
   * true: (coreutils)true invocation.             Do nothing, successfully.
   * truncate: (coreutils)truncate invocation.     Shrink/extend size of a file.
   * tsort: (coreutils)tsort invocation.           Topological sort.
   * tty: (coreutils)tty invocation.               Print terminal name.
   * uname: (coreutils)uname invocation.           Print system information.
   * unexpand: (coreutils)unexpand invocation.     Convert spaces to tabs.
   * uniq: (coreutils)uniq invocation.             Uniquify files.
   * unlink: (coreutils)unlink invocation.         Removal via unlink(2).
   * uptime: (coreutils)uptime invocation.         Print uptime and load.
   * users: (coreutils)users invocation.           Print current user names.
   * vdir: (coreutils)vdir invocation.             List directories verbosely.
   * wc: (coreutils)wc invocation.                 Line, word, and byte counts.
   * who: (coreutils)who invocation.               Print who is logged in.
   * whoami: (coreutils)whoami invocation.         Print effective user ID.
   * yes: (coreutils)yes invocation.               Print a string indefinitely.
   * cmp: (diffutils)Invoking cmp.                 Compare 2 files byte by byte.
   * diff: (diffutils)Invoking diff.               Compare 2 files line by line.
   * diff3: (diffutils)Invoking diff3.             Compare 3 files line by line.
   * patch: (diffutils)Invoking patch.             Apply a patch to a file.
   * sdiff: (diffutils)Invoking sdiff.             Merge 2 files side-by-side.
   * find: (find)Finding Files.                    Finding and acting on files.
   * locate: (find)Invoking locate.                Finding files in a database.
   * updatedb: (find)Invoking updatedb.            Building the locate database.
   * xargs: (find)Invoking xargs.                  Operating on many files.
   * awk: (gawk)Invoking Gawk.                     Text scanning and processing.
   * Gawk Work Flow: (gawkworkflow)Overview.         Participating in ‘gawk’ development.
   * gunzip: (gzip)Overview.                       Decompression.
   * gzexe: (gzip)Overview.                        Compress executables.
   * zcat: (gzip)Overview.                         Decompression to stdout.
   * zdiff: (gzip)Overview.                        Compare compressed files.
   * zforce: (gzip)Overview.                       Force .gz extension on files.
   * zgrep: (gzip)Overview.                        Search compressed files.
   * zmore: (gzip)Overview.                        Decompression output by pages.
   * tar: (tar)tar invocation.                     Invoking GNU ‘tar’.
   Archiving
   * Cpio: (cpio).                 Copy-in-copy-out archiver to tape or disk.
   * Tar: (tar).                   Making tape (or disk) archives.
   * Xorrecord: (xorrecord).           Emulates CD/DVD/BD program cdrecord
   * Xorriso-dd-target: (xorriso-dd-target). Device evaluator and disk image copier for GNU/Linux
   * Xorriso: (xorriso).           Burns ISO 9660 on CD, DVD, BD.
   * Xorrisofs: (xorrisofs).           Emulates ISO 9660 program mkisofs

   * dc: (dc).                   Arbitrary precision RPN "Desktop Calculator".
   Text creation and manipulation
   * Diffutils: (diffutils).       Comparing and merging files.
   * Gawk: (gawk).                 A text scanning and processing language.
   * Gawk Work Flow: (gawkworkflow).                 Participating in ‘gawk’ development.
   * grep: (grep).                 Print lines that match patterns.
   * M4: (m4).                     A powerful macro processor.
   * pm-gawk: (pm-gawk).    Persistent memory version of gawk.
   * sed: (sed).                   Stream EDitor.

   GNU organization
   * Maintaining Findutils: (find-maint).        Maintaining GNU findutils
   Network applications
   * awkinet: (gawkinet).          TCP/IP Internetworking With 'gawk'.
   GNU Gettext Utilities
   * gettext: (gettext).                          GNU gettext utilities.
   * autopoint: (gettext)autopoint Invocation.    Copy gettext infrastructure.
   * envsubst: (gettext)envsubst Invocation.      Expand environment variables.
   * gettextize: (gettext)gettextize Invocation.  Prepare a package for gettext.
   * msgattrib: (gettext)msgattrib Invocation.    Select part of a PO file.
   * msgcat: (gettext)msgcat Invocation.          Combine several PO files.
   * msgcmp: (gettext)msgcmp Invocation.          Compare a PO file and template.
   * msgcomm: (gettext)msgcomm Invocation.        Match two PO files.
   * msgconv: (gettext)msgconv Invocation.        Convert PO file to encoding.
   * msgen: (gettext)msgen Invocation.            Create an English PO file.
   * msgexec: (gettext)msgexec Invocation.        Process a PO file.
   * msgfilter: (gettext)msgfilter Invocation.    Pipe a PO file through a filter.
   * msgfmt: (gettext)msgfmt Invocation.          Make MO files out of PO files.
   * msggrep: (gettext)msggrep Invocation.        Select part of a PO file.
   * msginit: (gettext)msginit Invocation.        Create a fresh PO file.
   * msgmerge: (gettext)msgmerge Invocation.      Update a PO file from template.
   * msgunfmt: (gettext)msgunfmt Invocation.      Uncompile MO file into PO file.
   * msguniq: (gettext)msguniq Invocation.        Unify duplicates for PO file.
   * ngettext: (gettext)ngettext Invocation.      Translate a message with plural.
   * xgettext: (gettext)xgettext Invocation.      Extract strings into a PO file.
   * ISO639: (gettext)Language Codes.             ISO 639 language codes.
   * ISO3166: (gettext)Country Codes.             ISO 3166 country codes.
   GNU Utilities
   * gpg2: (gnupg).           OpenPGP encryption and signing tool.
   * gpgsm: (gnupg).          S/MIME encryption and signing tool.
   * gpg-agent: (gnupg).      The secret key daemon.
   * dirmngr: (gnupg).        X.509 CRL and OCSP server.
   * dirmngr-client: (gnupg). X.509 CRL and OCSP client.
   * pinentry: (pinentry).    Securely ask for a passphrase or PIN.
   Kernel
   * grub2-dev: (grub2-dev).                 The GRand Unified Bootloader Dev
   * GRUB2: (grub2).                 The GRand Unified Bootloader
   * grub2-install: (grub2)Invoking grub2-install.    Install GRUB on your drive
   * grub2-mkconfig: (grub2)Invoking grub2-mkconfig.  Generate GRUB configuration
   * grub2-mkpasswd-pbkdf2: (grub2)Invoking grub2-mkpasswd-pbkdf2.
   * grub2-mkrelpath: (grub2)Invoking grub2-mkrelpath.
   * grub2-mkrescue: (grub2)Invoking grub2-mkrescue.  Make a GRUB rescue image
   * grub2-mount: (grub2)Invoking grub2-mount.        Mount a file system using GRUB
   * grub2-probe: (grub2)Invoking grub2-probe.        Probe device information
   * grub2-script-check: (grub2)Invoking grub2-script-check.
   Compression
   * Gzip: (gzip).                 General (de)compression of files (lzw).
   Libraries
   * History: (history).       The GNU history library API.
   * RLuserman: (rluserman).       The GNU readline library User's Manual.
   * libcdio: (libcdio).           GNU Compact Disc Input, Output, and Control Library.
   * libgomp: (libgomp).          GNU Offloading and Multi Processing Runtime Library.
   * Source-highlight-lib: (source-highlight-lib).  Highlights contents
   * Auth-source: (auth).          The Emacs auth-source library.
   * CL-Lib: (cl).                 Partial Common Lisp support for Emacs Lisp.
   * D-Bus: (dbus).                Using D-Bus in Emacs.
   * Emacs MIME: (emacs-mime).     Emacs MIME de/composition library.
   * SMTP: (smtpmail).             Emacs library for sending mail via SMTP.
   * URL: (url).                   URL loading package.
   * Widget: (widget).             The "widget" package used by the Emacs
                                     Customization facility.
   Localization
   * libchewing: (libchewing).           The libchewing reference manual.
   Misc
   * Liblouis: (liblouis). A braille translator and back-translator
   DOS
   * Mtools: (mtools).        Mtools: utilities to access DOS disks in Unix.
   Editors
   * nano: (nano).                 Small and friendly text editor.
   Encryption
   * Nettle: (nettle).             A low-level cryptographic library.
   System administration
   * parted: (parted).                         GNU partitioning software
   * Which: (which).                               Show full path of commands.
   Texinfo documentation system
   * Pinfo: (pinfo).           curses based lynx-style info browser.
   Utilities
   * Source-highlight: (source-highlight).  Highlights contents
   * ZSH: (zsh).                     The Z Shell Manual.
   Emacs
   * Autotype: (autotype).         Convenient features for text that you enter
                                     frequently in Emacs.
   * Bovine: (bovine).             Semantic bovine parser development.
   * Calc: (calc).                 Advanced desk calculator and mathematical tool.
   * Dired-X: (dired-x).           Dired Extra Features.
   * Ebrowse: (ebrowse).           A C++ class browser for Emacs.
   * EDE: (ede).                   The Emacs Development Environment.
   * Ediff: (ediff).               A visual interface for comparing and
                                     merging programs.
   * EDT: (edt).                   An Emacs emulation of the EDT editor.
   * Eglot: (eglot).             Language Server Protocol client for Emacs.
   * EIEIO: (eieio).               An objects system for Emacs Lisp.
   * EasyPG Assistant: (epa).      An Emacs user interface to GNU Privacy Guard.
   * ERT: (ert).                   Emacs Lisp regression testing tool.
   * Eshell: (eshell).             A command shell implemented in Emacs Lisp.
   * EWW: (eww).      Emacs Web Wowser
   * Flymake: (flymake).           A universal on-the-fly syntax checker.
   * Forms: (forms).               Emacs package for editing data bases
                                     by filling in forms.
   * Htmlfontify: (htmlfontify).   Convert source code to html.
   * Ido: (ido).                   Interactively do things with buffers and files.
   * Modus Themes: (modus-themes). Elegant, highly legible and customizable themes.
   * PCL-CVS: (pcl-cvs).           Emacs front-end to CVS.
   * RefTeX: (reftex).             Emacs support for LaTeX cross-references
                                     and citations.
   * Remember: (remember).         Simple information manager for Emacs.
   * Semantic: (semantic).         Source code parser library and utilities.
   * SES: (ses).                   Simple Emacs Spreadsheet.
   * Speedbar: (speedbar).         File/Tag summarizing utility.
   * SRecode: (srecode).           Semantic template code generator.
   * Todo Mode: (todo-mode).       Make and maintain todo lists.
   * Transient: (transient).       Transient Commands.
   * use-package: (use-package). Declarative package configuration for Emacs.
   * VIP: (vip).                   An obsolete VI-emulation for Emacs.
   * VIPER: (viper).               A VI-emulation mode for Emacs.
   * vtable: (vtable).     Variable Pitch Tables.
   * Wisent: (wisent).             Semantic Wisent parser development.
   * WoMan: (woman).               Browse UN*X Manual Pages "W.O. (without) Man".
   * CC Mode: (ccmode).            Emacs mode for editing C, C++, Objective-C,
                                     Java, Pike, AWK, and CORBA IDL code.
   * IDLWAVE: (idlwave).           Major mode and shell for IDL files.
   * nXML Mode: (nxml-mode).       XML editing mode with RELAX NG support.
   * Octave mode: (octave-mode).   Emacs mode for editing GNU Octave files.
   * Org Mode: (org).      Outline-based notes management and organizer.
   * VHDL Mode: (vhdl-mode).       Emacs mode for editing VHDL code.
   * Emacs FAQ: (efaq).            Frequently Asked Questions about Emacs.
   * Emacs: (emacs).               The extensible self-documenting text editor.
   * Emacs Lisp Intro: (eintr).    A simple introduction to Emacs Lisp programming.
   * Elisp: (elisp).               The Emacs Lisp Reference Manual.
   * Emacs GnuTLS: (emacs-gnutls). The Emacs GnuTLS integration.
   * ERC: (erc).                   Powerful and extensible IRC client for Emacs.
   * EUDC: (eudc).                 Emacs client for directory servers (LDAP, BBDB).
   * Gnus: (gnus).                 The newsreader Gnus.
   * Mairix: (mairix-el).          Emacs interface to the Mairix mail indexer.
   * Message: (message).           Mail and news composition mode that
                                     goes with Gnus.
   * MH-E: (mh-e).                 Emacs interface to the MH mail system.
   * Newsticker: (newsticker).     A feed reader for Emacs.
   * PGG: (pgg).                   An obsolete Emacs interface to various
                                     PGP implementations.
   * Rcirc: (rcirc).               Internet Relay Chat (IRC) client.
   * SASL: (sasl).                 The Emacs SASL library.
   * SC: (sc).                     Supercite lets you cite parts of messages
                                     you're replying to, in flexible ways.
   * Sieve: (sieve).               Managing Sieve scripts in Emacs.
   * Tramp: (tramp).               Transparent Remote Access, Multiple Protocol
                                     Emacs remote file access via ssh and scp.
   * Denote Sequence: (denote-sequence).
                                   Sequence notes or Folgezettel with Denote.
   * Denote: (denote).             Simple notes with an efficient file-naming
                                     scheme.
   * Eat: (eat).                   Emulate A Terminal.
   * Embark: (embark).             Emacs Mini-Buffer Actions Rooted in Keymaps.
   * Forge: (forge).               Access Git Forges from Magit.
   * Ghub: (ghub).                 Client library for the Github API.
   * Magit: (magit).               Using Git from Emacs with Magit.
   * Magit-Section: (magit-section).
                                   Use Magit sections in your own packages.
   * Orderless: (orderless).       Completion style for matching regexps in any
                                     order.
   * Tempel: (tempel).             Simple templates for Emacs.
   * With-Editor: (with-editor).   Using the Emacsclient as $EDITOR.
