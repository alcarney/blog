:title: VSCode Config
:date: 2025-02-16
:tags: vscode
:identifier: 20250216T190725

VSCode
======

Add a ``Makefile`` rule to setup the configuration on a new machine

.. highlight:: none

.. code-block:: make
   :filename: Makefile

   .PHONY: vscode
   vscode:
        test -L $(HOME)/.config/Code/User || ln -s $(shell pwd)/vscode/ $(HOME)/.config/Code/User
	-code --install-extension charliermarsh.ruff
        -code --install-extension eamodio.gitlens
	-code --install-extension github.github-vscode-theme
	-code --install-extension ms-python.python
	-code --install-extension pkief.material-icon-theme
        -code --install-extension tamasfe.even-better-toml

.. code-block:: json
   :filename: vscode/settings.json

   {

Appearance
----------

Sync color theme to system theme

.. code-block:: json
   :filename: vscode/settings.json

   "window.autoDetectColorScheme": true,
   "workbench.preferredLightColorTheme": "GitHub Light Default",
   "workbench.preferredDarkColorTheme": "GitHub Dark Dimmed",

Change the icon theme

.. code-block:: json
   :filename: vscode/settings.json

   "workbench.iconTheme": "material-icon-theme",

Set the font

.. code-block:: json
   :filename: vscode/settings.json

   "editor.fontFamily": "'UbuntuMono NF', 'monospace', monospace",
   "editor.fontSize": 12,
   "editor.fontLigatures": true,
   "terminal.integrated.fontFamily": "'Ubuntu Mono NF', 'monospace', monospace",
   "terminal.integrated.fontSize": 12,
   "terminal.integrated.lineHeight": 1,

Adjust various UI elements

.. code-block:: json
   :filename: vscode/settings.json

   "editor.cursorStyle": "block",
   "editor.cursorBlinking": "solid",
   "editor.cursorSmoothCaretAnimation": "on",
   "editor.minimap.enabled": false,
   "editor.smoothScrolling": true,
   "debug.toolBarLocation": "commandCenter",
   "window.commandCenter": true,
   "window.titleBarStyle": "custom",
   "workbench.activityBar.location": "top",
   "workbench.editor.showTabs": "single",
   "workbench.layoutControl.enabled": true,
   "workbench.list.smoothScrolling": true,

Editing
-------

.. code-block:: json
   :filename: vscode/settings.json

   "files.autoSave": "off",
   "files.enableTrash": false,
   "files.insertFinalNewline": true,
   "files.trimTrailingWhitespace": true,
   "files.trimFinalNewlines": true,

Exclude files that aren't that useful from the explorer pane

.. code-block:: json
   :filename: vscode/settings.json

   "files.exclude": {
      "**/.hg": true,
      "**/.git": true,
      "**/.svn": true,
      "**/*.pyc": true,
      "**/.mypy_cache": true,
      "**/__pycache__": true,
   },

Languages
---------

Python
^^^^^^

.. code-block:: json
   :filename: vscode/settings.json

   "[python]": {
     "editor.rulers": [ 89 ]
   },

reStructuredText
^^^^^^^^^^^^^^^^

.. code-block:: json
   :filename: vscode/settings.json

   "[restructuredtext]": {
     "editor.tabSize": 3,
     "editor.wordBasedSuggestions": "off",
   },


.. code-block:: json
   :filename: vscode/settings.json

   }
