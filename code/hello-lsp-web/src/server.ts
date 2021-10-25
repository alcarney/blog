importScripts("https://cdn.jsdelivr.net/pyodide/v0.18.1/full/pyodide.js")

async function initPyodide() {

    console.log("Initing pyodide.")

    /* @ts-ignore */
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.18.1/full/"
    })

    return pyodide
}

const pyodideReady = initPyodide()

onmessage = async (event) => {
    console.log(`Client message:`, event.data)

    if (event.data.method === "initialize") {
        postMessage({
            jsonrpc: "2.0",
            id: event.data.id,
            result: {
                serverInfo: { name: "Hello, LSP" },
                capabilities: {}
            }
        })
    }

    let pyodide = await pyodideReady
    console.log(pyodide.runPython("import sys;sys.version"))
}