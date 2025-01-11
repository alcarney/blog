---
title: Bridging org-mode to docutils
date: 2023-07-28T14:08:26+00:00
tags:
  - python
  - docutils
identifier: 20230728T140826
---

# Bridging org-mode to docutils

It looks like it's fairly straightforward to bridge the org-mode format to docutils!

Building on the [orgparse](https://github.com/karlicoss/orgprase) project, it's simple enough to write a proof of concept `Parser` to bridge the two.

```python
import orgparse
from docutils import nodes
from docutils.parsers import Parser

class OrgParser(Parser):

   def parse(self, inputstring, document):
	   self.setup_parse(inputstring, document)

	   orgnodes = orgparse.loads(inputstring)

	   parents = [document]
	   current_level = 0

	   for org_node in orgnodes[1:]:
		   if org_node.level < current_level:
			   parents.pop()

		   parent = parents[-1]
		   section = nodes.section(
			   "",
			   nodes.title(
				   "",
				   nodes.Text(org_node.heading)
			   )
		   )
		   parent += section

		   section += nodes.paragraph(
			   "",
			   nodes.Text(org_node.body)
		   )

		   if org_node.level > current_level:
			   parents.append(section)

		   current_level = org_node.level

	   self.finish_parse()
```
Which can then be used to convert an org document into html.

```python
publish_file(
   source_path='file.org',
   destination_path='test.html',
   parser=OrgParser(),
   parser_name="",
   writer_name="html5"
)
```
