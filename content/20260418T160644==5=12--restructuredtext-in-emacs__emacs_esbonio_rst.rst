:title: reStructuredText in Emacs
:date: 2026-04-18
:tags: emacs, esbonio, rst
:identifier: 20260418T160644
:signature: 5=12

:in-project: emacs

reStructuredText in Emacs
=========================

.. code-block:: elisp
   :in-file: init.el

   (use-package rst
     :hook ((rst-mode . visual-wrap-prefix-mode))
     :bind (:map rst-mode-map
             ("C-c m" . alc-rst-mode-tmenu)))


Esbonio
-------

My primary use case for using reStructuredText is for `Sphinx <https://sphinx-doc.org/>`__ projects, so of course I'll be using `esbonio <https://docs.esbon.io/>`__!

.. code-block:: elisp
   :in-file: init.el

   (use-package esbonio
     :vc (:url "https://github.com/swyddfa/esbonio.el" :rev "main")
     :hook ((rst-mode . esbonio-eglot-ensure)))

Which exposes some functions I want to put into the transient menu for ``rst-mode`` buffers

.. code-block:: elisp
   :in-file: init.el

   (transient-define-prefix alc-rst-mode-tmenu ()
     "Major mode transient menu for `rst-mode'"
     ["Esbonio"
      ["Previews"
       ("p" "Preview File" esbonio-preview-file)
       ("s" "Toggle Sync Scroll" esbonio-sync-scroll-mode)]])
