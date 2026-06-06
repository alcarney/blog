:title: Eshell Integration
:date: 2026-06-06
:tags: blog, eshell
:identifier: 20260606T000449
:signature: 5=9=2

A Simple ``jj`` Integration for ``eshell``
==========================================

.. container:: post-teaser

   I'm trying to use ``eshell`` more and more, it's very cool being able to seamlessly switch between regular shell commands like ``cd``, ``ls`` etc. and calling Emacs functions like ``find-file`` or ``compile``.
   I'm enjoying it so much that I'm starting to feel like the ``jj`` commands I typically use need to be tied into Emacs a bit more!

   Thanks to `this episode <https://youtu.be/M6o1N2kfmuc>`__ of Álvaro Ramírez's Bending Emacs series, it turns out that it's trivial to intercept commands before they are invoked as a subprocess - just define a function called ``eshell/<command name>``!

As the ``jj`` cli is composed of many sub commands it's simple enough to write a dispatcher function based on the first argument

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun eshell/jj (&rest items)
     "Eshell wrapper around jj."
     (let ((cmd  (car items))
           (args (cdr items)))
       (cond ((string= cmd "log")  (alc-jj-log args))
             ((string= cmd "diff") (alc-jj-diff args))
             (t "Command not supported, run *jj ..."))))

I would have loved for this to transparently fall back to running ``jj`` directly, but I couldn't figure out the incantation to make this work well. I got close with:

.. code-block:: elisp

   (t (throw 'eshell-external
             (eshell-external-command "jj" items)))

which appears to be a common pattern in the eshell codebase.
However, eshell wasn't able to detect that the ``jj`` process had exited, forcing me to send a :kbd:`C-c C-c` to get the prompt back.

So for now I've admitted defeat and just return a message reminding myself to use ``*jj ...`` instead which bypasses my wrapper and runs it normally.

``jj diff``
^^^^^^^^^^^

Rather than dumping the output of ``jj diff`` into the eshell window, let's redirect it to a dedicated buffer.
At some point I'd like to build a jj-enhanced diff-mode with convenience commands for sending changes to different revisions.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el
   :template: elisp-module

   (defun alc-jj-diff (&rest args)
     "Wrapper around 'jj diff'"
     (let* ((current-dir default-directory)
            (pr (project-current nil))
            (buffer-name (if pr (format "*jj-diff[%s]*" (project-name pr)) "*jj-diff*")))
       (with-current-buffer (get-buffer-create buffer-name)
         ;; Ensure the command uses the current directory from where the command was invoked.
         (setq default-directory current-dir)

         ;; Clear any previous content
         (read-only-mode -1)
         (erase-buffer)

         ;; Call jj, insert output into current buffer
         (apply 'call-process "jj" nil t nil "diff" "--no-pager" "--color" "never" (delq nil args))
         (diff-mode)

         ;; Re-enable read-only mode and show the buffer
         (read-only-mode)
         (pop-to-buffer (current-buffer)))))

``jj log``
^^^^^^^^^^

Rather than dumping the output of ``jj diff`` into the eshell window, let's redirect it to a dedicated buffer.
Then we can invoke :denote:link:`alc-jj-log-view-mode <20260601T172422>` and get all the goodies defined there.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log (&rest args)
     "Wrapper around 'jj log'"
     (let* ((current-dir default-directory)
            (pr (project-current nil))
            (buffer-name (if pr (format "*jj-log[%s]*" (project-name pr)) "*jj-log*")))
       (with-current-buffer (get-buffer-create buffer-name)
         ;; Ensure the command uses the current directory from where the command was invoked.
         (setq default-directory current-dir)

         ;; Clear any previous content
         (read-only-mode -1)
         (erase-buffer)

         ;; Call jj, insert output into current buffer
         (apply 'call-process "jj" nil t nil "log" "--no-pager" "--color" "never" (delq nil args))
         (alc-jj-log-view-mode)

         ;; Re-enable read-only mode and show the buffer
         (read-only-mode)
         (pop-to-buffer (current-buffer)))))
