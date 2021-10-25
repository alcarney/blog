"""coderepo.py - A Sphinx extension for generating a GitHub like UI for folders
of code."""
import pathlib
from typing import Dict

import jinja2 as j2

from docutils import nodes
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

logger = getLogger("coderepo")


def load_project(
    *,
    env: BuildEnvironment,
    items: Dict[str, Dict],
    prefix: str,
    parent: pathlib.Path,
    depth: int = 0,
):
    """Recursively descend into a project and gather all the info we need to render
    it.

    Parameters
    ----------
    env:
        The build environment
    items:
        The dictionary that contains all the items discovered so far
    parent:
        The parent directory to process
    prefix:
        The portion of the filepath to remove
    depth:
        The current depth in the hierarchy
    """

    for item in parent.glob("*"):

        logger.debug("[coderepo]: %s - %s", item, item.suffix)
        if item.suffix in {".png"}:
            # Skip images for now.
            continue

        if item.name in {"node_modules", "dist"}:
            logger.debug("[coderepo]: Skipping %s", item)
            continue

        key = str(item).replace(prefix, "")
        items[key] = {
            "depth": depth,
            "name": item.name,
            "parent": str(parent).replace(prefix, "") if depth > 0 else "",
            "type": "folder" if item.is_dir() else "file",
        }

        if item.is_file():
            env.note_dependency(str(item))

            with item.open() as f:
                code = f.read()

            try:
                lexer = guess_lexer_for_filename(item.name, code)
                formatter = HtmlFormatter(prestyles="margin: 0")
                items[key]["content"] = highlight(code, lexer, formatter)
            except Exception:
                items[key]["content"] = f'<pre class="m-0">{code}</pre>'

        if item.is_dir():
            load_project(
                env=env, items=items, prefix=prefix, parent=item, depth=depth + 1
            )


class CodeProject(SphinxDirective):
    """Generate a file hierarchy representing a code project."""

    required_arguments = 1

    def run(self):
        _, path = self.env.relfn2path(self.arguments[0])
        project_dir = pathlib.Path(path)

        project = {}
        load_project(
            env=self.env, items=project, prefix=f"{project_dir}/", parent=project_dir
        )
        context = {"project": project}

        templates_dir = pathlib.Path(__file__).parent / "templates"
        env = j2.Environment(loader=j2.FileSystemLoader(templates_dir))
        template = env.get_template("repo.html")
        self.env

        viewer = nodes.raw(
            "",
            template.render(context),
            format="html",
        )
        result = [viewer]

        readme = project_dir / "README.rst"
        if readme.exists():
            self.env.note_dependency(str(readme))
            self.env.note_included(str(readme))

            with readme.open() as f:
                content = ["README", "======", *f.read().splitlines()]
                self.state_machine.insert_input(content, str(readme))

        return result


def setup(app: Sphinx):

    app.add_directive("code-project", CodeProject)

    return {"version": "1.0", "parallel_read_safe": True}
