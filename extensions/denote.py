"""denote.py - Add support for denote style file names.

This is used to power the entire site, based on the metadata blog posts are
generated, notes created etc.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
import typing
from datetime import datetime

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.dirhtml import DirectoryHTMLBuilder
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_refnode

if typing.TYPE_CHECKING:
    from docutils.nodes import Element
    from sphinx.addnodes import pending_xref
    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment

logger = getLogger('denote')
FILENAME_PATTERN = re.compile(r"(?P<identifier>\d{8}T\d{6})--(?P<title>[^_]+)__(?P<tags>[^.]+)", re.VERBOSE)

@dataclasses.dataclass
class Record:
    """Represents a 'record' with a denote style filename."""

    identifier: str
    slug: str

    timestamp: datetime
    title: str
    tags: list[str]

    @classmethod
    def parse(cls, filename: str) -> Record | None:
        """Parse an instance of a record from the given filename"""

        if (match := FILENAME_PATTERN.match(filename)) is None:
            return None

        identifier = match.group("identifier")
        date, time = identifier.split("T")
        dt = datetime(
            year=int(date[:4]),
            month=int(date[4:6]),
            day=int(date[6:8]),
            hour=int(time[:2]),
            minute=int(time[2:4]),
            second=int(time[4:6]),
        )

        slug = match.group("title")
        tags = match.group("tags").split("_")
        title = " ".join( c.title() for c in slug.split('-'))

        return cls(
            identifier=identifier,
            slug=slug,
            timestamp=dt,
            title=title,
            tags=tags,
        )

    @property
    def url(self):
        """Return the url for this record"""

        if "blog" in self.tags:
            dirname = pathlib.Path("blog", str(self.timestamp.year))
            url = str(dirname / self.slug)
        else:
            dirname = pathlib.Path("notes")
            url = str(dirname / self.identifier)

        return url


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
        domain: Denote = self.env.domains["denote"]

        if (record := domain.notes.get(docname)) is None:
            return super().get_target_uri(docname, typ)

        result = super().get_target_uri(record.url, typ)
        return result

    def get_outfilename(self, pagename: str) -> str:
        domain: Denote = self.env.domains["denote"]

        if (record := domain.notes.get(pagename)) is None:
            return super().get_outfilename(pagename)

        result = super().get_outfilename(record.url)
        return result


def discover_notes(app: Sphinx, docname: str, content: list[str]):
    """Automatically discover and index notes as they are read"""

    docpath = pathlib.Path(docname)
    if (record := Record.parse(docpath.name)) is None:
        return

    domain: Denote = app.env.domains["denote"]

    logger.info("[denote]: Found record: %r", record)
    domain.notes[docname] = record


def setup(app: Sphinx):
    app.add_builder(DenoteHTMLBuilder, override=True)
    app.add_domain(Denote)

    app.connect("source-read", discover_notes)

    return {"version": "1.0", "parallel_read_safe": True}
