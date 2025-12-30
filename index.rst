.. container:: home-grid

   .. admonition:: `Blog </blog>`__

      Blog posts, thoughts and ideas. Typically building some small project to figure out how something works.


   .. admonition:: :doc:`/code`

      A group of small programming projects that typically have one or more blog posts assoicated with them.


   .. admonition:: :doc:`/dotfiles`

      My dotfiles as literate configuration, a testing ground for `awdur <https://github.com/swyddfa/awdur>`__


   .. admonition:: `Notes </notes>`__

      Anything that doesn't fit into the above categories


.. raw:: html

   <style>
     .home-grid {
       display: grid;
       grid-template-columns: auto auto;
       gap: 1em 2em;
     }

     @media screen and (max-width: 1000px) {
       .home-grid {
         grid-template-columns: auto;
       }
     }
   </style>

.. toctree::
   :hidden:
   :maxdepth: 1

   code
   dotfiles
