:title: Useful HTML Tags
:date: 2019-11-16T17:43:34+00:00
:tags: html,web
:identifier: 20191116T174334

Useful HTML Tags
================

A collection of useful HTML tags that provide features with needing to break
out the JavaScript

Details
-------

Implementing a “Show more..." button

.. code-block:: html
   :class: mb-2

   <details>
       <summary>A short description</summary>
       <p>More detailed markup that can be shown/hidden based on user interaction</p>
   </details>

.. raw:: html

   <details class="border rounded p-2">
       <summary>A short description</summary>
       <p>More detailed markup that can be shown/hidden based on user interaction</p>
   </details>


Dropdown with Suggestions
-------------------------

.. code-block:: html
   :class: mb-2

   <form>
       <label for="inputDemo">Enter your preference:</label>
       <input list="preferences" id="inputDemo" placeholder="Type here..." />
       <datalist id="preferences">
           <option value="Before Breakfast"></option>
           <option value="Before Lunch"></option>
           <option value="Before Dinner"></option>
       </datalist>
   </form>

.. raw:: html

   <form>
       <label for="inputDemo">Enter your preference: </label>
       <input list="preferences" id="inputDemo" placeholder="Type here..."
              class="dark:bg-gray-900 px-2 py-1 border rounded" />
       <datalist id="preferences">
           <option value="Before Breakfast"></option>
           <option value="Before Lunch"></option>
           <option value="Before Dinner"></option>
       </datalist>
   </form>


Dialog Box
----------

Ok, this one does require a little bit of JavaScript

`MDN Documentation <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog>`__

.. code-block:: html

   <dialog></dialog>

.. raw:: html

   <button id="openDialog">Open Dialog</button>
   <dialog id="theDialog">
     <h1>Hello World!</h1>
   </dialog>

   <script>
     const button = document.getElementById('openDialog')
     const dialog = document.getElementById('theDialog')

     button.addEventListener('click', (event) => {
       dialog.showModal()
     })
   </script>

Color Picker
------------

.. code-block:: html
   :class: mb-2

   <label for="pickColor">Choose a color: </label>
   <input id="pickColor" type="color" />


.. raw:: html

   <div class="flex gap-4 items-center">
     <label for="pickColor">Choose a color: </label>
     <input id="pickColor" type="color" />
   </div>

Progress Bars
-------------

.. code-block:: html
   :class: mb-4

   <progress value="56" max="100"></progress>
   <meter min="0" max="100" value="16" low="25" high="75" optimum="50"></meter>
   <meter min="0" max="100" value="42" low="25" high="75" optimum="50"></meter>
   <meter min="0" max="100" value="96" low="25" high="75" optimum="50"></meter>

.. raw:: html

   <div class="flex flex-col gap-4">
     <progress value="56" max="100"></progress>
     <meter min="0" max="100" value="16" low="25" high="75" optimum="50"></meter>
     <meter min="0" max="100" value="42" low="25" high="75" optimum="50"></meter>
     <meter min="0" max="100" value="96" low="25" high="75" optimum="50"></meter>
   </div>

To Explore
----------

- ``inputmode``
- ``contenteditable``
- ``<mark>Some text</mark>`` - Highlight text
- ``<a href="tel:0123456789">0123456789</a>`` - Link to a phone number
- ``<ins>``
- ``<del>``
