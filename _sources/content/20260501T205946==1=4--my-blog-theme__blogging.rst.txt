:title: My Blog Theme
:date: 2026-05-01
:tags: blogging
:identifier: 20260501T205946
:signature: 1=4

My Blog Theme
=============

.. Pygments does not seem to like more modern CSS syntax like nesting.
   Rather than have glaring red errors all over the page, let's style them as regular text.

.. raw:: html

   <style>
     .highlight span.err { background: #fdf6e3; color: #657B83; }
     @media(prefers-color-scheme: dark) {
       .highlight span.err { background: #002b36; color: #839496; }
     }
   </style>

I use a custom Sphinx theme for this site.

Generally, I try and implement as much as I can using just HTML+CSS however, there are a few occasions where some JavaScript gets involved.

CSS Variables
-------------

Below are the CSS Variables used throughout the site's theme.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   :root {
       --bg-main: white;
       --fg-main: black;

       --bg-sidebar: #161b22;
       --fg-sidebar: white;
       --fg-sidebar-dim: #aaa;

       --highlight-color: #f0b100;
       --border-color: #657b83;

       --fg-accent-dim: #064e3b;
       --fg-accent: #059669;
       --fg-accent-bright: #a7f3d0;

       --transition: 300ms;

       --sidebar-min-width: 0.5em;
       --sidebar-max-width: 300px;

       --panel-min-height: 0.5em;
       --panel-max-height: 400px;

       /* Closed by default */
       --left-sidebar-width: var(--sidebar-min-width);
       --right-sidebar-width: var(--sidebar-min-width);
       --panel-height: var(--sidebar-min-width);
   }

Which makes implementing a dark theme straightforward

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media(prefers-color-scheme: dark) {
     :root {
         --bg-main: #0d1117;
         --fg-main: white;

         --border-color: #839496;

         --fg-accent-dim: #064e3b;
         --fg-accent: #059669;
         --fg-accent-bright: #a7f3d0;
     }
   }

As well as respecting the ``prefers-reduced-motion`` preference

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media screen and (prefers-reduced-motion: reduce) {
     :root {
       --transition: 0.001ms;
     }
   }

A CSS "Reset"
-------------

You might have heard of a `CSS reset <https://en.wikipedia.org/wiki/Reset_style_sheet>`__, while I haven't yet felt the need for a full blown reset stylesheet I do include the following

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   * {
     margin: 0;
     box-sizing: border-box;
   }

Utility Classes
---------------

``.hidden``
^^^^^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   .hidden { display: none; }

HTML Elements
-------------

Trying to work with the CSS cascade rather than against it, it's good to try and define global rules that apply to all HTML elements

Adding styles to the ``html`` element applies them to everything on the page.
I also *think* that by setting the font size here, I can use ``rem`` units to set all font sizes relative to this base size.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   html {
     font-size: 13pt;
     font-family: ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
     scroll-behavior: smooth;
   }

``a``
^^^^^

It's nice if links follow the accent color

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   a { color: var(--fg-accent);}

Section Links
"""""""""""""

Sphinx automatically inserts links for each section header.
I style the usual character (``¶``) so that it's not visible and instead use the link icon from the `feather icon set <https://feathericons.com/?query=link>`__.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   a.headerlink {
     float: right;
     color: var(--bg-main);

     &::before {
       content: "";
       display: inline-block;
       background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"> <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>');
       width: 1em;
       height: 1em;
     }
   }

