---
title: "Verfahren zur speicherbeschränkten Konstruktion eines global vollständigen Cloud-Optimized GeoTIFF in hoher Zoomstufe aus Kachel-Zugriffsprotokollen"
original_title: "Method for Memory-Bounded Construction of a Globally Complete, High-Zoom-Level Cloud-Optimized GeoTIFF from Tile-Access Logs"
original_language: "en"
date: 2026-09-02
publishDate: 2026-09-07
tags: ["Geo", "OpenStreetMap", "Quelloffen"]
kind: "disclosure"
kind_label: "Sperrveröffentlichung"
teaser_is_document: true
authors: ["Sascha Brawer"]
venue: "[Technical Disclosure Commons](https://www.tdcommons.org/dpubs_series/11589/)"
abstract: >
  Beschrieben wird ein speicherbeschränktes Verfahren, um aus einem
  gleitenden Fenster von Kachel-Zugriffsprotokollen einen global
  vollständigen Cloud-Optimized GeoTIFF in hoher Zoomstufe zu erzeugen –
  ein planetenweites Raster in der Grössenordnung von 10¹¹ Zellen –,
  wobei der Arbeitsspeicher im Wesentlichen unabhängig von der
  Zellenzahl bleibt. Die Ausgabe ist
  ein normkonformer COG mit vollständiger Übersichtspyramide in
  reduzierter Auflösung, gewonnen durch robuste Aggregation der
  Zeitreihe pro Kachel; sie ist mehrere Hundert Mal kleiner als eine
  naive dichte Kodierung. Das Verfahren verbindet einen raumfüllenden
  Kachelschlüssel mit eingebetteter Zoomstufe, eine zweistufige
  plattengestützte Sortierung (externe Sortierung pro Zeitraum, gefolgt
  von einem zeitraumübergreifenden Streaming-Merge), eine begrenzte
  Wurzel-zu-Blatt-Arbeitsmenge des Rasters, die sich daraus ergibt,
  dass der geordnete Datenstrom in Vorordnung des Baums konsumiert
  wird, eine einstufige Erzeugung der Übersichten im selben Durchgang,
  eine robuste Aggregation pro Zelle ohne Materialisierung der
  Zeitreihe sowie drei einander ergänzende Verkleinerungen der
  Ausgabegrösse (Grössenquantisierung, Deduplizierung von Kacheln über
  gemeinsame Dateipositionen und eine monotone Werttransformation).
  Eine ausgearbeitete Konfiguration erzeugt ein globales
  Zoomstufe-18-Raster mit weniger als einem Gigabyte Arbeitsspeicher
  und schreibt eine rund 600 MB grosse Datei, wo eine dichte Kodierung
  etwa 275 GB benötigen würde.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "osmviews-method.pdf"
---
Eine Sperrveröffentlichung der Technik hinter
[OSMViews](https://osmviews.toolforge.org/): wie dessen Builder ein
gleitendes Fenster von OpenStreetMap-Kachel-Zugriffsprotokollen mit
konstantem Speicher in ein planetenweites Raster verwandelt.
Veröffentlicht, um eine Patentierung zu verhindern; die
Referenzimplementierung liegt unter der MIT-Lizenz [auf
GitHub](https://github.com/brawer/osmviews).
