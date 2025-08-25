:title: Emacs Appearance
:date: 2025-02-28
:tags: emacs
:identifier: 20250228T200007
:signature: 5=2

Emacs Appearance
================

Fonts
-----

I quite like the Ubuntu family of fonts, but use the "Nerd Font" version to get some extra icons

.. code-block:: elisp
   :filename: emacs/init.el

   (set-face-attribute 'default nil :family "UbuntuMonoNerdFont" :height 120)
   (set-face-attribute 'fixed-pitch nil :family "UbuntuMonoNerdFont" :height 120)
   (set-face-attribute 'variable-pitch nil :family "UbuntuSansNerdFont" :weight 'light :height 120)

Make it easy to get relevant nerd icons

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package nerd-icons
     :ensure t)


Theme
-----

Load my theme related customisations, see :denote:link:`Emacs Themes <20250708T133920>` for details.

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package alc-theme
     :load-path "lisp"
     :config
     (require-theme 'modus-themes t)

     (setopt modus-themes-bold-constructs t
             modus-themes-italic-constructs t
             modus-themes-prompts '(bold italic)
             modus-themes-variable-pitch-ui nil)

     (setq alc-theme-load-light-theme-function
           (lambda () (modus-themes-load-theme 'modus-operandi))
           alc-theme-load-dark-theme-function
           (lambda () (modus-themes-load-theme 'modus-vivendi)))

     (add-to-list 'after-make-frame-functions 'alc-theme-sync-to-system-theme))

Line Numbers
------------

Enable line numbers for programming modes

.. code-block:: elisp
   :filename: emacs/init.el

   (add-hook 'prog-mode-hook (lambda () (display-line-numbers-mode t)))

Reserve enough space to display a line number that is 4 digits long and when a buffer is narrowed, always display the actual line number.

.. code-block:: elisp
   :filename: emacs/init.el

   (setq-default display-line-numbers-widen t
                 display-line-numbers-width 4)

Scrolling
---------

With Emacs 29 came ``pixel-scroll-precision-mode`` which makes the scrolling with a touchpad experience much nicer overall.

.. code-block:: elisp
   :filename: emacs/init.el

   (setq pixel-scroll-precision-use-momentum nil
         pixel-scroll-precision-interpolate-page t
         pixel-scroll-precision-momentum-seconds 0.5)
   (pixel-scroll-precision-mode t)

Tab Bar
-------

Not to be confused with the tabs you see in editors like VSCode, tabs allow for easy switching between different collections of windows - like workspaces.

As well as using the tab bar to show... well tabs, I also make use of the ``tab-bar-format-global`` variable to show global status information like battery levels.

.. code-block:: elisp
   :filename: emacs/init.el

   (setq tab-bar-close-button-show nil)
   (setq tab-bar-tab-hints t)
   (setq tab-bar-auto-width nil)
   (setq tab-bar-format '(tab-bar-format-tabs-groups
                          tab-bar-separator
                          tab-bar-format-align-right
                          tab-bar-format-global
                          tab-bar-format-menu-bar))

   (defun alc-tab-bar-tab-name-format-hints (name _tab i)
     (if tab-bar-tab-hints (concat (format "-%d-" i) "") name))

   (defun alc-tab-bar-tab-group-format-function (tab i &optional current-p)
     (propertize
      (concat (funcall tab-bar-tab-group-function tab))
      'face (if current-p 'tab-bar-tab-group-current 'tab-bar-tab-group-inactive)))

   (setq tab-bar-tab-group-format-function 'alc-tab-bar-tab-group-format-function)
   (setq tab-bar-tab-name-format-functions '(alc-tab-bar-tab-name-format-hints
                                             tab-bar-tab-name-format-close-button
                                             tab-bar-tab-name-format-face))

   ;; Disable the menu-bar, since it's accessible via the tab bar.
   (menu-bar-mode -1)
   (add-hook 'after-init-hook #'tab-bar-mode)

**Battery Info**

.. code-block:: elisp
   :filename: emacs/init.el

   (display-battery-mode)

**Time**

.. code-block:: elisp
   :filename: emacs/init.el

   (setq display-time-format "%H:%M %d/%m/%y"
         display-time-default-load-average nil)
   (display-time-mode)

Modeline
--------

For reference, here are the components that were in the default modeline

- ``mode-line-mule-info``
- ``mode-line-client``
- ``mode-line-frame-identification``
- ``mode-line-position``
- ``mode-line-misc-info``
- ``mode-line-end-spaces``

.. code-block:: elisp
   :filename: emacs/init.el

   (use-package alc-modeline
     :after alc-theme
     :load-path "lisp"
     :config
     (setq-default mode-line-format
                '("%e"
                  mode-line-front-space
                  alc-modeline-window-dedicated
                  alc-modeline-project-identification
                  "  "
                  alc-modeline-remote-indication
                  alc-modeline-buffer-identification
                  " "
                  alc-modeline-buffer-position
                  "      "
                  mode-line-modes
                  )))

See for more details

Miscellaneous
-------------

Disable some GUI elements

.. code-block:: elisp
   :filename: emacs/early-init.el

   (blink-cursor-mode -1)
   (tool-bar-mode -1)

   (setq inhibit-x-resources t
         inhibit-startup-message t)

And enable others

.. code-block:: elisp
   :filename: emacs/early-init.el

   (context-menu-mode t)
