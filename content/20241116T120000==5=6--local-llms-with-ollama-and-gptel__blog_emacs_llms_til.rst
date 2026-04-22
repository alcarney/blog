:title: Local LLMs with Ollama and gptel
:identifier: 20241116T120000
:signature: 5=6
:date: 2024-11-16
:tags: blog, emacs, llms, til
:author: Alex Carney
:language: en

Local LLMs with Ollama and gptel
================================

.. container:: post-teaser

   LLMs don't look like they're going to go away anytime soon, so I may as well start playing around with them.
   Since I am also using Emacs more and more it also makes sense to try using it as the interface to any models.

Installing Ollama
-----------------

I'm not terribly interested in messing around with API keys, rate limits and/or billing that seems to come with any of the hosted models.
Thankfully Bluefin/Aurorae `makes it easy <https://docs.projectbluefin.io/ai#local-ai>`__ to get `Ollama <https://github.com/ollama/ollama>`__ up and running locally.

.. code-block:: console

   $ ujust ollama install
   $ brew install ollama
   $ systemctl --user start ollama

This will make the Ollama API available locally on ``http://localhost:11434``.

.. tip::

   Bluefin/Aurorae also make it easy to spin up an instance of the `Open Web UI <https://docs.openwebui.com/>`__ if you want a Chat GPT style interface

   .. code-block:: console

      $ ujust ollama install-open-webui
      $ systemctl --user start ollama-web

   Once everything has spun up, the interface will be available locally on ``http://localhost:8080``


Choosing a Model
----------------

Installing Ollama by itself however does not give you much, you now have the infrastructure in place to run models and interact with them but it does not come with any models out of the box.

Unfortunately, there are so many models to choose from!
I have no idea how to pick between them and most of the benchmark scores are meaningless to me.

However, any model I run will have to run on my CPU so I can let my hardware constraints pick for me.
So looking for something small... ah! `llama3.2:3b <https://ollama.com/library/llama3.2>`__, it's a new-ish model, 3b parameters and only a 2GB download, seems as good a choice as any. - Any AI is better then no AI... right? 😅

.. code-block:: console

   $ ollama pull llama3.2

This was all I needed to do in order for the model to show up in Open Web UI however, as I mentioned in the intro I'm interested in interacting with these models via Emacs.

Installing gptel
----------------

If you search for packages that involve AI in some way you will quickly discover a lot of them!
However, stumbling across this `video demo <https://www.youtube.com/watch?v=bsRnh_brggM>`__ of `gptel <https://github.com/karthink/gptel>`__ was enough to sell me on it.

All it takes is a few lines of elisp to point ``gptel`` at the local Ollama API.

.. code-block:: elisp

   (package-install 'gptel)
   (setq gptel-model 'llama3.2:latest
         gptel-backend (gptel-make-ollama "Ollama"
                         :host "localhost:11434"
                         :stream t
                         :models '(llama3.2:latest)))

And I can now call ``M-x gptel`` to open a dedicated chat buffer with the ``llama3.2`` model.
Now all I have to do is figure out what these models are actually useful for!
