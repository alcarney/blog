:title: Using pdb from Emacs
:date: 2025-06-15
:tags: emacs, python
:identifier: 20250615T135327
:signature: 5=4=1

Using ``pdb`` from Emacs
========================

.. highlight:: none

.. container:: post-teaser

   I've recently been re-discovering Python's built-in debugger :external+python:py:mod:`pdb` and thought it was about time I took a look at exploring Emacs' support for it.

``pdb`` Basics
--------------

Emacs' ``pdb`` support is part of the `Grand Unified Debugger <https://www.gnu.org/software/emacs/manual/html_node/emacs/Debuggers.html>`__ framework.

Since everything is available out of the box, there's nothing really to setup!
Just run ``M-x pdb`` and Emacs will ask you how you want to invoke ``pdb``

.. code-block:: none

   Run pdb (like this): python -m pdb example.py

Emacs will then reconfigure itself to display both the pdb prompt in an interactive window, alongside the code you are debugging.

.. termshot:: /images/emacs-pdb.cast
   :title: M-x pdb

From here you can use ``pdb`` just as if you'd started it in your terminal.
But of course Emacs offers a set of additional keybindings, which differ slightly depending on in you have your cursor in the source code view or the pdb buffer.

=============  ==================  ==============   ==================
Command        ``pdb`` Equivalent  Keybind (Pdb)    Keybind (Code)
=============  ==================  ==============   ==================
``gud-break``  break (b)                            :kbd:`C-x C-a C-b`
``gud-step``   step (s)            :kbd:`C-c C-s`   :kbd:`C-x C-a C-s`
``gud-next``   next (n)            :kbd:`C-c C-n`   :kbd:`C-x C-a C-n`
``gud-print``                      :kbd:`C-c C-p`   :kbd:`C-x C-a C-p`
=============  ==================  ==============   ==================

See ``(info "(emacs)Commands of GUD")`` for the full list.

.. tip::

   Yes, those keybinds look pretty ugly, but if you enable ``repeat-mode`` following the first use the keymap below is activated and the listed commands are available with a single keypress!

   .. code-block:: elisp

      ;; from `gud.el`
      (defvar gud-pdb-repeat-map
        (let ((map (make-sparse-keymap)))
          (pcase-dolist (`(,key . ,cmd) '(("n" . gud-next)
                                          ("s" . gud-step)
                                          ("c" . gud-cont)
                                          ("l" . gud-refresh)
                                          ("f" . gud-finish)
                                          ("<" . gud-up)
                                          (">" . gud-down)))
            (define-key map key cmd))
          map)
        "Keymap to repeat `pdb' stepping instructions \\`C-x C-a C-n n n'.
      Used in `repeat-mode'.")


Startup Commands
----------------

My favourite thing about ``M-x pdb`` is that it will work with *any python command* that eventually results in a pdb session.
For example:

- Start a ``pdb`` session within the context of a ``pytest`` failure::

    pytest test_example.py --pdb

- Use ``uv`` to install a particular version of Sphinx and debug a failing build::

    uv run --with sphinx==9.1.0 sphinx-build -b html -P docs/ docs/_build/

- Select the ``hatch`` environment that uses Python 3.11 and Sphinx v8, run the named test and start ``pdb`` when it fails::

   hatch test -i py=3.11 -i sphinx=8 -- tests/example/test_example.py::test_this --pdb

The only commands that haven't worked for me so far are those invoked via ``make`` (possibly because each command is executed in a separate shell?).

.. tip::

   ``M-x pdb`` runs your given Python command from the ``default-directory`` of the current buffer.
   Running ``pdb`` via ``project-execute-extended-command`` (:kbd:`C-x p x` for me) runs the given command from your project's root.

Remote Debugging
----------------

If you've been keeping up with recent Python releases, you've likely already heard that ``pdb`` in Python 3.14 now supports
:external+python:std:ref:`attaching to existing Python processes<whatsnew314-remote-debugging>`!
I'm finding this particuarly useful when working with :gh:`Textualize/textual` as the process' own stdin and stdout channels are busy hosting the TUI.

To attach to a remote process, we "just" need to supply the process PID to the cli provided by the ``pdb`` module::

  uv run --python 3.14 python -m pdb -p 1234

(I'm using ``uv`` here as my system Python is currently 3.13).

Up until now I've been using ``htop`` to lookup the PID and type it in, but come on, we're using Emacs, surely we can do better than that!

Selecting PIDs using ``completing-read``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you didn't know, Emacs has
it's own built-in ``htop`` style program - `proced <https://www.masteringemacs.org/article/displaying-interacting-processes-proced>`__ (because of course it does!).

This means all the necessary infrastructure for discovering the available processes should be there for us to reuse.
And yes, after a quick search I find that the ``list-system-processes`` function returns a list of all the currently active PIDs

.. code-block:: elisp

   *** Welcome to IELM ***  Type (describe-mode) or press C-h m for help.
   ELISP> (list-system-processes)
   (1 2 3 4 5 6 7 8 10 13 15 16 17 18 19 20 21 22 23 24 25 27 28 ...)

Each PID can be passed to ``process-attributes`` to get some information about it:

.. code-block:: elisp

   ELISP> (process-attributes 42778)
   ((args . "python -m sphinx_agent") (pmem . 0.6490886804884154)
    (rss . 208580) (vsize . 733132) (thcount . 3) (nice . 0) (pri . 20)
    (pcpu . 0.5113255738694369) (etime 1 53556 420000 0)
    (start 27065 14522 350000 0) (ctime 0 0 0 0) (cstime 0 0 0 0)
    (cutime 0 0 0 0) (time 0 608 950000 0) (stime 0 29 470000 0)
    (utime 0 579 480000 0) (cmajflt . 0) (cminflt . 0) (majflt . 5)
    (minflt . 950190) (tpgid . -1) (ttname . "") (sess . 42771)
    (pgrp . 42771) (ppid . 42777) (state . "S") (comm . "python")
    (group . "alex") (egid . 1000) (user . "alex") (euid . 1000))


After a fair amount of head scratching I eventually arrived at the following elisp that will prompt me to select a process in minibuffer and return the corresponding PID:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python--pid-to-candidate (pid)
     "Convert the given PID into a completion candidate for `completing-read'"
     (let* ((process (process-attributes pid))
            (cmd (alist-get 'args process)))
       (if (string= (user-login-name) (alist-get 'user process))
         (cons (format "[%s] %s" pid cmd) pid))))

   (defun alc-python--select-process-pid ()
      "Select a process id via `completing-read'"
      (let* ((processes (mapcar 'alc-python--pid-to-candidate (list-system-processes)))
             (selection (completing-read "Select process: " processes nil t)))
        (cdr (assoc-string selection processes))))

I'd love to be able to pre-filter the list of processes to only include those that are debuggable by ``pdb`` (it must be possible as ``pdb`` itself gives a nice error message if you select an incompatible process), but I imagine that's a non-trivial undertaking.

Anyway with that helper out of the way we're only a ``defun`` away from implementing an "attach to process" command!

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-pdb-attach-to-process ()
      "Attach a pdb session to a running Python process."
      (interactive)
      (when-let* ((pid (alc-python--select-process-pid))
                  (prj (project-current nil))
                  (default-directory (project-root prj)))
        (pdb (format "uv run --no-project --python 3.14 python -m pdb -p %s" pid))))
