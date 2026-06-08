:title: Writing a Wayland Client
:date: 2026-01-05
:tags: python, wayland
:identifier: 20260105T224240
:signature: 8

Writing a Wayland Client
========================

.. container:: post-teaser

   For no particular reason, I decided it would be *fun*, to try writing a wayland client (i.e. open a window) using Python.

   After all, how hard could it be?..

Fundamentals
------------

Before we can dive into the specifics of the protocol, we need to understand how the client and server actually communicate with each other.

- :ref:`py-wayland-client-open-connection`
- :ref:`py-wayland-client-obj-discovery`
- :ref:`py-wayland-client-encode-message`
- :ref:`py-wayland-client-decode-message`
- :ref:`py-wayland-client-close-connection`

.. _py-wayland-client-open-connection:

Opening a connection
""""""""""""""""""""

.. highlight:: console

Communication with the wayland compositor is done over a `UNIX domain socket <https://en.wikipedia.org/wiki/Unix_domain_socket>`__.
No, I don't really know what that means either, but being a UNIX thing it probably looks like a file.

The `protocol <https://wayland.freedesktop.org/docs/html/ch04.html#sect-Protocol-Wire-Format>`__ says the socket is usually named ``waylnd-0`` (or whatever the ``WAYLAND_DISPLAY`` environment variable says), but unless I missed it, it doesn't tell you which folder should contain it!.

Thankfully, a quick search later, I'm informed it should be contained in your ``$XDG_RUNTIME_DIR``::

  $ ls -l $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY
  srwxr-xr-x. 1 alex alex 0 Jan  4 10:42 /run/user/1000/wayland-0=

Let's try and open a connection using Python

.. code-block:: python

   >>> import asyncio, os
   >>> (r, w) = await asyncio.open_unix_connection(f"{os.getenv('XDG_RUNTIME_DIR')}/{os.getenv('WAYLAND_DISPLAY')}")

Huh, that actually worked.

The protocol says that the server broadcasts the state of a bunch of objects on connection, so I guess we should try reading a message.
Each message has a header composed of 2, 32-bit words so we should try reading 8 bytes out of the reader.

.. code-block:: python

   >>> header = await r.read(8)

*Crickets...*

Hmm, I would've expected that to have returned by now, I guess I must be missing something.

.. _py-wayland-client-obj-discovery:

Global Object Discovery
"""""""""""""""""""""""

I don't know what led me to believe that I should be able to open the socket and start reading messages from it, if we continue with the file analogy, a file doesn't know when it has been opened!

This triggered a long period of me reading and re-reading parts of the documentation,  browsing `some of the code <https://gitlab.freedesktop.org/wayland/wayland>`__ and yes, a short conversation with a language model! 😅

Now as I write this, I *think* I understand enough to describe the first steps in establishing a connection with a wayland compositor.

#. The client issues a ``wl_display::get_registry`` request.
#. The server issues a sequence of ``wl_registry::global`` events, indicating what displays, inputs etc are available.
#. The client issues a sequence of ``wl_registry::bind`` requests, associating client-generated ids with the global objects.

Time to put it to the test!

.. _py-wayland-client-encode-message:

Encoding Messages
"""""""""""""""""

.. note::

   The protocol `recommends <https://wayland.freedesktop.org/docs/html/ch04.html#sect-Protocol-Code-Generation>`__ implementations use the provided `xml definition <https://gitlab.freedesktop.org/wayland/wayland/-/blob/main/protocol/wayland.xml>`__ to generate the code necessary to represent protocol messages.

   Since I'm only hacking together a toy example, I'm not going to worry about this.


Quoting the wayland `wire format <https://wayland.freedesktop.org/docs/html/ch04.html#sect-Protocol-Wire-Format>`__

