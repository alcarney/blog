+++
title = "Creating an Infinite Scaleable Grid"
author = ["Alex Carney"]
tags = ["js", "web", "svg"]
draft = true
+++

<figure>
  <div id="main"></div>
  <figcaption>
    <p>A pannable, zoomable grid</p>
  </figcaption>
</figure>
<script type="text/javascript" src="/js/grid-scale.js"></script>

<a id="code-snippet--draw-line"></a>
{{< highlight javascript >}}
function makeLine(a, b) {

   const line = document.createElementNS(svgns, "line")

   line.setAttribute("x1", a.x)
   line.setAttribute("x2", b.x)
   line.setAttribute("y1", a.y)
   line.setAttribute("y2", b.y)

   line.setAttribute("stroke", "white")
   line.setAttribute("stroke-opacity", 0.5)
   line.setAttribute("stroke-width", 0.2)

   return line
}
{{< /highlight >}}

<a id="code-snippet--draw-grid"></a>
{{< highlight javascript >}}
function drawGrid(canvas, viewBox, spacing) {

  const numRows = Math.ceil(viewBox.height / spacing)
  const numCols = Math.ceil(viewBox.width / spacing)

  for (let i = 0; i < numRows; i++) {

     const y = (i * spacing) + (spacing / 2)
     const line = makeLine({x: viewBox.xMin, y: y}, {x: viewBox.width, y: y})
     canvas.appendChild(line)
  }

  for (let i = 0; i < numCols; i++) {

    const x = (i * spacing) + (spacing / 2)
    const line = makeLine({x: x, y: viewBox.yMin}, {x: x, y: viewBox.height})
    canvas.appendChild(line)
  }
}
{{< /highlight >}}

{{< highlight javascript >}}
const svgns = "http://www.w3.org/2000/svg"

function makeLine(a, b) {

   const line = document.createElementNS(svgns, "line")

   line.setAttribute("x1", a.x)
   line.setAttribute("x2", b.x)
   line.setAttribute("y1", a.y)
   line.setAttribute("y2", b.y)

   line.setAttribute("stroke", "white")
   line.setAttribute("stroke-opacity", 0.5)
   line.setAttribute("stroke-width", 0.2)

   return line
}

function drawGrid(canvas, viewBox, spacing) {

  const numRows = Math.ceil(viewBox.height / spacing)
  const numCols = Math.ceil(viewBox.width / spacing)

  for (let i = 0; i < numRows; i++) {

     const y = (i * spacing) + (spacing / 2)
     const line = makeLine({x: viewBox.xMin, y: y}, {x: viewBox.width, y: y})
     canvas.appendChild(line)
  }

  for (let i = 0; i < numCols; i++) {

    const x = (i * spacing) + (spacing / 2)
    const line = makeLine({x: x, y: viewBox.yMin}, {x: x, y: viewBox.height})
    canvas.appendChild(line)
  }
}

const main = document.getElementById("main");
main.style.height = "300px"

const canvas = document.createElementNS(svgns, "svg")
canvas.setAttribute("width", "100%")
canvas.setAttribute("height", "100%")
canvas.setAttribute("preserveAspectRatio", "xMidYMid slice")
canvas.style.border = "solid 2px #242930"

main.appendChild(canvas)

const bbox = canvas.getBoundingClientRect()
const scale = 100;
const aspectRatio = bbox.width / bbox.height

const viewBox = {xMin: 0, yMin: 0, width: scale * aspectRatio, height: scale}
const viewBoxStr = [
  viewBox.xMin, viewBox.yMin, viewBox.width, viewBox.height
].join(" ")

canvas.setAttribute("viewBox", viewBoxStr)
drawGrid(canvas, viewBox, 20)
{{< /highlight >}}
