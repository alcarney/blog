:title: Managing Changes with ediff
:date: 2026-06-10
:tags: ediff
:identifier: 20260610T183929
:signature: 5=9=3

Managing Changes with ``ediff``
===============================

.. highlight:: none

.. container:: post-teaser

   Now that I have the ability to :denote:link:`edit the jj log <20260601T172422>` from within Emacs the next thing I wanted to try was reviewing diffs within Emacs and pushing worthwhile changes into the relevant revisions.

   I've never used it before but the obvious choice of frontend on the Emacs side would be ``ediff`` the question is... how to link it up with ``jj``...

``ui.diff-editor``
------------------

``jj`` provides the ``ui.diff-editor`` setting allowing you to specify the command it should invoke when running commands like ``jj squash --interactive``.
After consulting the `jj docs <https://docs.jj-vcs.dev/latest/config/#editing-diffs>`__ and ``(info "(ediff) Major Entry Points")`` I tried the following config:

.. code-block:: toml

   ui.diff-editor = [
     "emacsclient", "--eval",
     "(ediff-directories \"$left\" \"$right\" \".*\")"
   ]

Initially this looked very promising!

After running ``jj squash -i`` a ``MetaEdiff`` buffer opened and I was able to start browsing the changes.
Unfortunately, it didn't take long to notice the flaw in the plan...

Switching back to the terminal I noticed that the ``jj squash -i`` command had already completed and had pushed **all** changes from the current revision into the parent!

.. admonition:: The ``ui.diff-editor`` workflow

   #. Before invoking ``ui.diff-editor``, ``jj`` prepares a folder in ``/tmp`` like the following::

         $ tree /tmp/jj-diff-vrlA8y/
         /tmp/jj-diff-vrlA8y/
         ├── left
         │   └── content
         │       └── 20251213T204155==5=8--ibuffer.rst
         ├── left_state
         │   └── tree_state
         ├── right
         │   ├── content
         │   │   ├── 20251212T230256--adsp-the-podcast__bib_podcast.rst
         │   │   ├── 20251213T204155==5=8--ibuffer.rst
         │   │   ├── 20260103T183119==7=1--rtiow-with-zig__zig.rst
         │   │   ├── 20260105T224240==8--writing-a-wayland-client__python_wayland.rst
         │   │   └── 20260117T205315--bending-emacs__bib_emacs.rst
         │   └── JJ-INSTRUCTIONS
         └── right_state
             └── tree_state

         7 directories, 9 files

   #. ``jj`` then starts the ``ui.diff-editor`` with the expectation that the tool modifies the contents of ``/tmp/jj-diff-.../right`` to contain the content to be pushed into the target revision.

   #. ``jj`` waits for the ``ui.diff-editor`` process to exit, at which point it considers the changes to be confirmed and commits the result.

Unfortunately, there was no obvious (to me at least) way of holding the ``emacsclient`` process open while I made changes via ``ediff``.

Even if I could solve the issue with ``emacsclient --eval`` this workflow was still backwards to the one I was looking to implement.
I wanted to browse the diffs in Emacs, and then tell ``jj`` to move specific changes around, rather than having ``jj`` ask me "*of all of these diffs, which do you want to move?*".

As far as I could tell, there's no way to ``jj squash`` portions of a file without invoking the ``ui.diff-editor``, so I couldn't have Emacs run a series of ``jj squash`` commands as I selected various changes either...

``jj workspace add``
--------------------

But who said we had to use ``jj squash``?

Just before I picked up ``jj`` I had started experimenting with `git worktrees <https://git-scm.com/docs/git-worktree>`__ and have been slowly adopting the following convention when cloning repositories::

  git clone <url> ~/Projects/<owner>/<repo>/<name>

where ``<name>`` typically corresponds to a branch or a tag.

Not only does this make it easy to remember where I cloned a repo, but there's an obvious space under ``<owner>/<repo>/`` to add additional worktrees.
Thankfully ``jj`` has an equivalent concept -- workspaces -- which gave me an idea.