.. pull-quote::

   Every message is structured as 32-bit words; values are represented in the host's byte-order. The message header has 2 words in it:

   - The first word is the sender's object ID (32-bit).

   - The second has 2 parts of 16-bit.
     The upper 16-bits are the message size in bytes, starting at the header (i.e. it has a minimum value of 8).
     The lower is the request/event opcode.

   The payload describes the request/event arguments.
   Every argument is always aligned to 32-bits.
   Where padding is required, the value of padding bytes is undefined.
   There is no prefix that describes the type, but it is inferred implicitly from the xml specification.

So to send the initial ``wl_display::get_registry`` request we need to send:

- The object ID for ``wl_display``.

  This stumped me for a while, I still haven't found where in the spec it says this, but I eventually discovered this to be ``1``, always.

- The opcode for the ``get_registry`` request.

  Again, this is something I couldn't figure out from the documentation but this `reddit thread <https://www.reddit.com/r/wayland/comments/4dzc9d/what_are_the_wayland_protocol_opcodes/>`__ states that the opcode is derived from the order they are listed in the xml specification - which gives us an opcode of ``1``.

- The ID we want to assign to the registry object.

  The spec states that client's `must <https://wayland.freedesktop.org/docs/html/ch04.html#sect-Protocol-Creating-Objects>`__ allocate IDs sequentially, so this will be ``2``.

Packaging this up for the wire format looks something like the following:

.. code-block:: python

   >>> import struct

   >>> object_id = 1
   >>> opcode = 1
   >>> new_id = 2

   >>> fmt = struct.Struct("iii") # 3, 32-bit integers
   >>> msg = fmt.pack(
   ...     object_id,
   ...     opcode | (fmt.size << 16), # Shifting the message size into the upper 16 bits.
   ...     new_id,
   ... )

   >>> msg
   b'\x01\x00\x00\x00\x01\x00\x0c\x00\x02\x00\x00\x00'

Which we can write to the socket:

.. code-block:: python

   >>> w.write(msg)
   >>> await w.drain()

Ok... I guess that worked, let's see if we can read any messages this time.

.. _py-wayland-client-decode-message:

