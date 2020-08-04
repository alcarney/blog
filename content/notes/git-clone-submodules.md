+++
title = "Cloning Git Repos with Submodules"
description = "Working with git repositories that include submodules."
tags = ["git"]
links = ["https://stackoverflow.com/questions/3796927/how-to-git-clone-including-submodules"]
+++

To clone a repo that contains submodules we can run the following command

{{< highlight sh >}}
$ git clone --recurse-submodules <repo-url>
{{< /highlight >}}

Or if you've already cloned a repo only to later discover that it contained submodules

{{< highlight sh >}}
$ git submodule update --init --recursive
{{< /highlight >}}
