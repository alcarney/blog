Running Locally
---------------

It's possible to test your web extension by serving a local copy that the web
version of VSCode can then pick up and install.

#. Install dependencies

   .. code-block:: console

      $ npm install

#. Compile both the client and server components of the extension with webpack.
   Using the ``watch`` script means that webpack will automatically recompile the extension
   whenever you make changes.

   .. code-block:: console

      $ npm run watch 

#. In a separate terminal, spin up a web server to serve your extension 

   .. code-block:: console

      $ npm run serve 

      > hello-lsp-web@ serve /home/alex/Projects/blog/code/hello-lsp-web
      > npx serve --cors -l 5000

      npx: installed 88 in 6.613s

      ┌──────────────────────────────────────────────────┐
      │                                                  │
      │   Serving!                                       │
      │                                                  │
      │   - Local:            http://localhost:5000      │
      │   - On Your Network:  http://192.168.0.31:5000   │
      │                                                  │
      │   Copied local address to clipboard!             │
      │                                                  │
      └──────────────────────────────────────────────────┘

#. I don't fully understand this step, but running this command in a third terminal window
   somehow makes the local web server we spun up in the previous step, visible to the web
   version of VSCode.

   .. code-block:: console

      $ npm run tunnel

      > hello-lsp-web@ tunnel /home/alex/Projects/blog/code/hello-lsp-web
      > npx localtunnel -p 5000

      npx: installed 22 in 3.043s
      your url is: https://xxxx-yyyy-zzzz.loca.lt

#. Actually, before opening up the web version of VSCode, first open the ``https://...local.it`` 
   URL from the previous step in your web browser. You should see a web page like this

   .. figure:: /code/hello-lsp-web/resources/tunnel_warning.png

   Click the ``Click to Continue`` button to enable the tunnel.

#. Now open up `VSCode in your browser <https://vscode.dev/github/alcarney/blog>`_ and 
   once it has loaded. Bring up the command palette with :kbd:`F1` and pick the
   :guilabel:`Developer: Install Web Extension...` command.

   .. figure:: /code/hello-lsp-web/resources/install_extension.png

#. Finally, paste in your ``https://...loca.lt`` URL and click install. 
