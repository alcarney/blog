:title: Cusomising the Emacs Modeline
:date: 2025-02-28
:tags: emacs
:identifier: 20250228T200007
:signature: 5=2

Cusomising the Emacs Modeline
=============================

Heavily inspired by Protesilaos' excellent `tutorial <https://protesilaos.com/codelog/2023-07-29-emacs-custom-modeline-tutorial>`__ on writing custom modelines.

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
     :after (modus-themes)
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

And now for the definition of my custom components

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   ;;; alc-modeline.el --- Modeline configuration -*- lexical-binding: t -*-
   ;;; Code:

   (defgroup alc-modeline nil
     "My custom modeline"
     :group 'mode-line)

   (defgroup alc-modeline-faces nil
     "Faces for my custom modeline"
     :group 'alc-modeline)


**Project Indentification**

If the current buffer is associated with a project, show the name of the project.

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (defface alc-modeline-project-id-face
     '((default :inherit (bold)))
     "Face for styling the project indicator"
     :group 'alc-modeline-faces)

   (defvar-local alc-modeline-project-identification
    '(:eval
      (if-let ((pr (project-current))
               (file (buffer-file-name)))
          (propertize (format "🖿 %s " (project-name pr))
                      'face 'alc-modeline-project-id-face))))
   (put 'alc-modeline-project-identification 'risky-local-variable t)

**Remote Indication**

Replaces the default ``mode-line-remote`` and indicates if the current buffer is visiting a remote file

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (defvar-local alc-modeline-remote-indication
       '(:eval
          (when (file-remote-p default-directory)
            (propertize " ☁ "
                        'face '(bold)))))
   (put 'alc-modeline-remote-indication 'risky-local-variable t)

**Buffer Identification**

Intended to replace the default ``mode-line-buffer-identification`` and ``mode-line-modified`` components this displays the name of the buffer and a face depending on if the buffer is unsaved, read only etc.

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (defun alc-modeline-buffer-identification-face ()
     "Return the face(s) to apply to the buffer name in the modeline."
     (cond ((and (buffer-file-name)
                 (buffer-modified-p))
            'error)
           (buffer-read-only '(italic mode-line-buffer-id))
           (t 'mode-line-buffer-id)))

   (defvar-local alc-modeline-buffer-identification
       '(:eval
          (propertize "%b"
                      'face (alc-modeline-buffer-identification-face))))
   (put 'alc-modeline-buffer-identification 'risky-local-variable t)

**Buffer Position**

Shows line and column number for the position in the current buffer

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (defun alc-modeline-buffer-position-face ()
     "Return the face(s) to apply to the buffer position in the modeline."
     (if (mode-line-window-selected-p)
         'mode-line
       'mode-line-inactive))

   (defvar-local alc-modeline-buffer-position
       '(:eval
         (propertize "%l:%c"
                     'face (alc-modeline-buffer-position-face))))
   (put 'alc-modeline-buffer-position 'risky-local-variable t)

**Dedidcated Windows**

Indicates if the current window is dedicated.

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (defface alc-modeline-window-dedicated-face
     '((default :inherit (bold)))
     "Face for styling the dedicated window indicator"
     :group 'alc-modeline-faces)

   (defvar-local alc-modeline-window-dedicated
       '(:eval
         (when (window-dedicated-p)
           (propertize "🖈 "
                       'face 'alc-modeline-window-dedicated-face))))
   (put 'alc-modeline-window-dedicated 'risky-local-variable t)


**Modus Theme Integration**

The following code will only run if one of the ``modus-themes`` is active.
If they are active, then it will use colors from the theme to style elements of the modeline

.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (with-eval-after-load 'modus-themes
     (defun alc-modeline-apply-modus-colors ()
       "Style the modeline using colors provided by the `modus-themes'"
       (if (modus-themes--current-theme) ; Only if a modus-theme is active.
           (modus-themes-with-colors
             (set-face-attribute 'mode-line nil
                                 :background bg-active
                                 :overline bg-active
                                 :box `(:line-width 1 :color ,bg-active :style nil))
             (set-face-attribute 'mode-line-inactive nil
                                 :background bg-inactive
                                 :overline bg-inactive
                                 :box `(:line-width 1 :color ,bg-inactive :style nil))
             (set-face-attribute 'alc-modeline-project-id-face nil
                                 :background 'unspecified
                                 :foreground blue))))

     (alc-modeline-apply-modus-colors)
     (add-hook 'modus-themes-after-load-theme-hook #'alc-modeline-apply-modus-colors))


.. code-block:: elisp
   :filename: emacs/lisp/alc-modeline.el

   (provide 'alc-modeline)
