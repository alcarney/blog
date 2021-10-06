.. post:: 2018-10-12
   :tags: stylo, python
   :author: me
   :language: en
   :excerpt: 3
   :image: 1

.. description = "Introducing the new community gallery for stylo"

Introducing Stylo Doodles!
==========================

A few weeks back at `PyConUK`_ I gave my first `lighting talk`_
at a conference. During that talk I spoke publically about `stylo`_ for
the first time. Stylo is a Python library that I have been working on for just
over a year and a half and it aims to make the creation of images easier by
bringing together ideas from programming and mathematics.

Version `0.6.0`_ was recently released which included the first feature
that wasn't written by me! It's very exciting not only to see other people
starting to take an interest in the project but taking the time to make a
contribution!

Now that stylo seems to be getting to the point that it might me useful to
other people wouldn't it be great if there was a community driven example
gallery that people could get inspired by? - Well now there is! And it's
called `Stylo Doodles`_

.. figure:: /images/stylo-doodles.png
   :align: center


.. <!--more-->

All the examples are written as a `Jupyter Notebook`_ and can be submitted to the
gallery by opening a pull request against the stylo-doodles `repository`_. A small
python application is then run that builds the website and pushes the update to
the live website.


Current Features
----------------

The gallery website is very new but it currently has the following features

-   All images are displayed in a grid on the homepage with the order randomly
    chosen each time the website is built.
-   Each image has its own page (as shown above) which displays the full
    resolution image along with information about the author, image and the
    version of stylo used to generate it.
-   The source code from the notebook is extracted and is also displayed
    alongside the image.
-   You can also play around with any example **live in your browser** if you
    follow the `binder`_ link in the repository's README.


Adding Your Own Example
-----------------------

If you have an image that you would like to share there are only a couple of
things you need to do:

1.  Your image **must** be stored in a variable called ``image``. The build process
    will `import your notebook`_ as a Python module and look for a variable called
    ``image``.

2.  You also need to provide some additional information to the build system
    about your example in the form of a Python dictionary. This dictionary
    **must** be called ``info`` and it must be in **very first cell of the notebook**

    .. code-block:: python

       info = {
            "title": "Jack-O-Lantern",
            "author": "Alex Carney",
            "github_username": "alcarney",
            "stylo_version": "0.6.0",
            "dimensions": (1920, 1080)
       }

    The ``stylo_version`` field should be set to the value of ``stylo.__version__``
    at the time you created your image. The ``dimensions`` is tuple of the form
    ``(width, height)`` and will be used by the build system to determine the size
    of the image (in pixels) when it renders the full size copy for its detail
    page.

3.  Once your example is ready open a pull request adding your notebook to the
    ``notebooks/`` folder to the repository.

Be sure to check out the existing `examples`_ to use as a guide or drop by the
stylo `Gitter`_ room if you get stuck we'll be more than happy to help!


Future Developments
-------------------

Stylo Doodles is far from finished aside from adding examples there are many
more things that could be added to the website:

-   **User profiles:** A page for every author, which lists the examples they
    have contributed to the gallery.

-   **Search**: As the number of images grow users would probably want to be able
    to tag their images and be able to narrow down the list of images on the
    homepage.

-   **Recently Added:** Since the order of the homepage is random, as the number
    of images increases the chance of a new image being buried at the bottom will
    also increase, it would be good to have a way of sorting the images by date
    added.

-   **Descriptions:** Jupyter Notebooks support more than just code. Cells
    containing markdown can be placed in between code cells to provide extra
    context and explanation. It would be great if we could include these on the
    site as well.

If you are looking for a web based python project to get involved with this
would be a great one to get started with and I would be more than happy to have
a few contribuitors to work on this (or even stylo itself!) with me.

.. _0.6.0: https://alcarney.github.io/stylo/changes.html
.. _Gitter: https://gitter.im/stylo-py/Lobby
.. _Jupyter Notebook: https://jupyter.org
.. _PyConUK: https://2018.pyconuk.org/
.. _Stylo Doodles: https://alcarney.github.io/stylo-doodles
.. _binder: https://mybinder.org/v2/gh/alcarney/stylo-doodles/master
.. _examples: https://github.com/alcarney/stylo-doodles/tree/master/notebooks
.. _import your notebook: https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Importing%2520Notebooks.html
.. _lighting talk: https://youtu.be/F5jSUJVymXk?t=3480
.. _repository: https://github.com/alcarney/stylo-doodles
.. _stylo: https://github.com/alcarney/stylo
