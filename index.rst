.. container:: home-grid

   .. admonition:: `Blog </blog>`__

      Blog posts, thoughts and ideas. Typically building some small project to figure out how something works.


   .. admonition:: :doc:`/code`

      A group of small programming projects that typically have one or more blog posts assoicated with them.

      Most (but not yet all) of the code here is an excercise in literate programming, written using :gh:`swyddfa/awdur`.

   .. admonition:: `Notes </notes>`__

      Everything else.


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
