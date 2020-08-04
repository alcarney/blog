+++
title = "Installing npm packages globally without root"
description = "A few tweaks to configure npm to use the user's home for package installs"
tags = ["npm", "js"]
+++

1. Create a folder for global packages to be install into

   {{< highlight sh >}}
   $ mdkir "${HOME}/.npm-packages"
   {{< /highlight >}}

2. Tell `npm` to use this folder

   {{< highlight sh >}}
   $ npm config set prefix "${HOME}/.npm-packages"
   {{< /highlight >}}

3. Add the corresponding `${HOME}/.npm-packages/bin` folder to your `PATH`