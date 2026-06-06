:title: alc-jj-log-view-mode
:date: 2026-06-01
:tags: lisp
:identifier: 20260601T172422
:signature: 5=9=1

``alc-jj-log-view-mode``
========================

.. highlight:: none

.. container:: post-teaser

   Since I primarily use ``jj`` (and git really) via the log view I want a way to visualise and manipulate the graph.

   Rather than mess around with regular expressions, I thought it would be fun to write a simple tree-sitter grammer that can be used to power the mode.

   I want to write a tree-sitter parser for ``jj log`` output::

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

   Why? I hear you ask.

   I'm sure using something like tree-sitter for this is overkill, but that should mean it will be relatively easy to do and good as a learning exercise.
   Then once I have the grammar, I should be able to `use it as a foundation for an Emacs major-mode <https://www.masteringemacs.org/article/lets-write-a-treesitter-major-mode>`__.

Getting Started
---------------

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

Which is great!.. if you intend to ship your parser to the wider world and make it easy to integrate into other projects.
However, if you are only looking to hack something together for use with your Emacs config, you can get away with a lot less.

Emacs Quick Start
^^^^^^^^^^^^^^^^^

#. The only source file you really need is the ``grammar.js`` file

   .. code-block:: js

      /**
       * @file
       * @author Alex
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

#. So that Emacs can find the grammar, the ``parser.so`` file needs to be moved to ``.emacs.d/tree-sitter`` and renamed to
   ``libtree-sitter-<lang>.so``::

     $ mv parser.so ~/.emacs.d/tree-sitter/libtree-sitter-jjlog.so

#. With the parser in place, it should now be possible to call it from Emacs::

     ELISP> (treesit-parse-string "hello" 'jjlog)
     #<treesit-node source_file in 1-6>


Defining The Grammar
--------------------

The easiest way to model the output is as a linear sequence of changes, it would be interesting to see if you could encode the structure of the revision tree in the parse tree but that's likely not an easy undertaking.
So, for the time being I'm going to delcare the graph characters as ``extras`` so that they are effectively treated as whitespace

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

The type of each change is denoted by the symbol representing that change's node in the revision graph

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

.. code-block:: js
   :project: emacs
   :template: treesit-grammar
   :filename: tree-sitter-grammars/jjlog/grammar.js

   _change_metadata: $ => seq(
     field("change_id", $.ref),
     field("author", $.email),
     field("timestamp", $.datetime),
     repeat($.ref),
   ),

   ref:         $ => /[a-z0-9A-z]+/,
   email:       $ => /[^\s]+@[^\s]+/,
   datetime:    $ => /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/,

   _description: $ => seq(/[\n\r]/, $.description, /[\n\r]/),
   description: $ => /[^\n\r]+/,

.. code-block:: js
   :project: emacs
   :filename: tree-sitter-grammars/jjlog/grammar.js

   }

Major Mode
----------

Thankfully `this guide <https://www.masteringemacs.org/article/lets-write-a-treesitter-major-mode>`__ from Mastering Emacs provides a great starting point

When defining a major-mode, you often can base your mode on a more fundamental mode and inherit a lot of functionality for free.
Initially I thought of basing it on the mode you get when running ``vc-print-log`` (:kbd:`C-x v l`) i.e. ``log-view-mode`` would be worthwhile, however since the navigation commands are all powered by regular expressions I didn't think I would gain much and so based it on ``special-mode`` instead.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (require 'log-view)

   (define-derived-mode alc-jj-log-view-mode special-mode "jj-log"
     "Major mode for viewing and manipulating the jj log"

     (setq-local font-lock-defaults nil)
     (when (treesit-ready-p 'jjlog)
       (treesit-parser-create 'jjlog)
       (alc-jj-log-view-ts-setup)))

Where the setup function is like so

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-ts-setup ()
     "Setup treesit for alc-jj-log-view mode."
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


Syntax Highlighting
-------------------

Or in Emacs parlance, font locking.

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
