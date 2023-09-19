# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.append(os.path.abspath("extensions"))


from docutils.parsers.rst import nodes
from sphinx.application import Sphinx

# -- Project information -----------------------------------------------------

project = "Blog"
copyright = "2023, Alex Carney"
author = "Alex Carney"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "ablog",
    "coderepo",  # see: ./extensions.coderepo.py
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "tailwind",  # see: ./extensions/tailwind.py
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".env", "talks"]

# -- Options for ABlog extension ---------------------------------------------
blog_baseurl = "https://www.alcarney.me"
blog_feed_fulltext = True
blog_title = "Alex Carney | Blog"
post_date_format = "%b %d, %Y"

# -- Options for InterSphinx extension ---------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "py35": ("https://docs.python.org/3.5/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# -- Options for HTML output -------------------------------------------------
html_sidebars = {
    "blog": ["archives.html"],
    "blog/20*": ["archives.html"],
    "blog/tag/*": [],
    "blog/20*/*": ["postcard.html", "localtoc.html"],
    "code": [],
    "code/*": ["localtoc.html"],
    "index": [],
    "notes": [],
    "notes/*": ["localtoc.html"],
    "search": [],
}

html_favicon = "_static/favicon.ico"
html_static_path = ["_static"]
html_theme = "mytheme"
html_theme_path = ["theme"]
html_title = "Alex Carney"


def pypi_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """An easy way to link to projects on pypi."""

    ref = f"https://pypi.org/project/{text}"

    node = nodes.reference(rawtext, text, refuri=ref, **options)
    return [node], []


def template_override(app, pagename, templatename, context, doctree):
    """Allows for page templates to be overridden based on a ``:template: xxx``
    field in a document.

    .. important::

       The ``:template`` field *must* be included before the document title to be
       detected.
    """

    if not context:
        return

    meta = context.get("meta", None)
    if not meta:
        return

    return meta.get("template", None)


def setup(app: Sphinx):
    app.add_css_file("css/styles.css", priority=800)
    app.add_role("pypi", pypi_role)

    app.connect("html-page-context", template_override)
