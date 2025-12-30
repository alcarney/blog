:title: AST Simple Eval
:identifier: 20201217T120000
:date: 2020-12-17
:tags: blog, c, proglangs
:author: Alex Carney
:language: en

Evaluating a Simple Abstract Syntax Tree
========================================

.. container:: post-teaser

   Programming languages and their implementation is a topic I've been interested
   in for a long time and I thought it would be worth trying to get a bit more
   hands on and play with some of the ideas in this space. Choosing a topic
   somewhat at random I've chosen to take a look at implementing an Abstract Syntax
   Tree (AST).

30/12/2025
   Edited this post to

   - Reorganise code snippets so that we can use the current snapshot version of `awdur <https://github.com/swyddfa/awdur>`__
   - Add section on printing the AST
   - Convert mermaid diagrams to SVG

What is an Abstract Syntax Tree?
--------------------------------

An `Abstract Syntax Tree`_ is a way to represent a program's source
code within an interpreter/compiler. Consider an expression like ``1 + 2``, it
could be represented by the following tree.

.. raw:: html

   <style>
     .diagram rect,
     .diagram line,
     .diagram path { stroke: var(--fg-main); stroke-width: 0.5px; fill: none; }
     .diagram text { fill: var(--fg-main); }
   </style>

   <svg class="diagram" width="100%" viewBox="-80 -45 160 90" style="aspect-ratio: 16/9;"  >
     <rect x="-10" y="-40" width="20" height="25"></rect>
     <rect x="-50" y="10" width="20" height="25"></rect>
     <rect x="30" y="10" width="20" height="25"></rect>

     <text x="-5" y="-22">+</text>
     <text x="-44" y="28">1</text>
     <text x="35.5" y="28">2</text>

     <path d="M -10 -28 Q -30 -20 -40 10" />
     <path d="M 10 -28 Q 30 -20  40 10" />
   </svg>

