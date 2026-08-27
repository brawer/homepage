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
- Imprint (`/imprint/`, legal notice — titled "Impressum" on the
  German page) is not a section and not in the main nav — a single
  standalone page, linked only from the per-page footer. See "Imprint
  bundle front matter" below.
- Homepage (`content/_index.*.md`) is deliberately just a greeting.
  Intro sentence, location, social icons, and section links are
  template-driven from `Site.Params.intro`, `Site.Params.location`,
  `Site.Params.social`, and `Site.Menus.main` respectively — not
  duplicated into content. Any homepage template needs to pull from
  those, not hardcode a list. Note `intro`/`location` are per-language
  (set inside each `[languages.<lang>.params]` block in `hugo.toml`,
  since they're translated text) while `social` is the shared,
  language-independent `[params.social]` block (same URLs regardless
  of language) — different data sources, both rendered near each
  other on the page (`layouts/partials/social-icons.html`).

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
  `Open Source`/`Quelloffen`, `People`/`Menschen`) — each pair lives at
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
- **Tag order on art pieces: subject-matter tags first, `Oil`/`Öl`
  last** — e.g. `["Memes", "Animals", "Oil"]`,
  `["Tools", "Oil"]`, `["People", "Oil"]`. `Oil` is the shared
  medium/technique tag nearly every piece carries, so it trails as
  the least specific descriptor; subject tags (what the piece
  depicts) lead. Retrofitted 2026-08-24 across all existing pieces
  for consistency — before that, order was inconsistent (some had
  `Oil` first).

## Art bundle front matter

`title`, `date`, `publishDate`, `tags`, `medium`, `height_cm`,
`width_cm` (deliberately two numeric fields, not one `dimensions`
string — art convention is height × width, so `height_cm` is always
the physical top-to-bottom measurement regardless of orientation),
`image` (WebP filename, shared across language variants).

- `teaser` (optional, WebP filename) — added 2026-08-24. Grid views
  (list/tag pages) always show a square crop of the thumbnail (see
  DESIGN_BRIEF), auto-cropped from `image` via Hugo's smart anchor.
  That's a good enough default for most pieces, but not guaranteed
  for every aspect ratio/composition — `teaser` lets a piece use a
  separate, manually-curated near-square image for the grid instead,
  without changing what the detail page shows full-size. No current
  art piece needs one (all three existing pieces are already square
  paintings), but future landscape/portrait pieces might. Same
  pattern as publications' `image`-as-teaser vs. `pdf_preview`-on-detail
  split below — gallery-grid.html prefers `teaser` over `image` for
  any content type that sets it, not just art.
- **Deliberately not adding a `kind` field to art**, discussed
  2026-08-24 ahead of Sascha adding non-oil pieces (sketches,
  watercolors). Instead, `medium` (already required, already free
  text like `"Oil on canvas"`) does double duty as the art equivalent
  of publications' `kind` badge in the gallery grid — implemented the
  same day, see `gallery-grid.html`. Unlike publications, medium
  doesn't drive different required fields or template branches per
  type, so a whole new controlled-vocabulary field would have existed
  only to feed a badge that `medium` can feed directly. The existing
  `Oil`/`Öl` tag is unaffected/unchanged — it answers a different
  question (cross-cutting browse via `/tags/oil/`) than the per-item
  badge does, same relationship publications already have between
  their `kind` badge and topical tags like `Geo`/`NLP`. If a medium
  ever needs a field oils don't (e.g. sketches wanting a "sketchbook
  page #"), *that's* the actual signal for a real `kind` split — not
  this.
- **Superseded 2026-08-25, grid only**: `medium` no longer feeds a
  gallery-grid badge. NAVIGATION_DESIGN_SPEC.md §4 wants grid badges
  used "only where they carry information the thumbnail can't" — art's
  image is already unambiguous, so art tiles now show no badge at all.
  `medium` itself is untouched and still required, still shown on the
  art detail page's caption line (`layouts/art/single.html`) exactly as
  before — only `gallery-grid.html`'s badge branch changed. Publications
  and Projects tiles similarly dropped their `kind`/`role`-text badges
  in favor of a generic format glyph ("PDF" / `</>`) — see "Templates"
  below.
- **Superseded again, 2026-08-26**: the generic glyph badges above
  didn't survive real design review either — "PDF" is true of a
  patent, a talk, a lecture series, and a paper alike, so it carried
  almost no information for its ink. Replaced site-wide by a new
  `kind_label` field (see "Templates" below for the full rationale,
  shared across all three content types) — every art piece now has
  `kind_label: "Oil Painting"` / `"Ölgemälde"`. Deliberately a new
  field, not a repurposing of `medium` (which stays exactly what it
  was: required, free text, shown on the detail page) — `kind_label`
  is purely the grid's own short display string, and the two are free
  to diverge (a future sketch might have `medium: "Graphite on paper"`
  but still choose a `kind_label` like "Sketch" rather than something
  automatically derived from `medium`).
- `teaser_is_document` (required boolean, added 2026-08-26 alongside
  the grid port) — every current art piece is `false`. Controls the
  grid's document wash/filter/blur treatment (see "Templates" below);
  deliberately hand-set per item rather than derived from section, so
  a future black-and-white sketch could set this `true` if its teaser
  would genuinely benefit from the same treatment scanned documents
  get — oil paintings' vivid color is exactly why they're `false`
  today, not a rule about art as a section.
- `dimensions_text` (optional) — added 2026-08-27 for
  `are-you-a-human`, a one-off 3×3 grid of nine separate 40×40cm
  panels. `height_cm`/`width_cm` alone render as plain "H × W cm" (see
  above), which would misrepresent this piece as a single 40×40
  canvas; `dimensions_text`, when present, overrides that whole
  computed caption segment with a hand-authored string instead (here:
  `"40 × 40 cm each, nine parts (3 × 3 grid)"` /
  `"40 × 40 cm pro Bild, neunteilig (3 × 3-Raster)"`).
  `height_cm`/`width_cm` stay required and still describe one panel —
  only the *display* is overridden. Deliberately a hand-authored
  override rather than a general multi-panel schema (e.g.
  `panel_count`/`grid_rows`/`grid_cols` fields driving a computed
  string): Sascha doesn't expect to paint more grids like this, so
  per-item text is simpler and more maintainable than building
  composition logic for what may stay a single occurrence — same
  reasoning as `kind_label` being hand-authored rather than derived.
  Its `×` signs use the same U+202F (narrow no-break space) as the
  computed "H × W cm" string, typed as the raw character directly in
  the content string (verified via a small Python script reading the
  file back and checking codepoints, not by trusting what looked
  right when typed — see the `\uXXXX`-fragility note under
  "Templates" below) rather than as HTML entities, since this flows
  through `.Params` as page data, not as template source text; Go's
  auto-escaper only touches `<>&"'`, so the raw character survives
  untouched the same way the résumé's `date_range` dash does.

## Publications bundle front matter

`title`, `date`, `publishDate`, `tags`, `kind` (one of `"talk"`,
`"paper"`, `"patent"`, `"book"`, `"lecture"` — lowercase, same value
in every language, since it's an internal value templates branch on,
not display text; translate it for display via i18n strings, e.g.
`{{ i18n (printf "kind_%s" .Params.kind) }}`, not by changing the
front matter value itself), `kind_label` (grid-badge display text, see
"Templates" below — usually just the translated `kind`, e.g. `"Talk"`/
`"Vortrag"`, but not always: `JP6511221B2` uses `"Japanese Patent"`/
`"Japanisches Patent"` instead of plain "Patent", since the original
document being Japanese is genuinely informative and worth surfacing
at a glance), `teaser_is_document` (required boolean — whether the
grid teaser gets the document wash/filter/blur treatment; `true` for
`JP6511221B2`, `modellieren-raumbezogener-daten`, and
`programming-techniques-in-cl`, all genuinely flat scans/diagrams;
`false` for `transliteration-with-icu`, whose teaser is a colorful
geographic map, not a flat document — proof this has to be a per-item
call, not a blanket "all publications" default), `authors` (list,
order matters —
verified against source for patents), `venue`, `abstract`.

