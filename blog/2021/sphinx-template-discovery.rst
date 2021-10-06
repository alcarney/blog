.. post:: 2021-09-28
   :tags: sphinx, python
   :author: me
   :language: en
   :excerpt: 1

Sphinx Template Discovery
=========================

When I was redesigning this site, there were times when it wasn't obvious to me which
templates were being used to render a given page. Thankfully it's not too hard to get
Sphinx itself to tell you.

After some digging around in the `source code`_ for the HTML Builder I found the
``handle_page`` function responsible for passing the page to its corresponding template
and from there it was easy enough to add a print statement with the information that
I needed.

.. code-block:: python
   :emphasize-lines: 6

   def handle_page(self, pagename: str, addctx: Dict, templatename: str = 'page.html',
                   outfilename: str = None, event_arg: Any = None) -> None:
       ...

       try:
           print(f"{pagename}: {templatename}")
           output = self.templates.render(templatename, ctx)
       except UnicodeError:
           logger.warning(__("a Unicode error occurred when rendering the page %s. "
                             "Please make sure all config values that contain "
                             "non-ASCII content are Unicode strings."), pagename)


Then to determine which template was being used for a given page, I only had to find it 
in the build output.

.. code-block:: none 

   Running Sphinx v4.2.0
   loading pickled environment... done
   building [mo]: targets for 0 po files that are out of date
   building [dirhtml]: targets for 1 source files that are out of date
   updating environment: 0 added, 1 changed, 0 removed
   reading sources... [100%] blog/2021/sphinx-template-discovery                                                
   looking for now-outdated files... none found
   pickling environment... done
   checking consistency... done
   preparing documents... done
   blog/2021/sphinx-template-discovery: page.htmllate-discovery                                                 
   index: page.html. [100%] index                                                                               

   generating indices... genindex genindex: genindex.html
   done
   blog/author: catalog.html
   blog/author/me: collection.html
   blog/language: catalog.html
   blog/language/en: collection.html
   blog/archive: catalog.html
   blog/2021: collection.html
   blog/2020: collection.html
   blog/2019: collection.html
   blog/2018: collection.html
   blog/tag: catalog.html
   blog/tag/blogging: collection.html
   blog/tag/c: collection.html
   blog/tag/cli: collection.html
   blog/tag/containers: collection.html
   blog/tag/go: collection.html
   blog/tag/graphics: collection.html
   blog/tag/js: collection.html
   blog/tag/lxd: collection.html
   blog/tag/note-to-self: collection.html
   blog/tag/programming-languages: collection.html
   blog/tag/python: collection.html
   blog/tag/sphinx: collection.html
   blog/tag/stylo: collection.html
   blog/tag/svg: collection.html
   blog/tag/til: collection.html
   blog/tag/tinygo: collection.html
   blog/tag/vulkan: collection.html
   blog/tag/wasm: collection.html
   blog/tag/web: collection.html
   blog: collection.html
   blog/drafts: collection.html
   writing additional pages... search search: search.html
   done
   copying static files... done
   copying extra files... done
   dumping search index in English (code: en)... done
   dumping object inventory... done
   build succeeded.


.. _source code: https://github.com/sphinx-doc/sphinx/blob/4.x/sphinx/builders/html/__init__.py