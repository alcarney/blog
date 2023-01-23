function growShrinkProfile(profileElement, referenceElement) {
    const bbox = referenceElement.getBoundingClientRect()
    const className = bbox.top < 0 ? "small-profile" : "full-profile"
    profileElement.className = className
}

function activateShadow(navElement, referenceElement) {
    const bbox = referenceElement.getBoundingClientRect()
    if (bbox.top < 0) {
        navElement.classList.add("shadow-md")
    } else {
        navElement.classList.remove("shadow-md")
    }
}

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
    const ulHidden = "hidden"
    const ulVisible = "ml-2 border-l"
    const linkNormal = "pl-2 border-l-4 border-white dark:border-gray-800"
    const linkHighlighted = "pl-2 text-green-600 border-l-4 border-green-600"

    for (let section of Array.from(documentSections)) {
        const bbox = section.getBoundingClientRect()
        if (bbox.top > 30) {
            break
        }

        currentId = section.getAttribute("id")
    }
    console.debug("current section - ", currentId)

    const subSections = navRoot.querySelectorAll("ul")
    subSections.forEach(section => section.className = ulHidden)

    const links = navRoot.querySelectorAll("a[href^='#']")
    links.forEach(link => link.className = linkNormal)


    if (!tocTree.has(currentId)) {
        return
    }

    let navElements = [...tocTree.get(currentId)]

    let link = navElements.pop()

    // Style the link to indicate it's the current section.
    link.className = linkHighlighted

    // Expand all parent nodes to reveal the link
    navElements.forEach(element => element.className = ulVisible)

    // Also expand the next level down - if any
    const children = link.parentElement.querySelector("ul")
    if (children) {
        children.className = ulVisible
    }

}

const onScrollCallbacks = []

// The element the page uses to decide whether to grow or shrink the profile image.
const referenceElement = document.querySelector("#content")
const profileElement = document.querySelector("#profile-card")

if (profileElement) {
    growShrinkProfile(profileElement, referenceElement)
    onScrollCallbacks.push(() => growShrinkProfile(profileElement, referenceElement))
}

const localToc = document.querySelector("#localtoc")
console.debug("localtoc - ", localToc)
if (localToc) {
    const documentSections = document.querySelectorAll("section")
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

window.addEventListener('scroll', (_) => {
    onScrollCallbacks.forEach(callback => callback())
})