- I created a workspace called ``to`` (named after the ``--to`` argument accepted by the ``jj squash`` command) and selected the revision I wanted to push changes into::

    scratch $ jj workspace add ../to
    scratch $ cd ../to
    to $ jj edit <change-id>

- I evaluated the following in an ``eshell`` buffer to start an ``ediff`` session

  .. code-block:: elisp

     blog $ ediff-directories "scratch/" "to/" ".*"

  .. termshot:: /images/ediff-multi.cast

  (I was mildly dissapointed to realise that this included **all** files and directories, regardless of if there were any differences or not but let's focus on one thing at a time.)

- It didn't take long though to find a file containing some changes I was interested in moving across

  .. termshot:: /images/ediff-demo.cast

  (I think the colour scheme is backwards to how I would expect to see it, but perhaps that can be fixed just by flipping the argument order?).

  Hitting :kbd:`b` followed by :kbd:`wb` copied the change from the top window to the bottom and saved it.

- Finally, to get ``jj`` to notice the change and rebase any commits accordingly, I needed to run a command like ``jj status`` in the ``to/`` workspace.

That proved the concept at least, now it's time to write some elisp to make it easier to setup!

Basic ``ediff`` Integration
---------------------------

If you've spent any time browsing the ``ediff`` source code, you will have realised it is *very* extensible.
On one hand this is great! There should be more than enough flexibility built-in to align it to this workflow.
On the other hand... there are a **lot** of moving parts and details to get right to get something that works well.

In fact, there are so many moving parts, it's kind of hard to know where to start! 😅

Eventually I decided that I wanted an entry point similar to ``ediff-directories`` but something that felt closer to ``jj``...
actually wouldn't it be great to have something that resembled the output from ``jj status``?

.. code-block:: console

   $ jj status
   Working copy changes:
   M .dir-locals.el
   M .github/workflows/release.yml
   M Makefile
   A bytes.wasm
   M conf.py
   R content/{20250305T195742==5=3--language-servers-in-emacs__emacs.rst => 20250305T195742==5=3--eglot__emacs.rst}
   A content/20251212T230256--adsp-the-podcast__bib_podcast.rst
   M content/20251213T204155==5=8--ibuffer.rst
   A content/20260103T183119==7=1--rtiow-with-zig__zig.rst
   A content/20260105T224240==8--writing-a-wayland-client__python_wayland.rst
   A content/20260117T205315--bending-emacs__bib_emacs.rst
   M content/20260601T172422==5=9=1--alc-jj-log-view-mode__blog_treesitter.rst
   M content/20260610T183929==5=9=3--managing-changes-with-ediff__ediff.rst
   A content/20260630T162924==9--webassembly__wasm.rst
   A content/20260630T163145==9=1--binary-format__wasm.rst
   M pyproject.toml
   M uv.lock
   Working copy  (@) : npwrloyp 3f29045e scratch
   Parent commit (@-): qulqkxyo d3e9ee57 (no description set)


``ediff-directories`` is defined in ``ediff-mult.el`` and the file's ``Commentary:`` section provides the detail necessary to implement your own entry point. In fact, it actually encourages users to add their own!

Be sure to read the commentary yourself for the full details, but the process roughly breaks down into the following stages.

- :ref:`jj-ediff-list-changes`
- :ref:`jj-ediff-desc-changes`
- :ref:`jj-ediff-render-changes`
- :ref:`jj-ediff-act-change`
- :ref:`jj-ediff-bring-together`

.. _jj-ediff-list-changes:

Build a list of changes
^^^^^^^^^^^^^^^^^^^^^^^

The framework setup by ``ediff-mult.el`` expects changes (a.k.a session descriptions) to be represented in the following format::

  (nil nil (obj1 . nil) (obj2 . nil) (obj3 . nil))

where ``obj1``, ``obj2``, ``obj3`` are typically filepaths but can also refer to other objects like patches.

As far as I can tell, the ``ediff-mult.el`` framework doesn't use these objects for anything so we are free to pick whatever makes sense here.
So, given the output of ``jj diff --summary``::

  M .dir-locals.el
  A bytes.wasm
  M conf.py
  R content/{20250305T195742==5=3--language-servers-in-emacs__emacs.rst => 20250305T195742==5=3--eglot__emacs.rst}
  ...

I've opted to set ``obj1`` to the path that has changed and ``obj3`` to be the change type (``M``, ``A``, ``R`` etc.) as implemented by the following function

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-ediff--prepare-squash-changelist ()
     "Process the output of jj diff and return a list of changes for ediff."
     (with-temp-buffer
      (call-process "jj" nil t nil "diff" "--summary")
      (mapcar #'(lambda (line) `(nil nil
                                 (,(substring line 2) nil)     ; obj1
                                 (nil nil)                     ; obj2
                                 (,(substring line 0 1) nil))) ; obj3
              (string-split (buffer-string) "\n" t))))

