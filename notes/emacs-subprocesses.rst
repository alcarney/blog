Emacs Sub Processes
=================== 

Something that's quite useful in Emacs is the ability to start a running process
in the background. This can be done with the ``start-process`` function.


Examples
--------

We can set the directory to run in by wrapping the call to ``start-process`` in a
``let`` expression that sets the ``default-directory`` variable.

.. code-block:: elisp

  (let ((default-directory "~/Projects/blog"))
    (start-process "hugo" "hugo[blog]" "hugo" "server" "--buildDrafts" "--buildFuture"))

There's a lot of mentions of hugo here let's break this down a bit

- The first gives a name to the process, this will show up in places like the
  ``process-menu``
- The second names the buffer that will be used to display the output from the
  process
- The third is the ``hugo`` command itself, followed by any additional arguments
  to pass to it.
 