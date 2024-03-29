.. post:: 2019-07-07
   :tags: svg, web, js
   :author: Alex Carney
   :language: en
   :image: 1
   :excerpt: 4

.. description = "Implementing clicking and dragging of SVG elements using vanilla JavaScript"

Implementing Click & Drag with Vanilla JS
=========================================

.. raw:: html

   <figure>
     <div id="main"></div>
     <figcaption>
       <p>Try clicking and dragging on this circle.</p>
     </figcaption>
   </figure>
   <script type="text/javascript" src="/_static/js/click-drag.js"></script>


.. admonition:: Disclaimer

   This post makes use of a number of interactive elements to help illustrate a few
   concepts. Unfortunately these do not yet work on mobile devices - sorry mobile
   users!

I have for quite some time now wanted to play around with web development some
more, particularly using web technologies to build user interfaces of some
kind. However there is just **so much** out there it's been impossible for me to
really get anywhere past a "Hello, World!" tutorial before I find myself trying
out the next new shiny.

So I've decided to abandon everything and try a bottom up approach where I see
how far I can push the core web technologies - HTML, CSS and
JavaScript. Hopefully then by the time I start using one of the gazillion
libraries out there I will have a better understanding of why I
needed it in the first place.

In this post I will be looking at implementing clicking and dragging
functionality using only vanilla JavaScript. Clicking and dragging as a concept
can apply to many kinds of interactions so in this instance I'm specifically
referring to clicking on an SVG element moving it around on the page as
illustrated by the demo above.

.. <!--more-->


Setup
-----

All we need to get started is a HTML document that contains some markup which
provides someplace we can reference and attach our image element to, as well as
loading the code we write.

.. code-block:: html

   <div id="main"></div>
   <script type="text/javascript" src="/js/click-drag.js"></script>


Then the first step is to create our SVG image element to act as our "canvas"
that we can draw on.

.. <a id="code-snippet--create-canvas"></a>

.. code-block:: js

   const svgns = "http://www.w3.org/2000/svg"
   const main = document.getElementById("main")

   const canvas = document.createElementNS(svgns, "svg")
   canvas.setAttribute("width", "100%")
   canvas.setAttribute("height", "100%")
   canvas.style.border = "solid 2px #242930"

   main.appendChild(canvas)

A few things to note:

-   By adding our ``<svg>`` element as a child of some ``<div>`` element and setting
    both the ``width`` and ``height`` to ``100%`` our canvas will be able to
    scale responsively based on the styles applied to the parent ``<div>``
-   You might already be familiar with the `document.createElement()`_ function for
    creating HTML elements using JavaScript. However in order to work with SVG
    elements we need to use the `document.createElementNS()`_ function which allows
    us to use the SVG namespace instead of the HTML default.


The View Box
------------

The next step is to construct an appropriate ``viewBox`` definition for our
canvas. For more information on the ``viewBox`` you can refer to the `documentation`_
but to briefly summarise. An SVG image exists on an infinite plane and the
``viewBox`` is the window we use to view a portion of that space, changing the
definition of the ``viewBox`` allows you to zoom in and out on particular regions.

For our purposes what's important is that we construct a ``viewBox`` that matches
the proportions of the ``<svg>`` element as it is displayed in the browser. If
these proportions do not match then the element being dragged around will not
accurately track the cursor, either racing away from or lagging behind it.

One minor issue is that in our setup we didn't explicitly set the dimensions of
our ``<svg>`` element - so how can we know its proportions? Thankfully once the
``<svg>`` as been added to the page we can ask the browser for the bounding box
around the element.

.. <a id="code-snippet--set-viewbox"></a>

.. code-block:: js

   let bbox = canvas.getBoundingClientRect()

Among other properties that are outlined on `this`_ page we can get the width and
height of the rendered image in pixels from which its easy to calculate the
aspect ratio.

.. <a id="code-snippet--set-viewbox"></a>

.. code-block:: js

   const aspectRatio = bbox.width / bbox.height

We're free to choose whichever scale we want for the vertical height of the
``viewBox`` into the ``<svg>`` element. I have chosen ``100`` simply because it feels
like a nice round number. Once we've decided on a scale for the height, it's
easy enough to calculate the corresponding width from our aspect ratio.

.. <a id="code-snippet--set-viewbox"></a>

.. code-block:: js

   const height = 100
   const width = height * aspectRatio

With the dimensions of the ``viewBox`` taken care of all that is left to do is
decide on the coordinates to assign to the top left corner of the ``<svg>``
element and assign the view box to our canvas.

.. <a id="code-snippet--set-viewbox"></a>

