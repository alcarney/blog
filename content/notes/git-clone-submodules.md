---
description: Collections of tips and tricks I've gathered on working with Git
tags:
- git
links:
- url: https://stackoverflow.com/questions/3796927/how-to-git-clone-including-submodules
  name: Cloning Git Submodules
title: Notes on Git
---

## Submodules

To clone a repo that contains submodules we can run the following command

```sh
$ git clone --recurse-submodules <repo-url>
```

Or if you've already cloned a repo only to later discover that it contained
submodules

```sh
$ git submodule update --init --recursive
```