- `venue` can contain inline Markdown links, not just plain text —
  e.g. `modellieren-raumbezogener-daten` links the coordinating body's
  name to its own site (`KOGIS` in German, `COGIS` in English — same
  body, different acronym per language, plus `swisstopo`, each with
  its own link). Templates must render `venue` through `markdownify`
  rather than outputting it as a raw string, or these links won't
  render.
- **Markdownify footgun, found and fixed 2026-08-25**:
  `transliteration-with-icu`'s German `venue`, `"34. Internationalization
  & Unicode Conference (2010)"`, silently rendered as an HTML `<ol
  start="34">` instead of plain text — `markdownify` parses a string
  starting with `<number>. ` as the start of a Markdown ordered list,
  block-level, with no visual warning at build time (byline just grew
  an odd line break around it). The English `venue` (`"34th
  Internationalization..."`) didn't trigger this, since `th` breaks
  the ordered-list pattern — the bug is specific to German ordinal
  style (`34.`, not `34th`). Fixed by escaping the period:
  `venue: '34\. Internationalization & Unicode Conference (2010)'` —
  note the **single-quoted** YAML string, not double-quoted: YAML's
  double-quote form treats `\.` as an invalid escape sequence and
  fails to parse, while single-quoted YAML strings pass the backslash
  through literally, letting Markdown's own escaping handle it. Any
  `markdownify`-rendered field (`venue`, `abstract`, résumé
  `highlights`, art/publications teaser-adjacent prose) that happens
  to start with a numeral immediately followed by `. ` needs the same
  escape — checked all current content for this pattern (none other
  found) but it's worth rechecking whenever new content is added to a
  markdownified field.

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
  working title, or the spatial-data book's German original vs. its
  English working title). In practice only ONE language file of the
  pair carries it — whichever file's own `title` differs from the
  real source title (e.g. `modellieren-raumbezogener-daten`'s EN file
  has it, pointing at the German original; the DE file doesn't need
  it, since DE's own title already *is* the real title). (An earlier
  version of this note said both files always carry it — that was
  never actually true of any real item; corrected 2026-08-24.)
  Rendered as `Original title ({{Language}}): {{title}}` — the
  `{{Language}}` name shown is localized to the *site's* current
  language via an i18n key `language_name_<code>` (e.g.
  `language_name_ja` → "Japanese"/"Japanisch"), not the raw BCP-47
  code and not the named language's own name for itself. Add a new
  `language_name_<code>` pair to **both** `i18n/en.toml` and
  `i18n/de.toml` whenever a new `original_language` value shows up in
  content, or that page will show a literal missing-translation
  string instead of a name. Separately, the actual title text itself
  is wrapped in `<span lang="{{original_language}}">` — correct
  per-span language tagging for assistive tech/browsers, independent
  of which name is shown in the label.
- Single-PDF items use a `pdf` field. Multi-resource items (e.g. the
  `programming-techniques-in-cl` lecture series with dozens of PDFs)
  have no `pdf` field — links go directly in the Markdown body as
  relative links to bundle resources, which Hugo resolves
  automatically; no custom front-matter schema needed for that case.
