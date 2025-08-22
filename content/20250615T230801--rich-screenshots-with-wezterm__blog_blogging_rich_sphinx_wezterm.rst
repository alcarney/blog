:title: rich screenshots with wezterm
:date: 2025-08-22
:tags: blog, blogging, rich, sphinx, wezterm
:identifier: 20250615T230801

Taking Rich Screenshots with Wezterm
====================================

.. highlight:: none

.. container:: post-teaser

   When working on this site, I've often wanted to include a screenshot or two.
   But since git doesn't work well with binary files and I don't want to have to deal with media hosting I've tended to shy away from it.

   However, a lot of what I want to take a screenshot of can be rendered in a terminal.

   Which is suddenly quite interesting as a terminal's contents can be entirely described in plain(-ish) text.
   Surely it must be possible to capture the contents of a terminal window and then render it as some kind of image? Perhaps an SVG?

   .. termshot:: /images/emacs-pdb.cast
      :title: M-x pdb

   Yes it is!

   In this blog post I describe how I arrived at the workflow I used to include the above screenshot on this website.

Taking the screenshot
---------------------

I'll admit it, this whole idea started out as a solution in search of a problem!

I've been using `WezTerm <https://wezterm.org>`__ as my terminal emulator for a while now, but I wasn't taking advantage of the fact that it is configured using Lua and so I was looking for an excuse to try something non-trivial.

Before long I found it - ``pane:get_lines_as_escapes()``.

The above function returns the current contents of the terminal pane as a string, including all the escape codes that control the formatting!
By
`mashing <https://wezterm.org/config/lua/window-events/augment-command-palette.html#adding-a-rename-tab-entry-to-the-palette>`__
together a couple of
`examples <https://wezterm.org/config/lua/pane/get_lines_as_escapes.html>`__
from the documentation I soon had a custom command I could invoke through the command palette which would dump the contents of the active pane to a text file.

.. code-block:: lua

   wezterm.on('augment-command-palette', function(window, pane)
     return {
       {
         brief = 'Take screenshot',
         icon = 'cod_device_camera',

         action = act.PromptInputLine {
           description = 'Screenshot name',
           action = wezterm.action_callback(function(window, pane, line)
             if line then
               local text = pane:get_lines_as_escapes()
               local f = io.open(line .. '.txt', 'w+')

               f:write(text)
               f:flush()
               f:close()
             end
           end),
         },
       },
     }
   end)

.. admonition:: Flatpak permissions...

   I have the `Flatpak <https://flathub.org/apps/org.wezfurlong.wezterm>`__ version of  WezTerm installed.

   This led to a bizarre issue where the call to ``io.open()`` kept failing silently by returning ``nil``.
   `Apparently <https://stackoverflow.com/a/75390601>`__, in order to get an actual error message you need to wrap the call in an ``assert()``.

   Eventually, I was able to spot that WezTerm was complaining that the filesystem was read-only.
   Thankfully, the KDE System Settings app allowed me to grant WezTerm write access to my filesystem without too much hassle.

After running the command and giving it a filename I was left with a plain-ish text file that looked something like the following

