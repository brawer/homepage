# CLAUDE.md — brawer.ch

Personal Hugo site for Sascha Brawer. Deployed via GitHub Actions
(exact deploy target — container vs. scp — not yet decided). Working
in a content-first order: filling in real content before building
templates/CSS via `/design` mode.

## Site structure

- Sections: Art (`/art/`), Projects (`/projects/`, no entries yet —
  renamed from "Programming" partway through; if you see "Programming"
  or `/programming/` anywhere it's stale and should be fixed),
  Publications (`/publications/` — renamed from "papers" partway
  through; if you see "papers" anywhere it's stale and should be
  fixed), Résumé (`/resume/`).
- Menu order (see `hugo.toml` weights): Résumé, Projects,
  Publications, Art.
- Homepage (`content/_index.*.md`) is deliberately just a greeting.
  Intro sentence, social icons, and section links are template-driven
  from `Site.Params.intro`, `Site.Params.social`, and
  `Site.Menus.main` respectively — not duplicated into content. Any
  homepage template needs to pull from those, not hardcode a list.

## Bilingual (EN/DE)

- `defaultContentLanguage = "en"`; English at `/`, German at `/de/`.
- Per-item content: `index.en.md` / `index.de.md` in the same page
  bundle, sharing bundle resources (images/PDFs) automatically.
- **Policy: fully bilingual, no exceptions.** Every content item needs
  both `index.en.md` and `index.de.md`, as real files — see below for
  why a symlink between them doesn't work. Missing a translation is a
  content gap to fix, not an accepted asymmetry. This reverses an
  earlier decision in this project — if you see older notes or
  content saying "German-only is fine, it just won't appear on the
  English site," that policy no longer applies.
- **Do not use a symlink for identical-content items, even though an
  earlier version of this doc recommended exactly that.** Verified on
  2026-08-24 (Hugo v0.165.0, both via the real
  `transliteration-with-icu` bundle and an isolated repro): a
  `content/.../index.de.md` that's a symlink to `index.en.md` is
  silently invisible to Hugo — it does not become a `de` page at all
  (confirmed with `hugo list all`; a real duplicate file with the
  same content, by contrast, correctly produces two pages). No error,
  no warning, nothing in the build log — `git ls-files -s` showing
  mode `120000` only proves *git* sees it as a symlink, it says
  nothing about whether *Hugo* renders it. If identical text is ever
  wanted in both languages again, write a real second file with that
  text — never a symlink. `transliteration-with-icu/index.de.md` was
  converted from a symlink to a real (translated) file for this
  reason.
- Internal Markdown links are hand-written per language:
  `/tags/memes/` on English pages, `/de/tags/memes/` on German pages.
  Hugo does not auto-localize plain Markdown links — easy to get
  wrong when copy-pasting between language files.
- **No known bilingual gaps** as of 2026-08-24 — every content bundle
  has real `index.en.md` and `index.de.md` files, cross-checked
  against `hugo list all`'s page inventory (see "Verifying content
  structure" below) to confirm Hugo actually registers both as pages,
  not just that both exist on disk. Enforced automatically by
  `.github/workflows/check-content.yml` on every push/PR —
  fails if any page has zero translations (via Hugo's own
  `.Translations`, not a filename-matching reimplementation) or if
  any file under `content/` is a symlink.

## Typography (applies to content, not just templates)

- German content follows **Swiss conventions (de-CH)**, not
  German-German. Quotes: «guillemets» for double, ‹single guillemets›
  for nested — not „low-high" or ‚low-high'. No space between the
  guillemet and the text: «wie er sagte», not « wie er sagte ».
  Also de-CH drops ß in favor of ss throughout.
- English content: “curly double” / ‘curly single’ quotes.
- Dashes: English uses em dash (—, no surrounding spaces). German
  uses en dash (–, with surrounding spaces on both sides).
- Write these characters directly in Markdown source — don't rely on
  Goldmark's typographer extension to produce them automatically; its
  substitution table isn't per-language and won't produce guillemets.
  **This is enforced, not just advised**: `hugo.toml` explicitly sets
  `[markup.goldmark.extensions.typographer] disable = true`. It was
  briefly *not* disabled (Hugo's default), and while building the
  first real templates (2026-08-24) that turned out to have silently
  auto-converted several straight apostrophes in English content to
  curly ones at render time — the page looked correct, but the source
  was wrong and nothing said so. Content must be correct at the
  source; the build must not paper over it.
- `hugo.toml`'s `[languages.de]` block sets `locale = "de-CH"` (not
  plain `de`) specifically to flag this convention, even though the
  language *key* (and therefore file suffixes/`de` URL prefix) stayed
  `de` — renaming the key would have forced renaming every German
  content file in the repo, which wasn't worth it just to change one
  config string. (This field used to be named `languageCode`; renamed
  to `locale` when fixing Hugo's deprecation warning for it — same
  value, same purpose.)
- Fully retrofitted as of 2026-08-24, verified by
  `scripts/check_typography.py` (also wired into CI, see "Verifying
  content structure" below) — a real YAML-aware scan of every
  language's front matter *and* body, not a Markdown-body-only grep.
  That distinction mattered in practice: the grep-based version of
  this check (used until this session) only ever looked at German
  content and only at the Markdown body, so it missed straight
  apostrophes in **English** content (masked by the typographer
  extension, see above) and a straight quote inside a **front-matter**
  field (`resume`'s `experience[].highlights[]`, and a `"database"` in
  `programming-techniques-in-cl`'s body that had been fixed in German
  but never in English) — all now fixed. If you see a violation again,
  it's new content that skipped review, not a known pre-existing gap.
- See `DESIGN_BRIEF.md` for the template-side implications (don't
  hardcode straight quotes/plain hyphens in UI chrome strings).

## Tags (taxonomy)

- `[taxonomies] tag = "tags"` in `hugo.toml`.
- Some tags share one term across both languages (e.g. `Memes`,
  `Google`, `Unicode` — loanwords/proper nouns, deliberately not
  translated). These need no dedicated tag page or `translationKey`
  at all — verified via `hugo build` that Hugo auto-pairs
  auto-generated term pages across languages whenever the term string
  is identical, e.g. `Google` used on both an English and a German
  item's `tags` list produces `/tags/google/` and `/de/tags/google/`
  that are already `.Translations` of each other, with no
  `content/tags/google/` files needed.
- Some tags are translated (`Animals`/`Tiere`, `Oil`/`Öl`,
  `Open Source`/`Quelloffen`) — each pair lives at
  `content/tags/<term>/_index.<lang>.md` in *different* folders, and
  each page MUST carry a matching `translationKey` (e.g.
  `tag-animals`) so Hugo knows they're the same concept — unlike the
  shared-term case above, it can't auto-pair different strings.
  Verified: without `translationKey`, two differently-named term pages
  are just unrelated pages with no language switcher link between
  them. Naming convention: `tag-<english-term-lowercase>` (e.g.
  `tag-memes`, `tag-oil`, `tag-open-source` — hyphenate multi-word
  terms).
- Tag pages can hold real body content — e.g.
  `content/tags/memes/_index.*.md` explains the "memes painted in
  oil, as a series" concept once; individual art pieces link to the
  tag page (`[Memes](/tags/memes/)`) instead of repeating it.
- Tag casing: Title Case by default (`Memes`, `Animals`, `Oil`,
  `Geo`, `NLP`), except acronyms/numeronyms with their own strong
  lowercase convention (`NLP` stays all-caps, `i18n` stays all
  lowercase — treat these as the general rule, not one-off
  exceptions).

## Art bundle front matter

`title`, `date`, `publishDate`, `tags`, `medium`, `height_cm`,
`width_cm` (deliberately two numeric fields, not one `dimensions`
string — art convention is height × width, so `height_cm` is always
the physical top-to-bottom measurement regardless of orientation),
`image` (WebP filename, shared across language variants).

## Publications bundle front matter

`title`, `date`, `publishDate`, `tags`, `kind` (one of `"talk"`,
`"paper"`, `"patent"`, `"book"`, `"lecture"` — lowercase, same value
in every language, since it's an internal value templates branch on,
not display text; translate it for display via i18n strings, e.g.
`{{ i18n (printf "kind_%s" .Params.kind) }}`, not by changing the
front matter value itself), `authors` (list, order matters —
verified against source for patents), `venue`, `abstract`.

- `venue` can contain inline Markdown links, not just plain text —
  e.g. `modellieren-raumbezogener-daten` links the coordinating body's
  name to its own site (`KOGIS` in German, `COGIS` in English — same
  body, different acronym per language, plus `swisstopo`, each with
  its own link). Templates must render `venue` through `markdownify`
  rather than outputting it as a raw string, or these links won't
  render.

- Type-specific optional fields: `degree` (thesis), `patent_number` +
  `patent_status` + `assignee` (patent — `assignee` is the entity the
  patent was assigned to, typically the employer at the time of
  invention, e.g. `"Google LLC"` — use the assignee's official current
  name (check patents.google.com), not an informal shorthand; a
  single string, same value in both
  languages since it's a fact, not display text — don't translate it
  the way `kind` gets translated for display).
- `original_title` + `original_language` (BCP-47 tag) — for when the
  source document's real title differs from the page's own working
  `title` (e.g. the Japanese patent's actual title vs. its English
  working title). This is unrelated to the EN/DE bundle mechanism —
  both language files of the same item carry the same
  `original_title`, since it's a fact about the source document, not
  about site language.
- Single-PDF items use a `pdf` field. Multi-resource items (e.g. the
  `programming-techniques-in-cl` lecture series with dozens of PDFs)
  have no `pdf` field — links go directly in the Markdown body as
  relative links to bundle resources, which Hugo resolves
  automatically; no custom front-matter schema needed for that case.
- `pdf_preview` (optional, single-PDF items only) — filename of a
  WebP raster of the PDF's first page, e.g. `"pdf-preview.webp"`.
  Added 2026-08-24: the detail page shows this instead of the curated
  `image` teaser, which exists to look good cropped in the gallery
  grid, not to represent the document itself (see "Templates" below
  for the exact fallback behavior). Generated manually, once, same
  workflow as the existing `cwebp` conversion step: `pdftoppm -f 1 -l
  1 -r 200 -png the.pdf page1 && cwebp -q 90 -m 6 -metadata icc
  page1-1.png -o pdf-preview.webp` (macOS also has `qlmanage -t -s
  2000 -o . the.pdf` built in, no install needed, as a fallback if
  `pdftoppm`/`poppler` isn't installed). Checked into git like any
  other bundle resource — not regenerated at build time, and there's
  no Hugo-native way to rasterize a PDF page even if it were (Hugo's
  image pipeline only processes already-raster formats). Same
  filename in both language front-matter files, like `image`/`pdf`.

## Resume bundle front matter

`content/resume/index.<lang>.md` (a page bundle, like art/publications,
in case a downloadable PDF or a photo gets added later). Ported from
the old `brawer.ch/cv/` page; not a Hugo taxonomy or list — it's a
single structured page, so the CV table maps to structured front
matter (like `venue`) rather than free-form Markdown, so a future
template can render it consistently (icons, timeline layout, etc.)
rather than parsing prose.

- `title` — "Resume" / "Lebenslauf", matching the nav label in
  `hugo.toml`.
- `experience` — list of jobs/roles, each with `date_range` (display
  string, e.g. `"10/2019 – 9/2021"` or `"Since 10/2021"`/`"Seit
  10/2021"` — not split into structured start/end fields, same
  reasoning as `venue`: nothing here needs to compute on the date,
  only display it), `location`, `organization` + `organization_url`
  (both omitted, not empty-stringed, for entries with no employer —
  independent work, the 2018–2019 sabbatical), `role`, and
  `highlights` (list of strings, may contain inline Markdown links —
  render through `markdownify`, same as `venue`).
- `education` — list with `date_range`, `institution` +
  `institution_url`, `degree`, `details`.
- `skills` — object with `programming_languages`, `operating_systems`
  (each a prose string, may contain Markdown links). Used to also have
  a `libraries` field; dropped 2026-08-24 (content and template both
  updated together — don't resurrect just the template side of it).
- `spoken_languages` — list of plain strings (e.g. `"English
  (fluent)"`).
- Job/institution titles are translated per language where they read
  naturally in German (e.g. the University of Zürich entry's role is
  "External Lecturer" in English but just "Lehrauftrag" in German —
  the noun for the position itself, which also appears in that
  entry's highlight text, rather than a literal "external lecturer"
  title translation),
  but industry-standard leveled titles are kept in English in both
  languages (e.g. "Senior Staff Software Engineer (L7, ...)",
  "Director of Engineering") since translating those would obscure
  their actual (internationally recognized) meaning.
- **Deliberately left out, unlike the old page**: postal address and
  birth date. The old `brawer.ch/cv/` had both; dropped when porting
  here — don't re-add without asking first, this was an explicit call
  by Sascha, not an oversight.
- The cradle.bio (2025) stint is folded into a `highlights` bullet on
  the "Since 10/2021 – Independent" entry rather than its own
  `experience` entry, since it's a specific engagement within that
  ongoing independent period, not a separate role with its own dates
  — avoids a confusing overlapping date range next to an open-ended
  "since" entry. Phrased as helping out friends in an emergency, not
  as a formal role — deliberately never says "SRE", even though the
  underlying work (kept systems running, optimized machine cost,
  wrote lab-automation scripts) was exactly that.

## Images

- Store as WebP, not JPEG/HEIC:
  `cwebp -q 90 -m 6 -metadata icc input.jpg -o output.webp`
  (`-metadata icc` preserves color profile — matters for paintings).
- Publication teaser images are manually curated per item (title
  slide, diagram, or a plain typographic card) — there's no
  automatic source the way there is for art.
- **Responsive `<picture>` rendering is already built**, verified
  2026-08-24 (this Hugo build genuinely encodes AVIF, not just WebP —
  confirmed by inspecting output file magic bytes, not just trusting
  the build not to error): `layouts/partials/picture.html` for
  full/uncropped images (detail pages) and
  `layouts/partials/picture-thumbnail.html` for square-cropped
  gallery-grid thumbnails (list/tag pages). Both emit AVIF + WebP
  srcset plus a WebP `<img>` fallback; call with
  `{{ partial "picture.html" (dict "image" $resource "alt" "…") }}` —
  see each file's own header comment for the full param list. The
  thumbnail partial's default widths (400/800/1200) are sized so the
  smallest tier is roughly 1/3 of a present-day phone's screen width,
  for a 3-column mobile grid ("similar to a photos app," Sascha's
  framing) — 800/1200 cover 2x/3x device pixel ratios on that same
  grid cell. Crop anchor is `hugo.toml`'s `[imaging] anchor = "smart"`
  (Hugo's smartcrop) — verified it picks a sensible crop on both a
  portrait art image and a wide publication teaser without any
  per-image override, but that's not guaranteed for every future
  image; revisit with an explicit anchor param if a particular crop
  looks wrong once there's an actual page to view it on.

## Git LFS

- `*.webp` and `*.pdf` are tracked via `.gitattributes`.
- CI checkout MUST use `actions/checkout@v4` with `lfs: true`, or
  PDFs/images silently come through as broken LFS pointer files
  instead of actual content — easy to miss since the build won't
  error, it'll just produce a broken site.

## Verifying content structure

No templates exist yet, so `hugo build` can't render pages, but it's
still the right tool to sanity-check content/config — it parses every
front matter file and wires up taxonomies/menus/bundles regardless of
whether there's a layout to render them with:

- `hugo build` (or `hugo config`) — fails loudly on YAML syntax errors
  or bad `hugo.toml`. A clean exit with only "found no layout file"
  warnings means content/config are structurally sound.
- `hugo list all` — the authoritative page inventory (path, kind,
  permalink; no built-in translation-count column, but the `path`
  column tells you which files Hugo actually turned into pages). Use
  this, not `git ls-files`, to confirm bilingual coverage: cross-check
  that every `index.de.md`/`_index.de.md` path git knows about also
  shows up as a `path` here — a file present in git but missing from
  this list didn't become a page (that's exactly how the symlink
  pitfall above was caught: `git ls-files -s` showed the `.de.md`
  path just fine, `hugo list all` didn't list it at all).
- `hugo build` always writes `/public/` and `/resources/` and creates
  `.hugo_build.lock` — all three are gitignored, don't add them.
- **Bilingual coverage is enforced in CI**, not just manually: see
  `.github/workflows/check-content.yml`, added 2026-08-24.
  It rejects any symlink under `content/`, then builds the site with
  a throwaway template that ranges over every page on every language
  site and fails via `errorf` if any page has zero translations —
  using Hugo's own `.Translations`, the same mechanism `hugo list
  all` cross-checking relies on above, not a hand-rolled
  filename-matching reimplementation (which would have missed the
  symlink bug, same as `git ls-files -s` did).
- **Resource-reference coverage is also enforced in CI**: the same
  workflow's second step fails if any page's `image`/`pdf`
  front-matter field doesn't resolve to an actual bundle resource
  (checked via `Resources.GetMatch`, same ground-truth-over-filesystem
  reasoning as the translation check).
- **Typography and LFS integrity are also enforced in CI**, added
  2026-08-24: `scripts/check_typography.py` (a real YAML-aware
  front-matter + body scan, both languages — see the Typography
  section above for why this replaced an earlier grep-only,
  German-only, body-only version that missed real violations) runs as
  a CI step via `pip install pyyaml && python3
  scripts/check_typography.py`; run it locally the same way. A
  separate step checks every LFS-tracked `*.webp`/`*.pdf` isn't an
  unresolved pointer file. When testing *shell/grep*-based CI checks
  locally on macOS specifically: note this environment aliases the
  `grep` command to `ugrep`, which is more permissive than either BSD
  grep (macOS default) or GNU grep (Ubuntu, what CI actually runs);
  test with `/usr/bin/grep` explicitly if you need to verify true
  portability of a grep-based check.
- **Still not covered by CI** (deliberately, filed as follow-up
  issues rather than built now): internal Markdown link resolution
  (hand-written per-language links like `/tags/memes/` vs.
  `/de/tags/memes/` aren't validated against real page URLs — Hugo
  doesn't check plain Markdown links itself), and front-matter schema
  validation (required fields per `kind`/section aren't enforced
  anywhere; currently caught by review, which won't scale once
  `content/projects/` has entries and the content set grows).

## Templates (bare-bones, pre-/design)

A first functional template pass exists as of 2026-08-24 — deliberately
minimal/near-zero CSS (`static/css/main.css`), built to prove the
content/data model actually renders correctly end-to-end (including
the specific things most likely to have hidden problems:
`markdownify` fields, the lecture-series body-only content, one
shared grid across three content types) *before* either adding a lot
more content or committing to real visual design. Real visual design
is still entirely `/design` mode's job — nothing here should be taken
as a design decision, just a structural one.

- `layouts/_default/baseof.html` + `head.html`/`nav.html`/
  `language-switcher.html`/`social-icons.html`/`footer.html` partials
  — the shared page shell. Nav and social icons are template-driven
  from `Site.Menus.main`/`Site.Params.social`, per the Homepage bullet
  above. The language switcher hides itself via `.IsTranslated` rather
  than ever linking to a 404 — belt-and-suspenders alongside the CI
  bilingual-coverage check, not a replacement for it (CI only guards
  `main`; a page can briefly lack a translation in a local working
  tree while it's being authored, and the template shouldn't assume
  otherwise).
- `layouts/partials/gallery-grid.html` — the one shared grid component
  for Art/Publications/Projects list pages *and* tag pages, per
  DESIGN_BRIEF. Used by `layouts/_default/list.html` and
  `layouts/_default/term.html`, which are otherwise nearly identical
  (list pages differ from tag pages only in where `.Pages` comes
  from — Hugo handles that automatically).
- Per-section detail templates: `layouts/art/single.html`,
  `layouts/publications/single.html`, `layouts/resume/single.html`,
  `layouts/projects/single.html` (untested against real content —
  `content/projects/` is still empty — but matches the documented
  schema). The publications template does **not** special-case
  `kind == "lecture"` structurally: `programming-techniques-in-cl`'s
  body is already valid Markdown (headings, lists, a definition list)
  with no `pdf` field, so plain `.Content` renders it correctly as-is.
  Making it *look* like a grouped table/accordion rather than a plain
  list remains a CSS/`/design`-mode concern, per DESIGN_BRIEF — it was
  never actually a templating problem, just looked like one before
  anyone had built and looked at it.
- Publications detail page's hero image: `pdf_preview` if present, else
  falls back to the `image` teaser (added 2026-08-24, so the
  lecture-series item — no `pdf_preview`, no single PDF to preview —
  keeps showing its teaser unchanged). The gallery grid always uses
  `image` regardless — the two are deliberately independent fields,
  not a "detail page mode" switch on one field, so they can vary
  independently. Kept as its own isolated block in the template (not
  folded into general image-handling logic) specifically so an inline
  PDF embed/viewer can be added later as a sibling to it, near the
  "Download PDF" link, without restructuring this.
- `i18n/en.toml` + `i18n/de.toml` — every piece of UI chrome text
  (kind badges, "Download PDF", resume section headings, etc.) is a
  key here, translated for both languages, per the fully-bilingual
  policy applying to chrome as much as content.
- Verified concretely, not just "the build didn't error": inspected
  actual rendered HTML output for the home page, an art detail page,
  a standard publication, the patent (kind-specific fields), the
  lecture-series item (body-only rendering), the resume (nested
  `experience`/`education`/`skills`, `markdownify` on `highlights`),
  a tag page, and the language switcher on a translated page.
- The "H × W cm" art dimension string uses U+202F (narrow no-break
  space) around the × and before "cm" — non-breaking *and* narrower
  than a plain space (the correct typographic spacing here, not just
  a line-break fix). Written as the numeric HTML entity `&#x202F;`
  (hex form — matches the U+202F name directly, clearer than the
  decimal `&#8239;` equivalent) in template source text, deliberately
  *outside* any `{{ }}` action —
  Go's `html/template` auto-escaper would mangle it (double-escape the
  `&`) if it were inside a string an action returns. If you need this
  elsewhere, copy that pattern, not a `{{ printf "... ..." }}`
  approach — writing `\uXXXX` inside a Go template action's string
  literal is fragile in an AI-assisted editing workflow specifically:
  it reads as a JSON/text unicode escape to tooling upstream of the
  file write, not as literal source text, and silently resolves to
  the raw (nearly invisible) character instead of staying as legible
  escape text. Verified this exact failure mode while building this.

## Known open items (as of last content session)

- `/design` mode: real visual design (color, type scale, spacing,
  the lecture-series list treatment, resume icons/timeline, deciding
  actual grid aspect ratio/column counts beyond the current bare
  hard-coded 3-column square grid) — everything in the "Templates"
  section above is structural/functional only.
- `content/resume/` still has no icons/timeline layout — see the
  "Resume bundle front matter" section above.
- Section list pages (`content/art/_index.*.md`,
  `content/publications/_index.*.md`,
  `content/projects/_index.*.md`) don't exist yet. Optional —
  Hugo auto-generates a bare list page without them — but worth
  adding for section-level intro copy, same pattern as the tag pages.
  Until these exist, list-page `<h1>` titles are Hugo's un-translated
  auto-generated section names (e.g. always "Art", never "Kunst") —
  a known, minor bilingual gap in UI chrome, not content.
- `content/projects/` has zero entries — `layouts/projects/single.html`
  exists but is unverified against real content.