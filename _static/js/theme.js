function buildTocTree(tocTree, navRoot, parents) {
    if (navRoot.tagName !== "UL") {
        console.error(`Expected 'ul' element, got ${navRoot.tagName.toLowerCase()}`)
    }

    for (let element of Array.from(navRoot.children)) {
        const link = element.querySelector("a")
        const linkName = link.getAttribute("href").replace("#", "")
        let nodes = [...parents, link]

        tocTree.set(linkName, nodes)

        const children = element.querySelector("ul")
        if (children) {
            let newParents = [...parents, children]
            buildTocTree(tocTree, children, newParents)
        }
    }
}

function highlightCurrentSection(tocTree, navRoot, documentSections) {
    let currentId

    for (let section of Array.from(documentSections)) {
        const bbox = section.getBoundingClientRect()
        if (bbox.top > 55) {
            break
        }

        currentId = section.getAttribute("id")
    }
    console.debug("current section - ", currentId)

    const subSections = navRoot.querySelectorAll("ul")
    subSections.forEach(section => section.className = "") // was "hidden"

    const links = navRoot.querySelectorAll("a[href^='#']")
    links.forEach(link => link.className = "")


    if (!tocTree.has(currentId)) {
        return
    }

    let navElements = [...tocTree.get(currentId)]

    let link = navElements.pop()

    // Style the link to indicate it's the current section.
    link.className = "current"

    // Expand all parent nodes to reveal the link
    navElements.forEach(element => element.className = "")

    // Also expand the next level down - if any
    const children = link.parentElement.querySelector("ul")
    if (children) {
        children.className = ""
    }

}

const onScrollCallbacks = []


function main() {
    const localToc = document.querySelector("#localtoc")
    console.debug("localtoc - ", localToc)
    if (localToc) {
        const documentSections = document.querySelectorAll("article section")
        const navRoot = localToc.querySelector("a[href='#'] + ul")

        console.debug("sections - ", documentSections)
        console.debug("navroot - ", navRoot)

        const navTitle = localToc.querySelector("a[href='#']")
        navTitle.innerHTML = "Contents"

        if (!navRoot) {
            localToc.className = "hidden"

        } else {

            let tocTree = new Map()
            buildTocTree(tocTree, navRoot, [])
            console.debug("toctree - ", tocTree)

            highlightCurrentSection(tocTree, navRoot, documentSections)
            onScrollCallbacks.push(() => highlightCurrentSection(tocTree, navRoot, documentSections))
        }
    }

  document.querySelector('main').addEventListener('scroll', (_) => {
    onScrollCallbacks.forEach(callback => callback())
  })

}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
} else {
    main();
}
