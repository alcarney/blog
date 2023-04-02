"""tailwind.py - An extension to help make using Sphinx and Tailwind together nicer.

Current Features:

- Fixing Tailwind class names that get corrupted by the reStructuredText parser.
  e.g ``lg:m-4`` is parsed as ``lg-m-4``.
"""
from sphinx.application import Sphinx

PREFIXES = {
    "md",
    "lg",
}


def fix_class(class_name):
    """Fixes any Tailwind CSS class that's been corrupted by the rst parser"""

    for prefix in PREFIXES:
        if class_name.startswith(f"{prefix}-"):
            class_name = class_name.replace(f"{prefix}-", f"{prefix}:")

    if class_name.endswith("1-2"):
        class_name = class_name.replace("1-2", "1/2")

    return class_name


def doctree_read_handler(app, doctree):
    """A handler to fix the Tailwind CSS classes that get corrupted by the rst parser."""

    def has_classes(node):
        """Filter function that determines if a node is carrying css classes"""
        if not hasattr(node, "attributes"):
            return False

        if not "classes" in node.attributes:
            return False

        return len(node["classes"]) > 0

    for element in doctree.traverse(condition=has_classes):
        element["classes"] = [fix_class(clsname) for clsname in element["classes"]]


def setup(app: Sphinx):
    app.connect("doctree-read", doctree_read_handler)

    return {"version": "1.0", "parallel_read_safe": True}
