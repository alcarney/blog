from __future__ import annotations

import io
import json
import pathlib
import typing
from os.path import abspath, relpath

from docutils import nodes
from docutils.parsers.rst import directives
from rich.color import Color
from rich.console import Console
from rich.terminal_theme import TerminalTheme
from rich.text import Text
from sphinx.util.docutils import SphinxDirective

if typing.TYPE_CHECKING:
    from sphinx.application import Sphinx


class Termshot(SphinxDirective):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec = {
        "title": directives.unchanged,
    }

    def run(self):
        _, fpath = self.env.relfn2path(self.arguments[0])
        with pathlib.Path(fpath).open() as f:
            header = json.loads(f.readline())
            body = json.loads(f.readline())

        term = header["term"]
        ansi_colors = term["theme"]["palette"].split(":")

        text = Text.from_ansi(body[-1])
        theme = TerminalTheme(
            background=Color.parse(term["theme"]["bg"]).triplet,
            foreground=Color.parse(term["theme"]["fg"]).triplet,
            normal=[Color.parse(col).triplet for col in ansi_colors[:8]],
            bright=[Color.parse(col).triplet for col in ansi_colors[8:]],
        )

        console = Console(
            file=io.StringIO(),
            force_terminal=True,
            record=True,
            width=term["cols"],
            height=term["rows"],
        )
        console.print(text, end="")
        svg = console.export_svg(
            title=self.options.get("title", ""),
            theme=theme,
        )

        node = nodes.raw("", svg, format="html")
        return [node]


def setup(app: Sphinx):
    app.add_directive("termshot", Termshot)
    return {"version": "1.0", "parallel_read_safe": True}
