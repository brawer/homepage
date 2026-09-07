---
title: "Conversion of Input Text Strings"
date: 2010-08-26
publishDate: 2026-09-07
tags: ["Geo", "NLP", "i18n", "Google"]
kind: "patent"
kind_label: "Patent Family"
teaser_is_document: true
authors: ["Sascha Brawer", "Martin Jansche", "Richard Sproat", "Hiroshi Takenaka", "Yui Terashima"]
assignee: "Google LLC"
patent_family:
  - office: "US"
    number: "US 10,133,737 B2"
    status: "active"
    granted: "2018-11-20"
    expires: "2032-01-01"
  - office: "JP"
    number: "JP 6511221 B2"
    status: "active"
    granted: "2019-05-15"
    expires: "2031-08-26"
  - office: "KR"
    number: "KR 10-1890835 B1"
    status: "active"
    granted: "2018-09-28"
    expires: "2031-08-26"
  - office: "CN"
    number: "CN 103189859 B"
    status: "active"
    granted: "2016-08-17"
    expires: "2031-08-26"
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
pdf: "us10133737.pdf"
---
Patented technology for converting place names and similar geographic
strings between writing systems — part of the same line of work as the
[ICU transforms talk](/publications/transliteration-with-icu/).
