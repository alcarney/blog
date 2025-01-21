:title: Inspecting Python Threads
:identifier: 20241201T120000
:date: 2024-12-01
:tags: blog, python, til
:author: Alex Carney
:language: en

TIL: Inspecting Python Threads
==============================

.. container:: post-teaser

   One of my favourite things about Python is that pretty much everything about the language can be inspected at runtime and today I found out this is true even for threads.

   While working on `this PR <https://github.com/swyddfa/esbonio/pull/928>`__ I kept running into issues where the ``esbonio`` process would not terminate, despite everything to my knowledge at least, was being shutdown as expected.
   Having encountered issues like this before, I knew the culprit was likely to be some background thread was stuck on something and keeping the process alive.
   The problem was I had no idea which thread it could be or what it was doing.

Thanks to `this Stack Overflow <https://stackoverflow.com/questions/7189226/program-does-not-exit-how-to-find-out-what-python-is-doing>`__ post, I discovered Python does provide the tools to figure it out.

With a breakpoint set just before the point where the process should be exiting, we can first enumerate all the active threads.

.. code-block:: python

   >>> import threading
   >>> {t.ident: t.name for t in threading.enumerate()}
   {
       140658776004416: 'MainThread',
       140658503321280: 'pydevd.Writer',
       140658492835520: 'pydevd.Reader',
       140658482349760: 'pydevd.CommandThread',
       140658471864000: 'pydevd.CheckAliveThread',
       140658444601024: 'Thread-6',
       140658354423488: 'Thread-7'
   }

Ignoring all the threads that appear to be part of the debugger (``pydevd.*``), the issue is probably in ``Thread-6`` or ``Thread-7``.
With the help of the ``sys`` module we can get the current stack frame for each thread

.. code-block:: python

   >>> import sys
   >>> thread_6_stack_frame = sys._current_frames()[140658444601024]
   >>> thread_7_stack_frame = sys._current_frames()[140658354423488]

Then using the ``traceback`` module we can print the current call stack!

.. code-block:: python

   >>> traceback.print_stack(thread_6_stack_frame)
   File "/var/home/linuxbrew/.linuxbrew/Cellar/python@3.13/3.13.0_1/lib/python3.13/threading.py", line 1012, in _bootstrap
     self._bootstrap_inner()
   File "/var/home/linuxbrew/.linuxbrew/Cellar/python@3.13/3.13.0_1/lib/python3.13/threading.py", line 1041, in _bootstrap_inner
     self.run()
   File "/var/home/alex/.vscode/extensions/ms-python.debugpy-2024.12.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_daemon_thread.py", line 53, in run
     self._on_run()
   File "/var/home/alex/.vscode/extensions/ms-python.debugpy-2024.12.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_timeout.py", line 43, in _on_run
     self._event.wait(wait_time)
   File "/var/home/linuxbrew/.linuxbrew/Cellar/python@3.13/3.13.0_1/lib/python3.13/threading.py", line 656, in wait
     with self._cond:
   File "/var/home/linuxbrew/.linuxbrew/Cellar/python@3.13/3.13.0_1/lib/python3.13/threading.py", line 369, in wait
     if not gotit:

Hmm, not so useful.. but then again looking closer at the call stack this thread also seems to be related to the debugger.
What about the other thread?

.. code-block:: python

   >>> traceback.print_stack(thread_7_stack_frame)
   File "/var/home/linuxbrew/.linuxbrew/Cellar/python@3.13/3.13.0_1/lib/python3.13/threading.py", line 1012, in _bootstrap
     self._bootstrap_inner()
   File "/var/home/linuxbrew/.linuxbrew/Cellar/python@3.13/3.13.0_1/lib/python3.13/threading.py", line 1041, in _bootstrap_inner
     self.run()
   File "/home/alex/.local/share/hatch/env/virtual/esbonio/3pU26gTf/hatch-test.py3.13-sphinx6/lib/python3.13/site-packages/aiosqlite/core.py", line 107, in run
     tx_item = self._tx.get()

Ah! This thread is stuck somewhere in the ``aiosqlite`` library, looks like I wasn't cleaning up all the DB connections like I thought I was!
