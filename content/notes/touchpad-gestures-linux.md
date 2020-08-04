+++
title = "Enabling Touchpad Gestures on Linux"
tags = ["linux"]
description = "Enabling multi-finger touchpad gestures on linux."
+++

Turns out this was rather easy thanks to
[libinput-gestures](https://github.com/bulletmark/libinput-gestures)

## Installation

Using arch linux this process was made nice and simple thanks to the AUR package

{{< highlight sh >}}
$ yaourt -S libinput-gestures
{{< /highlight >}}

## Configuration

libinput-gestures comes with its own configuration file
`/etc/libinput-gestures.conf` that's well documented and has a straightforward
syntax. Below is my current configuration

{{< highlight conf >}}
gesture swipe up            xdotool key ctrl+F9
gesture swipe down          xdotool key alt+space
gesture swipe left          _internal ws_down
gesture swipe right         _internal ws_up
{{< /highlight >}}


Each gesture works with either 3 or 4 fingers and executes the command on the
right when triggered. Each direction is mapped to the following command.

- up: Sends the key combination `ctrl+F9` which in KDE presents all the windows
  on the current desktop
- down: Sends the key combination `alt+space` which I have set KDE to open
  Plasma Search
- left: Go to the previous workspace
- right: Go to the next workspace