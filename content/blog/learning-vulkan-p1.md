+++
title = "Learning Vulkan: Enumerating Physical Devices"
author = ["Alex Carney"]
description = "Enumerating Vulkan compatible physical devices"
date = 2020-01-01T21:00:00+01:00
tags = ["c", "vulkan", "graphics"]
draft = true
+++

Being an API for talking to various GPU and other compute devices every Vulkan
program starts off by looking for an appropriate [physical device][vkphysicaldevice]
to use. In this post I write a little C program that simply initialises the Vulkan
API and lists out the available devices in the system.

{{< highlight plain >}}
$ vkdevice
Device Name:            Intel(R) HD Graphics 520 (Skylake GT2)
  Type:                 Integrated GPU
  Vendor ID:            32902
  Device ID:            6422
  API Version:          v1.1.102
  Driver Version:       v19.3.1
{{< /highlight >}}

<!--more-->

> This is part of my "Learning Vulkan" series why I try to figure how to use
> Vulkan to explore various concepts in graphics programming. As mentioned in
> the [Overview]({{< relref "learning-vulkan-p0.md" >}}) I don't necessarily
> know what I'm doing!

## Setup

Unlike Python which has tools like `pip` and `venv` which are used to manage
dependencies and create isolated envrionments, C projects (as far as I know)
require the environment of your development machine to be "just right". This means
details such as the host operating system and its libraries are more important
than normal.

Since this series is a learning excercise, being able to compile and run code
across multiple systems is not a huge concern of mine right now. But here is a rough
overview of what is required to build this project...

I'm running Arch Linux with `gcc` and `make` installed along with the following
Vulkan related packages

{{< highlight sh >}}
$ pacman -Q | grep vulkan
vulkan-extra-layers 1.1.130+10614+a70d5d17e-1
vulkan-headers 1:1.1.130-1
vulkan-html-docs 1:1.1.130-1
vulkan-icd-loader 1.1.130-1
vulkan-intel 19.3.1-1
vulkan-man-pages 1:1.0.38-1
vulkan-trace 1.1.130+10614+a70d5d17e-1
vulkan-validation-layers 1.1.130-1
{{< /highlight >}}

I'm not sure however which of these are essential for the code contained in this
post.

### Project Structure

I'm intending over the course of this series to build up a repository of Vulkan
examples/utilities and since the API  has a reputation of being verbose I'll be looking
to reuse as much code as I can! So with that in mind I have opted for the following
project structure

{{< highlight sh >}}
$ tree -a --dirsfirst
.
├── bin
│   └── vkdevice
├── src
│   ├── vkdevice.c
│   └── vkdevice.o
├── .gitignore
└── Makefile
{{< /highlight >}}

Nothing ground breaking, a `src/` folder to hold the source and intermediate build files,
`bin/` to hold all the compiled programs and a plain `Makefile` to orchestrate the whole
thing.

### The Makefile

I know that there are tools such as [CMake][cmake] and [Autoconf][autoconf] that are
probably preferable to a plain Makefile since they can be used to abstract over some
differences between platforms. However since I'm not familiar with them and want to
focus on learning Vulkan I'm opting for a simpler approach to start out with.

{{< highlight make >}}
CC = gcc
CFLAGS = -Wall -Wextra
LDFLAGS = -lvulkan
{{< /highlight >}}

Here I'm declaring that I'm using the `gcc` compiler, the `CFLAGS` variable contains any
flags that should passed to compile steps (at the moment this just enables some compiler
warnings). Finally `LDFLAGS` contains any flags related to linking, `-lvulkan` tells the
linker to link our program against the Vulkan SDK.

{{< highlight make >}}
.PHONY: default clean
default: vkdevice
clean:
    rm src/*.o bin/*
{{< /highlight >}}

Next I define the `default` target to be `vkdevice` so that I can just run `make` and
have it build the project. Then there's a `clean` target so that it's easy to recompile
everything from scratch. Declaring both `default` and `clean` to be
[phony targets][phony-target] I think means we're tellling `make` not to look for
matching files on the filesystem.

{{< highlight make >}}
%.o: %.c
    $(CC) -c $(CFLAGS) $< $@

VKDEVICE = src/vkdevice.o
vkdevice:
    $(CC) $(LDFLAGS) $(VKDEVICE) -o bin/vkdevice
{{< /highlight >}}

Last but not least we get to the main part of the `Makefile`. First there is a generic
[pattern rule][pattern-rule] that instructs `make` on how to convert any `.c` file into
an `.o` file making use of any of the compiler flags defined earlier. This allows the
`Makefile` to be extended to compile each program we write by declaring a target that
links the relevant object files (as defined by `VKDEVICE`) into an executable.

Then we can compile the project by calling `make` from the same directory as the
`Makefile`

{{< highlight sh >}}
$ make
gcc -c -Wall -Wextra src/vkdevice.c -o src/vkdevice.o
gcc -lvulkan src/vkdevice.o -o bin/vkdevice
{{< /highlight >}}

## Creating an instance

With all the housekeeping out of the way, time to dive into the code which starts in
a fairly standard way with us including all the header files we need.

{{< highlight c >}}
#include <stdio.h>
#include <vulkan/vulkan.h>
{{< /highlight >}}

Then

{{< highlight c >}}
int main() {

    VkApplicationInfo app_info = {
        .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
        .pApplicationName = "vkDevice Info",
        .applicationVersion = 0x010000,
        .pEngineName = "vkEngine",
        .engineVersion = 0x010000,
        .apiVersion = VK_API_VERSION_1_1,
    };

    VkInstanceCreateInfo vk_info = {
        .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        .pApplicationInfo = &app_info,
    };

    VkInstance vk = NULL;
    VkResult res = vkCreateInstance(&vk_info, NULL, &vk);

    if (res != VK_SUCCESS) {
        fprintf(stderr, "Unable to create VkInstance!\n");
        return 0;
    }

    printf("Vulkan instance created!\n");

    vkDestroyInstance(vk, NULL);
    return 0;
}
{{< /highlight >}}

[autoconf]: https://www.gnu.org/software/autoconf/
[cmake]: https://cmake.org/
[pattern-rule]: https://www.gnu.org/software/make/manual/make.html#Pattern-Rules
[phony-target]: https://www.gnu.org/software/make/manual/make.html#Phony-Targets
[vkphysicaldevice]: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/VkPhysicalDevice.html