- `pdf_preview` (optional, single-PDF items only) — filename of a
  WebP raster of one page of the PDF, e.g. `"pdf-preview.webp"`.
  Added 2026-08-24: the detail page shows this instead of the curated
  `image` teaser, which exists to look good cropped in the gallery
  grid, not to represent the document itself (see "Templates" below
  for the exact fallback behavior). Generated manually, once, same
  workflow as the existing `cwebp` conversion step: `pdftoppm -f N -l
  N -r 200 -png the.pdf pageN && cwebp -q 90 -m 6 -metadata icc
  pageN-N.png -o pdf-preview.webp` (macOS also has `qlmanage -t -s
  2000 -o . the.pdf` built in for page 1 specifically, no install
  needed, as a fallback if `pdftoppm`/`poppler` isn't installed).
  **Which page (`N`) is an editorial call, not always page 1** — pick
  whichever page best represents the document. Default assumption is
  page 1 (the title page) unless told otherwise; `modellieren-
  raumbezogener-daten` deliberately uses page 7 instead (Sascha: the
  book's own chapter-by-chapter overview reads better than its title
  page). If asked to change one, regenerate with the same two
  commands at the requested page number — don't just assume page 1.
  Checked into git like any other bundle resource — not regenerated
  at build time, and there's no Hugo-native way to rasterize a PDF
  page even if it were (Hugo's image pipeline only processes
  already-raster formats). Same filename in both language front-matter
  files, like `image`/`pdf`.

## Projects bundle front matter

`content/projects/<slug>/index.<lang>.md`. First real entry added
2026-08-25 (`text-rendering-tests`); before that this section only
described the intended schema. Replaces an earlier placeholder shape
(`open_source` bool + single `link` field, still visible in old
`DESIGN_BRIEF.md` history) that predated any real requirements —
don't resurrect it.

- `title`, `date` (start of Sascha's involvement — also drives default
  chronological sort on `/projects/`, same role `date` plays for
  art/publications), `publishDate` (same convention as elsewhere: the
  day the page was added to the site, not the project's real-world
  date), `tags`, `image` (WebP teaser, optional — see below), `teaser`
  (optional override, same escape hatch as art/publications).
- `end_date` — optional integer year, e.g. `2021`. Omitted (not
  empty-stringed) for ongoing projects. Combined with `.Date` (the
  existing required `date` field, reused as the start year rather
  than adding a redundant `start_date`) to COMPUTE the byline's date
  phrase: `"Since {year}"` when absent, `"{start}–{end}"` when present
  — changed 2026-08-25 from an earlier free-form `date_range` string,
  on Sascha's call: generating it from structured fields is less
  fragile than hand-writing the string per entry. The résumé's
  `date_range` deliberately stays free-form, unlike this — that page's
  entries have genuinely heterogeneous precision/phrasing (some just
  a month/year, some `"Since 10/2021"`, one a single date) that a
  `start`+`end` pair can't cleanly cover, whereas every project entry
  needs only a plain year on each end. The closed-range case's
  narrow-no-break-space-wrapped dash uses the HTML-entity-outside-
  any-action pattern (`&#x202F;&ndash;&#x202F;`), same as art's "H × W
  cm" (see "Templates" below) — not the résumé's raw-character
  `replace()` trick, since there's no pre-formatted string to
  `replace()` here; the year values come straight from `.Date` and
  `.Params.end_date`.
- `status` — one of `"active"`, `"inactive"`. **This describes whether
  SASCHA is still actively involved in the project right now** — not
  whether the project/repo itself is alive, maintained, or archived
  upstream. Deliberately a separate field from `end_date` rather
  than derived from it (e.g. from whether `end_date` is present):
  they answer genuinely different questions, and parsing one out of
  the other would be fragile. Rendered as its own separate byline
  segment via `project_status_<value>` i18n keys, joined onto the
  rest of the byline (role/date/status) with a literal middle dot
  (·) — fixed 2026-08-25 from an initial `dash_separator` guess, on
  Sascha's nitpick: the byline should match the separator art's
  caption and publications' byline already use, not the résumé's
  em/en dash_separator (which is specific to that page's
  date_range+location join). **Deliberately NOT fused into the date
  phrase either** (e.g. not "Active since 2016") — tried that on
  2026-08-25 and reverted same-day on Sascha's correction: it
  overstated current engagement on projects he's still nominally
  involved in but not "super-active" on, so `status` needs to stay
  readable on its own rather than getting folded into an adjective
  in front of the year.
  **"Active" is about ongoing responsibility/involvement, not recent
  commit frequency** — clarified 2026-08-25 on `text-rendering-tests`:
  Sascha is still nominally the maintainer and still considers himself
  involved even though he "hasn't done much recently." Use `active`
  for "I'm still the person responsible for/involved in this, even at
  low intensity"; reserve `inactive` for projects Sascha has genuinely
  stepped away from (no longer the point of contact, regardless of
  role).
- `role` — one of `"creator"`, `"maintainer"`, `"contributor"` —
  lowercase internal value like publications' `kind`, translated for
  display on the project's own detail-page byline via `role_<value>`
  i18n keys (unchanged). It no longer feeds a gallery-grid badge as of
  2026-08-25 — see "Superseded 2026-08-25, grid only" under "Art
  bundle front matter" above; the grid now shows a generic `</>` glyph
  for every project tile regardless of `role`, per
  NAVIGATION_DESIGN_SPEC.md §4. **Single value,
  not a list**, even though a project can genuinely be more than one
  (e.g. `text-rendering-tests`: Sascha both created and still
  maintains it) — a list would break the one-badge-per-item pattern
  every other section already uses. When more than one applies, use
  this precedence: `creator` > `maintainer` > `contributor` — flipped
  2026-08-25 from an initial "maintainer wins" guess, on Sascha's call:
  `creator` is the stronger, more distinctive signal of impact on a
  portfolio site (originating something beats upkeeping it), so it
  should win the one available badge slot over `maintainer` when both
  are true. Ongoing-maintainer status, if relevant, can still show up
  in the prose/body (as it does on `text-rendering-tests`) or in
  `status`/`end_date`, which already cover "is Sascha still
  involved."
- `kind_label` — required, added 2026-08-26 (`text-rendering-tests`:
  `"Test Suite"`/`"Test-Suite"`). The grid-badge display text — see
  "Templates" below for the full rationale (shared across all three
  content types; this is the field publications call `kind_label` too,
  see that section). Projects had no equivalent of publications' `kind`
  before this — `role` answers a different question (Sascha's
  involvement) and doesn't double as a content-type descriptor the way
  `kind` does for publications, so this is a genuinely new field, not
  a rename or repurposing of anything existing.
- `teaser_is_document` (required boolean, added 2026-08-26 alongside
  the grid port) — `true` for `text-rendering-tests` (a genuine code/
  test-suite screenshot). Same field and rationale as publications'
  and art's — see either of those sections; not re-explained per
  section.
- `summary` — one or two plain-text sentences (may contain inline
  Markdown, rendered via `markdownify`), the short blurb shown on the
  detail page. Plays the role publications' `abstract` plays. Keep it
  short by design — longer text belongs in the Markdown body, which is
  optional and can be a sentence or two, not a full write-up.
- `github_url` (optional, single string) — the canonical repo link, a
  dedicated field like the résumé's `organization_url`/
  `institution_url`, not a generic `links` list, since GitHub is the
  one link type nearly every entry has and there's no current need for
  more than one repo link per project. Omit (don't empty-string) for
  proprietary/private projects with no public repo.
- `related_publications` (optional list of strings) — slugs of
  `content/publications/<slug>` bundles this project has an associated
  talk/paper/patent for (most projects have none; only a few do). The
  template resolves each via `site.GetPage`, rendering that item's own
  already-translated `kind` + title + link — deliberately not
  duplicating title/kind data here, and it covers both "talk" and
  "paper" cases through one field since `kind` already distinguishes
  them on the publications side.
- Tag order: subject-matter tags first, then any language/technology
  tag (e.g. `Rust`, `C++`), then `Open Source`/`Quelloffen` last if the
  repo is actually public — extends the same "generic descriptor
  trails" convention already used for `Oil` on art (see "Tags" above).
  Only tag `Open Source` when the repo genuinely is public.
- No `image` yet on `text-rendering-tests` — teaser images for
  projects are meant to be manually curated per item, same as
  publications' teasers (no automatic source), and none has been made
  yet; left as a `<!-- TODO -->` comment in the body instead of a
  fabricated placeholder image.

## Resume bundle front matter

`content/resume/index.<lang>.md` (a page bundle, like art/publications,
in case a downloadable PDF or a photo gets added later). Ported from
the old `brawer.ch/cv/` page; not a Hugo taxonomy or list — it's a
single structured page, so the CV table maps to structured front
matter (like `venue`) rather than free-form Markdown, so a future
template can render it consistently (icons, timeline layout, etc.)
rather than parsing prose.

- `title` — "Résumé" / "Lebenslauf", matching the nav label in
  `hugo.toml`. English changed from "Resume" to "Résumé" 2026-08-25
  (Sascha's call) — update both together if this ever changes again,
  per the "matching the nav label" rule.
- `experience` — list of jobs/roles, each with `date_range` (display
  string, e.g. `"10/2019 – 9/2021"` or `"Since 10/2021"`/`"Seit
  10/2021"` — not split into structured start/end fields, same
  reasoning as `venue`: nothing here needs to compute on the date,
  only display it), `location`, `organization` + `organization_url`
  (both omitted, not empty-stringed, for entries with no employer —
  independent work, the 2018–2019 sabbatical), `role`, and
  `highlights` (list of strings, may contain inline Markdown links —
  render through `markdownify`, same as `venue`).
- `education` — list with `date_range`, `location`, `institution` +
  `institution_url`, `degree`, `details`. `location` added
  2026-08-24 — originally missing, so the one education entry's
  location was jammed into the end of `details` as plain prose
  instead ("Passed with distinction. Saarbrücken, Germany."),
  rendering in a different position than `experience`'s dedicated
  `location` field. Split out for consistency: `details` is now just
  the achievement note, `location` renders in the same place
  `experience` puts it.
- **The dash between `date_range` and `location` (and between
  `degree` and `details`) is `i18n "dash_separator"`, never a
  hardcoded character** — found and fixed 2026-08-24: it had been a
  literal em dash baked into the template, which is wrong on the
  German page (de-CH wants en dash) and was never caught by
  `scripts/check_typography.py`, since that only scans *content*
  files, not template chrome. `dash_separator` is em dash (—) in
  `i18n/en.toml`, en dash (–) in `i18n/de.toml`, both spaced on both
  sides regardless of language — not the same as the "no surrounding
  spaces" em-dash rule for English prose in the Typography section,
  since this is a compact listing separator, not a sentence aside.
- `date_range` values with a real range (e.g. `"10/2019 – 9/2021"`)
  get the em/en dash inside them wrapped in U+202F (narrow no-break
  space) at render time, via `replace $exp.date_range " – " "…"` —
  same reasoning as the art page's "H × W cm" (see "Templates"
  below), but the implementation differs: this has to be the *raw*
  character, not the `&#x202f;` entity, since `replace`'s result is a
  dynamic string returned from a template action, and `html/template`
  auto-escapes such content in HTML context — a literal `&#x202f;`
  in the string would come out double-escaped as visible text
  (`&amp;#x202f;`), not render as anything. The raw character itself
  isn't touched by the escaper (`<>&"'` are the only characters it
  escapes), so it survives fine. If you need this pattern elsewhere,
  copy that, not the entity trick — and see the note in "Templates"
  below about `\uXXXX` escapes being unreliable to type through this
  tool pipeline; used a small Python script to place the exact
  codepoint reliably, verified by inspecting the actual bytes
  afterward, not by trusting what looked right when typed.
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

## Imprint bundle front matter

`content/imprint/index.<lang>.md` (a page bundle, like resume — not
a Hugo taxonomy or list). Added 2026-08-24 once Sascha mentioned he
does paid consulting work and holds a Swiss UID, which plausibly
triggers Swiss UWG Art. 3(1)(s) identity-disclosure requirements for
commercial offerings (narrower than Germany's Impressumspflicht, but
the same idea). Not linked from the main nav menu (`hugo.toml`
weights) — only reachable via a small link in the page footer
(`layouts/partials/footer.html`), rendered on every page via
`{{ with site.GetPage "/imprint" }}`, which resolves within the
*current* page's own language site automatically, so no manual `/de/`
prefixing is needed; the link label is just the page's own (already
localized) `.Title`, no separate i18n key.

- **Bundle folder is named `imprint` (the English term), not
  `impressum`** — deliberate, following the same URL-slug convention
  as `/resume/` (see "Bilingual" below): the folder name is shared
  across languages and never localized, so pick the English word for
  it regardless of which language "owns" the term. `/imprint/` and
  `/de/imprint/` both exist; the German page's `title` is "Impressum"
  even though the URL says "imprint", exactly mirroring how the
  German resume page is titled "Lebenslauf" at a URL that still says
  "resume".
- `title` only in front matter ("Imprint" / "Impressum"); everything
  else is free-form Markdown body (`layouts/imprint/single.html` is
  just `<h1>{{ .Title }}</h1>{{ .Content }}`, same minimal pattern as
  other single pages) — unlike resume, there's no future rendering
  need (icons, timeline) that would justify structured fields here.
- Content: legal name, postal address (Länggassstrasse 27, 3012 Bern),
  email (`mailto:` link), UID (CHE-484.325.065), a sentence stating
  VAT-registration exemption due to low annual turnover, and an
  explicit "this site does not use cookies" statement (true — no
  cookies are set anywhere on the site, so this was safe to state
  flatly rather than hedge).
- **Deliberate asymmetry with the resume's "no postal address"
  decision**: the resume omits the postal address (explicit call by
  Sascha, privacy preference for a CV), but the imprint page *does*
  include it, since Swiss commercial-identity disclosure is plausibly
  a legal requirement here, not a style choice — don't "fix" this
  inconsistency by adding or removing either one without asking.
- Template lives at the section-specific path
  `layouts/imprint/single.html`, not `layouts/_default/single.html`
  — following the same convention adopted after the `term.html`
  lookup bug (see "Templates" below): section-specific paths are
  known to resolve reliably in this Hugo setup, `_default/` ones
  aren't always reachable.

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

- `*.webp`, `*.pdf`, and (as of the 2026-08-26 self-hosted Karla font)
  `*.woff2` are tracked via `.gitattributes`.
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

- `layouts/_default/baseof.html` + `head.html`/`header.html`/
  `social-icons.html`/`footer.html` partials — the shared page shell.
  Location and social icons are template-driven from
  `Site.Params.location`/`Site.Params.social`, per the Homepage bullet
  above (`social-icons.html` despite its name renders both of these,
  not just social links — see its own header comment). The language
  half of `utility-nav.html` (see "Navigation, 2026-08-25" below)
  degrades gracefully via `.IsTranslated` rather than ever linking to a
  404 — belt-and-suspenders alongside the CI bilingual-coverage check,
  not a replacement for it (CI only guards `main`; a page can briefly
  lack a translation in a local working tree while it's being authored,
  and the template shouldn't assume otherwise). **`nav.html` and
  `language-switcher.html` were deleted 2026-08-25**, superseded by
  `header.html`/`drawer.html`/`primary-nav-links.html`/
  `utility-nav.html` — don't resurrect them, don't re-add either name
  as a new partial without checking this note first.
- `layouts/partials/gallery-grid.html` — the one shared grid component
  for Art/Publications/Projects list pages *and* tag pages, per
  DESIGN_BRIEF. Used by `layouts/_default/list.html` and
  `layouts/tags/term.html`, which are otherwise nearly identical
  (list pages differ from tag pages only in where `.Pages` comes
  from — Hugo handles that automatically).
  **The term.html file MUST live at `layouts/tags/term.html`, not
  `layouts/_default/term.html`** — found and fixed 2026-08-24. Every
  tag page (kind `term`) was silently rendering with
  `_default/taxonomy.html`'s content (the bare "term (count)" list
  meant only for `/tags/` itself) instead of the actual gallery grid,
  even though `.Kind` correctly reported `"term"` and a
  `_default/term.html` file existed. Confirmed empirically (not just
  from docs, which describe newer Hugo versions supposedly *not*
  cross-matching `taxonomy.html` for `term` pages — contradicted by
  what this Hugo v0.165.0 build actually does): `taxonomy.html` won
  regardless of whether `_default/term.html` existed at all, for
  every term — both ones with a backing `_index.md` (Memes) and
  purely auto-generated ones (Geo). Moving the file to the
  section-specific path `layouts/tags/term.html` fixed it
  immediately; `_default/taxonomy.html` still correctly serves `/tags/`
  itself unchanged. If you ever add a second taxonomy, verify its term
  pages the same way (`hugo build` + inspect actual rendered content,
  not just that the build didn't warn) rather than trusting
  `_default/term.html` to be reachable.
- Per-section detail templates: `layouts/art/single.html`,
  `layouts/publications/single.html`, `layouts/resume/single.html`,
  `layouts/projects/single.html` (rewritten 2026-08-25 for the real
  schema — `role`/computed-date/`status` byline, `summary`,
  `github_url`, `related_publications` — see "Projects bundle front
  matter" above; verified against the first real entry,
  `text-rendering-tests`). The publications template does **not**
  special-case
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
  "Download PDF" link, without restructuring this. That hero image and
  the `pdf` download link are, in turn, wrapped in one `<div
  class="hero">` (added 2026-08-25) — same structural change, same
  `/design`-mode-button-overlay reasoning, and same either-field
  wrapping condition (not just heroImage) as projects' `.hero`/
  `.hero-cta`, described next.
- Projects detail page's `image` and `github_url` are wrapped in one
  `<div class="hero">` (added 2026-08-25, structural-only — no CSS
  yet, ahead of a planned `/design`-mode pass to show `github_url` as
  a button overlaid on the hero image). Wrapping triggers on having
  *either* field, not just `image`, so a project with a `github_url`
  but no teaser image yet still gets its link rendered (as a plain,
  non-overlaid `<a class="hero-cta">`) instead of silently losing it
  — verified with a throwaway no-image test entry. Doing this now
  rather than in `/design` mode means the later styling pass is pure
  CSS (`position: relative` on `.hero`, `position: absolute` on
  `.hero-cta`) with no further template edit needed.
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

### Navigation, 2026-08-25

Sascha designed the site's navigation architecture separately (with
web Claude) and merged it to `main` as `NAVIGATION_DESIGN_SPEC.md` +
`WIREFRAME.html`. This subsection records the structural/behavioral
implementation of that spec — still pre-`/design`: real colors, icon
artwork, spacing, and animation stay deferred, per the spec doc and
the two files above.

- **First JavaScript in the repo**: `static/js/nav.js`, plain, no
  build step. Wires up the drawer, the fullscreen viewer, and the
  tag-page back arrow — all built on native `<dialog>`
  (`showModal()`/`close()`), which gives ESC-to-close, a native
  `::backdrop`, and native focus-trap + focus-restore-on-close for
  free. Don't hand-roll any of that.
- `layouts/partials/drawer.html` — the mobile nav drawer (Home + 4
  sections + language + imprint), rendered once in `baseof.html`.
  Opened by the `☰` trigger in `layouts/partials/header.html`
  (present on every page). `layouts/partials/primary-nav-links.html`
  is the one place `range site.Menus.main` lives, shared by the
  drawer and `header.html`'s desktop nav-bar. **The mobile-vs-desktop
  split is CSS-only** (`static/css/main.css`, ~768px breakpoint) —
  the nav-bar, the desktop utility-nav, and the drawer trigger all
  render unconditionally on every page; no template needs to know the
  viewport.
- `layouts/partials/utility-nav.html` — merged language switcher +
  imprint link, replacing the old separate `language-switcher.html`
  (deleted) and the imprint-only line that used to live directly in
  `footer.html`. `footer.html`'s call (`showImprint=true`, every page)
  is what actually gives the entry page its quiet "EN · DE · Imprint"
  row per spec §2 — `layouts/index.html` needs no separate instance.
  `header.html`'s desktop-only call passes `showImprint=false`
  (imprint stays footer-only by convention even at desktop widths).
- `layouts/partials/grid-header.html` + `chip-row.html` — the shared
  two-line grid header (title/back-arrow + item-count subtitle) and
  tag-chip row used by both `list.html` and `tags/term.html`, per spec
  §4/§5. Item-count is a flat `i18n "item_count_flat"` on section
  pages, a breakdown (`item_count_projects`/`_publications`/
  `_artworks`, each zero-omitted) on tag pages, bucketed by Hugo's
  built-in `.Section` — **not** the same thing as publications'
  unrelated `Params.kind`, same name, different concept. Tag
  co-occurrence and a section's own tag set are both deduped by
  `.RelPermalink` in an explicit `$seen` slice, checked with `in` —
  **Hugo's `union` was tried first and does NOT reliably dedupe two
  `Pages` collections returned from separate `.GetTerms` calls**
  (confirmed: produced visible duplicate chips in a real build). If
  you need to merge `Pages` collections elsewhere, dedupe by
  `.RelPermalink` explicitly rather than reaching for `union` again.
  `chip-row.html` is also reused by each detail `single.html`'s own
  tag row (moved from the bottom of the page to right after `<h1>`,
  per spec §6's fixed order).
- `layouts/partials/prev-next.html` — shared Prev/Next row on all
  three detail templates, using Hugo's built-in
  `.PrevInSection`/`.NextInSection` (section-scoped, date-descending —
  no `weight` set anywhere in current content, no config needed).
  **Hugo's `.Next`/`.Prev` naming is backwards from the visual
  direction** — found and fixed 2026-08-25, empirically (not just from
  docs), after Sascha reported the art fullscreen viewer's `N / M`
  counter moving opposite to the chevron clicked: with pages sorted
  newest-first (the same order the grid uses, unchanged), `.NextInSection`
  returns the page at the LOWER index (the newer neighbor, lower
  position number) and `.PrevInSection` returns the HIGHER index (the
  older neighbor, higher position number) — exactly backwards from
  what the method names suggest. So the visual "Prev" (‹, decrement)
  is fed by `.NextInSection`, and visual "Next" (›, increment) is fed
  by `.PrevInSection`, in both `prev-next.html` and the fullscreen
  viewer's own prev/next links in `art/single.html`. Verified against
  all 9 art pieces, including both boundary cases (position 1 has no
  "Prev"/‹, position 9 has no "Next"/›). If a similar Prev/Next needs
  building elsewhere, copy this swap, not the intuitive pairing.
- **Grid-tile badges changed** (`gallery-grid.html`): publications get
  a generic "PDF" glyph, projects a generic `</>` glyph, art none — see
  "Superseded 2026-08-25, grid only" under "Art bundle front matter"
  above for what this replaced and why the underlying fields are
  unaffected. Both use new `.badge`/`.badge-pdf`/`.badge-code` classes,
  deliberately **not** `.kind-badge` (that class still means a
  translated text pill on detail-page bylines — unchanged). The entry
  page (`layouts/index.html`) reuses these exact same classes for its
  Projects/Publications tiles, per spec §2's "same glyph... for
  consistency."
- **Art detail page got a `.hero` wrapper for the first time**
  (`layouts/art/single.html`) — only publications/projects had one
  before this. New behavior: the whole hero is one tappable `<button>`
  (not a separate overlay), no CTA button, a small ⤢ icon, opens the
  new fullscreen viewer (a second `<dialog>` on the same page,
  reusing `.PrevInSection`/`.NextInSection` for its own prev/next via
  a real page load with a `?view=full` query param that `nav.js`
  auto-reopens — not in-dialog image swapping, to avoid a second data
  source for the same adjacency `prev-next.html` already computes).
  The viewer is **art-only** — publications/projects heroes stay
  non-interactive except their existing CTA button.
- **Hero matte is a two-bucket CSS class, not per-image**: `.hero
  hero-matte-dark` (art — fixed `#2c2c2a`, deliberately does NOT
  follow system theme, gallery-framing convention) vs. `.hero
  hero-matte-light` (publications AND projects — `background: Canvas`,
  follows theme automatically with zero custom properties). Projects
  was an open question in the spec itself; Sascha resolved it as the
  light/document bucket, same as publications, not art's dark bucket.
- **Accessibility was treated as part of this structural pass, not
  deferred to `/design`** (Sascha's explicit ask): a skip link (first
  focusable element in `<body>`, jumps to `<main id="main">`), explicit
  `aria-label`s on every icon-only control (drawer trigger/close, back
  arrow, zoom, viewer close/prev/next), `aria-modal="true"` + a labeled
  `aria-label` on both `<dialog>`s (redundant with native `<dialog>`
  semantics in current browsers, kept for older AT/browser
  compatibility), `autofocus` on the viewer's close button, decorative
  images/badges marked `aria-hidden`/`alt=""` where an adjacent text
  label already carries the accessible name, and a CSS guardrail
  (comment in `main.css`) not to suppress the default `:focus-visible`
  outline on any new interactive element until `/design` mode
  deliberately restyles (not removes) it.
- **What's still explicitly deferred to `/design` mode**: the full
  light/dark custom-property token set from `WIREFRAME.html`; real
  icon artwork (placeholders stay ☰ ✕ ⤢ ← › ‹ "CV" "PDF" `</>`); chip/
  badge visual polish; drawer/viewer open/close animation; the
  detail-page "Read more" line-clamp (spec §6 itself allows unclamped
  scrolling text as an acceptable alternative — skipped entirely
  rather than building a clamp+JS-toggle now only to redo it later);
  `safe-area-inset-*` padding; the tablet/desktop two-column detail
  layout; larger circular Prev/Next buttons + arrow-key support;
  landscape-specific grid column counts/header collapse beyond what
  the responsive rules above already produce.
- **No content-model or CI-relevant changes** in this pass — no new
  front-matter fields, no `content/` edits. Confirmed
  `hugo build`/`hugo list all` output is unchanged, `check_typography.py`
  passes (though note it only scans `content/**/*.{en,de}.md`, **not**
  the new `i18n/*.toml` strings — those were reviewed manually against
  de-CH conventions instead). The interactive behavior itself
  (drawer/viewer open-close, focus handling, tag back-arrow) can't be
  verified by `hugo build` at all — it needs a manual `hugo server` +
  browser/keyboard/screen-reader check, which Sascha still needs to do
  (this session has no browser access — see the "No system automation"
  memory).

### Grid design pass ("Paper & Plum") and `kind_label`, 2026-08-26

A separate design session (an HTML/CSS Artifact mockup, not template
work directly) settled the actual visual design of the shared grid —
colors, type, shadows, and the grid badges specifically, which turned
out to need a bigger rethink than a font/color tweak. Recorded here
since it changes the content model, unlike the rest of that session's
purely visual CSS/token work (which isn't reproduced in this file —
see the mockup's own extensive inline comments for that history).

- **Grid badges retired a second time.** The 2026-08-25 fix (generic
  "PDF"/`</>` glyphs replacing translated `kind`/`role` text) didn't
  survive real scrutiny: a glyph like "PDF" is true of a patent, a
  talk, a lecture series, and a paper alike, so it carried almost no
  information for its ink — a content problem, not a legibility one,
  so no amount of contrast tuning would have fixed it.
- **Replaced by `kind_label`** — a new, required, bilingual field on
  **every** content type (art included, reversing the "no badge on
  art" call from 2026-08-25, which was specifically about a decorative
  glyph fighting the image; a quiet text label doesn't have that
  problem). Deliberately **hand-authored per item, not computed** from
  other fields (e.g. NOT derived from `kind` + `original_language` via
  template logic) — Sascha's call: there are only a handful of these
  across the whole site, so hand-authoring is simpler and more
  maintainable than composition logic for a few one-off cases. The
  fields it sits alongside (`kind` on publications, `medium` on art,
  `role` on projects) are untouched, still doing their own existing
  jobs — `kind_label` is purely the grid's display string, free to
  diverge from them (usually it's just the translated `kind` for
  publications, but not always: `JP6511221B2` uses "Japanese
  Patent"/"Japanisches Patent", not plain "Patent", since the source
  document's language is genuinely informative).
- **Stored in normal reading case** ("Test Suite", not "TEST SUITE"),
  **uppercased via CSS** (`text-transform: uppercase`) — matching how
  `i18n/en.toml`'s existing `kind_talk`/`kind_paper`/etc. are already
  stored. Not just a style call: a literal all-caps short string in
  content risks some assistive tech reading it as an acronym letter by
  letter, where CSS-driven uppercase keeps the real words in the
  accessibility tree.
- **Rendered below the title, not above** — genuinely surprised both
  of us; "category before headline" (an eyebrow/kicker, in editorial
  terms) was the more obvious pick, but it lost to Sascha's own read:
  the title is the one thing that actually differs per item (the
  focus), the kind is true of a whole category (the context), so focus
  should get the eye's attention first. Matches how card-based UI (app
  listings, product cards) usually does this, as opposed to how
  newspaper layout does it — no single established UX term covers
  this exactly ("eyebrow"/"kicker" specifically means above; Material
  Design's "supporting text" is the nearer term for below).
- All 28 existing bilingual content files (9 art × 2, 4 publications ×
  2, 1 project × 2) already carry a `kind_label` value — see the
  bundle front-matter sections above for the exact ones and their
  reasoning. Any new content item from here on needs one too, same as
  every other required field.
- **Ported into the real templates/CSS, 2026-08-26** (same day, second
  commit) — this content-model update and the actual
  `gallery-grid.html`/`static/css/main.css` port shipped together
  after all, once Sascha asked to lock in the validated design before
  it existed only in the mockup Artifact/session state. See "Known
  open items" below for exactly what shipped; header/drawer/footer got
  their own design pass and port the following day (2026-08-27) — see
  "Header/drawer/footer design pass" above.

### Header/drawer/footer design pass, 2026-08-27

A second mockup Artifact ("Paper & Plum Chrome") worked through the
page shell — header, mobile drawer, footer — the same mockup-first,
port-once-settled workflow as the grid design. Extensively iterated
with Sascha (many rounds of live feedback, several genuine bugs found
along the way); this section records the load-bearing decisions and
the reasoning that would be expensive to re-derive, not a round-by-round
transcript — see the mockup Artifact's own inline comments for that.
Ported into real templates/CSS the same day, once settled.

- **Body/main restructure, required for full-bleed header/footer**:
  `<body>` was the page's own centered/padded column before this pass
  (`max-width: 60rem; margin: 0 auto; padding: 0 1rem 3rem`) — that
  responsibility moved to `<main>` instead, since header and footer now
  need to visually extend edge-to-edge (a warm `--paper-dim` band, see
  below) while the content between them stays in the narrower centered
  column. `<body>` itself is now a `display: flex; flex-direction:
  column; min-height: 100dvh` container, with `<main>` as the one flex
  item that grows (`flex: 1 0 auto`) to absorb any leftover vertical
  space. That flex setup is doing double duty as a **viewport-anchored
  footer** (the classic pre-flexbox "sticky footer" LAYOUT TECHNIQUE —
  note this is a completely different thing from `position: sticky`,
  which is the unrelated, still-deferred résumé-only idea) — found and
  fixed after Sascha noticed on an iPad Mini simulation that a
  short-content page left the footer floating mid-screen with plain
  `--paper` visible beneath it instead of sitting at the real bottom
  edge. `100dvh`, not `100vh`: `100vh` overshoots the actually-visible
  height on mobile Safari whenever the address bar is showing;
  `100dvh` tracks the real, current viewport, and needs no
  `html { height: 100% }` companion rule the way the old pre-`dvh`
  version of this technique did (`dvh` units are viewport-relative
  already).
- **Header**: full-bleed `--paper-dim` (the same warm mat tone the
  grid tiles and footer use — see below), with a `--line` hairline
  along the bottom edge. Desktop layout is now identity-only — logo +
  the four primary sections, full stop. The header's own utility-nav
  call (language switcher, desktop-only, no imprint) was dropped
  entirely: with pages this short, showing language in both the header
  AND the footer on every page load was duplication for its own sake,
  not a real usability win. It now lives in exactly one place per
  viewport — the footer at desktop widths, the drawer at mobile widths
  (a different treatment there, see below). Logo + primary nav are
  grouped together on the left (not spread across the whole row) —
  the gap itself is the separator from nothing else being in the row,
  no divider needed. `.site-logo` gets invisible padding (no visible
  size change) so its touch target matches whichever sibling is
  already the header row's tallest at each breakpoint (40px at mobile,
  matching `.drawer-trigger`'s fixed box; ~28.4px at desktop, matching
  `.primary-links a`) — genuinely free, since the row was already
  reserving that much height for its sibling. `.drawer-trigger` and
  `.primary-links` were left untouched (already comfortably clear the
  24px WCAG touch-target floor); padding them further would have
  actually grown the header's rendered height, a real cost for no
  real gain.
- **Tonal elevation on the drawer** (`--drawer-surface`, a new token):
  the drawer's background tints toward `--accent` via `color-mix(in
  srgb, var(--paper) 88%, var(--accent) 12%)`, rather than the flat
  `--paper-raised` lighten used for small chips/buttons — a genuine
  Material 3 "tonal elevation" concept (elevated surfaces tint toward
  the theme's own color, not just lighten), tried live as a toggleable
  experiment before being made permanent. Deliberately NOT applied to
  chips/buttons (still plain `--paper-raised`) or grid tiles (still
  shadow-only, no tint) — this site only has one thing that's a
  genuine floating overlay right now; unifying every "raised" surface
  onto one mechanism would erase a real distinction (a tile is a photo
  resting flat on a table, the drawer is a page floating above the
  whole table — different physical relationships, different cues).
  **12%, not the 14% first tried** — verified with the same
  relative-luminance contrast method used throughout this project: 14%
  failed `--ink-faint` in light mode (4.45:1, under the 4.5:1 AA floor
  for text) against every text token actually used inside the drawer;
  12% clears all of them in both themes with real margin (worst case
  4.60:1 light / 4.83:1 dark). Re-verify the same way if `--paper` or
  `--accent` ever change.
- **`--accent-soft` is now derived, not hand-typed**: was a separately
  hardcoded `rgba()` tuple happening to match `--accent`'s own RGB;
  now `color-mix(in srgb, var(--accent) 10%, transparent)` (14% in
  dark mode) — mathematically identical output (verified: this is
  exactly what the spec defines the two forms to produce), so nothing
  about current rendering changed. What it buys: a future `--accent`
  hue change no longer needs `--accent-soft` hand-updated to match in
  three separate places. The alpha itself stays a deliberate,
  non-derived per-theme value (dark mode intentionally uses a stronger
  one, same reasoning as `--shadow-op-*`).
- **Drawer's close button is NOT the same fill color as the trigger,
  on purpose**: `.drawer-trigger` uses `--paper-raised`,
  `.drawer-close` uses `--paper` — everything else about them (size,
  position, icon scale) is identical ("literally the same button, just
  showing the other icon"), but `--paper-raised` has drifted close to
  `--drawer-surface`'s own tonal value in dark mode (the two were never
  designed against each other; `color-mix()` just landed them near the
  same number), so matching the close button to the trigger exactly
  would make it nearly vanish into the drawer's own background right
  when it's most needed. Verified: `--paper-raised` as a fill contrasts
  at only 1.07 against `--drawer-surface` in dark mode (practically
  invisible) vs. `--paper`'s 1.25. In light mode the two fills are
  close enough that this reads as "the same button" anyway — the
  divergence only matters, and only shows up, in dark mode. Re-check
  this pair with real numbers again if either token's formula changes.
- **`.drawer-header`/`.drawer-body` split**: the drawer used to have
  one blanket padding value for its entire contents. Found and fixed:
  that dragged the close button's position away from the exact slot
  the hamburger trigger occupied (measured — 1.75rem inset + a smaller
  button vs. the trigger's 1rem/1.1rem inset + larger button).
  `.drawer-header` now gets the SAME padding as `.site-header-inner`,
  so close lands exactly where open was tapped ("same control, now
  showing close"); `.drawer-body` (links + utility row) keeps its own,
  more generous padding independently.
- **Drawer's primary-links dividers are full edge-to-edge**, not
  scoped to each label's own width — the standard native-list
  convention (settings-style lists on both major mobile platforms):
  each row's label keeps its own inset, but the separator beneath it
  runs the full list width regardless. Implemented via a negative
  margin on each `<li>` equal to `.drawer-body`'s own horizontal
  padding (bleeding the divider out to the drawer's TRUE edge, not
  just partway), with matching padding on the `<a>` restoring the
  label's visual position — only the invisible box moved. (An
  intermediate idea — align the divider's end to the logo's own 1rem
  inset instead of the true edge — was tried and rejected: that number
  is itself just a coincidental match with the header's unrelated
  technical requirement, not a reference point anyone would actually
  perceive.)
- **Drawer's utility row is its own partial**,
  `layouts/partials/drawer-utility.html` — NOT a call to
  `utility-nav.html` (which header no longer calls at all, and
  footer.html still calls unchanged). Reasoning: opening the drawer is
  a deliberate "I'm here to act" gesture, same intent as tapping a
  primary link, so the language toggle deserves a real tap target
  instead of the marginal inline-text treatment that's still correct
  for the footer (nobody arrives there mid-task). Renders:
  - A **segmented control** (`.lang-switch`) for language, not two
    separate buttons with a gap — language is a single binary STATE
    (exactly one of {EN, DE} always selected), not two independent
    actions, so one merged pill makes "pick one of exactly two"
    visible from the shape alone. Reuses the site's existing chip
    visual language (small muted text, real tap target via padding +
    pill shape) rather than inventing a new button style. Current
    language is a plain `<span>`, not a link (mirrors
    `utility-nav.html`'s own `<strong>`-for-current convention).
  - A **plain "Imprint" link**, deliberately NOT upgraded alongside
    language — it's a one-off destination link, not a binary state,
    and stays exactly as marginal as the footer's own Imprint.
  - Both **centered as one row**, not edge-anchored — found and fixed
    twice: first tried stacked in a column (rejected: a rounded pill
    directly above flush text has an unresolvable optical-alignment
    mismatch, and even a perfect fix would still visually GROUP the
    two as if Imprint were a footnote of the language picker, which
    isn't true); then tried as a `space-between` row (rejected: with
    `.drawer-header` already anchoring logo-left/close-right, mirroring
    that same corner shape underneath made the whole panel read as
    "something in every corner"). Centering instead reuses the exact
    reasoning the page footer already uses — a quiet, self-contained
    closing block reads as "rest," not "direction," since it's the
    last thing in the drawer's own reading flow, same relationship the
    footer has to the whole page.
  - **`aria-label`s spelling out the language name** (e.g. `"DE,
    German"`, localized via the existing `language_name_<code>` i18n
    keys already used for `original_title_label`) — screen readers
    don't reliably pronounce two-letter codes as words. Combined
    "code, name" rather than just the name alone: WCAG 2.5.3 (Label in
    Name) wants the accessible name to CONTAIN the visible text, for
    voice-control users who say the visible label out loud — a bare
    `aria-label="German"` on a visibly-"DE" control would drop the
    visible label from the accessible name entirely and fail that.
    Same treatment applied to `utility-nav.html`'s own EN/DE (footer),
    which had the identical latent issue.
