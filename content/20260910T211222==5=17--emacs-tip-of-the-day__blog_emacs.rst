:title: Emacs Tip of the Day
:date: 2026-09-11
:tags: blog, emacs
:identifier: 20260910T211222
:signature: 5=17

Emacs Tip of the Day
====================

.. highlight:: none

.. container:: post-teaser

   With each Emacs release you see a flurry of blog posts and thanks to Mastering Emacs, an `annotated version <https://www.masteringemacs.org/article/whats-new-in-emacs-311>`__ of the release notes.
   These do a great job of getting me excited to try out all of the features, but there's just one problem.

   It's information overload.

   I'm rarely in a position to action the information there and then, and before you know it, life happens and you forget what you've read about. I'm *sure* there's still options/features from Emacs 28 that I haven't got around to playing with.

   So... what if Emacs could suggest something to try each time I start it up?


Getting NEWS
------------

Emacs, as I'm sure you know, has a fantastic culture of documentation and self discovery.
Every release is accompanied with a ``NEWS`` file describing every meaningful change, only a :kbd:`C-h n` away.

That means there is a function to open the latest news file ``view-emacs-news``.

If you look at the definition, you will see you can even view the ``NEWS`` for previous Emacs versions, going all the way back to v18.
Even Emacs "pre-history" is documented in an aggregated ``NEWS.1-17`` file!
You will also notice however, that the logic for getting the filepath to the ``NEWS`` file is embedded within the same function that calls ``find-file`` on it, so there's no way to get one without the other.

Or is there? :emphasis:`*cue VSauce music*...`

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-dashboard.el
   :template: elisp-module

   (defun alc-dashboard--get-news-buffer (&optional version)
     "Return the Emacs news buffer for the given VERSION"
     (let ((display-buffer-overriding-action
              '((display-buffer-no-window)
                (allow-no-window . t))))
       (view-emacs-news version)
       (buffer-name)))

By setting ``display-buffer-overriding-action`` we can suppress the default ``find-file`` behaviour and force the file to be opened in the background.

Navigating NEWS
---------------

Now we have a buffer full of ``NEWS`` we need a way to identify individual items.
Let's look at a random snippet of the ``NEWS`` file for Emacs 30.1.

.. code-block::

   * New Modes and Packages in Emacs 30.1

   ** New major modes based on the tree-sitter library

   ...

   *** New major mode 'php-ts-mode'.
   A major mode based on the tree-sitter library for editing PHP files.

   ** New package EditorConfig.
   This package provides support for the EditorConfig standard,
   an editor-neutral way to provide directory local (project-wide) settings.
   It is enabled via a new global minor mode 'editorconfig-mode'
   which makes Emacs obey the '.editorconfig' files.
   There is also a new major mode 'editorconfig-conf-mode'
   to edit those configuration files.

Section headers are one or more ``*`` characters followed by a blank line, whereas news items are one ore more ``*`` characters.

The format is simple enough that we only need a regular expression to write a function that will return a list of buffer offests of items in the current buffer.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-dashboard.el

   (defun alc-dashboard--get-news-items ()
     (let ((items nil))
       (save-excursion
         (goto-char (point-min))
         (while (re-search-forward "^[*]+ \\(.*\\)$" nil t)
           (let ((item-pos (match-beginning 1)))
             (forward-line)
             (unless (string= "" (string-trim (thing-at-point 'line t)))
               (push item-pos items)))))
       items))

You might be thinking, what good is a buffer offset when we want complete news items?

Well, if you open the mode help (:kbd:`C-h m`) for the ``NEWS`` file, you should see that ``outline-minor-mode`` is active, meaning all the navigation commands are available for us to use.
So given an ``item-pos`` we can use ``outline-mark-subtree`` to select the item's content

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-dashboard.el
   :slot: get-news-item

   (goto-char item-pos)
   (call-interactively 'outline-mark-subtree)
   (setq item (buffer-substring (region-beginning) (region-end)))

And then use ``oultline-up-heading`` to jump to the corresponding section header

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-dashboard.el
   :slot: get-news-section

   (call-interactively 'outline-up-heading)
   (setq section (thing-at-point 'line))

From there, it's easy enough to wrap this in a function to return a random news item from a given Emacs version.

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-dashboard.el

   (defun alc-dashboard-get-news-item (&optional version)
     "Get a random news item for the given Emacs VERSION"
     (with-current-buffer (alc-dashboard--get-news-buffer version)
       (let* ((items (alc-dashboard--get-news-items))
              (idx (random (length items)))
              (item-pos (nth idx items))
              item section)

   {{ insert(slots['get-news-item'], indent=6) }}

   {{ insert(slots['get-news-section'], indent=6) }}

         (list item section))))

Broadcasting NEWS
-----------------

From here we can play all sorts of tunes, just to name a few

- Pull random items from a random Emacs version (uniformly)
- Pull random items from a random Emacs version (weighted by release date)
- Pull items from NEWS sections we really care about (e.g. Emacs has N irc clients, you're likely to use only one).
- Add options to mark items as read so they are not repeated.
- Favourite items
- and so on...

However, writing a fully comprehensive tip of the day package is not what I'm looking to do right now, I just want a prompt to nudge me in the direction of something potentially interesting.

You may have noticed I named the module for this code ``alc-dashboard.el``, and while it *may* grow into a fancy dashboard, like those you see in Doom Emacs or similar I don't even want to do that yet.
Emacs already comes with an minimally viable dashboard

.. pull-quote::

   You mean ``about-emacs`` (:kbd:`C-h C-a`)?

No, not even that, the ``*scratch*`` buffer!

You can customize the ``initial-scratch-message`` variable so why not set it to display a random news item?
Let's write one more function to format the news item as a single string

.. code-block:: elisp
   :project: emacs
   :filename: lisp/alc-dashboard.el

   (require 's)

   (defun alc-dashboard-news-item-to-string (item)
     "Format the given news item as a string"
     (concat ";; "
       (s-join "\n;; "
         (s-split "\n"
           (format "%s\n-- %s" (car item) (cadr item))))))

Perhaps there's a nicer way to format the news item (perhaps somehow filling with a given ``fill-prefix``?) but this is what my current elisp skills can do.

Anyway it seems to do the job and we can use it to set the initial scratch message each time Emacs starts up.

.. code-block:: elisp
   :project: emacs
   :filename: init.el

   (use-package alc-dashboard
     :ensure nil
     :config (setq initial-scratch-message
                   (alc-dashboard-news-item-to-string (alc-dashboard-get-news-item))))


.. termshot:: /images/emacs-tip-of-the-day.cast
   :title: tmux

And for about 50 lines of elisp I'm happy with that! 😁
