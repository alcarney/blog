.. post:: 2021-01-13
   :tags: c, python, prog-langs
   :author: Alex Carney
   :language: en
   :excerpt: 2

.. code:
   - code/ccalc/
   - code/simple-ast/
   description: Creating a Python frontend to my simple AST evaluator

Creating a CPython Extension
============================

:doc:`Previously </blog/2020/ast-simple-eval>`, as part of my exploration
into how programming languages are implemented, I wrote a very simple AST
evaluator that knew how to add and multiply floats together. Since constructing
these ASTs by hand is quite painful I thought it would be fun to come up with a
frontend to my "programming language" which could do it for me.

Now your typical frontend would be some kind of parser built into the
compiler/interpreter. However, while I'm definitely interested in parsing I
don't quite feel like tackling that just yet. Instead I'm going to have Python
be the frontend and embed my toy language into it via a `CPython Extension`_

.. <!--more-->

Overview
--------

Before diving into the detail I think it would be worth keeping in mind what we
want the end result to be. By the end of this post, we want to have a CPython
extension that allows us to write normal-ish Python code to construct a
representation of some expression

.. code-block:: python

   >>> import ccalc
   >>> expression = (ccalc.Literal(1) + 2) * 3
   >>> expression
   Multiply<Plus<Literal<1.0>, Literal<2.0>>, Literal<3.0>>

and then be able to pass this expression to the AST evaluator we wrote in the
previous post and have it compute the result

.. code-block:: python

   >>> ccalc.eval_ast(expression)
   9.0

If you'd rather skip all the exposition you can find the final codebase

.. [here]({{< ref "/code/ccalc/_index.md"  >}})

We can break the implementation down into 3 main steps

- :ref:`ast_python_frontend__ast_repr`

  We need an equivalent Python representation to the ``AstNode`` structure,
  allowing the user to express the expression they want computed.

- :ref:`ast_python_frontend__ext_setup`

  Before we can get to the fun part, there's some setup required to get a
  CPython extension up and running.

- :ref:`ast_python_frontend__conversions`

  Finally we need to write the code that converts the Python representation into
  the C representation, passing it off to the evaluator before converting the
  result back into Python.

.. _ast_python_frontend__ast_repr:

Constructing an AST Representation
----------------------------------

To represent the AST in Python code we can create a class that captures the same
information as our :ref:`AstNode <ast_simple_eval__ast_repr>` struct from the C code

.. code-block:: python

   class AstNode:

      LITERAL = 0
      PLUS = 1
      MULTIPLY = 2

      def __init__(self, type=None, value=None, left=None, right=None):
         self.type = type
         self.value = value
         self.left = left
         self.right = right

From there it's simple enough to create some subclasses that help us fill out
the correct fields.

.. code-block:: python

   class Literal(AstNode):
      def __init__(self, value):
         super().__init__(type=AstNode.LITERAL, value=float(value))

   class Plus(AstNode):
      def __init__(self, left, right):
         super().__init__(type=AstNode.PLUS, left=left, right=right)

   class Multiply(AstNode):
      def __init__(self, left, right):
         super().__init__(type=AstNode.MULTIPLY, left=left, right=right)


Technically that's all we need but we haven't really gained anything in terms of
usability, constructing an AST from the classes we have defined so far would be
just as painful as it was in C.

Thankfully though, we don't have to stop here, by taking advantage of being able
to define implementations for arithmetic operations on our custom types we can
introduce a much nicer method of constructing expressions.

.. code-block:: python

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

Now if we wanted to construct an expression we can do so with fairly
straightforward Python code.

.. code-block:: python

   >>> import ccalc

   >>> (ccalc.Literal(1) + 2) * 3
   Multiply<Plus<Literal<1.0>, Literal<2.0>>, Literal<3.0>>

   >>> ccalc.Literal(1) + (2 * 3)
   Plus<Literal<1.0>, Literal<6.0>>

However, as shown with the second example above we need to be careful when
choosing the number to wrap in our ``ccalc.Literal`` class if we want to "catch"
the expression and construct our AST rather than have Python compute the value
directly

