---
title: Custom Jupyter Kernels
date: 2023-03-23T23:26:18+00:00
tags:
  - python
  - jupyter
identifier: 20230323T232618
---

# Custom Jupyter Kernels

It's possible to create custom Python environments for use within a Jupyter
notebook without having to run a jupyter server from each of them. The following
steps will allow you to have a single jupyter server running and have it use a
variety of Python environments in its notebooks

1.  Create a virtualenv and install any packages that you want available
2.  ``pip install ipykernel``
3.  ``ipykernel install --user --name <envname> --display-name <display name>``

Then the new environment should become available in the Change kernel menu

[IPython: Kernels for different environments](https://ipython.readthedocs.io/en/stable/install/kernel%5Finstall.html#kernels-for-different-environments)
