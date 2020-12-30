---
author:
- Alex Carney
date: 2020-12-28
description: Creating a Python frontend to my simple AST evaluator
draft: false
tags:
- c
- python
- programming-languages
title: Creating a Python C Extension
---

[Previously]({{< relref "ast-simple-eval.md" >}}), as part of my exploration
into how programming languages are implemented, I wrote a very simple AST
evaluator that knew how to add and multiply floats together. Since constructing
these ASTs by hand is quite painful I thought it would be fun to come up with a
frontend to my "programming language" which could do it for me.

Now your typical frontend would be some kind of parser built into the
compiler/interpreter. However, while I'm definitely iterested
in parsing I don't quite feel like tackling that just yet. Instead I'm going to
have Python be the frontend and embed my toy lanaguage into it via a [Python C
Extension][python-c-ext]

<!--more-->

## Overview

Before diving into the detail I think it would be worth giving a brief overview
on how this will work end-to-end.

- [Constructing an AST Representation]({{< relref "#ast-repr" >}}})

  The main idea behind using Python as the frontend is that the user should be
  able to write somewhat standard Python code to construct an expression which
  can then be passed to the C backend to be evaluated. This means that we will
  need to create some way to represent our AST from within Python.

- [Setting up the C Extension]({{< relref "#ext-setup" >}})

  With the ability to represent ASTs in the frontend Python code sorted, we then
  need to start thinking about the basics of creating a C Extension.

- [Converting Between Python and C]({{< relref "#conversions" >}})

  Finally we need to write the code that handles converting the Python
  representation of the AST into the C representation, evaluating it and then
  converting the result back into Python.

From this point on I'm going to refer to my toy language as `ccalc` as it is
essentially a calculator written in C - very original I know! 😄

## Constructing an AST Representation {#ast-repr}

To represent the AST in Python code we can create a class that captures the same
information as our [AstNode]({{< relref "ast-simple-eval.md#ast-repr" >}})
struct from the C code

``` python
class AstNode:

    LITERAL = 0
    PLUS = 1
    MULTIPLY = 2

    def __init__(self, type=None, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right
```

From there it's simple enough to create some subclasses that help us fill out
the correct fields.

``` python
class Literal(AstNode):
    def __init__(self, value):
        super().__init__(type=AstNode.LITERAL, value=float(value))

class Plus(AstNode):
    def __init__(self, left, right):
        super().__init__(type=AstNode.PLUS, left=left, right=right)

class Multiply(AstNode):
    def __init__(self, left, right):
        super().__init__(type=AstNode.MULTIPLY, left=left, right=right)
```

Technically that's all we need to represent the AST in Python but we haven't
really gained anything in terms of usability, constructing an AST from the
classes we have defined so far would be just as painful as it was in C.

Thankfully though, we don't have to stop here, by taking advantage of being able
to define implementations for arithmetic operations on our custom types we can
introduce a much nicer method of constructing expressions.

``` python
class AstNode:
    ...

    def __init__(self, type=None, value=None, left=None, right=None):

        # Automatically convert python numbers to Literal(x) AST nodes
        if left is not None and not isinstance(left, AstNode):
            left = Literal(left)

        if right is not None and not isinstance(right, AstNode):
            right = Literal(right)

        ...

    def __add__(self, other):
        return Plus(self, other)

    def __radd__(self, other):
        return Plus(other, self)

    def __mul__(self, other):
        return Multiply(self, other)

    def __rmul__(other, self):
        return Multiply(other, self)
```

Now if we wanted to construct an expression we can do so with fairly
straightforward Python code.

``` python
>>> import ccalc

>>> (ccalc.Literal(1) + 2) * 3
Multiply<Plus<Literal<1.0>, Literal<2.0>>, Literal<3.0>>

>>> ccalc.Literal(1) + (2 * 3)
Plus<Literal<1.0>, Literal<6.0>>
```

However, as shown with the second example above we need to be careful when
choosing the number to wrap in our `ccalc.Literal` class if we want to "catch"
the expression and construct our AST rather than have Python compute the value
directly

``` python
>>> 1 + (ccalc.Literal(2) * 3)
Plus<Literal<1.0>, Multiply<Literal<2.0>, Literal<3.0>>
```

## Setting up the C Extension {#ext-setup}

Using [this tutorial][real-python-c-ext] on Real Python as a guide I was able to
get a C Extension up and running surprisingly easily. Be sure to check out the
article for details but in short I ended up creating the following directory
structure

```
.
├── ccalc
│   └── __init__.py
├── ccalcmodule.c
└── setup.py
```

Where the `__init__.py` file contains the Python code we wrote in the previous
section. In `ccalcmodule.c` is the boilerplate needed to define a Python
module

```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static struct PyModuleDef ccalcmodule = {
    PyModuleDef_HEAD_INIT,
    "_ccalc",
    "Simple calculator implemented in C",
    -1,
    ccalc_methods
};

PyMODINIT_FUNC
PyInit__ccalc()
{
    return PyModule_Create(&ccalcmodule);
}
```

The `PyModuleDef` struct as the name implies, defines some basic information
about the module

- It's name `_ccalc`, this specifies what our module is called when we `import`
  it in regular Python code
- The next argument is the module's docstring
- `-1` is something to do with sub-interpreters? 🤷‍♂
- `ccalc_methods` is an array of structs delcaring all the functions this module
  exposes to the interpreter.️

Something that caught me out is that the `PyInit_<module name>` function *must*
match the name we gave the module in `PyModuleDef`, so since the module name is
`_ccalc` I needed an additional `_` character in the name so that the module can
be registered correctly.

The methods defined in `ccalc_methods` array follow a similar pattern