Tags
""""

When linking to tags I want the link to be styled like a "pill".

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   a.tag {
     color: var(--fg-accent-bright);
     background: var(--fg-accent-dim);
     border: solid 1px var(--fg-accent);
     border-radius: 3px;
     padding: 0.1em 0.5em;

     span.count {
       color: var(--fg-main);
     }
   }

Lists of tags should be flattened

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   ul.taglist {
     display: flex;
     gap: 1em;
     flex-wrap: wrap;

     li {
       list-style: none;
       margin: 0;
     }
   }

``blockquote``
^^^^^^^^^^^^^^

As generated by the ``.. pull-quote::`` directive.

.. pull-quote::

   The technology you use **impresses no one**.

   The experience you create with it is **everything**. -- `Sean Gerety`_

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   blockquote.pull-quote {
       padding: 0 1em;
       font-style: italic;
       border-left: solid var(--fg-accent);
   }

``details``
^^^^^^^^^^^

.. details:: Expand...

   For additional information.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   details > :not(summary) {
     border-left: solid 1px var(--border-color);
     padding: 0 0 0 1em;
     margin: 0 0.2em;
   }

``dd`` & ``dt``
^^^^^^^^^^^^^^^

Used by Sphinx/docutils to represent `definition lists <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#definition-lists>`__

``dt``
   Represents the term to be defined.

``dd``
   Contains the definition.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   dt { margin-top: 1em; }

   dd {
     margin-left: 1em;
     padding-left: 1em;
     border-left: solid 1px var(--fg-accent);

     p:first-child {
       margin-top: 0;
     }
   }

``figure``
^^^^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   figure {
     &.align-center img {
       display: block;
       margin: auto;
     }

     figcaption p {
       margin: auto;
       font-size: 0.8rem;
       text-align: center;
     }
   }


``h1-h6``
^^^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   h1, h2, h3, h4, h5, h6 {
     font-weight: 500;
   }

   h1 { font-size:   2rem; }
   h2 { font-size: 1.8rem; }
   h3 { font-size: 1.7rem; }
   h4 { font-size: 1.5rem; }
   h5 { font-size: 1.4rem; }
   h6 { font-size: 1.2rem; }

``img``
^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   img { max-width: 100%; }

``kbd``
^^^^^^^

e.g. :kbd:`C-x C-f`

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   kbd {
     padding: 0 0.15em;
     color: var(--fg-accent);
   }

``table``
---------

A ``table`` is composed of many elements.

=========  ===========
Element    Description
=========  ===========
``table``  Top-level table element
``thead``  Contains the table's header rows
``tbody``  Contains the table's rows
``tr``     Defines a row
``th``     Defines a header cell
``td``     Defines a normal cell
=========  ===========


.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   table {
     width: 100%;
     border-collapse: collapse;

     thead {
       tr {
         border-bottom: solid 1px var(--border-color);
       }
     }

     td, th {
       padding: 0 0.5em;
       border-right: 1px solid var(--border-color);
     }

     td:last-child, th:last-child {
       border-right: none;
     }
   }

Layout
------

The layout for this site is divided into the following sections

.. container::

   .. raw:: html

      <svg width="100%" style="aspect-ratio: 16 / 9" viewBox="-80 -45 160 90">
       <g style="fill:none;stroke:var(--fg-main);stroke-width:1px">
         <rect x="-50" y="-40" width="100" height="20" />

         <rect x="-50" y="-20" width="25" height="40" />
         <rect x="-25" y="-20" width="50" height="40" />
         <rect x="25" y="-20" width="25" height="40" />

         <rect x="-50" y="20" width="100" height="20" />
       </g>
       <g style="fill:var(--fg-main);font-size:6pt;">
         <text x="-14" y="-25">Header</text>
         <text x="-45" >Left</text>
         <text x="-10">Main</text>
         <text x="27">Right</text>
         <text x="-12" y="35">Footer</text>
       </g>
      </svg>

I want a somewhat dynamic layout for this site, meaning that the sidebars and the footer should be open/closable by the user.

Amazingly, it turns out that the ``grid-template-columns`` and ``grid-template-rows`` CSS properties `can be animated <https://css-tricks.com/animating-css-grid-how-to-examples/>`__!
So as long as you set the ``transition`` property and use a few CSS variables

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   body { overflow: hidden; }

   .grid {
     color: var(--fg-main);
     background: var(--bg-main);

     display: grid;
     grid-template-columns: var(--left-sidebar-width) 1fr var(--right-sidebar-width);
     grid-template-rows: 3em calc(100vh - 3em - var(--panel-height)) var(--panel-height);
     transition: var(--transition);
   }

Then the standard `checkbox trick <https://css-tricks.com/the-checkbox-hack/>`__ can be used to open/close the various elements!
For example, assuming that when checked the sidebar should close, the CSS for the left sidebar might look something like this.

.. code-block:: css

   #left-sidebar-checkbox {
     &:checked ~ .grid {
       --left-sidebar-width: var(--sidebar-min-width);

       .sidebar {
         opacity: 0;
       }
     }
   }

Which, assumes the following HTML structure.

.. code-block:: html

   <body>
     <input type="checkbox" id="left-sidebar-checkbox" class="hidden" />
     <div class="grid">
        ...
        <aside>
          <section class="left-sidebar-toggle">
            <label for="left-sidebar-checkbox"></label>
          </section>
          <div class="sidebar">...</div>

However, I think the only way to make this work across screen sizes, is to change the meaning of the checkbox state depending on the screen size.
This is bound to lead to some quirks if you resize the screen across a breakpoint, but hopefully, it's enough of an edge case to not have to worry too much about it! 😅

Desktop
^^^^^^^

Playing around with some screen sizes... about ``1000px`` feels the right time to have the left sidebar open by default.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media screen and (min-width: 1000px) {

      .grid {
        --left-sidebar-width: var(--sidebar-max-width);
        .left-sidebar { opacity: 100%; }
      }

      label[for="left-sidebar-checkbox"] rect.open-state {
         fill: var(--fg-sidebar-dim);
      }

      #left-sidebar-checkbox {

        &:checked ~ .grid label[for="left-sidebar-checkbox"] rect.open-state {
          fill: none;
        }

        &:checked ~ .grid {
          --left-sidebar-width: var(--sidebar-min-width);

          .left-sidebar {
            opacity: 0;
          }
        }
      }

   }

Then at around ``1600px``, the right sidebar may as well open by default

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media screen and (min-width: 1600px) {

      .grid {
        --right-sidebar-width: var(--sidebar-max-width);
        .right-sidebar { opacity: 100%; }
      }

      label[for="right-sidebar-checkbox"] rect.open-state {
         fill: var(--fg-sidebar-dim);
      }

      #right-sidebar-checkbox {

        &:checked ~ .grid label[for="right-sidebar-checkbox"] rect.open-state {
          fill: none;
        }

        &:checked ~ .grid {
          --right-sidebar-width: var(--sidebar-min-width);

          .right-sidebar {
            opacity: 0;
          }
        }
      }
   }

The panel will always be closed by default

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   #panel-checkbox {
     &:checked ~ .grid {
       --panel-height: var(--panel-max-height);
     }

     &:checked ~ .grid label[for="panel-checkbox"] rect.open-state {
       fill: var(--fg-sidebar-dim);
     }

   }

Components
----------

Header
^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   header.site {
     color: var(--fg-sidebar-dim);
     background: var(--bg-sidebar);

     padding: 0.5em;

     position: sticky;
     top: 0;

     display: flex;
     align-items: center;
     grid-column: span 3;

     z-index: 2;
   }

Site Title
""""""""""

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   section.site-title {
     display: flex;
     align-items: center;
     gap: 0.5em;

     h1 {
       font-size: 1.4rem;
     }

     a {
       color: var(--fg-sidebar-dim);

       span {
         color: var(--fg-accent);
       }
     }

     img {
       border-radius: 100%;
       width: 2em;
       border: solid 1px var(--fg-accent);
     }
   }