Which produces a list like the following

.. code-block:: elisp

   ELISP> (alc-jj-ediff--prepare-squash-changelist)
   ((nil nil (".dir-locals.el"          nil) (nil  nil)  ("M"  nil))
    (nil nil ("bytes.wasm"              nil) (nil  nil)  ("A"  nil))
    (nil nil ("conf.py"                 nil) (nil  nil)  ("M"  nil))
    (nil nil ("before.rst => after.rst" nil) (nil  nil)  ("R"  nil))
    ; ...    (obj1                      nil) (obj2 nil)  (obj3 nil))
    (nil nil ("uv.lock"                 nil) (nil  nil)  ("M"  nil)))

For renames it's probably better to split names ``"after.rst"`` out into ``obj2`` but I'll leave that to another day.

.. _jj-ediff-desc-changes:

Describe the changes
^^^^^^^^^^^^^^^^^^^^

In addition to the list of changes, ``ediff-mult.el`` expects a ``HEADER`` prepended to your list of changes::

  (regexp metaobj1 metaobj2 metaobj3 merge-save-buffer comparison-function)

Again, I *think* ``regexp``, ``metaobj1``, ``metaobj2``, ``metaobj3`` are free for us to use as we'd like.
However, I haven't yet managed to figure out how ``merge-save-buffer`` and ``comparison-function`` are used so I'm not entirely sure what they should be set to.

