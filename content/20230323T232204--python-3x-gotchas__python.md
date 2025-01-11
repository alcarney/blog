---
title: Python 3.x Gotchas
date: 2023-03-23T23:22:04+00:00
tags:
  - python
identifier: "20230323T232204"
---

# Python 3.x Gotchas

Here is a collection of potential issues and gotchas to watch out for when
writing Python 3.x code.

## ``pathlib`` on 3.5


While `pathlib` exists in Python 3.5, it's not fully integrated yet. Passing a
`pathlib.Path` object to the built-in `open` method will result in a surprising error

```python
TypeError: invalid file: PosixPath('path/to/file.txt')
```

In this situation it's better to call the path's :meth:`pathlib.Path.open` method instead.

## Explicit super() required for dynamically created classes


It seems that there is a bug surrounding classes created using the
`type(name, bases, attrs)` method where the "magic" that allows for the
implicit use of the `super()` function is not setup correctly. Therefore if
we were to create a class that wishes to delegate to the base class'
implementation we will have to provide the information to `super()` ourselves.

```python
import cmd

def init(self):
   # Add our stuff here...
   super(self.__class__, self).__init__()

MyPrompt = type("MyPrompt", (cmd.Cmd,), {"__init__": init})
```

### Click under Python 3 is picky around encodings

If Click is unhappy around the execution environment it finds itself in, it will
refuse to run. The workaround for this is to make sure that the appropriate
environment variables are exported before invoking a Click program

```
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```

[Source](https://click.palletsprojects.com/en/7.x/python3/#python-3-surrogate-handling)
