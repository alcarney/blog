function offsetDemo() {

    const svgns = "http://www.w3.org/2000/svg"
    const canvas = document.getElementById("offset-demo-canvas")
    const target = document.getElementById("offset-target")
    const position = document.getElementById("offset-position")
    const posBox = document.getElementById("offset-posbox")
    posBox.setAttribute("viewBox", "0 0 1 1")

    let bbox = canvas.getBoundingClientRect()
    const aspectRatio = bbox.width / bbox.height

    const height = 100
    const width = aspectRatio * height

    const viewBox = {minX: 0, minY: 0, width: width, height: height}

    const viewBoxStr = [
        viewBox.minX, viewBox.minY, viewBox.width, viewBox.height
    ].join(" ")

    canvas.setAttribute("viewBox", viewBoxStr)

    const circle = document.createElementNS(svgns, "circle")
    circle.setAttribute("cx", viewBox.width / 2)
    circle.setAttribute("cy", viewBox.height / 2)
    circle.setAttribute("r", 25)
    circle.setAttribute("fill", "#57cc8a")

    canvas.appendChild(circle)

    const point = document.createElementNS(svgns, "circle")
    point.setAttribute("cx", 0)
    point.setAttribute("cy", 0)
    point.setAttribute("r", 0.05)
    point.setAttribute("fill", "#57cc8a")

    posBox.appendChild(point)

    canvas.addEventListener("mousemove", (event) => {

        const x = event.offsetX
        const y = event.offsetY

        bbox = canvas.getBoundingClientRect()

        const u = x / bbox.width
        const v = y / bbox.height

        position.innerText = "(" + x + "px, " + y + "px)"
        target.innerText = "<" + event.target.tagName + ">"

        point.setAttribute("cx", u)
        point.setAttribute("cy", v)
    })
}

offsetDemo()
