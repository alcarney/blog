:title: Get the permalink to code
:date: 2025-04-30
:tags: emacs, git
:identifier: 20250430T213500
:signature: 5=1=1

Getting the permalink URL to a line of code
===========================================

.. highlight:: none

When writing responses to issues on GitHub, I often find myself wanting to grab the permalink to a specific piece of code.
Up until now I've always just clicked around the UI until I've found the piece of code I'm looking for.

However, surely I can convince Emacs to generate the correct URL for me?

Permalinks on GitHub have the following structure::

  https://github.com/<owner>/<repo>/blob/<commit>/<filepath>#L<start>(-L<end>)

So building the URL should be "just" a case of looking up the relevant info and joining it all together!

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-git.el

   (defun alc-git-permalink-to-kill-ring ()
     "Construct a permalink URL for the current line or region and place it on
   the kill-ring"
     (interactive)
     (if-let* ((repo (alc-git-get-remote-url))
               (commit (alc-git-get-commit))
               (filepath (alc-git-get-filepath))
               (pos (alc-git-get-position))
               (path-start (format "%s#L%s" filepath (nth 0 pos)))
               (url (s-join "/" `(,repo "blob" ,commit ,path-start))))
         (kill-new
          (if (nth 1 pos)
              (format "%s-L%s" url (nth 1 pos))
            url))
       (message "No permalink found")))

Owner and Repo
--------------

It's easy enough to get this information from the configured remotes of the git repository.
I was a bit surprised not to find a function that already did this in either ``vc`` or ``magit``, though it did finally give me an excuse to learn about ``condition-case``

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-git.el

   (defun alc-git-get-remote-url ()
     "Return the url of the remote associated with the current buffer.

   Prioritizes 'upstream' but will fall back to 'origin' if it is unavailable."
     (condition-case err
         (vc-git-repository-url buffer-file-name "upstream")
       (error err
              (condition-case err
                  (vc-git-repository-url buffer-file-name "origin")
                (error err nil)))))

Commit
------

Getting the commit of the current file is easy enough with ``vc-working-revision`` however, it would be nice to figure out how

- to adapt this to also work when viewing an older version of a file with magit
- to check if the current commit exists on the remote

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-git.el

   (defun alc-git-get-commit ()
     "Return the commit hash for the current file"
     (vc-working-revision buffer-file-truename))

Filepath
--------

The filepath of course needs to be relative to the root of the repository

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-git.el

   (defun alc-git-get-filepath ()
     "Return the filepath of the current buffer relative to the root of the
   repository"
     (string-remove-prefix (vc-git-root buffer-file-truename)
                           buffer-file-truename))


Start and End
-------------

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-git.el

   (defun alc-git-get-position ()
     "Return the start and end line number"
     (if (region-active-p)
         `(,(line-number-at-pos (region-beginning))
           ,(line-number-at-pos (region-end)))
       `(,(line-number-at-pos) nil)))


.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-git.el

   (provide 'alc-git)
