:template: layout.html

Welcome
=======

.. raw:: html

   <div class="flex flex-col mt-8 space-y-2 lg:flex-row lg:justify-between lg:space-y-0 lg:space-x-2">
      <div class="w-full p-4 prose-sm prose transition bg-white border lg:w-1/3 hover:shadow-lg prose-green">
         <h3><a href="/blog">Blog</a></h3>
         <p class="mt-4">
            Blog posts, thoughts and ideas. Typically building some small project to figure out how something works.
         </p>
      </div>
      <div class="w-full p-4 prose-sm prose transition bg-white border lg:w-1/3 hover:shadow-lg prose-green">
         <h3><a href="/code">Code</a></h3>
         <p class="mt-4">
            A group of small programming projects that typically have one or more blog posts assoicated with them.
         </p>
      </div>
      <div class="w-full p-4 prose-sm prose transition bg-white border lg:w-1/3 hover:shadow-lg prose-green">
         <h3><a href="/notes">Notes</a></h3>
         <p class="mt-4">
            A random collection of items that I find useful to refer back to from time to time, but aren't
            necessarily interesting enough to made into fully fledged blog posts.
         </p>
      </div>
   </div>
  

.. toctree::
   :hidden:
   :maxdepth: 1

   code
   notes