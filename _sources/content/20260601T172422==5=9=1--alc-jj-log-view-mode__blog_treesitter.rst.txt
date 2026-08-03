:title: alc-jj-log-view-mode
:date: 2026-06-07
:tags: blog, treesitter
:identifier: 20260601T172422
:signature: 5=9=1

Building ``alc-jj-log-view-mode``
=================================

.. highlight:: none

.. container:: post-teaser

   When I was first learning ``git``, it wasn't until I internalised how the various commands manipulated the commit graph did it really click for me.
   So even though I'm primarily using ``jj`` in my personal projects these days, I still find myself staring at the revision graph most of the time, which usually means running ``jj log`` after every other command!

   But instead, what if I wrote an Emacs major-mode that would display the output from ``jj log`` and let me manipulate the graph directly by running the relevant commands in the background?
   And what if that major-mode was based on tree-sitter?

I'm sure you're thinking that using tree-sitter for this is overkill, and you are probably right!
But if nothing else, this should be fun!

Getting Started with tree-sitter
--------------------------------
If you follow the `getting started <https://tree-sitter.github.io/tree-sitter/creating-parsers/1-getting-started.html>`__ guide on the tree-sitter website it's going to instruct you to run the ``tree-sitter init`` command in a directory::

   $ tree-sitter init
   ✔ Parser name · jjlog
   ✔ CamelCase name · JJLog
   ✔ Title (human-readable name) · jj log
   ✔ Description · l
   ✔ Repository URL ·
   ✔ Funding URL ·
   ✔ TextMate scope · source.jjlog
   ✔ File types (space-separated) · jjlog
   ✔ Version · 0.1.0
   ✔ License · MIT
   ✔ Author name · Alex
   ✔ Author email ·
   ✔ Author URL ·
   ✔ Package namespace · io.github.tree-sitter
   Bindings: c
   Your current configuration:
   {
     "name": "jjlog",
     "camelcase": "JJLog",
     "title": "jj log",
     "description": "l",
     "repository": "",
     "funding": "",
     "scope": "source.jjlog",
     "file_types": [
       "jjlog"
     ],
     "version": "0.1.0",
     "license": "MIT",
     "author": "Alex",
     "email": "",
     "url": "",
     "namespace": "io.github.tree-sitter",
     "bindings": {
       "c": true,
       "go": false,
       "java": false,
       "node": false,
       "python": false,
       "rust": false,
       "swift": false,
       "zig": false
     }
   }
   ✔ Does the config above look correct? · yes

This results in the following project structure::

   $ tree
   .
   ├── bindings
   │   └── c
   │       ├── tree_sitter
   │       │   └── tree-sitter-jjlog.h
   │       └── tree-sitter-jjlog.pc.in
   ├── CMakeLists.txt
   ├── grammar.js
   ├── Makefile
   ├── package.json
   ├── src
   │   ├── grammar.json
   │   ├── node-types.json
   │   ├── parser.c
   │   └── tree_sitter
   │       ├── alloc.h
   │       ├── array.h
   │       └── parser.h
   └── tree-sitter.json

   6 directories, 13 files

Which is great... if you intend to ship your parser to the wider world and make it easy to integrate into other projects.
However, if you are only looking to hack something together for use with your Emacs config, you can get away with a lot less.

Emacs Quick Start
^^^^^^^^^^^^^^^^^

#. The only source file you really need is the ``grammar.js`` file (example below is adapted from the tree-sitter `getting started <https://tree-sitter.github.io/tree-sitter/creating-parsers/1-getting-started.html>`__) guide.

   .. code-block:: js

      /**
       * @file
       * @author
       * @license MIT
       */

      /// <reference types="tree-sitter-cli/dsl" />
      // @ts-check

      export default grammar({
        name: "jjlog",

        rules: {
          // TODO: add the actual grammar rules
          source_file: $ => "hello"
        }
      });

