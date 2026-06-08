:title: Parsing org syntax with docutils
:date: 2026-08-12
:tags: docutils, esbonio, org
:identifier: 20260812T175124

Parsing ``org`` Syntax with ``docutils``
========================================

The simplest parser
-------------------

``docutils`` parsers are based on state machines and the library comes with its own framework for defining and running these machines.

There are two base machine types ``StateMachine`` and ``StateMachineWS``, where ``StateMachineWS`` builds on ``StateMachine`` to provide utilities for parsing languages that have whitespace as part of their grammar (like Python and reStructuredText).

For now, let's base the parser on ``StateMachine``, I don't think ``org`` syntax has many places where whitespace forms part of the grammar and we can  always change it later is needed.

.. code-block:: python

   class OrgStateMachine(StateMachine):

       def run(self, input_lines, document):
           super().run(
               input_lines,
               0,
               input_source=document["source"],
               context={"document": document},
           )

The ``context`` object is passed to each state and we can store whatever information we like in it.
For now, we're just passing the root ``document`` node.

Of course, a state machine isn't much use if it doesn't contain any states!
So let's define one now

.. code-block:: python

   class Document(State):
       patterns = {"text": ""}
       initial_transitions = ("text",)

       def text(self, match, context, next_state):
           context["document"] += nodes.paragraph(match.string, match.string)
           return context, "Document", []

Like with state machines ``docutils`` provides two base classes ``State`` and ``StateWS``.
Each state can, in turn, define "sub-states" called transitions.

.. code-block:: python

Finally, we can define the ``Parser`` implementation, which is responsible for setting up and running the state machine.

.. code-block:: python

   class OrgModeParser(Parser):
       def parse(self, input_string: str, document: nodes.document):
           self.setup_parse(input_string, document)
           self.statemachine = OrgStateMachine([Document], "Document")

           input_lines = string2lines(input_string)
           self.statemachine.run(input_lines, document)

           self.finish_parse()

   def main():
       publish_cmdline(parser=OrgModeParser(), writer="html5")

   if __name__ == "__main__":
       main()

With that, we've defined our "Hello, World!" parser which we can use to convert an org-mode document to html.

.. code-block:: console

   $ uv run python parser.py denote.org
   <!DOCTYPE html>
   <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
   <meta charset="utf-8" />
   <meta name="generator" content="Docutils 0.23: https://docutils.sourceforge.io/" />
   ...
   </head>
   <body>
   <main>
   <p>#+title: denote: Simple notes with an efficient file-naming scheme</p>
   <p>#+author: Protesilaos</p>
   <p>#+email: info&#64;protesilaos.com</p>
   <p>#+language: en</p>
   <p>#+options: ':t toc:nil author:t email:t num:t</p>
   <p>#+startup: content</p>
   <p>#+macro: stable-version 4.2.0</p>
   <p>#+macro: release-date 2026-05-20</p>
   <p>#+macro: development-version 4.3.0-dev</p>
   ...
   </body>
   </html>

Now with the basic framework in place, all we have to do is "just" define the necessary states and transitions to properly parse the document.

The rest of the owl
-------------------

Document Structure
^^^^^^^^^^^^^^^^^^
