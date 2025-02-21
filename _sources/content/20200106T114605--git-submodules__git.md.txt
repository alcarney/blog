---
title: Submodules
date: 2020-01-06T11:46:05+00:00
tags: git
identifier: 20200106T114605
---

# Submodules

## Adding

To add a new submodule to a repo, use the following command

```
$ git submodule add <repo-url> path/to/folder
```

## Cloning

To clone a repo that contains submodules we can run the following command
[Source](https://stackoverflow.com/questions/3796927/how-to-git-clone-including-submodules)

```
$ git clone —-recurse-submodules <repo-url>
```

Or if you’ve already cloned a repo only to later discover that it contained submodules

```
$ git submodule update —-init —-recursive
```

## Updating

To update a submodule

```
$ cd module/
module/ $ git checkout <ref>
module/ $ git pull
module/ $ cd ..

$ git add module
$ git commit -m 'Update submodule'
```
