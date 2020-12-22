function clientDemo() {
    const svgns = "http://www.w3.org/2000/svg"

    const canvas = document.getElementById("client-demo-canvas")
    const target = document.getElementById("client-target")
    const position = document.getElementById("client-position")
    const posBox = document.getElementById("client-posbox")
    posBox.setAttribute("viewBox", "0 0 1 1")

    let bbox = canvas.getBoundingClientRect()
    const aspectRatio = bbox.width / bbox.height

    const height = 100
    const width = aspectRatio * height

    const viewBox = { minX: 0, minY: 0, width: width, height: height }
    const viewBoxStr = [
        viewBox.minX, viewBox.minY, viewBox.width, viewBox.height
    ].join(" ")

    canvas.setAttribute("viewBox", viewBoxStr)

    const circle = document.createElementNS(svgns, "circle")
    circle.setAttribute("cx", viewBox.width / 2)
    circle.setAttribute("cy", viewBox.height / 2)
    circle.setAttribute("r", 25)
    circle.setAttribute("fill", "var(--primary)")

    canvas.appendChild(circle)

    const point = document.createElementNS(svgns, "circle")
    point.setAttribute("cx", 0)
    point.setAttribute("cy", 0)
    point.setAttribute("r", 0.05)
    point.setAttribute("fill", "var(--primary)")

    posBox.appendChild(point)

    canvas.addEventListener("mousemove", (event) => {

        bbox = canvas.getBoundingClientRect()

        const x = event.clientX - bbox.left
        const y = event.clientY - bbox.top

        position.innerText = `(${x.toFixed(0)}px, ${y.toFixed(0)}px)`
        target.innerText = `<${event.target.tagName}>`

        point.setAttribute("cx", x / bbox.width)
        point.setAttribute("cy", y / bbox.height)
    })

}

clientDemo()
