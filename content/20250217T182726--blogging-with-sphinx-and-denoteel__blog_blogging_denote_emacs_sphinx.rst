:title: Blogging with Sphinx and denote.el
:date: 2025-05-17
:tags: blog, blogging, denote, emacs, sphinx
:identifier: 20250217T182726

Blogging with Sphinx and ``denote.el``
======================================

.. highlight:: none

.. container:: post-teaser

   If you have spent any time following the Emacs community, you will have likely come across the `denote.el <https://protesilaos.com/emacs/denote>`__ project.
   ``denote.el`` defines a clever file-naming scheme and provides an associated Emacs package containing utilities for managing files which follow this naming scheme.

   In this blog post I outline how I have adopted ``denote.el`` to manage the content on this site and how I've extended `Sphinx <https://www.sphinx-doc.org/en/master/index.html>`__ to take advantage this.

``denote.el`` basics
--------------------

For an in-depth introduction to ``denote.el`` be sure to check out `this video <https://www.youtube.com/watch?v=mLzFJcLpDFI&list=PL8Bwba5vnQK0F6gR0AGOQH48xbLRe_qWC&index=2>`__ however, as mentioned in the introduction, the core of ``denote.el`` is the file-naming sheme::

  <timestamp>--<title>__<tags>

where

- ``<timestamp>`` captures the date and time the file was created and acts as the file's unique identifier
- ``<title>`` a lowercase ``-`` separated string which captures your traditional file name
- ``<tags>`` (called keywords by denote) is a ``_`` separated string of tag names

As an example the filename for this blog post is::

  20250217T182726--blogging-with-sphinx-and-denoteel__blog_blogging_denote_emacs_sphinx.rst

The main benefit in naming your files in this way is that you can perform some fairly sophisticated queries across your files with simple text based searches.

.. _denote-rst:

reStructuredText and ``denote.el``
----------------------------------

While I don't use Emacs all the time, it's safe to say that it has become my default editor when working on personal projects.
So it's nice to be able to make use of the utilities provided by the `denote.el <https://github.com/protesilaos/denote>`__ package when working on this site.

One of the main features provided by the package is to insert `front matter <https://protesilaos.com/emacs/denote#h:13218826-56a5-482a-9b91-5b6de4f14261>`__ into your notes corresponding to the information encoded in the filename **and** to keep the two in sync when either one changes.

``denote.el`` has built in support for several markup formats however, the :external+sphinx:std:ref:`reStructuredText <rst-primer>` syntax used by Sphinx is not one of them.
Of course, being an Emacs package this isn't something that a few lines of lisp cannot solve!

.. admonition:: What about Markdown?

   Yes, both ``denote.el`` and :external+sphinx:std:ref:`Sphinx support <markdown>` Markdown however, I simply prefer reStructuredText 😅

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package denote
     :ensure t
     :hook ((dired-mode . denote-dired-mode))
     :config

     ;; Add reStructuredText support to denote
     (add-to-list 'denote-file-types `(rst
                                       :extension ".rst"
                                       :date-key-regexp "^:date:"
                                       :date-value-function denote-date-iso-8601
                                       :date-value-reverse-function denote-extract-date-from-front-matter
                                       :front-matter ":title: %s\n:date: %s\n:tags: %s\n:identifier: %s\n\n"
                                       :title-key-regexp "^:title:"
                                       :title-value-function identity
                                       :title-value-reverse-function denote-trim-whitespace
                                       :keywords-key-regexp "^:tags:"
                                       :keywords-value-function ,(lambda (ks) (string-join ks ", "))
                                       :keywords-value-reverse-function denote-extract-keywords-from-front-matter
                                       :identifier-key-regexp "^:identifier:"
                                       :identifier-value-function identity
                                       :identifier-value-reverse-function denote-trim-whitespace
                                       :link ":denote:link:`%2$s <%1$s>`"
                                       :link-in-context-regexp ,(concat ":denote:link:`.*?<\\(?1:" denote-id-regexp "\\)>`"))))

Which gives denote the information it needs to read and write its metadata using reStructuredText's :external+sphinx:std:ref:`field list <rst-field-lists>` syntax.

.. literalinclude:: ./20250217T182726--blogging-with-sphinx-and-denoteel__blog_blogging_denote_emacs_sphinx.rst
   :language: rst
   :end-at: :identifier:

It also instructs ``denote`` to use a role called ``denote:link`` when inserting a link to another note, but we'll come back to that a bit later on.

Sphinx and ``denote.el``
------------------------