#. To build the grammar, run the following commands in the directory containing the ``grammar.js`` file::

     $ tree-sitter generate
     $ tree-sitter build

   Which results in the following::

      $ tree
      .
      ├── grammar.js
      ├── parser.so
      └── src
          ├── grammar.json
          ├── node-types.json
          ├── parser.c
          └── tree_sitter
              ├── alloc.h
              ├── array.h
              └── parser.h

      3 directories, 8 files

   .. note::

      This approach does come with a warning::

        Warning: No `tree-sitter.json` file found in your grammar, this file is required to generate with ABI 15. Using ABI version 14 instead.
        This file can be set up with `tree-sitter init`. For more information, see https://tree-sitter.github.io/tree-sitter/cli/init.

      However, since Emacs seems perfectly happy with an ABI v14 grammar at the moment, I've decided to ignore it for now.

#. So that Emacs can find the grammar, the ``parser.so`` file needs to be moved to ``.emacs.d/tree-sitter`` and renamed to
   ``libtree-sitter-<lang>.so``::

     $ mv parser.so ~/.emacs.d/tree-sitter/libtree-sitter-jjlog.so

#. With the parser in place, it should now be possible to call it from Emacs::

     ELISP> (treesit-parse-string "hello" 'jjlog)
     #<treesit-node source_file in 1-6>

.. _jj-log-grammar:

Writing The Grammar
-------------------

With a hello world in place, it's time to write the actual grammar rules.
Let's consider the output from ``jj log``::

   ❯ jj log
   @  qnsxyznm alcarneyme@gmail.com 2026-06-05 18:39:50 e4043b79
   │  (no description set)
   │ ○  qlvvlput alcarneyme@gmail.com 2026-04-23 09:44:00 f51dbe3d
   ├─╯  message method tracking
   ◆  onllqnnq github.action@users.noreply.github.com 2026-03-25 12:19:06 main* c0ae7d03
   │  chore: update CONTRIBUTORS.md
   ~  (elided revisions)
   │ ×  mslzorpz alcarneyme@gmail.com 2026-03-23 20:49:53 push-mslzorpzmxww* 60571548 (conflict)
   ├─╯  feat: allow passing a custom workspace implemenation
   ◆  twmmxqyw github.action@users.noreply.github.com 2026-03-19 10:16:51 main@origin 8c13d110
   │  chore: update CONTRIBUTORS.md
   ~

The easiest way to model this is as a linear sequence of changes.
While it would be interesting to see if you could mirror the structure of the revision tree in the parse tree, I'm going to assume it's not an easy task.
Plus, I don't think I need that level of detail for this.

So, for the time being I'm going to declare the line block characters as ``extras`` so that they are effectively treated as whitespace:

.. code-block:: js
   :project: emacs
   :template: treesit-grammar
   :filename: tree-sitter-grammars/jjlog/grammar.js

   name: "jjlog",

   extras: $ => [
     /\s/, '|', '├', '─', '╯',
   ],

   rules: {
     source_file: $ => repeat($._revision),

     _revision: $ => choice(
       $.revision,
       $.elided_revisions,
     ),

Modelling the elided revisions as a separate node type means that when it comes to implementing :ref:`navigation <alc-jj-log-view-navigation>` it's trivial to skip over the elided revisions.

The type of each change is denoted by the symbol representing that change's node in the revision graph:

.. code-block:: js
   :project: emacs
   :template: treesit-grammar
   :filename: tree-sitter-grammars/jjlog/grammar.js

   revision: $ => seq(
     $._node_type,
     $._change_metadata,
     optional('(conflict)'),
     $._description,
   ),

   _node_type: $ => choice($.working_copy, $.immutable_change, $.conflicted_change, $.normal_change),

   working_copy:      $ => '@',
   immutable_change:  $ => '◆',
   conflicted_change: $ => '×',
   normal_change:     $ => '○',
   elided_revisions:  $ => seq('~', optional('(elided revisions)')),

The definition of each of the metadata fields is straightforward enough.

.. code-block::
   :project: emacs
   :template: treesit-grammar
   :filename: tree-sitter-grammars/jjlog/grammar.js

     _change_metadata: $ => seq(
       field("change_id", $.ref),
       field("author", $.email),
       field("timestamp", $.datetime),
       repeat($.ref),
     ),

     ref:         $ => /[-a-z0-9@*A-z]+/,
     email:       $ => /[^\s]+@[^\s]+/,
     datetime:    $ => /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/,

     _description: $ => seq(/[\n\r]/, $.description, /[\n\r]/),
     description: $ => /[^\n\r]+/,
   }

The ``tree-sitter parse`` command can be used to quickly generate a parse tree for the example we considered at the start of this section::

  $ jj log > example-output
  $ tree-sitter parse example-output
  (source_file
    (revision
      (working_copy) change_id: (ref) author: (email) timestamp: (datetime) (ref) (description))
    (ERROR (ERROR))
    (revision
      (normal_change) change_id: (ref) author: (email) timestamp: (datetime) (ref) (description))
    (revision
      (immutable_change) change_id: (ref) author: (email) timestamp: (datetime) (ref) (ref) (description))
    (elided_revisions)
    (ERROR (ERROR))
    (revision
      (conflicted_change) change_id: (ref) author: (email) timestamp: (datetime) (ref) (ref) (description))
    (revision
      (immutable_change) change_id: (ref) author: (email) timestamp: (datetime) (ref) (ref) (description))
    (elided_revisions))

**Note:** *I have edited the output to merge lines and omit character ranges for brevity.*

You may have noticed the ``ERROR`` nodes, indicating that the grammar isn't properly handling the case where revisions branch off the mainline (e.g. ``│ ○  ...``) however, thanks to tree-sitter's error recovery, I've been able to ignore them!

Defining the Major Mode
-----------------------

With the grammar written it's time to write my first major-mode!

For details on how to define a tree-sitter based major-mode, `this guide <https://www.masteringemacs.org/article/lets-write-a-treesitter-major-mode>`__ from Mastering Emacs provides an excellent starting point.

When declaring a major-mode, you often base your mode on a more fundamental mode to inherit a lot of existing functionality for free.
Initially I thought of basing mine on ``log-view-mode`` (the mode you get when running ``vc-print-log``).
But since the navigation commands are all powered by regular expressions I didn't think I would gain much and so based it on ``special-mode`` instead:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (define-derived-mode alc-jj-log-view-mode special-mode "jj-log"
     "Major mode for viewing and manipulating the jj log"
     (when (treesit-ready-p 'jjlog)
       (treesit-parser-create 'jjlog)
       (alc-jj-log-view-ts-setup)))


Syntax Highlighting
^^^^^^^^^^^^^^^^^^^

Or in Emacs parlance, font locking.

I highly recommend you check out the `guide from Mastering Emacs <https://www.masteringemacs.org/article/lets-write-a-treesitter-major-mode>`__ if you are interested in the details.
Essentially, syntax highlighting a tree-sitter mode boils down to:

- Writing queries that apply faces to matches (e.g. ``((elided_revisions) @font-lock-comment-face)``, and
- assigning them to a named feature (e.g. ``:feature elided``).

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defvar alc-jj-log-view-font-lock-rules
     '(:language jjlog
       :override t
       :feature elided
       ([((elided_revisions) @font-lock-comment-face)])
       :language jjlog
       :override t
       :feature working-copy
       ([((working_copy) @success)])
       :language jjlog
       :override t
       :feature refs
       ([((revision (ref) @font-lock-function-name-face))])
       :language jjlog
       :override t
       :feature conflicted
       ([(conflicted_change) "(conflict)"] @error)
       :language jjlog
       :override t
       :feature metadata
       ([(email) (datetime)] @shadow)
       :language jjlog
       :override t
       :feature change-ids
       ([((revision change_id: (ref) @font-lock-keyword-face))])))

I adopted the ``defvar`` approach suggested in the Mastering Emacs article, though that's probably only necessary if you intend to publish your mode for other people to use.

Applying these rules to each time the major-mode is activated is the responsibility of the ``alc-jj-log-view-ts-setup`` function referenced in the previous section.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-ts-setup ()
     "Setup treesit for alc-jj-log-view mode."
     (setq-local font-lock-defaults nil)
     (setq-local treesit-font-lock-feature-list
                 '((change-ids
                    conflicted
                    elided
                    metadata
                    refs
                    working-copy)))

     (setq-local treesit-font-lock-settings
                  (apply #'treesit-font-lock-rules alc-jj-log-view-font-lock-rules))
     (treesit-major-mode-setup))

The ``treesit-font-lock-feature-list`` variable is interesting as you can sort your font lock rules into different levels, allowing people to opt into more or less highlighting based on their value of ``treesit-font-lock-level``.
Since I'm the only user, I've put everything into a single level.

.. termshot:: /images/jjlog-parse-tree.cast

The above screenshot shows the syntax highlighting rules in action in the top window, while the bottom uses ``treesit-explore-mode`` to visualise the corresponding parse tree.

.. _alc-jj-log-view-navigation:

Navigation
^^^^^^^^^^

Thanks to the parse tree, it's relatively straightforward to implement some navigation commands.
For now, all I'm really looking for is the ability to navigate between nodes in the graph by pressing :kbd:`n` and :kbd:`p`.

Since I use `combobulate <https://github.com/mickeynp/combobulate>`__ already for tree-sitter based navigation in other modes, I thought it made sense to try and leverage it here as well.
While I still don't understand the internals of combobulate that well, I was able to piece together the following navigation ruleset:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defvar alc-jj-log-view-combobulate-definitions
     '((procedures-sibling
        '((:activation-nodes
           ((:nodes ("revision")))
           :selector (:choose node :match-siblings (:match-rules ("revision"))))))))

