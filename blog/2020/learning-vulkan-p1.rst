.. post:: 2020-01-08
   :tags: c, vulkan, graphics
   :author: Alex Carney
   :language: en
   :excerpt: 2

.. description = "Enumerating Vulkan compatible physical devices"
.. series = ["Learning Vulkan"]

Learning Vulkan: Enumerating Physical Devices
=============================================

Being an API for talking to GPUs and other compute devices every Vulkan
program starts off by looking for an appropriate `physical device`_
to use. In this post I write a little C program that initialises the Vulkan
API and lists out the available devices in the system.

.. code-block:: none

   $ vkdevice
   Device Name:            Intel(R) HD Graphics 520 (Skylake GT2)
     Type:                 Integrated GPU
     Vendor ID:            32902
     Device ID:            6422
     API Version:          v1.1.102
     Driver Version:       v19.3.1

.. <!--more-->

.. note::

   This is part of my "Learning Vulkan" series where I try to figure how to use
   Vulkan to explore various concepts in graphics programming. As mentioned in
   the :doc:`Overview </blog/2020/learning-vulkan-p0>` I don't necessarily
   know what I'm doing!

Setup
-----

Unlike Python which has tools like ``pip`` and ``venv`` to manage
dependencies and development environments, C projects (as far as I know)
require the environment of your development machine to be "just right". This means
details such as the host operating system and its libraries are more important
than normal.

Since this series is a learning exercise, being able to compile and run code
across multiple systems is not a huge concern of mine right now. But here is a rough
overview of what is required to build this project...

I'm running Arch Linux with ``gcc`` and ``make`` installed along with the following
Vulkan related packages

.. code-block:: console

   $ pacman -Q | grep vulkan
   vulkan-extra-layers 1.1.130+10614+a70d5d17e-1
   vulkan-headers 1:1.1.130-1
   vulkan-html-docs 1:1.1.130-1
   vulkan-icd-loader 1.1.130-1
   vulkan-intel 19.3.1-1
   vulkan-man-pages 1:1.0.38-1
   vulkan-trace 1.1.130+10614+a70d5d17e-1
   vulkan-validation-layers 1.1.130-1

I'm not sure however which of these are essential for the code contained in this
post.

Project Structure
^^^^^^^^^^^^^^^^^

I'm intending over the course of this series to build up a repository of Vulkan
examples/utilities and since the API  has a reputation of being verbose I'll be looking
to reuse as much code as I can! So with that in mind I have opted for the following
project structure

.. code-block:: console

   $ tree -a --dirsfirst
   .
   ├── bin
   │   └── vkdevice
   ├── src
   │   ├── vkdevice.c
   │   └── vkdevice.o
   ├── .gitignore
   └── Makefile

Nothing ground breaking, a ``src/`` folder to hold the source and intermediate build files,
``bin/`` to hold all the compiled programs and a plain ``Makefile`` to orchestrate the whole
thing.

The Makefile
^^^^^^^^^^^^

I know that there are tools such as `CMake`_ and `Autoconf`_ that are
probably preferable to a plain Makefile since they can be used to abstract over some
differences between platforms. However since I'm not familiar with them and want to
focus on learning Vulkan I'm opting for a simpler approach to start out with.

.. code-block:: make

   CC = gcc
   CFLAGS = -Wall -Wextra
   LDFLAGS = -lvulkan

Here I'm declaring that I'm using the ``gcc`` compiler, the ``CFLAGS`` variable contains any
flags that should passed to compile steps (at the moment this just enables some compiler
warnings). Finally ``LDFLAGS`` contains any flags related to linking, ``-lvulkan`` tells the
linker to link our program against the Vulkan SDK.