.. code-block:: python

   >>> 1 + (ccalc.Literal(2) * 3)
   Plus<Literal<1.0>, Multiply<Literal<2.0>, Literal<3.0>>

.. _ast_python_frontend__ext_setup:

Setting up the C Extension
--------------------------

Using `this tutorial`_ from Real Python as a guide I was able
to get a C Extension up and running surprisingly easily. Be sure to check out
the article for details but in short I ended up creating the following directory
structure

.. code-block:: none

   .
   ├── ccalc
   │   └── __init__.py
   ├── ccalcmodule.c
   └── setup.py

Where the ``__init__.py`` file contains the Python code we wrote in the previous
section and ``ccalcmodule.c`` contains the boilerplate needed to define a Python
module

.. code-block:: c

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

The ``PyModuleDef`` struct as the name implies, defines some basic information
about the module

- It's name ``_ccalc``, specifies what our module is called when we ``import``
  it in regular Python code
- The next argument is the module's docstring
- ``-1`` is something to do with sub-interpreters?
- ``ccalc_methods`` is an array of structs delcaring all the functions this module
  exposes to the interpreter.️

Something that caught me out is that the ``PyInit_<module name>`` function *must*
match the name we gave the module in ``PyModuleDef``,  since the module name is
``_ccalc`` I needed an additional ``_`` character in the name so that the module can
be registered correctly.

The methods declared in the ``ccalc_methods`` array follow a similar pattern

.. code-block:: c

   static PyMethodDef ccalc_methods[] = {
      {"hello_world", method_hello_world, METH_VARARGS, "Print 'Hello, World!'."},
      {NULL, NULL, 0, NULL} // I think this is required so that Python knows when
                            // it's reached the end of the array
   };

- ``hello_world`` is the name we want regular Python code to use when calling this
  method
- ``method_hello_world`` is the name of the function in our C code
- ``METH_VARARGS`` tells Python the kinds of arguments our function should be
  called with. Check out the `documentation`_ for more details.
- The final parameter sets the docstring for the function

Finally we need the the actual method definition itself.

.. code-block:: c

   static PyObject*
   method_hello_world(PyObject *self, PyObject *args)
   {
      printf("Hello, World!\n");
      Py_RETURN_NONE;
   }

Building the Extension
^^^^^^^^^^^^^^^^^^^^^^

To my surprise, this was the easiest step of them all. Rather than worrying
about writing a ``Makefile`` or providing the right flags to link against my
version of Python, it turns out that ``setuptools`` takes care of all those
details.

All I had to do was write a standard ``setup.py`` file, just with some additional
information about the extension itself

.. literalinclude:: /code/ccalc/setup.py
   :language: python

With the packaging defined a ``python setup.py install`` was all that was needed
to build and install the extension into my virtual environment.

.. {{< command command="python setup.py install" prompt="(.env) $" >}}

.. code-block:: none
   :class: dropdown

   (.env) $ python setup.py install

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

With the C code sorted and building, we can import it in Python code and call
functions from it just as we would with any other module.

.. code-block:: python

   >>> import _ccalc
   >>> _ccalc.hello_world()
   Hello, World!

.. _ast_python_frontend__conversions:

Converting Between Python and C
-------------------------------

Now for the fun part! It's time to write a method for our extension module
``method_eval_ast`` that takes a Python representation of the AST and converts it
into our C representation before executing it and passing the result back up to
Python.

.. code-block:: c

   static PyObject*
   method_eval_ast(PyObject *self, PyObject *args)
   {
      ...
   }

   // Be sure to expose the new method to the module
   static PyMethodDef ccalc_methods[] = {
      {"eval_ast", method_eval_ast, METH_VARARGS, "Evaluate the given ast."},
      ...
   }

This can be broken down into a three step process

- :ref:`ast_python_frontend__function_args`
- :ref:`ast_python_frontend__c_ast`
- :ref:`ast_python_frontend__return`

.. _ast_python_frontend__function_args:

Parsing Function Arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^

When writing a ``METH_VARARGS`` style function, it gets called with 2 parameters
``self`` and ``args``. ``self`` in this case is a reference to our ``_ccalc`` module and
``args`` is a reference to a tuple containing the arguments that were passed to
our function.

