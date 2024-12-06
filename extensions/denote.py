"""denote.py - Add support for denote style file names for my notes.
"""
from __future__ import annotations

import pathlib

from sphinx.application import Sphinx
from sphinx.builders.dirhtml import DirectoryHTMLBuilder


def parse_denote_name(name: str):
    date, rest = name.split('--')
    title, tags = rest.split('__')

    return date, title, tags


class DenoteHTMLBuilder(DirectoryHTMLBuilder):
    """Translates documents with denote style filenames into something less crazy for
    the web"""

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        if "--" not in docname:
            return super().get_target_uri(docname, typ)

        docpath = pathlib.Path(docname)
        date, title, tabs = parse_denote_name(docpath.stem)

        old = super().get_target_uri(docname, typ)
        result = super().get_target_uri(str(docpath.parent / date), typ)
        print(f"uri: {docname} -> {result}")
        return result

    def get_outfilename(self, pagename: str) -> str:
        if "--" not in pagename:
            return super().get_outfilename(pagename)

        pagepath = pathlib.Path(pagename)
        date, title, tabs = parse_denote_name(pagepath.stem)

        old = super().get_target_uri(pagename)
        result = super().get_outfilename(str(pagepath.parent / date))
        print(f"page: {pagename} -> {result}")
        return result


def setup(app: Sphinx):
    app.add_builder(DenoteHTMLBuilder, override=True)

    return {"version": "1.0", "parallel_read_safe": True}
