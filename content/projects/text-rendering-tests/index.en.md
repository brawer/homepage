---
title: "Text Rendering Tests"
image: "text-rendering-tests.webp"
date: 2016-08-31
publishDate: 2026-08-25
status: "active"
role: "creator"
tags: ["Typography", "Google", "Unicode", "Python", "C++", "Open Source"]
summary: "Unicode’s test suite for text rendering engines"
github_url: "https://github.com/unicode-org/text-rendering-tests"
---
I started this project in 2016 while working on text rendering at
Google, as [Behdad Esfahbod](https://behdad.org/) and I brought
[Variable Fonts](https://en.wikipedia.org/wiki/Variable_font) back to
life. That required Adobe’s, Apple’s, and Microsoft’s closed-source
engines to behave _exactly_ like the free stack we shipped in Chrome
and Android; otherwise the idea would have foundered on platform
fragmentation again, just like during the “[Font Wars](https://www.pastemagazine.com/design/adobe/the-font-wars).” So I asked
around at other companies and font foundries, and put together this
test suite. Not my most technically challenging work, but it helped
make implementations across the industry more consistent. It’s since
moved to the Unicode Consortium, where I’m still nominally the
maintainer, though these days I rarely touch it.