Which I derived from the following:

- `combobulate-navigation.el <https://github.com/mickeynp/combobulate/blob/4e8cf0df8e22cdaf87c6637eddb60500f0055f46/combobulate-navigation.el#L1082-L1091>`__
  contains the definitions of ``combobulate-navigate-next`` and ``combobulate-navigate-previous`` which rely on a ``procedures-sibiling`` ruleset to identify what the next/previous syntax nodes should be:

  .. code-block:: elisp
     :emphasize-lines: 2

     (defun combobulate--navigate-next ()
       (with-navigation-nodes (:skip-prefix t :procedures (combobulate-read procedures-sibling))
         (combobulate-nav-get-next-sibling
          (combobulate--get-nearest-navigable-node))))

- `combobulate-html.el <https://github.com/mickeynp/combobulate/blob/4e8cf0df8e22cdaf87c6637eddb60500f0055f46/combobulate-html.el#L210-L214>`__
  had an example rule definition that appears to say "choose the next node of the same type" which I was able to adapt for my grammar:

  .. code-block:: elisp

     (procedures-sibling
      '((:activation-nodes
         ((:nodes
           ("attribute")))
         :selector (:choose node :match-siblings (:match-rules ("attribute"))))

All that's left is to wrap the rules in a new language definition:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (define-combobulate-language
    :name jjlog
    :language jjlog
    :major-modes (alc-jj-log-view-mode)
    :custom alc-jj-log-view-combobulate-definitions)