As the contents of this tuple can be arbitrary it's up to our code to correctly
interpret the values that have been given to it. Thankfully Python provides a
handy function ``PyArg_ParseTuple`` that can take care of this for us.

.. code-block:: c

   PyObject *obj = NULL;

   if (!PyArg_ParseTuple(args, "O", &obj)) {
      return NULL;
   }

This function takes a `format string`_ that specifies the
number and type of arguments we expect to be given. In this case ``"O"`` says that
we want to take a single object - our AST. We also need to pass the correct
number of pointers into this function so that it can "return" the parsed values
to us.

In the case of invalid arguments being given, this function will set the global
error indicator for us with the correct error message. So all that would be left
for us to do is to return ``NULL`` which indicates to the code calling us that
there was an error. See the documentation on `error handling`_ for more details

.. _ast_python_frontend__c_ast:

Constructing the C AST
^^^^^^^^^^^^^^^^^^^^^^

With a reference to the Python object that (hopefully!) represents a valid AST
it's time to do the conversion into our C representation. To do this we'll write
a function dedicated to handling the conversion and call it from
``method_eval_ast``

.. code-block:: c

   AstNode *ast = AstTree_FromPyObject(obj);
   if (ast == NULL) {
      return NULL;
   };

The first step is to dynamically allocate enough memory to store the C
representation. Easy enough to do, assuming that you know the size of the
tree...

Allocating Memory
"""""""""""""""""

It took me a while to realise it, but even though we're writing C code we are
still within the Python interpreter. This means we still have access to all the standard
Python functions - we just need to look up their C equivalents. Why not just ask the
tree itself how big it is by calling ``len()`` on it?

After a quick trip to the documentation I discover that ``len`` is "spelt"
``PyObject_Length`` in the C API, add some of the required book keeping and we
should be able to allocate enough space

.. code-block:: c

   static AstNode*
   AstTree_FromPyObject(PyObject *obj)
   {
      Py_ssize_t num_nodes = PyObject_Length(obj);
      if (num_nodes == -1) {
         return NULL;
      }

      AstNode *ast = malloc(num_nodes * sizeof(AstNode));
      if (ast == NULL) {
         return NULL;
      }

      // ...
   }

Something important to note here, up until now we've been calling into the
Python C API which has been taking care of reporting any errors it encounters.
However, the call to ``malloc`` is now our code and it's our responsibility to
correctly report any errors we counter.

If we were to leave the code as is and this call to ``malloc`` fails, Python would
know that an error had occured but not be able to tell the user what was wrong.

.. code-block:: python

   >>> import ccalc
   >>> import _ccalc
   >>> _ccalc.eval_ast(ccalc.Literal(2))
   Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
   SystemError: <built-in function eval_ast> returned NULL without setting an error

Instead we also need to call ``PyErr_SetString`` to raise the appropriate
exception that describes our error.

.. code-block:: c

   AstNode *ast = malloc(num_nodes * sizeof(AstNode));
   if (ast == NULL) {
      PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for the AST.");
      return NULL;
   }

With the information set, Python is able to report a much better error
message to the user

.. code-block:: python

   >>> import ccalc
   >>> import _ccalc
   >>> _ccalc.eval_ast(ccalc.Literal(2))
   Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
   MemoryError: Unable to allocate memory

Finally let's not forget to jump back to the Python code and implement ``__len__``
on our ``AstNode`` class.

.. code-block:: python

   class AstNode:
      ...

      def __len__(self):
         left = 0 if self.left is None else len(self.left)
         right = 0 if self.right is None else len(self.right)
         return 1 + left + right

Inspecting Nodes
""""""""""""""""

With the memory to hold the tree allocated it's time to start on the actual
conversion. To handle this we'll write another function ``AstNode_FromPyObject``
that we can recursively call whenever we need to descend down a branch. This
function will take a reference ``obj`` to the Python representation of the node
we're currently converting, another reference `ast` to the memory we allocated
and finally an ``index`` into the array that we should write the node to.

.. code-block:: c

   static int
   AstNode_FromPyObject(PyObject *obj, AstNode *ast, Py_ssize_t index)
   {
      AstNode *node = &astindex];
      // ...
   }