- **`#nav-drawer::backdrop` is scoped separately from the generic
  `dialog::backdrop`** — a fixed warm-black scrim (`rgba(26, 22, 19,
  .55)`), not theme-swapped, matching the fullscreen art viewer's own
  "dark isolating scrim doesn't need to follow the page theme"
  convention. Deliberately scoped to `#nav-drawer` only, not the shared
  `dialog::backdrop` rule — the viewer's own backdrop was never
  reviewed in this pass and stays on the original neutral value.
- **Footer**: full-bleed `--paper-dim`, same tone as the header and the
  grid tiles' own mat, plus a `--line` hairline along the TOP edge —
  header and footer now read as a matching pair of warm mat bands
  bracketing the cooler `--paper` content area between them. The
  hairline is new/symmetric with the header's: with only the header at
  `--paper-dim` (an earlier point in this same pass), the footer's
  hairline-free top edge relied on the paper/paper-dim tonal shift
  alone to read as a boundary; once both were the same tone as each
  other, that asymmetry no longer had a reason to exist, and the
  contrast is deliberately too subtle to carry the boundary alone
  either way. `.footer-inner`'s content is centered, not left-aligned
  — a short, symmetrical, self-contained closing block reads as "rest"
  when centered (no direction left to point in), where left-alignment
  is reserved for content that implies "keep reading this way."
