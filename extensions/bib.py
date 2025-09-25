from __future__ import annotations

import functools
import typing

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

if typing.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.builders import Builder
    from sphinx.directives import ObjDescT
    from sphinx.environment import BuildEnvironment


@typing.final
class BookDirective(ObjectDescription[str]):
    """Describe a book"""

    has_content = True

    required_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        **ObjectDescription.option_spec,
        "author": directives.unchanged,
        "published": directives.unchanged,
        "isbn": directives.unchanged,
        "cover": directives.unchanged,
        "state": functools.partial(
            directives.choice,
            values=("read", "reading", "to-read", "dnf"),
        ),
    }

    @typing.override
    def handle_signature(self, sig: str, signode: addnodes.desc_signature) -> str:
        """Write out the nodes that provide the metadata about the book."""
        signode += addnodes.desc_name(text=sig)

        if (state := self.options.get("state")) is not None:
            signode += addnodes.desc_type(text="State")
            signode += addnodes.desc_sig_space()
            signode += addnodes.desc_annotation(text=state)

        if (author := self.options.get("author")) is not None:
            signode += addnodes.desc_type(text="Author")
            signode += addnodes.desc_sig_space()
            signode += addnodes.desc_addname(text=author)

        if (published := self.options.get("published")) is not None:
            signode += addnodes.desc_type(text="Published")
            signode += addnodes.desc_sig_space()
            signode += addnodes.desc_addname(text=published)

        if (isbn := self.options.get("isbn")) is not None:
            signode += addnodes.desc_type(text="ISBN")
            signode += addnodes.desc_sig_space()
            signode += addnodes.desc_addname(text=isbn)

        return sig

    @typing.override
    def transform_content(self, content_node: addnodes.desc_content) -> None:
        """Used to add the book's cover image"""

        container = nodes.container()
        container["classes"] = ["cover-image"]
        content_node += container

        if (cover_image := self.options.get("cover")) is None:
            cover_image = "/images/covers/generic.svg"

        container += nodes.image(uri=cover_image, width="100%", height="100%")

    @typing.override
    def add_target_and_index(
        self, name: str, sig: str, signode: addnodes.desc_signature
    ) -> None:
        return super().add_target_and_index(name, sig, signode)


@typing.final
class BibDomain(Domain):
    """A domain for building an managing a biblography"""

    name = "bib"
    label = "Bibliography"

    object_types: dict[str, ObjType] = {
        "book": ObjType("book", "book"),
    }

    roles = {
        "book": XRefRole(),
    }

    directives = {
        "book": BookDirective,
    }

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: addnodes.pending_xref,
        contnode: nodes.Element,
    ) -> nodes.Element | None:
        """Resolve cross references"""

        # if (record := self.records.find(identifier=target)) is None:
        #     return None

        # if record.docname is None:
        #     return None

        # if (linktext := contnode.astext()) == target:
        #     contnode = nodes.Text(record.title)
        # else:
        #     contnode = nodes.Text(linktext)

        # return make_refnode(
        #     builder, fromdocname, record.docname, None, [contnode], record.title
        # )

        return None


def setup(app: Sphinx):
    app.add_domain(BibDomain)
    return {"version": "1.0", "parallel_read_safe": True}
