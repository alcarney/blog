---
title: Custom Text Objects
date: 2019-11-14T23:59:09+00:00
tags:
  - vim
identifier: 20191114T235909
---

# Custom Text Objects

The following snippet of vimscript (if I’m reading it right) will create 26(!) custom text objects

```vim
for char in [‘_’, ‘.’, ‘:’, ‘,’, ‘;’, ‘<bar>’, ‘/‘, ‘<bslash>’, ‘*’, ‘+’, ‘%’, ‘-‘, ‘#’]
    execute ‘xnoremap i’ . char . ‘:<C-u>normal! T’ . char . ‘vt’ . char . ‘<CR>’
    execute ‘onoremap i’ . char . ‘:normal vi’ . char . ‘<CR>’
    execute ‘xnoremap a’ . char . ‘:<C-u>normal! F’ . char . ‘vt’ . char . ‘<CR>’
    execute ‘onoremap a’ . char . ‘:normal va’ . char . ‘<CR>’
endfor
```

[Source](https://gist.github.com/romainl/c0a8b57a36aec71a986f1120e1931f20)