Decoding Messages
"""""""""""""""""

We should start by reading the header - which is composed of 2x32-bit integers = 8 bytes.

.. code-block:: python

   >>> hdr = await r.read(8)
   >>>

Exciting! There's actually data there this time!
Time to find out how many more bytes there are to read.

.. code-block:: python

   >>> struct.unpack('ii', hdr)
   (2, 2359296)  # (object_id, [size|opcode])

   >>> object_id, sizeop = _
   >>> object_id
   2  # Message is associated with the he wl_registry object we requested

   >>> size = sizeop >> 16
   >>> size
   36  # bytes

   >>> opcode = sizeop & 0xFFFF
   >>> opcode
   0  # wl_registry::global

It looks like this message is announcing the first of the global objects!
Remembering the fact that the message size includes the header, we need to read an additional ``(36 - 8) = 28`` bytes to extract the payload.

.. code-block:: python

   >>> payload = await r.read(28)
   >>> payload
   b'\x01\x00\x00\x00\x0e\x00\x00\x00wl_compositor\x00\x00\x00\x06\x00\x00\x00'

I'm willing to guess that this message is announcing the ``wl_compositor`` object!

However, let's try decoding this message anyway.
Consulting the `documentation <https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_registry>`__ for the ``wl_registry::global`` event you will see that the first argument is the name for this object.

.. code-block:: python

   >>> struct.unpack('i', payload[:4])
   (1,)

Next is the name of the interface this object implements, as a string.
Thanks to the Python REPL we already have an idea on what the string we're expecting to see, but here is how the wire protocol encodes strings.

.. pull-quote::

   Starts with an unsigned 32-bit length (including null terminator), followed by the UTF-8 encoded string contents, including terminating null byte, then padding to a 32-bit boundary.
   A null value is represented with a length of 0. Interior null bytes are not permitted.

So, the next byte should give us the string length

.. code-block:: python

   >>> struct.unpack('i', payload[4:8])
   (14,)

   >>> payload[8:(8+14)]
   b'wl_compositor\x00'

That looks about right!
However, since the string does not align to a 32 bit boundary (``14 % 4 = 2``), we should consume ``14 + 2 = 16`` bytes of the payload.

Which should leave us a final 4 bytes representing the version number of the interface the object implements.

.. code-block:: python

   >>> payload[24:]
   b'\x06\x00\x00\x00'

   >>> struct.unpack('i', payload[24:])
   (6,)

Now we're speaking wayland!
However, I don't know about you but this is starting to stretch beyond what I can keep track of manually in a REPL session.

.. _py-wayland-client-close-connection:

Closing a connection
""""""""""""""""""""

As far as I can tell, we close the connection simply by closing the socket connection.

.. code-block:: python

   >>> w.close()

A Simple Client
---------------

At this stage, we probably know enough to write a client that can connect and discover the available global objects.

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   import asyncio
   import logging
   import os
   import pathlib
   import struct

``WlDisplay``
"""""""""""""

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   class WlDisplay:
       """Represents the ``wl_display`` object."""

       def __init__(self, oid: int = 1, client):
           self.oid = oid
           self.client = client

       def get_registry(self, new_id: int = 2) -> bytes:
           self.client.log.debug("[wl_display::get_registry] %s", new_id)
           fmt = struct.Struct('iii')
           return fmt.pack(
               self.oid,
               1 | (fmt.size << 16),
               new_id
           )


``WlRegistry``
""""""""""""""

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   class WlRegistry:
       """Represents the ``wl_registry`` object."""

       def __init__(self, oid: int = 2, client):
           self.oid = oid
           self.client = client
           self.event = [
               self.handle_global,
           ]

       def handle_global(self, payload: bytes):
           """Handle the wl_registry::global event."""

           name, payload = parse_int(payload)
           interface, payload = parse_string(payload)
           version, payload = parse_int(payload)

           self.client.server_log.debug(
               f"[wl_registry::global]: %s, %s v%s",
               name,
               interface,
               version,
           )

Where ``parse_int`` and ``parse_string`` look like the following.

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   def parse_int(payload: bytes) -> tuple[int, bytes]:
       i, payload = payload[:4], payload[4:]
       return struct.unpack('i', i)[0], payload

   def parse_string(payload: bytes) -> tuple[str, bytes]:
       l, payload = payload[:4], payload[4:]
       length = struct.unpack('i', l)[0]

       # Account for alignment
       pad = l % 4
       s, payload = payload[:l-1], payload[l + pad:]

       return s.decode('utf-8'), payload


``WlClient``
""""""""""""

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   class WlClient:
       def __init__(self):
           # The client needs to hold the reader/writer objects
           self.reader: asyncio.StreamReader | None = None
           self.writer: asyncio.StreamWriter | None = None

           # As well as all the objects we create while interacting with the protocol.
           self.objects = []

           # For tracking async tasks
           self._tasks: set[asyncio.Task[Any]] = set()

           # Logging
           self.log = logging.getLogger('client')
           self.server_log = logging.getLogger('server')

Connecting to the socket and starting the event handling loop

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   #
       async def connect(self, socket: pathlib.Path):
           self.reader, self.writer = asyncio.open_unix_connection(str(socket))
           self._tasks.add(asyncio.create_task(self.handle_events()))

The main event handling loop:

.. code-block:: python
   :project: wayland-clients
   :filename: simple_client.py

   #
       async def handle_events(self):
           """Read and process events sent from the server."""

           while True:
               # Read the header and select the relevant object
               header = await self.reader.read(8)
               object_id, sizeop = struct.unpack('ii', header)
               obj = self.objects[object_id - 1]

               # Determine payload size and opcode
               size = sizeop >> 16
               opcode = sizeop & 0xFFFF

               # Read payload and handle event.
               payload = await self.reader.read(size - 8)
               handler = obj.event[opcode]

               handler(payload)
