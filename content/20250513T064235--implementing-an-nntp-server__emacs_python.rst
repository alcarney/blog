:title: Implementing an NNTP Server
:date: 2025-05-13
:tags: emacs, python
:identifier: 20250513T064235

Implementing an NNTP Server
===========================


CAPABILITIES
^^^^^^^^^^^^

Much like the LSP protocol, there is an initial handshake where the client establishes what the server is capable of.

.. code-block:: python

   async def send_capabilities(writer: asyncio.StreamWriter):
       """Report the server's capabilities to the client"""
       await send(writer, "101 Capability list:")
       await send(writer, "VERSION 2")
       await send(writer, "READER")
       await send(writer, "LIST ACTIVE NEWSGROUPS")
       await send(writer, ".")

I don't really know what capabilities I'll want/need long term but this seems sufficient to get the ball rolling.

MODE READER
^^^^^^^^^^^

.. code-block:: python

   # Based on the capabilities we're sending the spec says the client
   # should not use the mode reader command, but GNUs seems to do it
   # anyway...
   elif message == "MODE READER":
       # 200 - Posting allowed
       # 201 - Posting prohibited
       await send(writer, "201 Reader mode, posting prohibited")

Not sure if this ever needs to do anything...

NEWGROUPS
^^^^^^^^^

Allows the server to send a list of new groups

.. code-block:: python

   async def send_newgroups(writer: asyncio.StreamWriter, since: datetime):
       """Send any new groups added since the given datetime."""
       await send(writer, "231 list of new newgroups follows")
       await send(writer, ".")

But sending an empty list seems perfectly acceptable for now.

LIST (ACTIVE)
^^^^^^^^^^^^^

.. code-block:: python

   async def send_list(writer: asyncio.StreamWriter, keyword: str = "ACTIVE"):
       """Implementation of the various LIST commands."""

       if keyword == "ACTIVE":
           await send_list_active(writer)

       else:
           await send(writer, "501 Syntax Error")


   async def send_list_active(writer: asyncio.StreamWriter):
       """Implementation of the LIST ACTIVE command."""
       await send(writer, "215 list of newsgroups follows")
       await send(writer, "com.example 4 1 n")
       await send(writer, ".")


At this point it is possible to browse the list of groups on our server!