.. code-block:: make

   .PHONY: default clean
   default: vkdevice
   clean:
      rm src/*.o bin/*

Next I define the ``default`` target to be ``vkdevice`` so that I can just run ``make`` and
have it build the project. Then there's a ``clean`` target so that it's easy to recompile
everything from scratch. Declaring both ``default`` and ``clean`` to be `phony targets`_ I
think means we're telling ``make`` not to look for matching files on the filesystem.

.. code-block:: make

   %.o: %.c
      $(CC) -c $(CFLAGS) $< $@

   VKDEVICE = src/vkdevice.o
   vkdevice:
      $(CC) $(LDFLAGS) $(VKDEVICE) -o bin/vkdevice

Last but not least we get to the main part of the ``Makefile``. First there is a generic
`pattern rule`_ that instructs ``make`` on how to convert any ``.c`` file into
an ``.o`` file making use of any of the compiler flags defined earlier. This allows the
``Makefile`` to be extended to compile each program we write by declaring a target that
links the relevant object files (as defined by ``VKDEVICE``) into an executable.

Then we can compile the project by calling ``make`` from the same directory as the
``Makefile``

.. code-block:: console

   $ make
   gcc -c -Wall -Wextra src/vkdevice.c -o src/vkdevice.o
   gcc -lvulkan src/vkdevice.o -o bin/vkdevice

Creating an instance
--------------------

With all the housekeeping out of the way, time to dive into the code which starts in
a fairly standard way with us including all the header files we need.

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <vulkan/vulkan.h>

   int main() {
      // Insert code...
   }

Then we start by filling out the ``VkApplicationInfo`` and ``VkInstanceCreateInfo`` structs.
Unsurprisingly the first is used to provide information about our application such as
the version of the API we wish to use. The application name and version fields are
arbitrary and can be set to whatever we like.

.. code-block:: c

   VkApplicationInfo app_info = {
      .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
      .pApplicationName = "vkDevice Info",
      .applicationVersion = VK_MAKE_VERSION(1,0,0),
      .apiVersion = VK_API_VERSION_1_1,
   };

   VkInstanceCreateInfo vk_info = {
      .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
      .pApplicationInfo = &app_info,
   };

The ``vk_info`` struct is then be used to create the instance.

.. code-block:: c

   VkInstance vk = NULL;
   VkResult res = vkCreateInstance(&vk_info, NULL, &vk);

   if (res != VK_SUCCESS) {
      fprintf(stderr, "Unable to create VkInstance!\n");
      return 0;
   }

We also have to be sure to destroy the instance once we have finished with it

.. code-block:: c

   // Code omitted...

   cleanup_instance:
      vkDestroyInstance(vk, NULL);

   return 0;

This is me attempting to apply `this`_ rule from the Linux kernel style
guide to help manage resources through the lifetime of the program.

Listing Devices
---------------

Now that we have an instance we can start querying the API for the physical devices that
are in the system. The issue is however - we don't know how many devices the system has!
To get around this we first have to call ``vkEnumeratePhysicalDevices`` with a ``NULL``
pointer, it will then mutate the `count` variable that we give to be equal to the number
of available devices.

Note that we skip straight to the ``cleanup_instance`` label we defined earlier if this
step fails.

.. code-block:: c

   uint32_t count = 0;
   res = vkEnumeratePhysicalDevices(vk, &count, NULL);
   if (res != VK_SUCCESS) {
      fprintf(stderr, "Unable to enumerate physical devices\n");
      goto cleanup_instance;
   }

Next we attempt to allocate enough memory to store each of the devices in an array.

.. code-block:: c

   VkPhysicalDevice* physical_devices = malloc(count * sizeof(VkPhysicalDevice));
   if (physical_devices == NULL) {
      fprintf(stderr, "Unable to enumerate physical devices\n");
      goto cleanup_instance;
   }

Finally with the array allocated we can call ``vkEnumeratePhysicalDevices`` a second time
to populate it. Notice how this time the error path has to jump to the ``cleanup_devices``
label so that we can be sure to ``free`` the newly allocated memory.

.. code-block:: c

   res = vkEnumeratePhysicalDevices(vk, &count, physical_devices);
   if (res != VK_SUCCESS) {
      fprintf(stderr, "Unable to enumerate physical devices\n");
      goto cleanup_devices;
   }

   // Code omitted...

   cleanup_devices:
      free(physical_devices);
      physical_devices = NULL;

   cleanup_instance:
      vkDestroyInstance(vk, NULL);


.. admonition:: Editor's Note

   As I was writing this post I looked up the `documentation`_
   for ``vkEnumeratePhysicalDevices`` and noticed that there is a different way to
   approach this section. We could've instead decided on a fixed size array

   .. code-block:: c

      uint32_t MAX_DEVICES = 4;
      VkPhysicalDevice physical_devices[MAX_DEVICES];
      res = vkEnumeratePhysicalDevices(vk, &MAX_DEVICES, physical_devices);

   In this situation the function will return up to ``MAX_DEVICES`` and if there more
   devices than can fit in the array then ``res`` will be set to ``VK_INCOMPLETE`` giving
   us the option to try again with a larger array.

   This creates a dilemma - which approach is better? 🤔

Device Properties
-----------------

It turns out that a ``VkPhysicalDevice`` on its own is rather useless since it doesn't
carry any information about itself. In order to find out more about what the device is
and what features of the API it supports you need to call additional functions such as

- `vkGetPhysicalDeviceProperties`_
- `vkGetPhysicalDeviceImageFormatProperties`_
- `vkGetPhysicalDeviceQueueFamilyProperties`_
- and many more!!

Typically as part of your program's setup you would call a number of these to gather
information about support for features that matter to you to help decide which device
is best suited to your use case. However for this toy program we're only going to call
``vkGetPhysicalDeviceProperties`` for each device which will give us information such as
its name.

.. code-block:: c

   for (uint32_t i = 0; i < count; i++) {
      VkPhysicalDeviceProperties properties = {};
      vkGetPhysicalDeviceProperties(physical_devices[i], &properties);


Version numbers (``MAJOR.MINOR.PATCH``) in the Vulkan API are encoded into a single 32bit
integer as defined in the `specification`_. Thankfully the spec also defines a number of
macros that make decoding them nice and easy for us.

.. code-block:: c

   uint32_t vk_major = VK_VERSION_MAJOR(properties.apiVersion);
   uint32_t vk_minor = VK_VERSION_MINOR(properties.apiVersion);
   uint32_t vk_patch = VK_VERSION_PATCH(properties.apiVersion);

   uint32_t driver_major = VK_VERSION_MAJOR(properties.driverVersion);
   uint32_t driver_minor = VK_VERSION_MINOR(properties.driverVersion);
   uint32_t driver_patch = VK_VERSION_PATCH(properties.driverVersion);

All that's left to do is to print out the information we have gathered.

.. code-block:: c

      printf("Device Name:     \t%s\n", properties.deviceName);
      printf("  Type:          \t%s\n", vkPhysicalDeviceType_as_string(properties.deviceType));
      printf("  Vendor ID:     \t%d\n", properties.vendorID);
      printf("  Device ID:     \t%d\n", properties.deviceID);
      printf("  API Version:   \tv%d.%d.%d\n", vk_major, vk_minor, vk_patch);
      printf("  Driver Version:\tv%d.%d.%d\n", driver_major, driver_minor, driver_patch);
   }

I should also note that ``vkPhysicalDeviceType_as_string`` is a helper function I
defined that converts a member of the `VkPhysicalDeviceType`_ enum
into a string representation with a ``switch`` statement.

Conclusion
----------

And that's that! I've taken my first few baby steps with the Vulkan API and I hope that
if you've read this far then this post was as useful to you as it was to me! If you are
interested then you can see the full code listing `here`_ and I'll see you in the
next one.

.. _Autoconf: https://www.gnu.org/software/autoconf/
.. _CMake: https://cmake.org/
.. _documentation: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/vkEnumeratePhysicalDevices.html
.. _here: https://github.com/alcarney/vk/blob/2e7daaa68d79c6467e91bbd9d5ebfcf34729f6a5/src/vkdevice.c
.. _pattern rule: https://www.gnu.org/software/make/manual/make.html#Pattern-Rules
.. _phony targets: https://www.gnu.org/software/make/manual/make.html#Phony-Targets
.. _physical device: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/VkPhysicalDevice.html
.. _specification: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/html/vkspec.html#extendingvulkan-coreversions-versionnumbers
.. _this: https://www.kernel.org/doc/html/v4.10/process/coding-style.html#centralized-exiting-of-functions
.. _vkGetPhysicalDeviceImageFormatProperties: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/vkGetPhysicalDeviceImageFormatProperties.html
.. _vkGetPhysicalDeviceProperties: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/vkGetPhysicalDeviceProperties.html
.. _vkGetPhysicalDeviceQueueFamilyProperties: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/vkGetPhysicalDeviceQueueFamilyProperties.html
.. _VkPhysicalDeviceType: https://www.khronos.org/registry/vulkan/specs/1.1-extensions/man/html/VkPhysicalDeviceType.html
