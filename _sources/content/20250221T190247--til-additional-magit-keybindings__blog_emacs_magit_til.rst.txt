:title: TIL: Additional magit keybindings
:date: 2025-02-21
:tags: blog, emacs, magit, til
:identifier: 20250221T190247

TIL: Additional magit keybindings
=================================

.. highlight:: none

.. container:: post-teaser

   It always helps to spend the time now and again to read the manual for the tools you use!
   By simply reading the `Getting Started <https://magit.vc/manual/magit/Getting-Started.html>`__ section of the ``magit`` user manual I found not one but two commands I had never come across before!

Despite using ``magit`` on and off for years I had only known about the ``magit-status`` command (bound to :kbd:`C-x g` by default).
However, magit also provides you with the following bindings

``magit-dispatch`` (:kbd:`C-x M-g`)
   This gives you immediate access to any of the commands you would normally invoke from the magit status buffer! ::

    Transient and dwim commands
     A Apply           i Ignore           r Rebase
     b Branch          I Init             t Tag
     B Bisect          j Display status   T Note
     c Commit          J Display buffer   V Revert
     C Clone           l Log              w Apply patches
     d Diff            L Log (change)     W Format patches
     D Diff (change)   m Merge            X Reset
     e Ediff (dwim)    M Remote           y Show Refs
     E Ediff           N Forge            Y Cherries
     f Fetch           o Submodule        z Stash
     F Pull            O Subtree          Z Worktree
     h Help            P Push             ! Run
                       Q Command

``magit-file-dispatch`` (:kbd:`C-c M-g`)
   As the name suggests, this opens a transient containing commands that can be applied to the current file ::

     File actions   Inspect                               Navigate        More actions
        s Stage      D Diff...   L Log...   B Blame...     p Prev blob     c Commit
        u Unstage    d Diff      l Log      b Blame        n Next blob     e Edit line
      , x Untrack                t Trace    m Blame echo   v Goto blob
      , r Rename                                           V Goto file
      , k Delete                                           g Goto status
      , c Checkout                                         G Goto magit
