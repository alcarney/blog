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

Using [this tutorial][real-python-c-ext] from Real Python as a guide I was able
to get a C Extension up and running surprisingly easily. Be sure to check out
the article for details but in short I ended up creating the following directory
structure

```
.
├── ccalc
│   └── __init__.py
├── ccalcmodule.c
└── setup.py
```

Where the `__init__.py` file contains the Python code we wrote in the previous
section and `ccalcmodule.c` contains the boilerplate needed to define a Python
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
- The final parameter sets the docstring for the function

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
to build and install the extension into my virtual environment.

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

With the C code sorted and building, we can import it in Python code and call
functions from it just as we would with any other module.

``` python
>>> import _ccalc
>>> _ccalc.hello_world()
Hello, World!
```

## Converting Between Python and C {#conversions}

Now for the fun part! It's time to write a method for our extension module
`method_eval_ast` that takes a Python representation of the AST and convert it
into our C representation before executing it and passing the result back up to
Python.

``` c

static PyObject*
method_eval_ast(PyObject *self, PyObject *args)
{
    ...
}

// Be sure to expose the new method with the module
static PyMethodDef ccalc_methods[] = {
    {"eval_ast", method_eval_ast, METH_VARARGS, "Evaluate the given ast."},
    ...
}
```

This can be broken down into a three step process

- [Parsing Function Arguments]({{< relref "#function-args">}})
- [Constructing the C AST]({{< relref "#c-ast" >}})
- [Returning the Result]({{< relref "#return" >}})

### Parsing Function Arguments {#function-args}

When writing a `METH_VARARGS` style function, it gets called with 2 parameters
`self` and `args`. `self` in this case is a reference to our `_ccalc` module and
`args` is a reference to a tuple containing the arguments that were passed to
our function.

As the contents of this tuple can be arbitrary it's up to our code to correctly
interpret the values that have been given to it. Thankfully Python provides a
handy function `PyArg_ParseTuple`that can take care of this for us.

``` c
PyObject *obj = NULL;

if (!PyArg_ParseTuple(args, "O", &obj)) {
    return NULL;
}
```

This function takes a [format string][python-c-ext-fmt-str] that specifies the
number and type of arguments we expect to be given. In this case `"O"` says that
we want to take a single object - our AST. We also need to pass the correct
number of pointers into this function so that it is "return" the parsed values
to us.

In the case of invalid arguments being given, this function will set the global
error indicator for us with the correct error message. All that's left for us to
do is to return `NULL` which indicates to the code calling us that there was an
error. See the [documentation][python-c-ext-err] for more details on error
handling.

### Constructing the C AST {#c-ast}

With a reference to the Python object that (hopefully!) represents a valid AST
it's time to do the conversion into our C representation. To do this we'll write
a function dedicated to handling the conversion and call it from
`method_eval_ast`

``` c
AstNode *ast = AstTree_FromPyObject(obj);
if (ast == NULL) {
    return NULL;
};
```

The first stumbling block is that now we could be given an AST of arbitrary
complexity we have to dynamically allocate enough memory to store it! Which
means we need a way of determining how many nodes there are in a given tree.

**Allocating Memory**

After much head scratching I eventually realized that even though we're now
writing C code, we're still within the Python intereter! Why not just ask the
tree itself how big it is by calling `len()` on it?

Well, first of all we need to implement `__len__` on the tree itself, but that's
simple enough

``` python
class AstNode:
    ...

    def __len__(self):
        left = 0 if self.left is None else len(self.left)
        right = 0 if self.right is None else len(self.right)
        return 1 + left + right
```

Then we just need to figure out the equivalent of `len(obj)` in the Python's C
API

``` c
static AstNode*
AstTree_FromPyObject(PyObject *obj)
{
    Py_ssize_t num_nodes = PyObject_Length(obj);
    if (num_nodes == -1) {
        return NULL;
    }

    // ...
}
```

With the prerequisties taken care of we can ask for the memory to store our AST.

``` c
AstNode *ast = malloc(num_nodes * sizeof(AstNode));
if (ast == NULL) {
    return NULL;
}
```

Something important to note here, up until now we've been calling into the
Python C API which has been taking care of reporting any errors it
encounters. However, as this is now our code and it's our responsibility to
report any errors we counter.

If we were to leave the code as is and this call to `malloc` fails, Python would
know that an error had occured but not be able to tell the user what was wrong.

``` python
>>> import ccalc
>>> import _ccalc
>>> _ccalc.eval_ast(ccalc.Literal(2))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
SystemError: <built-in function eval_ast> returned NULL without setting an error
```

Instead we also need to call `PyErr_SetString` to raise the appropriate
exception that describes our error.

``` c
AstNode *ast = malloc(num_nodes * sizeof(AstNode));
if (ast == NULL) {
   PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for the AST.");
   return NULL;
}
```

With the information set, Python is able to report a much better error
message to the user

``` python
>>> import ccalc
>>> import _ccalc
>>> _ccalc.eval_ast(ccalc.Literal(2))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
MemoryError: Unable to allocate memory for the AST.
```


**Doing the Conversion**

With the memory to hold the tree allocated it's time to do the actual
conversion. To handle this we'll write another function `AstNode_FromPyObject`
that we can recursively call whenever we need to descend down a branch. This
function will take a reference `obj` to the node we're currently converting,
another reference `ast` to the array we allocated for our tree

Before we can

**Traversing the Tree**

 This was the definitely the trickiest part of this
process for me as it took some thought on how to map each node we visit

### Returning the Result {#return}

## Next Steps

[arg-spec]: https://docs.python.org/3/c-api/arg.html#c.PyArg_ParseTuple
[python-c-ext]: https://docs.python.org/3/extending/extending.html
[python-c-ext-args]: https://docs.python.org/3/extending/extending.html#the-module-s-method-table-and-initialization-function
[python-c-ext-err]: https://docs.python.org/3/c-api/exceptions.html
[python-c-ext-fmt-str]: https://docs.python.org/3/c-api/arg.html#parsing-arguments
[real-python-c-ext]: https://realpython.com/build-python-c-extension-module/
