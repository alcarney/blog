:title: Language Servers in Emacs
:date: 2025-03-05
:tags: emacs
:identifier: 20250305T195742

Language Servers in Emacs
=========================

I use ``eglot`` as my language client since it is available out of the box and integrates nicely with core packages like ``xref``

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package eglot
     :bind (("<f2>" . eglot-rename))
     :custom
     (eglot-autoshutdown t)
     (eglot-extend-to-xref t)
     :config
     (advice-add 'eglot--workspace-configuration-plist :around #'alc-eglot-fix-workspace-configuration-scope)

     (add-to-list 'display-buffer-alist
                  '("\\*EGLOT workspace configuration\\*"
                    (display-buffer-below-selected)
                    (dedicated . t))))

Workspace Configuration
-----------------------

Convincing ``eglot`` to apply the correct ``workspace/configuration`` settings for the current server and project is the single most frustrating part of using it...

One issue is making sure ``eglot`` evaluates settings at the right scope

.. code-block:: elisp
   :filename: emacs/init.el

   (require 's)

   (defun alc-eglot-fix-workspace-configuration-scope (orig-fun server &optional path)
     "Fix the scopeUri of a workspace/configuration request.

   When eglot handles a workspace/configuration request with an
   associated scopeUri it uses the `file-name-directory' function to
   determine the directory from which to resolve the configuration
   values.

   This causes an issue for servers like esbonio and pyright which
   set the scopeUri to a directory. For `file-name-directory' to
   treat the path as a directory it must include a trailing slash, a
   convention which these servers do not follow.

   Therefore `file-name-directory' treats the path as a file and
   removes the final component, causing eglot to resolve the
   configuration relative to the wrong directory.

   This function fixes the issue by advising the
   `eglot--workspace-configuration-plist' function, ensuring that
   paths referencing directories include the trailing slash."
     (if (and path
              (file-directory-p path)
              (not (s-ends-with? "/" path)))
         (funcall orig-fun server (concat path "/"))
       (funcall orig-fun server path)))