One of the nice things about ASTs is that they remove some of the ambiguity that
can exist in plain text. Consider the expression ``1 + 2 * 3``, there are two ways
to interpret it and depending on which you choose you will get a different
result - either ``(1 + 2) * 3 = 9`` or ``1 + (2 * 3) = 7`` (rules like `BODMAS`_
dictate that we should choose the second version but there's still a choice).
This choice gets encoded into the structure of tree itself


.. raw:: html

   <svg class="diagram" width="100%" viewBox="-160 -90 340 180" style="aspect-ratio: 16/9;"  >
     <g transform="translate(-60, -20)">
       <text x="-60" y="-50" style="font-family: monospace; font-size: 8pt">(1 + 2) * 3</text>
       <rect x="-100" y="-60" width="160" height="160" />
       <rect x="-10" y="-40" width="20" height="25"></rect>
       <text x="-4" y="-20">*</text>
       <g>
         <rect x="-50" y="10" width="20" height="25" />
         <rect x="30" y="10" width="20" height="25" />

         <text x="-45" y="28">+</text>
         <text x="35.5" y="28">3</text>

         <path d="M -10 -28 Q -30 -20 -40 10" />
         <path d="M 10 -28 Q 30 -20  40 10" />
       </g>
       <g transform="translate(-40,50)">
         <rect x="-50" y="10" width="20" height="25" />
         <rect x="30" y="10" width="20" height="25" />

         <text x="-44" y="28">1</text>
         <text x="35.5" y="28">2</text>

         <path d="M -10 -28 Q -30 -20 -40 10" />
         <path d="M 10 -28 Q 30 -20  40 10" />
       </g>
     </g>

     <g transform="translate(70, -20) scale(-1,1)">
       <text x="-10" y="-50" transform="scale(-1, 1)" style="font-family: monospace; font-size: 8pt">1 + (2 * 3)</text>
       <rect x="-100" y="-60" width="160" height="160" />
       <rect x="-10" y="-40" width="20" height="25"></rect>
       <text x="-5" y="-22">+</text>
       <g>
         <rect x="-50" y="10" width="20" height="25" />
         <rect x="30" y="10" width="20" height="25" />

         <text x="-44" y="28" transform="scale(-1,1)">1</text>
         <text x="36" y="29" transform="scale(-1,1)">*</text>

         <path d="M -10 -28 Q -30 -20 -40 10" />
         <path d="M 10 -28 Q 30 -20  40 10" />
       </g>
       <g transform="translate(-40,50)">
         <rect x="-50" y="10" width="20" height="25" />
         <rect x="30" y="10" width="20" height="25" />

         <text x="-44" y="28" transform="scale(-1,1)">2</text>
         <text x="35.5" y="28" transform="scale(-1,1)">3</text>

         <path d="M -10 -28 Q -30 -20 -40 10" />
         <path d="M 10 -28 Q 30 -20  40 10" />
       </g>
     </g>

   </svg>

Encoding a program in this way allows the interpreter/compiler to focus on the
semantic meaning of the program without having to worry about the finer details
of how that program happens to be written down.

.. _ast_simple_eval__ast_repr:

Representing the AST
--------------------

For no particular reason other than I fancied trying it, I decided to use C to represent my AST.
In order to encode the example trees above, we'll need three node types

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   #include <stdio.h>

   typedef enum {
       AST_LITERAL,
       AST_PLUS,
       AST_MULTIPLY,
   } AstNodeType;

Where each node is represented by the following struct.

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   typedef struct _ast {
       /* The type of node this represents e.g.
          a literal, an operator etc. */
       AstNodeType type;

       /* In the case of a literal value, this field
          holds the actual value */
       float value;

       /* In the case of an operator, this pointer
          refers to the left child node */
       struct _ast *left;

       /* In the case of an operator, this pointer
          refers to the right child node */
       struct _ast *right;
   } AstNode;

Although the ``typedef`` will let us refer to this struct using the name ``AstNode``
from here on out, this name does not exist within the body of the struct
definition itself. In order to have the struct hold pointers to other instances
of the same type it's necessary to also name the struct definition ``_ast``

Printing the AST
----------------

Keeping things simple, we can recurse over all the nodes and print a single line representation of each node.
By indenting each line according to its depth in the tree, it should be possible to visually parse the structure.

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   void
   ast_print(AstNode *ast, int level)
   {
       for (int i = 0; i < level; i++) {
           printf("  ");
       }

When printing an ``AST_LITERAL`` node, it's enough to just print the contained value

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   switch(ast->type) {
   case AST_LITERAL:
       printf("%.2f\n", ast->value);
       break;

For ``AST_PLUS`` nodes, we need to print a representation of the operation and then recurse down both branches of the tree.

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   case AST_PLUS:
       printf("+\n");
       ast_print(ast->left, level + 1);
       ast_print(ast->right, level + 1);
       break;

Similarly for ``AST_MULTIPLY`` nodes.

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

       case AST_MULTIPLY:
           printf("*\n");
           ast_print(ast->left, level + 1);
           ast_print(ast->right, level + 1);
           break;
       }
   }

Evaluating the AST
------------------

To evaluate an instance of the AST we have defined we can take a similiar approach to printing it.

If the node we are evaluating is an ``AST_LITERAL`` then all we have to do is return the value stored in that node

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   float
   ast_evaluate(AstNode *ast)
   {
       switch(ast->type) {
       case AST_LITERAL:
           return ast->value;

In the case of ``AST_PLUS``, we recursively call ``ast_evaluate`` on both the left and right branches of the tree and then add the resulting values together

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   case AST_PLUS: {
       float a = ast_evaluate(ast->left);
       float b = ast_evaluate(ast->right);

       return a + b;
   }

Simiarly for ``AST_MULTIPLY``, but returing ``a * b`` in this case.

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

       case AST_MULTIPLY: {
           float a = ast_evaluate(ast->left);
           float b = ast_evaluate(ast->right);

           return a * b;
       }
       }
   }

Bringing it together
--------------------

We have enough of a toy example together to be able to define, print and evaluate a tree for the two examples in the introduction.

.. code-block:: c
   :project: simple-ast
   :filename: simple-ast.c

   int
   main()
   {
       AstNode one = { .type = AST_LITERAL, .value = 1.0f };
       AstNode two = { .type = AST_LITERAL, .value = 2.0f };
       AstNode three = { .type = AST_LITERAL, .value = 3.0f };

       AstNode plus1 = { .type = AST_PLUS, .left = &one, .right = &two};
       AstNode example1 = { .type = AST_MULTIPLY, .left = &plus1, .right = &three};

       AstNode mul1 = { .type = AST_MULTIPLY, .left = &two, .right = &three};
       AstNode example2 = { .type = AST_PLUS, .left = &one, .right = &mul1};

       float result1 = ast_evaluate(&example1);
       float result2 = ast_evaluate(&example2);

       ast_print(&example1, 0);
       printf("Example 1: %.2f\n", result1);

       ast_print(&example2, 0);
       printf("Example 2: %.2f\n", result2);

       return 0;
   }

Which we can execute with the help of a compiler.

.. code-block:: console

   $ gcc simple-ast.c -o simple-ast
   $ ./simple-ast
   *
     +
       1.00
       2.00
     3.00
   Example 1: 9.00
   +
     1.00
     *
       2.00
       3.00
   Example 2: 7.00

And there you have it, a calculator that only knows how to add and multiply floats!
If you want to see the entire source file you can find it :ref:`here <code-simple-ast>`.

.. _Abstract Syntax Tree: https://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _BODMAS: https://en.wikipedia.org/wiki/Order_of_operations#Mnemonics
