Jinja Templates
===============

Basic Setup
-----------

#. Create a folder containing all your templates

   .. code-block:: none

      templates
      ├── layout.html
      ...
      └── links.html

#. Create an ``Environment`` with an appropriate loader so that ``jinja`` is able to 
   find the templates.

   .. code-block:: python

      import jinja2 as j2

      loader = j2.FileSystemLoader(templates_dir)
      env = j2.Environment(loader=loader)

#. Load the relevant template(s) from the environment

   .. code-block:: python

      template = env.get_template("layout.html")

#. Create the context containing the variables that are passed down into the template.

   .. code-block:: python

      context = {
         "date": datetime.now(),
         "author": "S. King",
         "word_count": float("inf")
      }

#. Render the template!

   .. code-block:: python

      with open(filename, "w") as f:
         f.write(template.render(context))