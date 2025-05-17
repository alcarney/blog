"""denote.py - Add support for denote style file names.

This is used to power the entire site, based on the metadata blog posts are
generated, notes created etc.
"""

from __future__ import annotations

import pathlib
import typing
from datetime import datetime, timezone

from docutils import nodes

from .builder import DenoteHTMLBuilder
from .domain import Denote
from .record import Record

if typing.TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx


UTC = timezone.utc


def discover_records(app: Sphinx, docname: str, content: list[str]):
    """Discover and index records based on their filename"""

    docpath = pathlib.Path(docname)
    if (record := Record.parse(docpath.name)) is None:
        return

    domain: Denote = app.env.domains["denote"]
    domain.add_record(docname, record)


def parse_records(app: Sphinx, doctree):
    """Extract additional information from a document's content"""

    docname = app.env.docname
    domain: Denote = app.env.domains["denote"]
    metadata = app.env.metadata.get(docname, {})

    if (record := domain.records.get(docname)) is None:
        return

    if (title := doctree.next_node(condition=nodes.title, descend=True)) is not None:
        record.title = title.astext()

    if (date := metadata.get("date")) is not None:
        record.timestamp = datetime.fromisoformat(date)

        # Assume UTC if no timezone available
        if record.timestamp.tzinfo is None:
            record.timestamp = record.timestamp.replace(tzinfo=UTC)


def generate_collections(app: Sphinx):
    """Generate collections of records according to some criteria"""

    domain: Denote = app.env.domains["denote"]

    # Emit an all blog posts page
    context = {"collection": list(domain.posts.all()), "title": "Blog"}
    yield ("blog", context, "blog/collection.html")

    context.update(
        {
            "baseurl": app.config.blog_baseurl,
            "title": app.config.blog_title,
            "now": datetime.now(tz=UTC),
            "relurl": "blog/atom.xml",
            "sphinx_version": "8",
        }
    )
    yield ("blog/atom", context, "blog/atom.xml")

    # Emit a page for each year
    by_year = domain.posts.by_year()
    for year, collection in by_year.items():
        context = {"collection": collection, "title": f"Posts in {year}"}
        yield (f"blog/{year}", context, "blog/collection.html")

    # Emit a page for each tag - include both notes and posts on these pages
    by_tag = domain.records.by_tag()
    yield ("tag", {"tags": by_tag}, "blog/tags.html")

    for tag, collection in by_tag.items():
        context = {"collection": collection, "title": f"Tagged with: {tag}"}
        yield (f"tag/{tag}", context, "blog/collection.html")


def update_html_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document,
):
    """Add additional information to the context passed to the Jinja template"""
    domain: Denote = app.env.domains["denote"]
    context["denote"] = domain

    if (record := domain.records.get(pagename)) is not None:
        context["record"] = record


def setup(app: Sphinx):
    app.add_config_value("blog_baseurl", default="", rebuild="env")
    app.add_config_value("blog_title", default="", rebuild="env")

    app.add_builder(DenoteHTMLBuilder, override=True)
    app.add_domain(Denote)

    app.connect("source-read", discover_records)
    app.connect("doctree-read", parse_records)
    app.connect("html-collect-pages", generate_collections)
    app.connect("html-page-context", update_html_context)

    return {"version": "1.0", "parallel_read_safe": True}
