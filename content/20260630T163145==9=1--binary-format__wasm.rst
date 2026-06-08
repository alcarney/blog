:title: WASM Dump
:date: 2026-06-30
:tags: wasm
:identifier: 20260630T163145
:signature: 9=1

WASM Binary Format
==================

.. highlight:: none

After years of thinking *I really should play with WebAssembly more* I thought it was time I actually did something about it.

Needing somewhere to start, why don't I try building a hexdump-style tool allowing me to peek inside a compiled wasm module?
I'm aware that there are many tools already out there for this sort of thing, but I think the best way to learn is to have a go at building things myself.
Besides, with plenty of other tools available, it will be easy to check my work!

Since learning WebAssembly own it's own is not enough, why don't I try writing this in Common Lisp as well? 😅

Dumping Bytes
-------------

The first step is just to figure out reading a file into memory, and printing out the bytes as we go, should be simple enough right?

.. code-block:: lisp

   CL-USER> (with-open-file (in "~/data.txt" :element-type '(unsigned-byte 8))
              (do ((byte (read-byte in nil nil)   ; initialize `byte` by reading the first byte from the file.
                         (read-byte in nil nil))) ; on each iteration, read next byte from the stream.
                  ((null byte)) ; do until `byte` is `nil`
                (format t "~x" byte))) ; print the value of byte as a hexadecial.
   48656C6C6F2C20576F726C6421
   NIL

Nice!
It's not as pretty as a typical hexdump, but it appears to have done the right thing.
It also shouldn't take that much tweaking to get it looking nice either...

.. code-block:: lisp

   CL-USER> (with-open-file (in "~/more-data.txt" :element-type '(unsigned-byte 8))
              (do ((nbytes 0 (1+ nbytes)) ; count the number of bytes read
                   (byte (read-byte in nil nil)
                         (read-byte in nil nil)))
                  ((null byte))

                ;; at the start of each line print the number of bytes read so far
                (if (eq (mod nbytes 16) 0)
                    (format t "~8,'0x: " nbytes))

                ;; every pair of bytes print a space - except on newlines
                (if (and (> nbytes 0) (evenp nbytes) (not (eq (mod nbytes 16) 0)))
                    (format t " "))

                ;; pad each byte to be 2 chars wide
                (format t "~2,'0x" byte)

                ;; every 16 bytes print a newline
                (if (eq (mod nbytes 16) 15)
                    (format t "~%"))))

   00000000: 3237 2F30 342F 3230 3236 2032 303A 3539
   00000010: 3A34 3820 2D20 4C69 6261 7469 6F6E 2043
   00000020: 7261 7368 0A20 4F53 2020 2020 2020 2020
   00000030: 2020 2020 2020 2020 2020 2020 4C69 6E75
   00000040: 780A 2056 6572 7369 6F6E 2020 2020 2020
   00000050: 2020 2020 2020 2020 2031 312E 312E 302E
   ...
   000003E0: 6572 5468 7265 6164 5374 6172 7428 290A
   NIL

Not bad for a few lines of code!

Getting a WASM Module
---------------------

For the "Hello, World!" program in the previous section any file would do, but now that we're looking to inspect a WASM module... we need a module to inspect!

I think I want something more complicated than a module that `exports a single function <https://developer.mozilla.org/en-US/docs/WebAssembly/Guides/Understanding_the_text_format#our_first_function_body>`__ but there's no point in handling a massive program like Python yet.

How about a tree-sitter grammar? I wrote a :ref:`simple one <jj-log-grammar>` recently that should give us a nice example right?

Thankfully, the ``tree-sitter`` cli makes it easy enough to compile to WASM, it even fetches the `WASI-SDK <https://github.com/webassembly/wasi-sdk>`__ for us::

  $ tree-sitter build --wasm
  Downloading wasi-sdk from https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-29/wasi-sdk-29.0-x86_64-linux.tar.gz...
    % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                   Dload  Upload  Total   Spent   Left   Speed
    0      0   0      0   0      0      0      0                              0
  100 113.9M 100 113.9M   0      0 54.01M      0   00:02   00:02         54.73M
  Extracting wasi-sdk to /home/alex/.cache/tree-sitter/wasi-sdk...

Which results in a nicely sized WASM module for us to play with::

  $ ls -l
  -rwxr-xr-x ... 6029 2026-07-01 12:25 tree-sitter-jjlog.wasm

.. note::

   I am assuming, since tree-sitter has pulled in the ``wasi-sdk``, that this module is actually a `WASI <https://github.com/webassembly/wasi>`__ module. Something which is not covered in the core specification.

   I am also assuming however, that this distinction only matters when it comes to executing the module.

What's in a module anyway?
--------------------------

Thankfully, the :external+wasm:std:ref:`specification <binary-module>` for the WASM binary representation can tell us that and it says that the module must begin with a 4-byte "magic" number representing the string ``\0asm`` and a 4-byte version field (of the binary format, not the spec!).

.. code-block:: lisp

   (defun format-bytes (bytes &key offset note)
     (let ((fmt nil))))

.. code-block:: lisp

   (defun print-bytes (offset bytes annotation)
     (format t "~8,'0x: ~{~2,'0x ~}~v@a~a~%" offset bytes (- 42 (* 3 (length bytes))) "; " annotation))

   (defun read-header (stream)
     "Read the wasm header from STREAM"
     (let ((offset (file-position stream))
           (magic   ())
           (version ()))
       (dotimes (n 4) (push (read-byte stream) magic))
       (assert (equal magic (list #x6d #x73 #x61 #x0)))
       (print-bytes offset (nreverse magic) ".asm")

       (dotimes (n 4) (push (read-byte stream) version))
       (assert (equal version (list 0 0 0 1)))
       (print-bytes (+ 4 offset) (nreverse version) "v1")))

So let's see if we can extract that

.. code-block:: lisp

   CL-USER> (with-open-file (in "tree-sitter-jjlog.wasm" :element-type '(unsigned-byte 8))
               (dotimes (n 8) (format t "~2,'0x " (read-byte in))))
   00 61 73 6D 01 00 00 00

Following the header a module has zero or more sections which at a high level, are composed of:

- a single byte ID denoted their type,
- a ``u32`` representing the length of their content
- the content.

That, should be enough information at least to write some code to give us the high-level
structure of our WASM module, or at least it would... if we knew how integers work.

Parsing Integers
^^^^^^^^^^^^^^^^

Since a ``u32`` cannot be stored in a single byte, we need to look at how WebAssembly encodes them.
The :external+wasm:std:ref:`spec <binary-value>` states that all integers are encoded using the LEB128 integer encoding, with some extra constraints.

The way this is stated in the spec is quite intimidating and takes a while to wrap your head around it.
But I *think* for unsigned ints you can summarise it as:

- Only the low 7 bits in every byte encode the number, giving us the 128 (= 2\ :sup:`7`) in LEB128)
- When the high bit is set this indicates that the number continues in the next byte
- To reconstruct the number, you need to shift subsequent bytes up by the corresponding multiple of 7 bits.

Though I'm sure there are some subtleties that I am missing at this stage.

Anyway, after a fair amount of head scratching I've arrived at the following function that appears to do the right thing.

.. code-block:: lisp

   (defun read-leb128-uint (stream)
     "Read a LEB128 unsigned integer from STREAM"
      (do ((value 0)
           (shift 0 (+ shift 7))
           (byte (read-byte stream) (read-byte stream)))
           ((progn
               ;; update value as part of the "should the loop terminate check"
               ;; this appears to be the only place where the correct values are
               ;; are available.
               (setf value (logior value (ash (logand #x7f byte) shift)))
               (eq 0 (logand #x80 byte)))  ; continue until high bit is not set.
            ;; when done, return final value and the bytes read
            value)))

.. admonition:: Author's Note

   I spent more time than I care to admit trying to get this function right, I have no idea if this the "correct" way to use a ``DO`` form, or if another construct would've been easier to use.
   But it's done now and I can move on!

Scanning Sections
^^^^^^^^^^^^^^^^^

Now we can read numbers properly, we now know enough to skip over sections

.. code-block:: lisp

   (defun skip-unknown-section (stream offset section-id length)
     (print-bytes offset (list section-id)
                         (format nil "Section: ~a [~a bytes]" section-id length))
     ;; skip over the content
     (file-position stream (+ (file-position stream) length)))

   (defun read-section (stream)
     (let ((offset     (file-position stream))
           (section-id (read-byte stream))
           (length     (read-leb128-uint stream)))
        (case section-id (otherwise (skip-unknown-section stream offset section-id length)))))

With that it should now be possible to walk the overall structure of the module.

.. code-block:: lisp

   CL-USER> (with-open-file (in "~/.emacs.d/tree-sitter-grammars/jjlog/tree-sitter-jjlog.wasm" :element-type '(unsigned-byte 8))
              (read-header in)
              (loop
                (read-section in)))

   00000000: 00 61 73 6D                             ; .asm
   00000004: 01 00 00 00                             ; v1
   00000008: 00                                      ; Section: 0 [16 bytes]
   0000001A: 01                                      ; Section: 1 [28 bytes]
   00000038: 02                                      ; Section: 2 [90 bytes]
   00000094: 03                                      ; Section: 3 [5 bytes]
   0000009B: 07                                      ; Section: 7 [48 bytes]
   000000CD: 09                                      ; Section: 9 [7 bytes]
   000000D6: 0A                                      ; Section: 10 [3388 bytes]
   00000E15: 0B                                      ; Section: 11 [1991 bytes]
   000015DF: 00                                      ; Section: 0 [147 bytes]
   00001675: 00                                      ; Section: 0 [127 bytes]
   000016F6: 00                                      ; Section: 0 [148 bytes]
   ; Debugger entered on #<END-OF-FILE {1202A84C73}>

Module Sections
---------------

We're in "draw the rest of the owl" territory and we "just" need to parse the content of each of the sections.

It quickly became obvious that implementing support for the full spec is beyond the scope of a single blog post!
So what follows now is just enough code to provide an overview of the contents of the specific WASM module I chose as my example.

The module contains the following section types

- Section 1: :ref:`9-1-type-section`

Which we can update our ``read-section`` function to handle.

.. code-block:: lisp

   (defun read-section (stream)
     (let ((offset     (file-position stream))
           (section-id (read-byte stream))
           (length     (read-leb128-uint stream)))
        (case section-id (1         (read-type-section    stream offset section-id length))
                         (2         (read-import-seciton  stream offset section-id length))
                         (otherwise (skip-unknown-section stream offset section-id length)))))

.. _9-1-type-section:

Type Section
^^^^^^^^^^^^

The type section provides a list of type definitions referenced elsewhere within the module.
The ``tree-sitter-jjlog.wasm`` module only contains function signatures (``0x60``) that reference ``i32`` types (``0x7f``)

.. code-block:: lisp

   (defun read-function-type (stream offset)
     (let (num-params num-return)
       (assert (eq (read-byte stream) #x60))
       (format t "~8,'0x: 60 " offset)

       (setf num-params (read-leb128-uint stream))
       (format t "[~a] " num-params)
       (dotimes (n num-params) (format t "~2,'0x " (read-byte stream)))

       (setf num-return (read-leb128-uint stream))
       (format t "[~a] " num-return)
       (dotimes (n num-return) (format t "~2,'0x " (read-byte stream)))

       (format t "~%")))

   (defun read-type-section (stream offset section-id length)
     (print-bytes offset (list section-id)
                         (format nil "Type Section: ~a [~a bytes]" section-id length))
     (let ((num-types (read-leb128-uint stream)))
       (dotimes (n num-types) (read-function-type stream (file-position stream)))))

.. _9-2-import-section:

Import Section
^^^^^^^^^^^^^^

The import section declares the dependencies the host needs to provide in the form ``module name type`` where module and name are :external+wasm:std:ref:`names <binary-name>`.

Names are represented by a list of bytes, where a LEB128 encoded number specifies the number of bytes to read which encode the name as a UTF-8 string.
Now properly decoding UTF-8 is non-trivial however, this section happens to only use plain ASCII characters so we can get away with a fairly simple function.

.. code-block:: lisp

   (defun read-name (stream)
     (let* ((length (read-leb128-uint stream))
            (bytes (dotimes (_ length) (read-byte stream))))
       (coerce (mapcar #'code-char bytes) 'string)))

Each has an associated :external+wasm:std:ref:`external type <binary-externtype>`.

.. code-block:: lisp

   (defun read-external-type (stream)
     (let (etype (read-byte stream))
       (case (#x02 (read-memory-type stream)))))

.. code-block:: lisp

   (defun read-import (stream offset)
     (let ((module (read-name stream)
           (name   (read-name stream)
           ))))

   (defun read-import-section (stream offset section-id length)
     (print-bytes offset (list section-id)
                         (format nil "Import Section: ~a [~a bytes]" section-id length))
     (let ((num-imports (read-leb128-uint stream)))
       (dotimes (n num-imports) (read-import stream (file-position stream)))))
