:title: Notes October
:identifier: 20241103T120000
:signature: 3=1
:date: 2024-11-03
:tags: blog, esbonio, pygls
:author: Alex Carney
:language: en

Notes for October
=================

.. container:: post-teaser

   I want to try and get into the habit of writing more, so taking inspiration from Simon Willison’s `weeknotes <https://simonwillison.net/tags/weeknotes/>`__ here's a quick writeup of what I have been doing in the month of October.

Esbonio
-------

`esbonio <https://github.com/swyddfa/esbonio>`__ *is a language server for your Sphinx documentation projects*

Work towards the big ``1.0`` release continues and in the `latest pre-release <https://github.com/swyddfa/esbonio/releases/tag/esbonio-vscode-extension-v0.96.0>`__ of the VSCode extension, it should now be possible to preview documentation builds when running on Codespaces.
(`Issue <https://github.com/swyddfa/esbonio/issue/896>`__, `PR <https://github.com/swyddfa/esbonio/pull/905>`__)

Up until now, Esbonio has required a correctly configured Python environment in order to work at all.
However, one of the most common issues I see is people struggling with this initial setup step and Esbonio will refuse to try anything until it is complete.

This isn't ideal and in reality there is plenty Esbonio could do even if the Python environment is has access to is not complete!
So this month I started looking into ways to make the server useful in more situations

- The VSCode extension now comes with a default Python enviroment to use when the user does not provide their own
  (`PR <https://github.com/swyddfa/esbonio/pull/915>`__)

- The language server can now continue to work if one of the required Sphinx extensions is not available
  (`PR <https://github.com/swyddfa/esbonio/pull/913>`__)

- The language server will fallback to Sphinx's default ``alabaster`` theme if the requested HTML theme is not available
  (`PR <https://github.com/swyddfa/esbonio/pull/916>`__)

There will, of course, be many more situations to handle but it's a start!

pygls
-----

`pygls <https://github.com/openlawlibrary/pygls>`__ *is the language server framework I help to maintain and use in Esbonio*

Work towards the ``2.0`` release continues and this month I finally was able to tackle the migration from Python's low-level to high-level asyncio APIs

- `Move JsonRPCServer.start_io to high-level asyncio API  <https://github.com/openlawlibrary/pygls/pull/506>`__
- `Migrate JsonRPCServer.start_tcp and JsonRPCServer.start_ws to high level asyncio APIs <https://github.com/openlawlibrary/pygls/pull/507>`__
- `Replace "transports" with "writers" <https://github.com/openlawlibrary/pygls/pull/508>`__

I also was able to add TCP and WebSocket support to the language client

- `Add TCP support to pygls' LanguageClient <https://github.com/openlawlibrary/pygls/pull/501>`__
- `Add start_ws method to pygls' LanguageClient <https://github.com/openlawlibrary/pygls/pull/503>`__

Finally, I was able to clean up the `library's support <https://github.com/openlawlibrary/pygls/pull/509>`__ for `Pyodide <https://pyodide.org/>`__ and started thinking about what it would take to embed a simple language client into the docs for demos - disappointingly, it may be harder than I would like!
