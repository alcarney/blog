:title: Eat: Emulate a terminal
:date: 2025-07-05
:tags: emacs
:identifier: 20250705T225630
:signature: 5=7=1

Eat: Emulate a Terminal
=======================

The `emacs-eat <https://codeberg.org/akib/emacs-eat>`__ is a terminal emulator written in Emacs Lisp.

One of its best features is to turn eshell into a complete terminal environment

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package eat
     :ensure t
     :hook (eshell-load . eat-eshell-mode))
