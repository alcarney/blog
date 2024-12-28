Wezterm
=======

.. highlight:: none

`Wezterm <https://wezfurlong.org/wezterm/>`__ configuration

.. code-block:: make
   :filename: Makefile

   .PHONY: wezterm
   wezterm:
        test -L $(HOME)/.config/wezterm || ln -s $(shell pwd)/wezterm $(HOME)/.config/wezterm

.. code-block:: lua
   :filename: wezterm/wezterm.lua

   local wezterm = require 'wezterm'
   local config = wezterm.config_builder()

Appearance
----------

Choose a font

.. code-block:: lua
   :filename: wezterm/wezterm.lua

   config.font = wezterm.font('UbuntuMono Nerd Font')

Choose a light/dark theme based on the system.

.. code-block:: lua
   :filename: wezterm/wezterm.lua

   if wezterm.gui.get_appearance():find("Dark") then
     config.color_scheme = 'Modus-Vivendi'
   else
     config.color_scheme = 'Modus-Operandi'
   end

Use the "retro" tab bar.

.. code-block:: lua
   :filename: wezterm/wezterm.lua

   config.use_fancy_tab_bar = false

.. code-block:: lua
   :class: hidden
   :filename: wezterm/wezterm.lua

   return config
