:title: Notes November
:identifier: 20241204T120000
:signature: 3=2
:date: 2024-12-04
:tags: blog, esbonio, lspdevtools, pytestlsp
:author: Alex Carney
:language: en

Notes for November 2024
=======================

.. container:: post-teaser

   Doubling my streak of writing notes on the :denote:link:`previous month <20241103T120000>` to 2, here are some of the things I worked on in November.

vscode-wasi-pygls
-----------------

.. figure:: https://github.com/alcarney/vscode-wasi-pygls/blob/main/screenshot.png?raw=true
   :target: https://github.com/alcarney/vscode-wasi-pygls/blob/main/screenshot.png?raw=true

This project is a proof of concept demonstrating how a pygls powered language server can be run entirely in the browser by making use of VSCode's `support for WebAssembly <https://code.visualstudio.com/blogs/2023/06/05/vscode-wasm-wasi>`__.

- Thanks to the work I managed to land in pygls in October, this project is now able to use the upstream version of the framework rather than my fork! (`PR <https://github.com/alcarney/vscode-wasi-pygls/pull/3>`__)

- I also pulled in ``@vscode/wasm-wasi-lsp`` as a dependency, removing some of the code I had previously taken from the :gh:`microsoft/vscode-wasm` repo (`PR <https://github.com/alcarney/vscode-wasi-pygls/pull/7>`__)


esbonio
-------

`esbonio <https://github.com/swyddfa/esbonio>`__ *is a language server for your Sphinx documentation projects*

- I `updated esbonio <https://github.com/swyddfa/esbonio/pull/928>`__ to the latest pygls ``v2`` pre-release

pytest-lsp
----------

`pytest-lsp <https://github.com/swyddfa/lsp-devtools>`__ *is a pytest plugin for writing end-to-end tests for language servers*

- `Updated pytest-lsp <https://github.com/swyddfa/lsp-devtools/pull/188>`__ to the latest pygls ``v2`` pre-release

lsp-devtools
------------

`lsp-devtools <https://github.com/swyddfa/lsp-devtools>`__ *is an attempt at building some of the developer tools I wished existed when I first started working on esbonio*

- `Dropped support <https://github.com/swyddfa/lsp-devtools/pull/190>`__ for Python 3.8
- `Updated lsp-devtools <https://github.com/swyddfa/lsp-devtools/pull/192>`__ to the latest pygls ``v2`` pre-release
