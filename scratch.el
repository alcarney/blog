(defun insert-links-for-closed-prs (repo start end buffer)
  (let ((shell-command-dont-erase-buffer t))
    (shell-command
     (string-join `("gh"
                    "-R" ,repo
                    "pr" "list"
                    "--state" "merged"
                    "--author" "alcarney"
                    "--search" ,(format "\"created:%s..%s\"" start end)
                    "--json" "number,title,url"
                    "--template" "'{{range .}}`#{{.number}} {{.title}} <{{.url}}>`__ {{\"\\n\"}}{{end}}'")
                  " ")
     (get-buffer buffer))))

(let ((start  "2024-11-01T00:00")
      (end    "2024-12-01T00:00")
      (buffer "notes-november.rst"))
  (insert-links-for-closed-prs "swyddfa/lsp-devtools" start end buffer)

  (with-current-buffer buffer (rst-mode)))
