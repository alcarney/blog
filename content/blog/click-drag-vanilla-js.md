+++
title = "Implementing Click & Drag with Vanilla JS"
author = ["Alex Carney"]
date = 2019-07-03T19:45:00+01:00
tags = ["svg", "web", "js"]
draft = false
+++

<figure>
  <div id="main"></div>
  <figcaption>
    <p>Try clicking and dragging on this circle.</p>
  </figcaption>
</figure>
<script type="text/javascript" src="/js/click-drag.js"></script>

> **Disclaimer:**
>
> This post makes use of a number of interactive elements to help illustrate a few
> concepts. Unfortunately these do not yet work on mobile devices - sorry mobile
> users!

I have for quite some time now wanted to play around with web development some
more, particularly using web technologies to build user interfaces of some
kind. However there is just **so much** out there it's been impossible for me to
really get anywhere past a "Hello, World!" tutorial before I find myself trying
out the next new shiny.

So I've decided to abandon  everything and try a bottom up approach
where I see how far I can push the core web technologies - HTML, CSS and
JavaScript. Hopefully then by the time I start using one of the
gazillion libraries/frameworks out there I have a better understanding of why I
needed it in the first place.

In this post I will be looking at implementing clicking and dragging
functionality using only vanilla JavaScript. Clicking and dragging as a concept
can apply to many kinds of interactions so in this instance I'm specifically
referring to clicking on an SVG element moving it around on the page and then
letting go of it again as illustrated by the demo above.


## Setup {#setup}

All we need to get started is a HTML document that contains some markup which
provides someplace we can reference and attach our image element to, as well as
loading the code we write.

{{< highlight html >}}
<div id="main"></div>
<script type="text/javascript" src="./click-drag.js"></script>
{{< /highlight >}}

Then the first step is to create our SVG image element to act as our "canvas"
that we can draw on.

<a id="code-snippet--create-canvas"></a>
{{< highlight javascript >}}
const svgns = "http://www.w3.org/2000/svg"
const main = document.getElementById("main")

const canvas = document.createElementNS(svgns, "svg")
canvas.setAttribute("width", "100%")
canvas.setAttribute("height", "100%")
canvas.style.border = "solid 2px #242930"

main.appendChild(canvas)
{{< /highlight >}}

A few things to note:

-   By adding our `<svg>` element as a child of some `<div>` element and setting
    both the `width` and `height` to `100%` our canvas will be able to
    scale responsively based on the styles applied to the parent `<div>`
-   You might already be familiar with the [`document.createElement()`](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement) function for
    creating HTML elements using JavaScript. However in order to work with SVG
    elements we need to use the [`document.createElementNS()`](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElementNS) function which allows
    us to use the SVG namespace instead of the HTML default.


## The View Box {#the-view-box}

