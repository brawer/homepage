---
title: "Transkription und Transliteration von Eigennamen mit ICU Transforms"
original_title: "Proper Name Transcription/Transliteration with ICU Transforms"
original_language: "en"
date: 2010-10-19
publishDate: 2026-08-23
tags: ["Geo", "NLP"]
kind: "talk"
authors: ["Sascha Brawer", "Martin Jansche", "Hiroshi Takenaka", "Yui Terashima"]
venue: "34. Internationalization & Unicode Conference (2010)"
abstract: >
  Wir schildern unsere Erfahrungen mit einer tiefgreifenden Lokalisierung
  von Google Maps, bei der Millionen geografischer Namen unterschiedlichster
  Herkunft in mehrere Zielsprachen übertragen werden mussten, darunter
  Russisch, Mandarin und Japanisch. Wir gehen das Problem der
  Transliteration aus mehreren Ausgangssprachen in mehrere Zielsprachen an,
  indem wir über eine explizite phonetische Zwischendarstellung pivotieren.
  Jedes Transliterationsschema ist als Abfolge von ICU-Transforms
  implementiert, wobei einige bestehende Transforms aus ICU und CLDR
  wiederverwendet werden, der grösste Teil aber eigens für dieses Problem
  geschrieben wurde. Wir erläutern die einzelnen Schritte beim Erstellen
  von Transliterationsregeln, beschreiben bestehende offizielle und
  de-facto-Standards und Richtlinien und geben Empfehlungen für die
  Entwicklung und das Testen eigener ICU-Transforms.
image: "teaser.webp"
pdf: "icu-transforms-talk.pdf"
---
Dies war ein Vortrag, kein publiziertes Paper – Folien und eine
Aufzeichnung der Präsentation, aber kein eigenständiger schriftlicher
Beitrag. Gehalten an der IUC 34 in Santa Clara.
