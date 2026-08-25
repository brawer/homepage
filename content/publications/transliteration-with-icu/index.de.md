---
title: "Transkription und Transliteration von Eigennamen mit ICU-Transformationen"
original_title: "Proper Name Transcription/Transliteration with ICU Transforms"
original_language: "en"
date: 2010-10-19
publishDate: 2026-08-23
tags: ["Geo", "NLP", "Google", "Unicode", "Quelloffen"]
kind: "talk"
authors: ["Sascha Brawer", "Martin Jansche", "Hiroshi Takenaka", "Yui Terashima"]
venue: '34\. Internationalization & Unicode Conference (2010)'
abstract: >
  Wir schildern unsere Erfahrungen mit einer tiefgreifenden Lokalisierung
  von Google Maps, bei der Millionen geografischer Namen unterschiedlichster
  Herkunft in mehrere Zielsprachen übertragen werden mussten, darunter
  Russisch, Mandarin und Japanisch. Wir behandeln das Problem der
  Transliteration aus mehreren Ausgangssprachen in mehrere Zielsprachen,
  indem wir über eine explizite phonetische Zwischendarstellung gehen.
  Jedes Transliterationsschema ist als Abfolge von ICU-Transformationen
  implementiert, wobei einige bestehende Transformationen aus ICU und
  CLDR wiederverwendet werden, der grösste Teil aber eigens neu
  geschrieben wurde. Wir erläutern die einzelnen Schritte beim
  Erstellen von Transliterationsregeln, beschreiben bestehende
  offizielle und De-facto-Standards und Richtlinien und geben
  Empfehlungen für die Entwicklung und das Testen eigener
  ICU-Transformationen.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "icu-transforms-talk.pdf"
---
Dies war ein Vortrag, kein publiziertes Paper – Folien und eine
Aufzeichnung der Präsentation, aber kein eigenständiger schriftlicher
Beitrag. Gehalten an der IUC 34 in Santa Clara.
