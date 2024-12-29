"""denote.py - Add support for denote style file names for my notes."""

from __future__ import annotations

import pathlib
import typing

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.dirhtml import DirectoryHTMLBuilder
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode

if typing.TYPE_CHECKING:
    from docutils.nodes import Element
    from sphinx.addnodes import pending_xref
    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment


def parse_denote_name(name: str) -> tuple[str, str, str] | None:
    """Given a docname, parse the relevant denote file name components, if possible."""
    docpath = pathlib.Path(name)

    if "--" not in (docname := docpath.stem):
        return None

    date, rest = docname.split("--")
    title, tags = rest.split("__")

    return date, title, tags


class Denote(Domain):
    """A domain for denote style note taking."""

    name = "denote"
    label = "Denote"

    object_types: dict[str, ObjType] = {
        "note": ObjType("note", "note"),
    }

    roles = {
        "note": XRefRole(),
    }

    @property
    def notes(self) -> dict[str, tuple[str, str, str]]:
        return self.data.setdefault("notes", {})

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: Element,
    ) -> Element | None:
        """Resolve cross references"""

        print(self.notes)
        print(f"resolve: {fromdocname=} {typ=} {target=} {node=} {contnode=}")

        if (dest := self.notes.get(target)) is None:
            return None

        docname, title, tags = dest
        ref_title = title.replace("-", " ").title()

        if contnode.astext() == target:
            contnode = nodes.Text(ref_title)

        return make_refnode(builder, fromdocname, docname, None, [contnode], ref_title)


class DenoteHTMLBuilder(DirectoryHTMLBuilder):
    """Translates documents with denote style filenames into something less crazy for
    the web"""

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        if (result := parse_denote_name(docname)) is None:
            return super().get_target_uri(docname, typ)

        date, title, tags = result

        dirname = pathlib.Path(docname).parent
        result = super().get_target_uri(str(dirname / date), typ)
        return result

    def get_outfilename(self, pagename: str) -> str:
        if (result := parse_denote_name(pagename)) is None:
            return super().get_outfilename(pagename)

        date, title, tags = result

        dirname = pathlib.Path(pagename).parent
        result = super().get_outfilename(str(dirname / date))
        return result


def discover_notes(app: Sphinx, docname: str, content: list[str]):
    """Automatically discover and index notes as they are read"""

    if (result := parse_denote_name(docname)) is None:
        return

    date, title, tags = result
    domain: Denote = app.env.domains["denote"]

    domain.notes[date] = note = (docname, title, tags)
    print(f"found: {note}")


def setup(app: Sphinx):
    app.add_builder(DenoteHTMLBuilder, override=True)
    app.add_domain(Denote)

    app.connect("source-read", discover_notes)

    return {"version": "1.0", "parallel_read_safe": True}
