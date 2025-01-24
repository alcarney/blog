from __future__ import annotations

import typing

from sphinx.builders.dirhtml import DirectoryHTMLBuilder
from sphinx.util.logging import getLogger

if typing.TYPE_CHECKING:
    from .domain import Denote


logger = getLogger("denote")


class DenoteHTMLBuilder(DirectoryHTMLBuilder):
    """Translates documents with denote style filenames into something less crazy for
    the web"""

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        domain: Denote = self.env.domains["denote"]

        if (record := domain.records.get(docname)) is None:
            return super().get_target_uri(docname, typ)

        result = super().get_target_uri(record.url, typ)
        return result

    def get_outfilename(self, pagename: str) -> str:
        domain: Denote = self.env.domains["denote"]

        # Special case for the rss feed
        if pagename == "blog/atom":
            outpath = super().get_outfilename(pagename)
            return outpath.replace("/index.html", ".xml")

        if (record := domain.records.get(pagename)) is None:
            return super().get_outfilename(pagename)

        result = super().get_outfilename(record.url)
        return result
