:title: Bash Config
:date: 2025-02-16
:tags: bash
:identifier: 20250216T190236

Bash Configuration
==================

At some point I need to come back and figure out why things are set up this way.
But for now, this is how Fedora had setup the configuration for bash and if I don't follow this things break.

.. code-block:: make
   :filename: Makefile

   .PHONY: bash
   bash:
   	test -L $(HOME)/.bash_profile || ln -s $(shell pwd)/bash_profile $(HOME)/.bash_profile
   	test -L $(HOME)/.bashrc || ln -s $(shell pwd)/bashrc $(HOME)/.bashrc
   	test -L $(HOME)/.bashrc.d || ln -s $(shell pwd)/bash $(HOME)/.bashrc.d

``.bash_profile``
^^^^^^^^^^^^^^^^^

The profile doesn't do anything except source the ``bashrc`` file

.. code-block:: bash
   :filename: bash_profile

   # Get the aliases and functions
   if [ -f ~/.bashrc ]; then
           . ~/.bashrc
   fi

``.bashrc``
^^^^^^^^^^^

The ``bashrc`` then sources the system config

.. code-block:: bash
   :filename: bashrc

   if [ -f /etc/bashrc ]; then
           . /etc/bashrc
   fi

Adds user specific dirs to the ``PATH``

.. code-block:: bash
   :filename: bashrc

   if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
   then
       PATH="$HOME/.local/bin:$HOME/bin:$PATH"
   fi
   export PATH

Then sources additional config from the ``~/.bashrc.d`` dir

.. code-block:: bash
   :filename: bashrc

   if [ -d ~/.bashrc.d ]; then
           for rc in ~/.bashrc.d/*; do
                   if [ -f "$rc" ]; then
                           . "$rc"
                   fi
           done
   fi

   unset rc


Aliases
-------

.. code-block:: bash
   :filename: bash/10-aliases

   alias ls='ls -CFhX --color=auto --group-directories-first'
   alias pypath='echo $PYTHONPATH | tr '\'':'\'' '\''\n'\'''


Options
-------

I set the following options

.. code-block:: bash
   :filename: bash/00-options

   shopt -s autocd         # If no command found, but matches a directory, cd into it
   shopt -s checkjobs      # Warn about background jobs before exiting
   shopt -s checkwinsize   # Update the COLUMNS and LINES environment variables between each command
   shopt -s extglob        # Enable extended pattern matching features
   shopt -s globstar       # Enable recursive globbing i.e `./**/*.py`


Environment Variables
---------------------

``CDPATH``
^^^^^^^^^^

.. code-block:: bash
   :filename: bash/00-options

   [ -d "$HOME/Projects" ] && export CDPATH=".:~/Projects"

.. pull-quote::

   The search path for the cd command.
   This is a colon separated list of directories in which the shell looks for destination directories specified by the cd command. -- man(1) bash

This means I can ``cd`` into a project folder from anywhere on my system!

``PATH``
^^^^^^^^

Update the ``PATH`` based on whatever folders are available.

.. code-block:: bash
   :filename: bash/00-options

   paths=(
       "$HOME/go/bin"
       "$HOME/.cargo/bin"
       "$HOME/.npm-packages/bin"
   )

   for p in ${paths[@]}
   do
       [ -d $p ] && export PATH="$p:$PATH"
   done


History
-------

.. code-block:: bash
   :filename: bash/00-options

   shopt -s histappend

   HISTCONTROL=erasedups
   HISTFILESIZE=100000
   HISTIGNORE='cd:ls'
   HISTSIZE=10000


Prompt
------

.. code-block:: bash
   :filename: bash/20-prompt

   __venv_py_version()
   {
       if [ -z "${VIRTUAL_ENV}" ]; then
           echo ""
       else
           echo " 🐍 v$(python --version | sed 's/Python //')"
       fi
   }

   __is_toolbox()
   {
       if [ -f /run/.containerenv ] && [ -f /run/.toolboxenv ]; then
           name=$(grep name /run/.containerenv | sed 's/.*"\(.*\)"/\1/')

       else
           name="\h"
       fi

       echo "\[\e[32m\]${name}\[\e[0m\]"
   }

   if [ -f "/usr/share/git-core/contrib/completion/git-prompt.sh" ]; then
       source "/usr/share/git-core/contrib/completion/git-prompt.sh"

       export GIT_PS1_SHOWDIRTYSTATE=1       # (*) unstaged changes, (+) staged changes
       export GIT_PS1_SHOWSTASHSTATE=1       # ($) stashed
       export GIT_PS1_SHOWUNTRACKEDFILES=1   # (%) untracked files
       export GIT_PS1_SHOWUPSTREAM=verbose
       export GIT_PS1_SHOWCOLORHINTS=1

       export PROMPT_COMMAND='__git_ps1 "\n\w " "$(__venv_py_version)\n$(__is_toolbox) > " "[ %s]"'
   else
       export PS1="\W\n> "
   fi
