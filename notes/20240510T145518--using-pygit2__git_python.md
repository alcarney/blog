---
title: Using pygit2
date: 2024-05-10T14:55:18+01:00
tags: git python
identifier: "20240510T145518"
---

# Using pygit2

`pygit2` can be used to manipulate a git repository from Python

## Creating a repo

To create a new repository

```python
>>> import pygit2
>>> repo = pygit2.init_repository('/path/to/repository', False)  # True implies 'bare' repository
```

## Creating a blob

A 'blob' is some content, typically from a file.

```python
>>> blob = repo.create_blob('print("Hello, World!")')
>>> blob
4648e701849ee7d52fb685111a7f0e4323505a35
```

## Creating a tree

Note, that a 'blob' is the content is contains nothing else, for it to become a file it must be included in some tree. This means that the same blob can be reused in multiple files!

```python
>>> from pygit2.enums import FileMode

>>> builder = repo.TreeBuilder()
>>> builder.insert('a', blob, FileMode.BLOB)
>>> builder.insert('b', blob, FileMode.BLOB)
>>> builder.insert('c', blob, FileMode.BLOB)

>>> tree = builder.write()  # at this point the tree becomes a real object under .git/
```

## Creating a commit

Once you have a complete tree, you likely want to commit it to the repo

```python
>>> author = pygit2.Signature("Alice", "alice@example.com")
>>> commit = repo.create_commit(
...     'refs/heads/main',  # where the commit is going
...     author,
...     author,  # this is the committer
...     "the commit message",
...     tree,
...     [],  # the parent commit(s), empty list here implies an initial commit
... )
```

## git checkout

At this point, the working directory is still empty, to sync the state with the commit we just made we need to do a git checkout. This seemed a little clunky but I was able to make the following work

```python
>>> ref = repo.lookup_reference_dwim('main')
>>> repo.checkout(ref)
```
