:title: Series and Hierarchies with denote-sequence
:date: 2025-05-20
:tags: blogging, denote, sphinx
:identifier: 20250520T192340
:signature: 1=1

Series and Hierarchies with ``denote-sequence``
===============================================


.. code-block:: elisp
   :filename: emacs/init.el

   (use-package denote
     :ensure t
     :hook ((dired-mode . denote-dired-mode))
     :config

     ;; Add reStructuredText support to denote
     (add-to-list 'denote-file-types `(rst
                                       :extension ".rst"
                                       :date-key-regexp "^:date:"
                                       :date-value-function denote-date-iso-8601
                                       :date-value-reverse-function denote-extract-date-from-front-matter
                                       :front-matter ":title: %s\n:date: %s\n:tags: %s\n:identifier: %s\n:signature: %s\n\n"
                                       :title-key-regexp "^:title:"
                                       :title-value-function identity
                                       :title-value-reverse-function denote-trim-whitespace
                                       :signature-key-regexp ":signature:"
                                       :signature-value-function identity
                                       :signature-value-reverse-function denote-trim-whitespace
                                       :keywords-key-regexp "^:tags:"
                                       :keywords-value-function ,(lambda (ks) (string-join ks ", "))
                                       :keywords-value-reverse-function denote-extract-keywords-from-front-matter
                                       :identifier-key-regexp "^:identifier:"
                                       :identifier-value-function identity
                                       :identifier-value-reverse-function denote-trim-whitespace
                                       :link ":denote:link:`%2$s <%1$s>`"
                                       :link-in-context-regexp ,(concat ":denote:link:`.*?<\\(?1:" denote-id-regexp "\\)>`"))))


.. code-block:: elisp
   :filename: emacs/init.el

   (use-package denote-sequence
     :ensure t
     :after denote
     :custom
     (denote-sequence-scheme 'numeric))
