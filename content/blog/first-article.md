+++
title = "I've Started a Blog… Again!"
author = ["Alex"]
description = "First article with ox-hugo"
date = 2018-09-22
tags = ["blogging"]
draft = false
+++

Not that you would have known it, but I've had a blog since 2014.  Well 2015 if
you're feeling generous, the first (and only) post went up in the last few
hours of New Year's Eve. It was a look back on some of the projects I had
worked on that year and I announced my intentions to start blogging.

Fast forward nearly 4 years and here I am announcing my intentions to start
blogging - **again**. So I guess you are wondering what happened?

I got lost.

My first attempt at running a blog was using [Jekyll](https://jekyllrb.com) and for some mystical reason
(It's been so long I can't actually remember why), I decided that it was not the
static site generator I was looking for. So I promptly set off on a voyage of
discovery in search of the ultimate static site generator.

Here is a list of some of the other static site generators I have played with
over the years in no particular order:

-   [Metalsmith](http://www.metalsmith.io/): Written in Javascript, this one appealed to me with
    its "everything is a plugin" approach. In theory I should be able to add any
    feature I wanted simply by finding/writing the right plugin.

-   [Hakyll](https://jaspervdj.be/hakyll/): I was going through a Haskell phase and I thought it would
    be a great idea to have my blog powered with it as well. **Haskell all the
    things!**

-   [Sphinx](http://www.sphinx-doc.org): Sphinx is an awesome tool for writing
    documentation. A big part of that is [reStructuredText](http://docutils.sourceforge.net/rst.html), add in the [ABlog](https://ablog.readthedocs.io/)
    extension and you should have a great setup for a blog.

-   [Pelican](https://blog.getpelican.com/) & [Nikola](https://getnikola.com/): However as Sphinx is primarily built
    for documentation projects, I found that I was fighting it more
    than anything. That led me to take a look at Pelican and Nikola, both written
    in Python and have support for reStructuredText and
    [Jupyter](http://jupyter.org/).

-   [Vuepress](https://vuepress.vuejs.org/): Having played around a bit with [VueJS](https://vuejs.org/), the
    thought of being able to take a dynamic site written in a powerful frontend
    framework and make a static site out of it seemed appealing. The best of both
    worlds.

-   [Hugo](https://gohugo.io/): Who **doesn't** want a static site generator written in Go? :)

-   [Emacs](https://www.gnu.org/software/emacs/) & [org-mode](https://orgmode.org/): Yes, [you can](https://orgmode.org/worg/org-blog-wiki.html) use emacs
    as a static site generator.

At this point you might be wondering what was wrong with all of the above so
that after nearly 4 years of tinkering I still had nothing to show for it?

Nothing. Absolutely nothing.

The problem was with me. I wanted complete control over the output, from the
contents of `<head>` to the CSS styling of links. There would always
be a point where I would start fighting against the very abstractions
designed to make my life easier! It got to the point where I even tried writing
my own static site generator...


## A New Perspective {#a-new-perspective}

After endless hours lost fiddling with scripts and stylesheets I stumbled
across a quote on the internet that would snap me out of my spiral of perpetual
procrastination.

> The technology you use **impresses no one**.
>
> The experience you create with it is **everything**. -- [Sean Gerety](https://twitter.com/ideakitchn?lang=en)

I have found myself saying this again and again, so much so that I think it may
have fundamentally altered the way I think about programming. I fell into a
trap of getting caught up in the merits of the technology for the sake of the
technology itself and lost sight of the experience - the blog itself.

Rejuvenated I've gone back to where it all started and have started using [Jekyll](https://jekyllrb.com)
again. I'm using the [Hydeout](https://fongandrew.github.io/hydeout/) theme as it's built in a way that allows me to make
a few (minor!) tweaks of my own. Within a few hours I was already working on the
draft that became this blog post, a place I never even got to in most of my
previous attempts.

It turns out that Markdown is a perfectly acceptable format for a blog. You
don't have to engineer your blog's theme from the ground up especially when a
prebuilt theme exists in the style you were going to build yourself anyway. It
doesn't matter that your blog can seamlessly format a Jupyter Notebook as a
regular blog post when you don't have any notebooks to publish in the first
place...

What matters is the content itself, that you have something interesting to say
and you have some way of making that available to other people. Everything else
is just an implementation detail, which if done right is invisible to the
consumers of your content anyway.

It's strange that I had learn something that is probably obvious to most people
the hard way but I'm here now. If you are reading this then things are looking
up but I can't quite declare victory as I'm no further forward than I was 4
years ago, first let's see if I make it to blog post number #2...