The first step in the process is to determine the type of node we are
converting, which we can do by inspecting the value of the ``type`` field.

.. code-block:: c

   PyObject *type = PyObject_GetAttrString(obj, "type");
   if (type == NULL) {
      return 0;
   }

   long node_type = PyLong_AsLong(type);
   Py_DECREF(type);

The call to ``PyObject_GetAttrString`` is equivalent to ``obj.type`` in Python and
returns a **new reference** to a generic Python object. In order to get an
actual number we need to use ``PyLong_AsLong`` to convert it.

In theory ``type`` could be a reference to anything, so there's always the chance
that ``PyLong_AsLong`` could fail in which case it would return ``-1``. As stated in
`the documentation`_ we should really be performing extra checks here to determine
if the value is actually ``-1`` or if there was an error but I've decided to omit
those for now.

Something else to note is that ``type`` was a **new reference** and since Python
uses `Reference Counting`_ internally it's our responsibility to decrement the
count (using ``Py_DECREF``) when we are finished with it - at least that's what I
think should be done based on what I found in the documentation on `ownership`_

Converting the Node
^^^^^^^^^^^^^^^^^^^

Now that we have an integer ``node_type`` that corresponds with one of the
``AstNodeType`` enum entries we can use a ``switch`` statement and start writing the
conversion code for each type in turn.

.. code-block:: c

   switch(node_type) {
   case AST_LITERAL: {

      PyObject *value = PyObject_GetAttrString(obj, "value");
      if (value == NULL) {
         return 0;
      }

      double v = PyFloat_AsDouble(value);
      Py_DECREF(value);

      // ...
   }
   }

Considering the ``Literal`` node types first, we can follow a very similar process
to the previous section to extract the ``value`` field from the node giving us
enough information to fill out our first ``AstNode`` instance!

.. code-block:: c

   node->type = AST_LITERAL;
   node->value = v;
   node->left = NULL;
   node-> right = NULL;

   return 1;

As this node type has no children there's no further work to do and we can
return successfully. However, in the case of ``AST_PLUS`` and ``AST_MULTIPLY``
things aren't as straightforward...

Traversing the Tree
^^^^^^^^^^^^^^^^^^^

Handling the other node types starts off easy enough, since  they are almost
identical we can handle their differences in the ``switch`` statement and then use
the remainder of the function to handle recursing down both the ``left`` and
``right`` branches.

.. code-block:: c

   case AST_PLUS: {
      node->type = AST_PLUS;
      break;
   }
   case AST_MULTIPLY: {
      node->type = AST_MULTIPLY;
      break;
   }

We can then get references to the child nodes in the same way we've been
referencing all the other fields so far

.. code-block:: c

   PyObject *left = PyObject_GetAttrString(obj, "left");
   if (left == NULL) {
      return 0;
   }

   PyObject *right = PyObject_GetAttrString(obj, "right");
   if (right == NULL) {
      return 0;
   }

Then "all" that is left to do is set the ``left`` and ``right`` pointers on the
``AstNode`` struct and call ``AstNode_FromPyObject`` on each branch - remembering to
adjust the ``index`` value accordingly.

.. code-block:: c

   node->left = &ast[index + 1];
   node->right = &ast[index + 2];

   if (!AstNode_FromPyObject(left, ast, index + 1)) {
      return 0;
   }

   if (!AstNode_FromPyObject(right, ast, index + 2)) {
      return 0;
   }

   return 1;

At least... that's what I wanted to do initially, unfortunately this solution
wouldn't work in practice,. If ``left`` is a reference to anything other than an
``AST_LITERAL`` then it's children would be overwritten when we start processing
nodes on the ``right`` branch!

This had me scratching my head for quite a while, trying to come up with a way
to compute the correct offset for the ``right`` branch - without success.

Instead, since this is C I ended up changing the ``index`` argument from an actual
``Py_ssize_t`` to a pointer to one. This allows recursive calls to increment the
index as needed and by the time execution returns to the top level function, the
value referenced by the pointer is automatically the correct value.

