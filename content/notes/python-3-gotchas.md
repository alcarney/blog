+++
description = "As the legacy of Python 3.x grows I forget how new some features are"
tags = ["python"]
title = "Python 3.x Gotchas"
+++

## Beware pathlib on 3.5

While `pathlib` exists in Python 3.5, it's not fully integrated yet. Passing a
`pathlib.Path` object to the built-in `open` method will result in a surprising error

{{< highlight python >}}
TypeError: invalid file: PosixPath('path/to/file.txt')
{{< /highlight >}}

In this situation it's better to call the path's `open()` method instead.
