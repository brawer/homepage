---
title: "Sitemaps für das Web-Crawling"
date: 2005-05-31
publishDate: 2026-09-07
tags: ["Google"]
kind: "patent"
kind_label: "Patentfamilie"
teaser_is_document: true
authors: ["Sascha Brawer", "Maximilian Ibel", "Ralph M. Keller", "Narayanan Shivakumar"]
assignee: "Google LLC"
patent_family:
  # siehe index.en.md — zwei US-Stränge, Priorität 2005-05-31.
  # TODO(review): expires-Daten der beiden 2010er-Patente sind
  # konservative Schätzungen (~2018–2019 wegen nicht bezahlter
  # Gebühren erloschen), nicht verifiziert.
  - office: "US"
    number: "US 7,769,742 B1"
    status: "lapsed"
    granted: "2010-08-03"
    expires: "2019-02-03"
  - office: "US"
    number: "US 7,801,881 B1"
    status: "lapsed"
    granted: "2010-09-21"
    expires: "2019-03-21"
  - office: "US"
    number: "US 8,037,055 B2"
    status: "expired"
    granted: "2011-10-11"
    expires: "2025-06-30"
  - office: "US"
    number: "US 9,355,177 B2"
    status: "lapsed"
    granted: "2016-05-31"
    expires: "2025-06-30"
abstract: >
  Zwei Seiten des Sitemaps-Mechanismus für das Crawling durch
  Suchmaschinen. Eine Website erzeugt eine XML-Datei, die ihre URLs
  samt Metadaten auflistet – Zeitpunkt der letzten Änderung,
  Änderungshäufigkeit, relative Priorität – und meldet den
  Suchmaschinen, dass diese Datei existiert. Ein Crawler liest diese
  Dateien dann, um Seiten zu finden, die er sonst übersehen würde,
  unveränderte Seiten auszulassen und die Lastgrenzen der Website
  einzuhalten, statt sich allein auf das Verfolgen von Links zu
  verlassen.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "us9355177.pdf"
---
Die Patente hinter dem [Sitemaps-Protokoll](https://www.sitemaps.org/),
das 2005 bei Google mitentwickelt und offen als Industriestandard
veröffentlicht wurde – zwei US-Fortsetzungsstränge, einer für die
Website-Seite und einer für die Crawler-Seite.
