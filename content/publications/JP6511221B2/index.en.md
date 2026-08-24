---
title: "Conversion of Input Text Strings"
original_title: "入力テキスト文字列の変換"
original_language: "ja"
date: 2019-05-15
publishDate: 2026-08-23
tags: ["Geo", "NLP", "i18n", "Google"]
kind: "patent"
authors: ["Sascha Brawer", "Martin Jansche", "Richard Sproat", "Hiroshi Takenaka", "Yui Terashima"]
venue: "Japan Patent Office"
patent_number: "JP6511221B2"
patent_status: "granted"
assignee: "Google LLC"
abstract: >
  A method for converting strings of geographic names from one script or
  language into another by combining two techniques: translating words
  by meaning where a known equivalent exists (e.g. “Park” → 「公園」), and
  transliterating the remaining words phonetically into the target
  script. The two are combined into a single mixed-form output — for
  example, an English park name ending in “Park” gets its generic part
  translated and its specific part transliterated, matching how such
  names are conventionally rendered by fluent speakers of the target
  language.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "JP6511221B2.pdf"
---
Japanese patent covering technology for converting place names and
similar geographic strings between writing systems — part of the same
line of work as the [ICU transforms talk](/publications/transliteration-with-icu/).
