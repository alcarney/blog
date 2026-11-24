:title: Making a Lisp
:date: 2026-11-24
:tags: blog, mal, python
:identifier: 20260903T120018
:signature: 10

:in-project: mal-py

Making a Lisp in Python
=======================

.. highlight:: none

.. container:: post-teaser

   Earlier this year I stumbled across the `Make a Lisp <https://github.com/kanaka/mal>`__ repository on GitHub.
   Having had an interest in implementing a programming language for many years I finally acted on it and sat down to work my way through the steps.

   I would categorise this as a "speed run", in the sense I have skipped **many** details and my implementation does not pass the majority of tests.
   Rather than building a comprehensive implementation of ``mal`` I wanted to get an overall feel for the main ideas behind lisps in general and what it takes to implement one.
   If I'm honest, I just wanted to see how macros worked and so I stopped as soon as I had implemented them.

   I chose Python for this, since it's the language I'm fluent in and already supports all the necessary runtime features.

   There's not much commentary/explanation to be found here as I wrote this mostly for my benefit, but by all means take a look if you're interested!

Setup
-----

To get setup I had to

#. Clone the mal repo::

    ~/Projects $ mkdir -p kanaka/mal
    ~/Projects $ git clone https://github.com/kanaka/mal kanaka/mal/master

#. Create a folder for my implementation::

      mal/master $ mkdir impls/py

#. Make the edits described in the `Getting Started <https://github.com/kanaka/mal/blob/master/process/guide.md#getting-started>`__ guide to Makefile.impls ::

     IMPLS = ... py ...
     ...
     py_STEP_TO_PROG = impls/py/$($(1)).py

#. Add the ``run`` file:

   .. code-block:: bash
      :in-file: run

      #!/usr/bin/env bash
      exec python $(dirname $0)/${STEP:-stepA_mal}.py "${@}"

   .. awdur:file:: run
      :permissions: x

#. Finally, since I'm embedding the source for my implementation into this site using `awdur <https://github.com/swyddfa/awdur>`__,
   I added the following to the site's  ``Makefile``, to automate the extraction of the code and execution of the tests for the given step

   .. literalinclude:: ../Makefile
      :language: make
      :start-at: MAL_STEP
      :end-before: include

Step 0
------

:in-file: step0_repl.py

This is the "Hello, World" step, putting in the framework needed for a REPL, where:

- **R** stands for read

  .. code-block:: python
     :in-slot: read

     def read(input_: str):
         return input_

- **E** stands for eval

  .. code-block:: python
     :in-slot: eval

     def evaluate(input_: str):
         return input_

- **P** stands for print

  .. code-block:: python
     :in-slot: print

     def print_(input_: str):
         return input_

- **L** stands for loop

  .. code-block:: python
     :in-slot: repl

     def repl(input_: io.TextIO):
         print("user> ", end="", flush=True)
         while (line := input_.readline()) != "":
             print(print_(evaluate(read(line))))
             print("user> ", end="", flush=True)

All of which combine to form the first version of our lisp interpreter

.. code-block:: python

   import typing

   if typing.TYPE_CHECKING:
       import io

   {{ insert(slots.read) }}
   {{ insert(slots.eval) }}
   {{ insert(slots.print) }}
   {{ insert(slots.repl) }}

   if __name__ == "__main__":
       import sys
       repl(sys.stdin)

Which is enough to pass the first stage::

   Testing test^py^step0; step file: impls/py/step0_repl.py, test file: tests/step0_repl.mal
   Running: env STEP=step0_repl MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step0_repl.mal -- ../py/run
   Testing basic string
   Testing string containing spaces
   Testing string containing symbols
   Test long string
   Non alphanumeric characters
   ------- Optional Functionality --------------
   ------- (Not needed for self-hosting) -------
   Non alphanumeric characters

   TEST RESULTS (for ../tests/step0_repl.mal):
       0: soft failing tests
       0: failing tests
      24: passing tests
      24: executed tests
      24: total tests in the file (0 skipped)

Step 1
------

After step 0, the steps get big enough to give each of them their own file.
:denote:link:`Step 1 <20260903T200146>` introduces reading and printing::

   Testing test^py^step1; step file: impls/py/step1_read_print.py, test file: tests/step1_read_print.mal
   Running: env STEP=step1_read_print MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step1_read_print.mal -- ../py/run
   Testing read of numbers
   Testing read of symbols
   Testing non-numbers starting with a dash.
   Testing read of lists
   Test commas as whitespace
   -------- Deferrable Functionality --------
   Testing read of nil/true/false
   Testing read of strings
   Testing reader errors
   Testing read of quoting
   Testing keywords
   Testing read of vectors
   Testing read of hash maps
   Testing read of comments
   Testing read of @/deref
   Colon character inside a symbol
   -------- Optional Functionality --------
   Testing read of ^/metadata
   Non alphanumeric characters in strings
   Non alphanumeric characters in comments

   FAILURES:
   FAILED TEST (line 144): '[1 2' -> '.*\n.*(EOF|end of input|unbalanced).*':
       Expected : '.*\n.*(EOF|end of input|unbalanced).*'
       Got      : '[1 2\n['

   TEST RESULTS (for ../tests/step1_read_print.mal):
       0: soft failing tests
       1: failing tests
      60: passing tests
      61: executed tests
     121: total tests in the file (60 skipped)

