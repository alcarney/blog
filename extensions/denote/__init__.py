"""denote.py - Add support for denote style file names.

This is used to power the entire site, based on the metadata blog posts are
generated, notes created etc.
"""

from __future__ import annotations

import functools
import json
import pathlib
import typing
from datetime import datetime, timezone

from docutils import nodes
from sphinx import addnodes
from sphinx.util.osutil import relative_uri

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


def find_summary(node: nodes.Node) -> bool:
    if not isinstance(node, nodes.Element):
        return False

    return "post-teaser" in node.attributes.get("classes", [])


def render_summary(app: Sphinx, record: Record, relative_to: str) -> str:
    """Render a summary of the content in the given record"""

    if record.docname is None:
        return ""

    doctree = app.env.get_doctree(record.docname)
    if (summary := doctree.next_node(condition=find_summary)) is None:
        return ""

    # Don't modify the original document
    summary = summary.deepcopy()

    # Make references relative to the parent document
    for ref in summary.findall(addnodes.pending_xref):
        ref["refdoc"] = relative_to

    app.env.resolve_references(summary, relative_to, app.builder)

    # We also need to fix the base image url
    original_imgpath = app.builder.imgpath
    app.builder.imgpath = relative_uri(
        app.builder.get_target_uri(relative_to), "_images"
    )

    html = app.builder.render_partial(summary)

    app.builder.imgpath = original_imgpath
    return html["body"]


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


def make_collection_context(
    collection: list[Record], title: str, app: Sphinx
) -> dict[str, Any]:
    """Make the context necessary to pass to the ``blog/collection.html`` template."""

    return {
        "collection": collection,
        "title": title,
        "render_summary": functools.partial(render_summary, app),
    }


def generate_collections(app: Sphinx):
    """Generate collections of records according to some criteria"""

    domain: Denote = app.env.domains["denote"]

    # Emit an all blog posts page
    context: dict[str, Any] = make_collection_context(
        list(domain.posts.all()), "Blog Posts", app
    )
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
        context = make_collection_context(collection, f"Posts in {year}", app)
        yield (f"blog/{year}", context, "blog/collection.html")

    # Emit a page for each tag - include both notes and posts on these pages
    by_tag = domain.records.by_tag()
    yield ("tag", {"tags": by_tag}, "blog/tags.html")

    nodes = []
    links = []
    all_records = set()
    for tag, collection in by_tag.items():
        nodes.append({"id": tag, "kind": "tag"})

        for r in collection:
            links.append({"source": r.identifier, "target": tag})
            all_records.add(r.identifier)

        context = make_collection_context(collection, f"Tagged with: {tag}", app)
        yield (f"tag/{tag}", context, "blog/collection.html")

    # Placeholder graph view
    nodes.extend({"id": r, "kind": "record"} for r in all_records)
    context = {"nodes": json.dumps(nodes), "links": json.dumps(links)}

    yield ("notes", context, "blog/graph.html")


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