.. code-block:: js

   const viewBox = {minX: 0, minY: 0, width: width, height: height}

   const viewBoxStr = [
     viewBox.minX, viewBox.minY, viewBox.width, viewBox.height
   ].join(" ")

   canvas.setAttribute("viewBox", viewBoxStr)

Something to Click on
---------------------

By this point we have finished preparing our canvas and it's time to add
something for us to interact with. To keep things simple I will stick to a ``<circle>``
element, though the method we use here should apply to any SVG element (or any
collection of elements under a ``<g>`` tag).

.. <a id="code-snippet--add-circle"></a>

.. code-block:: js

   const circle = document.createElementNS(svgns, "circle")
   circle.setAttribute("cx", viewBox.width / 2)
   circle.setAttribute("cy", viewBox.height / 2)
   circle.setAttribute("r", 15)
   circle.setAttribute("fill", "#57cc8a")

   canvas.appendChild(circle)

.. note::

   Of course the way in which you define the position of your interactive element
   will depend on the element you have chosen.


Implementing the Drag
---------------------

We will create an event handler for the ``mousemove`` event and attach it to
our canvas.

.. code-block:: js

   canvas.addEventListener("mousemove", (event) => {
     // Do something clever here...
   })

The function we write will be called every time the cursor moves regardless of
whether the user has clicked or not. This means our event handler has to be able
to cope with two situations, the cursor moving when the user has clicked and the
cursor moving when the user has not clicked.

To do this we will declare a variable called ``clicked`` outside the scope of our
function.

.. <a id="code-snippet--dragging"></a>

.. code-block:: js

   let clicked = false

For the moment we will ignore the details around how this variable is updated
(it is covered in the next section), instead let's focus on what we do while the
cursor is moving about the page

Let's get the simpler case out of the way first


Not Clicked
^^^^^^^^^^^

When the mouse is moving but the user has not clicked, then there is nothing for
us to do! We can simply check the value of the ``clicked`` variable and stop the
function if it meets the criteria.

.. code-block:: js

   if (!clicked) {
     return
   }


Clicked
^^^^^^^

Now for the interesting part! The mouse is moving and the user has clicked on
the circle, all we have to do now is update its position to match
the cursor's current position. The only problem is... where is it?

Like all mouse related events the ``event`` object passed into the event handler
will contain a number of position related properties.

-   ``e.client<XY>``: Coordinates of the cursor with respect to the current portion
    of the document visible on the page.
-   ``e.offset<XY>``: Coordinates of the cursor with respect to the edge of the
    target element
-   ``e.page<XY>``: Coordinates of the cursor with respect to the entire HTML page,
    including any portions of the page not currently visible
-   ``e.screen<XY>``: Coordinates of the cursor with respect to the user's display

Reading through those descriptions you would imagine that the ``e.offset<XY>``
properties would be the best fit for our use case. However it's not quite as
simple as that.

Below you should see 2 boxes, the bigger one on the left is our canvas. The
smaller box on the right contains a smaller circle that represents the
calculated position of the cursor based on the ``offset<XY>`` properties like so.

.. code-block:: js

   const x = event.offsetX
   const y = event.offsetY

Try moving the mouse across the canvas and keep an eye on the calculated
position.


.. raw:: html

   <figure>
     <div id="offset-demo"
          style="display:grid;grid-template-columns:50% auto;grid-gap:10px">
     <h3 id="offset-title" style="margin: 0; padding: 15px; padding-top: 0">
       Cursor Position: Offset
     </h3>
       <div>
         <p style="margin:0;padding-left:20px">Target: <span id="offset-target"></span></p>
         <p style="margin:0;padding-left:20px">Position: <span id="offset-position"></span></p>
       </div>
       <svg width="100%"
            id="offset-demo-canvas"
            style="border: solid 2px var(--background-dark)">
       </svg>
       <svg width="50%"
            id="offset-posbox"
            style="border: solid 2px var(--background-dark);margin:auto"><svg>
     </div>
     <figcaption>
       <p>
         Determining the cursor's position using the <code>event.offsetX</code> and
         <code>event.offsetY</code> properties
       </p>
     </figcaption>
   </figure>
   <script type="text/javascript" src="/_static/js/click-drag-offset.js"></script>

Notice the issue when we move across the circle? Why does the calculated
position of the cursor suddenly jump whenever we touch it? The answer lies in
the description of the ``offset<XY>`` property "with respect to the edge of the
**target** element"

When initially trying to implement this I incorrectly assumed that the target
element meant the element that we attached the event listener to - the canvas. In
fact the target element is whichever element is currently under the cursor

To work around this we can calculate the offset values we need ourselves. In
order to do this we will make use of both the bounding box returned from the
``canvas.getBoundingClientRect()`` method as well as the ``client<XY>`` properties
found on the mouse event.

