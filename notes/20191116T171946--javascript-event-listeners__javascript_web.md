---
title: JavaScript Event Listeners
date: 2019-11-16T17:19:46+00:00
tags:
  - javascript
  - web
identifier: 20191116T171946
---

# JavaScript Event Listeners

Traditionally you might have added an event listener like so

```javascript
element.addEventListener('click', callback, false)
```

Where the `false` argument relates to event bubbling/capturing. However
this argument can be replaced with an object that gives greater control
over the behaviour

```javascript
element.addEventListener('click', callback, {
	capture: false,  // Same as the behaviour as the original bool
	once: true,      // Run the event once then automatically unregister the listener
	passive: false,  // If true the function will never call preventDefault()?
})
```
