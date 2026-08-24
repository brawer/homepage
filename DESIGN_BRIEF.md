# brawer.ch — Design Brief

## What this site is
A personal site for Sascha, built with Hugo, covering three areas of work: oil
paintings/drawings, open-source (and some proprietary) software projects, and
publications (papers, talks, patents, a book, a lecture series). The site is
bilingual (English/German). Content already exists in the repo as Markdown +
images/PDFs; this brief is for designing the CSS/templates only — the content
model is fixed.

## Site map & page types

| URL pattern              | Page type          | Purpose                                                                 |
|---------------------------|---------------------|--------------------------------------------------------------------------|
| `/` (and `/de/`)          | Home (single)       | "Hello, I'm Sascha" + LinkedIn/GitHub/email icons + 1–2 sentence intro + links to the four sections |
| `/art/`                    | List (gallery)      | Visual grid of all artwork, images possibly cropped to a consistent thumbnail shape. Click → detail page |
| `/art/<slug>/`             | Detail (leaf)       | Full image + title, medium, height × width, date, a paragraph of text, tags |
| `/projects/`               | List (gallery)      | Visual grid of projects (mix of open-source and proprietary), same gallery treatment as Art |
| `/projects/<slug>/`        | Detail (leaf)       | Description, links (repo / demo), tags                                  |
| `/publications/`           | List (gallery)      | Visual grid of papers, talks, patents, a book, a lecture series, same gallery treatment as Art |
| `/publications/<slug>/`    | Detail (leaf)       | Title, authors, venue, abstract, tags, download(s) — see note below, one item is structurally different |
| `/resume/`                 | Single              | One-page résumé/CV                                                      |
| `/tags/<tag>/`             | Taxonomy list       | Everything (art, publications, projects) carrying that tag, e.g. `/tags/memes/`. Some tag pages carry their own intro text (see below) |

Every content URL above also exists under `/de/...` — the site is fully
bilingual by policy: any item missing a German (or English) version is a
content gap to fix, not an accepted asymmetry. See `CLAUDE.md` for current
known gaps.

## Bilingual (EN/DE) — design implications
- Needs a **language switcher** in the header, using each page's
  `.Translations`. Since both languages are always expected to exist, the
  switcher can assume symmetry and doesn't need conditional "hide if
  missing" logic — though it's still worth having it degrade gracefully
  (hide the link rather than 404) for the period while remaining gaps are
  being filled in.
- Some tag pages exist under different terms per language (e.g.
  `/tags/animals/` vs. `/de/tags/tiere/`) — the switcher logic for taxonomy
  pages needs to resolve through `translationKey`, not just try the same
  URL with `/de/` prepended.
- Nothing about layout/visual design changes between languages — same
  templates render both, just different text. German text runs slightly
  longer on average than English; leave reasonable breathing room in
  headings/nav rather than tight-fitting to English text length.

## Design goals for `/design` mode
- **Home page**: minimalist, portrait-free is fine, name + one-line identity
  statement, small social icons (LinkedIn, GitHub, email), then clear nav/
  links into Art / Projects / Publications / Résumé, in that order. This
  is an entry point, not a landing page with heavy marketing copy. Note:
  the intro text, icons, and nav links are all pulled from site config/menu
  at the template level, not hardcoded per page — see `CLAUDE.md` for where.
- **All three content sections now share one gallery-style grid** — Art,
  Projects, and Publications all have a teaser image per item (paintings,
  a curated title-slide/diagram/typographic card for publications, and
  presumably something equivalent for projects), so `/art/`, `/projects/`,
  and `/publications/` list pages should reuse a single grid/gallery
  component rather than Art getting a visual treatment and the other two
  getting a plain text list. Thumbnails cropped to a consistent aspect
  ratio for visual rhythm across all three. A small `kind` badge (Talk /
  Paper / Patent / Book / Lecture) is still worth layering onto the
  Publications grid, since that section mixes quite different document
  types even though they now look visually uniform in the grid. As
  before, the full/uncropped visual only appears on each item's own
  detail page — the grid is thumbnails only, cropped for consistency.
- **Art detail page**: image-forward, metadata (medium, height × width,
  date) presented as a compact label/caption block, not competing with the
  image. Note dimensions are two separate numeric fields (height, then
  width) — template should join them as "H × W cm", don't expect a
  pre-formatted string.
- **Publications detail page — two layouts needed, not one**:
  - *Standard case* (talk/paper/patent/book): one title, one abstract, one
    download link/button for a single PDF.
  - *Lecture-series case* (currently just one item,
    `programming-techniques-in-cl`): no single PDF — instead a personal
    intro paragraph followed by grouped lists of many downloadable PDFs
    (lectures grouped by semester, plus a separate "listings to download"
    group). This content already exists as plain Markdown lists/definition
    lists in the body — needs either its own template variant keyed on
    `kind == "lecture"`, or CSS that makes a long Markdown-body list of
    links look intentional (e.g. styled as a two-column table or accordion
    per semester) rather than a wall of plain links.
  - A few items also carry an `original_title`/`original_language` pair
    (e.g. the Japanese patent) — when present, show as a small subtitle
    under the main title, e.g. "Original title (ja): …".
  - Patents may also carry an `assignee` (the company/entity the patent
    was assigned to) — worth surfacing next to `patent_number` and
    `patent_status` in that compact metadata block, not buried in the
    abstract.