It turns out that the bounding box also returns the coordinates of the top left
corner of the canvas relative to the user's current view of the document -
exactly the same coordinate system used by the ``client<XY>`` properties! From
those two pieces of information it's easy enough to recover the ``offset<XY>``
values ourselves.

.. code-block:: js

   bbox = canvas.getBoundingClientRect()

   const x = event.clientX - bbox.left
   const y = event.clientY - bbox.top

By calculating the coordinates using values that are independent of the element
currently underneath the cursor we sidestep any issues that arise from a
changing target. Try the same thing again on the canvas below.

.. raw:: html

   <figure>
   <div id="client-demo"
         style="display:grid;grid-template-columns:50% auto;grid-gap:10px">
      <h3 id="offset-title" style="margin: 0; padding: 15px; padding-top: 0">
         Cursor Position: Client
      </h3>
      <div>
         <p style="margin:0;padding-left:20px">Target: <span id="client-target"></span></p>
         <p style="margin:0;padding-left:20px">Position: <span id="client-position"></span></p>
      </div>
      <svg width="100%"
            id="client-demo-canvas"
            style="border: solid 2px var(--background-dark)">
      </svg>
         <svg width="50%"
            id="client-posbox"
            style="border: solid 2px var(--background-dark);margin:auto"><svg>
   </div>
   <figcaption>
      <p>
         Determining the cursor's position using the <code>event.clientX</code> and
         <code>event.clientY</code> properties
      </p>
   </figcaption>
   </figure>
   <script type="text/javascript" src="/_static/js/click-drag-client.js"></script>

.. important::

   Since the values ``bbox.top`` and ``bbox.left`` are defined relative to the user's
   current view on the document these values are **not** constant. They will change
   whenever the user alters their view of the page, i.e. performing actions like
   resizing the window or scrolling. This is why we ask for an updated bounding box
   every time our event handler is called.

Now that we can reliably know the position of the cursor, we can focus on the
final piece of this puzzle - updating the position of our ``<circle>``
element. There is however one further issue to work through. The position of the
cursor that we've just calculated is using a different coordinate system to the
one used to draw our circle!

Although we have managed to correctly calculate the cursor's position relative
to our canvas, that position is measured using pixels which makes it highly
dependent on the resolution of the user's screen. A user who uses a 4K monitor
and positions their cursor at the bottom right of the canvas will have a
calculated position much larger than a user on a smartphone...

What this means is that if we map this calculated position directly onto the
circle it won't accurately follow the cursor. The only time the circle would
follow the cursor correctly is when the pixel based coordinates line up with the
coordinate system used in the SVG image. I.e. when the dimensions of the canvas
match up **exactly** with the scale used to define our `viewBox` which in this
case would be ``100px`` tall

Since the mouse circle and the circle use different coordinate systems, we don't
actually care about the exact position we have just calculated. What's more
important is the position of the cursor relative to bounds of the canvas - a
percentage. For example, let's say that the cursor was halfway down the canvas
(``50%``) then we could calculate the corresponding coordinate value in the SVG
coordinate system by multiplying the total height by ``50%``. In our particular
case this would mean setting ``y = 100 * 0.5 = 50``.

We can adopt this approach by using the `width` and `height` information
returned as part of the bounding box to modify our calculation to produce a
percentage rather than an absolute value.

.. code-block:: js

   const x = (event.clientX - bbox.left) / bbox.width
   const y = (event.clientY - bbox.top) / bbox.height

To then convert this percentage into its corresponding value in the SVG
coordinate system all we have to do is multiply it by the width and height of
that system and assign the result to our circle's position!

.. code-block:: js

   circle.setAttriubte("cx", x * viewBox.width)
   circle.setAttribute("cy", y * viewBox.height)

Bringing all that together we end up with the following implementation of our
``mousemove`` event handler.

.. <a id="code-snippet--dragging"></a>

.. code-block:: js

   canvas.addEventListener("mousemove", (event) => {

      if (!clicked) {
         return
      }

      bbox = canvas.getBoundingClientRect()

      const x = (event.clientX - bbox.left) / bbox.width
      const y = (event.clientY - bbox.top) / bbox.height

      circle.setAttribute("cx", x * viewBox.width)
      circle.setAttribute("cy", y * viewBox.height)
   })

Nearly there! The only thing left to do is decide on how we want to update the
``clicked`` variable.


Click Detection
---------------

Finally all that's left is to do is decide how we want to toggle the dragging
behaviour. This mostly comes down to how you want the user to interact with the
draggable object and will change depending on your use case. To keep things
simple I will go with a fairly simple interaction model

