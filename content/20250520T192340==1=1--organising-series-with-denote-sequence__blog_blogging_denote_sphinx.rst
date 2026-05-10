:title: Organising Series with denote-sequence
:date: 2026-05-11
:tags: blog, blogging, denote, sphinx
:identifier: 20250520T192340
:signature: 1=1

Organising Series  with ``denote-sequence``
===========================================

.. highlight:: none

.. container:: post-teaser

   I've never had a good way of grouping a series of related posts on this site.
   However now that I can use `denote <https://protesilaos.com/emacs/denote>`__ style filenames, a natural way of acheiving this would be to rely on one of the schemes provided by `denote-sequence <https://protesilaos.com/emacs/denote-sequence>`__ to encode this information.

   In this blog post I outline how I built on my :denote:link:`previous post <20250217T182726>` to add support for denote sequences to Sphinx.


``denote.el`` basics - revisted
-------------------------------

Since I was not using it at the time, I neglected to mention a component of denote's file naming scheme::

  <timestamp>==<signature>--<title>__<tags>

where:

- ``<timestamp>`` captures the date and time the file was created and acts as the file's unique identifier,
- ``<signature>`` **NEW!**
- ``<title>`` a lowercase ``-`` separated string which captures your traditional file name,
- ``<tags>`` (called keywords by denote) is a ``_`` separated string of tag names.

To quote the `documentation <https://protesilaos.com/emacs/denote#h:4e9c7512-84dc-4dfb-9fa9-e15d51178e5d>`__:

.. pull-quote::

   File names can include an arbitrary string of alphanumeric characters in the SIGNATURE field. Signatures have no clearly defined purpose and are up to the user to define.

The ``denote-sequence`` extension defines a number of schemes for use with this field allowing for hierarchies of related notes to be defined.

Personally I prefer the numeric scheme

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package denote-sequence
     :ensure t
     :after denote
     :custom
     (denote-sequence-scheme 'numeric))

Which provides the following pattern::

  20250102T120001==1--top-level-one.txt
  20250102T120004==1=1--child-one.txt
  20250102T120005==1=2--child-two.txt

  20250102T120002==2--top-level-two.txt
  20250102T120007==2=1--child-one.txt
  20250102T120008==2=1=1--nested-child-one.txt

  20250102T120003==3--top-level-three.txt

and so on.


reStructuredText and ``denote.el``
----------------------------------

As before I am using reStructuredText, which ``denote.el`` does not support by default.
To use ``denote-sequence`` we need to extend the ``rst`` definition from last time to include support for the signature field.

.. code-block:: elisp
   :project: emacs
   :filename: init.el
   :emphasize-lines: 12, 16-18

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
                                       :front-matter ":title: %s\n:date: %s\n:tags: %s\n:identifier: %s\n:signature: %s\n\n"
                                       :title-key-regexp "^:title:"
                                       :title-value-function identity
                                       :title-value-reverse-function denote-trim-whitespace
                                       :signature-key-regexp ":signature:"
                                       :signature-value-function identity
                                       :signature-value-reverse-function denote-trim-whitespace
                                       :keywords-key-regexp "^:tags:"
                                       :keywords-value-function ,(lambda (ks) (string-join ks ", "))
                                       :keywords-value-reverse-function denote-extract-keywords-from-front-matter
                                       :identifier-key-regexp "^:identifier:"
                                       :identifier-value-function identity
                                       :identifier-value-reverse-function denote-trim-whitespace
                                       :link ":denote:link:`%2$s <%1$s>`"
                                       :link-in-context-regexp ,(concat ":denote:link:`.*?<\\(?1:" denote-id-regexp "\\)>`"))))

Sphinx and ``denote.el``
------------------------

.. note::

   This section contains just the highlights, see the `complete implementation <https://github.com/alcarney/blog/tree/960d28fd049e5df1abba0caa289ebcaf40630c9c/extensions/denote>`__ for full details.

The :denote:link:`previous post <20250217T182726>` did all the heavy lifting when it comes to the Sphinx integration, so adding ``denote-sequence`` support was surprisingly straightforward, only requiring a few tweaks to make the information available to the relevant components.

Discovering Sequences
^^^^^^^^^^^^^^^^^^^^^

To detect which files belong to which sequence (if any), the code for parsing filenames needed to be updated to handle signatures

