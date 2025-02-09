:title: January 2025
:date: 2025-02-09
:tags: blog, monthnotes
:identifier: 20250209T000309

Notes for December/January
==========================

.. container:: post-teaser

   Somehow it is already Feburary...

   So it's about time I tried another one of these month note things, especially since the last one was in :denote:link:`November <20241204T120000>`.

pygls
-----

There has been an `issue <https://github.com/openlawlibrary/pygls/issues/433>`__ in ``pygls`` which has affected ``esbonio`` for a while.
In December I finally got around to trying to fix it and I opened a `pull request <https://github.com/openlawlibrary/pygls/pull/516>`__ introducing a new way of handling request handlers.

Some more testing is needed before you can call it ready, but I'm optimistic it's going to pan out.

esbonio
-------

I also managed to put a fair amount of work into the upcoming ``v1`` of  ``esbonio`` during January

- `Added <https://github.com/swyddfa/esbonio/pull/937>`__ a new ``${venv:<path>}`` config variable, finally making it possible to share ``pythonCommand`` settings for projects that use virtual environments directly

- Made it possible to `customize <https://github.com/swyddfa/esbonio/pull/940>`__ how often Sphinx builds are triggered

- `Re-implemented <https://github.com/swyddfa/esbonio/pull/941>`__ completion suggestions for directive arguments

- Fixed quite a few bugs which made their way into the `v1.0.0b10 release <https://github.com/swyddfa/esbonio/releases/tag/esbonio-language-server-v1.0.0b10>`__ this week.