- **Tag pages**: reuse the same gallery/grid component regardless of which
  section(s) the tagged items come from — since Art, Projects, and
  Publications now share one visual treatment, a tag page doesn't need
  per-section styling logic even when it mixes items from different
  sections. Some tag pages (e.g. `/tags/memes/`) have their own intro
  paragraph in front — render that above the grid, not as a separate page.
- **Résumé page**: should read as a 2026-appropriate CV, not the old
  `brawer.ch/cv/` page's plain HTML table (still viewable there for
  reference) — a timeline/card layout rather than a literal table.
  Sascha suggested small icons per organization; if pursued, use
  generic/neutral iconography (initials, a monogram, a generic
  building/institution glyph) rather than employers' actual logos —
  those are trademarks and this site isn't licensed to display them.
  The front matter already separates `organization` from
  `organization_url`, so an icon slot could key off the org name
  without a new content field, if a small fixed icon set covers the
  ~10 organizations involved. Some entries (independent work, a
  sabbatical) have no `organization` at all — the layout needs to
  degrade gracefully for those, not assume every row has a company.
- **Typography preference**: use proper typographic quotes throughout, in
  both languages — but note each language has its own convention, not one
  shared glyph set. English uses “curly double” and ‘curly single’ quotes.
  German uses **Swiss conventions (de-CH)**, not the German-German
  low-high style: «guillemets» for double quotes and ‹single guillemets›
  for a nested quote inside one, with no space between the guillemet and
  the text (e.g. «wie er sagte» not « wie er sagte »). This is a
  deliberate departure from „German-German" „low-high" quotes — don't let
  a template or plugin default to those. For dashes: English body copy
  uses em dashes (—, no surrounding spaces, e.g. "the code — and the
  paintings — both matter"); German body copy uses en dashes (–, with
  surrounding spaces, e.g. "der Code – und die Bilder – zählen beide"),
  matching standard German typographic convention rather than the English
  em-dash style. This applies to hardcoded template strings as much as
  Markdown content — don't let a straight quote or plain hyphen slip into
  UI chrome text (buttons, labels) while content correctly uses the
  typographic versions. The site's German language block is configured
  with `locale = "de-CH"` (not plain `de`) specifically to signal
  this — worth keeping in mind if any tooling/spellcheck/hyphenation
  behavior is locale-aware, since de-CH also conventionally drops ß in
  favor of ss.
- **Consistent typographic system** across all sections — this is one
  person's site with several different "collections," not separate sites,
  so navigation, header, footer, and type scale should feel unified.
- Images are served by Hugo's image pipeline (responsive WebP/AVIF,
  multiple widths) — templates should use `<picture>`/srcset output, not
  a single fixed `<img>`.

## Content model reference (for template variables)
See `CLAUDE.md` at the repo root for the full rationale behind these
fields — this is just the shape.

**Art bundle** (`content/art/<slug>/index.<lang>.md`): `title`, `date`,
`publishDate`, `tags`, `medium`, `height_cm`, `width_cm` (two numbers, not
one string), `image` (WebP resource filename, shared across language
variants), body = descriptive paragraph.

**Publications bundle** (`content/publications/<slug>/index.<lang>.md`):
`title`, `date`, `publishDate`, `tags`, `kind` (`talk` / `paper` / `patent`
/ `book` / `lecture` — lowercase, needs an i18n-translated display label,
see `CLAUDE.md`), `authors` (list), `venue` (may contain inline
Markdown links — render through `markdownify`, don't output as a raw
string), `abstract`, `image` (WebP
teaser, curated per item — no automatic source the way art has). Optional:
`degree` (thesis only), `patent_number` + `patent_status` + `assignee`
(patent only — `assignee` is the company/entity the patent was
assigned to, e.g. "Google LLC"), `original_title` + `original_language`
(any kind, when applicable), `pdf` (single-PDF items only — absent
for the lecture-series item, which instead has resource links
directly in the Markdown body).

**Project bundle** (`content/projects/<slug>/index.<lang>.md`, no
entries yet): `title`, `date`, `tags`, `image` (WebP teaser), `open_source`
(bool), optional repo/demo `link`, body = description.

**Resume bundle** (`content/resume/index.<lang>.md`, single page, not a
list): `title`, `experience` (list of `{date_range, location,
organization?, organization_url?, role, highlights[]}` — `organization`
omitted for entries with no employer), `education` (list of
`{date_range, institution, institution_url, degree, details}`),
`skills` (`{programming_languages, operating_systems, libraries}`,
each a prose string), `spoken_languages` (list of strings). `venue`-
style fields (`highlights`, `skills.*`) may contain inline Markdown
links — render through `markdownify`. See `CLAUDE.md` for full field
rationale.

## Out of scope for this brief
- Hosting/deployment mechanics (GitHub Actions build, container vs scp) —
  unrelated to visual design.
- Content writing — all copy will be filled in directly in the Markdown
  files.
- Bilingual content-authoring workflow (translationKey, tag translation
  policy) — see `CLAUDE.md`, not relevant to CSS/layout work.