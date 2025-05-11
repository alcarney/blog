:title: Blogging with Sphinx and denote.el
:date: 2025-04-09
:tags: blogging, emacs, sphinx
:identifier: 20250217T182726

Blogging with Sphinx and ``denote.el``
======================================

.. highlight:: none

.. container:: post-teaser

   If you have spent any time following the Emacs community, you will have likely come across the `denote.el <https://protesilaos.com/emacs/denote>`__ project.
   ``denote.el``, primarily, is a clever file-naming scheme with an associate Emacs package which provides utilities for managing files that follow this naming scheme.

   In this blog post I outline how I have adopted this file-naming scheme to manage the content on this site and how I've extended `Sphinx <https://www.sphinx-doc.org/en/master/index.html>`__ to take advantage of the information encoded in the file names.

``denote.el`` basics
--------------------

For an in-depth introduction to ``denote.el`` be sure to check out `this video <https://www.youtube.com/watch?v=mLzFJcLpDFI&list=PL8Bwba5vnQK0F6gR0AGOQH48xbLRe_qWC&index=2>`__ however, as mentioned in the introduction, the core of ``denote.el`` is the file-naming sheme::

  <timestamp>--<title>__<tags>.ext

where

- ``<timestamp>`` captures the date and time the file was created and acts as the file's unique identifier
- ``<title>`` a lowercase ``-`` separated string which captures your traditional file name
- ``<tags>`` (called keywords by denote) is a ``_`` separated string of tag names

As an example the filename for this blog post is::

  20250217T182726--blogging-with-sphinx-and-denoteel__blog_blogging_emacs_sphinx.rst

The main benefit in naming your files in this way is that you can perform some fairly sophisticated queries across your files with simple text based searches.

reStructuredText and ``denote.el``
----------------------------------

While I don't use Emacs all the time, it's safe to say that it has become my default editor when working on personal projects.
So it's nice to be able to make use of the utilities provided by the `denote.el <https://github.com/protesilaos/denote>`__ package when working on this site.

One of the main features provided by the package is to insert `front matter <https://protesilaos.com/emacs/denote#h:13218826-56a5-482a-9b91-5b6de4f14261>`__ into your notes corresponding to the information encoded in the filename **and** to keep the two in sync when either one changes.

``denote.el`` has built in support for several markup formats however, the :external+sphinx:std:ref:`reStructuredText <rst-primer>` syntax used by Sphinx is not one of them.
Of course, being an Emacs package this isn't something that a few lines of lisp cannot solve!

.. admonition:: What about Markdown?

   Yes, both ``denote.el`` and Sphinx support :external+sphinx:std:ref:`markdown` however, I simply prefer reStructuredText 😅

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

.. literalinclude:: ./20250217T182726--blogging-with-sphinx-and-denoteel__blogging_emacs_sphinx.rst
   :language: rst
   :end-at: :identifier:

It also instructs ``denote`` to use a role called ``denote:link`` when inserting a link to another note, but we'll come back to that a bit later on.

Sphinx and ``denote.el``
 ------------------------

Again, denote is primarily a file-naming scheme, so you don't *have* to do anything special to get it to work with Sphinx - it will just work\ :sup:`TM`.
However, by extending Sphinx I get to smooth off some rough edges and take advantage of the metadata in the filename to build some nice features.

- :ref:`denote-sphinx-mark-posts`
- :ref:`denote-sphinx-pretty-urls`
- :ref:`denote-sphinx-cross-references`

I'm only going to elaborate on some aspects of the code underpinning this, so if you want the full details be sure to take a look at the `complete implementation <https://github.com/alcarney/blog/blob/6fecce876ffbb808390a6b59a62ae081abaaf395/extensions/denote>`__ of the denote extension.

.. _denote-sphinx-mark-posts:

Using Tags to Mark Blog Posts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are currently two main sections to this site - blog posts and notes.

The obvious solution to this would be to create a ``blog/`` folder and a ``notes/`` folder and call it a day.
However, denote lends itself well to having just a folder full of files and I quite liked the idea of dumping all the content into a single folder and using the presence of a special tag to indicate the content type.

This allows for a nice workflow where something can start of as a note but grow into a fully fledged blog post over time.

To implement this, I have a simple `Record <https://github.com/alcarney/blog/blob/6fecce876ffbb808390a6b59a62ae081abaaf395/extensions/denote/record.py#L15>`__
dataclass that captures the information encoded in a denote filename.
Then when constructing an instance of this class from the filename it's easy enough to look for a ``blog`` tag and use it to set a flag indicating that the file represents a blog post.

.. literalinclude:: ../extensions/denote/record.py
   :language: python
   :dedent:
   :start-at: @classmethod
   :end-before: @property

.. _denote-sphinx-pretty-urls:

Pretty URLs
^^^^^^^^^^^

You may have noticed that the url to this page is not ::

  https://www.alcarney.me/content/20250217T182726--blogging-with-sphinx-and-denoteel__blog_blogging_emacs_sphinx/



.. _denote-sphinx-cross-references:

Cross References
^^^^^^^^^^^^^^^^

Generating Feeds and Archives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. role:: strike
   :class: line-through

This is mainly :strike:`stolen from` inspired by the `ablog <https://ablog.readthedocs.io/en/stable/>`__ extension (which is a fantastic option if you want a Sphinx-powered blog by the way)

Using the ``html-collect-pages`` event it's possible to generate entirely new pages during the build process and since all of denote's metadata is right there in the filename it's easy to select just the subsets you are interested in

.. literalinclude:: ../extensions/denote/__init__.py
   :language: python
   :start-at: def generate_collections
   :end-before: def update_html_context

Still to Come
-------------

- Fixing search
- ``denote-sequence``
