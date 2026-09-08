---
title: "Patti"
subtitle: "Compiling Unification-Based Finite-State Automata into Machine Instructions for a Superscalar Pipelined RISC Processor"
date: 1998-01-01
publishDate: 2026-09-08
tags: ["NLP"]
kind: "thesis"
kind_label: "Diploma Thesis"
teaser_is_document: true
authors: ["Sascha Brawer"]
venue: "[Saarland University](https://www.coli.uni-saarland.de/index.php?lang=en), Computational Linguistics"
degree: "Diploma (Diplom-Linguist) in Computational Linguistics, minor Computer Science"
abstract: >
  A compiler that turns a unification-based linguistic formalism —
  non-deterministic finite-state automata whose transitions are labeled
  with typed attribute-value matrices — directly into PowerPC machine
  code. Its fine-grained knowledge of the task enables optimizations
  that are hard to reach with general-purpose techniques: static
  branch-prediction heuristics, data-cache control, and scheduling that
  runs some unifications in parallel on the processor’s superscalar
  pipeline. Extracting noun groups from texts of a few thousand words
  took fractions of a millisecond on a 1997 Power Macintosh — on the
  order of 21 million tokens per second — fast enough that unification
  and pattern matching cease to be bottlenecks, and fast enough to put
  linguistic analysis within reach of interactive applications.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "patti.pdf"
---
My diploma thesis at Saarland University, supervised by Hans Uszkoreit
and Manfred Pinkal. It describes work I did during an internship at
[Apple’s Advanced Technology Group](https://en.wikipedia.org/wiki/Apple_Advanced_Technology_Group)
in Cupertino.

I presented the core ideas as a talk in September 1999 — at the IBM
T. J. Watson Research Center, Lucent Bell Labs, Xerox PARC, Saarland
University, and the University of Zürich. [Slides](patti-talk.pdf).
