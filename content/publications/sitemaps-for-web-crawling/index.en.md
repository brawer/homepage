---
title: "Sitemaps for Web Crawling"
date: 2005-05-31
publishDate: 2026-09-07
tags: ["Google"]
kind: "patent"
kind_label: "Patent Family"
teaser_is_document: true
authors: ["Sascha Brawer", "Maximilian Ibel", "Ralph M. Keller", "Narayanan Shivakumar"]
assignee: "Google LLC"
patent_family:
  # Two US threads, priority 2005-05-31: a "sitemap generating client"
  # (US 7,801,881 -> US 8,037,055) and a "web crawler scheduler"
  # (US 7,769,742 -> US 9,355,177).
  # TODO(review): the `expires` dates on the two lapsed 2010 patents
  # are conservative estimates — both lapsed ~2018–2019 for unpaid
  # maintenance fees; exact lapse dates not verified.
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
  Two sides of the Sitemaps mechanism for search-engine crawling. A
  website generates an XML file listing its URLs together with metadata
  — last-modified time, change frequency, relative priority — and
  notifies search engines that the file exists. A crawler then reads
  these files to discover pages it would otherwise miss, skip pages
  that have not changed, and stay within a site’s load limits, instead
  of relying on link-following alone.
image: "teaser.webp"
pdf_preview: "pdf-preview.webp"
pdf: "us9355177.pdf"
---
The patents behind the [Sitemaps protocol](https://www.sitemaps.org/),
co-developed at Google in 2005 and published openly as an industry
standard — two US continuation threads, one for the website side and
one for the crawler side.
