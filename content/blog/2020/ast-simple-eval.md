---
author:
- Alex Carney
date: 2020-12-27
description: |
   Playing around with constructing and evaluating Abstract Syntax Trees
draft: false
tags:
- c
- programming-languages
title: Evaluating a Simple Abstract Syntax Tree
---

Programming languages and their implementation is a topic I've been interested
in for a long time and I thought it would be worth trying to get a bit more
hands on and play with some of the ideas in this space. Choosing a topic
somewhat at random I've chosen to take a look at implementing an Abstract Syntax
Tree (AST).

<!--more-->

## What is an Abstract Syntax Tree?

An [Abstract Syntax Tree][ast-wiki] is a way to represent a program's source
code within an interpreter/compiler. Consider an expression like `1 + 2`, it
could be represented by the following tree.

{{< mermaid >}}
graph TD
   + --- 1
   + --- 2
{{< /mermaid >}}

One of the nice things about ASTs is that they remove some of the ambiguity that
can exist in plain text. Consider the expression `1 + 2 * 3`, there are two ways
to interpret it and depending on which you choose you will get a different
result - either `(1 + 2) * 3 = 9` or `1 + (2 * 3) = 7`. This choice gets encoded
into the structure of tree itself

{{< mermaid >}}
graph TD
   subgraph "1 + (2 * 3)"
   p2[+] --- u1[1]
   p2[+] --- m2[x]
   m2[*] --- u2[2]
   m2[*] --- u3[3]
   end
   subgraph "(1 + 2) * 3"
   m1[*] --- p1[+]
   m1[*] --- v3[3]
   p1[+] --- v1[1]
   p1[+] --- v2[2]
   end
{{< /mermaid >}}

Encoding a program in this way allows the interpreter/compiler to focus on the
semantic meaning of the program without having to worry about the finer details
of how that program happens to be written down.

## Representing an AST

For no particular reason other I fancied trying it, I decided to use C to
represent my AST where each node is represented by the following struct.

{{< include file="simple-ast.c" lines="9-25" >}}

Although the `typedef` will let us refer to this struct using the name `AstNode`
from here on out, this name does not exist within the body of the struct
definition itself. In order to have the struct hold pointers to other instances
of the same type it's necessary to also name the struct definition `_ast`

In order to express the example trees above we only need to specify a few node
types

{{< include file="simple-ast.c" lines="3-7" >}}

With our AST node representation defined, it's easy enough to construct a tree
for the two examples we outlined earlier

{{< include file="simple-ast.c" lines="79-87" >}}

## Evaluating the AST

To evaluate an instance of the AST we have defined we can take a simple approach

- If the node we are evaluating is an `AST_LITERAL` then all we have to do is
  return the value stored in that node

  {{< include file="simple-ast.c" lines="53-59" >}}

- In the case of `AST_PLUS`, we recursively call `ast_evaluate` on
  both the left and right branches of the tree and then add the resulting values
  together

  {{< include file="simple-ast.c" lines="60-65" >}}

- Simiarly for `AST_MULTIPLY`, but returing `a * b` in this case.

  {{< include file="simple-ast.c" lines="67-75" >}}

Calling this function on each of our example trees and printing the result we
see that we indeed compute the values we would expect in each case

```
Example 1: 9.00
Example 1: 7.00
```

And there you have it, a calculator that only knows how to add and multiply
floats! 😃 If you want to see the entire source file you can find it
[here](/listings/simple-ast.c).

[ast-wiki]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
