---
description: A collection of notes on writing Makefiles
links:
- url: https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html#Automatic-Variables
  name: Automatic Variables
- url: https://www.gnu.org/software/make/manual/html_node/Pattern-Rules.html#Pattern-Rules2",
  name: Pattern Rules
- url:  "https://nullprogram.com/blog/2017/08/20/"
  name: Writing Portable Makefiles
tags:
- c
- make
title: Writing Makefiles
---


## Pattern Rules

A pattern rule can be used to define a generic recipe for turning a file of type
X into a file a type Y for example, compiling `program.c` into `program.o`. A
pattern rule can be defined as follows

``` makefile
%.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@
```

- `%.o`/`%.c` Will match files of the form `*.o` and `*.c` respectively
- `$<` can be used to reference all the dependencies of the target, in this case
  the `*.c` file.
- `$@` can be used to reference the target itself, in this case the `$@` file


## Example


``` makefile
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
```