Again, denote is primarily a file-naming scheme, so you don't *have* to do anything special to get it to work with Sphinx - it will just work\ :sup:`TM`.
However, by extending Sphinx I get to smooth off some rough edges and take advantage of the metadata in the filename to build some nice features.

- :ref:`denote-sphinx-discover-content`
- :ref:`denote-sphinx-mark-posts`
- :ref:`denote-sphinx-pretty-urls`
- :ref:`denote-sphinx-cross-references`


.. note::

   I'm only going to elaborate on some aspects of the code underpinning this, so if you want the full details be sure to take a look at the `complete implementation <https://github.com/alcarney/blog/blob/6fecce876ffbb808390a6b59a62ae081abaaf395/extensions/denote>`__ of the denote extension.

   - The `Record <https://github.com/alcarney/blog/blob/6fecce876ffbb808390a6b59a62ae081abaaf395/extensions/denote/record.py#L15>`__
     dataclass captures all of the information encoded in and derived from a denote style filename.

   - The `Denote <https://github.com/alcarney/blog/blob/6fecce876ffbb808390a6b59a62ae081abaaf395/extensions/denote/domain.py#L83>`__ Sphinx :external:std:ref:`Domain <domain-api>` is the main store of ``Record`` instances and can be thought of as the "backend" of the extension.

   - The rest of the extension uses the APIs provided by the two above classes to integrate with Sphinx at various points in the build lifecycle.

.. _denote-sphinx-discover-content:

Discovering Content
^^^^^^^^^^^^^^^^^^^

Thanks to the ``source-read`` event it's trivial to build an index of all the files in the Sphinx project that have a denote style filename

.. literalinclude:: ../extensions/denote/__init__.py
   :language: python
   :start-at: def discover_records
   :end-before: def parse_records

Once Sphinx has parsed the file the ``doctree-read`` event is emitted, which we can use to extract additional information from the file's front matter and content.

.. literalinclude:: ../extensions/denote/__init__.py
   :language: python
   :start-at: def parse_records
   :end-before: def generate_collections

I primarily use this to change the post date or title without having to change the identifier or title portions of the filename - which would lead to broken links.

.. _denote-sphinx-mark-posts:

Using Tags to Mark Blog Posts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are currently two main sections to this site - blog posts and notes (the code section is broken and we can talk about dotfiles another time! 😅).

The obvious solution to this would be to create a ``blog/`` folder and a ``notes/`` folder and call it a day.
However, denote lends itself well to having just a folder full of files and I quite liked the idea of dumping all my files into a ``content/`` folder and using tags to... *ahem* denote different types of content.

This allows for a nice workflow where something can start as a note but can easily be promoted to a blog post if needed.

Implementing this quite straightforward, choose a name for the tag (``blog``) and when it is found set the corresponding flag on the ``Record`` instance. Note that I also remove the ``blog`` tag from the list of tags so that it does not appear in the list of tags in the sidebar.

.. code-block:: python

   if (match := FILENAME_PATTERN.match(filename)) is None:
       return None

   tags = match.group("tags").split("_")

   try:
       tags.remove("blog")
       is_blogpost = True
   except ValueError:
       is_blogpost = False

   return Record(
       ...,
       tags=tags,
       is_blogpost=is_blogpost,
   )

Then make use of the flag when ever it's relevant, for example when building the index of all blog posts

.. code-block:: python

   def add_record(self, docname: str, record: Record):
       """Add a record to the domain"""
       record.docname = docname
       self.records[docname] = record

       if record.is_blogpost:
           self.posts[docname] = record


.. _denote-sphinx-pretty-urls:

Pretty URLs
^^^^^^^^^^^

You may have noticed that the url to this page is not ::

  https://www.alcarney.me/content/20250217T182726--blogging-with-sphinx-and-denoteel__blog_blogging_emacs_sphinx/

This is because I have created a custom Sphinx `builder <https://github.com/alcarney/blog/blob/6fecce876ffbb808390a6b59a62ae081abaaf395/extensions/denote/builder.py#L16>`__, derived from the standard ``DirectoryHTMLBuilder`` and which implements the following url scheme

- Blog posts are written to ``/blog/<year>/<title>`` e.g. ``/blog/2025/blogging-with-sphinx-and-denoteel``
- Notes are written to ``/notes/<identifier>`` e.g. ``/notes/20250217T182726``

