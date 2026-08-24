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
  not just that both exist on disk. Worth adding a CI check that
  fails when a bundle has one language file but not the other, or
  when either is a symlink.

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
- `hugo.toml`'s `[languages.de]` block sets `locale = "de-CH"` (not
  plain `de`) specifically to flag this convention, even though the
  language *key* (and therefore file suffixes/`de` URL prefix) stayed
  `de` — renaming the key would have forced renaming every German
  content file in the repo, which wasn't worth it just to change one
  config string. (This field used to be named `languageCode`; renamed
  to `locale` when fixing Hugo's deprecation warning for it — same
  value, same purpose.)
- Fully retrofitted as of 2026-08-24: no remaining German-German
  „low-high" quotes or stray em dashes anywhere in `content/**/*.de.md`
  (verified by grepping for `„` and `—` across all German content —
  zero matches). If you see either again, it's new content that
  skipped review, not a known pre-existing gap.
- See `DESIGN_BRIEF.md` for the template-side implications (don't
  hardcode straight quotes/plain hyphens in UI chrome strings).

## Tags (taxonomy)

- `[taxonomies] tag = "tags"` in `hugo.toml`.
- Some tags share one term across both languages (e.g. `Memes` — a
  loanword, deliberately not translated).
- Some tags are translated (`Animals`/`Tiere`, `Oil`/`Öl`) — each pair
  lives at `content/tags/<term>/_index.<lang>.md` in *different*
  folders, and each page MUST carry a matching `translationKey` (e.g.
  `tag-animals`) so Hugo knows they're the same concept — it can't
  infer that from differing folder names the way it does for
  `index.en.md`/`index.de.md` pairs. Naming convention:
  `tag-<english-term-lowercase>` (e.g. `tag-memes`, `tag-oil`).
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
- `skills` — object with `programming_languages`, `operating_systems`,
  `libraries` (each a prose string, may contain Markdown links).
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
- There's no automated resource-reference check yet (front matter
  `image`/`pdf` fields pointing at files that don't exist in the
  bundle) — verified manually via a throwaway debug template during
  the 2026-08-24 session, came back clean, but this isn't wired into
  any repeatable check. Worth turning into a real CI step alongside
  the bilingual-coverage check mentioned above.

## Known open items (as of last content session)

- No Hugo layout templates exist yet at all — that's the immediate
  next step, via `/design` mode. A `hugo build` right now won't
  produce readable HTML regardless of content completeness.
- `content/resume/` is ported and now includes the cradle.bio (2025)
  stint, but still has no icons/timeline layout — see the "Resume
  bundle front matter" section above.
- Section list pages (`content/art/_index.*.md`,
  `content/publications/_index.*.md`,
  `content/projects/_index.*.md`) don't exist yet. Optional —
  Hugo auto-generates a bare list page without them — but worth
  adding for section-level intro copy, same pattern as the tag pages.
- `content/projects/` has zero entries.
- Missing German translation for `content/publications/JP6511221B2/`
  — see Bilingual section above for why this now matters
  (fully-bilingual is policy, not a nice-to-have).