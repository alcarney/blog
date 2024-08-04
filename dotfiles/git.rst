Git
===

.. code-block:: make
   :filename: Makefile

   .PHONY: git
   git:
   	test -L $(HOME)/.gitconfig || ln -s $(shell pwd)/gitconfig $(HOME)/.gitconfig


Author
------

.. highlight:: none

Setting basic identity details for commits

.. code-block::
   :filename: gitconfig

   [user]
   name  = Alex Carney
   email = alcarneyme@gmail.com


Aliases
-------

.. code-block::
   :filename: gitconfig

   [alias]
   co = checkout
   amend = commit --amend --no-edit  # Squash changes into the previous commit

A nice view of a repository's history

.. code-block::
   :filename: gitconfig

   hist = log --branches --remotes --tags --graph --oneline --decorate


.. code-block::

   $ git hist
   * 9bbbedca (origin/sphinx-8, sphinx-8) lsp: Drop Sphinx 5.x, add support for Sphinx 8.x
   *   44f758bc (HEAD -> develop, upstream/develop, origin/develop) Merge branch 'release' into develop
   |\
   | * 6a2086c7 (tag: esbonio-vscode-extension-v0.95.1, upstream/release, release) Esbonio VSCode Extension Release v0.95.1
   | * 72be1341 (origin/take-2) code: Update changelog
   * | fc194b26 Start testing against 3.13
   * | 306fbaf9 Bump ruff version
   * | 4552ff34 [pre-commit.ci] pre-commit autoupdate
   * | 5bce0a3c build(deps): bump semver from 7.6.2 to 7.6.3 in /code
   * | d02c69ad build(deps-dev): bump @vscode/vsce from 2.30.0 to 2.31.1 in /code
   * | 8de0b24a devenv: Install the latest hatch
   * | c96bc561 devenv: Bump NodeJS version
   ...


A better (for some definition of "better") git status command

.. code-block::
   :filename: gitconfig

   s = !git status -sb && git --no-pager diff --shortstat

.. code-block::

   $ git s
   ## release...origin/release [ahead 2]
    M dotfiles.rst
    M dotfiles/bash.rst
   ?? dotfiles/.#git.rst
   ?? dotfiles/git.rst
    2 files changed, 12 insertions(+), 3 deletions(-)


Credential Helper
-----------------

This tells git to use the `GitHub CLI <https://cli.github.com/>`__ to authenticate when pushing/pulling from GitHub

.. code-block::
   :filename: gitconfig

   [credential "https://github.com"]
   helper =
   helper = !gh auth git-credential


Other Options
-------------

.. code-block::
   :filename: gitconfig

   [commit]
   verbose = true

   [core]
   editor = nvim

   [diff]
   colorMoved = default

   [merge]
   conflictstyle = diff3

   [pull]
   rebase = true

   [rerere]
   enabled = true

   # Used by forge.el
   [github]
   user = alcarney
