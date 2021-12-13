PDF Documents
=============

Rotating Pages
--------------

Using the :pypi:`PyPDF2` package it's quite easy to rotate pages with Python.
The following snippet flips each page in a document by 180 degress.

.. code-block:: python 

   import PyPDF2

   source = open('source.pdf, 'rb')
   output = open('output.pdf', 'wb')

   reader = PyPDF2.PdfFileReader(source)
   writer = PyPDF2.PdfFileWriter()

   for idx in range(reader.numPages):
       page = reader.getPage(idx)
       page.rotateClockwise(180)
       writer.addPage(page)

   writer.write(output)
    
   source.close()
   output.close()