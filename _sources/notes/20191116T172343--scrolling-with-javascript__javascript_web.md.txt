---
title: Scrolling with JavaScript
date: 2019-11-16T17:23:43+00:00
tags:
  - javascript
  - web
identifier: 20191116T172343
---

# Scrolling with JavaScript

It’s possible to use JavaScript to scroll the window

```javascript
window.scrollTo(0, 1000)
```

That says to scroll the window horizontally no pixels and to scroll down the
page 1000 pixels. However this will be executed instantly and the effect could
be jarring for the user so we can make this happen “smoothly” like so

```javascript
window.scrollTo({left: 0, top: 1000, behaviour: 'smooth'})
```
