---
tags:
- c
- python
title: ccalc
description: |
   A CPython extension that embeds the `simple-ast` program into Python
---

A CPython extension that embeds the [simple-ast]({{< ref "code/simple-ast" >}})
program into Python.

``` python
>>> import ccalc
>>> expression = (ccalc.Literal(1) + 2) * 3
>>> expression
Multiply<Plus<Literal<1.0>, Literal<2.0>>, Literal<3.0>>

>>> ccalc.eval_ast(expression)
9.0
```

### Building

It's probably worth creating a virtual environment to work in

{{< command command="python -m venv .env" />}}

Assuming you have a C compiler available, building the extension is as easy as
running the following command

{{< command command="python setup.py install" prompt="(.env) $" />}}
