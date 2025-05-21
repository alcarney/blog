:title: Using git from Emacs
:date: 2025-02-21
:tags: emacs, git
:identifier: 20250221T184014
:signature: 5=1

Using ``git`` from Emacs
------------------------

Of course, no Emacs config would be complete without :gh:`magit/magit`

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package magit
     :ensure t
     :defer
     :custom
     (magit-format-file-function #'magit-format-file-nerd-icons))

``diff-hl``
^^^^^^^^^^^

:gh:`dgutov/diff-hl` highlights regions of the buffer that have changed relative to some reference commit (typically ``HEAD``)

.. seealso::

   `This article <https://karthinks.com/software/fringe-matters-finding-the-right-difference/>`__ from Karthink shows how you can change the reference commit

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package diff-hl
     :ensure t
     :hook ((dired-mode . diff-hl-dired-mode))
     :config
     (global-diff-hl-mode)
     (diff-hl-margin-mode))

Forge
^^^^^

I've also started playing around with :gh:`magit/forge`

.. important::

   Forge looks for your GitHub username in your ``gitconfig``

   .. code-block::
      :filename: gitconfig

      [github]
      user = alcarney


.. code-block:: elisp
   :filename: emacs/init.el

   (use-package forge
     :ensure t
     :after magit)

All thanks to :gh:`magit/forge/discussions/544`, it's possible to define an auth source that uses the ``gh`` cli to authenticate with the API!

.. code-block:: elisp
   :filename: emacs/init.el

   (cl-defun auth-source-ghcli-search (&rest spec
                                             &key backend require
                                             type max host user port
                                             &allow-other-keys)
     "Given a property list SPEC, return search matches from the `:backend'.
   See `auth-source-search' for details on SPEC."
     ;; just in case, check that the type is correct (null or same as the backend)
     (cl-assert (or (null type) (eq type (oref backend type)))
                t "Invalid GH CLI search: %s %s")

     (when-let* ((hostname (string-remove-prefix "api." host))
                 ;; split ghub--ident again
                 (ghub_ident (split-string (or user "") "\\^"))
                 (username (car ghub_ident))
                 (package (cadr ghub_ident))
                 (cmd (format "gh auth token --hostname '%s'" hostname))
                 (token (when (string= package "forge") (string-trim-right (shell-command-to-string cmd))))
                 (retval (list
                          :host hostname
                          :user username
                          :secret token)))
       (auth-source-do-debug  "auth-source-ghcli: return %s as final result (plus hidden password)"
                              (seq-subseq retval 0 -2)) ;; remove password
       (list retval)))

   (defvar auth-source-ghcli-backend
     (auth-source-backend
      :source "." ;; not used
      :type 'gh-cli
      :search-function #'auth-source-ghcli-search)
     "Auth-source backend for GH CLI.")

   (defun auth-source-ghcli-backend-parse (entry)
     "Create a GH CLI auth-source backend from ENTRY."
     (when (eq entry 'gh-cli)
       (auth-source-backend-parse-parameters entry auth-source-ghcli-backend)))

   (if (boundp 'auth-source-backend-parser-functions)
       (add-hook 'auth-source-backend-parser-functions #'auth-source-ghcli-backend-parse)
     (advice-add 'auth-source-backend-parse :before-until #'auth-source-ghcli-backend-parse))

   (setq auth-sources '(gh-cli))


``alc-git``
-----------

I also have a few utility functions defined in a local package

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package alc-git
     :ensure nil
     :load-path "lisp/"
     :bind ("C-x v w" . alc-git-permalink-to-kill-ring))
