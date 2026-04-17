:title: Generating post summaries
:date: 2025-08-30
:tags: blogging, sphinx
:identifier: 20250830T203717
:signature: 1=2

Generating Post Summaries
=========================

My :ref:`original <blog-generating-feeds-archives>` method for generating index pages only has access to the post's metadata so it is unable to insert any content.
I was able to work around this somewhat by using HTMX to load in a subset of the full page, but this is less than ideal for a number of reasons

- It requires JavaScript to work
- The contents of the page jumps around as you scroll
- The links in the post summaries don't actually work!

This is also the reason why at the time of writing, my RSS feed only contains post titles.

First attempt
-------------

Write a helper function for converting the summary into HTML

.. code-block:: python

   def render_summary(app: Sphinx, record: Record) -> str:
       """Render a summary of the content in the given record"""

       if record.docname is None:
           return ""

       doctree = app.env.get_and_resolve_doctree(record.docname, app.builder)
       if (summary := doctree.next_node(condition=find_summary)) is None:
           return ""

       html = app.builder.render_partial(summary)
       return html["body"]


Add the helper to the template context

.. code-block:: python

   # Emit an all blog posts page
   context: dict[str, Any] = {
       "collection": list(domain.posts.all()),
       "title": "Blog",
       "render_summary": functools.partial(render_summary, app),
   }
   yield ("blog", context, "blog/collection.html")


And call it from the template

.. code-block:: html+jinja

   <div style="min-width: 0">
     {{ render_summary(post) }}
   </div>

This get's us pretty close!
But it's not perfect, following any link generated from a cross-reference results in a 404.

Fixing Cross References
-----------------------

Unfortunately, while the ``get_and_resolve_doctree`` method is very useful, it's doing too much work and making assumptions that do not hold for this use case.

Specifically, it's resolving the cross-references relative to the post's page, rather than the index page we're trying to include summary within.
Taking heavy inspiration from `ablog <https://github.com/sunpy/ablog/blob/0a3aa0386d9005ad6fbea779aa3b1080c4178453/src/ablog/blog.py#L391>`__ (again! 😅), it was relatively straightforward to adjust

.. code-block:: python

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
       html = app.builder.render_partial(summary)
       return html["body"]

Requiring us to also pass through the ``pagename`` variable through to the function

.. code-block:: html+jinja

   <div style="min-width: 0">
     {{ render_summary(post, relative_to=pagename) }}
   </div>

Images
------

A similar issue was that image urls were also incorrect.

This took a little while to figure out as the way images are handled in Sphinx involve a few moving parts, but ultimately involved ensuring that the images were resolved relative to the correct document

.. code-block:: python

   original_imgpath = app.builder.imgpath
   app.builder.imgpath = relative_uri(
       app.builder.get_target_uri(relative_to), "_images"
   )

   html = app.builder.render_partial(summary)

   app.builder.imgpath = original_imgpath
   return html["body"]
