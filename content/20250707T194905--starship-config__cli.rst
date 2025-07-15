:title: Starship config
:date: 2025-07-07
:tags: cli
:identifier: 20250707T194905

Starship config
===============

`Starship <https://starship.rs/>`__ is an all singing, all dancing framework for customising your shell prompt


Config
------

Tell editors that support completions in TOML files where to find the schema.

.. code-block:: toml
   :filename: starship.toml

   "$schema" = 'https://starship.rs/config-schema.json'

Ensure that there's a blank link between prompts.

.. code-block:: toml
   :filename: starship.toml

   add_newline = true


Jujutsu
"""""""

The following was pieced together using examples from the `jj wiki <https://github.com/jj-vcs/jj/wiki/Starship>`__

.. code-block:: toml
   :filename: starship.toml

   [custom.jj]
   ignore_timeout = true
   description = "The current jj status"
   when = "jj root --ignore-working-copy"
   symbol = "jj "
   command = '''
   jj log --revisions @ --no-graph --ignore-working-copy --color always --limit 1 --template '
     separate(" ",
       change_id.shortest(8),
       bookmarks,
       "|",
       concat(
         if(conflict, "✘"),
         if(divergent, ""),
         if(hidden, ""),
         if(immutable, "◆"),
       ),
       raw_escape_sequence("\x1b[1;32m") ++ if(empty, "(empty)") ++ raw_escape_sequence("\x1b[0m"),
       raw_escape_sequence("\x1b[1;32m") ++ coalesce(
         truncate_end(29, description.first_line(), "…"),
         "(no description set)",
       ) ++ raw_escape_sequence("\x1b[0m"),
     )
   '
   '''

Of course, if we have git and jj co-located, we only want one to show

.. code-block:: toml
   :filename: starship.toml

   [git_state]
   disabled = true

   [git_commit]
   disabled = true

   [git_metrics]
   disabled = true

   [git_branch]
   disabled = true

   [custom.git_branch]
   when = true
   command = "jj root --ignore-working-copy >/dev/null 2>&1 || starship module git_branch"