Half the tests are skipped, but the core functionality is there.

Step 2
------

:denote:link:`Step 2 <20260904T183038>` adds basic evaluation::

   Testing test^py^step2; step file: impls/py/step2_eval.py, test file: tests/step2_eval.mal
   Running: env STEP=step2_eval MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step2_eval.mal -- ../py/run
   Testing evaluation of arithmetic operations
   Testing empty list
   -------- Deferrable Functionality --------
   Testing nil inside vector
   Testing evaluation within collection literals
   Check that evaluation hasn't broken empty collections

   FAILURES:
   FAILED TEST (line 37): '[nil]' -> '.*\n\\[nil\\]':
       Expected : '.*\n\\[nil\\]'
       Got      : "[nil]\nundefined symbol '['"

   TEST RESULTS (for ../tests/step2_eval.mal):
       0: soft failing tests
       1: failing tests
       9: passing tests
      10: executed tests
      15: total tests in the file (5 skipped)

Again, since I am "speed-running" the mal process, I've not added support for additional data types like vectors.

Step 3
------

:denote:link:`Step 3 <20260904T191754>` introduces ``def!`` and ``let*`` special forms, granting lisp code the ability to manipulate the environment::

   Testing test^py^step3; step file: impls/py/step3_env.py, test file: tests/step3_env.mal
   Running: env STEP=step3_env MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step3_env.mal -- ../py/run
   Testing REPL_ENV
   Testing def!
   Verifying symbols are case-sensitive
   Check env lookup non-fatal error
   Check that error aborts def!
   Testing let*
   Testing outer environment
   -------- Deferrable Functionality --------
   Testing let* with vector bindings

   Exception: OSError(5, 'Input/output error')
   Output before exception:
   (let* [z 9] z)
   Traceback (most recent call last):
     File "/var/home/alex/Projects/kanaka/mal/master/impls/py/../py/step3_env.py", line 58, in <module>
       repl(sys.stdin)
       ~~~~^^^^^^^^^^^
     File "/var/home/alex/Projects/kanaka/mal/master/impls/py/../py/step3_env.py", line 48, in repl
       print(print_(evaluate(read(line), env)))
                    ~~~~~~~~^^^^^^^^^^^^^^^^^
     File "/var/home/alex/Projects/kanaka/mal/master/impls/py/../py/step3_env.py", line 30, in evaluate
       for binding, expr in itertools.batched(fs[1], n=2):
                            ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
   TypeError: 'S' object is not iterable


   TEST RESULTS (for ../tests/step3_env.mal):
       0: soft failing tests
       0: failing tests
      27: passing tests
      28: executed tests
      28: total tests in the file (0 skipped)

Step 4
------

:denote:link:`Step 4 <20260904T200139>` fleshes out the language some more, adding if statements and lambdas::

   Testing test^py^step4; step file: impls/py/step4_if_fn_do.py, test file: tests/step4_if_fn_do.mal
   Running: env STEP=step4_if_fn_do MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step4_if_fn_do.mal -- ../py/run
   -----------------------------------------------------
   Testing list functions
   Testing if form
   Testing 1-way if form
   Testing basic conditionals
   Testing equality and the representation of nil false true
   Testing builtin and user defined functions
   Testing closures
   Testing do form
   Testing special form case-sensitivity
   Testing recursive sumdown function
   Testing recursive fibonacci function
   Testing recursive function in environment.
   -------- Deferrable Functionality --------
   Testing if on strings
   Testing string equality
   Testing variable length arguments
   Testing language defined not function
   -----------------------------------------------------
   Testing string quoting
   Testing pr-str
   Testing str
   Testing prn
   Testing println
   Testing keywords
   Testing vector truthiness
   Testing vector printing
   Testing vector functions
   Testing vector equality
   Testing vector parameter lists
   Nested vector/list equality

   FAILURES:
   FAILED TEST (line 123): '(= nil "")' -> '.*\nfalse':
       Expected : '.*\nfalse'
       Got      : '(= nil "")\n\'""\' not found'

   TEST RESULTS (for ../tests/step4_if_fn_do.mal):
       0: soft failing tests
       1: failing tests
      50: passing tests
      51: executed tests
     199: total tests in the file (148 skipped)

Step 5
------

:denote:link:`Step 5 <20260905T105802>` adds tail call optimisation::

   Testing test^py^step5; step file: impls/py/step5_tco.py, test file: tests/step5_tco.mal
   Running: env STEP=step5_tco MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step5_tco.mal -- ../py/run
   Testing recursive tail-call function
   TODO: test let*, and do for TCO
   Test mutually recursive tail-call functions

   TEST RESULTS (for ../tests/step5_tco.mal):
       0: soft failing tests
       0: failing tests
       8: passing tests
       8: executed tests
       8: total tests in the file (0 skipped)