Now, the ``combobulate-navigate-next`` and ``combobulate-navigate-previous`` commands are bound by default to :kbd:`C-M-n` and :kbd:`C-M-p` but it's easy enough to rebind them using the keymap for ``alc-jj-log-view-mode``.

Commands
^^^^^^^^

Finally, we arrive at the reason why I've gone to all this effort - I want to be able to manipulate the log from this buffer!
I'm sure there's a lot I could add, but the commands I'm going to use most often are:

- :ref:`alc-jj-log-view-new-before`
- :ref:`alc-jj-log-view-new-after`
- :ref:`alc-jj-log-view-edit`
- :ref:`alc-jj-log-view-describe`
- :ref:`alc-jj-log-view-reload`

Most of these are going to require identifying the change id for the revision at point so we may as well solve that now.
The grammar and resulting parse tree is simple enough that we only need to search upwards until we find the containing ``revision`` node and selecting the ``change_id`` field.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view--change-at-point ()
     "Return the change id for the revision under point, if point is not on a revision
   returns nil."
     (let ((node (treesit-node-at (point))))
       (while (not (or (string= (treesit-node-type node) "revision")
                       (null (treesit-node-parent node))))
         (setq node (treesit-node-parent node)))
       ;; Make sure we found a revision
       (if (string= (treesit-node-type node) "revision")
           (substring-no-properties
            (treesit-node-text
             (treesit-node-child-by-field-name node "change_id"))))))