Currently I've opted to set ``metaobj1`` and ``metaobj2`` to the ``<change-id> <commit-id> <description>`` corresponding with the source and desintation revisions:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-ediff--prepare-squash-header ()
     "Process the output of 'jj show' and return the header information for ediff."
     (let ((wcopy (alc-jj--revision-info "@"))
           (to (alc-jj--revision-info "to@")))
       (list nil wcopy to nil nil #'string=)))

   (defun alc-jj--revision-info (revision)
     "Return a short string describing the given revision"
     (with-temp-buffer
       (call-process "jj" nil t nil
         "show" revision
         "-T" "separate(\" \", change_id.shortest(8), commit_id.shortest(8), description.first_line())"
         "--no-patch")
       (string-trim (buffer-string))))

This is taking advantage of jj's `templates <https://docs.jj-vcs.dev/latest/templates/>`__ to return the relevant information in the required format.

.. _jj-ediff-render-changes:

Render the changes
^^^^^^^^^^^^^^^^^^

Now that we can list the changes to consider, the next job is to construct a ``MetaEdiff`` buffer to present them.

Since this buffer is used to track and launch this group of ediff sessions we do have to make sure we provide everything that ``ediff-mutli.el`` expects to find.
But since the required information is stored in overlays, we still have a surprising amount of freedom over the format of the buffer.

Copying the overall structure of ``ediff-redraw-directory-group-buffer`` I eventually arrived at the following redraw function.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-ediff-redraw-session-buffer (meta-list)
     "Given the META-LIST of changes render the corresponding MetaEdiff buffer."
     (let ((meta-buffer (ediff-get-group-buffer meta-list))
           (session-num 0)
           ;; Declare any setq'q vars here so they don't leak into the wider scope
           point elt header)
       (ediff-with-current-buffer meta-buffer
         (setq point (point))
         (erase-buffer)
         ;; delete phony overlays that used to represent sessions before the buffer
         ;; was redrawn
         (mapc #'delete-overlay (overlays-in 1 1))

         ;; Pull the HEADER off the list of changes
         (setq header (car meta-list)
               meta-list (cdr meta-list))

         (insert "Working copy changes:\n")

         ;; Loop over each change and insert it into the buffer.
         (while meta-list
           (setq elt (car meta-list)
                 meta-list (cdr meta-list)
                 session-num (1+ session-num))
           (alc-jj-ediff-insert-session-info-in-meta-buffer elt session-num))

         ;; Render information provided by the HEADER
         (insert (format "Working copy   (@)  : %s\n" (nth 2 header)))
         (insert (format "Target revsion (to@): %s\n" (nth 3 header)))

         (set-buffer-modified-p nil)
         (goto-char point)
         meta-buffer)))

There's a few details worth calling out:

- The ``(insert "Working copy changes:\n")`` line is not only necessary to reproduce the look of ``jj status`` but is essential to ensure ``ediff-mult.el`` works as expected.
  If you don't include some kind of header in the buffer you break some assumptions made by ``ediff-mult.el`` and it will enter an infinite loop!

- To comply with another assumption made by ``ediff-mult.el``, ``alc-jj-ediff-redraw-session-buffer`` must return the ``meta-buffer``.

- So that ``ediff-mult.el`` can perform the necessary book keeping, ``alc-jj-ediff-insert-session-info-in-meta-buffer`` must ensure that the list describing the change (as returned by ``alc-jj-ediff--prepare-squash-changelist``) is added to an overlay corresponding to the change's position in the buffer

  .. code-block:: elisp
     :project: emacs
     :filename: lisp/alc-jj.el

     (defun alc-jj-ediff-insert-session-info-in-meta-buffer (session-info session-num)
       (let ((file-a (ediff-get-session-objA session-info))
             (file-b (ediff-get-session-objB session-info))
             (change (ediff-get-session-objC session-info))
             (start-pos (point)))
         (ediff-insert-session-activity-marker-in-meta-buffer session-info)
         (ediff-insert-session-status-in-meta-buffer session-info)
         (insert (format "%s %s\n" (car change) (car file-a)))
         (ediff-set-meta-overlay start-pos (point) session-info session-num)))

  Thankfully, using ``ediff-insert-session-info-in-meta-buffer`` as a guide implementing this function was quite straight forward.

.. _jj-ediff-act-change:

Act on changes
^^^^^^^^^^^^^^

The final piece of the puzzle is to define what should happen when one of these changes are selected.
This is done through an action function and it is responsible for actually launching/resuming the corresponding ediff session.

Below is my first attempt at writing such a function, essentially it's a heavily stripped down version of ``ediff-filegroup-action``

.. code-block:: elisp
   :project: emacs

   (defun alc-jj-ediff-filegroup-action ()
     (interactive)
     (let* (;; Standard command invocation metadata
            (pos (ediff-event-point last-command-event))
            (meta-buffer (ediff-event-buffer last-command-event))
            (info (ediff-get-meta-info meta-buffer pos))
            (session-buffer (ediff-get-session-buffer info))
            ;; file objects
            (file-a (ediff-get-session-objA-name info))
            ;; jj specifics.
            (current-ws (alc-jj--get-workspace-root))
            (to-ws      (alc-jj--get-workspace-root "to")))
       (cond ;; reactivate an existing session
             ((ediff-buffer-live-p session-buffer)
              (ediff-with-current-buffer session-buf (ediff-recenter 'no-rehighlight)))
             ;; start a new one
             (t
              (ediff (concat to-ws "/" file-a)
                     (concat current-ws "/" file-a))))))

To summarise:

- The ``let*`` binding uses a bunch of ediff helper functions to figure out what was selected and to calcuate the two root directories corresponding to the current (``@``) and ``to@`` jj workspaces.
- The ``cond`` expression (attempts to) resume a previously suspended ediff session corresponding with the selection and otherwise spins up a new one.

.. _jj-ediff-bring-together:

Bring it all together
^^^^^^^^^^^^^^^^^^^^^

With all the main components in place, all that's left is to define a command that wires it all up to provide an ``ediff-mult.el`` entry point!

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-squash-changes ()
     "Start an ediff session to selectively move changes from the current workspace
   into the \"to@\" workspace."
     (interactive)
     (ediff-show-meta-buffer
       (ediff-prepare-meta-buffer #'alc-jj-ediff-filegroup-action
                                  `(,(alc-jj-ediff--prepare-squash-header)
                                    ,@(alc-jj-ediff--prepare-squash-changelist))
                                  "*jj squash --interactive"
                                  #'alc-jj-ediff-redraw-session-buffer
                                  'alc-jj-squash)))

Invoking this command presents a ``MetaEdiff`` buffer resembling the output ``jj status``

.. termshot:: /images/alc-jj-ediff-squash.cast

I can then select one of the modified files from the list and browse the changes!

.. termshot:: /images/alc-jj-ediff-view-changes.cast


Finishing Touches
-----------------

We're getting close, but there are some further details to iron out before this setup could be used for real.

Suspend / Resume
^^^^^^^^^^^^^^^^

Despite including code in ``alc-jj-ediff-filegroup-action`` to resume a suspended ediff session, if you actually tried resuming a session you would find that a duplicate session would be created instead.

This is because it's the responsibility of the action function to arrange for the ``*Ediff Control Panel*`` buffer to be stored in the session's ``info`` list::

   (nil nil (obj1 . nil) (obj2 . nil) (obj3 . nil))

In fact, the helper function we use to get the ``session-buffer`` (``ediff-get-session-buffer``) expects to find it in the position of the first ``nil`` in the list.
Once again using ``ediff-filegroup-action`` as a reference we can see that this is done by utilising a startup hook passed to the call to the ``ediff`` function:

.. code-block:: elisp

   (ediff (concat to-ws "/" file-a)
          (concat current-ws "/" file-a)
          `(list (lambda ()
                   (setcar (quote ,info) ediff-control-buffer))))

However, I think I prefer using a named function for this:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-ediff--store-control-buffer (session)
     "Store the `ediff-control-buffer' in the given SESSION info list.
   To be used as an ediff startup hook"
     `(lambda ()
         (setcar (quote ,session) ediff-control-buffer)))

See :ref:`jj-ediff-filegroup-action` for how this function is used.

Committing Changes
^^^^^^^^^^^^^^^^^^

In order for ``jj`` to recognize that something has changed we need run a command like ``jj status`` in both the current and ``to@`` workspaces.

Thankfully, ``ediff`` provides more than just startup hooks, (see ``(info "(ediff)Hooks")`` for details) for example ``ediff-suspend-hook`` and ``ediff-quit-hook`` hooks are run each time a session is suspended or quit respectively.

Shamelessly stealing a pattern from ``ediff-mult.el`` we can use a startup hook to configure a quit hook local to the current session:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-ediff--snapshot-on-exit (workspace)
     "Run 'jj status' in the given WORKSPACE when ediff quits."
     `(lambda ()
         (add-hook 'ediff-quit-hook
                   (lambda ()
                     (let ((default-directory ,workspace))
                       (call-process "jj" nil nil nil "status")))
                   nil 'local)))

See :ref:`jj-ediff-filegroup-action` for how this function is used.

.. _jj-ediff-filegroup-action:

``alc-jj-ediff-filegroup-action``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For completeness, here is the updated version of the ``alc-jj-ediff-filegroup-action`` function incorporating the changes outlined above.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-ediff-filegroup-action ()
     (interactive)
     (let* (;; Standard command invocation metadata
            (pos (ediff-event-point last-command-event))
            (meta-buffer (ediff-event-buffer last-command-event))
            (info (ediff-get-meta-info meta-buffer pos))
            (session-buffer (ediff-get-session-buffer info))
            ;; file objects
            (file-a (ediff-get-session-objA-name info))
            ;; jj specifics.
            (current-ws (alc-jj--get-workspace-root))
            (to-ws      (alc-jj--get-workspace-root "to")))
       (cond ;; reactivate an existing session
             ((ediff-buffer-live-p session-buffer)
              (ediff-with-current-buffer session-buffer (ediff-recenter 'no-rehighlight)))
             ;; start a new one
             (t
              (ediff (concat to-ws "/" file-a)
                     (concat current-ws "/" file-a)
                     ;; startup-hooks
                     `(list ,(alc-jj-ediff--store-control-buffer info)
                            ,(alc-jj-ediff--snapshot-on-exit to-ws)
                            ,(alc-jj-ediff--snapshot-on-exit current-ws)))))))

``alc-jj-log-view-set-target-revision``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, to complement the new entry point :ref:`alc-jj-log-view-squash-changes <jj-ediff-bring-together>` it would be nice to have the ability to point the ``to@`` workspace at different revisions from within the log view.

What's nice is that as soon as you have multiple workspaces ``jj`` automatically includes them in the log, and in a format that didn't require me to adjust my :ref:`tree-sitter grammar <jj-log-grammar>`! ::

  @  npwrloyp alcarneyme@gmail.com 2026-06-10 23:42:02 default@ d1e9f171
  │  scratch
  ○  yrqozqzu alcarneyme@gmail.com 2026-06-10 18:26:30 to@ a79ce09f
  │  emacs: Add tweaks from Emacs Redux article

The hardest part about this is making sure the ``to/`` workspace is there in the first place:

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj--get-workspace-root (&optional name)
     (with-temp-buffer
       (if (eq 0 (apply #'call-process "jj" nil t nil "workspace" "root"
                                       (if name (list "--name" name) '())))
         (string-trim (buffer-string)))))

   (defun alc-jj-get-workspace (name &optional create)
     "Return the path to the workspace with the given NAME, if CREATE is t then the workspace will be
   created if necessary"
     (let ((path    (alc-jj--get-workspace-root name))
           (current (alc-jj--get-workspace-root)))
       (if (not (or path current))
         (error "Not a jj repo."))
       (if (and (null path) create)
          (let ((new-path (concat (file-name-directory current) name)))
            (call-process "jj" nil t nil "workspace" "add" new-path)
            new-path)
        path)))

However, once the workspace is available the only thing left to do is running ``jj edit`` from the right workspace folder

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-jj.el

   (defun alc-jj-log-view-set-target-revision ()
     "Move the to@ workspace to point at the revision under point."
     (interactive)
     (if-let ((change-id (alc-jj-log-view--change-at-point)))
       (progn
         (let ((default-directory (alc-jj-get-workspace "to" t)))
           ;; The workspace might be stale...
           (call-process "jj" nil nil nil "workspace" "update-state")
           (call-process "jj" nil nil nil "edit" change-id))
         ;; Be sure to update the log relative to the current workspace
         (alc-jj-log-view-reload))))

Final Thoughts
--------------

Despite having something I can start using day to day there is still a lot that can still be added, including:

- Support for added (``A``) and renamed (``R``) files.

- Refreshing the ``MetaEdiff`` buffer to reflect changes made.

- Despite using functions like ``ediff-insert-session-activity-marker-in-meta-buffer`` and ``ediff-insert-session-status-in-meta-buffer`` I don't see any status indications, so there are a few more details to figure out.

This approach, while it aligns with the way I want to work it does introduce some problems:

- Going behind ``jj``'s back and moving changes without it's knowledge means there's a fair amount of work needed to make sure ``jj`` is kept up to date and I doubt that I've handled every case yet.

- I've not confirmed this yet, but I also wouldn't be surprised if I couldn't use ``jj undo`` to undo an edit like I'd be able to if I used ``jj squash``.

However, regardless of if this was a good idea or not in the long run, I've once again learnt a lot and had a lot of fun while doing so! 😀
