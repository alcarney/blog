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


class BibDirective(ObjectDescription[str]):
    """Base directive for bibliographic items."""

    has_content = True

    required_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        **ObjectDescription.option_spec,
        "state": directives.unchanged,
        "cover": directives.unchanged,
        "no-cover": directives.flag,
        "link": directives.uri,
    }

    DEFAULT_COVER = "book.svg"

    @typing.override
    def handle_signature(self, sig: str, signode: addnodes.desc_signature) -> str:
        """Write out the nodes that provide the metadata about the entry."""

        # Add a cover image.
        if not self.options.pop("no-cover", False):
            container = nodes.container(classes=["bib-image"])
            signode.parent.children.insert(0, container)

            cover = self.options.pop("cover", self.DEFAULT_COVER)
            container += nodes.image(uri=f"/images/bib/{cover}")

        # Add the state and title
        state = self.options.pop("state", "")
        signode += addnodes.desc_addname(text=state, classes=["bib-state"])

        signode += addnodes.desc_sig_space()
        signode += addnodes.desc_name(text=sig)

        # Add all remaining bibliographic fields
        for key in self.options:
            if key in ObjectDescription.option_spec:
                continue

            field_name = " ".join(k.capitalize() for k in key.split("-"))
            field_value = self.options[key]
            field_type = self.option_spec[key]

            if field_type == directives.uri:
                signode += nodes.reference(text=field_name, refuri=field_value)
                signode += addnodes.desc_sig_space()
                signode += addnodes.desc_addname(text="", classes=["bib-value"])

            else:
                signode += addnodes.desc_addname(text=field_name, classes=["bib-field"])
                signode += addnodes.desc_sig_space()
                signode += addnodes.desc_addname(
                    text=field_value, classes=["bib-value"]
                )

        return sig

    @typing.override
    def add_target_and_index(
        self, name: str, sig: str, signode: addnodes.desc_signature
    ) -> None:
        return super().add_target_and_index(name, sig, signode)


@typing.final
class BookDirective(BibDirective):
    """Describe a book"""

    option_spec = {
        **BibDirective.option_spec,
        "author": directives.unchanged,
        "authors": directives.unchanged,
        "published": directives.unchanged,
        "isbn": directives.unchanged,
        "read-online": directives.uri,
    }


@typing.final
@typing.final
class YoutubeDirective(BibDirective):
    """Describe a YouTube video."""

    option_spec = {
        **BibDirective.option_spec,
        "video-id": directives.unchanged,
    }

    def handle_signature(self, sig: str, signode: addnodes.desc_signature) -> str:
        # Disable the default cover image
        self.options["no-cover"] = True

        # And embed the video instead.
        if (video_id := self.options.pop("video-id", None)) is not None:
            container = nodes.container(classes=["bib-video"])
            _ = signode.parent.children.insert(0, container)

            iframe = f"""<iframe width="100%" height="100%" frameborder="0"
                                 src="https://www.youtube.com/embed/{video_id}"
                                 title="YouTube video player"
                                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin"
                                 allowfullscreen></iframe>
            """
            container += nodes.raw("", iframe, format="html")

        return super().handle_signature(sig, signode)


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
        "youtube": YoutubeDirective,
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
