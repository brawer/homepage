---
title: "Patti"
subtitle: "Übersetzung unifikationsbasierter endlicher Automaten in Maschinenbefehle für einen superskalaren Pipeline-RISC-Prozessor"
original_title: "Patti: Compiling Unification-Based Finite-State Automata into Machine Instructions for a Superscalar Pipelined RISC Processor"
original_language: "en"
date: 1998-01-01
publishDate: 2026-09-08
tags: ["NLP", "Apple"]
kind: "thesis"
kind_label: "Diplomarbeit"
teaser_is_document: true
authors: ["Sascha Brawer"]
venue: "[Universität des Saarlandes](https://www.coli.uni-saarland.de/index.php?lang=en), Computerlinguistik"
degree: "Diplom-Linguist (Computerlinguistik), Nebenfach Informatik"
abstract: >
  Ein Compiler, der einen unifikationsbasierten linguistischen
  Formalismus – nichtdeterministische endliche Automaten, deren
  Übergänge mit typisierten Attribut-Wert-Matrizen beschriftet sind –
  direkt in PowerPC-Maschinencode übersetzt. Dank seines detaillierten
  Wissens über die Aufgabe kann er Optimierungen vornehmen, die mit
  allgemeinen Verfahren nur schwer erreichbar sind: Heuristiken zur
  statischen Sprungvorhersage, Steuerung des Daten-Caches und eine
  Anordnung der Maschinenbefehle, die einzelne Unifikationen parallel
  in der superskalaren Pipeline des Prozessors ausführt. Das
  Extrahieren von Nominalgruppen aus Texten von einigen tausend Wörtern
  dauerte auf einem Power Macintosh von 1997 Bruchteile einer
  Millisekunde – in der Grössenordnung von 21 Millionen Token pro
  Sekunde – schnell genug, dass Unifikation und Mustervergleich keine
  Engpässe mehr sind, und schnell genug, um linguistische Analyse für
  interaktive Anwendungen praktikabel zu machen.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "patti.pdf"
---
Meine Diplomarbeit an der Universität des Saarlandes, betreut von Hans
Uszkoreit und Manfred Pinkal. Sie beschreibt die Arbeit, die ich
während eines Praktikums bei [Apples Advanced Technology Group](https://en.wikipedia.org/wiki/Apple_Advanced_Technology_Group)
in Cupertino geleistet habe.

Die Kernideen habe ich im September 1999 als Vortrag vorgestellt – am
IBM T. J. Watson Research Center, bei den Lucent Bell Labs, am Xerox
PARC, an der Universität des Saarlandes und an der Universität Zürich.
[Folien](patti-talk.pdf).
