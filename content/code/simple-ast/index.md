---
description: |
   A program that can construct and evaluate simple Abstract Syntax Trees
tags:
- c
title: Simple AST
---

A simple C program that can construct and evaluate a simple Abstract Syntax Tree
(AST). The AST represents a toy "programming language" that only knows how to
add and multiply floating point numbers together.

```
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
```

### Building

Having no real dependencies beyond the standard library this program can be
compiled with just a C compiler

{{< command command="gcc simple-ast.c -o simple-ast" />}}
