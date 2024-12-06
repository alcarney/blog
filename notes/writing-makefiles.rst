Writing Makefiles
=================

Pattern Rules
-------------

A pattern rule can be used to define a generic recipe for turning a file of type
X into a file a type Y for example, compiling ``program.c`` into ``program.o``. A
pattern rule can be defined as follows

.. code-block:: make

   %.o: %.c
	   $(CC) -c $(CFLAGS) $< -o $@

``%.o`` and ``%.c``
   Match files of the form ``*.o`` and ``*.c`` respectively

``$<``
   References all the dependencies of the target, in this case the ``*.c`` file.

``$@``
   References the target itself, in this case the ``.o`` file


Examples
--------

.. code-block:: make

   .POSIX:

   CC = gcc
   CFLAGS = -Wall $(shell pkg-config --cflags xcb-image)
   LDLIBS = $(shell pkg-config --libs xcb-image)

   default: main

   debug: CFLAGS += -g
   debug: main

   main: main.o
      $(CC) $< -o $@ $(LDLIBS)

   %.o: %.c
      $(CC) -c $(CFLAGS) $< -o $@

Links & Resources
-----------------

- `Automatic Variables <https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html#Automatic-Variables>`_
- `Pattern Rules <https://www.gnu.org/software/make/manual/html_node/Pattern-Rules.html#Pattern-Rules2>`_
- `Writing Portable Makefiles <https://nullprogram.com/blog/2017/08/20/>`_