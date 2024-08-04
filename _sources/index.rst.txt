:template: layout.html

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: Blog
      :link: blog-posts
      :link-type: ref
      :class-title: text-lg text-green-600 bang!font-normal
      :class-card: w-full p-4 prose-sm prose dark:prose-invert transition bg-white dark:bg-gray-800 border dark:border-gray-600 lg:w-1/3 hover:shadow-lg prose-green

      Blog posts, thoughts and ideas. Typically building some small project to figure out how something works.

   .. grid-item-card:: Code
      :link: /code
      :link-type: doc
      :class-title: text-lg text-green-600 bang!font-normal
      :class-card: w-full p-4 prose-sm prose dark:prose-invert transition bg-white dark:bg-gray-800 border dark:border-gray-600 lg:w-1/3 hover:shadow-lg prose-green

      A group of small programming projects that typically have one or more blog posts assoicated with them.

   .. grid-item-card:: Dotfiles
      :link: /dotfiles
      :link-type: doc
      :class-title: text-lg text-green-600 bang!font-normal
      :class-card: w-full p-4 prose-sm prose dark:prose-invert transition bg-white dark:bg-gray-800 border dark:border-gray-600 lg:w-1/3 hover:shadow-lg prose-green

      My dotfiles as literate configuration, a testing ground for `awdur <https://github.com/swyddfa/awdur>`__

   .. grid-item-card:: Notes
      :link: /notes
      :link-type: doc
      :class-title: text-lg text-green-600 bang!font-normal
      :class-card: w-full p-4 prose-sm prose dark:prose-invert transition bg-white dark:bg-gray-800 border dark:border-gray-600 lg:w-1/3 hover:shadow-lg prose-green

      A random collection of items that I find useful to refer back to from time to time, but aren't necessarily interesting enough to made into fully fledged blog posts.

.. toctree::
   :hidden:
   :maxdepth: 1

   code
   dotfiles
   notes