Step 6
------

I wasn't too interested in implementing the "atoms" introduced in :denote:link:`Step 6 <20260905T122636>` so I skipped those::

   Testing test^py^step6; step file: impls/py/step6_file.py, test file: tests/step6_file.mal
   Running: env STEP=step6_file MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step6_file.mal -- ../py/run
   Testing that (do (do)) not broken by TCO
   Testing read-string, eval and slurp
   Testing load-file
   Testing atoms
   Test that do only evals each slot once
   Testing swap!/closure interaction
   Testing whether closures can retain atoms
   -------- Deferrable Functionality --------
   Testing read-string parsing errors
   Testing reading of large files
   Testing `@` reader macro (short for `deref`)
   Testing that vector params not broken by TCO
   Testing that *ARGV* exists and is an empty list
   Testing that eval sets aa in root scope, and that it is found in nested scope
   -------- Optional Functionality --------
   Testing comments in a file
   Testing map literal across multiple lines in a file
   Checking that eval does not use local environments.
   Non alphanumeric characters in comments in read-string

   FAILURES:
   FAILED TEST (line 54): '(def! a (atom 2))' -> '.*\n\\(atom\\ 2\\)':
       Expected : '.*\n\\(atom\\ 2\\)'
       Got      : "(def! a (atom 2))\n'atom' not found"

   TEST RESULTS (for ../tests/step6_file.mal):
       0: soft failing tests
       1: failing tests
      15: passing tests
      16: executed tests
      71: total tests in the file (55 skipped)

Step 7
------

:denote:link:`Step 7 <20260906T003603>` introduces the ability to toggle off (and on), whether or not a form is evaluated.
Again, in-keeping with "speedrun" approach, I haven't even implemented the reader macros like ``'`` since I'm more interested in the evaluator at the moment.

::

   Testing test^py^step7; step file: impls/py/step7_quote.py, test file: tests/step7_quote.mal
   Running: env STEP=step7_quote MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step7_quote.mal -- ../py/run
   Testing cons function
   Testing concat function
   Testing regular quote
   Testing simple quasiquote
   Testing quasiquote with lists
   Testing unquote
   Quasiquote and environments
   Testing splice-unquote
   Testing symbol equality
   -------- Deferrable Functionality --------
   Testing ' (quote) reader macro
   Testing cons and concat with vectors
   -------- Optional Functionality --------
   Testing ` (quasiquote) reader macro
   Testing ~ (unquote) reader macro
   Testing ~@ (splice-unquote) reader macro
   Testing vec function
   Testing that vec does not mutate the original list
   Test quine
   Testing quasiquote with vectors
   Testing unquote with vectors
   Testing splice-unquote with vectors
   Misplaced unquote or splice-unquote

   FAILURES:
   FAILED TEST (line 58): '(quasiquote {"a" b})' -> '.*\n\\{"a"\\ b\\}':
       Expected : '.*\n\\{"a"\\ b\\}'
       Got      : '(quasiquote {"a" b})\n{'

   TEST RESULTS (for ../tests/step7_quote.mal):
       0: soft failing tests
       1: failing tests
      25: passing tests
      26: executed tests
     124: total tests in the file (98 skipped)

Step 8
------

:denote:link:`Step 8 <20260906T122503>` introduces macros and is where I stopped following the mal process.

::

   Testing test^py^step8; step file: impls/py/step8_macros.py, test file: tests/step8_macros.mal
   Running: env STEP=step8_macros MAL_IMPL=js ../../runtest.py  --deferrable --optional   ../tests/step8_macros.mal -- ../py/run
   Testing trivial macros
   Testing unless macros
   Testing evaluation of macro result
   Test that macros do not break empty list
   Test that macros do not break quasiquote
   -------- Deferrable Functionality --------
   Testing non-macro function
   Testing nth, first and rest functions
   Testing cond macro
   Testing EVAL in let*
   Testing nth, first, rest with vectors
   Testing EVAL in vector let*
   Test return value of defmacro!
   ------- Optional Functionality --------------
   ------- (Not needed for self-hosting) -------
   Test that macros use closures

   FAILURES:
   FAILED TEST (line 48): '(nth (list 1) 0)' -> '.*\n1':
       Expected : '.*\n1'
       Got      : "(nth (list 1) 0)\n'nth' not found"

   TEST RESULTS (for ../tests/step8_macros.mal):
       0: soft failing tests
       1: failing tests
      16: passing tests
      17: executed tests
      61: total tests in the file (44 skipped)

Final Thoughts
--------------

I was pleasantly surprised to see how straightforward the main ideas behind a lisp are.

Sure, implementing this in Python meant that it did all the heavy lifting and I didn't have to think too hard about most of the implementation details but that was kind of the point.

I now have a handy reference for when I want to try a similar exercise in a different language!