- **`utility-nav.html` (footer's EN · DE · Imprint) rewritten as a flex
  row with one uniform `gap`**, not literal spaces/a middot-with-spaces
  baked into the text — widening the EN/DE gap for easier tapping
  without also widening the gap around the middot would leave DE
  closer to Imprint than to EN, visually implying "DE · Imprint" as a
  pair, which isn't true. One shared `gap` keeps every adjacent pair
  exactly equal. The middot is its own `aria-hidden` `<span>` — purely
  decorative, a screen reader already gets "EN, DE, Imprint" as
  distinct links without it.
- **Touch-target sizes were checked with real numbers, not assumed**
  (WCAG 2.5.8's 24×24 CSS px floor) — everything on the site now
  clears it. Two real, measured failures were found and fixed, both via
  *invisible* padding (no visible size/color change, just a bigger
  hit-box): the footer/header's EN/DE/Imprint links and the drawer's
  standalone Imprint link both measured ~20.4px tall with zero padding;
  both now measure ~30px. (The drawer's Imprint specifically needed
  this even though the footer's compound "EN · DE · Imprint" line
  might arguably qualify for the usual "inline text" exception — the
  drawer's version is its own standalone one-word paragraph, a shakier
  fit for that exception.) `.drawer-trigger`/`.drawer-close` (fixed
  40×40px), `.drawer .primary-links a` (~58px), `.lang-switch`
  segments (~32px), and `.chip` (~29px) were all already comfortably
  over the floor and needed no change.
- **Deliberately NOT done in this pass, and why**: no hover-state
  color change on grid tile titles (unlike the header/footer/drawer's
  text links) — a whole-card link already has its own hover language
  (shadow deepens + lifts, tuned during the grid design pass), and
  adding accent-colored text on top would be a redundant second cue
  for a state the card already signals clearly, not reinforcement. No
  sticky/pinned header anywhere yet — deferred specifically to the
  résumé page's own future design pass (the one page expected to be
  long enough for it to earn its keep); everything else stays
  non-sticky since short pages make the difference imperceptible.

## Known open items (as of last content session)

- **The "Paper & Plum" grid design is live, ported 2026-08-26**
  (`static/css/main.css` + `layouts/partials/gallery-grid.html`) —
  tokens (color, light+dark, self-hosted Karla via `@font-face`),
  rounded-corner/shadow tile treatment, the document wash/filter/blur
  (`teaser_is_document`-gated), `kind_label` rendering, and the
  container-query tight-tile behavior are all real now, not just in
  the mockup. Ported ahead of Sascha's own "add more art/patents
  first" plan specifically so the validated design would live in git
  rather than only in session state/the mockup Artifact — that
  content-completeness check now applies to *validating the design
  further* (more real test cases for `teaser_is_document`'s
  bidirectional override), not to whether the port itself could
  happen. Scope was deliberately the grid + the page canvas it sits on
  (body font/background/color had to move to the new tokens too, plus
  the chip row, since a page can't tastefully mix Karla-and-warm-tokens
  cards with system-font-and-Canvas chrome). Not done in this port:
  loading-performance tuning for the font (`font-display`/`preload`/
  layout-shift), explicitly deferred per Sascha's own "get the design
  working first."
- **Header/drawer/footer chrome is now also live, ported 2026-08-27**
  — see "Header/drawer/footer design pass" above for the full list of
  what shipped (tonal drawer elevation, full-bleed header/footer mat
  bands, the drawer's segmented language control, touch-target fixes,
  the viewport-anchored footer). What's left, deferred to `/design`
  mode: hero images, résumé icons/timeline layout, the lecture-series
  list treatment, and a sticky/pinned header specifically for the
  résumé page once that page's own pass happens (tracked separately,
  not sitewide — see that page's own future notes).
- **Gallery grid thumbnails now render square, fixed 2026-08-25** --
  see `static/css/main.css` git history. Root cause not fully
  re-diagnosed (the original 2026-08-24 finding below still stands as
  a data point), but the fix was straightforward: swap the previous
  `display:contents`-on-`<picture>` approach for the more standard
  container-crop pattern -- `aspect-ratio: 1/1` + `overflow:hidden`
  directly on `<picture>` itself (kept as a normal sized block box),
  with its `<img>` child stretched to fill via `height:100%` +
  `object-fit:cover`. Confirmed by Sascha via the dev server on art,
  projects, publications, and a mixed tag page. Still purely a
  throwaway fix to make broken/missing teaser images visually
  obvious ahead of real content review -- not a `/design`-mode
  decision, and the exact crop/positioning may change once that
  pass happens.
  **Follow-on bug, found and fixed 2026-08-25 (same day, separate
  session)**: individual thumbnails were correctly square, but grid
  CELLS weren't all the same size as each other -- most visible on a
  mixed tag page with very different title lengths (e.g.
  `/tags/unicode/`'s `text-rendering-tests` vs. `transliteration-with-
  icu`). Classic CSS Grid gotcha: bare `1fr` in `grid-template-columns`
  is actually `minmax(auto, 1fr)`, so each column's floor is its own
  content's min-content size (a tile's title text, if it has a long
  unbreakable word) -- NOT the aspect-ratio-cropped image, which was
  already correct. Fixed by using `minmax(0, 1fr)` instead, which
  removes that content-based floor and forces all three columns to
  always be exactly equal, plus `overflow-wrap: break-word` on
  `.gallery-item h3` as a safety net now that a pathologically long
  title can no longer widen its column.
  Original 2026-08-24 finding, kept for reference: confirmed by
  pixel-measuring a real screenshot at the time: 613×799px (ratio
  0.77), not 613×613 -- real, substantial, not a rounding thing. The
  earlier `display: contents` fix did *not* resolve it then, and
  further remote debugging wasn't productive without eyes on the
  actual DevTools computed styles -- deliberately not chased further
  at the time (the parts that mattered for that session's derisking
  goal were confirmed fine: image files genuinely square at the file
  level, `<picture>`/`<img>`/`srcset` markup standard and correct,
  grid columns computing to equal widths).
  **Detail-page images (`picture.html`, e.g. any publication's hero
  image) were never affected and need no fix** -- confirmed
  2026-08-24, still true. The square-crop bug was specifically about
  forcing an artificial 1:1 ratio to get square crops from
  non-square sources -- that's what `picture-thumbnail.html`/
  `.gallery-grid` do. `picture.html` never does this: it shows
  images at their natural shape (`.detail-image` is just
  `max-width:100%; height:auto`), and relies on the `<img>`'s real
  `width`/`height` HTML attributes (set from the actual resized
  dimensions) for layout-shift prevention -- which is standard,
  well-supported browser behavior (implicit `aspect-ratio` derived
  from those attributes) requiring no CSS `aspect-ratio` override at
  all. Different mechanism, not hit by the same failure mode.
- `content/resume/` still has no icons/timeline layout — see the
  "Resume bundle front matter" section above.
- Section list pages (`content/art/_index.*.md`,
  `content/publications/_index.*.md`,
  `content/projects/_index.*.md`) don't exist yet. Optional —
  Hugo auto-generates a bare list page without them — but worth
  adding for section-level intro copy, same pattern as the tag pages.
  (List-page `<h1>` titles are already correctly translated without
  these, by borrowing the label from `hugo.toml`'s nav menu — see
  `layouts/_default/list.html` — so that's not a reason to add them;
  section-level intro copy is.)
- `content/projects/` has one entry (`text-rendering-tests`, added
  2026-08-25) — fully reviewed and edited by Sascha (role, status,
  body prose, teaser image all real/final; the schema itself picked
  up a couple of corrections along the way, see "Projects bundle
  front matter" above). Still needs its real remaining entries: at
  least `osm-diffs` and `rust-s2` were discussed as upcoming additions
  — same schema, see "Projects bundle front matter" above.