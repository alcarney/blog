:title: Emacs Completions
:date: 2026-04-22
:tags: emacs
:identifier: 20260422T183610
:signature: 5=13

Emacs Completions
=================

No Emacs configuration is complete without a lengthy discussion on how completions are handled.

.. _emacs-completions-native:

``*Completions*``
-----------------

.. seealso::

   `The *Completions* Buffer Gets a Big Upgrade in Emacs 29 <https://robbmann.io/posts/emacs-29-completions/>`__

I actually quite like the default ``*Completions*`` buffer and used it extensively from Emacs 29.1 to around 30.1.
(Also seeing how there is a `bunch of stuff <https://github.com/emacs-mirror/emacs/blob/45304541ec906855e2412e15848bb8c8e7aa9d58/etc/NEWS#L165>`__ coming in Emacs 31 I'm sure I will switch back again to it before long! 😅)

My config wasn't anything particuarly exciting, as I only:

- Tweaked some options that control how it is rendered

  .. code-block:: elisp
     :project: emacs
     :filename: init.el

     (setq completions-detailed t
           completions-format 'one-column
           completions-group t
           completions-header-format (propertize "%s candidates\n" 'face 'shadow)
           completions-max-height 15
           completion-show-help nil)

- Tweaked some options that control its behaviour

  .. code-block:: elisp
     :project: emacs
     :filename: init.el

     (setq completion-auto-help 'visible
           completion-auto-select 'second-tab
           completion-cycle-threshold 3)

  That is to say, the ``*Completions*`` buffer only opens on the *second* attempt at completing something.
  However, once it is open keep it updated and only focus it on the second completion attempt with no progress made.

  If there are only 3 or fewer options, don't bother with the ``*Completions*`` buffer at all.

- Finally, use :kbd:`C-n` and :kbd:`C-p` to cycle through completion candidates.

  .. code-block:: elisp

     (dolist (kmap (list minibuffer-local-map completion-in-region-mode-map))
       (keymap-set kmap "C-p" #'minibuffer-previous-completion)
       (keymap-set kmap "C-n" #'minibuffer-next-completion))

However there are occasions where you want just a little bit... :ref:`more <emacs-completions-vertico>`.


Consult
-------

`Consult <https://github.com/minad/consult>`__, the grab-bag of utility functions built on top of ``completing-read``.
I admit, I probably don't use this as much as I should.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package consult
     :ensure t
     :custom
     (consult-preview-key "M-.")
     :bind (("C-x b" . consult-buffer)))

I don't often want the live preview feature, but it's nice to be able to opt into it by hitting :kbd:`M-.`

Embark
------

.. seealso::

   `Fifteen ways to use Embark <https://karthinks.com/software/fifteen-ways-to-use-embark/>`__

`Embark <https://github.com/oantolin/embark>`__, another excellent package, that I should try and use more deeply!

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package embark
     :ensure t
     :bind (("C-." . embark-act)
            ("M-." . embark-dwim)))


Since I have consult installed, use the recommended `emabrk-consult <https://github.com/minad/consult#embark-integration>`__ package (though I admit I'm not sure what it does!)

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package embark-consult
     :after (embark consult)
     :ensure t)

Orderless
---------

Continuing with the established theme I use the `orderless <https://github.com/oantolin/orderless>`__ completion style as even a basic config is useful, but it would be great to experiment with some `style dispatchers <https://github.com/oantolin/orderless#style-dispatchers>`__!

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package orderless
     :ensure t
     :custom
     (completion-styles '(orderless basic))
     (completion-category-defaults nil)
     (completion-category-overrides '((file (styles basic partial-completion)))))


.. _emacs-completions-vertico:

Vertico
-------

.. seealso::

   `VOMPECCC: A Modular Completion Framework for Emacs <https://www.chiply.dev/post-vompeccc>`__
      The article that pushed me over the edge to actually setting vertico up.

As mentioned in the :ref:`emacs-completions-native` section above, I was really happy with the built-in completions experience.
I find the ~95% of the time, I already know what I'm trying to select and I'm only really looking for a bit of tab-completion to save on the typing.

Therefore vertico's `unobtrusive <https://github.com/minad/vertico/blob/main/extensions/vertico-unobtrusive.el>`__ mode is perfect.

To cover that remaining 5%, I can use the `multiform extension <https://github.com/minad/vertico/tree/main#configure-vertico-per-command-or-completion-category>`__ to switch to a different mode for some pre-determined cases, or on an ad-hoc basis thanks to the ``vertico-mutliform-map`` keymap.

So I have arrived at the following config.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package vertico
     :ensure t
     :init
     (vertico-mode)
     :config

     (setq vertico-multiform-commands
           '((consult-line buffer)))

     (setq vertico-multiform-categories
           '((t unobtrusive)))

     (vertico-multiform-mode t))

The trick was realising I could use ``(t unobtrusive)`` as a fallback to active the unobtrusive mode by default!

As for ``completion-in-region``, I still don't feel the need for something like `corfu <https://github.com/minad/corfu>`__ but I was definitely excited to see the following snippet in vertico's README.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (setq completion-in-region-function #'consult-completion-in-region)

So I get to keep my consistent completion experience regardless of what I am completing!