On narrow screens, omit the site title text.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media screen and (max-width: 600px) {
     section.site-title {
       h1 { display: none; }
     }
   }

Site Navigation
"""""""""""""""

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   section.site-navigation {
     flex-grow: 1;
     font-size: 1.2rem;
     padding: 0 0.5em;

     label[for="menu-toggle"] { display: none; }

     nav {
       text-align: center;

       ul {
         padding: 0;
         display: flex;
         gap: 0.5em;
         justify-content: flex-end;

         li {
           list-style: none;
         }
       }
     }
   }

When the display is too narrow, hide the nav list and show the menu toggle instead.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media screen and (max-width: 600px) {
     section.site-navigation {

       label[for="menu-toggle"] {
         color: var(--fg-sidebar-dim);
         display: inline-block;
         width: 2em;
       }

       #menu-toggle:not(:checked) ~ nav ul {
         height: 0;
       }

       #menu-toggle:checked ~ nav ul {
         height: 145px;
       }

       #menu-toggle:checked ~ label[for="menu-toggle"] {
         color: var(--fg-accent);
       }

       nav {
         position: relative;
         text-align: left;

         ul {
           position: absolute;
           background: var(--bg-sidebar);
           display: block;
           z-index: 3;
           width: 100%;
           transition: var(--transition);
           overflow: hidden;
         }

         li {
           padding: 0.5em;
         }

         li:not(:first-child) {
           border-top: solid 1px var(--border-color);
         }
       }
     }
   }

Layout Toggles
""""""""""""""

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   section.layout-toggles {
      color: var(--fg-sidebar-dim);

      label[for="left-sidebar-checkbox"] {}

      label[for="panel-checkbox"] {
        svg { transform: rotate(-90deg); }
      }

      label[for="right-sidebar-checkbox"] {
        svg { transform: rotate(180deg); }
      }
   }

Sidebars
--------

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   .grid > aside {
     color: var(--fg-sidebar);
     background: var(--bg-sidebar);
   }

By making the sidebar content ``position: sticky`` it will move with the viewport.


.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   div.left-sidebar,
   div.right-sidebar {
     height: calc(100vh - 3em - var(--panel-height));
     padding: 0.5em;
     position: sticky;
     top: 3em;
     opacity: 0;
     overflow-y: auto;
     transition: var(--transition);

     h5 {
       font-weight: normal;
     }

     ul { padding: 0 0 0 1em; }

     section {
       margin-bottom: 2em;
     }
   }

Metadata
^^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   section.post-metadata {
     display: grid;
     grid-template-columns: 2em auto;

     ul.taglist {
       justify-content: flex-end;
     }
   }

Page Contents
^^^^^^^^^^^^^

These styles control the table of contents for the current page as generated by Sphinx's ``{{toc}}`` template macro.
As far as I can tell, there is no easy way to override the generated HTML, so these styles need to work with what we have.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   #localtoc {
     padding: 0;

     a {
       color: var(--fg-sidebar);
       border-right: solid 5px var(--bg-sidebar);
       display: inline-block;
       width: calc(100% - 20px); /* Need to leave room for the list marker */

       &.current {
          color: var(--fg-accent);
          border-color: var(--fg-accent);
       }
     }

     ul { padding: 0 0 0 1em; }

     li {
       padding: 0.1em 0em;
       list-style: disc inside;
     }
   }

Since I want the top-level "Contents" link to be a section header, yet Sphinx renders it as another list item, some amount of fiddling is required.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   #localtoc > ul,
   #localtoc > ul > li,
   #localtoc > ul > li > a,
   #localtoc > ul > li > ul {
       padding: 0;
   }

   #localtoc > ul > li {
       list-style: none;
   }

   #localtoc > ul > li > a {
       border: none;
       font-size: 1.4rem;
       text-decoration: none;
   }

Related Pages
^^^^^^^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   section.post-related {
     padding: 0;

     a {
       color: var(--fg-sidebar);
       border-right: solid 5px var(--bg-sidebar);
       display: inline-block;
       width: 100%;
       overflow: hidden;
       text-wrap: nowrap;
       text-overflow: ellipsis;

       &.current {
         color: var(--fg-accent);
         border-color: var(--fg-accent);
       }
     }

     ul { padding: 0 0 0 1em; }
     li { list-style: disc; }
   }

Search
^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   search {
     form { display: flex; }

     input[type="search"] {
       padding: 0.5em;
       font-size: 1rem;
       color: var(--fg-sidebar);
       background: #0d1117;
       border: solid 1px var(--border-color);
       border-radius: 5px 0 0 5px;
       width: 100%;

       &:focus {
         outline: transparent;
         border-color: var(--fg-accent);
       }
     }

     [type="submit"] {
       color: var(--fg-sidebar);
       background: var(--fg-accent);
       border-radius: 0 5px 5px 0;
       border: solid 1px 1px var(--border-color);
     }
   }

Social Links
^^^^^^^^^^^^

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   section.social-links {
     nav {
       display: flex;
       margin: 0.5em 0;
       justify-content: space-around;
     }

     a { color: var(--fg-sidebar); }
   }

Main
----

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   main {
     min-width: 0;
     max-height: 100%;
     overflow-y: auto
   }

``article``
^^^^^^^^^^^

I use ``article`` elements to contain the main content of the page.

Setting the ``scroll-margin`` ensures that section headers are not obscured by the site header when scrolling to a particular section.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   article {
     padding: 0 2em;
     line-height: 1.5;
     max-width: 100ch;

     section {
       scroll-margin: 3em;
     }

     footer {
       border-top: solid 1px var(--border-color);
     }
   }

On mobile the padding should be reduced a bit to create more space

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   @media screen and (max-width: 600px) {
     article { padding: 0 0.5em; }
   }


Code
""""

