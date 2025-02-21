from __future__ import annotations

import pathlib
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

    def get_output_path(self, page_name: str) -> pathlib.Path:
        domain: Denote = self.env.domains["denote"]

        # Special case for the rss feed
        if page_name == "blog/atom":
            outpath = super().get_output_path(page_name)
            xml = str(outpath).replace("/index.html", ".xml")
            return pathlib.Path(xml)

        if (record := domain.records.get(page_name)) is None:
            return super().get_output_path(page_name)

        result = super().get_output_path(record.url)
        return result
