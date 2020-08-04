+++
title = "Custom Jupyter Kernels"
description = "\"Publishing\" multiple Python environments to use within Jupyter"
tags = ["python", "jupyter"]
links = ["https://ipython.readthedocs.io/en/stable/install/kernel%5Finstall.html#kernels-for-different-environments"]
+++

It's possible to create custom Python environments for use within a Jupyter
notebook without having to run a jupyter server from each of them. The following
steps will allow you to have a single jupyter server running and have it use a
variety of Python environments in its notebooks

1.  Create a virtualenv and install any packages that you want available
2.  `pip install ipykernel`
3.  `ipykernel install --user --name <envname> --display-name <display name>`

Then the new environment should become available in the Change kernel menu