``` c
static PyMethodDef ccalc_methods[] = {
    {"hello_world", method_hello_world, METH_VARARGS, "Print 'Hello, World!'."},
    {NULL, NULL, 0, NULL} // I think this is required so that Python knows when
                          // it's reached the end of the array
};
```

- `hello_world` is the name we want regular Python code to use when calling this
  method
- `method_hello_world` is the name of the function in our C code
- `METH_VARARGS` tells Python the kinds of arguments our function should be
  called with. Check out the [documentation][python-c-ext-args] for more
  details.
- The final parameter being the docstring

Finally we need the the actual method definition itself.

``` c
static PyObject*
method_hello_world(PyObject *self, PyObject *args)
{
    printf("Hello, World!\n");
    Py_RETURN_NONE;
}
```

### Building the Extension

To my surprise, this was the easiest step of them all. Rather than have to worry
about writing a `Makefile` or providing the right flags to link against my
version of Python, it turns out that `setuptools` can handle it all!

All I had to do was write a standard `setup.py` file, just with some additional
information about the extension itself

{{< include file="ccalc/setup.py">}}

With the packaging defined a `python setup.py install` was all that was needed
to build and install the extension into the virtual environment.

{{< command command="python setup.py install">}}
running install
running bdist_egg
running egg_info
creating ccalc.egg-info
writing ccalc.egg-info/PKG-INFO
writing dependency_links to ccalc.egg-info/dependency_links.txt
writing top-level names to ccalc.egg-info/top_level.txt
writing manifest file 'ccalc.egg-info/SOURCES.txt'
reading manifest file 'ccalc.egg-info/SOURCES.txt'
writing manifest file 'ccalc.egg-info/SOURCES.txt'
installing library code to build/bdist.linux-x86_64/egg
running install_lib
running build_py
creating build
creating build/lib.linux-x86_64-3.8
creating build/lib.linux-x86_64-3.8/ccalc
copying ccalc/__init__.py -> build/lib.linux-x86_64-3.8/ccalc
running build_ext
building '_ccalc' extension
creating build/temp.linux-x86_64-3.8
x86_64-linux-gnu-gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -O2 -Wall -g -fstack-protector-strong -Wformat -Werror=format-security -g -fwrapv -O2 -g -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2 -fPIC -I/home/alex/Projects/scratch/.env/include -I/usr/include/python3.8 -c ccalcmodule.c -o build/temp.linux-x86_64-3.8/ccalcmodule.o
x86_64-linux-gnu-gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-Bsymbolic-functions -Wl,-z,relro -g -fwrapv -O2 -Wl,-Bsymbolic-functions -Wl,-z,relro -g -fwrapv -O2 -g -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2 build/temp.linux-x86_64-3.8/ccalcmodule.o -o build/lib.linux-x86_64-3.8/_ccalc.cpython-38-x86_64-linux-gnu.so
creating build/bdist.linux-x86_64
creating build/bdist.linux-x86_64/egg
creating build/bdist.linux-x86_64/egg/ccalc
copying build/lib.linux-x86_64-3.8/ccalc/__init__.py -> build/bdist.linux-x86_64/egg/ccalc
copying build/lib.linux-x86_64-3.8/_ccalc.cpython-38-x86_64-linux-gnu.so -> build/bdist.linux-x86_64/egg
byte-compiling build/bdist.linux-x86_64/egg/ccalc/__init__.py to __init__.cpython-38.pyc
creating stub loader for _ccalc.cpython-38-x86_64-linux-gnu.so
byte-compiling build/bdist.linux-x86_64/egg/_ccalc.py to _ccalc.cpython-38.pyc
creating build/bdist.linux-x86_64/egg/EGG-INFO
copying ccalc.egg-info/PKG-INFO -> build/bdist.linux-x86_64/egg/EGG-INFO
copying ccalc.egg-info/SOURCES.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying ccalc.egg-info/dependency_links.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying ccalc.egg-info/top_level.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
writing build/bdist.linux-x86_64/egg/EGG-INFO/native_libs.txt
zip_safe flag not set; analyzing archive contents...
__pycache__._ccalc.cpython-38: module references __file__
creating dist
creating 'dist/ccalc-1.0.0-py3.8-linux-x86_64.egg' and adding 'build/bdist.linux-x86_64/egg' to it
removing 'build/bdist.linux-x86_64/egg' (and everything under it)
Processing ccalc-1.0.0-py3.8-linux-x86_64.egg
removing '/home/alex/Projects/scratch/.env/lib/python3.8/site-packages/ccalc-1.0.0-py3.8-linux-x86_64.egg' (and everything under it)
creating /home/alex/Projects/scratch/.env/lib/python3.8/site-packages/ccalc-1.0.0-py3.8-linux-x86_64.egg
Extracting ccalc-1.0.0-py3.8-linux-x86_64.egg to /home/alex/Projects/scratch/.env/lib/python3.8/site-packages
ccalc 1.0.0 is already the active version in easy-install.pth

Installed /home/alex/Projects/scratch/.env/lib/python3.8/site-packages/ccalc-1.0.0-py3.8-linux-x86_64.egg
Processing dependencies for ccalc==1.0.0
Finished processing dependencies for ccalc==1.0.0
{{< /command >}}


## Converting Between Python and C {#conversions}

## Next Steps

[arg-spec]: https://docs.python.org/3/c-api/arg.html#c.PyArg_ParseTuple
[python-c-ext]: https://docs.python.org/3/extending/extending.html
[python-c-ext-args]: https://docs.python.org/3/extending/extending.html#the-module-s-method-table-and-initialization-function
[real-python-c-ext]: https://realpython.com/build-python-c-extension-module/