.. code-block:: c

   (*index)++;
   node->left = &ast[*index];
   if (!AstNode_FromPyObject(left, ast, index)) {
      return 0;
   }

   (*index)++;
   node->right = &ast[*index];
   if (!AstNode_FromPyObject(right, ast, index)) {
      return 0;
   }

   return 1;

I have no idea if this is a terrible idea for real world scenarios, but it seems
to work well enough for this at least.

To complete the conversion code, all that remains is to make the initial call to
``AstNode_FromPyObject`` from our main ``AstTree_FromPyObject``  function

.. code-block:: c

   Py_ssize_t index = 0;
   if (!AstTree_FromPyObject(obj, ast, &index)) {
      free(ast);
      return NULL;
   }

   return ast;

.. _ast_python_frontend__return:

Returning the Result
^^^^^^^^^^^^^^^^^^^^

Phew! That was a lot of work but we're almost there. We just need to add a few
more lines to ``method_eval_ast`` that takes the newly constructed AST and
evaluates it, before converting the result into a Python float and returning it.

.. code-block:: c

   double result = ast_evaluate(ast);
   free(ast);
   return PyFloat_FromDouble(result);

That's the C Extension finished, the only thing we could do is import the
``_ccalc`` module from ``ccalc`` and expose the methods we want to present a unified
interface to users of the module.

.. code-block:: python

   # In ccalc/__init__.py
   import _ccalc

   eval_ast = _ccalc.eval_ast

And that way we can now make the example code from the start of this post
actually work!

.. code-block:: python

   >>> import ccalc
   >>> expression = (ccalc.Literal(1) + 2) * 3
   >>> expression
   Multiply<Plus<Literal<1.0>, Literal<2.0>>, Literal<3.0>>

   >>> ccalc.eval_ast(expression)
   9.0

Final Thoughts
--------------

There was a lot of code flying around in this post, if you want to see the final
result in its entirety you can find it

.. [here]({{< ref "/code/ccalc/_index.md" >}})

Best Practice?
^^^^^^^^^^^^^^

This was my first CPython extension so I might be missing out on some best
practices, for example a question I had was around my use of ``malloc`` and
``free``. While writing this section I found the documentation on `memory management`_
and it appears that the recommendation is to use the ``PyMem_*`` family of
functions, even for allocations that are not ``PyObjects``. However it looks
like there is a learning curve to these as some functions require holding
the `GIL`_ and some don't.

Hmm... speaking of the GIL, should this extension be acquiring it at any point?
🤔

Another approach
^^^^^^^^^^^^^^^^

Another note worth mentioning is that it looks like it's possible to
`define custom types`_ directly in C. This means it should be possible to extend
the ``AstNode`` C struct to be an object than can be manipulated directly from
Python code - bypassing the need for all the conversion code we had to write.

However, I decided against this approach mainly because the "convert between the
representations" approach means we get to evolve the Python and C
representations semi independently. Assuming that the Python representation
exposes the correct fields then any method of generating the AST from Python is
perfectly valid.

Anyway, I think this post has gone on long enough I hope you found it useful and
I'll see you in the next one!

.. TODO: Now that is blog is powered by Sphinx, most of these links could be replaced with their
   intersphinx counterparts.

.. _CPython Extension: https://docs.python.org/3/extending/extending.html
.. _define custom types: https://docs.python.org/3/extending/newtypes_tutorial.html
.. _documentation: https://docs.python.org/3/extending/extending.html#the-module-s-method-table-and-initialization-function
.. _error handling: https://docs.python.org/3/c-api/exceptions.html
.. _format string: https://docs.python.org/3/c-api/arg.html#parsing-arguments
.. _GIL: https://docs.python.org/3/glossary.html#term-global-interpreter-lock
.. _memory management: https://docs.python.org/3/c-api/memory.html
.. _ownership: https://docs.python.org/3/extending/extending.html#ownership-rules
.. _Reference Counting: https://en.wikipedia.org/wiki/Reference_counting
.. _the documentation: https://docs.python.org/3/c-api/long.html?highlight=aslong#c.PyLong_AsLong
.. _this tutorial: https://realpython.com/build-python-c-extension-module/