-   If the mouse is over the circle and the user clicks then start dragging
-   If the user releases the mouse button then stop dragging

.. <a id="code-snippet--clicking"></a>

.. code-block:: js

   circle.addEventListener("mousedown",  (_) => { clicked = true })
   circle.addEventListener("mouseup", (_) => { clicked = false })

Additionally I will impose one final condition

-   If the mouse leaves the bounds of the canvas then stop dragging.

.. <a id="code-snippet--clicking"></a>

.. code-block:: js

   canvas.addEventListener("mouseleave", (_) => { clicked = false })

This last point is to work around an issue that arises when the user moves the
cursor out of the bounds of the canvas and releases the mouse button. Since the
cursor is no longer over the circle the handler for the ``mouseup`` event on the
circle is never fired so when the user brings their cursor back over the canvas
our code still believes the user never released the mouse button and so the
circle will appear "stuck" to their cursor until they click again.


Conclusion
----------

There you have it, those were some of the basics required to get a working proof
of concept of clicking and dragging functionality using only the JavaScript APIs
that come with your web browser. However in writing this blog post I realised
as with anything that the rabbit hole goes deep and there are many
considerations to keep in mind if you wanted to "productionise" this code for
any real usage.

-   **Touchscreen Support**

    If you were reading this post on a mobile device you will already have noticed
    that none of the interactive demos have worked. This is because touchscreens
    have their own family of ``touchXXXX`` events that are triggered when a user
    interacts with a webpage. While there is some mouse emulation done by the
    browsers (e.g. a `touchstart` event will trigger a ``mousedown`` event if not
    handled), some key events such as `mousemove` are not emulated and require
    dedicated support in your code. See `these`_ `articles`_ for more details

-   **Snap to Center**

    This is only a minor issue and depending on your use case may not be a problem
    at all. Currently whenever you pick up the circle its center snaps to the
    cursor's position. There may be situations where you would prefer the keep the
    object's relative position to the cursor e.g. fine adjustments, the last thing
    you would want is for the object to jump to the cursor just because the user
    happened to click on it off center.

    A way around this would be to record the original positions of both the mouse
    cursor and the object on a click, then on each ``mousemove`` event calculate the
    distance moved by the cursor and apply it to the original recorded position of
    the object.

-   **Multiple Objects**

    Chances are when using this functionality in a real application you would want
    the ability to click and drag on multiple objects. Adding support for this
    would require reworking at least some of the code, having the canvas object
    handle all mouse movements is probably a good idea but of course updating the
    circle's position directly would have to change. It would probably make sense
    to move the click detection logic onto the canvas also, making use of the
    ``event.target`` property to determine which object would need updating.

-   **Canvas Resizing**

    While the existing code makes some effort to ensure this works in a responsive
    manner it is currently only "statically responsive". What I mean is that on
    page load all the necessary calculations are performed to ensure that the
    ``viewBox`` has the correct proportions for example. However if the user were to
    resize the webpage, or rotate their device chances are the proportions of the
    canvas would change meaning that the circle would no longer follow the cursor
    correctly.

    In order to be truly responsive, we would need to listen for events such as
    `resize`_ and perform all the calculations again.

-   **Pan and Zoom**

    Something I realised when writing up the part where we map the cursor's
    position onto the position of the circle is that I had by chance chosen a
    special case where the maths is a little easier. The calculations
    ``x * viewBox.width`` and ``y * viewBox.height`` only work because our ``viewBox`` starts
    at ``(0, 0)``.

    Say we had an application that also allowed for panning and zooming of the
    canvas itself then the chances are our ``viewBox`` would not be starting at
    ``(0, 0)`` and we would have to include an offset in our calculations to reflect
    this. This means for the general case our code should probably look something
    like this

    .. code-block:: js

      circle.setAttribute("cx", (x * viewBox.width) - viewBox.minX)
      circle.setAttribute("cy", (y * viewBox.height) - viewBox.minY)

I'm sure there are more edge cases and considerations to think of but this post
is long enough already! - Perhaps this is why people use libraries for this kind
of thing 🤔...

I will leave you with the final version of the code that went into the demo you
saw at the start of this blog post so you can see it all in context. Hopefully
you found this useful and I'll see you in the next one!

.. _document.createElement(): https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement
.. _document.createElementNS(): https://developer.mozilla.org/en-US/docs/Web/API/Document/createElementNS
.. _documentation: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox
.. _this: https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect
.. _these: https://www.html5rocks.com/en/mobile/touch/
.. _articles: https://www.html5rocks.com/en/mobile/touchandmouse/
.. _resize: https://developer.mozilla.org/en-US/docs/Web/API/Window/resize%5Fevent
