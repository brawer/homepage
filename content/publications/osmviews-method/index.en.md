---
title: "Method for Memory-Bounded Construction of a Globally Complete, High-Zoom-Level Cloud-Optimized GeoTIFF from Tile-Access Logs"
date: 2026-09-02
publishDate: 2026-09-07
tags: ["Geo", "OpenStreetMap", "Open Source"]
kind: "disclosure"
kind_label: "Defensive Disclosure"
teaser_is_document: true
authors: ["Sascha Brawer"]
venue: "[Technical Disclosure Commons](https://www.tdcommons.org/dpubs_series/11589/)"
abstract: >
  A memory-bounded method is disclosed for constructing a globally
  complete, high-zoom-level Cloud-Optimized GeoTIFF—a planet-wide raster
  on the order of 10¹¹ cells—from a rolling window of tile-access logs,
  using working memory that is essentially constant in the number of
  cells. The output is a standards-compliant
  COG with a full reduced-resolution overview pyramid, derived by
  robustly aggregating the per-tile time series; it is several hundred
  times smaller than a naïve dense encoding. The method combines a
  level-embedding space-filling tile key, a two-stage disk-backed
  ordering (per-period external sort followed by a cross-period
  streaming merge), a bounded root-to-leaf raster working set that
  follows from consuming the ordered stream in tree pre-order,
  single-pass inline overview generation, per-cell robust aggregation
  computed without materializing the time series, and three
  complementary output-size reductions (magnitude quantization, tile
  deduplication by shared file offsets, and a monotone value
  transform). A worked configuration builds a global zoom-18 raster in
  under one gigabyte of resident memory and emits a roughly 600 MB file
  where a dense encoding would require approximately 275 GB.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "osmviews-method.pdf"
---
A defensive disclosure of the technique behind
[OSMViews](https://osmviews.toolforge.org/): how its builder turns a
rolling window of OpenStreetMap tile-access logs into a planet-wide
raster in constant memory. Published to prevent patentability;
the reference implementation is [on
GitHub](https://github.com/brawer/osmviews) under the MIT license.