.. code-block:: python

   # denote/record.py
   FILENAME_PATTERN = re.compile(
       r"""
       (?P<identifier>\d{8}T\d{6})
       (==(?P<signature>[^-]+))?
       --(?P<title>[^_]+)
       __(?P<tags>[^.]+)
       """,
       re.VERBOSE,
   )

   @dataclasses.dataclass
   class Record:
       ...

       signature: str | None
       sequence: tuple [int, ...] | None

       @classmethod
       def parse(cls, filename: str | None) -> Record | None:

           if (match := FILENAME_PATTERN.match(filename)) is None:
               return None

           ...

           sequence = None
           if (signature := match.group("signature")) is not None:
               sequence = tuple(int(s) for s in signature.split("="))

           ...

           return cls(
              ...
              signature=signature,
              sequence=sequence,
           )

Indexing Sequences
^^^^^^^^^^^^^^^^^^

To represent a sequence hierachy I introduced this ``Sequence`` class.

.. code-block:: python

   @dataclasses.dataclass
   class Sequence:
       """Used to represent the hierarchy described by a sequence."""

       identifier: str | None = dataclasses.field(default=None)
       """The identifier of the note at this node in the sequence, if known"""

       children: dict[int, Sequence] = dataclasses.field(default_factory=dict)
       """The list of child nodes in the sequence, if any"""

Storing child nodes in a dictionary, rather than a list allows us to support sequences with gaps, or constructing sequences out of order without too much extra thought.

I don't think I mentioned it last time, but to make it easy to select records by certain criteria all records are stored in a modified ditctionary that maintains numerous indexes of identifiers:

.. code-block:: python

   class RecordCollection(collections.UserDict[str, Record]):
       """A dictionary of records that also maintains a number of groupings"""

       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)

           self._by_tag = {}
           self._by_year = {}
           self._by_identifier: dict[str, str] = {}
           self._by_sequence: Sequence = Sequence()

When building the sequence hierachy the main thing to consider is that sequences can be constructed out of order:

.. code-block:: python

   def __setitem__(self, key: str, item: Record) -> None:
       super().__setitem__(key, item)

       ...

       if (sequence := item.sequence) is not None:
           node = self._by_sequence

           for idx in sequence:
               if idx not in node.children:
                   node.children[idx] = Sequence()

               node = node.children[idx]

           node.identifier = item.identifier


Rendering Sequences
^^^^^^^^^^^^^^^^^^^

Currently, the main way sequences are shown on this site is the "Related Pages" section in the sidebar which is only shown
on pages that are part of a sequence:

.. code-block:: html+jinja

   {%- if record and record.sequence %}
   <section class="post-related">
     <h5>Related Pages</h5>
     {%- set sequence = denote.records.sequence_hierarchy(record.sequence) %}
     {{ render_sequence(sequence) }}
   </section>
   {%- endif %}

Using the index automatically maintained by the ``__setitem__`` method in the previous section, the implementation of the ``sequence_hierarchy`` helper is easy enough.
By definition, all records in a sequence will start with the same number so we only need to consider the first element of a sequence's tuple:

.. code-block:: python

   def sequence_hierarchy(self, key: tuple[int, ...]) -> Sequence:
       """Return the hierarchy of all posts in a sequence"""
       return self._by_sequence.children[key[0]]

Going back to the template, the ``render_sequence`` macro is given the top-level ``Sequence`` node and recurses down the hierarchy rendering out a nested list as it goes:

.. code-block:: html+jinja

   {% macro render_sequence(node) -%}
     {%- set item = denote.records.find(identifier=node.identifier) %}
     {%- if node.children | length > 0 %}
       {{ render_node(item) }}
       <ul>
         {%- for child in node.children.values() %}
         <li>{{ render_sequence(child) }}</li>
         {%- endfor %}
       </ul>
     {% else %}
       {{ render_node(item) }}
     {%- endif %}

   {%- endmacro %}

Where the record at each node in the sequence is given to the ``render_node``  macro to generate the link to the corresponding page.

.. code-block:: html+jinja

   {% macro render_node(node) -%}
     {% if node.identifier != record.identifier %}
     <a class="reference internal" title="{{ node.title }}" href="{{ pathto(node.url) }}">
       {{ node.title }}
     </a>
     {% else %}
     <a class="current" title="{{ node.title }}" href="#">
       {{ node.title }}
     </a>
     {% endif %}
   {% endmacro -%}
