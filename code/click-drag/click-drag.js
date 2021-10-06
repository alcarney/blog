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
const viewBox = { minX: 0, minY: 0, width: width, height: height }

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
circle.addEventListener("mousedown", (_) => { clicked = true })
circle.addEventListener("mouseup", (_) => { clicked = false })
canvas.addEventListener("mouseleave", (_) => { clicked = false })