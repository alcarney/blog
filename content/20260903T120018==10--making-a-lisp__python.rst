:title: Making a Lisp
:date: 2026-09-03
:tags: python
:identifier: 20260903T120018
:signature: 10

Making a Lisp in Python
=======================

.. highlight:: none

The `Make a Lisp <https://github.com/kanaka/mal>`__ repository on GitHub looks like a great resource for a guide on implementing your own lisp interpreter which, for reasons\ :sup:`TM` I'm growing increasingly interested in.

Sure, Python might not be the best language for this, but it's the one I'm fluent in which is good enough for now as I'm only looking to get a feel for the ideas.

Setup
-----

To get setup I had to

#. Clone the mal repo::

    ~/Projects $ mkdir -p kanaka/mal
    ~/Projects $ git clone https://github.com/kanaka/mal kanaka/mal/master

#. Create a folder for my implementation

   mal/master $ mkdir impls/py

#. Make the edits described in the `Getting Started <https://github.com/kanaka/mal/blob/master/process/guide.md#getting-started>`__ guide to Makefile.impls ::

     IMPLS = ... py ...
     ...
     py_STEP_TO_PROG = impls/py/$($(1)).py

#. Add the ``run`` file:

   .. code-block:: bash
      :project: mal-py
      :filename: run

      #!/usr/bin/env bash
      exec python $(dirname $0)/${STEP:-stepA_mal}.py "${@}"

#. Then because I'm embedding the source for my implementation in this site using `awdur <https://github.com/swyddfa/awdur>`__, I added the following to my ``Makefile``, automating the extraction of the code and execution of the tests for the current step.

   .. code-block:: Makefile

      mal: dotfiles
          -rm $(PROJECTS)/kanaka/mal/master/impls/py/*
	  cp $(DOTFILES)/mal-py/* $(PROJECTS)/kanaka/mal/master/impls/py/
	  make -C $(PROJECTS)/kanaka/mal/master/ test^py^stepN
