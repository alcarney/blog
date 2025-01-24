from __future__ import annotations

import dataclasses
import pathlib
import re
from datetime import datetime, timezone

UTC = timezone.utc
FILENAME_PATTERN = re.compile(
    r"(?P<identifier>\d{8}T\d{6})--(?P<title>[^_]+)__(?P<tags>[^.]+)", re.VERBOSE
)


@dataclasses.dataclass
class Record:
    """Represents a 'record' with a denote-style filename."""

    identifier: str
    """The identifier part of the denote-style filename"""

    slug: str
    """The title part of the denote-style filename"""

    tags: list[str]
    """The list of tags from the denote-style filename"""

    timestamp: datetime
    """The record's identifier, parsed as a datetime"""

    title: str
    """The 'pretty' version of the record's title."""

    is_blogpost: bool = dataclasses.field(default=False)
    """Indicates if this record represents a blog post."""

    docname: str | None = dataclasses.field(default=None)
    """The Sphinx docname this record is associated with (if known)"""

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
            tzinfo=UTC,
        )

        slug = match.group("title")
        tags = match.group("tags").split("_")
        title = " ".join(c.title() for c in slug.split("-"))

        try:
            tags.remove("blog")
            is_blogpost = True
        except ValueError:
            is_blogpost = False

        return cls(
            identifier=identifier,
            slug=slug,
            timestamp=dt,
            title=title,
            tags=tags,
            is_blogpost=is_blogpost,
        )

    @property
    def url(self):
        """Return the url for this record"""

        if self.is_blogpost:
            dirname = pathlib.Path("blog", str(self.timestamp.year))
            url = str(dirname / self.slug)
        else:
            dirname = pathlib.Path("notes")
            url = str(dirname / self.identifier)

        return url