The next step is to construct an appropriate `viewBox` definition for our
canvas. For more information on the `viewBox` you can refer to [this](https://vanseodesign.com/web-design/svg-viewbox/) article but
to briefly summarise. An SVG image exists on an infinite plane and the `viewBox`
is the window we use to view a portion of that space, changing the definition of
the `viewBox` allows you to zoom in and out on particular regions.

For our purposes what's important is that we construct a `viewBox` that matches
the proportions of the `<svg>` element as it is displayed in the browser. If
these proportions do not match then the element being dragged around will not
accurately track the cursor, either racing away from or lagging behind it.

One minor issue is that in our setup we didn't explicitly set the dimensions of
our `<svg>` element - so how can we know its proportions? Thankfully once the
`<svg>` as been added to the page we can ask the browser for the bounding box
around the element.

<a id="code-snippet--set-viewbox"></a>
{{< highlight javascript >}}
let bbox = canvas.getBoundingClientRect()
{{< /highlight >}}

Among other properties that are outlined on [this](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect) page we can get the width and
height of the rendered image in pixels from which its easy to calculate the
aspect ratio.

<a id="code-snippet--set-viewbox"></a>
{{< highlight javascript >}}
const aspectRatio = bbox.width / bbox.height
{{< /highlight >}}

We're free to choose whichever scale we want for the vertical height of the
`viewBox` into the `<svg>` element. I have chosen `100` simply because it feels
like a nice round number. Once we've decided on a scale for the height, it's
easy enough to calculate the corresponding width from our aspect ratio.

<a id="code-snippet--set-viewbox"></a>
{{< highlight javascript >}}
const height = 100
const width = height * aspectRatio
{{< /highlight >}}

With the dimensions of the `viewBox` taken care of all that is left to do is
decide on the coordinates to assign to the top left corner of the `<svg>`
element and assign the view box to our canvas.

<a id="code-snippet--set-viewbox"></a>
{{< highlight javascript >}}
const viewBox = {minX: 0, minY: 0, width: width, height: height}

const viewBoxStr = [
  viewBox.minX, viewBox.minY, viewBox.width, viewBox.height
].join(" ")

canvas.setAttribute("viewBox", viewBoxStr)
{{< /highlight >}}


## Something to Click on {#something-to-click-on}

By this point we have finished preparing our canvas and it's time to add
something for us to interact with. To keep things simple I will stick to a `<circle>`
element, though the method we use here should apply to any SVG element (or any
collection of elements under a `<g>` tag).

<a id="code-snippet--add-circle"></a>
{{< highlight javascript >}}
const circle = document.createElementNS(svgns, "circle")
circle.setAttribute("cx", viewBox.width / 2)
circle.setAttribute("cy", viewBox.height / 2)
circle.setAttribute("r", 15)
circle.setAttribute("fill", "#57cc8a")

canvas.appendChild(circle)
{{< /highlight >}}

> **Note:**
>
> Of course the way in which you define the position of your interactive element
> will depend on the element you have chosen.


## Implementing the Drag {#implementing-the-drag}

We will create an event handler for the `mousemove` event and attach it to
our canvas.

{{< highlight javascript >}}
canvas.addEventListener("mousemove", (event) => {
  // Do something clever here...
})
{{< /highlight >}}

The function we write will be called every time the cursor moves regardless of
whether the user has clicked or not. This means our event handler has to be able
to cope with two situations, the cursor moving when the user has clicked and the
cursor moving when the user has not clicked.

To do this we will declare a variable called `clicked` outside the scope of our
function.

<a id="code-snippet--dragging"></a>
{{< highlight javascript >}}
let clicked = false
{{< /highlight >}}

For the moment we will ignore the details around how this variable is updated
(it is covered in the next section), instead let's focus on being what we do
once while the cursor is moving about the page

Let's get the simpler case out of the way first


### Not Clicked {#not-clicked}

When the mouse is moving but the user has not clicked, then there is nothing for
us to do! We can simply check the value of the `clicked` variable and stop the
function if it meets the criteria.

{{< highlight javascript >}}
if (!clicked) {
  return
}
{{< /highlight >}}


### Clicked {#clicked}

Now for the interesting part! The mouse is moving and the user has clicked on
the circle, all we have to do now is update the position of the circle to match
the cursor's current position. The only problem is... where is it?

Like all mouse related events the `event` object passed into the event handler
will contain a number of position related properties.

-   `e.client<XY>`: Coordinates of the cursor with respect to the current portion
    of the document visible on the page.
-   `e.offset<XY>`: Coordinates of the cursor with respect to the edge of the
    target element
-   `e.page<XY>`: Coordinates of the cursor with respect to the entire HTML page,
    including any portions of the page not currently visible
-   `e.screen<XY>`: Coordinates of the cursor with respect to the user's display

Reading through those descriptions you would imagine that the `e.offset<XY>`
properties would be the best fit for our use case. However it's not quite as
simple as that.

Below you should see 2 boxes, the bigger one on the left is our canvas. The
smaller box on the right contains a smaller circle that represents the
calculated position of the cursor based on the `offset<XY>` properties like so.

{{< highlight javascript >}}
const x = event.offsetX
const y = event.offsetY
{{< /highlight >}}

Try moving the mouse across the canvas and keep an eye on the calculated
position.

<figure>
  <div id="offset-demo"
       style="display:grid;grid-template-columns:50% auto;grid-gap:10px">
    <svg width="100%"
         id="offset-demo-canvas"
         style="border: solid 2px #242930">
    </svg>
    <div>
      <h3 id="offset-title"
          style="margin: 0; padding: 15px; padding-top: 0">Cursor Position: Offset</h3>
      <p style="margin:0;padding-left:20px">Target: <span id="offset-target"></span></p>
      <p style="margin:0;padding-left:20px">Position: <span id="offset-position"></span></p>
      <svg width="50%"
           id="offset-posbox"
           style="border: solid 2px #242930;"><svg>
    </div>
  </div>
  <figcaption>
    <p>
      Determining the cursor's position using the <code>event.offsetX</code> and
      <code>event.offsetY</code> properties
    </p>
  </figcaption>
</figure>
<script type="text/javascript" src="./js/click-drag-offset.js"></script>

Notice the issue when we move across the circle? Why does the calculated
position of the cursor suddenly jump whenever we touch it? The answer lies in
the description of the `offset<XY>` property "with respect to the edge of the
**target** element"

When initially trying to implement this I incorrectly assumed that the target
element meant the element that we attached the event listener to - the canvas. In
fact the target element is whichever element is currently under the cursor

To work around this we can calculate the offset values we need ourselves. In
order to do this we will make use of both the bounding box returned from the
`canvas.getBoundingClientRect()` method as well as the `client<XY>` properties
found on the mouse event.

It turns out that the bounding box also returns the coordinates of the top left
corner of the canvas relative to the user's current view of the document -
exactly the same coordinate system used by the `client<XY>` properties! From
those two pieces of information it's easy enough to recover the `offset<XY>`
values ourselves.

{{< highlight javascript >}}
bbox = canvas.getBoundingClientRect()

const x = event.clientX - bbox.left
const y = event.clientY - bbox.top
{{< /highlight >}}

By calculating the coordinates from values based off of values independent of
the element currently underneath the cursor we sidestep any issues that arise
from a changing target. Try the same thing again on the canvas below.

<figure>
  <div id="client-demo"
       style="display:grid;grid-template-columns:50% auto;grid-gap:10px">
    <svg width="100%"
         id="client-demo-canvas"
         style="border: solid 2px #242930">
    </svg>
    <div>
      <h3 id="offset-title"
          style="margin: 0; padding: 15px; padding-top: 0">Cursor Position: Client</h3>
      <p style="margin:0;padding-left:20px">Target: <span id="client-target"></span></p>
      <p style="margin:0;padding-left:20px">Position: <span id="client-position"></span></p>
      <svg width="50%"
           id="client-posbox"
           style="border: solid 2px #242930;"><svg>
    </div>
  </div>
  <figcaption>
    <p>
      Determining the cursor's position using the <code>event.clientX</code> and
      <code>event.clientY</code> properties
    </p>
  </figcaption>
</figure>
<script type="text/javascript" src="./js/click-drag-client.js"></script>

> **Important:**
>
> Since the values `bbox.top` and `bbox.left` are defined relative to the user's
> current view on the document these values are **not** constant. They will change
> whenever the user alters their view of the page, this could mean actions like
> resizing the window or scrolling. This is why we ask for an updated bounding box
> while handling every event to ensure we compensate for these effects

Once we know the position of the cursor, all that's left to do is to update the
position of our `<circle>` element

{{< highlight javascript >}}
const x = event.clientX
const y = event.clientY

circle.setAttriubte("cx", x)
circle.setAttribute("cy", y)
{{< /highlight >}}

Bringing all that together we end up with the following implementation of our
`mousemove` event handler.

<a id="code-snippet--dragging"></a>
{{< highlight javascript >}}
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
{{< /highlight >}}

Nearly there! The only thing left to do is decide on how we want to update the
`clicked` variable.


## Click Detection {#click-detection}

Finally all that's left is to do is decide how we want to toggle the dragging
behaviour. This mostly comes down to how you want the user to interact with the
draggable object and will change depending on your use case. To keep things
simple I will go with a fairly simple interaction model

-   If the mouse is over the circle and the user clicks then start dragging
-   If the user releases the mouse button then stop dragging

<a id="code-snippet--clicking"></a>
{{< highlight javascript >}}
circle.addEventListener("mousedown",  (_) => { clicked = true })
circle.addEventListener("mouseup", (_) => { clicked = false })
{{< /highlight >}}

Additionally I will impose one final condition

-   If the mouse leaves the bounds of the canvas then stop dragging.

This last point is to work around an issue that arises when the user moves the
cursor out of the bounds of the canvas and releases the mouse button. Since the
cursor is no longer over the circle the handler for the `mouseup` event on the
circle is never fired.

<a id="code-snippet--clicking"></a>
{{< highlight javascript >}}
canvas.addEventListener("mouseleave", (_) => { clicked = false })
{{< /highlight >}}


## Conclusion {#conclusion}

While this works there are a number of ways in which this can be improved

-   Touchscreen support
-   Snap to Center
-   Canvas resizing


### Complete Code {#complete-code}

Here is the final version of the code.

{{< highlight javascript >}}
// Setup
const svgns = "http://www.w3.org/2000/svg"
const main = document.getElementById("main")

const canvas = document.createElementNS(svgns, "svg")
canvas.setAttribute("width", "100%")
canvas.setAttribute("height", "100%")
canvas.style.border = "solid 2px #242930"

main.appendChild(canvas)

// Viewbox
let bbox = canvas.getBoundingClientRect()
const aspectRatio = bbox.width / bbox.height
const height = 100
const width = height * aspectRatio
const viewBox = {minX: 0, minY: 0, width: width, height: height}

const viewBoxStr = [
  viewBox.minX, viewBox.minY, viewBox.width, viewBox.height
].join(" ")

canvas.setAttribute("viewBox", viewBoxStr)

// Something to click on
const circle = document.createElementNS(svgns, "circle")
circle.setAttribute("cx", viewBox.width / 2)
circle.setAttribute("cy", viewBox.height / 2)
circle.setAttribute("r", 15)
circle.setAttribute("fill", "#57cc8a")

canvas.appendChild(circle)

// Implementing the drag
let clicked = false
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

// Click detection
circle.addEventListener("mousedown",  (_) => { clicked = true })
circle.addEventListener("mouseup", (_) => { clicked = false })
canvas.addEventListener("mouseleave", (_) => { clicked = false })
{{< /highlight >}}