Sphinx/docutils render inline code in ``<code>`` tags with the text further wrapped in a ``<span>`` tag.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   article {
     code.literal {
       &::before, &&::after {
         content: "`";
       }

       span.pre {
         font-weight: 600;
         font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
       }
     }
   }

While code blocks are in a ``<div class="highlight">`` tag.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   div.highlight {
     padding: 0.5em;
     margin: 0.5em 0;
     overflow-x: auto;
     border: solid 1px var(--border-color);
     border-radius: 5px;
   }

I use `awdur <https://github.com/swyddfa/awdur>`__ throughout this site to take the contents of code blocks and export them to separate code files (for example all the CSS on this page!).
Awdur provides a code block header, indicating where the code will be exported to.
This header also needs to be styled to match the look and feel of this site.

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   div.awdur-codeblock {
     border: none;

     div.awdur-codeblock-header {
       color: var(--fg-sidebar);
       background: var(--bg-sidebar);
       padding: 0 0.5em;

       border: solid 1px var(--border-color);
       border-top-left-radius: 5px;
       border-top-right-radius: 5px;
       border-bottom: none;
     }

     div.highlight {
       border-top: none;
       border-top-left-radius: 0;
       border-top-right-radius: 0;
       margin-top: 0;
     }
   }

Typography
""""""""""

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   article {
     h1, h2, h3, h4, h5, h6 { color: var(--fg-accent); }

     p { margin: 1em 0; }

     table {
       line-height: unset;
       p { margin: 0;}
     }
   }

Footer
------

.. code-block:: css
   :project: sphinx:dirhtml
   :filename: _static/css/styles.css

   footer.site {
     color: var(--fg-sidebar);
     background: var(--bg-sidebar);

     grid-column: span 3;
   }