I'm sure it will also be useful to have the ability to select a revision given a change id.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view--select-revision-with-change-id (change-id)
     "Given a CHANGE-ID move point to the corresponding revision."
     (if-let ((nodes (treesit-filter-child
                      (treesit-buffer-root-node)
                      (lambda (n) (string= change-id
                                           (treesit-node-text (treesit-node-child-by-field-name n "change_id")))))))
       (goto-char (treesit-node-start (car nodes)))))


.. _alc-jj-log-view-new-before:

Insert a Revision Before Point
""""""""""""""""""""""""""""""

This is just a case of selecting the change at point, and assuming we find it, invoking the appropriate jj command in background before reloading the buffer.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-new-before ()
     "Insert a new revision before the revision under point"
     (interactive)
     (if-let ((change-id (alc-jj-log-view--change-at-point)))
       (progn
         (call-process "jj" nil nil nil "new" "--no-edit" "--insert-before" change-id)
         (alc-jj-log-view-reload))))

.. _alc-jj-log-view-new-after:

Insert a Revision After Point
"""""""""""""""""""""""""""""

Same as previous but with ``--insert-after``.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-new-after ()
     "Insert a new revision after the revision under point"
     (interactive)
     (if-let ((change-id (alc-jj-log-view--change-at-point)))
       (progn
         (call-process "jj" nil nil nil "new" "--no-edit" "--insert-after" change-id)
         (alc-jj-log-view-reload))))


.. _alc-jj-log-view-edit:

Edit the Revision at Point
""""""""""""""""""""""""""

It would be nice to trigger a revert of all the relevant buffers, but I think that's a task for another day.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-edit ()
     "Edit the revision under point."
     (interactive)
     (if-let ((change-id (alc-jj-log-view--change-at-point)))
       (progn
         (call-process "jj" nil nil nil "edit" change-id)
         (alc-jj-log-view-reload))))


.. _alc-jj-log-view-describe:

Describe the Revision at Point
""""""""""""""""""""""""""""""

Edit the commit message for the revision under point.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-describe ()
     "Edit the commit message for the revision under point"
     (interactive)
     (if-let ((change-id (alc-jj-log-view--change-at-point)))
       (progn
         (call-process "jj" nil 0 nil "describe" change-id)
         (alc-jj-log-view-reload))))

What's nice is that since I've already configured ``jj`` to use ``emacsclient`` as the editor, this kind of just works.
The one gotcha is that ``call-process`` usually blocks until the process exits - which prevents Emacs from ever opening the message buffer for me to edit!

This can be fixed by passing ``0`` to the ``DISPLAY`` parameter which forces it not to wait.
While this does mean I need to manually refresh the log view to see the result of my edit, I can live with that for now.

.. _alc-jj-log-view-reload:

Reload the Buffer
"""""""""""""""""

Reloading the buffer is pretty much just a case of calling the ``alc-jj-log`` command to regenerate the contents.
However, it would be nice to preserve the position of the point - or at least keep it in the same general position.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-reload ()
     "Regenerate the log view buffer's content."
     (interactive)
     (let ((change-id (alc-jj-log-view--change-at-point)))
       (alc-jj-log)
       (if change-id
         (alc-jj-log-view--select-revision-with-change-id change-id))))

Final Thoughts
--------------

I've had a lot of fun piecing this together and to be honest I've probably spent more time on the writeup than the actual code at this point!
The combination of tree-sitter and Emacs is such a nice hammer I'm now left wondering what other nails I can hit with it... 🤔
