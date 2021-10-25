import { ExtensionContext, Uri } from "vscode";
import { LanguageClientOptions } from "vscode-languageclient";

// Be sure to use the browser version of the client!
import { LanguageClient } from "vscode-languageclient/browser";

export function activate(context: ExtensionContext) {

    console.log("activating extension")

    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: "file", language: "plaintext" },
        ],
        outputChannelName: "Hello Language Server",
    }

    const path = Uri.joinPath(context.extensionUri, "dist/server.js")
    const worker = new Worker(path.toString())

    const client = new LanguageClient("hello-lsp-web", "Hello LSP", clientOptions, worker)
    context.subscriptions.push(client.start())

    client.onReady().then(() => {
        console.log("hello-lsp-web server is ready")
    })
}