.. code-block:: none

   \x1b[38:2::255:255:255m\x1b[48:2::49:49:49m|\x1b(B\x1b[0;1m\x1b[38:2::255:255:255m\x1b[40m*gud-test*        x\x1b(B\x1b[0m\x1b['z...

Rendering the Screenshot
------------------------

Now that we have the raw data, there are lots of ways we could approach rendering it, for example you could dump it into `xterm.js <https://github.com/xtermjs/xterm.js>`__.

However, while I have nothing against JavaScript it's always nice not to rely on it unnecessarily.
Since this is a static screenshot anyway it makes sense to render it offline and embed the result in the page.

Using the `rich <https://github.com/textualize/rich>`__ Python library, it only takes a few lines of code to convert the screenshot from plain-ish text to an SVG.

.. code-block:: python

   import io
   import pathlib

   from rich.console import Console
   from rich.text import Text

   content = pathlib.Path('<filepath>').read_text()
   text = Text.from_ansi(content)

   console = Console(
       file=io.StringIO(),
       force_terminal=True,
       record=True,
       width=None,
       height=None,
   )
   console.print(text, end="")
   svg = console.export_svg(title="Example screenshot")

There is one small issue... passing ``None`` for the ``width`` and ``height`` of the ``Console`` object means that it will use the dimensions of the current terminal executing the code rather than the dimensions of the terminal the screenshot was captured from!

Width and Height
^^^^^^^^^^^^^^^^

In order for the captured data to be rendered correctly, rich's ``Console`` object needs to use the same ``width`` and ``height`` as the original terminal.

This means that when we take the screenshot, we also need to capture the dimensions of the terminal pane.
Easy enough with WezTerm's Lua API, but where to store the values?

Rather than try and invent a file format, why not reuse the `asciicast <https://docs.asciinema.org/manual/asciicast/v3/>`__ format from `asciinema <https://asciinema.org/>`__?
After all a screenshot is just a single frame screencast!

We don't need to worry too much about the details of the format, the following snippet should be enough for this use case.

.. code-block:: json

   {"version": 3, "term": {"cols": "<width>", "rows": "<height>"}}
   [0, "o", "<captured_output>"]

Which we can modify our custom WezTerm command to produce.

.. code-block:: lua

   wezterm.on('augment-command-palette', function(window, pane)
     return {
       {
         brief = 'Take screenshot',
         icon = 'cod_device_camera',

         action = act.PromptInputLine {
           description = 'Screenshot name',
           action = wezterm.action_callback(function(window, pane, line)
             if line then
               local dimensions = pane:get_dimensions()
               local body = {0, "o", pane:get_lines_as_escapes()}

               local header = {
                 version = 3,
                 term = {
                   cols = dimensions.cols,
                   rows = dimensions.viewport_rows,
                 },
               }

               local f = io.open(line .. '.cast', 'w+')
               f:write(wezterm.json_encode(header) .. '\n')
               f:write(wezterm.json_encode(body))
               f:flush()
               f:close()
             end
           end),
         },
       },
     }
   end)


And update our Python code accordingly

.. code-block:: python

   fpath = pathlib.Path('<filepath>')
   with fpath.open() as f:
      header = json.loads(f.readline())
      body = json.loads(f.readline())

   text = Text.from_ansi(body[-1])

   console = Console(
       file=io.StringIO(),
       force_terminal=True,
       record=True,
       width=header["term"]["cols"],
       height=header["term"]["rows"],
   )
   console.print(text, end="")
   svg = console.export_svg(title=self.options.get("title", ""))

At this point you'd think it would be job done, but there is one more detail to consider...

.. raw:: html
   :file: ../images/termshot-colorless.svg

My terminal colours are not being preserved!

SGR Codes
^^^^^^^^^

I'm not the right person to try and explain how terminal rendering works.
I only know enough to say that the story is long and built up using many layers of escape codes...

The codes that matter for this tale are something called `SGR codes <https://strasis.com/documentation/limelight-xe/reference/ecma-48-sgr-codes>`__ and they control various formatting properties including colour.
Most documentation I've found will say that to set the text colour to... red for example, you need to use the following escape sequence::

  \x1b[38;2;255;0;0m

However, there are some places that specify an alternative representation::

  \x1b[38:2::255:0:0m

It turns out that WezTerm uses this second style, which ``rich`` does not recognise, resulting in the colourless image you saw above.
To fix this, `I tweaked <https://github.com/Textualize/rich/pull/3789>`__ the way rich parsed escape codes to allow for both styles, resulting in the image you see below.

.. raw:: html
   :file: ../images/termshot-sgr-fix.svg

Which is better, but it still isn't an accurate representation of what I see in my terminal.

Colour Palette
^^^^^^^^^^^^^^

Aside from providing specific RGB values, SGR codes also allow for applications to choose from a palette of 16 colours - 8 "normal" and 8 "bright" colours.

The specific colours in this palette are of course dependent on whatever theme you have configured in your terminal emulator, so the final step is to ensure that ``rich`` uses the same colour palette as my terminal.

Thankfully the asciicast format supports recording this information alongside the width and height, all we need to do is extend the screenshot command in WezTerm to populate it.


.. code-block:: lua

   local dimensions = pane:get_dimensions()
   local theme = wezterm.get_builtin_color_schemes()[window:effective_config().color_scheme]
   local body = {0, "o", pane:get_lines_as_escapes()}

   local header = {
     version = 3,
     term = {
       cols = dimensions.cols,
       rows = dimensions.viewport_rows,
       theme = {
         fg = theme.foreground,
         bg = theme.background,
         palette = table.concat(append_tables(theme.ansi, theme.brights), ':'),
       },
     },
   }

.. details:: Expand to see the complete command implementation

   .. code-block:: lua
      :filename: wezterm/commands/screenshot.lua

      local wezterm = require 'wezterm'
      local io = require 'io'
      local os = require 'os'
      local act = wezterm.action

      local M = {}

      local function append_tables(...)
       local result = {}
       for _, tbl in ipairs({...}) do
           for i = 1, #tbl do
               result[#result + 1] = tbl[i]
           end
       end
       return result
      end

      function M.setup()

        wezterm.on('augment-command-palette', function(window, pane)
          return {
            {
              brief = 'Take screenshot',
              icon = 'cod_device_camera',

              action = act.PromptInputLine {
                description = 'Screenshot name',
                -- initial_value = os.date('%Y%m%dT%H%M%S--terminal-screenshot'), -- apparently this requires a nightly build
                action = wezterm.action_callback(function(window, pane, line)
                  if line then
                    local dimensions = pane:get_dimensions()
                    local theme = wezterm.get_builtin_color_schemes()[window:effective_config().color_scheme]
                    local body = {0, "o", pane:get_lines_as_escapes()}

                    local header = {
                      version = 3,
                      term = {
                        cols = dimensions.cols,
                        rows = dimensions.viewport_rows,
                        theme = {
                          fg = theme.foreground,
                          bg = theme.background,
                          palette = table.concat(append_tables(theme.ansi, theme.brights), ':'),
                        },
                      },
                    }

                    local f = io.open(line .. '.cast', 'w+')
                    f:write(wezterm.json_encode(header) .. '\n')
                    f:write(wezterm.json_encode(body))
                    f:flush()
                    f:close()
                  end
                end),
              },
            },
          }
        end)
      end

      return M

Which of course requires a similar update to the rendering code

.. code-block:: python

   term = header["term"]
   ansi_colors = term["theme"]["palette"].split(":")
   theme = TerminalTheme(
       background=Color.parse(term["theme"]["bg"]).triplet,
       foreground=Color.parse(term["theme"]["fg"]).triplet,
       normal=[Color.parse(col).triplet for col in ansi_colors[:8]],
       bright=[Color.parse(col).triplet for col in ansi_colors[8:]],
   )

   ...

   svg = console.export_svg(
       title=self.options.get("title", ""),
       theme=theme,
   )

Which, finally, results in the SVG you saw at the start of this blog post!

Sphinx Integration
------------------

When working on a post for this site, I want to be able to just include the ``*.cast`` file produced by WezTerm as I would with any other image

.. code-block:: rst

   .. termshot:: /images/example.cast
      :title: Example

and have Sphinx perform the conversion to SVG automatically during the build.
This can be done by creating a custom `directive <https://docutils.sourceforge.io/docs/howto/rst-directives.html>`__.

The following class defintion defines the interface for the directive, we want it accept a single argument (``/images/example.cast``)
and have the option to specify a ``:title:``.

.. literalinclude:: ../extensions/termshot.py
   :start-at: class Termshot
   :end-before: def run
   :language: python

Each directive has a ``run()`` method, which should return a list of nodes which are inserted into the document at the location where the directive was used.

Other Sphinx directives like ``.. figure::`` or ``.. include::`` interpret absolute paths as paths relative to the project root.
I want the ``.. termshot::`` directive to behave in the same way, so I pass the given filepath through the ``self.env.relfn2path`` function which handles that for me

.. literalinclude:: ../extensions/termshot.py
   :dedent:
   :start-at: def run
   :end-before: with
   :language: python

Once the svg has been generated, it needs to be included in the final HTML somehow, there are many way to approach this but for simplicity I've opted to inline the SVG code using a ``raw`` docutils node.

.. literalinclude:: ../extensions/termshot.py
   :dedent:
   :language: python
   :start-at: svg =
   :end-at: return [node

.. details:: Expand to see the complete implementation

   .. literalinclude:: ../extensions/termshot.py
      :language: python
