from __future__ import annotations

import collections
import functools
import typing

from docutils import nodes
from sphinx.domains import Domain, Index, IndexEntry, ObjType
from sphinx.roles import XRefRole
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_refnode

if typing.TYPE_CHECKING:
    from docutils.nodes import Element
    from sphinx.addnodes import pending_xref
    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment

    IndexedContent = tuple[list[tuple[str, list[IndexEntry]]], bool]

from .record import Record, Sequence

logger = getLogger("denote")


class RecordCollection(collections.UserDict[str, Record]):
    """A dictionary of records that also maintains a number of groupings"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._by_tag = {}
        self._by_year = {}
        self._by_identifier: dict[str, str] = {}
        self._by_sequence: Sequence = Sequence()

    def __setitem__(self, key: str, item: Record) -> None:
        super().__setitem__(key, item)

        if item.identifier in self._by_identifier:
            return

        self._by_identifier[item.identifier] = key

        year = item.timestamp.year
        self._by_year.setdefault(year, []).append(key)

        for tag in item.tags:
            self._by_tag.setdefault(tag, []).append(key)

        if (sequence := item.sequence) is not None:
            node = self._by_sequence

            for idx in sequence:
                if idx not in node.children:
                    node.children[idx] = Sequence()

                node = node.children[idx]

            node.identifier = item.identifier

    def find(self, *, identifier: str | None = None) -> Record | None:
        """Find records by various criteria."""

        if identifier is not None:
            return self.get(self._by_identifier.get(identifier))

    def all(self):
        items = [self[k] for k in self.keys()]
        return self._date_sort(items)

    def by_tag(self) -> dict[int, list[Record]]:
        """Return all records, grouped by tag"""
        records: dict[int, list[Record]] = {}

        for tag, keys in self._by_tag.items():
            # Some keys may have been deleted, only consider those that are still present.
            items = [record for k in keys if (record := self.get(k)) is not None]
            records[tag] = self._date_sort(items)

        return records

    def by_year(self) -> dict[int, list[Record]]:
        """Return all records, grouped by year"""
        records: dict[int, list[Record]] = {}

        for year, keys in self._by_year.items():
            # Some keys may have been deleted, only consider those that are still present.
            items = [record for k in keys if (record := self.get(k)) is not None]
            records[year] = self._date_sort(items)

        return records

    def sequence_hierarchy(self, key: tuple[int, ...]) -> Sequence:
        """Return the hierarchy of all posts in a sequence"""
        return self._by_sequence.children[key[0]]

    def _date_sort(self, items: list[Record]) -> list[Record]:
        """Ensure all records are sorted by post date."""
        # Use the timestamp field, as some posts may use the :date: field to override
        # the original timestamp in the identifier
        return sorted(items, key=lambda r: r.timestamp, reverse=True)


class AllTagsIndex(Index):
    """Index tag names."""

    name = "tag"
    localname = "Tags"

    def generate(self, docnames=None) -> IndexedContent:
        items: dict[str, IndexEntry] = {}
        for tag_name, records in self.domain.records.by_tag().items():
            key = tag_name[0].upper()
            items.setdefault(key, []).append(
                IndexEntry(
                    tag_name,
                    0,
                    f"tag/{tag_name}",
                    "",
                    f"{len(records)}",
                    "",
                    "",
                )
            )
        return sorted(items.items()), True


class AllNotesIndex(Index):
    """Index all notes."""

    name = "notes"
    localname = "Notes"

    def generate(self, docnames=None) -> IndexedContent:
        items: dict[str, IndexEntry] = {}
        for record in self.domain.records.all():
            if record.is_blogpost:
                continue

            key = record.title[0].upper()
            items.setdefault(key, []).append(
                IndexEntry(
                    record.title,
                    0,
                    record.docname,
                    "",
                    "",
                    "",
                    "",
                )
            )
        return sorted(items.items()), True


class TagIndex(Index):
    """Index records by tag name."""

    def __init__(self, domain, *, tag_name: str):
        super().__init__(domain)
        self.tag_name = tag_name

    def generate(self, docnames=None) -> IndexedContent:
        items: dict[str, IndexEntry] = {}
        for record in self.domain.records.all():
            if self.tag_name not in record.tags:
                continue

            key = record.title[0].upper()
            items.setdefault(key, []).append(
                IndexEntry(
                    record.title,
                    0,
                    record.docname,
                    "",
                    "",
                    "",
                    "",
                )
            )
        return sorted(items.items()), True

    @classmethod
    def for_(cls, tag_name: str):
        """Sphinx requires indcies to be class objects, so this function makes a
        subclass for the given tag name.
        """

        return type(
            f"{tag_name.capitalize()}TagIndex",
            (cls,),
            {
                "__init__": functools.partial(cls.__init__, tag_name=tag_name),
                "name": f"tag-{tag_name}",
                "localname": f"#{tag_name}",
            },
        )


class ArchiveIndex(Index):
    """Index posts by published date."""

    def __init__(self, domain, *, year: int):
        super().__init__(domain)
        self.year = year

    def generate(self, docnames=None) -> IndexedContent:
        items: dict[str, IndexEntry] = {}
        for record in self.domain.posts.all():
            if self.year != record.timestamp.year:
                continue

            key = f"{record.timestamp:%m}-{record.timestamp:%b}"
            items.setdefault(key, []).append(
                IndexEntry(
                    record.title,
                    0,
                    record.docname,
                    "",
                    "",
                    "",
                    "",
                )
            )
        return sorted(items.items()), True

    @classmethod
    def for_(cls, year: int):
        """Sphinx requires indcies to be class objects, so this function makes a
        subclass for the given year.
        """

        return type(
            f"Archive{year}Index",
            (cls,),
            {
                "__init__": functools.partial(cls.__init__, year=year),
                "name": f"blog-{year}",
                "localname": f"Posted in: {year}",
                "shortname": f"#{year}",
            },
        )


class Denote(Domain):
    """A domain for denote style note taking."""

    name = "denote"
    label = "Denote"

    # Don't list dynamic indices here, instead populate them once we've discovered all
    # records
    indices = [
        AllNotesIndex,
        AllTagsIndex,
    ]

    object_types: dict[str, ObjType] = {
        "note": ObjType("note", "note"),
    }

    roles = {
        "link": XRefRole(),
    }

    @property
    def posts(self) -> RecordCollection:
        return self.data.setdefault("posts", RecordCollection())

    @property
    def records(self) -> RecordCollection:
        return self.data.setdefault("records", RecordCollection())

    def add_record(self, docname: str, record: Record):
        """Add a record to the domain"""
        logger.debug("[denote]: Found record: %r", record)
        record.docname = docname

        # Silence the 'not included in toctree' warnings
        # Is this the right way to do that?
        self.env.metadata[docname]["orphan"] = True
        self.records[docname] = record

        if record.is_blogpost:
            self.posts[docname] = record

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

        if target.startswith("__"):
            return self._resolve_tag(fromdocname, builder, target, contnode)

        return self._resolve_record(fromdocname, builder, target, contnode)

    def _resolve_record(
        self,
        fromdocname: str,
        builder: Builder,
        target: str,
        contnode: Element,
    ):
        """Resolve a reference to a specific record."""
        if (record := self.records.find(identifier=target)) is None:
            return None

        if record.docname is None:
            return None

        if (linktext := contnode.astext()) == target:
            contnode = nodes.Text(record.title)
        else:
            contnode = nodes.Text(linktext)

        return make_refnode(
            builder, fromdocname, record.docname, None, [contnode], record.title
        )

    def _resolve_tag(
        self,
        fromdocname: str,
        builder: Builder,
        target: str,
        contnode: Element,
    ):
        """Resolve a reference to a specific tag."""

        todocname = f"tag/{target[2:]}"

        if (linktext := contnode.astext()) == target:
            contnode = nodes.Text(f"#{target[2:]}")
        else:
            contnode = nodes.Text(linktext)

        return make_refnode(
            builder, fromdocname, todocname, None, [contnode], f"#{target[2:]}"
        )
