---
title: "Proper Name Transcription/Transliteration with ICU Transforms"
date: 2010-10-19
publishDate: 2026-08-23
tags: ["Geo", "NLP", "Google", "Unicode", "Open Source"]
kind: "talk"
kind_label: "Talk"
authors: ["Sascha Brawer", "Martin Jansche", "Hiroshi Takenaka", "Yui Terashima"]
venue: "34th Internationalization & Unicode Conference (2010)"
abstract: >
  We describe our experience with a deep localization of Google Maps,
  where millions of geographic names from diverse origins had to be
  represented in several target languages, including Russian, Mandarin,
  and Japanese. We tackle the problem of transliterating from several
  source languages into several target languages by pivoting through an
  explicit intermediate phonetic representation. Each transliteration
  scheme is implemented as a sequence of ICU transforms, reusing a few
  existing transforms from ICU and CLDR, but consisting mostly of
  transforms written specifically for this problem. We discuss the steps
  that go into building transliteration rules, describe existing official
  and de facto standards and guidelines, and give recommendations for
  developing and testing custom ICU transforms.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "icu-transforms-talk.pdf"
---
This was a talk rather than a published paper — slides and a recording
of the presentation, no separate written paper. Presented at IUC 34 in
Santa Clara.
