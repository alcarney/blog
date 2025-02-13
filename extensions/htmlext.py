from __future__ import annotations

import typing

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

if typing.TYPE_CHECKING:
    from sphinx.application import Sphinx


class details(nodes.Element): ...


def visit_details(self, node: details):
    self.body.append("<details>")

    if (summary := node.attributes.get("summary")) is not None:
        self.body.append("<summary>")
        self.body.append(summary)
        self.body.append("</summary>")


def depart_details(self, node: details):
    self.body.append("</details>")


class Details(SphinxDirective):
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    has_content = True

    def run(self):
        kwargs = {}

        if len(self.arguments) > 0:
            kwargs["summary"] = self.arguments[0]

        node = details("", **kwargs)
        node += self.parse_content_to_nodes()

        return [node]


def setup(app: Sphinx):
    app.add_directive("details", Details)

    app.add_node(details, html=(visit_details, depart_details))
    return {"version": "1.0", "parallel_read_safe": True}