.. warning::

   This involves overwriting the ``get_target_uri`` and ``get_output_path`` methods on the base builder class, which I am 90% sure are **not** part of Sphinx's public API. This can and `will <https://github.com/alcarney/blog/commit/61c21eb612d247ab34891ad76e74a27702ffef27#diff-a634783132b52e5d734032dc004c9ae0bb4db3ba32b3108a5b19714be4d7635d>`__ break on you between Sphinx versions!

.. _denote-sphinx-cross-references:

Cross References
^^^^^^^^^^^^^^^^

Remember back in the :ref:`denote-rst` section I instructed denote to use the following syntax when inserting links?

.. code-block:: elisp

   :link ":denote:link:`%2$s <%1$s>`"
   :link-in-context-regexp ,(concat ":denote:link:`.*?<\\(?1:" denote-id-regexp "\\)>`"

This was so I could define a ``:denote:link:`` role as part of the ``Denote`` domain

.. code-block:: python

   class Denote(Domain):
       """A domain for denote style note taking."""
       name = "denote"
       roles = {
           "link": XRefRole(),
       }


and implement the :external:py:meth:`~sphinx.domains.Domain.resolve_xref` method so that links generated by ``denote-link`` and related commands link to the correct page when generating the html for this site

.. literalinclude:: ../extensions/denote/domain.py
   :dedent:
   :language: python
   :start-at: def resolve_xref

.. admonition:: Example

   Here are links to :denote:link:`20250216T190756` and my :denote:link:`neovim config <20250216T190621>`.

   See below for how this looks in the source for this page

   .. literalinclude:: ./20250217T182726--blogging-with-sphinx-and-denoteel__blog_blogging_denote_emacs_sphinx.rst
      :language: rst
      :start-at: .. admonition:: Example
      :end-at: Generating


Generating Feeds and Archives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. role:: strike
   :class: line-through

This is mainly :strike:`stolen from` inspired by the `ablog <https://ablog.readthedocs.io/en/stable/>`__ extension (which is a great extension if you want a Sphinx-powered blog by the way)

Using the ``html-collect-pages`` event it's possible to generate entirely new pages during the build process and since all of denote's metadata is right there in the filename it's easy to select just the subsets of files you are interested in

Currently I generate

- An index of all blog posts

  .. literalinclude:: ../extensions/denote/__init__.py
     :dedent:
     :language: python
     :start-at: def generate_collections
     :end-before: context.update

- An RSS feed of all blog posts

  .. literalinclude:: ../extensions/denote/__init__.py
     :dedent:
     :language: python
     :start-at: context.update
     :end-at: yield ("blog/atom"

- An index of all blog posts in a given year

  .. literalinclude:: ../extensions/denote/__init__.py
     :dedent:
     :language: python
     :start-at: by_year =
     :end-at: yield (f"blog/{year}"

- An index of all blog posts *and notes* with a given tag

  .. literalinclude:: ../extensions/denote/__init__.py
     :dedent:
     :language: python
     :start-at: by_tag =
     :end-at: yield (f"tag/{tag}"

I still need to make it so that I can pull out a record's content in the ``blog/collection.html`` template - you may notice that the RSS feed only contains post titles at the moment!

But for the HTML at least I was able to cheat and use `HTMX <https://htmx.org/>`__ to pull the content through when the post scrolls into view.

.. literalinclude:: ../_templates/blog/collection.html
   :language: jinja
   :dedent:
   :start-at: Use HTMX
   :end-at: /div

Which of course isn't ideal, especially when you realise any links in the inserted content will be broken! 😅


Next Steps
----------

As you might guess this is still quite immature and there's plenty that I'd still like to explore or needs fixing!

- **Fixing search**

  The search bar you see in the sidebar is pretty much useless in its current form.
  Yes, you can type something in and it will take you to a search results page, but all the links on that page will be broken!

- **Fixing notes**

  While I could send you a direct link to one of the notes on this site and you could see it, there's no actual way to browse them at this time.

- ``denote-sequence``

  There are many pages on this site which form a series of some kind.
  However, the only way to handle this currently is for me to remember to add relevant links forwards and backwards in the chain!

  Building on a part of the denote file-naming scheme I've ignored so far - the signature - the `denote-sequence <https://protesilaos.com/emacs/denote-sequence>`__ package provides a mechanism for encoding hierarchical sequences of related notes which would be perfect for my use case!

- **Knowledge Graphs**

  I doubt views like Obsidian's `graph view <https://help.obsidian.md/plugins/graph>`__ are that useful in practise - but they are cool to look at!
  If nothing else it would be a fun excerise to try and build a similar view for this site.
