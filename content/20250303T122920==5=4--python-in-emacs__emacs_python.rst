:title: Python in Emacs
:date: 2025-03-03
:tags: emacs, python
:identifier: 20250303T122920
:signature: 5=4


Python in Emacs
===============

Settings for Python files

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package python
     :hook ((python-mode . alc-python-mode-hook)
            (python-ts-mode . alc-python-mode-hook))
     :custom
     (python-shell-dedicated 'project))

Use ruff for formatting by default.
However, this can be overriden on a per-project basis by setting ``apheleia-formatter`` in a ``.dir-locals.el`` file.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (with-eval-after-load 'apheleia
     (setf (alist-get 'python-ts-mode apheleia-mode-alist)
          '(ruff-isort ruff)))

A function to run each time a Python file is visited.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (defun alc-python-mode-hook ()
     "Tweaks and config to run when starting `python-mode'"
     (require 'alc-python)
     (setq-local fill-column 88)

     ;; Files in site-packages/ etc. should be read only by default.
     ;; Also do not start eglot in these locations to cut down on the
     ;; number of server instances.
     ;;
     ;; However, make sure this only runs for buffer's associated with a
     ;; file. Previous versions of this code would set `(with-temp-buffer ...)`
     ;; buffers read-only which breaks functions like `python-shell-send-region'!
     (if-let ((file-name (buffer-file-name)))
       (if (alc-python-library-file-p file-name)
           (read-only-mode)
         (eglot-ensure))))

Python Environments
-------------------

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   ;;; alc-python.el --- Python configuration -*- lexical-binding: t -*-
   ;;; Code:

No configuration would be complete without considering the *many* ways in which you might work with Python environments!

The following function allows me to use the minibuffer to select an environment from all the environment defined for the current project

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-env-select ()
     "Select from a list of available Python environments, return the path to
   the Python executable"
     (if-let ((prj (project-current)))
         (cond ((alc-python-project-poetry-p prj)
                (alc-python-env-poetry-select prj))
               ((alc-python-project-hatch-p prj)
                (alc-python-env-hatch-select prj)))))

The main use case of course, is to "activate" the chosen environment within the context of the current project.
It works by updating the ``.dir-locals.el`` file for the current project

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-env-activate ()
     "Select a Python environment and activate it."
     (interactive)
     (if-let ((selected-env (alc-python-env-select))
              (default-directory (project-root (project-current))))
         (progn
           (setq-local python-shell-interpreter selected-env)
           (modify-dir-local-variable 'python-mode
                                      'python-shell-interpreter
                                      selected-env
                                      'add-or-replace)
           (modify-dir-local-variable 'python-mode
                                      'eglot-workspace-configuration
                                      `(:python
                                        (:pythonPath ,selected-env)
                                        :python.analysis
                                        (:logLevel "trace"))
                                      'add-or-replace)
           ;; Annoyingly, `modify-dir-local-variable' will leave the
           ;; .dir-locals.el file open in an unsaved buffer
           (save-buffer)
           (kill-buffer))))

Hatch
"""""

Depending on the project, environments can be defined in a ``hatch.toml`` file, or the ``tool.hatch`` namespace in ``pyproject.toml``

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-project-hatch-p (prj)
     "Return t if the given Python PRJ is managed by hatch."
     (let ((root (project-root prj)))
       (or (file-exists-p (concat root "hatch.toml"))
           (not (null (gethash "hatch"
                               (gethash "tool"
                                        (alc-python-load-toml (concat root "pyproject.toml"))
                                        (make-hash-table))))))))

The ``hatch env show`` command has a ``--json`` flag and provides plenty of information about the available environments!

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-env-hatch-discover (prj)
     "Return a list of hatch managed environments available in PRJ"
     (if-let* ((default-directory (project-root prj))
               (hatch-exe (executable-find "hatch"))
               (hatch-cmd (format "%s env show --json" hatch-exe))
               (hatch-envs (json-parse-string
                            (shell-command-to-string hatch-cmd))))
         (let ((envs ()))
           (maphash (lambda (k v) (push k envs))
                    hatch-envs)
           envs)))

While the ``hatch env find`` command can give us the path to the environment (but not the interpreter), using ``hatch env run python`` to print the value of ``sys.executable`` we also ensure that the environment is created if necessary.

   .. code-block:: elisp
      :project: emacs
      :filename: lisp/alc-python.el

      (defun alc-python-env-hatch-select (prj)
        "Select a Hatch environment defined by the given PRJ"
        (if-let* ((default-directory (project-root prj))
                  (hatch-envs (alc-python-env-hatch-discover prj))
                  (selected-env (completing-read "Select env: " hatch-envs))
                  (hatch-exe (executable-find "hatch"))
                  (hatch-cmd (format "%s -e %s env run python -- -c 'import sys;print(sys.executable)'"
                                     hatch-exe selected-env)))
            (car (reverse (split-string
                           (string-trim (shell-command-to-string hatch-cmd))
                           "\n")))))

Poetry
""""""

While not foolproof, the presence of a ``poetry.lock`` file is a pretty good indicator that the current project is using poetry.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-project-poetry-p (prj)
     "Return t if the given Python PRJ is managed by poetry."
     (file-exists-p (concat (project-root prj) "poetry.lock")))

Poetry provides a command to list environments, but unfortunately does not seem to give a way to return the list as JSON, hopefully the following is robust enough to parse the output.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-env-poetry-discover (prj)
     "Return a list of poetry managed environments available in PRJ"
     (if-let* ((default-directory (project-root prj))
               (poetry-exe (executable-find "poetry"))
               (poetry-cmd (format "%s env list" poetry-exe))
               (poetry-envs (shell-command-to-string poetry-cmd)))
         (seq-filter
          (lambda (s) (not (string= s "(Activated)")))
          (split-string poetry-envs))))

It does not correctly handle the case where it is called in a project that is not managed by Poetry, but hopefully guarding its use with ``alx-python-project-poetry-p`` should prevent it from doing the wrong thing.

It's only know that I'm writing the function to switch the environment in use that it looks like ``poetry`` doesn't want to be used this way?..
Oh well, for the projects I use poetry with currently, I can assume that there's only the one environment anyway 😅

   .. code-block:: elisp
      :project: emacs
      :filename: lisp/alc-python.el

      (defun alc-python-env-poetry-select (prj)
        "Select a Poetry environment defined by the given PRJ"
        (if-let* ((default-directory (project-root prj))
                  (poetry-envs (alc-python-env-poetry-discover prj))
                  (selected-env (completing-read "Select env: " poetry-envs))
                  (poetry-exe (executable-find "poetry")))
          (string-trim (shell-command-to-string (format "%s env info --executable" poetry-exe)))))

Helper Functions
""""""""""""""""

A function that tries to distinguish between library code and project code

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-library-file-p (file-name)
     "Determine if the given FILE-NAME is a library file"
     (or  (string-match-p "site-packages/" file-name)
          (string-match-p "typeshed-fallback/" file-name)
          (string-match-p "/usr/lib\\(64\\)?/" file-name)))

A function that uses the Python standard library to parse a TOML file as JSON.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (defun alc-python-load-toml (filename)
     "Load the toml in FILENAME as json, utilising the TOML parser in the
     Python standard library"
     (let ((cmd (string-join `("python" "-c"
                               "'import json,pathlib,sys,tomllib;print(json.dumps(tomllib.loads(pathlib.Path(sys.argv[1]).read_text())))'"
                               ,filename)
                             " ")))
       (json-parse-string (shell-command-to-string cmd))))


.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-python.el

   (provide 'alc-python)
