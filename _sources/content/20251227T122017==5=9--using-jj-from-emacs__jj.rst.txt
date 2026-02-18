:title: Using jj from Emacs
:date: 2025-12-27
:tags: jj
:identifier: 20251227T122017
:signature: 5=9

Using ``jj`` from Emacs
=======================

As I'm starting to use `jj <https://docs.jj-vcs.dev/latest/>`__ more and more, it's inevitable that I'm going to want some integration between ``jj`` and Emacs.
There are many packages already available that do this, including but not limited to

- `jujutsu.el <https://github.com/bennyandresen/jujutsu.el>`__
- `jj-mode <https://github.com/bolivier/jj-mode.el>`__
- `vc-jj <https://elpa.gnu.org/packages/vc-jj.html>`__

However, I want to use this as an excuse to learn how to write my own extensions/utilities for Emacs.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package alc-jj)


``eshell/jj-diff``
^^^^^^^^^^^^^^^^^^

I'm trying to use ``eshell`` more and more, it's very cool being able to seamlessly switch between regular shell commands like ``cd``, ``ls`` etc. and calling Emacs functions like ``find-file`` or ``compile``!

:bib:cite:`yt-be07`

So, after seeing `this episode <https://youtu.be/M6o1N2kfmuc>`__ of Álvaro Ramírez's Bending Emacs series I've been eager to find an excuse to try it out.

Rather than dumping the output of ``jj diff`` into the eshell window, wouldn't it be great to redirect it to a dedicated buffer instead?

*What, like this?*

.. code-block:: console

   $ jj diff --no-pager --color never > #<buffer *jj-diff*>

Well, yes but that's a lot to type, plus the buffer is created uses ``fundamental-mode`` it would be nice to have it automatically enable ``diff-mode`` at least.
A better option would be to define my own eshell command that wrapped the underlying ``jj`` command to handle this for me.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el
   :template: elisp-module

   (defun eshell/jj-diff (&rest args)
     "Eshell wrapper around 'jj diff'"
     (let ((current-dir default-directory))
       (with-current-buffer (get-buffer-create "*jj-diff*")
         ;; Ensure the command uses the current directory from where the command was invoked.
         (setq default-directory current-dir)

         ;; Clear any previous content
         (read-only-mode -1)
         (erase-buffer)

         ;; Call jj, insert output into current buffer
         (apply 'call-process "jj" nil t nil "diff" "--no-pager" "--color" "never" args)
         (diff-mode)

         ;; Re-enable read-only mode and show the buffer
         (read-only-mode)
         (pop-to-buffer (current-buffer)))))
